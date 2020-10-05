#!/usr/bin/env python3
from pwn import *
import codecs
from base64 import b64decode
from string import ascii_lowercase

HOST = 'chal.ctf.b01lers.com'
PORT = 2008

r = remote(HOST,PORT)

def generate_dict():
    bacon_dict = {}

    for i in range(0, 26):
        tmp = bin(i)[2:].zfill(5)
        tmp = tmp.replace('0', 'a')
        tmp = tmp.replace('1', 'b')
        bacon_dict[tmp] = chr(65 + i)

    return bacon_dict

bacon_dict = generate_dict()

def bacon(words):
    cipher = ''
    words = words.lower()
    words = re.sub(r'[^ab]+', '', words)

    for i in range(0, len(words) // 5):
        cipher += bacon_dict.get(words[i * 5:i * 5 + 5], ' ')
    return cipher.lower()

rot13trans = str.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz', 'NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm')
def rot13(s):
    return s.translate(rot13trans)

def atbash(s):
    alphabet = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    cipher = ''
    for word in s:
        if not word.upper() in alphabet:
            cipher += word
        else:
            if word in [x.lower() for x in alphabet]:
                cipher += alphabet[len(alphabet) - alphabet.index(word.upper()) - 1 % len(alphabet)].lower()
            else:
                cipher += alphabet[len(alphabet) - alphabet.index(word) - 1 % len(alphabet)]
    return cipher

def Base64(s):
    return b64decode(s).decode()

if __name__ == '__main__':
    context.log_level = "DEBUG"
    count = 0
    while True:
        r.recvuntil('Method: ')
        method = r.recvuntil('\n').strip()
        r.recvuntil('Ciphertext: ')
        argument = r.recvuntil('\n').strip()

        r.recv()

        result = globals()[method.decode()](argument.decode())  # :)
        r.sendline(result.encode())
        count += 1
        if count == 1000:
            print(r.recv())
            exit(0)

