# Notes
- No PIE and manual 4-byte stack canary added
- 64 byte buffer
- Win function is at `0x08049336`
- Canary is fixed value stored in canary.txt
- Asks how many bytes to write a character at a time
- It uses this value as input to `read(0, buf, count)` and we can overflow read
- Detects smashing if canary is overwritten with memcmp

**Problem**: We can brute force canary one-byte at a time because it's fixed

# Writeup
