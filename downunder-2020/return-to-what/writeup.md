# Return to what (Pwn, X points)

TODO: maybe make an actual writeup since this is like half done.

"""
Return to what (TODO)

Author: Faith

This will show my friends

nc chal.duc.tf 30003
"""


## Decompile

```
undefined8 main(void) {
  puts("Today, we\'ll have a lesson in returns.");
  vuln();
  return 0;
}

void vuln(void) {
  char local_38 [48];
  puts("Where would you like to return to?");
  gets(local_38);
  return;
}
```

```
Arch:     amd64-64-little
RELRO:    Partial RELRO
Stack:    No canary found
NX:       NX enabled
PIE:      No PIE (0x400000)
```

## Exploiting

This is a classic ROP based buffer-overflow (BOF) vulnerability. NX is on which
means we can't inject shellcode which forces us to use ROP. The lack of PIE
means we can easily identify other places in the executable to call to leak the
information we need to create our exploit. The plan will be this:

1. Leak a few libc addresses from GOT to identify libc version
2. Construct shell exploit from that libc version
