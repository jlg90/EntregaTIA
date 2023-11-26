from defines import *
import time
from  tools import *
from defines import StoneMove
import copy


class SearchEngine():
    def __init__(self):
        self.m_board = None
        self.m_chess_type = None
        self.m_alphabeta_depth = None
        self.m_total_nodes = 0

    def before_search(self, board, color, alphabeta_depth):
        self.m_board = [row[:] for row in board]
        self.m_chess_type = color
        self.m_alphabeta_depth = alphabeta_depth
        self.m_total_nodes = 0
        
    def alpha_beta_search(self, depth, alpha, beta, maximizing_player, best_move, current_move):
        if depth == 0 or self.is_terminal_node():
            return self.evaluate_board(maximizing_player)
        if maximizing_player:
            max_eval = float('-inf')
            for move in self.get_possible_moves():
                if self.m_board[move.positions[0].x][move.positions[0].y] == Defines.NOSTONE and self.m_board[move.positions[1].x][move.positions[1].y] == Defines.NOSTONE:
                    self.make_move(move, self.m_chess_type)
                    eval = self.alpha_beta_search(depth - 1, alpha, beta, False, best_move, current_move)
                    self.undo_move(move)
                    if eval > max_eval:
                        max_eval = eval
                        if current_move is not None:
                            current_move.positions[0].x = move.positions[0].x
                            current_move.positions[0].y = move.positions[0].y
                            current_move.positions[1].x = move.positions[1].x
                            current_move.positions[1].y = move.positions[1].y
                            current_move.score = move.score
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break 
            return max_eval
        else:
            min_eval = float('inf')
            for move in self.get_possible_moves():
                if self.m_board[move.positions[0].x][move.positions[0].y] == Defines.NOSTONE and self.m_board[move.positions[1].x][move.positions[1].y] == Defines.NOSTONE:
                    self.make_move(move, self.m_chess_type)
                    eval = self.alpha_beta_search(depth - 1, alpha, beta, True, best_move, current_move)
                    self.undo_move(move)
                    if eval < min_eval:
                        min_eval = eval
                        if current_move is not None:
                            current_move.positions[0].x = move.positions[0].x
                            current_move.positions[0].y = move.positions[0].y
                            current_move.positions[1].x = move.positions[1].x
                            current_move.positions[1].y = move.positions[1].y
                            current_move.score = move.score
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
            return min_eval

    def is_valid_move(self, move):
        x, y = move.positions[0].x, move.positions[0].y
        x1, y1 = move.positions[1].x, move.positions[1].y
        return self.m_board[x][y] != Defines.NOSTONE and self.m_board[x1][y1] != Defines.NOSTONE
    
    
    def evaluate_board(self, maximizing_player):
        if maximizing_player:
            player_color = Defines.BLACK
            opponent_color = Defines.WHITE
        else:
            player_color = Defines.WHITE
            opponent_color = Defines.BLACK

        player_score = self.calculate_score(player_color)
        opponent_score = self.calculate_score(opponent_color)

        return player_score - opponent_score

    def make_move(self, move, color):
        for position in move.positions:
            self.m_board[position.x][position.y] = color

    def undo_move(self, move):
        for position in move.positions:
            self.m_board[position.x][position.y] = Defines.NOSTONE

    
    def get_possible_moves(self):
        original_board = copy.deepcopy(self.m_board)  # Guardar el estado original del tablero

        moves = []
        for i1 in range(1, Defines.GRID_NUM - 1):
            for j1 in range(1, Defines.GRID_NUM - 1):
                if self.is_interesting_position(i1, j1):
                    for i2 in range(1, Defines.GRID_NUM - 1):
                        for j2 in range(1, Defines.GRID_NUM - 1):
                            
                            if self.is_interesting_position(i2, j2) and  (i1 != i2 or j1 != j2):
                                move = StoneMove()
                                move.positions[0].x = i1
                                move.positions[0].y = j1
                                move.positions[1].x = i2
                                move.positions[1].y = j2
                                self.make_move(move, self.m_chess_type) 
                                move.score = self.calculate_score(self.m_chess_type)  
                                self.undo_move(move) 
                                moves.append(move)
        moves.sort(key=lambda x: x.score, reverse=True)
        first_moves = moves[:50]
        self.m_board = original_board  # Restaurar el tablero original
        return first_moves

    def is_interesting_position(self, x, y):
        for dx in range(-5, 6):
            for dy in range(-5, 6):
                nx, ny = x + dx, y + dy
                if isValidPos(nx, ny) and self.m_board[nx][ny] != Defines.NOSTONE:
                    return True
        return False

    def calculate_score(self, color):
        player_score = 0
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        score_per_line = {1: 1, 2: 5, 3: 10, 4: 50, 5: 200, 6: 1000}

        for i in range(1, Defines.GRID_NUM - 1):
            for j in range(1, Defines.GRID_NUM - 1):
                if self.m_board[i][j] == color:
                    for direction in directions:
                        stones_in_line = 1
                        potential_in_line = 0
                        blocked_ends = 0

                        # Hacia adelante en la dirección
                        x, y = i, j
                        while stones_in_line < 6:
                            x += direction[0]
                            y += direction[1]
                            if not isValidPos(x, y) or self.m_board[x][y] != color:
                                if isValidPos(x, y) and self.m_board[x][y] != Defines.NOSTONE:
                                    blocked_ends += 1
                                break
                            stones_in_line += 1

                        # Hacia atrás en la dirección
                        x, y = i - direction[0], j - direction[1]
                        while stones_in_line < 6:
                            if not isValidPos(x, y) or self.m_board[x][y] != color:
                                if isValidPos(x, y) and self.m_board[x][y] != Defines.NOSTONE:
                                    blocked_ends += 1
                                break
                            stones_in_line += 1
                            x -= direction[0]
                            y -= direction[1]

                        # Evaluar potencial y bloqueo
                        if blocked_ends < 2:
                            potential_in_line = 6 - stones_in_line - blocked_ends
                            player_score += score_per_line[stones_in_line] + potential_in_line

        return player_score

    def is_terminal_node(self):
        for i in range(1, Defines.GRID_NUM - 1):
            for j in range(1, Defines.GRID_NUM - 1):
                if self.m_board[i][j] == Defines.NOSTONE:
                    return False
        return True


    # Si no hay espacios vacíos, el juego termina en empate.
        return True

def flush_output():
    import sys
    sys.stdout.flush()