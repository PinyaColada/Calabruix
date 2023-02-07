from typing import Iterable, Iterator, List, Dict, Tuple

Square = int
Bitboard = int

BB_EMPTY = 0
BB_ALL = 0xffff_ffff_ffff_ffff

SQUARES = [
    A1, B1, C1, D1, E1, F1, G1, H1,
    A2, B2, C2, D2, E2, F2, G2, H2,
    A3, B3, C3, D3, E3, F3, G3, H3,
    A4, B4, C4, D4, E4, F4, G4, H4,
    A5, B5, C5, D5, E5, F5, G5, H5,
    A6, B6, C6, D6, E6, F6, G6, H6,
    A7, B7, C7, D7, E7, F7, G7, H7,
    A8, B8, C8, D8, E8, F8, G8, H8,
] = range(64)

BB_SQUARES = [
    BB_A1, BB_B1, BB_C1, BB_D1, BB_E1, BB_F1, BB_G1, BB_H1,
    BB_A2, BB_B2, BB_C2, BB_D2, BB_E2, BB_F2, BB_G2, BB_H2,
    BB_A3, BB_B3, BB_C3, BB_D3, BB_E3, BB_F3, BB_G3, BB_H3,
    BB_A4, BB_B4, BB_C4, BB_D4, BB_E4, BB_F4, BB_G4, BB_H4,
    BB_A5, BB_B5, BB_C5, BB_D5, BB_E5, BB_F5, BB_G5, BB_H5,
    BB_A6, BB_B6, BB_C6, BB_D6, BB_E6, BB_F6, BB_G6, BB_H6,
    BB_A7, BB_B7, BB_C7, BB_D7, BB_E7, BB_F7, BB_G7, BB_H7,
    BB_A8, BB_B8, BB_C8, BB_D8, BB_E8, BB_F8, BB_G8, BB_H8,
] = [1 << sq for sq in range(64)]

BB_CORNERS = BB_A1 | BB_H1 | BB_A8 | BB_H8

BB_FILES = [
    BB_FILE_A,
    BB_FILE_B,
    BB_FILE_C,
    BB_FILE_D,
    BB_FILE_E,
    BB_FILE_F,
    BB_FILE_G,
    BB_FILE_H,
] = [0x0101_0101_0101_0101 << i for i in range(8)]

BB_RANKS = [
    BB_RANK_1,
    BB_RANK_2,
    BB_RANK_3,
    BB_RANK_4,
    BB_RANK_5,
    BB_RANK_6,
    BB_RANK_7,
    BB_RANK_8,
] = [0xff << (8 * i) for i in range(8)]

FILE_NAMES = ["a", "b", "c", "d", "e", "f", "g", "h"]
RANK_NAMES = ["1", "2", "3", "4", "5", "6", "7", "8"]
SQUARE_NAMES = [f + r for r in RANK_NAMES for f in FILE_NAMES]
BB_PROMOTION_RANKS = BB_RANK_1 | BB_RANK_8


