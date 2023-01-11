from typing import Dict, Set
from pieces import ALL_PIECES_DICT
from computer import BB_SQUARES, BB_EMPTY, ComputerManager
import re

Bitboard = int


class FenLoader:
    def __init__(self, fen_string: str, set_pieces: Set = None):
        fen = fen_string.split(" ")
        self.set_pieces = set_pieces
        self.board = self.process_fen(fen[0])
        self.turn = fen[1]
        self.castling = fen[2]
        self.en_passant = fen[3]
        self.halfmove_clock = fen[4]
        self.fullmove_number = fen[5]

    @staticmethod
    def process_fen(fen: str) -> str:
        fen = re.sub(r'\d', lambda x: '1' * int(x.group()), fen)
        fen = fen.split("/")[::-1]
        fen = "".join(fen)
        return fen

    def load_board(self) -> Dict:
        board = {
            "White": BB_EMPTY,
            "Black": BB_EMPTY,
            "All": BB_EMPTY,
            "En passant": BB_EMPTY,
            "Castling": BB_EMPTY
        }

        for piece in self.set_pieces:
            board[piece.name] = BB_EMPTY

        skipping = 0
        for i, piece in enumerate(self.board):
            if skipping > 0:
                skipping -= 1
                continue

            if piece.isdigit():
                skipping += int(piece) - 1
                continue

            if piece.lower() not in ALL_PIECES_DICT:
                continue

            board[ALL_PIECES_DICT[piece.lower()]] |= BB_SQUARES[i]

            if piece.isupper():
                board["White"] |= BB_SQUARES[i]
            else:
                board["Black"] |= BB_SQUARES[i]

            board["All"] |= BB_SQUARES[i]

        if self.en_passant != "-":
            board["En Passant"] = BB_SQUARES[ComputerManager.compute_square(self.en_passant)]

        if "K" in self.castling:
            board["Castling"] |= BB_SQUARES[ComputerManager.compute_square("h1")]
        if "Q" in self.castling:
            board["Castling"] |= BB_SQUARES[ComputerManager.compute_square("a1")]
        if "k" in self.castling:
            board["Castling"] |= BB_SQUARES[ComputerManager.compute_square("h8")]
        if "q" in self.castling:
            board["Castling"] |= BB_SQUARES[ComputerManager.compute_square("a8")]

        return board

    def load_turn(self) -> bool:
        return True if self.turn == "w" else False

    def load_halfmove_clock(self) -> int:
        return int(self.halfmove_clock)

    def load_fullmove_number(self) -> int:
        return int(self.fullmove_number)
