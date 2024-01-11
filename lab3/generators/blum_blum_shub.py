from lab3.generators.pseudo_random_generator import PseudoRandomGenerator


class BlumBlumShub(PseudoRandomGenerator):
    def __init__(self, seed: int) -> None:
        super().__init__(seed)
        self.n = 11 * 23

    def gen(self, n: int) -> bytes:
        x = []
        for _i in range(n):
            byte = 0
            for _j in range(8):
                byte = (byte << 1) | (self.seed % 2)
                self.seed = self.seed ** 2 % self.n
            x.append(byte)
        return bytes(x)
