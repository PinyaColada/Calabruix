from chess_deck import ChessDeck
from bitboards import BitboardManager
from computer import ComputerManager
from move import Move
from pieces import *
from decks import Deck

if __name__ == '__main__':
    bbm = BitboardManager()
    cpm = ComputerManager()
    basic_deck = Deck(white_pieces=[Rook(True), Knight(True), Bishop(True), Queen(True), King(True), Bishop(True), Knight(True), Rook(True)],
                      black_pieces=[Rook(False), Knight(False), Bishop(False), Queen(False), King(False), Bishop(False), Knight(False), Rook(False)])
    chess = ChessDeck(white_pieces_deck=basic_deck, black_pieces_deck=basic_deck, fen="1b1k4/r6r/5n2/Bn6/8/8/8/K2R4 b - - 0 1")

    chess.start_game()
