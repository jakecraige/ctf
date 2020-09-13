# Perfect Secrecy (Crypto, 50 points)

> Alice sent over a couple of images with sensitive information to Bob,
> encrypted with a pre-shared key. It is the most secure encryption scheme,
> theoretically...

This challenge gives you two png images and asks you to find the flag. It tells
you that they used the same key to encrypt both and used "the most theoretically
secure encryption scheme" and the challenge is called "Perfect Secrecy".

The encryption scheme that provides perfect secrecy and is theoretically
perfect, is the one-time pad. This scheme is just `key XOR message`. The issue
with using the same key more than once is that if you XOR two ciphertexts
together, the key cancels out and you are left with the difference between the
plaintexts which leaks information.

```
ct1 XOR ct2
==
key XOR msg1 XOR key XOR msg2
==
msg1 XOR msg2
```

Knowing that they reused the key on these images, we XOR them together and store
the resulting image, which contains the flag.

```python
from PIL import Image, ImageChops

im1 = Image.open("image1.png")
im2 = Image.open("image2.png")

result = ImageChops.logical_xor(im1,im2)
result.save('result.png')
```

![result](result.png)
