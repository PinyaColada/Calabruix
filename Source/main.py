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
    chess.push(Move(cpm.compute_square("e2"), cpm.compute_square("e4")))
    chess.push(Move(cpm.compute_square("e7"), cpm.compute_square("e5")))
    chess.push(Move(cpm.compute_square("d1"), cpm.compute_square("h5")))
    chess.push(Move(cpm.compute_square("d7"), cpm.compute_square("d6")))
    chess.push(Move(cpm.compute_square("f1"), cpm.compute_square("c4")))
    chess.push(Move(cpm.compute_square("g8"), cpm.compute_square("f6")))

    chess.start_game()
