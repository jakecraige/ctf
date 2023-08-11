# Gerald Catalog
### Author: anli

service worker somewhere

## Notes
- No {{{raw_html}}} in templates
- Doesn't use safe compare for user password (timing leak)
  Password doesn't look hashed either

## API
### POST /register
{
  user: str // len between 3-20
  password: str // len 8+
}
- Adds to DB if new
- Calls ctx.login (without any password), if the impl does any cleaning like
  trimming spaces, we could register with a different username and log in as the
  other user.
- redirects to /geralds
### GET /geralds
### GET /gerald/:id
Renders template based on provided ID, error if copyrightCLaim and not
localhost, otherwise renders with image: gerald.png?caption={urlEncode(caption}) 
Also sends notifications.
### GET /gerald.png?caption=:caption
Caption must be string and less than 100, image
Image generated using a canvas and `fillText` to add caption.
### POST /add
{
  name: str (any len)
  caption: str (less than 100)
}
Adds gerald to DB (looks unpollutable). Always generates unique ID.
### PUT /gerald/:id/subscription
{
  endpoint: URL,
  keys: {
    auth: str,
    p256dh: str,
  }
}
Ownership of gerald by ID is validated, subscription iss validated, and then set
as the subscription in the DB.
!!!!! DING DING INTERESTING !!!!!!
- This endpoint is later used with `fetch` and sends the id, name and caption in
  the body
- Validation Flow:
  - endpoint and keys must be set and return valid types
    - must be port 80, 443 or none.
    - hostname must not be banned, (localhost, host.docker.internal, ENV)
    - host cannot include :, bcactf.com or 192.168.
    - hostname cannot start with 127.
    - protocol must be HTTP
  - returns new object, invalidating any pollution unless it was useful before
    the return.
- The content in the push payload is encrypted via https://httpwg.org/specs/rfc8188.html
  We can view plaintext content locally with SW debugger though.
### DELETE /gerald/:id/subscription
Retrieves gerald by ID, verifies ownersship, and sets sub to undefined.

## Potential Attack
- Force a view that will send a notification to us, get flag in caption
- Pollute database with my username as `__proto__` (name taken lol)
- XSS through image generation so that we can make API calls from localhost,
  allowing viewing the gerald

## Attack Chain

1. Bypass copyright claim check
2. View the flag gerald to send us notification
 
