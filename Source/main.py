from chess_deck import ChessDeck
from bitboards import BitboardManager
from computer import ComputerManager
from move import Move
from pieces import *
from decks import Deck

if __name__ == '__main__':
    basic_deck = Deck()
    chess = ChessDeck(white_pieces_deck=basic_deck, black_pieces_deck=basic_deck)

    chess.start_game()
