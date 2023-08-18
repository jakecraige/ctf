# Cybercrime Society Club Germany
You are agent Json Bourne. Your mission: Hack this new cybercrime website before it is too late.

```
Uses auth cookie and checks DB for a cookie value to match.
Admin user has to have specific email and userid > 90000000
Uses json.dumps and json.loads for DB. Any RCE?

delete_accounts seems vulnerable to deleting other user accounts on LN105. We
can use this to delete admin and change our email. Then run command
```

## Exploit path
- Create account
- Make us admin
- Use command to get flag
