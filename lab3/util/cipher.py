from lab3.generators.pseudo_random_generator import PseudoRandomGenerator


class Cipher:
    def __init__(self, generator: PseudoRandomGenerator) -> None:
        self.generator = generator
        self.offset = 0

    def get_offset(self) -> int:
        return self.offset

    def encrypt(self, message: bytes) -> bytes:
        length = len(message)
        self.offset += length
        return bytes(a ^ b for (a, b) in zip(message, self.generator.gen(length)))

    def decrypt(self, message: bytes, offset: int) -> bytes:
        length = len(message)

        if offset == self.offset:
            self.offset += length
        elif offset > self.offset:
            self.offset = offset + length
            self.generator.skip(offset - self.offset)
        else:
            self.offset = offset + length
            self.generator.reset()
            self.generator.skip(offset)

        return bytes(a ^ b for (a, b) in zip(message, self.generator.gen(length)))
