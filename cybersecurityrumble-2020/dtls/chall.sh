#!/bin/bash

# /usr/lib/libc.so.6|head -n 1
# GNU C Library (GNU libc) stable release version 2.31.

# clone
git clone https://github.com/eclipse/tinydtls.git dtls

# build
cd dtls && autoconf && autoheader && ./configure && make && cd ..

# listen
tcpdump -i lo  port 31337 -w dump.pcap &

# Wait for tcpdump...
sleep 2

# serve
dtls/tests/dtls-server -p 31337 &

# send flag
cat flag.txt|dtls/tests/dtls-client 127.0.0.1 -p 31337
