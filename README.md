# GitHub as a microservice

[![Open Microservice Guide](https://img.shields.io/badge/OMG-enabled-brightgreen.svg?style=for-the-badge)](https://microservice.guide)


#### Example using Asyncy
```storyscript
# Make GitHub API requests
res = github api url:'/users/stevepeak'

# Make GitHub GraphQL requests
res = github graphql query:'{user}'

# Webhooks made easy.
when github events webhooks events:['push'] as event
    repo = event.payload['repository']
```
