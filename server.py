#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import hmac
import statsd
import requests
from hashlib import sha1
from flask import Flask, request, make_response

app = Flask(__name__)


@app.route('/', methods=['post'])
def main():
    data = request.data.decode('utf-8')
    secret = os.getenv('WEBHOOK_SECRET')
    if secret:
        signature = request.headers['X-Hub-Signature']
        sig = hmac.new(os.getenv('WEBHOOK_SECRET'), data, digestmod=sha1)
        if signature != f'sha1={sig.hexdigest()}':
            return ('Signature does not match.', 400)

    event = request.headers['X-GitHub-Event']

    if os.getenv('OMG_STATSD_HOST'):
        c = statsd.StatsClient(
            host=os.getenv('OMG_STATSD_HOST'),
            port=os.getenv('OMG_STATSD_PORT'),
            prefix=os.getenv('OMG_STATSD_PREFIX')
        )
        c.incr(f'webhooks.event.{event}')

    res = requests.post(
        os.getenv('OMG_ENDPOINT'),
        data=data
    )
    res.raise_for_status()

    return ('Accepted', 200)
