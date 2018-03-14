#!/usr/bin/env python

import os
import sys
import json
import requests


def main(command, query):
    headers = {
        'Authorization': 'token %s' % os.getenv('API_TOKEN'),
        'User-Agent': os.getenv('USER_AGENT')
    }
    if command == 'get':
        uri = "https://api.github.com%s" % (query)
        r = requests.get(uri, headers=headers)
        return r.text

    if command == 'graphql':
        r = requests.post('https://api.github.com/graphql', json.dumps({"query": query}), headers=headers)
        return r.text

if __name__ == '__main__':
    print(main(sys.argv[1], sys.argv[2]))
