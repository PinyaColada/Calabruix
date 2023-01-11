Color = bool
Square = int
Bitboard = int
COLORS = [WHITE, BLACK] = [True, False]

ALL_PIECES_DICT = {
    "w": "Wall",
    "n": "Knight",
    "b": "Bishop",
    "q": "Queen",
    "k": "King",
    "g": "Ghost",
    "c": "Chancellor",
    "r": "Rook",
    "p": "Pawn"
}


class Piece:
    def __init__(self, color):
        self.step_attacks = []
        self.diagonal_slide = False
        self.vertical_slide = False
        self.horizontal_slide = False
        self.symbol = ""
        self.name = ""
        self.color = color
        self.can_castle = False
        self.symmetry = True
        self.price = 0
        self.can_be_promotion = True

    def get_symbol(self):
        return self.symbol if self.color is WHITE else self.symbol.lower()

    def swap_color(self):
        self.color = not self.color

    def __eq__(self, other):
        if not isinstance(other, Piece):
            return False
        if hash(self) != hash(other):
            return False
        return True

    def __hash__(self):
        return hash(self.name) + hash(self.color)

    def __ne__(self, other):
        return not self.__eq__(other)


class King(Piece):
    def __init__(self, color: Color):
        Piece.__init__(self, color)
        self.step_attacks = [1, -1, 7, 8, 9, -7, -8, -9]
        self.name = "King"
        self.symbol = "K"
        self.price = 0
        self.can_be_promotion = False


class Pawn(Piece):
    def __init__(self, color: Color):
        Piece.__init__(self, color)
        self.step_attacks = [[7, 9], [-7, -9]]
        self.name = "Pawn"
        self.symbol = "P"
        self.symmetry = False
        self.price = 1
        self.can_be_promotion = False


class Bishop(Piece):
    def __init__(self, color: Color):
        Piece.__init__(self, color)
        self.diagonal_slide = True
        self.name = "Bishop"
        self.symbol = "B"
        self.price = 6


class Knight(Piece):
    def __init__(self, color: Color):
        Piece.__init__(self, color)
        self.step_attacks = [6, -6, 10, -10, 15, -15, 17, -17]
        self.name = "Knight"
        self.symbol = "N"
        self.price = 6


class Rook(Piece):
    def __init__(self, color: Color):
        Piece.__init__(self, color)
        self.vertical_slide = True
        self.horizontal_slide = True
        self.name = "Rook"
        self.symbol = "R"
        self.can_castle = True
        self.price = 10


class Queen(Piece):
    def __init__(self, color: Color):
        Piece.__init__(self, color)
        self.vertical_slide = True
        self.horizontal_slide = True
        self.diagonal_slide = True
        self.name = "Queen"
        self.symbol = "Q"
        self.price = 16


class Archbishop(Piece):
    def __init__(self, color: Color):
        Piece.__init__(self, color)
        self.diagonal_slide = True
        self.step_attacks = [6, -6, 10, -10, 15, -15, 17, -17]
        self.name = "Archbishop"
        self.symbol = "A"
        self.price = 12


class Chancellor(Piece):
    def __init__(self, color: Color):
        Piece.__init__(self, color)
        self.vertical_slide = True
        self.horizontal_slide = True
        self.step_attacks = [6, -6, 10, -10, 15, -15, 17, -17]
        self.name = "Chancellor"
        self.symbol = "C"
        self.can_castle = True
        self.price = 16


class Ghost(Piece):
    def __init__(self, color: Color):
        Piece.__init__(self, color)
        self.step_attacks = [8, 16, -8, -16, 1, 2, -1, -2]
        self.name = "Ghost"
        self.symbol = "G"
        self.can_castle = True
        self.price = 8


class Wall(Piece):
    def __init__(self, color: Color):
        Piece.__init__(self, color)
        self.name = "Wall"
        self.symbol = "W"
        self.can_castle = True
        self.price = 0
        self.can_be_promotion = False
