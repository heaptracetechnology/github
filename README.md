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

### GitHub Webhooks
```sh
$ omg subscribe webhooks -e WEBHOOK_SECRET=foobar -e OAUTH_TOKEN=foobar
```

Create a server to accept GitHub Webhooks.

#### Example Asyncy Usage
```storyscript
# GitHub Oauth Login
http server
  when listen path:'/login/github' as req
    url = github login_redirect scope:['repo']
                                redirect:'{req.url}/oauth_success'
    req redirect :url

  when listen path:'/login/github/oauth_success' as req
    token = github login_token code:req.arguments['code']
    user = github api :token url:'/user'
    user.login  # the github.com/username

# GitHub Webhook Handler
http server
  when listen path:'/github/webhooks' method:'post' as req
    if github validate signature:req.headers['X-Hub-Signature']
                       body:req.body_raw
      # payload is ok
    else
      # payload is not valid

```