class ComputerManager:
    @staticmethod
    def compute_square(name: str) -> Square:
        return SQUARE_NAMES.index(name)

    @staticmethod
    def compute_square_name(sq: Square) -> str:
        return SQUARE_NAMES[sq]

    @staticmethod
    def compute_rank(sq: Square) -> int:
        return sq >> 3

    @staticmethod
    def compute_file(sq: Square) -> int:
        return sq & 7

    def compute_distance(self, a: Square, b: Square) -> int:
        return max(abs(self.compute_file(a) - self.compute_file(b)), abs(self.compute_rank(a) - self.compute_rank(b)))

    def compute_edges(self, sq: Square) -> Bitboard:
        """
        Returns a bitboard with the edges that a rook would go if the board was empty.
        """
        edges = (((BB_RANK_1 | BB_RANK_8) & ~BB_RANKS[self.compute_rank(sq)] |
                  ((BB_FILE_A | BB_FILE_H) & ~BB_FILES[self.compute_file(sq)])))
        return edges

    def compute_sliding_attacks(self, square: Square, occupied: Bitboard, deltas: Iterable[int]) -> Bitboard:
        """
        The compute_sliding_attacks function takes a square and a bitboard of occupied squares as arguments.
        It then iterates through the eight directions (north, northeast, etc.) in which pieces slide.
        For each direction, it iterates through the squares that are one square away from the given square in that direction.
        If the square is occupied it adds the attack and then breaks out of the loop.
        """
        attacks = BB_EMPTY
        for delta in deltas:
            sq = square
            while True:
                sq += delta
                if not (0 <= sq < 64) or self.compute_distance(sq, sq - delta) > 2:
                    break

                attacks |= BB_SQUARES[sq]
                if occupied & BB_SQUARES[sq]:
                    break

        return attacks

    def compute_step_attacks(self, square: Square, deltas: Iterable[int]) -> Bitboard:
        """
        It calls the compute_sliding_attacks function with a filled bitboard as the occupied squares.
        This way it will do only one iteration of the slide.
        """
        return self.compute_sliding_attacks(square, BB_ALL, deltas)

    def compute_mask_attack_table(self, deltas: List[int]) -> Tuple[List[Bitboard], List[Dict[Bitboard, Bitboard]]]:
        """
        The compute_mask_attack_table function computes a table of masks and attack tables.
        The mask table is an array of bitboards, one for each square on the board.  The attack_table is also an array, but of dictionaries.
        The key is a bitboard of occupied squares, and the value is the bitboard of attacks for that particular mask and occupied squares.
        """
        mask_table = []
        attack_table = []
        for square in range(64):
            attacks = {}
            mask = self.compute_sliding_attacks(square, BB_EMPTY, deltas) & ~self.compute_edges(square)
            for subset in self.compute_gen_carry_rippler(mask):
                attacks[subset] = self.compute_sliding_attacks(square, subset, deltas)

            attack_table.append(attacks)
            mask_table.append(mask)

        return mask_table, attack_table

    def compute_gen_carry_rippler(self, mask: Bitboard) -> Iterator[Bitboard]:
        """Carry rippler algorithm to traverse all subsets of a bitboard
        More info at https://www.chessprogramming.org/Carry_Rippler"""
        subset = BB_EMPTY
        while True:
            yield subset
            subset = (subset - mask) & mask
            if not subset:
                break

    def compute_rays(self) -> List[List[Bitboard]]:
        """
        The compute_rays function computes the set of all rays, a ray being a set of squares that are on the same rank, file, or diagonal as a given square.
        """
        ray_list = []
        for index_a, bb_a in enumerate(BB_SQUARES):
            rays_row = []
            for index_b, bb_b in enumerate(BB_SQUARES):
                if BB_DIAG_ATTACK[index_a][0] & bb_b:
                    rays_row.append((BB_DIAG_ATTACK[index_a][0] & BB_DIAG_ATTACK[index_b][0]) | bb_a | bb_b)
                elif BB_RANK_ATTACK[index_a][0] & bb_b:
                    rays_row.append(BB_RANK_ATTACK[index_a][0] | bb_a)
                elif BB_FILE_ATTACK[index_a][0] & bb_b:
                    rays_row.append(BB_FILE_ATTACK[index_a][0] | bb_a)
                else:
                    rays_row.append(BB_EMPTY)
            ray_list.append(rays_row)
        return ray_list

    def compute_ray(self, a: Square, b: Square) -> Bitboard:
        """Return a ray from two squares, if they are on the same rank, file or diagonal"""
        return RAYS[a][b]

    def compute_between(self, a: Square, b: Square) -> Bitboard:
        """The compute_between function computes the set of squares between two squares on the same rank, file, or diagonal."""
        bb = RAYS[a][b] & ((BB_ALL << a) ^ (BB_ALL << b))
        return bb & (bb - 1)


BB_DIAG_MASK, BB_DIAG_ATTACK = ComputerManager().compute_mask_attack_table([7, 9, -7, -9])
BB_FILE_MASK, BB_FILE_ATTACK = ComputerManager().compute_mask_attack_table([-8, 8])
BB_RANK_MASK, BB_RANK_ATTACK = ComputerManager().compute_mask_attack_table([-1, 1])

RAYS = ComputerManager().compute_rays()
