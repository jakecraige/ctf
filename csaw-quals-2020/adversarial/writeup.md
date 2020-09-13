# adversarial (Crypto, 200 points)

> You have a new mission from HQ to hunt down some rogue flags. Check the
> details in the assignment. Find something good, and you'll be rewarded with
> one better
> HINT: flags you discover are not in flag format.
> nc crypto.chal.csaw.io 5000

In this challenge you are provided an `assignment.txt` file with a series of
ciphertexts and a description of how they were encrypted. In particular, it's
important to see how they were encrypted. The relevant content is included
below:

```python
KEY = os.environ['key']
IV = os.environ['iv']

secrets = open('/tmp/exfil.txt', 'r')

for pt in secrets:
    ctr = Crypto.Util.Counter.new(128, initial_value=long(IV.encode("hex"), 16))
    cipher = Crypto.Cipher.AES.new(KEY, Crypto.Cipher.AES.MODE_CTR, counter=ctr)
    ciphertext = cipher.encrypt(pt)
    send(ciphertext.encode("base-64"))
```

We can see that they are using AES-CTR-128 with a static key and IV. The issue
here is that the IV is static. With AES-CTR it's critical that you use a random
IV, otherwise it's basically a one-time pad and reusing a key with a one-time
pad is well... not a one time pad, and not secure.

