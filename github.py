#!/usr/bin/env python
import os
import sys
import requests
import json

def main(command, query):
    if command == 'get':
        uri = "https://api.github.com%s" % (query)
        r = requests.get(uri)
        output = json.dumps(r.json())
        return output

    if command == 'graphql':
        headers = {'Authorization': 'token %s' % os.environ['API_TOKEN']}
        r = requests.post('https://api.github.com/graphql', json.dumps({"query": query}), headers=headers)
        output = json.dumps(r.json())
        return output

if __name__ == '__main__':
    print(main(sys.argv[1], sys.argv[2]))
