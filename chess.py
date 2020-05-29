import sys
from AI import *

# Initialize pygame first
pygame.init()

# Draw screen
screen = pygame.display.set_mode((8 * squaresize, 8 * squaresize))

# Set caption
pygame.display.set_caption("Chess with AI")

# Load fonts
gameover_font = pygame.font.Font("assets/FreeSansBold.ttf", 32)

# Load and draw chessboard
bg = pygame.image.load("assets/chessboard.png").convert()
bg = pygame.transform.scale(bg, (8 * squaresize, 8 * squaresize))

# Create Board object
board = Board()

# Store pieces for drawing them on board
pieces = [piece for row in board.array for piece in row if piece]

# To maintain frame per second
clock = pygame.time.Clock()

# 1 indicates player turn 0 indicates ai turn
player = 1
AI = 0

# Give turn randomly
turn = random.randint(0, 1)

# This will use to highlight piece when selected
selected = False


def get_inputs():
    """
    Get inputs from user to make moves.function returns coordinates of mouse click position
    """
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos_col, pos_row = pygame.mouse.get_pos()
                pos_col, pos_row = math.floor(pos_col / squaresize), math.floor(pos_row / squaresize)
                return pos_col, pos_row


def select_piece(row, col, color):
    """
    Return piece if selected piece belongs to player
    """
    for piece in pieces:
        if piece == board.array[row][col] and piece.color == color:
            return piece


def game_over(winner):
    """
    Print name of winner on screen at checkmate
    """
    gameover_text = gameover_font.render("{} wins".format(winner), True, (255, 255, 255))
    screen.blit(gameover_text, (0, 0))


# Will become true if either of them put other in checkmate
ai_win = False
player_win = False

# Run the game
run = True

while run:
    # Draw screen
    screen.blit(bg, (0, 0))

    # Draw all pieces by using draw method of Piece class
    for piece in pieces:
        piece.draw(screen)

    # This will update display
    pygame.display.update()

    # Check turn
    if turn == player:
        pos = get_inputs()
        if not pos:
            sys.exit()
            
        elif not selected:
            col, row = pos
            selected_piece = select_piece(row, col, 'w')
            if selected_piece is not None:
                player_moves = selected_piece.valid_moves(board)
                castle_moves = []

                # Highlight piece when selected
                selected = True
                selected_piece.highlight = True

                # Check for castling possibility
                left_castle, right_castle = board.castling('w')
                if type(selected_piece) == King:
                    if left_castle:
                        for move in left_castle:
                            castle_moves.append(move)
                    if right_castle:
                        for move in right_castle:
                            castle_moves.append(move)

                # add player moves and castle moves
                moves = player_moves + castle_moves

        elif selected:
            col, row = pos
            selected_piece.highlight = False
            if (row, col) in moves:
                # Make castle move if valid
                if (row, col) in castle_moves:
                    castle = board.castling_move(selected_piece, row, col, 'w')
                    if castle:
                        # Change turn after move and unhighlight piece
                        turn = AI
                        selected = False

                else:  # Make normal move
                    # Store initial position in case if we have to reverse move
                    old_row = selected_piece.row
                    old_col = selected_piece.col
                    dest = board.array[row][col]
                    promotion = board.move_piece(selected_piece, row, col)
                    if type(selected_piece) == King or type(selected_piece) == Rook:
                        selected_piece.moved = True
                    if dest:
                        # Remove opponent piece if captured
                        pieces.remove(dest)
                    if promotion:
                        # Respawn Queen object in case of pawn promotion
                        pieces.append(promotion[0])
                        pieces.remove(promotion[1])

                    # Check if move puts player in check
                    check = board.is_checked('w')
                    if check:
                        # Reverse move if it puts player i check
                        selected = False
                        board.move_piece(selected_piece, old_row, old_col)
                        board.array[row][col] = dest
                        if type(selected_piece) == King or type(selected_piece) == Rook:
                            selected_piece.moved = False
                        if dest:
                            pieces.append(dest)
                        if promotion:
                            pieces.append(promotion[1])
                            pieces.remove(promotion[0])

                    else:
                        # Change turn and unhighlight selected piece after making move
                        selected = False
                        turn = AI

            else:
                # Keep player in turn until move complete
                # and unhighlight piece if no valid move is selected by player
                selected = False

    elif turn == AI:
        # Get coordinates to move piece based on minimax score
        score, ai_piece, (row, col) = minimax(board, 2, -math.inf, math.inf, True)

        # Ai in checkmate and player wins
        if score == -math.inf:
            player_win = True
            run = False
        else:
            dest = board.array[row][col]
            promotion = board.move_piece(ai_piece, row, col)
            if type(ai_piece) == King or type(ai_piece) == Rook:
                ai_piece.moved = True
            if dest:
                # Remove opponent piece if captured
                pieces.remove(dest)
            if promotion:
                # Respawn Queen object in case of pawn promotion
                pieces.append(promotion[0])
                pieces.remove(promotion[1])

        # Change turn after move completion
        turn = player

        # Player in checkmate Ai wins
        if score == math.inf:
            ai_win = True
            run = False

    # Draw pieces on board
    for piece in pieces:
        piece.draw(screen)
    if player_win:
        game_over('player')
    elif ai_win:
        game_over('AI')
    pygame.display.update()

pygame.time.wait(5000)
pygame.quit()
