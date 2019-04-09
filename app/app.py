# -*- coding: utf-8 -*-

import os
import sys
import json
import jwt
import hmac
import requests
import responder
from time import time
import statsd as Statsd
from hashlib import sha1
from base64 import b64decode
from urllib.parse import urlencode


api = responder.API(debug=True)


class env:
    user_agent = os.getenv('USER_AGENT', 'Undefined')
    hostname = os.getenv('HOSTNAME', 'github.com')
    oauth_token = os.getenv('OAUTH_TOKEN')
    api_hostname = os.getenv('API_HOSTNAME', f'api.{hostname}')
    webhook_secret = os.getenv('WEBHOOK_SECRET')
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    statsd = None

    if os.getenv('OMG_STATSD_HOST'):
        statsd = Statsd.StatsClient(
            host=os.getenv('OMG_STATSD_HOST'),
            port=os.getenv('OMG_STATSD_PORT'),
            prefix=os.getenv('OMG_STATSD_PREFIX')
        )
    else:
        statsd = None


class GitHub:
    rest_url = f'https://{env.api_hostname}'
    graphql_url = f'https://{env.api_hostname}/graphql'

    @staticmethod
    def create_app_token(iid):
        """
        Generate a JWT token for a GitHub App integration
        """
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
            headers['Authorization'] =f"Bearer {env.oauth_token}"

        headers.setdefault('User-Agent', env.user_agent)

        return headers

    @staticmethod
    def _query(url, method, token=None,
               iid=None, headers=None, *args, **kwargs):
        headers = GitHub.make_headers(headers, token, iid)
        res = getattr(requests, method)(url, *args, headers=headers, **kwargs)

        if env.statsd:
            env.statsd.gauge('ratelimit.limit',
                             res.headers.get('X-RateLimit-Limit'))
            env.statsd.gauge('ratelimit.remaining',
                             res.headers.get('X-RateLimit-Remaining'))
            env.statsd.gauge('ratelimit.reset',
                             res.headers.get('X-RateLimit-Reset'))
            env.statsd.incr(f'status.code.{res.status_code}')

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
