# GitHub as a microservice

[![Open Microservice Guide](https://img.shields.io/badge/OMG-enabled-brightgreen.svg?style=for-the-badge)](https://microservice.guide)


### <img src="https://user-images.githubusercontent.com/4370550/56803568-460e5800-6823-11e9-8a70-25ab4b7e32ea.png" width="40" align="center"> Storyscript example

```storyscript
# Make GitHub API requests
res = github api url:'/users/stevepeak'

# Make GitHub GraphQL requests
res = github graphql query:'{user}'

# Webhooks made easy.
when github events webhooks events:['push'] as event
    repo = event.payload['repository']
```
