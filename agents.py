from chess_game import *
from enum import Enum
from copy import copy

class Agent(Enum):
    MM = 'MinMax'
    AS = 'AStar'
    BF = 'BellmanFord'
    NN = 'NeuralNetwork'

class ChessAgent():

    cg: ChessGame = None
    agent: Agent = None

    def __init__(self, game_state: ChessGame, agent: Agent):
        self.cg = game_state
        self.agent = agent

    # get the value of the gamestate
    def get_board_val(self, gs: ChessGame, agent:bool) -> int:
        # this is the initial board value
        val_dict_w = {'WhiteKing': 0, 'WhiteQueen': 9, 'WhiteRook': 5, 'WhiteBishop': 3,
                                         'WhiteKnight': 3, 'WhitePawn': 1}
        val_dict_b = {'BlackKing': 0, 'BlackQueen': 9, 'BlackRook': 5, 'BlackBishop': 3,
                                         'BlackKnight': 3, 'BlackPawn': 1}
        val_dict = {True: val_dict_w, False: val_dict_b}
        val_dict_agent = val_dict[agent]
        val_dict_player = val_dict[not agent]
        # board_val = -1 * (8 + (2 * 5) + (3 * 4) + 9)
        board_val = 0
        for x in gs.get_pcount(agent).keys():
            board_val += val_dict_agent[x] * gs.get_pcount(agent)[x]
        for x in gs.get_pcount(not agent).keys():
            board_val += - (val_dict_player[x] * gs.get_pcount(not agent)[x])

        return board_val

    # n is the number of moves ahead it will consider. will spit out {'piece': (new coord)}
    def pick_move(self, n: int) -> dict:
        move_dict = {'MinMax': self.minimax, 'AStar': self.astar, 'BellmanFord': self.bellmanford,
                     'NeuralNetwork': self.neuralnet}
        return move_dict[self.agent.value](self.cg, n)

    # returns tuple (piece, move_location, value)
    def minimax(self, gs: ChessGame, n: int) -> tuple:
        max_turn = self.minimaxPick(gs, n, -999999, 999999, True, '', '')
        return max_turn

    def minimaxPick(self, gs: ChessGame, n: int, alpha: int, beta: int, is_agent: bool, move: str, piece: str) -> tuple:
        if gs.check_game_over(is_agent):
            return piece, move, -999999
        if gs.check_game_over(not is_agent):
            return piece, move, 999999

        else:
            if n == 0:
                # print(f'{piece} to {move} generates value: {self.get_board_val(gs, gs.which_turn)}')
                return piece, move, self.get_board_val(gs, gs.which_turn)
            else:
                if is_agent:
                    best_val = -999999
                    best_piece = ''
                    best_move = ''
                    did_break: bool = False
                    # print(gs.get_val_moves())
                    for x in gs.get_val_moves().keys():
                        for y in gs.get_val_moves()[x]:
                            next_gs = self.get_next_state(x, y, gs)
                            # input()
                            # print('blacks turn')
                            # print(f'x: {x}, y: {y}')
                            # print(f'white_pieces{next_gs.get_pieces(True)}')
                            # print(f'black_pieces{next_gs.get_pieces(False)}')
                            value = self.minimaxPick(next_gs, n, alpha, beta, (not is_agent), y, x)
                            if best_val < value[2]:
                                # print(f'{x} to {y} generates a max of {value[2]}')
                                best_piece = x
                                best_move = y
                                best_val = value[2]
                                alpha = max(alpha, best_val)
                            if beta <= alpha:
                                # print(f'beta: {beta}, alpha: {alpha}')
                                did_break = True
                                break
                        if did_break:
                            break
                    return best_piece, best_move, best_val
                else:
                    best_val = 999999
                    best_piece = ''
                    best_move = ''
                    did_break: bool = False
                    for x in gs.get_val_moves().keys():
                        for y in gs.get_val_moves()[x]:
                            next_gs = self.get_next_state(x, y, gs)
                            # input()
                            # print('whites turn')
                            # print(f'x: {x}, y: {y}')
                            # print(f'white_pieces{next_gs.get_pieces(True)}')
                            # print(f'black_pieces{next_gs.get_pieces(False)}')
                            value = self.minimaxPick(next_gs, n - 1, alpha, beta, (not is_agent), y, x)
                            if best_val > value[2]:
                                # print(f'{x} to {y} generates a min of {value[2]}')
                                best_piece = x
                                best_move = y
                                best_val = value[2]
                                beta = min(beta, best_val)
                            if beta <= alpha:
                                # print(f'beta: {beta}, alpha: {alpha}')
                                did_break = True
                                break
                        if did_break:
                            break
                    return best_piece, best_move, best_val

    def get_next_state(self, piece: str, move: tuple, gs: ChessGame):
        game_state = ChessGame()
        for x in range(8):
            for y in range(8):
                game_state.chess_board[x][y] = copy(gs.get_board()[x][y])
        game_state.which_turn = not copy(gs.which_turn)
        game_state.white_piece = copy(gs.white_piece)
        game_state.black_piece = copy(gs.black_piece)
        game_state.piece_types = {True: game_state.white_piece, False: game_state.black_piece}
        game_state.wagent_pieces = copy(gs.wagent_pieces)
        game_state.bagent_pieces = copy(gs.bagent_pieces)
        game_state.pieces = {True: game_state.wagent_pieces, False: game_state.bagent_pieces}
        game_state.wagent_piece_count = copy(gs.wagent_piece_count)
        game_state.bagent_piece_count = copy(gs.bagent_piece_count)
        game_state.piece_count = {True: game_state.wagent_piece_count, False: game_state.bagent_piece_count}
        game_state.wagent_ki_move = copy(gs.wagent_ki_move)
        game_state.bagent_ki_move = copy(gs.bagent_ki_move)
        game_state.wagent_r1_move = copy(gs.wagent_r1_move)
        game_state.wagent_r2_move = copy(gs.wagent_r2_move)
        game_state.bagent_r1_move = copy(gs.bagent_r1_move)
        game_state.bagent_r2_move = copy(gs.bagent_r2_move)

        game_state.move_piece(piece, (move[0], move[1]), not game_state.which_turn)

        return game_state


    def astar(self, gs: ChessGame, n: int):
        pass

    def bellmanford(self, gs: ChessGame, n: int):
        pass

    def neuralnet(self, gs: ChessGame, n: int):
        pass
