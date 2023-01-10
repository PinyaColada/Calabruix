from typing import Optional
from pieces import Piece
from computer import ComputerManager
Square = int
cpm = ComputerManager()


class Move:
    def __init__(self, from_sq: Square | str, to_sq: Square | str, promotion: Optional[Piece] = None):
        self.from_sq = cpm.compute_square(from_sq) if isinstance(from_sq, str) else from_sq
        self.to_sq = cpm.compute_square(to_sq) if isinstance(to_sq, str) else to_sq
        self.promotion = promotion

    def is_going_right(self) -> bool:
        return cpm.compute_file(self.from_sq) < cpm.compute_file(self.to_sq)

    def is_going_straight(self) -> bool:
        return cpm.compute_file(self.from_sq) == cpm.compute_file(self.to_sq)

    def is_promotion(self) -> bool:
        return self.promotion is not None

    def __str__(self):
        start = cpm.compute_square_name(self.from_sq)
        end = cpm.compute_square_name(self.to_sq)
        prom = "" if self.promotion is None else self.promotion.symbol.lower()
        return start + end + prom

    def __eq__(self, other):
        if not isinstance(other, Move):
            return False
        if self.from_sq != other.from_sq:
            return False
        if self.to_sq != other.to_sq:
            return False
        if self.promotion != other.promotion:
            return False
        return True
