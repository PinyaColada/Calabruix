from chess_deck import ChessDeck
from bitboards import BitboardManager
from computer import ComputerManager
from move import Move
from pieces import *
from decks import Deck

if __name__ == '__main__':
    bbm = BitboardManager()
    cpm = ComputerManager()
    basic_deck = Deck(white_pieces=[Wall(True), Knight(True), Bishop(True), Queen(True), King(True), Bishop(True), Knight(True), Ghost(True)],
                      black_pieces=[Chancellor(False), Knight(False), Bishop(False), Queen(False), King(False), Bishop(False), Knight(False), Rook(False)])
    chess = ChessDeck(white_pieces_deck=basic_deck, black_pieces_deck=basic_deck)

    chess.start_game()
