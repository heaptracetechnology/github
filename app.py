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
    def get(query):
        return GitHub._query(
            '/'.join([GitHub.rest_url, query.lstrip('/')]), 'get'
        )

    @staticmethod
    def post(query, body):
        return GitHub._query(
            '/'.join([GitHub.rest_url, query.lstrip('/')]), 'post',
            data=body
        )

    @staticmethod
    def graphql(query):
        return GitHub._query(
            GitHub.graphql_url, 'post',
            data=json.dumps({'query': query})
        )


if __name__ == '__main__':
    sys.stdout.write(json.dumps(getattr(GitHub, sys.argv[1])(*sys.argv[2:])))
