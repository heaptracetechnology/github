# GitHub as a microservice

[![Open Microservice Guide](https://img.shields.io/badge/OMG-enabled-brightgreen.svg?style=for-the-badge)](https://microservice.guide)


#### Example using Asyncy
```storyscript
# Make GitHub API requests
res = github api url:'/users/stevepeak'

# Make GitHub GraphQL requests
res = github graphql query:'{user}'

# Webhooks made easy.
when github server webhook events:['push'] as event
    repo = event.payload['repository']

# Login made easy.
when github server login scope:['user'] redirect:'https://...' as user
    token = user.access_token
```
