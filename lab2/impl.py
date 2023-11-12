import random


def blum_blum_shub_key_generator(length, prime1=101, prime2=103, seed=123):
    N = prime1 * prime2
    x = seed
    byte_array = []
    for _ in range(length):
        byte = 0
        for _ in range(8):
            x = pow(x, 2, N)
            byte = (byte << 1) | (x & 1)
        byte_array.append(byte)
    return bytes(byte_array)


def solitaire_key_generator(length, deck_size=52, seed=None):
    deck = list(range(1, deck_size + 1)) + ["A", "B"]

    if seed is not None:
        random.seed(seed)

    def move_jokers():
        # Simplified joker movement steps
        a_index = deck.index("A")
        b_index = deck.index("B")
        deck.insert((a_index + 1) % len(deck), deck.pop(a_index))
        deck.insert((b_index + 2) % len(deck), deck.pop(b_index))

    key_stream = []
    for _ in range(length):
        move_jokers()
        top_card = deck[0]
        top_index = deck.index(top_card) if top_card != "A" and top_card != "B" else 53
        key_byte = deck[top_index] % 256
        key_stream.append(key_byte)

    return bytes(key_stream)


def stream_cipher(data, key_generator, *key_args):
    key_stream = key_generator(*key_args)
    return bytes([data_byte ^ key_byte for data_byte, key_byte in zip(data, key_stream)])
