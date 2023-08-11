import random
import time
import datetime
import base64
import sys
import os
from Crypto.Cipher import AES

os.environ['TZ'] = 'US/Eastern'
time.tzset()

# Challenge data
enc_time = "2023-08-02 10:27"
enc_b64 = "lQbbaZbwTCzzy73Q+0sRVViU27WrwvGoOzPv66lpqOWQLSXF9M8n24PE5y4K2T6Y"

# Example Data generated locally in Python2.7.18
#  enc_time = "2023-08-10 19:23"
#  enc_b64 = "eHrFw5FbHspyFlRGOnI+SNKvR2UB3eKjbxaHprBvs0c="

# Example Data generated locally in Python3
#  enc_time = "2023-08-10 20:50"
#  enc_b64 = "4Gk06iOVQlnKy6PJkEZ+r9II5lvVt1f096XLfZSh4tg="

def decrypt():
    enc_time_datetime = datetime.datetime.strptime(enc_time, "%Y-%m-%d %H:%M")
    enc_flag = base64.b64decode(enc_b64)

    ts = time.mktime(enc_time_datetime.timetuple()) * 1000
    #  ts = enc_time_datetime.timestamp() * 1000
    iter_limit = 10000000
    print("Starting...")
    print(ts)
    print(ts+iter_limit, ts>1691715021004)

    #  ts = 1691714498192
    print(ts)

    for i in range(0, iter_limit):
        seed = round(ts+i)
        random.seed(seed)
        if seed % 500000 == 0:
            sys.stdout.write(".")
            sys.stdout.flush()

        key = []
        for i in range(0,16):
            key.append(random.randint(0,255))
        key = bytearray(key)

        iv = b"\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"

        cipher = AES.new(key, AES.MODE_CBC, iv)
        pt = cipher.decrypt(enc_flag)

        # filter output to something close to a flag
        if b'flag' in pt:
            print(pt)

decrypt()
