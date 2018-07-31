# -*- coding: utf-8 -*-

import hmac
import json
import os
import requests
import statsd
from datetime import datetime
from flask import Flask, request, make_response
from hashlib import sha1

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
        headers={'Content-Type': 'application/json'},
        data={
            'eventType': f'com.github.webhook.{event}',
            'cloudEventsVersion': '0.1',
            'eventID': request.headers['X-GitHub-Delivery'],
            'eventTime': str(datetime.now()),
            'contentType': 'application/json',
            'data': json.loads(data)
        }
    )
    res.raise_for_status()

    return ('Accepted', 200)
