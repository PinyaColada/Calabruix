from typing import Dict, Set
from pieces import SYMBOL_TO_NAME
from computer import BB_SQUARES, BB_EMPTY, ComputerManager
import re

Bitboard = int


class FenLoader:
    def __init__(self, fen_string: str, set_pieces: Set, dict_attacks: Dict):
        fen = fen_string.split(" ")
        self.set_pieces = set_pieces
        self.attacks = dict_attacks
        self.board = self.process_fen(fen[0])
        self.turn = fen[1]
        self.castling = fen[2]
        self.en_passant = fen[3]
        self.halfmove_clock = fen[4]
        self.fullmove_number = fen[5]

    @staticmethod
    def process_fen(fen: str) -> str:
        """It processes the fen string, so it's easier to process"""
        fen = re.sub(r'\d', lambda x: '1' * int(x.group()), fen)  # Replace the numbers with their respective number of 1s
        fen = fen.split("/")[::-1]  # Split by / and reverse the list
        fen = "".join(fen)  # Join the list
        return fen

    def load_board(self) -> Dict:
        board = {  # Each game state will always have this bitboards
            "White": BB_EMPTY,
            "Black": BB_EMPTY,
            "All": BB_EMPTY,
            "En passant": BB_EMPTY,
            "Castling": BB_EMPTY,
            "Invincible": BB_EMPTY,
            "Non capture": BB_EMPTY
        }

        for piece in self.set_pieces:
            board[piece.name] = BB_EMPTY

        for i, piece in enumerate(self.board):
            if piece.isdigit():
                continue

            if piece.lower() not in SYMBOL_TO_NAME:
                continue

            piece_name = SYMBOL_TO_NAME[piece.lower()]
            board[piece_name] |= BB_SQUARES[i]

            if piece.isupper():
                board["White"] |= BB_SQUARES[i]
            else:
                board["Black"] |= BB_SQUARES[i]
            board["All"] |= BB_SQUARES[i]

            if self.attacks[piece_name]['Invincible']:
                board["Invincible"] |= BB_SQUARES[i]

            if self.attacks[piece_name]['Non capture']:
                board["Non capture"] |= BB_SQUARES[i]

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
