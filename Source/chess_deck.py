from typing import Optional, List, Iterator, Set
from fen_loader import FenLoader
from bitboards import BitboardManager
from computer import SQUARES, BB_EMPTY, BB_SQUARES, BB_RANK_1, BB_RANK_2, BB_RANK_7, BB_RANK_8, BB_CORNERS, BB_FILES, \
    BB_DIAG_MASK, BB_DIAG_ATTACK, BB_RANK_MASK, BB_RANK_ATTACK, BB_FILE_MASK, BB_FILE_ATTACK, BB_FILE_H, BB_FILE_A, \
    BB_ALL
from computer import ComputerManager
from decks import Deck
from move import Move
from pieces import King, Piece
from enum import Enum

Square = int
Bitboard = int
Color = bool

COLORS = [WHITE, BLACK] = [True, False]
COLOR_NAMES = ["black", "white"]


class GameResolution(Enum):
    WHITE_WINS = 1,
    BLACK_WINS = 2,
    DRAW_BY_STALEMATE = 3,
    DRAW_BY_REPETITION = 4,
    ONGOING = 5


class ChessDeck:
    def __init__(self, white_pieces_deck: Deck, black_pieces_deck: Deck, fen: Optional[str] = None):
        self.game = None
        self.attacks = None
        self.bbm = BitboardManager()
        self.cpm = ComputerManager()
        self.white_deck = white_pieces_deck.white_pieces
        self.black_deck = black_pieces_deck.black_pieces

        self.white_set = white_pieces_deck.get_set_pieces(WHITE)
        self.black_set = black_pieces_deck.get_set_pieces(BLACK)

        self.white_prom = white_pieces_deck.get_prom_pieces(WHITE)
        self.black_prom = black_pieces_deck.get_prom_pieces(BLACK)

        self.piece_set = self.white_set.union(self.black_set)
        self.create_dict_attacks()

        if fen is None:
            self.reset_game()
            self.turn = WHITE
            self.halfmove_clock = 0
            self.fullmove_number = 1
        else:
            fnl = FenLoader(fen, self.piece_set)
            self.game = fnl.load_board()
            self.turn = fnl.load_turn()
            self.halfmove_clock = fnl.load_halfmove_clock()
            self.fullmove_number = fnl.load_fullmove_number()




    def reset_game(self):
        """Resets the game and loads both decks"""
        self.game = {
            "Pawn": BB_RANK_2 | BB_RANK_7,
            "White": BB_RANK_2,
            "Black": BB_RANK_7,
            "All": BB_RANK_2 | BB_RANK_7,
            "Castling": BB_CORNERS,
            "En passant": BB_EMPTY
        }
        self.load_deck(self.white_deck, WHITE)
        self.load_deck(self.black_deck, BLACK)

    def load_deck(self, deck: List[Piece], color: Color) -> None:
        """Load a deck in their corresponding side of the board"""
        for position, piece in enumerate(deck):
            if piece is None:
                continue

            bb_piece = (BB_RANK_1 if color else BB_RANK_8) & BB_FILES[position]
            if piece.name not in self.game:
                self.game[piece.name] = bb_piece
            else:
                self.game[piece.name] |= bb_piece

            self.game["White" if color else "Black"] |= bb_piece
            self.game["All"] |= bb_piece

    def clear_game(self):
        """Clears the game"""
        for key in self.game:
            self.game[key] = BB_EMPTY

    def get_pieces_of_color(self, color: Color) -> Bitboard:
        return self.game["White"] if color else self.game["Black"]

    def get_set_of_color(self, color: Color) -> Set:
        return self.white_set if color else self.black_set

    def get_board_as_str(self) -> str:
        """Get the board as a string."""
        white_pieces = self.game["White"]
        black_pieces = self.game["Black"]
        board = [
            "· ", "· ", "· ", "· ", "· ", "· ", "· ", "· \n",
            "· ", "· ", "· ", "· ", "· ", "· ", "· ", "· \n",
            "· ", "· ", "· ", "· ", "· ", "· ", "· ", "· \n",
            "· ", "· ", "· ", "· ", "· ", "· ", "· ", "· \n",
            "· ", "· ", "· ", "· ", "· ", "· ", "· ", "· \n",
            "· ", "· ", "· ", "· ", "· ", "· ", "· ", "· \n",
            "· ", "· ", "· ", "· ", "· ", "· ", "· ", "· \n",
            "· ", "· ", "· ", "· ", "· ", "· ", "· ", "· \n"
        ]
        for piece in self.piece_set:
            piece_bb = self.game[piece.name] & (white_pieces if piece.color else black_pieces)
            piece_bb = self.bbm.flip_vertical(piece_bb)
            for pos in self.bbm.scan_reversed(piece_bb):
                board[pos] = f"{piece.get_symbol()}{board[pos][1:]}"

        return "".join(board)

    def create_dict_attacks(self) -> None:
        """
        The create_dict_attacks function creates a dictionary of attacks for each piece.
        The keys are the names of the pieces, and the values are dictionaries containing
        the attack vectors for that piece. The keys in these sub-dictionaries are strings
        describing how to compute those attacks.
        """
        self.attacks = {
            "King": {"Step": [self.cpm.compute_step_attacks(sq, King(WHITE).step_attacks) for sq in SQUARES]},
        }

        for piece in self.piece_set:
            if piece in self.attacks:
                continue

            attacks = {}
            if piece.step_attacks:
                if piece.symmetry:
                    attacks['Step'] = [self.cpm.compute_step_attacks(sq, piece.step_attacks) for sq in SQUARES]
                else:
                    attacks['Steps'] = [[self.cpm.compute_step_attacks(sq, direction) for sq in SQUARES] for direction
                                        in piece.step_attacks]
            if piece.horizontal_slide:
                attacks['Horizontal slide'] = [BB_RANK_MASK, BB_RANK_ATTACK]
            if piece.vertical_slide:
                attacks['Vertical slide'] = [BB_FILE_MASK, BB_FILE_ATTACK]
            if piece.diagonal_slide:
                attacks['Diagonal slide'] = [BB_DIAG_MASK, BB_DIAG_ATTACK]

            self.attacks[piece.name] = attacks

    def gen_legal_moves(self) -> Iterator[Move]:
        """First it computes if the king is in check or not by looking up the attackers of the square where the king is.
        If it has attackers then it calls the function gen_scape_moves to generate the moves that can escape the check."""
        king_bb = self.game["King"] & (self.game["White"] if self.turn else self.game["Black"])
        king_sq = self.bbm.msb(king_bb)
        attackers = self.get_attackers_of_square(king_sq, not self.turn)
        blockers = self.get_blockers(king_sq, self.turn)
        if attackers:
            for move in self.gen_scape_moves(attackers):
                if self.is_safe(king_sq, move, blockers):
                    yield move
        else:
            for move in self.gen_pseudo_moves():
                if self.is_safe(king_sq, move, blockers):
                    yield move

    def is_safe(self, king_sq: Square, move: Move, blockers: Bitboard) -> bool:

        if move.from_sq == king_sq:
            if self.is_move_castling(move):
                return True
            else:
                return not self.is_square_attacked(move.to_sq, not self.turn)
        elif self.is_the_move_a_en_passant(move):
            return bool(not blockers & BB_SQUARES[move.from_sq]) and not self.is_ep_skewered(king_sq, move.from_sq)
        else:
            return bool(not blockers & BB_SQUARES[move.from_sq] or (self.cpm.compute_ray(move.from_sq, move.to_sq) & BB_SQUARES[king_sq]))

    def is_ep_skewered(self, king_sq: Square, capturer: Square) -> bool:
        last_move_sq = self.bbm.msb(self.game['En passant']) + (-8 if self.turn else 8)
        occupancy = self.game['All'] & ~BB_SQUARES[last_move_sq] & ~BB_SQUARES[capturer]
        horizontal_attackers = BB_EMPTY
        for piece in self.piece_set:
            if not piece.horizontal_slide:
                continue
            horizontal_attackers |= self.game[piece.name] & self.get_pieces_of_color(not self.turn)

        if BB_RANK_ATTACK[king_sq][BB_RANK_MASK[king_sq] & occupancy] & horizontal_attackers:
            return True
        return False

    def get_blockers(self, sq: Square, color: Color) -> Bitboard:
        """Get the blockers of a square, by seeing if the """

        blockers = BB_EMPTY
        snipers = BB_EMPTY

        for piece in self.get_set_of_color(not color):
            if piece.horizontal_slide:
                snipers |= self.attacks[piece.name]['Horizontal slide'][1][sq][0] & self.game[piece.name]
            if piece.vertical_slide:
                snipers |= self.attacks[piece.name]['Vertical slide'][1][sq][0] & self.game[piece.name]
            if piece.diagonal_slide:
                snipers |= self.attacks[piece.name]['Diagonal slide'][1][sq][0] & self.game[piece.name]
        snipers = snipers & self.get_pieces_of_color(not color)

        for sniper in self.bbm.scan_reversed(snipers):
            between = self.cpm.compute_between(sniper, sq) & self.game['All']
            if self.bbm.is_one_bit_on(between):
                blockers |= between
        return blockers & self.get_pieces_of_color(color)

    def gen_scape_moves(self, attackers: Bitboard) -> Iterator[Move]:
        """Generates the scape moves of the king. It moves if there is any available square to scape that has no attackers,
        if it has only one attacker then see if it can be captured or a piece can be put in the middle if it has a slide attack."""
        king_bb = self.game["King"] & self.get_pieces_of_color(self.turn)
        king_sq = self.get_king_square(self.turn)
        king_attacks = self.get_mask_attack(king_sq)
        attacked_squares = self.get_attacked_squares_by_sliders(king_sq, attackers)

        for square in self.bbm.scan_reversed(king_attacks & ~self.get_pieces_of_color(self.turn) & ~attacked_squares):
            yield Move(king_sq, square)

        if self.bbm.is_one_bit_on(attackers):
            attacker_sq = self.bbm.msb(attackers)
            attacker_name = self.get_type_at(attacker_sq)
            target_squares = BB_EMPTY
            if "Diagonal slide" in self.attacks[attacker_name] or "Horizontal slide" in self.attacks[attacker_name] or "Vertical slide" in self.attacks[attacker_name]:
                target_squares = self.cpm.compute_between(attacker_sq, king_sq) | attackers
            elif "Step" in self.attacks[attacker_name] or "Steps" in self.attacks[attacker_name]:
                target_squares |= attackers

            if target_squares:
                yield from self.gen_pseudo_moves(~king_bb, target_squares)

    def get_attacked_squares_by_sliders(self, king_sq: Square, attackers: Bitboard) -> Bitboard:
        sliders = BB_EMPTY
        for piece in self.get_set_of_color(not self.turn):
            if piece.horizontal_slide or piece.vertical_slide or piece.diagonal_slide:
                sliders |= self.game[piece.name]
        attackers &= sliders
        attacked = BB_EMPTY
        for attacker in self.bbm.scan_reversed(attackers):
            attacked |= self.cpm.compute_ray(attacker, king_sq) & ~self.game['All']
        return attacked

    def gen_pseudo_moves(self, start_mask: Bitboard = BB_ALL, end_mask: Bitboard = BB_ALL) -> Iterator[Move]:
        """
        The gen_pseudo_moves function generates all possible pseudo-legal moves for the current player.
        It does this by first generating all possible attack moves and then adding in the remaining legal moves.
        The gen_attack_moves function is used to generate these attack moves, while the gen_push_pawns and
        gen_castling functions are used to add in other legal move types.
        """
        my_pieces = self.game["White"] if self.turn is WHITE else self.game["Black"]
        their_pieces = self.game["Black"] if self.turn is WHITE else self.game["White"]
        my_pawns = self.game["Pawn"] & my_pieces
        my_pieces_wo_pawns = my_pieces & ~self.game["Pawn"]

        for attack_move in self.gen_attack_moves(my_pieces_wo_pawns, ~my_pieces, start_mask, end_mask):
            yield attack_move

        for must_capture_move in self.gen_attack_moves(my_pawns, their_pieces | self.game['En passant'], start_mask,
                                                       end_mask):
            yield must_capture_move

        double_move = self.game['Pawn'] & self.game['White'] & BB_RANK_2 if self.turn is WHITE else self.game['Pawn'] & \
                                                                                                    self.game[
                                                                                                        'Black'] & BB_RANK_7
        one_move = self.game['Pawn'] & self.game['White'] if self.turn is WHITE else self.game['Pawn'] & self.game[
            'Black']

        for push_move in self.gen_push_pawns(one_move, 8, start_mask, end_mask):
            yield push_move

        for push_move in self.gen_push_pawns(double_move, 16, start_mask, end_mask):
            yield push_move

        for castling_move in self.gen_castling_moves(start_mask, end_mask):
            yield castling_move

    def gen_attack_moves(self, pieces: Bitboard, condition: Bitboard, start_mask: Bitboard = BB_ALL,
                         end_mask: Bitboard = BB_ALL) -> Iterator[Move]:
        """ The gen_attack_moves function generates all possible pseudo moves that can be made by a player given the current board state"""
        for from_sq in self.bbm.scan_reversed(pieces & start_mask):
            bb_moves = self.get_mask_attack(from_sq) & condition & end_mask
            for to_sq in self.bbm.scan_reversed(bb_moves):
                if self.cpm.compute_rank(to_sq) in [0, 7] and self.get_type_at(from_sq) == "Pawn":
                    promotion_pieces = self.white_prom if self.turn is WHITE else self.black_prom
                    for promotion_piece in promotion_pieces:
                        yield Move(from_sq, to_sq, promotion_piece)
                else:
                    yield Move(from_sq, to_sq)

    def gen_push_pawns(self, bb_pawns: Bitboard, distance: int, start_mask: Bitboard = BB_ALL,
                       end_mask: Bitboard = BB_ALL) -> Iterator[Move]:
        """ The gen_push_pawns function generates all possible moves for a pawn to move forward one or two squares. """
        for from_sq in self.bbm.scan_reversed(bb_pawns & start_mask):
            to_sq = from_sq + (distance if self.turn is WHITE else -distance)
            if self.is_square_empty(to_sq) and (BB_SQUARES[to_sq] & end_mask) != BB_EMPTY:
                if self.cpm.compute_rank(to_sq) in [0, 7]:
                    promotion_pieces = self.white_prom if self.turn is WHITE else self.black_prom
                    for promotion in promotion_pieces:
                        yield Move(from_sq, to_sq, promotion)
                else:
                    yield Move(from_sq, to_sq)

    def gen_castling_moves(self, start_mask: Bitboard = BB_ALL, end_mask: Bitboard = BB_ALL) -> Iterator[Move]:
        """
        The gen_castling_moves function generates all possible castling moves for the current player.
        It does this by iterating through each of the squares on the castling bitboard, and checking
        if there is a piece between those two squares. If there isn't, then it checks to see if
        the king would be attacked by an enemy piece.
        If they aren't, then it creates a Move object with that move and yields it.
        """
        backrank = BB_RANK_1 if self.turn == WHITE else BB_RANK_8
        king = self.game['King'] & self.game['White' if self.turn else 'Black']
        if (king & start_mask) == BB_EMPTY:
            return
        king_sq = self.bbm.msb(king)

        for candidate in self.bbm.scan_reversed(self.game["Castling"] & backrank):
            castling_space = self.cpm.compute_between(candidate, king_sq)
            if castling_space & self.game['All']:
                continue

            king_movement = self.cpm.compute_between(king_sq,
                                                     candidate if abs(candidate - king_sq) < 4 else candidate + 1)
            if self.is_bitboard_attacked(king_movement, not self.turn):
                continue

            if self.cpm.compute_file(king_sq) < self.cpm.compute_file(candidate):
                to_square = self.bbm.msb(self.bbm.shift_2_right(king))
            else:
                to_square = self.bbm.msb(self.bbm.shift_2_left(king))

            if (BB_SQUARES[to_square] & end_mask) == BB_EMPTY:
                return
            yield Move(king_sq, to_square)

    def get_mask_attack(self, sq: Square) -> Bitboard:
        """
        The get_mask_attack function returns a bitboard of all the squares that are attacked by the piece on sq.
        The get_mask_attack function is called from within the gen_pseudo_move function, and it uses information about which pieces
        are in play for each player.
        """
        piece_set = self.white_set if self.turn is WHITE else self.black_set
        bb_moves = BB_EMPTY

        for piece in piece_set:
            bb_sq = BB_SQUARES[sq]
            if not (bb_sq & self.game[piece.name]):
                continue

            if 'Step' in self.attacks[piece.name]:
                bb_moves |= self.attacks[piece.name]['Step'][sq]
            elif 'Steps' in self.attacks[piece.name]:
                bb_moves |= self.attacks[piece.name]['Steps'][0][sq] if self.turn is WHITE else \
                self.attacks[piece.name]['Steps'][1][sq]

            for slide_type in ('Diagonal slide', 'Vertical slide', 'Horizontal slide'):
                if slide_type in self.attacks[piece.name]:
                    mask = self.attacks[piece.name][slide_type][0]
                    attack = self.attacks[piece.name][slide_type][1]
                    bb_moves |= attack[sq][mask[sq] & self.game['All']]

        return bb_moves

    def set_piece_at(self, sq: Square, piece_name: str, color: Color):
        """Set the piece at a square to a specific piece and color"""
        mask = BB_SQUARES[sq]
        self.remove_piece_at(sq)
        self.game[piece_name] |= mask
        self.game['All'] |= mask
        self.game['White' if color else 'Black'] |= mask

    def get_type_at(self, sq: Square) -> Optional[str]:
        """
        The get_type_at function returns the type of piece at a given square.
        """
        mask = BB_SQUARES[sq]
        for key, bitboard in self.game.items():
            if key in ['All', 'White', 'Black', 'Castling']:
                continue
            if mask & bitboard:
                return key
        return None

    def get_color_at(self, sq: Square) -> Optional[Color]:
        """Get the color of the given square"""
        mask = BB_SQUARES[sq]
        if mask & self.game['White']:
            return WHITE
        elif mask & self.game['Black']:
            return BLACK
        return None

    def remove_piece_at(self, sq: Square) -> str:
        """
        The remove_piece_at function removes a piece from the board.
        It takes in a square as an argument and returns the dictionary key of piece that was removed.
        """
        mask = BB_SQUARES[sq]
        bb_key = self.get_type_at(sq)
        if bb_key is None:
            return ""

        self.game[bb_key] ^= mask
        self.game['All'] ^= mask
        self.game['White' if self.get_color_at(sq) else 'Black'] ^= mask
        return bb_key

    def is_square_attacked(self, sq: Square, color: Color) -> bool:
        """
        The is_square_attacked function returns a boolean value of whether a square is attacked by a given color.
        """
        return bool(self.get_attackers_of_square(sq, color))

    def get_attackers_of_square(self, sq: Square, color: Color) -> Bitboard:
        attackers = BB_EMPTY
        for attacking_piece in self.bbm.scan_reversed(self.get_pieces_of_color(color)):
            if self.get_mask_attack(attacking_piece) & BB_SQUARES[sq]:
                attackers |= BB_SQUARES[attacking_piece]
        return attackers

    def is_square_empty(self, sq: Square) -> bool:
        return self.get_type_at(sq) is None

    def is_the_move_a_en_passant(self, move: Move) -> bool:
        """
        The is_the_move_a_en_passant function returns a boolean value of whether the next move would be an en passant move.
        """
        return bool(self.game['En passant'] & BB_SQUARES[move.to_sq]) & bool(BB_SQUARES[move.from_sq] & self.game['Pawn'])

    def is_bitboard_attacked(self, bb: Bitboard, color: Color) -> bool:
        """
        The is_bitboard_attacked function takes a bitboard and a color as arguments.
        It returns True if any of the selected squares is attacked.
        """
        for sq in self.bbm.scan_reversed(bb):
            if self.is_square_attacked(sq, color):
                return True
        return False

    def push(self, move: Move):
        """
        The push function takes a move as input and updates the board accordingly.
        It also handles castling, en passant.
        """
        self.clear_en_passant()
        self.apply_move(move)
        if self.is_move_castling(move):
            additional_move = self.get_additional_castling_move(move)
            self.apply_move(additional_move)

        if self.can_be_en_passanted(move):
            self.set_en_passant(move)

        if self.has_been_an_en_passant_capture(move):
            self.remove_piece_at(move.to_sq - 8 if self.turn is WHITE else move.to_sq + 8)

        if move.is_promotion():
            self.set_piece_at(move.to_sq, move.promotion.name, self.turn)

        self.update_castling_rights(move)
        self.turn = not self.turn

    def is_move_castling(self, move: Move) -> bool:
        """Checks if a move is a castling move"""
        return (self.get_type_at(move.to_sq) == 'King') & (self.cpm.compute_distance(move.from_sq, move.to_sq) == 2)

    def can_be_en_passanted(self, move: Move) -> bool:
        """Checks if a move generates an en passant opportunity"""
        return (self.get_type_at(move.to_sq) == 'Pawn') & (self.cpm.compute_distance(move.from_sq, move.to_sq) == 2)

    def has_been_an_en_passant_capture(self, move: Move) -> bool:
        """Checks if a move is an en passant take"""
        is_pawn_capture = (self.get_type_at(move.to_sq) == 'Pawn') & (not move.is_going_straight())
        return is_pawn_capture

    def set_en_passant(self, move: Move):
        """Sets the en passant square"""
        self.game['En passant'] |= BB_SQUARES[move.to_sq - 8] if self.turn is WHITE else BB_SQUARES[move.to_sq + 8]

    def clear_en_passant(self):
        """Clears the en passant square"""
        self.game['En passant'] = BB_EMPTY

    def apply_move(self, move: Move):
        """Apply a move to the board"""
        bb_key = self.remove_piece_at(move.from_sq)
        self.set_piece_at(move.to_sq, bb_key, self.turn)

    def update_castling_rights(self, move: Move) -> None:
        """ The update_castling_rights function updates the castling rights for both players after each move"""
        backrank = BB_RANK_1 if self.turn is WHITE else BB_RANK_8
        if self.get_type_at(move.to_sq) == 'King':
            self.game['Castling'] &= ~backrank
        elif BB_SQUARES[move.from_sq] & self.game['Castling']:
            self.game['Castling'] ^= BB_SQUARES[move.from_sq]

    def get_additional_castling_move(self, move: Move) -> Move:
        """Given a two square distance king move, return the corresponding castling move"""
        backrank = BB_RANK_1 if self.turn == WHITE else BB_RANK_8
        if move.is_going_right():
            castling_piece_sq = self.bbm.msb(backrank & BB_FILE_H)
            return Move(castling_piece_sq, move.to_sq - 1)
        else:
            castling_piece_sq = self.bbm.msb(backrank & BB_FILE_A)
            return Move(castling_piece_sq, move.to_sq + 1)

    def get_status_game(self) -> GameResolution:
        """It returns the status of the game"""
        if not any(self.gen_legal_moves()):
            if self.is_square_attacked(self.get_king_square(self.turn), not self.turn):
                return GameResolution.WHITE_WINS if self.turn is BLACK else GameResolution.BLACK_WINS
            else:
                return GameResolution.DRAW_BY_STALEMATE
        return GameResolution.ONGOING

    def get_king_square(self, color: Color) -> Square:
        """Returns the square of the king of a given color"""
        return self.bbm.msb(self.game['King'] & self.get_pieces_of_color(color))

    def start_game(self):
        """just for testing"""
        done = False
        while not done:
            print(self.get_board_as_str())
            match self.get_status_game():
                case GameResolution.WHITE_WINS:
                    print('White wins')
                    done = True
                    continue
                case GameResolution.BLACK_WINS:
                    print('Black wins')
                    done = True
                    continue
                case GameResolution.DRAW_BY_STALEMATE:
                    print('Draw by stalemate')
                    done = True
                    continue

            for move in self.gen_legal_moves():
                print(f"{move} ", end="")
            print("")

            command = input("Insert a move: ")
            filtered_command = command.replace(" ", "").lower()
            if filtered_command == "exit":
                done = True
                continue
            for move in self.gen_legal_moves():
                if str(move) == filtered_command:
                    self.push(move)
                    break
            else:
                print("Invalid move")
