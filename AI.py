from board import *
import math
import random


def score_value(board, color):
    """
    Give score to each piece positive to own piece and negative to opponent piece.
    some important moves affect score based board condition.
    return score after correcting it for all pieces and piece moves.
    """
    score = 0
    ai_moves = board.opponent_moves(color)
    player_moves = board.opponent_moves('w')

    for i in range(8):
        for j in range(8):
            piece = board.array[i][j]
            if piece is not None and piece.color == color:
                left_castle, right_castle = board.castling('b')
                if right_castle:
                    score += 50
                if type(piece) == King:
                    score += 1000
                    if (piece.row, piece.col) in player_moves:
                        score -= 200
                elif type(piece) == Queen:
                    score += 1100
                    if piece.row == 0 or piece.row == 1:
                        score -= 100
                elif type(piece) == Rook:
                    score += 500
                    if board.black_rook_left.row == 0 and board.black_rook_left.col == 0:
                        score += 40
                elif type(piece) == Bishop:
                    score += 300
                    if piece.row == 0 or piece.row == 1:
                        score -= 40
                elif type(piece) == Knight:
                    score += 350
                    if (piece.row, piece.col) in [(0, 1), (0, 6)]:
                        score -= 50
                elif type(piece) == Pawn:
                    score += 70
                    if (piece.row, piece.col) in [(0, 2), (0, 3), (0, 4)]:
                        score -= 20

            if piece is not None and piece.color != color:
                if type(piece) == King:
                    score -= 1000
                    if (piece.row, piece.col) in ai_moves:
                        score += 200
                elif type(piece) == Queen:
                    score -= 1000
                elif type(piece) == Rook:
                    score -= 500
                elif type(piece) == Bishop:
                    score -= 300
                elif type(piece) == Knight:
                    score -= 300
                elif type(piece) == Pawn:
                    score -= 50

    return score


