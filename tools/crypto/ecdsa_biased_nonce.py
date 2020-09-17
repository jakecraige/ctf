#!/usr/bin/python3
"""
A helper library for using lattice reduction to solve for ECDSA private keys
when the nonce has a known fixed-bit bias.

Based on: https://blog.trailofbits.com/2020/06/11/ecdsa-handle-with-care/
"""

import ecdsa
import olll
import random
from binascii import hexlify, unhexlify
from hashlib import sha1

def mod_inv(num, mod):
    """
    Based on Fermat's Little Theorem
           n^p   = n       mod p
           n^p-1 = 1       mod p
    (n^-1)*n^p-1 = 1(n*-1) mod p
           n^p-2 = n^-1    mod p
    """
    return pow(num, mod-2, mod)

def sig_decode(sig, n):
    """
    Attempts to decode a hex encoded signature into an (r, s) integer tuple,
    making some assumptions about common formats from the length.
    """
    sig = unhexlify(sig)
    n_bits = n.bit_length()
    n_bytes = int(n_bits / 8)

    if len(sig) == n_bytes*2: # Raw, padded R || S (assumed big-endian)
        return (
            int.from_bytes(sig[:n_bytes], "big"),
            int.from_bytes(sig[n_bytes:], "big"),
        )
    elif sig[0] == 0x30: # Assume DER
        return ecdsa.util.sigdecode_der(sig, n)
    else:
        raise Exception("Unable to decode sig of size: {}".format(len(sig)))

def ecdsa_solver(curve, bit_bias, raw_msg_and_sigs, expected_pubkey = None):
    """
    Uses the LLL algorithm to solve for the private key when signatures were
    generated with a fixed MSB bias. Does not currently handle non-MSB bias, but
    should be fairly easy to by multiplying by a power of 2 so that the fixed
    bits become the MSB.
    """
    g = curve.generator
    n = curve.order
    nonce_bound = 2**(n.bit_length()-bit_bias)
    msg_and_sigs = [(msg, sig_decode(sig, n)) for (msg, sig) in raw_msg_and_sigs]

    # Construct a matrix with our constants for the order and bound of the
    # biased nonce included in the right spots.
    mat_size = len(msg_and_sigs)+1
    matrix = [[0]*mat_size for _ in range(mat_size)]
    for (i, row) in enumerate(matrix[:-2]):
        row[i] = n
    matrix[-2][-2] = nonce_bound / n
    matrix[-1][-1] = nonce_bound

    # Precompute nth values to reuse when building the last matrix rows.
    m_n, (r_n, s_n) = msg_and_sigs[-1]
    s_n_inv = mod_inv(s_n, n)
    r_n_s_inv = r_n * s_n_inv
    m_n_s_inv = m_n * s_n_inv

    # Populate msg and sigs rows
    sig_row = matrix[-2]
    msg_row = matrix[-1]
    for (i, (msg, (r, s))) in enumerate(msg_and_sigs[:-1]):
        s_inv = mod_inv(s, n)
        sig_row[i] = r*s_inv - r_n_s_inv
        msg_row[i] = msg*s_inv - m_n_s_inv

    # If a public key wasn't provided, we'll just recover the two possibilities
    # from the signature and see which one works.
    expected_pubkeys = None
    if expected_pubkey is not None:
        expected_pubkeys = [expected_pubkey]
    else:
        sig = ecdsa.Signature(r_n, s_n)
        expected_pubkeys = sig.recover_public_keys(m_n, g)

    # Lastly, reduce and solve for priate key
    print("Reducing matrix...")
    reduced = olll.reduction(matrix, 0.75)
    print("Done, solving...")
    msg_1, (r_1, s_1) = msg_and_sigs[0]
    for possible_nonces in reduced:
        nonce_diff = possible_nonces[0]
        nonce_part = mod_inv(r_n*s_1 - r_1*s_n, n) # precomputed since it's static
        msg_part = s_n*msg_1 - s_1*m_n - s_1*s_n*nonce_diff
        # x = (r_n*s_1 - r_1*s_n)^-1 * (s_n*m_1 - s_1*m_n - s_1*s_n(k_1-k_n))
        privkey = (nonce_part * msg_part) % n

        for expected_pubkey in expected_pubkeys:
            if ecdsa.ecdsa.Public_key(g, g * privkey) == expected_pubkey:
                return privkey

def ecdsa_sign_biased(curve, hash_fn, int_privkey, msg, bit_bias):
    """
    Helper to produce nonces with a MSB fixed 0-bias of bit_bias length
    """
    pubkey = ecdsa.ecdsa.Public_key(curve.generator, curve.generator * int_privkey)
    privkey = ecdsa.ecdsa.Private_key(pubkey, int_privkey)
    nonce = random.randrange(1, curve.order)
    nonce >>= bit_bias
    digest = int.from_bytes(hash_fn(msg.encode()).digest(), "big")
    sig = privkey.sign(digest, nonce)
    order_bytes = int(curve.order.bit_length() / 8)
    raw_sig = sig.r.to_bytes(order_bytes, "big") + sig.s.to_bytes(order_bytes, "big")
    return (digest, raw_sig.hex())

if __name__ == '__main__':
    curve = ecdsa.NIST192p
    privkey = 1094795585
    bit_bias = 42
    msg_and_sigs = []
    for _ in range(6):
        # NOTE: message doesn't need to be the same, just doesn't have to be
        # different either :)
        res = ecdsa_sign_biased(curve, sha1, privkey, "hello", bit_bias)
        msg_and_sigs.append(res)

    priv = ecdsa_solver(curve, bit_bias, msg_and_sigs)
    if priv is not None:
        print("Found private key: {}".format(hex(priv)))
    else:
        print("Unable to find private key, double check the provided parameters and provide more signatures if possible.")
