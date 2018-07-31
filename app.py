# -*- coding: utf-8 -*-

import os
import sys
import json
import requests


if os.getenv('OMG_STATSD_HOST'):
    import statsd as Statsd
    statsd = Statsd.StatsClient(
        host=os.getenv('OMG_STATSD_HOST'),
        port=os.getenv('OMG_STATSD_PORT'),
        prefix=os.getenv('OMG_STATSD_PREFIX')
    )
else:
    statsd = None


class GitHub:
    rest_url = 'https://api.github.com'
    graphql_url = 'https://api.github.com/graphql'
    _headers = {
        'Authorization': f"token {os.getenv('OAUTH_TOKEN')}",
        'User-Agent': os.getenv('USER_AGENT', 'Undefined')
    }

    @staticmethod
    def _query(url, method, *args, **kwargs):
        res = getattr(requests, method)(
            url, *args,
            headers=GitHub._headers,
            **kwargs
        )

        if statsd:
            statsd.gauge('ratelimit.limit',
                         res.headers.get('X-RateLimit-Limit'))
            statsd.gauge('ratelimit.remaining',
                         res.headers.get('X-RateLimit-Remaining'))
            statsd.gauge('ratelimit.reset',
                         res.headers.get('X-RateLimit-Reset'))
            statsd.incr(f'status.code.{res.status_code}')

        try:
            res.raise_for_status()
        except:
            sys.stderr.write(res.text)
            raise
        else:
            return res.text

    @staticmethod
    def api(method, url, data=None, params=None):
        return GitHub._query(
            '/'.join([GitHub.rest_url, url.lstrip('/')]), method,
            data=data,
            params=params
        )

    @staticmethod
    def graphql(query):
        return GitHub._query(
            GitHub.graphql_url, 'post',
            data=json.dumps({'query': query})
        )


if __name__ == '__main__':
    command = sys.argv[1]
    kwargs = json.loads(sys.argv[2])
    res = getattr(GitHub, command)(**kwargs)
    sys.stdout.write(res)