def minimax(board, depth, alpha, beta, maximizingPlayer):
    """
    Minimax function will recursively look through all possible board state
    and pick one where maximizing player get highest score
    depth indicates number of recursions
    alpha,beta value used to break loop which iterates over all possible moves by each piece of each side
    """
    if depth == 0:
        score = score_value(board, 'b')
        return score, None, None

    if maximizingPlayer:  # Ai side with black piece color is maximizing player

        # Set initial score value
        value = -math.inf

        # Get all valid moves available to ai
        valid_moves = board.opponent_moves('b')

        # Pick move randomly, this move will get changed based on minimax score
        best_row, best_col = random.choice(valid_moves)

        # Get moves by pieces
        ai_moves = board.possible_moves('b')

        # Initialize piece with None,it will changed based on minimax score
        best_piece = None

        # Iterate over all possible moves by each piece
        for piece, move_list in ai_moves:

            # Check for castling possibility
            castle_moves = []
            left_castle, right_castle = board.castling('b')
            if type(piece) == King:
                if left_castle:
                    for move in left_castle:
                        castle_moves.append(move)
                if right_castle:
                    for move in right_castle:
                        castle_moves.append(move)

            # Add castling moves to piece move_list
            moves = move_list + castle_moves

            # Castling implementation is complex, we have to look if castling is allowed at given position
            for r, c in moves:
                # preserve initial piece and coordinates
                old_row = piece.row
                old_col = piece.col
                dest = board.array[r][c]

                # Make castling move if possible at given coordinates
                if (r, c) in castle_moves:
                    castle = board.castling_move(piece, r, c, 'b')
                    if castle:
                        score, Piece, move = minimax(board, depth - 1, alpha, beta, False)

                        # Reverse the move to get back to initial board state
                        if [(r, c)] == left_castle:
                            board.move_piece(piece, old_row, old_col)
                            board.move_piece(board.black_rook_left, r, c - 2)
                            board.black_king.moved = False
                            board.black_rook_left.moved = False
                        if [(r, c)] == right_castle:
                            board.move_piece(piece, old_row, old_col)
                            board.move_piece(board.black_rook_right, r, c + 1)
                            board.black_king.moved = False
                            board.black_rook_right.moved = False

                        # Update the score
                        if score > value:
                            value = score
                            best_row = r
                            best_col = c
                            best_move = (best_row, best_col)
                            best_piece = piece
                        alpha = max(alpha, value)
                        if alpha >= beta:
                            return value, piece, best_move

                else:
                    # Check for pawn promotion
                    promotion = board.move_piece(piece, r, c)
                    if type(piece) == King or type(piece) == Rook:
                        check_castle = piece.moved
                        piece.moved = True

                    # Check if move put ai in check
                    check = board.is_checked('b')
                    if check:
                        # Reverse the move if move put piece in check
                        board.move_piece(piece, old_row, old_col)
                        board.array[r][c] = dest
                        if type(piece) == King or type(piece) == Rook:
                            piece.moved = False
                        continue  # move is not allowed stop further execution

                    score, Piece, move = minimax(board, depth - 1, alpha, beta, False)

                    # Revert the move after getting score to get back to initial board state
                    board.move_piece(piece, old_row, old_col)
                    board.array[r][c] = dest

                    # Check king or rook piece's moved state
                    if type(piece) == King or type(piece) == Rook:
                        if check_castle is False:
                            piece.moved = False

                    # Change value to score if score is bigger,change initial piece and move to new piece and move
                    # returned by minimax function
                    if score > value:
                        value = score
                        best_row = r
                        best_col = c
                        best_move = (best_row, best_col)
                        best_piece = piece
                    alpha = max(alpha, value)

                    # break loop if alpha is bigger than beta
                    if alpha >= beta:
                        if type(piece) == King or type(piece) == Rook:
                            piece.moved = True
                        return value, piece, best_move

        # Return initial value if no move found which means ai in checkmate
        if type(best_piece) == King or type(best_piece) == Rook:
            best_piece.moved = True
        return value, best_piece, (best_row, best_col)

    else:  # Minimizing player with white piece

        # Set initial score value
        value = math.inf

        # Get all valid moves available to player
        valid_moves = board.opponent_moves('w')

        # Pick move randomly, this move will get changed based on minimax score
        best_row, best_col = random.choice(valid_moves)

        # Get moves by pieces
        player_moves = board.possible_moves('w')

        # Initialize piece with None,it will changed based on minimax score
        best_piece = None

        # Iterate over all possible moves by each piece
        for piece, move_list in player_moves:

            # Check for castling possibility
            castle_moves = []
            left_castle, right_castle = board.castling('w')
            if type(piece) == King:
                if left_castle:
                    for move in left_castle:
                        castle_moves.append(move)
                if right_castle:
                    for move in right_castle:
                        castle_moves.append(move)

            # Add castling moves to piece move_list
            moves = move_list + castle_moves

            # Check if castling is allowed at given position
            for r, c in moves:
                # preserve initial piece and coordinates
                old_row = piece.row
                old_col = piece.col
                dest = board.array[r][c]

                # Make castling move if possible at given coordinates
                if (r, c) in castle_moves:
                    castle = board.castling_move(piece, r, c, 'w')
                    if castle:
                        score, Piece, move = minimax(board, depth - 1, alpha, beta, True)

                        # Reverse the move to get back to initial board state
                        if [(r, c)] == left_castle:
                            board.move_piece(piece, old_row, old_col)
                            board.move_piece(board.white_rook_left, r, c - 2)
                            board.white_king.moved = False
                            board.white_rook_left.moved = False
                        if [(r, c)] == right_castle:
                            board.move_piece(piece, old_row, old_col)
                            board.move_piece(board.white_rook_right, r, c + 1)
                            board.white_king.moved = False
                            board.white_rook_right.moved = False
                        if score < value:
                            value = score
                            best_row = r
                            best_col = c
                            best_move = (best_row, best_col)
                            best_piece = piece
                        beta = min(beta, value)
                        if alpha >= beta:
                            return value, piece, best_move

                else:
                    # Check for pawn promotion
                    promotion = board.move_piece(piece, r, c)
                    if type(piece) == King or type(piece) == Rook:
                        check_castle = piece.moved
                        piece.moved = True

                    # Check if move put player in check
                    check = board.is_checked('w')
                    if check:
                        # Reverse the move if move put piece in check
                        board.move_piece(piece, old_row, old_col)
                        board.array[r][c] = dest
                        if type(piece) == King or type(piece) == Rook:
                            piece.moved = False
                        continue  # move is not allowed stop further execution

                    score, Piece, move = minimax(board, depth - 1, alpha, beta, True)

                    # Revert the move after getting score to get back to initial board state
                    board.move_piece(piece, old_row, old_col)
                    board.array[r][c] = dest

                    # Check king or rook piece's moved state
                    if type(piece) == King or type(piece) == Rook:
                        if check_castle is False:
                            piece.moved = False

                    # Change value to score if score is smaller,change initial piece and move to new piece and move
                    # returned by minimax function
                    if score < value:
                        value = score
                        best_row = r
                        best_col = c
                        best_move = (best_row, best_col)
                        best_piece = piece
                    beta = min(beta, value)

                    # break loop if alpha is bigger than beta
                    if alpha >= beta:
                        return value, piece, best_move

        # Return initial value if no move found which means player in checkmate
        return value, best_piece, (best_row, best_col)
