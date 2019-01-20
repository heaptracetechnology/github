# -*- coding: utf-8 -*-

import os
import sys
import json
import requests

from flask import Flask, request


app = Flask(__name__)


if os.getenv('OMG_STATSD_HOST'):
    import statsd as Statsd
    statsd = Statsd.StatsClient(
        host=os.getenv('OMG_STATSD_HOST'),
        port=os.getenv('OMG_STATSD_PORT'),
        prefix=os.getenv('OMG_STATSD_PREFIX')
    )
else:
    statsd = None


listeners = {}


class GitHub:
    rest_url = 'https://api.github.com'
    graphql_url = 'https://api.github.com/graphql'

    @staticmethod
    def make_headers(headers, token):
        if headers is None:
            headers = {}

        if token:
            headers['Authorization'] = f"token {token}"
        else:
            headers['Authorization'] =f"token {os.getenv('OAUTH_TOKEN')}"

        headers.setdefault('User-Agent', os.getenv('USER_AGENT', 'Undefined'))

        return headers

    @staticmethod
    def _query(url, method, token=None, headers=None, *args, **kwargs):
        headers = GitHub.make_headers(headers, token)
        res = getattr(requests, method)(url, *args, headers=headers, **kwargs)

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
    def api(url, **kwargs):
        return GitHub._query(
            '/'.join([GitHub.rest_url, url.lstrip('/')]),
            **kwargs
        )

    @staticmethod
    def graphql(query, **kwargs):
        return GitHub._query(
            GitHub.graphql_url, 'post',
            data=query, **kwargs
        )

    @staticmethod
    def webhook(req):
        # TODO X-Hub-Signature
        event = req.headers['X-Github-Event']
        data = json.dumps(dict(
            eventType=f'github.webhook.{event}',
            contentType='application/vnd.omg.object+json',
            eventID=req.headers['X-Github-Delivery'],
            data=req.json
        ))
        sends = 0
        for listener in listeners.values():
            if listener.get('events') is None or event in listener['events']:
                sends = sends + 1
                requests.post(
                    listener['endpoint'] or os.getenv('OMG_ENDPOINT'),
                    data=data,
                    headers={'Content-Type': 'application/json'}
                )
        return f'{sends} listeners got notifications.'


@app.route('/api', methods=['POST'])
def api():
    return GitHub.api(**request.json)


@app.route('/graphql', methods=['POST'])
def graphql():
    return GitHub.graphql(**request.json)


@app.route('/subscribe', methods=['POST'])
def subscribe():
    body = request.json
    listeners[body['id']] = body
    return 'Subscribed'


@app.route('/unsubscribe', methods=['POST'])
def unsubscribe():
    if listeners.pop(request.json['id'], False): return 'Unsubscribed'
    else:
        return 'No subscription found.'


@app.route('/webhooks', methods=['POST'])
def webhooks():
    # webhooks from Gitub.com
    return GitHub.webhook(request)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
