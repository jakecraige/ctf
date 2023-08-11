Goal: Get a push notification sent to us for "Flag Gerald", the payload content
      will include the flag.

## Possible Attack Flow
1. Subscribe to "Flag Gerald" views
2. Find an SSRF to have the server view it
3. Decode the push packet to find content

## Points of Interest
*GET /gerald.png?caption=STRING*
This seems like the primary way to have a go at getting the server to make
an internal request to view the gerald, but the image renderer is using
canvas with `ctx.fillText` which doesn't look vulnerable.

*PUT /gerald/:id/subscription*
Allows us to get an POST SSRF to just about any endpoint, and it seems easy
to bypass the localhost checking if we want.

*Handlebars View has access to flag*
The database's `getGeralds` and `getGerald` returns the full content geralds,
which is then rendered from `geralds.hbs` and `genrald.hbs`. There could be some
sort of injection here to cause some unexpected behavior where we are able to
either XSS or even access the flag. Though the hint references push so prob not.
<!-- attack the password validation for another user, but technically this is unsafe. -->

*JavaScript Object as a Database*
This screams manipulation of the data structures or prototype pollution,
especially because this is where the flag is stored in memory `this.flag`,
but I can't find a way yet.

There is no real validation on `username`, so we can set it to stuff like
`__proto__`, but funny that username was already taken XD.

*The Gerald Subscriptions are a Singleton*
```javascript
function setSubscription(id, subscription) {
  this.geralds[id].subscription = subscription;
}
```
This is somewhat peculiar since the state DB state is shared between users,
though it does create unique ones for each user with random UUIDs.

*Unsafe Password Comparison*
`this.users[username].password === password`, I doubt they want us to timing
attack the password validation for another user, but technically this is unsafe.

--------------------------------------------------------------------------------

## Key Defenses
- Only localhost IPs can view the gerald with a "copyright claim" on it
  ```
  ctx.ip !== "127.0.0.1" && ctx.ip !== "::1" && ctx.ip !== "::ffff:127.0.0.1"
  ```
  q: Can we trick the IP check?
  a: I considered proxy headers, but koa doesn't use them unless you enable it
     specifically by setting `app.proxy=true` and they don't seem to.
     I don't understand IPv6 though, is there another way?
- Subscription validation ensures that we can't trivially point it at localhost,
  though we can use `0.0.0.0` or a DNS entry to route it there anyways.

## XSS & SSRF Research
We need to find a GET request SSRF to get the flag.

*Web Push*
We can have it SSRF to send us notifications directly, and likely bypass their
mechanisms to prevent it going to localhost. Is there a way we can get it to
issue a GET request somewhere?

Time to dig into web push RFC..
- https://developers.google.com/web/fundamentals/push-notifications/web-push-protocol
- https://datatracker.ietf.org/doc/html/draft-ietf-webpush-protocol


1. Application sends msg to push service endpoint
2. Push service endpoint responds with 
   ```
   HTTP/1.1 202 Accepted
   Date: Thu, 11 Dec 2014 23:56:55 GMT
   Link: </receipt-subscription/3ZtI4YVNBnUUZhuoChl6omUvG4ZM>; rel="urn:ietf:params:push:receipt"
   Location: https://push.example.net/message/qDIYHNcfAIPP_5ITvURr-d6BGt
   ```
   The receipt will be set to the SSRF URL
3. Application eventually requests receipts by making a GET request to the link



> push message receipt:  A message delivery confirmation sent from the
>      push service to the application server.

> ## Receiving Push Message Receipts
> The application server requests the delivery of receipts from the
>    push service by making a HTTP GET request to the receipt subscription
>       resource.


*Image Rendering*
Gerald image viewing uses arbitrary user input into `canvas.fillText`

*Handlebars*
`gerald.hbs` does `<img src="{{image}}" />` with a URL that we have full control
of the caption value, except that it's run through `encodeURIComponent`. If
there are other dynamic srcs it i
