# Skiddyana Pwnz and the Loom of Fate

> Enter an ancient place, contrived beyond reason, and alter the fate of this world.
> nc 0.cloud.chals.io 33616

### Functions
```
func main
1. Enter room of loom
   - `loomRoom(prophecy_str, local_str)`
2. Read wall of prophecy
   - `print("%s", prophecy_str)`
3. Enter the room of fates
   - `fgets(usr_phrase_str, 26)`
   - If pass matches, `fatesRoom(prophecy_str)`

func loomDummy(param_1, param_2) # sets new prophecy
    fgets(input_str, 286)
    if (inputLen < 257) strcpy(param_2, input_str)
    return input_str

func fatesRoom(param_1) # overflows
    strcpy(local_overflow_target, param_1)

func theVoid
    Prints the flag
```

### Exploit Path
1. Leak the password (or change to our value) loomRoom
2. Overwrite a return pointer in fatesRoom to go to the void

Overwrite the prophecy string with the password addr and print it.


Enter fates room and select yes to copy the param value into the target. This
does.. something?

Can we control the param value?

