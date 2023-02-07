from chess_deck import ChessDeck
from bitboards import BitboardManager
from computer import ComputerManager
from move import Move
from pieces import *
from decks import Deck

if __name__ == '__main__':
    cpm = ComputerManager()
    basic_deck = Deck(knook_deck=True)
    chess = ChessDeck(white_pieces_deck=basic_deck, black_pieces_deck=basic_deck, fen="1k6/8/8/8/8/8/PP2p3/1K6 b - - 0 1")
    chess.start_game()
