#!/usr/bin/env python
import os
import sys
import requests
import json

def main(command, request):
    if command == 'get':
        uri = "https://api.github.com%s" % (request)
        r = requests.get(uri)
        output = json.dumps(r.json())
        return output

    if command == 'query':
        query = '{ user(login: "joshpollara") { repositories(first: 10) { nodes { languages(first: 3) { nodes { name } } } } } }'
        headers = {'Authorization': 'token %s' % os.environ['API_TOKEN']}
        r = requests.post('https://api.github.com/graphql', json.dumps({"query": query}), headers=headers)
        output = json.dumps(r.json())
        return output

if __name__ == '__main__':
    print(main(sys.argv[1], sys.argv[2]))
