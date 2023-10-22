#!/usr/bin/env python3 -tt
"""
File: crypto.py
---------------
Assignment 1: Cryptography
Course: CS 41
Name: <YOUR NAME>
SUNet: <SUNet ID>

Replace this with a description of the program.
"""
import utils
import random


# Caesar Cipher

def encrypt_caesar(plaintext, shift=3):
    """Encrypt plaintext using a Caesar cipher.

    Add more implementation details here.
    :param plaintext:
    :param shift:
    """
    encrypted = ""
    for char in plaintext:
        if char.isalpha():
            shifted = ord(char) + shift
            if char.islower():
                if shifted > ord('z'):
                    shifted -= 26
            elif char.isupper():
                if shifted > ord('Z'):
                    shifted -= 26
            encrypted += chr(shifted)
        else:
            encrypted += char
    return encrypted


def decrypt_caesar(ciphertext, shift=3):
    """Decrypt a ciphertext using a Caesar cipher.

    Add more implementation details here.
    """
    return encrypt_caesar(ciphertext, -shift)


# Vigenere Cipher

def encrypt_vigenere(plaintext, keyword):
    """Encrypt plaintext using a Vigenere cipher with a keyword.

    Add more implementation details here.
    """
    encrypted = ""
    key_length = len(keyword)
    for i, char in enumerate(plaintext):
        if char.isalpha():
            shift = ord(keyword[i % key_length].lower()) - ord('a')
            encrypted += encrypt_caesar(char, shift)
        else:
            encrypted += char
    return encrypted


def decrypt_vigenere(ciphertext, keyword):
    """Decrypt ciphertext using a Vigenere cipher with a keyword.

    Add more implementation details here.
    """
    decrypted = ""
    key_length = len(keyword)
    for i, char in enumerate(ciphertext):
        if char.isalpha():
            shift = ord(keyword[i % key_length].lower()) - ord('a')
            decrypted += decrypt_caesar(char, shift)
        else:
            decrypted += char
    return decrypted


# Merkle-Hellman Knapsack Cryptosystem

def generate_private_key(n=8):
    """Generate a private key for use in the Merkle-Hellman Knapsack Cryptosystem.

    Following the instructions in the handout, construct the private key components
    of the MH Cryptosystem. This consistutes 3 tasks:

    1. Build a superincreasing sequence `w` of length n
        (Note: you can check if a sequence is superincreasing with `utils.is_superincreasing(seq)`)
    2. Choose some integer `q` greater than the sum of all elements in `w`
    3. Discover an integer `r` between 2 and q that is coprime to `q` (you can use utils.coprime)

    You'll need to use the random module for this function, which has been imported already

    Somehow, you'll have to return all of these values out of this function! Can we do that in Python?!

    @param n bitsize of message to send (default 8)
    @type n int

    @return 3-tuple `(w, q, r)`, with `w` a n-tuple, and q and r ints.
    """
    # 1. Generate a superincreasing sequence w of length n
    w = [random.randint(1, 5)]
    for _ in range(1, n):
        w.append(w[-1] + random.randint(1, 10))

    # 2. Choose an integer q greater than the sum of all elements in w
    q = w[-1] + random.randint(1, 10)

    # 3. Find an integer r such that it is coprime to q
    r = random.randint(2, q - 1)
    while not utils.coprime(r, q):
        r = random.randint(2, q - 1)

    return tuple(w), q, r


def create_public_key(private_key):
    """Create a public key corresponding to the given private key.

    To accomplish this, you only need to build and return `beta` as described in the handout.

        beta = (b_1, b_2, ..., b_n) where b_i = r × w_i mod q

    Hint: this can be written in one line using a list comprehension

    @param private_key The private key
    @type private_key 3-tuple `(w, q, r)`, with `w` a n-tuple, and q and r ints.

    @return n-tuple public key
    """
    w, q, r = private_key
    return tuple([(r * w_i) % q for w_i in w])


def encrypt_mh(message, public_key):
    """Encrypt an outgoing message using a public key.

    1. Separate the message into chunks the size of the public key (in our case, fixed at 8)
    2. For each byte, determine the 8 bits (the `a_i`s) using `utils.byte_to_bits`
    3. Encrypt the 8 message bits by computing
         c = sum of a_i * b_i for i = 1 to n
    4. Return a list of the encrypted ciphertexts for each chunk in the message

    Hint: think about using `zip` at some point

    @param message The message to be encrypted
    @type message bytes
    @param public_key The public key of the desired recipient
    @type public_key n-tuple of ints

    @return list of ints representing encrypted bytes
    """
    encrypted = []
    for byte in message:
        bits = utils.byte_to_bits(byte)
        encrypted.append(sum([bit * b for bit, b in zip(bits, public_key)]))
    return encrypted


def decrypt_mh(ciphertexts, private_key):
    """Decrypt an incoming message using a private key

    1. Extract w, q, and r from the private key
    2. Compute s, the modular inverse of r mod q, using the
        Extended Euclidean algorithm (implemented at `utils.modinv(r, q)`)
    3. For each byte-sized chunk, compute
         c' = cs (mod q)
    4. Solve the superincreasing subset sum using c' and w to recover the original byte
    5. Reconsitite the encrypted bytes to get the original message back

    @param ciphertexts Encrypted message chunks
    @type ciphertexts list of ints
    @param private_key The private key of the recipient
    @type private_key 3-tuple of w, q, and r

    @return bytearray or str of decrypted characters
    """
    w, q, r = private_key
    s = utils.modinv(r, q)
    decrypted = bytearray()

    for c in ciphertexts:
        c_prime = (c * s) % q
        bits = []
        for w_i in reversed(w):
            if w_i <= c_prime:
                bits.append(1)
                c_prime -= w_i
            else:
                bits.append(0)
        decrypted.append(utils.bits_to_byte(reversed(bits)))

    return decrypted
