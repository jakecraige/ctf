# Notes
- Sets up a segfault handler that prints the flag:?!!
- Reads input in 100 byte buffer with `gets` (UNSAFE)
- Calls `vuln` which creates a 16 byte buffer and copies into it

# Writeup
- Gives it a long input to overrun the return pointer and crash which prints
  flag
