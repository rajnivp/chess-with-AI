from piece import *


def pawn_promotion(piece, row):
    """
    Check if pawn is eligible for promotion on its next move based on its current position
    """
    if piece.color == "w":
        row_pos = 1
        inc = -1
    elif piece.color == "b":
        row_pos = 6
        inc = 1
    if type(piece) == Pawn and piece.row == row_pos and row == piece.row + inc:
        return True
    else:
        return False


class Board:
    """
    Board is an 8x8 array that stores piece objects.None indicates empty square.
    'b' indicates side with black color pieces.'w' indicates side with white color pieces.
    """

    def __init__(self):
        self.empty = [[None for x in range(8)] for y in range(8)]

        # King and rook objects are stored to make castling easy
        self.black_king = King(0, 4, 'b', b_king)
        self.white_king = King(7, 4, 'w', w_king)
        self.white_rook_left = Rook(7, 0, 'w', w_rook)
        self.white_rook_right = Rook(7, 7, 'w', w_rook)
        self.black_rook_left = Rook(0, 0, 'b', b_rook)
        self.black_rook_right = Rook(0, 7, 'b', b_rook)
        self.array = [
            [self.black_rook_left, Knight(0, 1, 'b', b_knight), Bishop(0, 2, 'b', b_bishop), Queen(0, 3, 'b', b_queen),
             self.black_king, Bishop(0, 5, 'b', b_bishop), Knight(0, 6, 'b', b_knight), self.black_rook_right],
            [Pawn(1, i, 'b', b_pawn) for i in range(8)],
            [None for x in range(8)],
            [None for x in range(8)],
            [None for x in range(8)],
            [None for x in range(8)],
            [Pawn(6, i, 'w', w_pawn) for i in range(8)],
            [self.white_rook_left, Knight(7, 1, 'w', w_knight), Bishop(7, 2, 'w', w_bishop), Queen(7, 3, 'w', w_queen),
             self.white_king, Bishop(7, 5, 'w', w_bishop), Knight(7, 6, 'w', w_knight), self.white_rook_right]]

    def possible_moves(self, color):
        """
        Generates all possible moves by a side of given color.
        returns list of tuples which contains particular piece and list of coordinates where it can move.
        """
        possible_moves = []
        for i in range(8):
            for j in range(8):
                if self.array[i][j] is not None and self.array[i][j].color == color:
                    move_list = self.array[i][j].valid_moves(self)
                    possible_moves.append((self.array[i][j], move_list))

        return possible_moves

    def opponent_moves(self, color):
        """
        Returns list of coordinates of squares where pieces of given color can move
        """
        opponent_moves = []
        for i in range(8):
            for j in range(8):
                if self.array[i][j] is not None and self.array[i][j].color == color:
                    move_list = self.array[i][j].valid_moves(self)
                    for move in move_list:
                        opponent_moves.append(move)

        return opponent_moves

    def is_checked(self, color):
        """
        Check if king piece of given color is in check
        """
        if color == 'w':
            opponent_moves = self.opponent_moves('b')
            if (self.white_king.row, self.white_king.col) in opponent_moves:
                return True

        elif color == 'b':
            opponent_moves = self.opponent_moves('w')
            if (self.black_king.row, self.black_king.col) in opponent_moves:
                return True

        return False

    def move_piece(self, piece, row, col):
        """
        Move piece to new position. if pawn promotion happen then respawn a Queen object.
        if piece captures opponent piece then that square will be occupied by piece and original
        location of piece will become empty square None.
        """

        # Check if move cause pawn promotion
        promotion = pawn_promotion(piece, row)
        old_col = piece.col
        old_row = piece.row
        piece.col = col
        piece.row = row
        self.array[old_row][old_col] = None

        if promotion:
            if piece.color == 'b':
                self.array[row][col] = Queen(row, col, piece.color, b_queen)

            elif piece.color == 'w':
                self.array[row][col] = Queen(row, col, piece.color, w_queen)

            return self.array[row][col], piece

        else:
            self.array[row][col] = piece

    def castling(self, color):
        """
        Check if castling is possible for a side of given color by checking if king and rook object
        has moved and if any squares through which king passes is in check.if castling is possible then
        returns list of tuple containing coordinates for possible castle move location for king.
        """
        left_castle_moves = []
        right_castle_moves = []

        if color == "w":
            king = self.white_king
            left_rook = self.white_rook_left
            right_rook = self.white_rook_right
            opponet_moves = self.opponent_moves('b')
            row = 7

        elif color == "b":
            king = self.black_king
            left_rook = self.black_rook_left
            right_rook = self.black_rook_right
            opponet_moves = self.opponent_moves('w')
            row = 0

        if king.moved is False:
            if self.array[row][0] == left_rook and left_rook.moved is False:
                if not self.array[row][1] and not self.array[row][2] and not self.array[row][3]:
                    steps = {(row, 2), (row, 3), (row, 4)}
                    if not steps.intersection(opponet_moves):
                        left_castle_moves.append((row, 2))

            if self.array[row][7] == right_rook and right_rook.moved is False:
                if not self.array[row][5] and not self.array[row][6]:
                    steps = {(row, 4), (row, 5), (row, 6)}
                    if not steps.intersection(opponet_moves):
                        right_castle_moves.append((row, 6))

        return left_castle_moves, right_castle_moves

    def castling_move(self, piece, row, col, color):
        """
        Returns true if castling move happens otherwise returns false by checking
        castling possibility and available positions for castling i.e left or right castle
        """
        if type(piece) == King:
            if color == 'w':
                left_castle_moves, right_castle_moves = self.castling(color)
                if [(row, col)] == left_castle_moves:
                    self.move_piece(piece, row, col)
                    self.move_piece(self.white_rook_left, row, col + 1)
                    return True

                elif [(row, col)] == right_castle_moves:
                    self.move_piece(piece, row, col)
                    self.move_piece(self.white_rook_right, row, col - 1)
                    return True

            if color == 'b':
                left_castle_moves, right_castle_moves = self.castling(color)
                if [(row, col)] == left_castle_moves:
                    self.move_piece(piece, row, col)
                    self.move_piece(self.black_rook_left, row, col + 1)
                    return True

                elif [(row, col)] == right_castle_moves:
                    self.move_piece(piece, row, col)
                    self.move_piece(self.black_rook_right, row, col - 1)
                    return True

        return False
