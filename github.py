#!/usr/bin/env python

import os
import sys
import requests


def main(command, query):
    if command == 'get':
        uri = "https://api.github.com%s" % (query)
        r = requests.get(uri)
        return r.text

    if command == 'graphql':
        headers = {'Authorization': 'token %s' % os.environ['API_TOKEN']}
        r = requests.post('https://api.github.com/graphql', json.dumps({"query": query}), headers=headers)
        return r.text

if __name__ == '__main__':
    print(main(sys.argv[1], sys.argv[2]))
