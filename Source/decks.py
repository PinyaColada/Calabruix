from typing import Optional, Set, List
from pieces import *

COLORS = [WHITE, BLACK] = [True, False]
Color = bool


class Deck:
    def __init__(self, white_pieces: List[Optional[Piece]], black_pieces: List[Optional[Piece]]):
        self.white_pieces = white_pieces
        self.black_pieces = black_pieces

    def get_deck(self, color: Color) -> List[Optional[Piece]]:
        return self.white_pieces if color is WHITE else self.black_pieces

    def get_set_pieces(self, color: Color) -> Set:
        set_pieces = set(self.white_pieces if color is WHITE else self.black_pieces)
        set_pieces.add(Pawn(color))
        set_pieces.discard(None)
        return set_pieces

    def get_prom_pieces(self, color: Color) -> Set:
        set_pieces = set(self.white_pieces) if color is WHITE else set(self.black_pieces)
        set_pieces.discard(King(WHITE) if color is WHITE else King(BLACK))
        set_pieces.discard(None)
        return {piece for piece in set_pieces if piece.can_be_promotion}

    def weight_deck(self, color: Color) -> int:
        return sum(piece.price for piece in self.get_deck(color))

    def is_castling_pieces_at_extremes(self, color: Color) -> bool:
        color_pieces = self.get_deck(color)
        left_piece = color_pieces[0]
        right_piece = color_pieces[-1]
        return left_piece is not None and left_piece.can_castle and right_piece is not None and right_piece.can_castle

    def is_more_than_one_king(self, color: Color) -> bool:
        return self.get_deck(color).count(King(color)) > 1

    def is_king_in_place(self, color: Color) -> bool:
        if self.get_deck(color)[4] != King(color):
            return False
        return True

    def is_deck_legal(self) -> bool:
        if self.weight_deck(WHITE) > 64:
            return False
        if self.weight_deck(BLACK) > 66:
            return False
        if not self.is_castling_pieces_at_extremes(WHITE) or not self.is_castling_pieces_at_extremes(BLACK):
            return False
        if self.is_more_than_one_king(WHITE) or self.is_more_than_one_king(BLACK):
            return False
        if self.is_king_in_place(WHITE) or self.is_king_in_place(BLACK):
            return False
        return True