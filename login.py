# -*- coding: utf-8 -*-

import os
import sys
from uuid import uuid4
from json import loads
from datetime import datetime
import requests
import flask
from flask import request
from urllib.parse import urlencode


HOSTNAME = os.getenv('HOSTNAME', 'github.com')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
USER_AGENT = os.getenv('USER_AGENT', 'Unknown')

app = flask.Flask(__name__)

subscriptions = {}


def url(url: str, **query) -> str:
    return f'{url}?{urlencode(query)}'


@app.route('/subscribe', methods=['POST'])
def subscribe():
    data = loads(request.get_data())
    subscriptions[data['id']] = data
    return 'Subscribed'


@app.route('/unsubscribe', methods=['DELETE'])
def unsubscribe():
    id = request.args.get('id')
    subscriptions.pop(id, None)
    return 'Unsubscribed'


@app.route('/<id>', defaults={'state': None})
@app.route('/<id>/<state>')
def login(id, state):
    code = request.args.get('code', '')
    if code:
        res = requests.post(
            f'https://{HOSTNAME}/login/oauth/access_token',
            data={
                'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET,
                'code': code,
                'state': state
            },
            headers={
                'User-Agent': USER_AGENT,
                'Accept': 'application/json'
            }
        )

        res.raise_for_status()

        result = res.json()
        result['scope'] = result['scope'].split(',')
        result['state'] = state
        data = {
            'eventType': 'github.login',
            'cloudEventsVersion': '0.1',
            'source': 'login',
            'eventID': str(uuid4()),
            'eventTime': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
            'contentType': 'application/vnd.omg.object+json',
            'data': result
        }

        # Send access_token back to platform
        requests.post(
            subscriptions[id]['endpoint'],
            data=data,
            headers={
                'Content-Type': 'application/json'
            }
        )

        # Redirect user to new web page
        return flask.redirect(subscriptions[id]['data']['redirect'])

    else:
        # Redirect user to login at GitHub
        state = request.args.get('state', '')
        proto = request.headers.get('X-Forwarded-Proto', 'http')
        host = request.headers.get('Host')
        return flask.redirect(
            url(f'https://{HOSTNAME}/login/oauth/authorize',
                client_id=CLIENT_ID,
                scope=','.join(subscriptions[id]['data']['scope']),
                state=state,
                redirect_uri=f'{proto}://{host}/{id}/{state}')
        )