The solution to this challenge is basically that of [Cryptopals Challenge
20](https://cryptopals.com/sets/3/challenges/20). It works as follows:

1. Create a series of "pseudo-blocks" made up of the bytes from all ciphertexts
   at the same index. So if we have two ciphertexts that are one block long, we
   iterate over each byte and create blocks like `block[i] = [ciphertext[0][i],
   ciphertext[1][i]]`.
1. Next we brute force the one-byte key for each block and use the frequency of
   ascii characters to make a best guess at what the key is.
1. Lastly we concatenate all the bytes of the key into a key, and decrypt the
   actual ciphertexts. If our frequencies are good enough, we'll get some
   plaintext.

The trickiest part of this is getting the frequencies right, in my solution I 
was lazy and just kept pulling different frequencies from solutions to similar
problems online until one of them worked, hence the quite unexpected numbers in
it XD. But it works well enough.

One you do that, run the exploit script to get the "flag", submit it to the
server mentioned in the description for the actual flag.

```sh
$ python3 exploit.py
Found 20 ciphertexts
PLAINTEXTS
what is real? How do you define real? If <ou're tal.ing abou9 what you can feel, 2hat yox can sm
neo, sooner or later you're going to real,ze, just $s I did,mthat there's a diffe7ence bhtween k
the flag is: 4fb81eac0729a -- The flag is\x7f 4fb81eacu729a -- \x19e flag is: 4fb81eacu729a -  The fl
message 86831. Test message 86831. Test m ssage 868v1. Test  essage 86831. Test m ssage 56831. T
i am the Architect. I created the Matrix.eI have be n waitin* for you. You have m$ny que~tions a
attack at dawn. Use the address 37.9257 1u.2036 193|.283 - D" not reply to this m ssage.-Attack
have you ever had a dream Neo, that you w re so sur  was rea!? What if you were u+able tb wake f
which brings us at last to the moment of 1ruth, whe7ein the +undamental flaw is u)timateay expre
message 64023. Test message 64023. Test m ssage 640w3. Test  essage 64023. Test m ssage ;4023. T
unfortunately, no one can be told what th  Matrix i6. You ha;e to see it for your6elf. Teis is y
the Matrix is older than you know. I pref r countin" from th( emergence of one in1egral lnomaly
the Matrix is a system, Neo. That system ,s our ene(y. But w%en you're inside, yo0 look lround,
the flag is: 4fb81eac0729a -- The flag is\x7f 4fb81eacu729a -- \x19e flag is: 4fb81eacu729a -  The fl
sentient programs. They can move in and o0t of any 6oftware >till hard-wired to t-eir sy~tem. Th
zion Keys: 8 - F - A - Q - 1 - Z - R - Z h B - Z - \x17- R - Rc Repeat: 8 - F - A -eQ - 1   Z - R
i won't lie to you, Neo. Every single maneor woman 2ho has s9ood their ground, ev ryone zho has
please. As I was saying, she stumbled upo+ a soluti*n whereb4 nearly 99% of all t st subgects ac
i've seen an agent punch through a concre1e wall. M n have e ptied entire clips a1 them lnd hit
everything that has a beginning has an en!. I see t-e end co ing. I see the darkn ss sprhading.
test message 10592. Test message 10592. T st messag  10592. \x19st message 10592. T st mes~age 105
```

## Exploit Script

```python
from pwn import *
from collections import Counter

# I manually created this file by pulling all the base64 ciphertexts into a
# newline separated file for easier parsing.
CIPHERTEXTS_FILE = "./ciphertexts.txt"
BLOCK_SIZE = 16

def parse_ciphertexts():
    ciphertexts_file = open(CIPHERTEXTS_FILE, "r")
    ciphertexts = []
    current_ciphertext_b64 = ""
    for line in ciphertexts_file.readlines():
        if line == "\n":
            ciphertexts.append(b64d(current_ciphertext_b64))
            current_ciphertext_b64 = ""
            continue
        current_ciphertext_b64 += line[:-1]
    return ciphertexts

def get_chunks(l, n):
    n = max(1, n)
    return list((l[i:i+n] for i in range(0, len(l), n)))

freq = {}
freq[' '] = 700000000
freq['e'] = 390395169
freq['t'] = 282039486
freq['a'] = 248362256
freq['o'] = 235661502
freq['i'] = 214822972
freq['n'] = 214319386
freq['s'] = 196844692
freq['h'] = 193607737
freq['r'] = 184990759
freq['d'] = 134044565
freq['l'] = 125951672
freq['u'] = 88219598
freq['c'] = 79962026
freq['m'] = 79502870
freq['f'] = 72967175
freq['w'] = 69069021
freq['g'] = 61549736
freq['y'] = 59010696
freq['p'] = 55746578
freq['b'] = 47673928
freq['v'] = 30476191
freq['k'] = 22969448
freq['x'] = 5574077
freq['j'] = 4507165
freq['q'] = 3649838
freq['z'] = 2456495

def do_score(candidate: bytes) -> int:
    total_score = 0
    for byte in candidate:
        char_score = freq.get(chr(byte), 0)
        total_score += char_score
    return total_score

def find_xor_key(i, block):
    best_key = None
    best_score = 0
    best_cand = None
    for k in range(256):
        candidate = xor(block, bytes([k]))
        score = do_score(candidate)
        if score > best_score:
            best_score = score
            best_key = k
            best_cand = candidate
    return bytes([best_key])

def exploit():
    ciphertexts = parse_ciphertexts()
    print("Found {} ciphertexts".format(len(ciphertexts)))

    min_len = 99999999
    for ct in ciphertexts:
        if len(ct) < min_len:
            min_len = len(ct)
    num_blocks_to_solve = min_len % BLOCK_SIZE

    # Transpose into blocks of byte 0 of every block, byte 1 of every block, etc.
    # Each block will all encrypted with the same key.
    pseudo_blocks = [[b"" for _ in range(BLOCK_SIZE)] for _ in range(num_blocks_to_solve)]
    for ct in ciphertexts:
        blocks = get_chunks(ct, BLOCK_SIZE)
        for (block_i, block) in enumerate(blocks[:num_blocks_to_solve]):
            for (byte_i, byte) in enumerate(block):
                pseudo_blocks[block_i][byte_i] += bytes([byte])

    # Search though the blocks to find the best candidate key for each
    block_keys = []
    for (block_i, block) in enumerate(pseudo_blocks):
        key = b""
        for byte_block in block:
            key += find_xor_key(block_i, byte_block)
        block_keys.append(key)

    # Use the keys to decrypt each block
    print("PLAINTEXTS")
    for ct in ciphertexts:
        blocks = get_chunks(ct, BLOCK_SIZE)
        plaintext = b""
        for (i, key) in enumerate(block_keys):
            #  plaintext += xor(blocks[i], key)
            plaintext += xor(key, blocks[i])
        print(plaintext.decode("unicode_escape"))

exploit()
```
