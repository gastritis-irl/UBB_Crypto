from typing import Union


class PseudoRandomGenerator:
    def __init__(self, seed: Union[int, list[int]]) -> None:
        self.seed = seed
        self.initial_seed = seed

    def gen(self, n: int) -> bytearray:
        pass

    def reset(self) -> None:
        self.seed = self.initial_seed

    def skip(self, n: int) -> None:
        self.gen(n)
