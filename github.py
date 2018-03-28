#!/usr/bin/env python

import os
import sys
import json
import requests


def main(command, query, body):
    headers = {
        'Authorization': 'token %s' % os.getenv('API_TOKEN'),
        'User-Agent': os.getenv('USER_AGENT')
    }

    if command == 'get':
        uri = "https://api.github.com%s" % (query)
        res = requests.get(uri, headers=headers)

    if command == 'post':
        uri = "https://api.github.com%s" % (query)
        res = requests.post(uri, headers=headers, data=body)

    if command == 'graphql':
        uri = 'https://api.github.com/graphql'
        res = requests.post(uri, json.dumps({"query": query}), headers=headers)
    
    try:
        res.raise_for_status()
    except:
        sys.stderr.write(res.text)
        raise
    else
        return r.text

if __name__ == '__main__':
    print(main(sys.argv[1], sys.argv[2], sys.argv[3]))
