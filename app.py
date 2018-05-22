#!/usr/bin/env python

import os
import sys
import json
import requests


class GitHub:
    rest_url = 'https://api.github.com'
    graphql_url = 'https://api.github.com/graphql'
    _headers = {
        'Authorization': 'token %s' % os.getenv('API_TOKEN'),
        'User-Agent': os.getenv('USER_AGENT', 'Asyncy')
    }

    @staticmethod
    def _query(url, method, *args, **kwargs):
        res = getattr(requests, method)(
            url, *args,
            headers=GitHub._headers, **kwargs
        )
        try:
            res.raise_for_status()
        except:
            sys.stderr.write(res.text)
            raise
        else:
            return res.json()

    @staticmethod
    def get(endpoint):
        return GitHub._query(
            '/'.join([GitHub.rest_url, endpoint.lstrip('/')]), 'get'
        )

    @staticmethod
    def post(endpoint, data):
        return GitHub._query(
            '/'.join([GitHub.rest_url, endpoint.lstrip('/')]), 'post',
            data=data
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

    sys.stdout.write(json.dumps(res))
