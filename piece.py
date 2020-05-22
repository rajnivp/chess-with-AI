import pygame

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

squaresize = 60


def move_locations(your_color, row, col, board):
    if row < 0 or row > 7 or col < 0 or col > 7:
        return False
    piece = board.array[row][col]
    if piece is None:
        return True
    else:
        if piece.color != your_color:
            return True
        else:
            return False


def capture_locations(your_color, row, col, board):
    piece = board.array[row][col]
    if piece is None:
        return False
    else:
        if piece.color != your_color:
            return True
        else:
            return False


class Piece:
    def __init__(self, row, col, color, img):
        self.row = row
        self.col = col
        self.color = color
        self.img = pygame.image.load(img)
        self.highlight = False

    def draw(self, screen):
        if self.highlight:
            pygame.draw.rect(screen, (0, 0, 200),
                             (self.col * squaresize, self.row * squaresize, squaresize, squaresize), 5)

        screen.blit(self.img, (self.col * squaresize, self.row * squaresize))

    def valid_moves_linear(self, board):
        # Horizontal moves
        move_list = []
        new_row = self.row

        for i in (-1, 1):
            new_col = self.col
            while True:
                new_col += i
                if move_locations(self.color, new_row, new_col, board):
                    move_list.append((new_row, new_col))
                    if capture_locations(self.color, new_row, new_col, board):
                        break
                else:
                    break

        # Vertical moves
        new_col = self.col

        for i in (-1, 1):
            new_row = self.row
            while True:
                new_row += i
                if move_locations(self.color, new_row, new_col, board):
                    move_list.append((new_row, new_col))
                    if capture_locations(self.color, new_row, new_col, board):
                        break
                else:
                    break

        return move_list

    def valid_moves_diagonal(self, board):
        move_list = []

        # Loop through all the possible diagonal directions
        increments = [(-1, -1), (1, 1), (1, -1), (-1, 1)]
        for offset in increments:
            new_row = self.row
            new_col = self.col
            while True:
                new_row += offset[1]
                new_col += offset[0]
                if move_locations(self.color, new_row, new_col, board):
                    move_list.append((new_row, new_col))
                    if capture_locations(self.color, new_row, new_col, board):
                        break
                else:
                    break
        return move_list


class Pawn(Piece):
    def __init__(self, row, col, color, img):
        super().__init__(row, col, color, img)

    def valid_moves(self, board):
        move_list = []

        increment = {"w": -1, "b": 1}
        offsets = [-1, 1]
        color = self.color

        new_row = self.row + increment[color]
        # normal move forward
        if new_row >= 0 and new_row < 8 and board.array[new_row][self.col] == None:
            move_list.append((new_row, self.col))

            if (self.row == 1 and color == "b") or (self.row == 6 and color == "w"):
                new_row += increment[color]
                if new_row >= 0 and new_row < 8 and board.array[new_row][self.col] == None:
                    move_list.append((new_row, self.col))

        # attack move diagonal
        for change in offsets:
            new_col = self.col + change
            new_row = self.row + increment[color]

            if not move_locations(color, new_row, new_col, board) or not capture_locations(color, new_row, new_col,
                                                                                           board):
                continue

            else:
                move_list.append((new_row, new_col))

        return move_list


class Rook(Piece):

    def __init__(self, row, col, color, img):
        super().__init__(row, col, color, img)
        self.moved = False

    def valid_moves(self, board):
        return self.valid_moves_linear(board)


class Bishop(Piece):

    def __init__(self, row, col, color, img):
        super().__init__(row, col, color, img)

    def valid_moves(self, board):
        return self.valid_moves_diagonal(board)


class Knight(Piece):

    def __init__(self, row, col, color, img):
        super().__init__(row, col, color, img)

    def valid_moves(self, board):
        move_list = []
        offsets = [(-1, -2), (-1, 2), (-2, -1), (-2, 1),
                   (1, -2), (1, 2), (2, -1), (2, 1)]

        for offset in offsets:
            new_col = self.col + offset[0]
            new_row = self.row + offset[1]

            if move_locations(self.color, new_row, new_col, board):
                move_list.append((new_row, new_col))

        return move_list


class King(Piece):

    def __init__(self, row, col, color, img):
        super().__init__(row, col, color, img)
        self.moved = False

    def valid_moves(self, board):
        move_list = []
        offsets = [(1, 1), (-1, -1), (1, -1), (-1, 1),
                   (0, 1), (1, 0), (-1, 0), (0, -1)]

        for offset in offsets:
            new_col = self.col + offset[0]
            new_row = self.row + offset[1]

            if move_locations(self.color, new_row, new_col, board):
                move_list.append((new_row, new_col))

        return move_list


class Queen(Piece):

    def __init__(self, row, col, color, img):
        super().__init__(row, col, color, img)

    def valid_moves(self, board):
        move_list1 = self.valid_moves_diagonal(board)
        move_list2 = self.valid_moves_linear(board)

        return list(set(move_list1 + move_list2))
