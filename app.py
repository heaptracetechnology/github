# -*- coding: utf-8 -*-

import os
import sys
import json
import jwt
import hmac
import requests
from time import time
from hashlib import sha1
from base64 import b64decode
from urllib.parse import urlencode

from flask import Flask, request, redirect


app = Flask(__name__)

UA = os.getenv('USER_AGENT', 'Undefined')
HOSTNAME = os.getenv('HOSTNAME', 'github.com')
API = os.getenv('API_HOSTNAME', f'api.{HOSTNAME}')

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
    rest_url = f'https://{API}'
    graphql_url = f'https://{API}/graphql'

    @staticmethod
    def create_app_token(iid):
        now = int(time())

        token = jwt.encode({
                'iat': now,
                'exp': now + 60,
                'iss': os.getenv('APP_ID')
            }, b64decode(os.getenv('APP_PRIVATE_KEY')), algorithm='RS256')

        res = GitHub._query(
            f'{GitHub.rest_url}/installations/{iid}/access_tokens',
            method='post',
            token=token.decode('utf-8'),
            headers={
                'Accept': 'application/vnd.github.machine-man-preview+json'
            }
        )
        return res.json()['token']

    @staticmethod
    def make_headers(headers, token, iid):
        if headers is None:
            headers = {}

        if iid:
            token = GitHub.create_app_token(iid)
            headers['Accept'] = 'application/vnd.github.machine-man-preview+json'

        if token:
            headers['Authorization'] = f"Bearer {token}"

        else:
            headers['Authorization'] =f"Bearer {os.getenv('OAUTH_TOKEN')}"

        headers.setdefault('User-Agent', UA)

        return headers

    @staticmethod
    def _query(url, method, token=None,
               iid=None, headers=None, *args, **kwargs):
        headers = GitHub.make_headers(headers, token, iid)
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
            return res

    @staticmethod
    def api(url, **kwargs):
        return GitHub._query(
            '/'.join([GitHub.rest_url, url.lstrip('/')]),
            **kwargs
        ).text

    @staticmethod
    def graphql(query, **kwargs):
        return GitHub._query(
            GitHub.graphql_url, 'post',
            data=query, **kwargs
        ).text


@app.route('/api', methods=['POST'])
def api():
    return GitHub.api(**request.json)


@app.route('/graphql', methods=['POST'])
def graphql():
    return GitHub.graphql(**request.json)


@app.route('/webhook_validate', methods=['POST'])
def webhook_validate():
    assert request.json['headers'].get('X-GitHub-Event')
    signature = request.json['headers'].get('X-Hub-Signature')
    assert signature, 'X-Hub-Signature not found in the header.'
    sha_name, signature = signature.split('=')
    assert sha_name == 'sha1'
    mac = hmac.new(
        os.getenv('WEBHOOK_SECRET'),
        msg=request.json['body'],
        digestmod='sha1'
    )
    return dumps({
        'valid': str(mac.hexdigest()) == str(signature),
        'event': request.json['headers']['X-GitHub-Event']})


@app.route('/login_redirect', methods=['GET'])
def login_redirect():
    data = request.json
    query = dict(
        scope=','.join(data['scope']) if data['scope'] else None,
        state=data.get('state', None),
        client_id=os.getenv('CLIENT_ID'),
        redirect_uri=data.get('redirect')
    )
    return f'https://{HOSTNAME}/login/oauth/authorize?{urlencode(query)}'


@app.route('/login_token', methods=['POST'])
def login_token():
    body = request.json
    res = requests.post(
        f'https://{HOSTNAME}/login/oauth/access_token',
        data=json.dumps(dict(
            client_id=os.getenv('CLIENT_ID'),
            client_secret=os.getenv('CLIENT_SECRET'),
            code=body['code'],
            state=body['state']
        )),
        headers={
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'application/json',
            'User-Agent': UA
        }
    )
    return res.json()['access_token']


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
