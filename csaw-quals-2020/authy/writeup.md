# authy (Crypto, 150 points)

> Check out this new storage application that your government has started! It's
> supposed to be pretty secure since everything is authenticated...
>
> curl crypto.chal.csaw.io:5003

This challenge provides you with a remote server and a `handout.py` file for
what is running on it. It's a flask app with two endpoints, `/new` to create
a note and `/view` to view the note. The goal of this challenge is to become an
admin so that the server will return the flag to you when you view the `/view`
endpoint:

```python
encode = base64.b64decode(info["id"]).decode('unicode-escape').encode('ISO-8859-1')
hasher = hashlib.sha1()
hasher.update(SECRET + encode)
gen_checksum = hasher.hexdigest()

if checksum != gen_checksum:
    return ">:(\n>:(\n>:(\n"

try:
    entrynum = int(note_dict["entrynum"])
    if 0 <= entrynum <= 10:

        if (note_dict["admin"] not in [True, "True"]):
            return ">:(\n"
        if (note_dict["access_sensitive"] not in [True, "True"]):
            return ">:(\n"

        if (entrynum == 7):
            return "\nAuthor: admin\nNote: You disobeyed our rules, but here's the note: " + FLAG + "\n\n"
        else:
            return "Hmmmmm...."
```

So we need to provide it an `id` that produces a valid SHA1 hash and ensure that
the data has `admin=True, access_sensitive=True, entrynum=7`. When you create
a note, it automatically sets these to not those values and looks like so:

```python
if "admin" in payload.keys():
    return ">:(\n>:(\n"
if "access_sensitive" in payload.keys():
    return ">:(\n>:(\n"

info = {"admin": "False", "access_sensitive": "False" }
info.update(payload)
info["entrynum"] = 783

infostr = ""
for pos, (key, val) in enumerate(info.items()):
    infostr += "{}={}".format(key, val)
    if pos != (len(info) - 1):
        infostr += "&"

infostr = infostr.encode()

identifier = base64.b64encode(infostr).decode()

hasher = hashlib.sha1()
hasher.update(SECRET + infostr)
```

So the default string looks like this
`admin=False&access_sensitive=False&author=tpurp&note=note&entrynum=783` and
create the integrity hash by prefixing the secret. The SHA2 family of
functions, which includes SHA1, are vulnerable to length-extension attacks. This
means that we can use the data we know and the hash provided by the server, and
create a new hash that is valid without knowing the secret!

Knowing this, the exploit happens like so:
1. Create a note and retrieve the id and integrity hash
2. Extend the id and hash with the content `&admin=True&access_sensitive=True&entrynum=7`,
   because the parsing of this happens in order, the trailing attributes
   override the default and allow us to become admin.
3. Submit the new id and hash to the server to get the flag.

The extension and encoding were the tricky parts of getting the solution. The
hash extension requires knowing the secret length which was not provided, and it
puts non-utf-8 characters into the output which will fail on the server side
since they run `python3` which defaults to utf-8 and causes a 500. To handle
this the solution escapes the unicode characters first and on the server they 
will undo this with the following lines:

```python
# This is the one that fails without the escaping!
identifier = base64.b64decode(info["id"]).decode()
checksum = info["integrity"]

params = identifier.replace('&', ' ').split(" ")
note_dict = { param.split("=")[0]: param.split("=")[1]  for param in params }

# Here when they use it for computing the checksum they undo it for us. How
# nice of them :)
encode = base64.b64decode(info["id"]).decode('unicode-escape').encode('ISO-8859-1')
hasher = hashlib.sha1()
hasher.update(SECRET + encode)
```

Once all of this is in place, we can run our exploit script and see the
following output:

```sh
$ python3 exploit.py
Created note
        ID: admin=False&access_sensitive=False&author=tpurp&note=note&entrynum=783
        Hash: 141b1b343e56c4180cefac70416a82d53f3fc679
Forged hash
        ID: b'admin=False&access_sensitive=False&author=tpurp&note=note&entrynum=783\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x98&admin=True&access_sensitive=True&entrynum=7'
        Hash: acd50f67cc9ee7f42aa6c58371bd732f48c3c58d

Author: admin
Note: You disobeyed our rules, but here's the note: flag{h4ck_th3_h4sh}
```

## Exploit Script

```python
import requests
import base64
import hashlib
from hashpumpy import hashpump

URL = "http://crypto.chal.csaw.io:5003"

def exploit():
    # Create the note to get the initial hash
    data = {'author': 'tpurp', 'note': 'note'}
    res = requests.post(URL+"/new", data=data)
    id_b64, integrity = res.text[19:-1].split(':')
    id_txt = base64.b64decode(id_b64).decode()
    print("Created note")
    print("\tID: {}".format(id_txt))
    print("\tHash: {}".format(integrity))

    # The initial exploit looped to brute force secret length with a for loop.
    # Just hard code it for the writeup.
    sec_len = 13
    id_suffix = b"&admin=True&access_sensitive=True&entrynum=7"
    (forgedHsh, id_txt_ext) = hashpump(integrity, id_txt, id_suffix, sec_len)
    print("Forged hash")
    print("\tID: {}".format(id_txt_ext))
    print("\tHash: {}".format(forgedHsh))

    # We have to escape the unicode chars because python3 will fail by default
    # when decoding since it deafults to utf-8.
    escaped = bytes(id_txt_ext.decode('unicode_escape'), 'unicode_escape')
    data = {'id': base64.b64encode(escaped).decode(), 'integrity': forgedHsh}
    res = requests.post(URL+"/view", data=data)
    print(res.text)

exploit()
```
