#!/bin/sh
set -e

apk update
apk add --no-cache python py-pip

pip install requests

rm -rf /var/cache/apk/*
