import pygame

# Images for each piece
b_bishop = "assets/bbishop.png"
b_king = "assets/bking.png"
b_knight = "assets/bknight.png"
b_pawn = "assets/bpawn.png"
b_queen = "assets/bqueen.png"
b_rook = "assets/brook.png"

w_bishop = "assets/wbishop.png"
w_king = "assets/wking.png"
w_knight = "assets/wknight.png"
w_pawn = "assets/wpawn.png"
w_queen = "assets/wqueen.png"
w_rook = "assets/wrook.png"

# Size of square block
squaresize = 60


class Piece:
    """
    Piece class objects stores color,position and image.
    each piece inherits from this class
    """

    def __init__(self, row, col, color, img):
        # Position on board and piece color
        self.row = row
        self.col = col
        self.color = color

        # Load image of piece
        self.img = pygame.image.load(img)

        # Highlight piece when selected
        self.highlight = False

    def draw(self, screen):
        """
        Draw loaded images of pieces at its (row,col) position on board.
        highlight it with light blue square if piece is selected
        """
        if self.highlight:
            pygame.draw.rect(screen, (0, 0, 200),
                             (self.col * squaresize, self.row * squaresize, squaresize, squaresize), 5)

        screen.blit(self.img, (self.col * squaresize, self.row * squaresize))

    def move_locations(self, row, col, board):
        """
        Check if piece can move to (row,col) position on board if it is empty
        or occupied by opponent piece
        """
        if row < 0 or row > 7 or col < 0 or col > 7:
            return False
        piece = board.array[row][col]
        if piece is None:
            return True
        else:
            if piece.color != self.color:
                return True
            else:
                return False

    def capture_locations(self, row, col, board):
        """
        Check if piece can capture opponent piece at (row,col) position on board
        """
        piece = board.array[row][col]
        if piece is None:
            return False
        else:
            if piece.color != self.color:
                return True
            else:
                return False

    def valid_moves_linear(self, board):
        """
        Get all possible squares where piece can make linear movements and
        return list of tuples containing (row,col) coordinates of board
        where piece can move
        """
        # Horizontal moves
        move_list = []
        new_row = self.row

        for i in (-1, 1):
            new_col = self.col
            while True:
                new_col += i
                if self.move_locations(new_row, new_col, board):
                    move_list.append((new_row, new_col))
                    if self.capture_locations(new_row, new_col, board):
                        break
                else:
                    break

        # Vertical moves
        new_col = self.col

        for i in (-1, 1):
            new_row = self.row
            while True:
                new_row += i
                if self.move_locations(new_row, new_col, board):
                    move_list.append((new_row, new_col))
                    if self.capture_locations(new_row, new_col, board):
                        break
                else:
                    break

        return move_list

    def valid_moves_diagonal(self, board):
        """
        Get all possible squares where piece can make diagonal movements and
        return list of tuples containing (row,col) coordinates of board
        where piece can move
        """
        move_list = []

        # Check for all possible diagonal moves
        increments = [(-1, -1), (1, 1), (1, -1), (-1, 1)]
        for offset in increments:
            new_row = self.row
            new_col = self.col
            while True:
                new_row += offset[1]
                new_col += offset[0]
                if self.move_locations(new_row, new_col, board):
                    move_list.append((new_row, new_col))
                    if self.capture_locations(new_row, new_col, board):
                        break
                else:
                    break

        return move_list


class Pawn(Piece):
    def __init__(self, row, col, color, img):
        super().__init__(row, col, color, img)

    def valid_moves(self, board):
        """
        Generates all possible moves that can be made by piece
        and returns a list of tuples containing all valid
        (row,col) coordinates where it can move
        """
        move_list = []

        increment = {"w": -1, "b": 1}
        offsets = [-1, 1]
        color = self.color

        new_row = self.row + increment[color]
        # Normal move forward
        if 0 <= new_row < 8 and board.array[new_row][self.col] is None:
            move_list.append((new_row, self.col))

            if (self.row == 1 and color == "b") or (self.row == 6 and color == "w"):
                new_row += increment[color]
                if 0 <= new_row < 8 and board.array[new_row][self.col] is None:
                    move_list.append((new_row, self.col))

        # Attack move diagonal
        for change in offsets:
            new_col = self.col + change
            new_row = self.row + increment[color]

            if not self.move_locations(new_row, new_col, board) or not self.capture_locations(new_row, new_col, board):
                continue
            else:
                move_list.append((new_row, new_col))

        return move_list


class Rook(Piece):

    def __init__(self, row, col, color, img):
        super().__init__(row, col, color, img)

        # Check if rook is moved to determine castling possibility
        self.moved = False

    def valid_moves(self, board):
        """
        Return list of  valid linear coordinates where piece can move
        """
        return self.valid_moves_linear(board)


class Bishop(Piece):

    def __init__(self, row, col, color, img):
        super().__init__(row, col, color, img)

    def valid_moves(self, board):
        """
        Return list of  valid diagonal coordinates where piece can move
        """
        return self.valid_moves_diagonal(board)


class Knight(Piece):

    def __init__(self, row, col, color, img):
        super().__init__(row, col, color, img)

    def valid_moves(self, board):
        """
        Generate all possible moves and return list of tuples
        with valid (row,col) coordinates
        """
        move_list = []
        offsets = [(-1, -2), (-1, 2), (-2, -1), (-2, 1),
                   (1, -2), (1, 2), (2, -1), (2, 1)]

        for offset in offsets:
            new_col = self.col + offset[0]
            new_row = self.row + offset[1]

            if self.move_locations(new_row, new_col, board):
                move_list.append((new_row, new_col))

        return move_list


class King(Piece):

    def __init__(self, row, col, color, img):
        super().__init__(row, col, color, img)

        # Check if king is moved to determine castling possibility
        self.moved = False

    def valid_moves(self, board):
        """
        Generate all possible moves and return list of tuples
        with valid (row,col) coordinates
        """
        move_list = []
        offsets = [(1, 1), (-1, -1), (1, -1), (-1, 1),
                   (0, 1), (1, 0), (-1, 0), (0, -1)]

        for offset in offsets:
            new_col = self.col + offset[0]
            new_row = self.row + offset[1]

            if self.move_locations(new_row, new_col, board):
                move_list.append((new_row, new_col))

        return move_list


class Queen(Piece):

    def __init__(self, row, col, color, img):
        super().__init__(row, col, color, img)

    def valid_moves(self, board):
        """
        Return list of all valid linear and diagonal coordinates where
        piece can move
        """
        move_list1 = self.valid_moves_diagonal(board)
        move_list2 = self.valid_moves_linear(board)

        return list(set(move_list1 + move_list2))
