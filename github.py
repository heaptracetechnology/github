#!/usr/bin/env python
import sys
import requests
import json

def main(command, query):
    if command == 'get':
        uri = "https://api.github.com%s" % (query)
        r = requests.get(uri)
        output = json.dumps(r.json())
        return output

if __name__ == '__main__':
    print(main(sys.argv[1], sys.argv[2]))
