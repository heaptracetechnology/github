# GitHub API as a microservice

[![Open Microservice Guide](https://img.shields.io/badge/OMG-enabled-brightgreen.svg?style=for-the-badge)](https://microservice.guide)


### GitHub APIv3
```sh
$ omg exec api -a method=get -a url=/user -e OAUTH_TOKEN=foobar
✔ Ran command: `api` with output: {"login":"foobar","id":...
```

### GitHub GraphQL
```sh
$ omg exec graphql -a query='...' -e OAUTH_TOKEN=foobar
✔ Ran command: `graphql` with output: {"data":...
```

#### Example Asyncy Usage
```storyscript
http server
    when listen path:'/login/github' method:'get' as req
        req redirect url:(github oauthRedirect scope:['read:user', 'user:email'])

    when listen path:'/github/oauth_success' method:'get' as req
        # get the oauth details from the user
        token = github oauthGetAccessToken code:req.params['code']
        res = github graphql query:'query{viewer{login,name,databaseId,email}}'
                             :token
```
