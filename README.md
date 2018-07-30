# GitHub API as a microservice


### GitHub APIv3
```sh
$ omg exec github -c api -a method=get -a url=/user -e OAUTH_TOKEN=foobar
✔ Ran command: `api` with output: {"login":"foobar","id":...
```

### GitHub GraphQL
```sh
$ omg exec github -c graphql -a query='...' -e OAUTH_TOKEN=foobar
✔ Ran command: `graphql` with output: {"data":...
```

### GitHub Webhooks
```sh
$ omg exec github -c webhooks -e WEBHOOK_SECRET=foobar -e OAUTH_TOKEN=foobar
```

Create a server to accept GitHub Webhooks.

#### Example Asyncy Usage
```storyscript
github webhooks as client
    when client push as result
        # a new push payload was received
        # ...
```
