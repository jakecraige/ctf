# L10N Poll
### Author: anli

http://web.bcactf.com:49159/

## Notes

- A site with language selectors that asks questions and localizes languages
- Uses JWTs to fetch a localization file via the `lion-token` cookie param
  - JWT has `language` key signed with RSA-SHA256
  - Does verification accept any type of JWT?!
- Seems like maybe we need to pollute global JS namespace for file? Maybe
    scoping? hm...
- Need to get flag from flag.txt

## Attack
- Create a JWT Token with POST to /localization-language for the language of 
  `key`
- Pass the JWT token to GET /localisation-file to download public key
- Use public key as the secret for creating a HS256 JWT for the language of
  'key.txt' (they are using a vuln older version of jwt lib where sym and asym can be mixed)
- Pass the new JWT token to GET /localisation-file to download flag
