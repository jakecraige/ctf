# Sticky Notes

## Likely Attack

1. Create board w/ sticky notes with XSS payload
2. Use XSS to fetch flag from notes server :3101/flag

## Next Steps

- [ ] Get PoC of XSS payload
- [ ] Verify bot will visit
- [ ] Adapt XSS to get flag
- [ ] Exfil flag

## High Level
- Main challenge is that the notes server which serves our content sets content
  type to `text/plain` so HTML isn't rendered and XSS fails
- Uses disk storage for boards and files, maybe an LFI somewhere but I can't find one
- Maybe some sort of Python specific bug with parameter deserialization? FastAPI
  is newish
- Could this be related to request smuggling?
- Could we make the content invalid utf-8 to trick browser into processing?

---------------------------

- You can create a board and add notes to it (XSS?)
- A bot will visit the board with a GET /visit/:board_id
  - Sets an httpOnly+sameSiteStrict cookie with the TOKEN
- Both running on same docker host
  - Web (python) runs on port 3100
    - Rate limits /board/:id/report to 3/minute. This is how to get the bot to
      visit, accepts arbitrary UUID.
    - It writes boards and notes to DISK (Injectable?)
    - ## API
      - GET /
      - GET /create_board
      - POST /board/add_note { board_id (uuid), body (max 20480)}
      - GET /board/:id
      - GET /board/:id/notes
      - GET /board/:id/report
  - Notes (python) runs on port 3101
    - Custom HTTP server implementation (TCP server we can telnet to)
    - If token is provided, it will send back FLAG
    - ## API
      - /flag
        If Cookie has token value in in it, sends back flag, otherwise 401
      - /:path
        Reads from /tmp/boards/:path and sends back file
  - Bot (javascript) runs on port 3102
- Flag is set as ENV var "FLAG"
- No authentication, so we can add notes to anyone's board if we know the UUID
- (CRLF attack) Could we abuse custom HTTP server to write our own headers by custom
  structured response? Newline after their header seems to mitigate
- board_id injectable? NO it's a random UUID
- note_name injectable? SORT OF, it's computed based on the number of notes and
  named accordingly. so note0->note9
- os_error_handler is interesting, as if there could be a way to trigger it to
  leak info. Docs suggest this has to do with file operations
  Can trigger via valid UUID but non-existent board
  ```
  {"message":"[Errno 2] No such file or directory:
  '/tmp/boards/23134054-1105-49c3-b901-838c31e2d55d'"}
  ```
- FastAPI until recently assumed everything was JSON if not a form
  https://snyk.io/vuln/SNYK-PYTHON-FASTAPI-1303092
  > A request with a content type of text/plain containing JSON data would be
  > accepted and the JSON data would be extracted. Requests with content type
  > text/plain are exempt from CORS preflights, for being considered Simple
  > requests. The browser will execute them right away including cookies, and the
  > text content could be a JSON string that would be parsed and accepted by the
  > FastAPI application.
  Is it possible to leverage this for extracting cookies? CORS may not be
  relevant
- Reporting takes like 15-20s


- If I embed the website into a frame 
- Recall iframes share context with parent

- NEW ATTACK
 - We don't steal token, we just have the XSS make the request for the flag
   instead, to 35.224.135.84:3101/flag

- Could there be some sort of timing attach with the time.sleep in notes
    response?

Interesting behavior with pathlib, if we can get leading slashes we can read arbitrary
stuff
```python
from pathlib import Path
>>> print(Path("/tmp/boards") / "/test")
/test
```

## Attack

We need to steal the TOKEN using the bot, and then call :3101/flag to get the
flag.

- Notes are loaded into iframes, likely need to walk up to the parent window in
  exploit
- No noticed XSS mitigations, but the notes get served with text/plain in an
  iframe so they actually are in a `<pre>`
- The trick seems to be figuring out how to get this token with XSS, given
  cookie mitigations.
- XST (cross-site-tracing) via HTTP TRACE will echo back cookies, can we do this
    against their custom server?
  - Is there any other method of getting the server to leak it? (LFI?)

## Adding Note
1. POST /board/add_note (accepts board_id(UUID) and body(str) params)
   1. Reads all notes from /tmp/boards/:board_id
   2. Creates new note at /tmp/boards/:board_id/note0 (0...8 max)
      File content is raw body str

## Reading Note
1. GET /:board_id/:note_name
  1. Processes first line of HTTP header for route, splitting on space and
     choosing indexing into [1]
  2. Cleans route using regexp `[^a-z0-9-/]` and strips leading/trailing `/`
  3. If route is `flag`
    1. Reads each line until it finds `Cookie:`
    2. If the token value is in the cookie, returns True, else False
    3. If true, returns flag in response, else 401.
  4. Else
    1. Reads rest of HTTP req until empty line
    2. Creates path at /tmp/boards/:route
    3. Reads the file and creates header with fixed Content-Type: text/plain
    4. Sends header to client
    5. Sends file in 1448 sized chunks, sleeping 0.1 between


