import random
import time
import datetime
import base64
import os

os.environ['TZ'] = 'US/Eastern'
time.tzset()

from Crypto.Cipher import AES
flag = b"flag{THIS_IS_A_FLAG}"
iv = b"\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"

for i in range(0, 16-(len(flag) % 16)):
    flag += b"\0"

ts = time.time()

print("Flag Encrypted on %s" % datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M'))
seed = round(ts*1000)
print(seed)

random.seed(seed)

key = []
for i in range(0,16):
    key.append(random.randint(0,255))

key = bytearray(key)


cipher = AES.new(key, AES.MODE_CBC, iv)
ciphertext = cipher.encrypt(flag)

print(base64.b64encode(ciphertext).decode('utf-8'))
