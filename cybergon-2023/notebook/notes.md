# Findings

- in add() the content is malloced but doesn't have to be written to, this might
  have stuff in it if we do things if we do things

- the fgets(256) in edit() lets us read past where we should and segfalt the
  program in a few ways. It can be used to ovewrite the note item pointers in
  notes_list and might be able to go all the way to the return pointer of edit.

  This might allow us to get arbitrary reads with view()

  Then we can get writes by overwriting an item in the list to a pointer, we can
  then use add() with that index and write 8 bytes of content there

- there's a win function which just calls puts. Maybe we can use that if we
  control rdx or overwrite puts@plt or somthing

- No PIE so doing this might be easy
  Ovewrite as follows:
  1. add note so it exists
  2. edit note so we can try and overwrite something
  3. view to leak?
  4. ovewrite again with edit so we can write now
  5. use ad to write somehow

- This seems heap-groomy except there are no free calls

- Heap allocations are 128 bytes away, with next chunk 32 bytes
- Heap allocations are 64 bytes away, with next chunk 32 bytes
- On edit: 32 bytes + 8 bytes where the A is the next hunk

- The last value gets decremented by 32 each time

```
Before write:
pwndbg> x/32gx $rax
0x4ae300:       0x000000000000000a      0x0000000000000000
0x4ae310:       0x0000000000000000      0x0000000000020cf2

Last chunk


Healthy Two Note Heap:

0x1fec2a0:      0x0000000001fec2c0      0x0000000000000000 * first start
0x1fec2b0:      0x0000000000000000      0x0000000000000021
0x1fec2c0:      0x0041414141414141      0x0000000000000000
0x1fec2d0:      0x0000000000000000      0x0000000000000021
0x1fec2e0:      0x0000000001fec300      0x0000000000000000
0x1fec2f0:      0x0000000000000000      0x0000000000000021
0x1fec300:      0x000000000000000a      0x0000000000000000
0x1fec310:      0x0000000000000000      0x0000000000000021
0x1fec320:      0x0000000001fec340      0x0000000000000000 * second start
0x1fec330:      0x0000000000000000      0x0000000000000021
0x1fec340:      0x0042424242424242      0x0000000000000000
0x1fec350:      0x0000000000000000      0x0000000000000021
0x1fec360:      0x0000000001fec380      0x0000000000000000 * the value here is what we write
0x1fec370:      0x0000000000000000      0x0000000000000021   when we use edit
0x1fec380:      0x000000000000000a      0x0000000000000000
0x1fec390:      0x0000000000000000      0x0000000000020c71

Chunk format:
p64(size) + 

```

