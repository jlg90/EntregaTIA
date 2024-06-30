from tools import *
from defines import *
import math
import numpy as np
import time
import  random
class SearchEngine():
    def __init__(self):
        # Inicializa los atributos del motor de búsqueda
        self.m_board = None  # Tablero de juego
        self.m_chess_type = None  # Tipo de ficha actual
        self.m_alphabeta_depth = None  # Profundidad de búsqueda alpha-beta
        self.m_total_nodes = 0  # Número total de nodos explorados
        self.ourColor = 0  # Color de la ficha del motor

        # Ventana de búsqueda de amenazas
        self.possible_first_x = 1
        self.possible_first_y = Defines.GRID_NUM - 1
        self.possible_last_x = Defines.GRID_NUM - 1
        self.possible_last_y = 1

        self.turn = 0  # Contador de turnos
        self.pre_move = [StoneMove(), StoneMove()]  # Movimientos previos

    def restart(self):
        # Reinicia los parámetros del motor de búsqueda
        self.possible_first_x = 1
        self.possible_first_y = Defines.GRID_NUM - 1
        self.possible_last_x = Defines.GRID_NUM - 1
        self.possible_last_y = 1
        self.turn = 0
        self.pre_move = [StoneMove(), StoneMove()]

    def before_search(self, board, color, alphabeta_depth):
        # Prepara el motor de búsqueda copiando el tablero y estableciendo parámetros
        self.m_board = [row[:] for row in board]
        self.m_chess_type = color
        self.m_alphabeta_depth = alphabeta_depth
        self.m_total_nodes = 0

    def alpha_beta_search(self, depth, alpha, beta, ourColor, bestMove, preMove):
        # Realiza la búsqueda alpha-beta para encontrar el mejor movimiento
        self.ourColor = ourColor
        self.m_alphabeta_depth = 2
        
        # Verifica si el juego ha sido ganado por el último movimiento
        if is_win_by_premove(self.m_board, preMove):
            print("ALGUIEN HA GANADO")

            if ourColor == self.m_chess_type:
                # Si el oponente gana
                return 0
            else:
                # Si el motor gana
                return Defines.MININT + 1

        self.pre_move[0] = preMove
        if self.turn == 0:
            self.pre_move[1] = preMove

        self.turn += 2
        
        alpha = 0
        # Verifica si es el primer movimiento del juego
        if self.check_first_move():
            bestMove.positions[0].x = 10
            bestMove.positions[0].y = 10
            bestMove.positions[1].x = 10
            bestMove.positions[1].y = 10
        else:
            # Realiza la búsqueda del mejor movimiento posible
            move = self.find_possible_move(self.m_alphabeta_depth)
            alpha = move[0]

            bestMove.positions[0].x = move[1][0][0]
            bestMove.positions[0].y = move[1][0][1]
            bestMove.positions[1].x = move[1][1][0]
            bestMove.positions[1].y = move[1][1][1]

            self.pre_move[1] = bestMove

        return alpha
    
    def check_first_move(self):
        # Comprueba si el tablero está vacío (primer movimiento)
        for i in range(1, len(self.m_board) - 1):
            for j in range(1, len(self.m_board[i]) - 1):
                if self.m_board[i][j] != Defines.NOSTONE:
                    return False
        return True
    
    def find_possible_move(self, depth, turn=0):
        # Busca movimientos posibles en el tablero
        possibles = []
        for i in range(1,20):
            for j in  range(1,20):
                if self.m_board[i][j] is Defines.NOSTONE:
                    possibles.append([i,j])
        #Randomizamos  el contenido de la lista con las posiciones del tablero libres para que cada vez  comienze con la lectura del mismo  desde un punto diferente.
        random.shuffle(possibles) 
        localscore = [0, [[-1, -1], [-1, -1]]]
        self.transp = {}
        localscore = self.negamax(possibles, depth, -math.inf, math.inf)  # Aplica NEGAMAX

        return localscore
    
    def negamax(self, candidates, depth_level, alpha_cutoff, beta_cutoff, current_turn=1):
        # Función de búsqueda MAX para el algoritmo de búsqueda alpha-beta
        better_move = [0, [[-1, -1], [-1, -1]]]

        # Condición base: se alcanza la profundidad máxima de búsqueda
        if depth_level == 0:
            better_move[0] = self.evaluate_threats(self.ourColor)
            return better_move
        else:
            better_move[0] = float('-inf')
            candidate_move = StoneMove()
            search_color = self.ourColor

            if current_turn == -1:
                search_color = Defines.BLACK if self.ourColor == Defines.WHITE else Defines.WHITE

            index = 0

            # Explora los movimientos candidatos
            for first_position in candidates:
                candidates.remove(first_position)

                for second_position in candidates:
                    # Configura el movimiento candidato
                    candidate_move.positions[0].x = first_position[0]
                    candidate_move.positions[0].y = first_position[1]
                    candidate_move.positions[1].x = second_position[0]
                    candidate_move.positions[1].y = second_position[1]

                    # Realiza el movimiento en el tablero
                    make_move(self.m_board, candidate_move, search_color)

                    # Inicializa la puntuación tentativa del movimiento
                    tentative_score = [0, [[-1, -1], [-1, -1]]]

                    # Realiza la búsqueda recursiva y almacena la puntuación
                    recursive_score = self.negamax(candidates, depth_level - 1, -alpha_cutoff, -beta_cutoff, -current_turn)
                    tentative_score[0] = -recursive_score[0]
                    tentative_score[1] = [first_position, second_position]

                    # Deshace el movimiento en el tablero
                    make_move(self.m_board, candidate_move, Defines.NOSTONE)

                    # Aplica la poda alpha-beta
                    if tentative_score[0] > better_move[0]:
                        better_move = tentative_score

                    if better_move[0] >= beta_cutoff:
                        return better_move

                    if better_move[0] > alpha_cutoff:
                        alpha_cutoff = better_move[0]

                    if alpha_cutoff >= beta_cutoff:
                        return better_move

                candidates.insert(index, first_position)
                index += 1

        return better_move



    def evaluate_threats(self, color):
        # Evalúa las amenazas en el tablero para ambos jugadores y calcula la puntuación
        opponent_color = Defines.BLACK if color == Defines.WHITE else Defines.WHITE

        max_threat_score = 0
        min_threat_score = 0

        directions = [
            (1, 0),  # Horizontal
            (0, 1),  # Vertical
            (1, 1),  # Diagonal \
            (1, -1)  # Diagonal /
        ]

        def evaluate_line(x, y, dx, dy, player_color):
            # Evalúa una línea específica en el tablero para contar fichas y espacios
            stones = 0
            spaces = 0
            block_count = 0
            score = 0
            consecutive_stones = 0
            for i in range(-5, 1):
                for j in range(6):
                    nx, ny = x + (i + j) * dx, y + (i + j) * dy
                    if 0 <= nx < Defines.GRID_NUM and 0 <= ny < Defines.GRID_NUM:
                        if self.m_board[nx][ny] == player_color:
                            consecutive_stones += 1
                        elif self.m_board[nx][ny] == Defines.NOSTONE:
                            spaces += 1
                        else:
                            block_count += 1

                if consecutive_stones == 6:
                    score += math.inf
                elif consecutive_stones == 5 and spaces >= 1:
                    score += 50000
                elif consecutive_stones == 4 and spaces >= 2:
                    score += 10000
                elif consecutive_stones == 3 and spaces >= 3:
                    score += 1000
                elif consecutive_stones == 2 and spaces >= 4:
                    score += 100

                # Resetea para la siguiente evaluación
                consecutive_stones = 0
                spaces = 0
                block_count = 0

            return score

        for x in range(Defines.GRID_NUM):
            for y in range(Defines.GRID_NUM):
                for dx, dy in directions:
                    max_threat_score += evaluate_line(x, y, dx, dy, color)
                    min_threat_score += evaluate_line(x, y, dx, dy, opponent_color)

        return max_threat_score - min_threat_score


def flush_output():
    # Función para forzar la salida estándar
    import sys
    sys.stdout.flush()
