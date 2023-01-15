from typing import Optional, Set, List
from pieces import *
from random import randint

COLORS = [WHITE, BLACK] = [True, False]
Color = bool

# A deck consist of 8 pieces of each color, the white deck and the black deck can be different, due to the black pieces
# having more points in compensation of playing second


class Deck:
    def __init__(self, white_pieces: List[Optional[Piece]] = None, black_pieces: List[Optional[Piece]] = None):
        self.white_pieces = self.create_random_deck(WHITE)
        self.black_pieces = self.create_random_deck(BLACK)

    def get_deck(self, color: Color) -> List[Optional[Piece]]:
        return self.white_pieces if color is WHITE else self.black_pieces

    def get_set_pieces(self, color: Color) -> Set:
        set_pieces = set(self.white_pieces if color is WHITE else self.black_pieces)
        set_pieces.add(Pawn(color))
        set_pieces.discard(None)
        return set_pieces

    def get_prom_pieces(self, color: Color) -> Set:
        """Get all the pieces that a pawn can be promoted from the deck"""
        set_pieces = set(self.white_pieces) if color is WHITE else set(self.black_pieces)
        set_pieces.discard(King(WHITE) if color is WHITE else King(BLACK))
        set_pieces.discard(None)
        return {piece for piece in set_pieces if piece.can_be_promotion}

    def weight_deck(self, color: Color) -> int:
        """Return how many points have been used with the deck"""
        return sum(piece.price for piece in self.get_deck(color))

    def is_castling_pieces_at_extremes(self, color: Color) -> bool:
        """The castling pieces must be at the extremes of the deck and nowhere else"""
        color_pieces = self.get_deck(color)
        left_piece = color_pieces[0]
        right_piece = color_pieces[-1]
        return left_piece is not None and left_piece.can_castle and right_piece is not None and right_piece.can_castle

    def is_more_than_one_king(self, color: Color) -> bool:
        """A deck can only have one king"""
        return self.get_deck(color).count(King(color)) > 1

    def is_king_in_place(self, color: Color) -> bool:
        """A king must always be in the deck and in the forth position"""
        if self.get_deck(color)[4] != King(color):
            return False
        return True

    def create_random_castling_piece(self, color: Color) -> Piece:
        """Create a random castling piece"""
        if color:
            piece = WHITE_CASTLE_PIECES[randint(0, len(WHITE_CASTLE_PIECES) - 1)]
        else:
            piece = BLACK_CASTLE_PIECES[randint(0, len(BLACK_CASTLE_PIECES) - 1)]
        return piece

    def create_random_unique_piece(self, color: Color) -> Piece:
        """Create a random unique piece"""
        if color:
            piece = WHITE_UNIQUE_PIECES[randint(0, len(WHITE_UNIQUE_PIECES) - 1)]
        else:
            piece = BLACK_UNIQUE_PIECES[randint(0, len(BLACK_UNIQUE_PIECES) - 1)]
        return piece

    def create_random_common_piece(self, color: Color) -> Piece:
        """Create a random common piece"""
        if color:
            piece = WHITE_COMMON_PIECES[randint(0, len(WHITE_COMMON_PIECES) - 1)]
        else:
            piece = BLACK_COMMON_PIECES[randint(0, len(BLACK_COMMON_PIECES) - 1)]
        return piece

    def create_random_deck(self, color: Color):
        """Create a random deck of pieces following the basic rules, but not the weight rules"""
        deck: List = [None] * 8
        deck[4] = King(color)
        deck[3] = self.create_random_unique_piece(color)
        deck[0] = self.create_random_castling_piece(color)
        deck[-1] = self.create_random_castling_piece(color)
        for i in range(8):
            if deck[i] is None:
                deck[i] = self.create_random_common_piece(color)
        return deck

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
