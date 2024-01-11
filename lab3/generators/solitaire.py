import sys
from collections import Counter

from lab3.generators.pseudo_random_generator import PseudoRandomGenerator

sys.path.append('')


class Solitaire(PseudoRandomGenerator):
    def __init__(self, seed: list[int]) -> None:
        super().__init__(seed)
        if Counter(seed) != Counter([*range(1, 55)]):
            raise Exception("Invalid seed")
        self.seed = seed.copy()
        self.initial_seed = seed.copy()

    def reset(self) -> None:
        self.seed = self.initial_seed.copy()

    def gen_half(self, n: int) -> bytes:
        seq = []
        pack_size = len(self.seed)
        while len(seq) < n:
            # a)
            w_joker = self.seed.index(53)
            if w_joker == pack_size - 1:
                self.seed[1], self.seed[2:] = self.seed[w_joker], self.seed[1:w_joker]
                w_joker = 1
            else:
                self.seed[w_joker + 1], self.seed[w_joker] = self.seed[w_joker], self.seed[w_joker + 1]
                w_joker += 1
            # b)
            b_joker = self.seed.index(54)
            if b_joker == pack_size - 2:
                self.seed[1], self.seed[2:] = self.seed[b_joker], self.seed[1:b_joker] + self.seed[b_joker + 1:]
                b_joker = 1
            elif b_joker == pack_size - 1:
                self.seed[2], self.seed[3:] = self.seed[b_joker], self.seed[2:b_joker]
                b_joker = 2
            else:
                self.seed[b_joker + 2], self.seed[b_joker:b_joker + 2] = self.seed[b_joker], self.seed[
                                                                                             b_joker + 1:b_joker + 3]
                b_joker += 2
            # c)
            joker_1, joker_2 = min(w_joker, b_joker), max(w_joker, b_joker)
            self.seed = self.seed[joker_2 + 1:] + self.seed[joker_1:joker_2 + 1] + self.seed[:joker_1]
            # d)
            cards_to_count = min(self.seed[-1], 53)
            self.seed[:-1] = self.seed[cards_to_count:-1] + self.seed[:cards_to_count]
            # e)
            if self.seed[0] < 53:
                seq.append(self.seed[self.seed[0]])
        return bytes(seq)

    def gen(self, n: int) -> bytes:
        seq1 = self.gen_half(n)
        seq2 = self.gen_half(n)
        return bytes((a & 0x0F) | ((b << 4) & 0xF0) for (a, b) in zip(seq1, seq2))
