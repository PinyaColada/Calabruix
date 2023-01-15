from typing import Iterator
from computer import BB_ALL, BB_FILES, BB_SQUARES
Bitboard = int
Square = int


class BitboardManager:
    def shift_down(self, b: Bitboard) -> Bitboard:
        return b >> 8

    def shift_2_down(self, b: Bitboard) -> Bitboard:
        return b >> 16

    def shift_up(self, b: Bitboard) -> Bitboard:
        return (b << 8) & BB_ALL

    def shift_2_up(self, b: Bitboard) -> Bitboard:
        return (b << 16) & BB_ALL

    def shift_right(self, b: Bitboard) -> Bitboard:
        return (b << 1) & ~BB_FILES[0] & BB_ALL

    def shift_2_right(self, b: Bitboard) -> Bitboard:
        return (b << 2) & ~BB_FILES[0] & ~BB_FILES[2] & BB_ALL

    def shift_left(self, b: Bitboard) -> Bitboard:
        return (b >> 1) & ~BB_FILES[-1]

    def shift_2_left(self, b: Bitboard) -> Bitboard:
        return (b >> 2) & ~BB_FILES[-2] & ~BB_FILES[-1]

    def shift_up_left(self, b: Bitboard) -> Bitboard:
        return (b << 7) & ~BB_FILES[-1] & BB_ALL

    def shift_up_right(self, b: Bitboard) -> Bitboard:
        return (b << 9) & ~BB_FILES[0] & BB_ALL

    def shift_down_left(self, b: Bitboard) -> Bitboard:
        return (b >> 9) & ~BB_FILES[-1]

    def shift_down_right(self, b: Bitboard) -> Bitboard:
        return (b >> 7) & ~BB_FILES[0]

    def is_one_bit_on(self, bb: Bitboard) -> int:
        return self.msb(bb) == self.lsb(bb)

    def lsb(self, bb: Bitboard) -> int:
        """Given a bitboard, returns the index of the least significant bit.
        The least significant bit is the bit with the lowest index.
        https://www.chessprogramming.org/BitScan
        """
        return (bb & -bb).bit_length() - 1

    def scan_forward(self, bb: Bitboard) -> Iterator[Square]:
        """Given a bitboard, return an iterator that yields the indices of the set bits. The least significant bit is yielded first."""
        while bb:
            r = bb & -bb
            yield r.bit_length() - 1
            bb ^= r

    def msb(self, bb: Bitboard) -> int:
        """Given a bitboard, returns the index of the most significant bit. The procedure is similar to the lsb procedure.
        https://www.chessprogramming.org/BitScan"""
        return bb.bit_length() - 1

    def scan_reversed(self, bb: Bitboard) -> Iterator[Square]:
        """Given a bitboard, return an iterator that yields the indices of the set bits. The most significant bit is yielded first."""
        while bb:
            r = bb.bit_length() - 1
            yield r
            bb ^= BB_SQUARES[r]

    def bb_to_str(self, b: Bitboard) -> str:
        """Given a bitboard, returns a string representation of the board.
        Checks if the bitboard is normal or an inversed bitboard."""
        b = self.flip_vertical(b)
        sign = 0 if bin(b)[0] == "0" else 1
        aux = [(b >> shift_ind) & 1 for shift_ind in range(b.bit_length())]
        [aux.append(sign) for _ in range(64 - len(aux))]
        aux = map(lambda x: str(x[1]) + " " + "\n" if not (x[0] + 1) % 8 else str(x[1]) + " ", enumerate(aux))
        return "".join(list(aux))

    def flip_vertical(self, bb: Bitboard) -> Bitboard:
        """Given a bitboard, returns the bitboard with the vertical axis flipped.
        https://www.chessprogramming.org/Flipping_Mirroring_and_Rotating"""
        bb = ((bb >> 8) & 0x00ff_00ff_00ff_00ff) | ((bb & 0x00ff_00ff_00ff_00ff) << 8)
        bb = ((bb >> 16) & 0x0000_ffff_0000_ffff) | ((bb & 0x0000_ffff_0000_ffff) << 16)
        bb = (bb >> 32) | ((bb & 0x0000_0000_ffff_ffff) << 32)
        return bb

    def flip_horizontal(self, bb: Bitboard) -> Bitboard:
        """Given a bitboard, returns the bitboard with the horizontal axis flipped.
        https://www.chessprogramming.org/Flipping_Mirroring_and_Rotating"""
        bb = ((bb >> 1) & 0x5555_5555_5555_5555) | ((bb & 0x5555_5555_5555_5555) << 1)
        bb = ((bb >> 2) & 0x3333_3333_3333_3333) | ((bb & 0x3333_3333_3333_3333) << 2)
        bb = ((bb >> 4) & 0x0f0f_0f0f_0f0f_0f0f) | ((bb & 0x0f0f_0f0f_0f0f_0f0f) << 4)
        return bb

    def flip_diagonal(self, bb: Bitboard) -> Bitboard:
        """Given a bitboard, returns the bitboard with the diagonal axis flipped.
        https://www.chessprogramming.org/Flipping_Mirroring_and_Rotating"""
        t = (bb ^ (bb << 28)) & 0x0f0f_0f0f_0000_0000
        bb = bb ^ t ^ (t >> 28)
        t = (bb ^ (bb << 14)) & 0x3333_0000_3333_0000
        bb = bb ^ t ^ (t >> 14)
        t = (bb ^ (bb << 7)) & 0x5500_5500_5500_5500
        bb = bb ^ t ^ (t >> 7)
        return bb

    def flip_anti_diagonal(self, bb: Bitboard) -> Bitboard:
        """Given a bitboard, returns the bitboard with the anti-diagonal axis flipped.
        https://www.chessprogramming.org/Flipping_Mirroring_and_Rotating"""
        t = bb ^ (bb << 36)
        bb = bb ^ ((t ^ (bb >> 36)) & 0xf0f0_f0f0_0f0f_0f0f)
        t = (bb ^ (bb << 18)) & 0xcccc_0000_cccc_0000
        bb = bb ^ t ^ (t >> 18)
        t = (bb ^ (bb << 9)) & 0xaa00_aa00_aa00_aa00
        bb = bb ^ t ^ (t >> 9)
        return bb