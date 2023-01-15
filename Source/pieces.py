Color = bool
Square = int
Bitboard = int
COLORS = [WHITE, BLACK] = [True, False]

SYMBOL_TO_NAME = {
    "w": "Wall",
    "n": "Knight",
    "b": "Bishop",
    "q": "Queen",
    "k": "King",
    "g": "Ghost",
    "c": "Chancellor",
    "r": "Rook",
    "p": "Pawn",
    "f": "Frog",
    "h": "Archer",
    "z": "Amazon",
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
        self.is_unique = False
        self.can_be_promotion = True
        self.is_invincible = False
        self.can_capture = True

    def get_symbol(self):
        return self.symbol if self.color is WHITE else self.symbol.lower()

    def __str__(self):
        return ("White " if self.color is WHITE else "Black ") + self.name

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
        self.price = 5


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
        self.is_unique = True
        self.name = "Queen"
        self.symbol = "Q"
        self.price = 17


class Amazon(Piece):
    def __init__(self, color: Color):
        Piece.__init__(self, color)
        self.step_attacks = [6, -6, 10, -10, 15, -15, 17, -17]
        self.vertical_slide = True
        self.horizontal_slide = True
        self.diagonal_slide = True
        self.is_unique = True
        self.name = "Amazon"
        self.symbol = "Z"
        self.price = 24


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
        self.is_unique = True
        self.name = "Chancellor"
        self.symbol = "C"
        self.price = 16


class Ghost(Piece):
    def __init__(self, color: Color):
        Piece.__init__(self, color)
        self.step_attacks = [8, 16, -8, -16, 1, 2, -1, -2]
        self.name = "Ghost"
        self.symbol = "G"
        self.can_castle = True
        self.price = 7


class Wall(Piece):
    def __init__(self, color: Color):
        Piece.__init__(self, color)
        self.name = "Wall"
        self.symbol = "W"
        self.can_castle = True
        self.price = 0
        self.can_be_promotion = False


class Archer(Piece):
    def __init__(self, color: Color):
        Piece.__init__(self, color)
        self.step_attacks = [7, 9, -7, -9, 14, 18, -14, -18]
        self.name = "Archer"
        self.symbol = "H"
        self.price = 4


class Frog(Piece):
    def __init__(self, color: Color):
        Piece.__init__(self, color)
        self.step_attacks = [6, -6, 10, -10, 15, -15, 17, -17, 16, -16, 2, -2]
        self.name = "Frog"
        self.symbol = "F"
        self.price = 2
        self.is_invincible = True
        self.can_capture = False


ALL_PIECES = [Pawn(WHITE), Knight(WHITE), Bishop(WHITE), Rook(WHITE), Queen(WHITE), King(WHITE),
              Ghost(WHITE), Chancellor(WHITE), Wall(WHITE), Archbishop(WHITE), Archer(WHITE), Frog(WHITE), Amazon(WHITE)]

WHITE_CASTLE_PIECES = [Rook(WHITE), Ghost(WHITE), Wall(WHITE)]
BLACK_CASTLE_PIECES = [Rook(BLACK), Ghost(BLACK), Wall(BLACK)]

WHITE_UNIQUE_PIECES = [Queen(WHITE), Chancellor(WHITE), Amazon(WHITE)]
BLACK_UNIQUE_PIECES = [Queen(BLACK), Chancellor(BLACK), Amazon(BLACK)]

WHITE_COMMON_PIECES = [Knight(WHITE), Bishop(WHITE), Archer(WHITE), Frog(WHITE), Archbishop(WHITE)]
BLACK_COMMON_PIECES = [Knight(BLACK), Bishop(BLACK), Archer(BLACK), Frog(BLACK), Archbishop(BLACK)]
