from enum import Enum


class GamePiece(Enum):
    WKI = 'WhiteKing'
    BKI = 'BlackKing'
    WQU = 'WhiteQueen'
    BQU = 'BlackQueen'
    WRO = 'WhiteRook'
    BRO = 'BlackRook'
    WBI = 'WhiteBishop'
    BBI = 'BlackBishop'
    WKN = 'WhiteKnight'
    BKN = 'BlackKnight'
    WPA = 'WhitePawn'
    BPA = 'BlackPawn'


class ChessGame:
    def __init__(self):
        # the game state of the chess game
        self.chess_board = [[None for x in range(8)] for y in range(8)]

        # used to indicate which turn it is True = White, False = Black
        self.which_turn: bool = True

        # list of which pieces belong to which team
        self.white_piece: list = [GamePiece.WKI, GamePiece.WQU, GamePiece.WRO, GamePiece.WKN, GamePiece.WBI, GamePiece.WPA]
        self.black_piece: list = [GamePiece.BKI, GamePiece.BQU, GamePiece.BRO, GamePiece.BKN, GamePiece.BBI, GamePiece.BPA]
        self.piece_types = {True: self.white_piece, False: self.black_piece}

        # dict of black and white agent pieces where key is the piece and value is coord
        self.wagent_pieces: dict = {}
        self.bagent_pieces: dict = {}
        self.pieces = {True: self.wagent_pieces, False: self.bagent_pieces}

        # dict storing how much of each piece that they have
        self.wagent_piece_count: dict = {'WhiteKing': 0, 'WhiteQueen': 0, 'WhiteRook': 0, 'WhiteBishop': 0,
                                         'WhiteKnight': 0, 'WhitePawn': 0}
        self.bagent_piece_count: dict = {'BlackKing': 0, 'BlackQueen': 0, 'BlackRook': 0, 'BlackBishop': 0,
                                         'BlackKnight': 0, 'BlackPawn': 0}
        self.piece_count: dict = {True: self.wagent_piece_count, False: self.bagent_piece_count}

        # these booleans are used for checking if a king can castle or not
        self.wagent_ki_move = False
        self.bagent_ki_move = False
        self.wagent_r1_move = False
        self.wagent_r2_move = False
        self.bagent_r1_move = False
        self.bagent_r2_move = False

        '''
        initialize the chess_board to what the start of a chess game is and then it updates the chess_pieces and 
        the chess_piece_count dictionaries accordingly
        '''
        for x in range(0, 8):
            self.chess_board[1][x] = GamePiece.WPA
            self.wagent_pieces[f'p{x}'] = (1, x)
            self.wagent_piece_count['WhitePawn'] += 1
            self.chess_board[6][x] = GamePiece.BPA
            self.bagent_pieces[f'p{x}'] = (6, x)
            self.bagent_piece_count['BlackPawn'] += 1

        self.chess_board[0][0], self.chess_board[0][7] = GamePiece.WRO, GamePiece.WRO
        self.wagent_pieces['r1'] = (0, 0)
        self.wagent_pieces['r2'] = (0, 7)
        self.wagent_piece_count['WhiteRook'] += 2
        self.chess_board[7][0], self.chess_board[7][7] = GamePiece.BRO, GamePiece.BRO
        self.bagent_pieces['r1'] = (7, 0)
        self.bagent_pieces['r2'] = (7, 7)
        self.bagent_piece_count['BlackRook'] += 2
        self.chess_board[0][1], self.chess_board[0][6] = GamePiece.WKN, GamePiece.WKN
        self.wagent_pieces['kn1'] = (0, 1)
        self.wagent_pieces['kn2'] = (0, 6)
        self.wagent_piece_count['WhiteKnight'] += 2
        self.chess_board[7][1], self.chess_board[7][6] = GamePiece.BKN, GamePiece.BKN
        self.bagent_pieces['kn1'] = (7, 1)
        self.bagent_pieces['kn2'] = (7, 6)
        self.bagent_piece_count['BlackKnight'] += 2
        self.chess_board[0][2], self.chess_board[0][5] = GamePiece.WBI, GamePiece.WBI
        self.wagent_pieces['b1'] = (0, 2)
        self.wagent_pieces['b2'] = (0, 5)
        self.wagent_piece_count['WhiteBishop'] += 2
        self.chess_board[7][2], self.chess_board[7][5] = GamePiece.BBI, GamePiece.BBI
        self.bagent_pieces['b1'] = (7, 2)
        self.bagent_pieces['b2'] = (7, 5)
        self.bagent_piece_count['BlackBishop'] += 2
        self.chess_board[0][3] = GamePiece.WQU
        self.wagent_pieces['q'] = (0, 3)
        self.wagent_piece_count['WhiteQueen'] += 1
        self.chess_board[7][3] = GamePiece.BQU
        self.bagent_pieces['q'] = (7, 3)
        self.bagent_piece_count['BlackQueen'] += 1
        self.chess_board[0][4] = GamePiece.WKI
        self.wagent_pieces['ki'] = (0, 4)
        self.wagent_piece_count['WhiteKing'] += 1
        self.chess_board[7][4] = GamePiece.BKI
        self.bagent_pieces['ki'] = (7, 4)
        self.bagent_piece_count['BlackKing'] += 1

    # returns the 2d array of the chess board
    def get_board(self) -> list:
        return self.chess_board

    # returns the pieces dict for a specific player (uses the wagent or bagent keys)
    def get_pieces(self, agent: bool) -> dict:
        return self.pieces[agent]

    # returns the piece count for a specific player (uses the GamePiece values for keys)
    def get_pcount(self, agent) -> dict:
        return self.piece_count[agent]

    # returns an agent's piece types
    def get_ptype(self, agent) -> list:
        return self.piece_types[agent]

    # returns all the valid moves
    def get_val_moves(self) -> dict:
        if self.king_in_check(self.which_turn):
            return self.get_out_of_check(self.which_turn)
        else:
            move_list = {}
            for x in self.get_pieces(self.which_turn).keys():
                move_list[x] = [y for y in self.get_moves(self.get_pieces(self.which_turn)[x])
                                if not self.move_check_check(x, y, self.which_turn)]
            return move_list

    def piece_attacking(self, coor):
        piece_type = self.get_board()[coor[0]][coor[1]]
        if piece_type.value == 'BlackPawn':
            return [x for x in self.get_moves(coor) if x != (coor[0]-1, coor[1])]
        elif piece_type.value == 'WhitePawn':
            return [x for x in self.get_moves(coor) if x != (coor[0]+1, coor[1])]
        else:
            return self.get_moves(coor)

    # returns a true or false to check if current agent lost
    def check_game_over(self, agent: bool) -> bool:
        player_to_check = {True: 'White', False: 'Black'}
        if self.king_in_check(agent):
            goc_moves = self.get_out_of_check(agent)
            # print(goc_moves)
            if len(goc_moves) == 0:
                print(f'{player_to_check[agent]} loses')
                return True
            else:
                # print(f'{player_to_check[agent]} can get out of check: {goc_moves}')
                return False
        else:
            # print(f'{player_to_check[agent]} not in check')
            return False

    # helper function that checks if the king is in check
    def king_in_check(self, agent: bool) -> bool:
        # checks to see if the other player can move to king's location
        other_player_pieces = self.get_pieces(not agent)
        for x in other_player_pieces.keys():
            if self.get_pieces(agent)['ki'] in self.piece_attacking(self.get_pieces(not agent)[x]):
                return True
            else:
                continue

        # if true is not returned return False because king is not in check
        return False

    # helper move that returns a dict of pieces u can move and where they can move
    def get_out_of_check(self, agent: bool) -> dict:
        possible_moves = {}
        agent_pieces = self.get_pieces(agent)

        # find moves that a player can make where the king will no longer be in check (uses move_check_check method)
        for x in agent_pieces.keys():
            piece_moves = [y for y in self.get_moves(agent_pieces[x]) if not self.move_check_check(x, y, agent)]
            if x == 'ki':
                if agent:
                    if not self.wagent_ki_move:
                        piece_moves = [x for x in piece_moves if x not in [(0, 2), (0, 5)]]
                else:
                    if not self.bagent_ki_move:
                        piece_moves = [x for x in piece_moves if x not in [(7, 2), (7, 5)]]

            if len(piece_moves) != 0:
                possible_moves[x] = piece_moves

        return possible_moves

    # helper function that checks if a move results in a check and then returns the result
    def move_check_check(self, piece: str, move: tuple, agent: bool) -> bool:
        agent_pieces = self.get_pieces(agent)

        # move the piece the piece check if the agent king is in check and the move things back
        old_coor = agent_pieces[piece]
        temp_piece = self.get_board()[move[0]][move[1]]
        agent_pieces[piece] = move
        self.get_board()[move[0]][move[1]] = self.get_board()[old_coor[0]][old_coor[1]]
        self.get_board()[old_coor[0]][old_coor[1]] = None
        in_check = self.king_in_check(agent)
        self.get_board()[old_coor[0]][old_coor[1]] = self.get_board()[move[0]][move[1]]
        self.get_board()[move[0]][move[1]] = temp_piece
        agent_pieces[piece] = old_coor

        return in_check

    # changes the turn to the other player
    def end_turn(self) -> None:
        self.which_turn = not self.which_turn

    # move piece (handle castle and pawn promotion)
    def move_piece(self, piece: str, new_coor: tuple, agent: bool) -> None:
        agent_to_castlebools = {True: [self.wagent_ki_move, self.wagent_r1_move, self.wagent_r2_move],
                                False: [self.bagent_ki_move, self.bagent_r1_move, self.bagent_r2_move]}
        if piece == 'ki':
            agent_to_castlebools[agent][0] = True
        if piece == 'r1':
            agent_to_castlebools[agent][1] = True
        if piece == 'r2':
            agent_to_castlebools[agent][2] = True

        agent_pieces = self.get_pieces(agent)
        old_coor = agent_pieces[piece]
        agent_pieces[piece] = new_coor
        if new_coor in self.get_pieces(not agent).values():
            for x in self.get_pieces(not agent).keys():
                if self.get_pieces(not agent)[x] == new_coor:
                    del self.get_pieces(not agent)[x]
                    # print(self.get_pcount(not agent))
                    self.get_pcount(not agent)[self.get_board()[new_coor[0]][new_coor[1]].value] -= 1
                    break
        self.get_board()[new_coor[0]][new_coor[1]] = self.get_board()[old_coor[0]][old_coor[1]]
        self.get_board()[old_coor[0]][old_coor[1]] = None

        # handle pawn promotion
        if piece[0] == 'p':
            if agent:
                if agent_pieces[piece][0] == 7:
                    # IMPORTANT: I made black promotion for Queen for AI purposes only I need to change this in the future
                    # replace_piece = input('what do you want to pick: WhiteQueen, WhiteRook, WhiteBishop, WhiteKnight')
                    self.replace_piece(piece, 'WhiteQueen', agent)
            else:
                if agent_pieces[piece][0] == 0:
                    # IMPORTANT: I made black promotion for Queen for AI purposes only I need to change this in the future
                    # replace_piece = input('what do you want to pick: BlackQueen, BlackROok, BlackBishop, BlackKnight')
                    self.replace_piece(piece, 'BlackQueen', agent)
        # handle castling
        elif piece[0:2] == 'ki':
            if agent:
                if new_coor == (0, 2) and self.wagent_ki_move:
                    self.move_piece('r1', (0, 3), agent)
                if new_coor == (0, 6):
                    self.move_piece('r2', (0, 5), agent)
            else:
                if new_coor == (7, 2) and self.bagent_ki_move:
                    self.move_piece('r1', (7, 3), agent)
                if new_coor == (7, 6):
                    self.move_piece('r2', (7, 5), agent)

    def get_moves(self, coor: tuple) -> list:
        piece = self.get_board()[coor[0]][coor[1]]
        if piece is None:
            return []
        else:
            move_dict: dict = {'WhiteKing': self.get_moves_wki,
                               'BlackKing': self.get_moves_bki,
                               'WhiteQueen': self.get_moves_wqu,
                               'BlackQueen': self.get_moves_bqu,
                               'WhiteRook': self.get_moves_wro,
                               'BlackRook': self.get_moves_bro,
                               'WhiteBishop': self.get_moves_wbi,
                               'BlackBishop': self.get_moves_bbi,
                               'WhiteKnight': self.get_moves_wkn,
                               'BlackKnight': self.get_moves_bkn,
                               'WhitePawn': self.get_moves_wpa,
                               'BlackPawn': self.get_moves_bpa}
            return move_dict[piece.value](coor)

    def castle_moves(self, agent: bool) -> list:
        castle_move_list = []
        if agent:
            if self.wagent_ki_move is False:
                if not self.wagent_r1_move:
                    if self.get_board()[0][1] is None and self.get_board()[0][2] is None and self.get_board()[0][3] is None:
                        castle_move_list.append((0, 2))

                if not self.wagent_r2_move:
                    if self.get_board()[0][5] is None and self.get_board()[0][6] is None:
                        castle_move_list.append((0, 6))
        else:
            if self.bagent_ki_move is False:
                if not self.bagent_r1_move:
                    if self.get_board()[7][1] is None and self.get_board()[7][2] is None and self.get_board()[7][3] is None:
                        castle_move_list.append((7, 2))

                if not self.bagent_r2_move:
                    if self.get_board()[7][5] is None and self.get_board()[7][6] is None:
                        castle_move_list.append((7, 6))
        return castle_move_list

    def get_moves_wki(self, coor: tuple) -> list:
        possible_moves = [(coor[0], coor[1]+1),
                          (coor[0]+1, coor[1]),
                          (coor[0]+1, coor[1]+1),
                          (coor[0]+1, coor[1]-1),
                          (coor[0]-1, coor[1]),
                          (coor[0]-1, coor[1]+1),
                          (coor[0]-1, coor[1]-1),
                          (coor[0], coor[1]-1)]
        legal_moves = [x for x in possible_moves if 0 <= x[0] <= 7
                       and 0 <= x[1] <= 7
                       and not (self.chess_board[x[0]][x[1]] in self.white_piece)]
        castle_moves_list = self.castle_moves(True)
        # print(castle_moves_list)
        if len(castle_moves_list) != 0:
            for x in castle_moves_list:
                legal_moves.append(x)

        return legal_moves

    def get_moves_bki(self, coor: tuple) -> list:
        possible_moves = [(coor[0], coor[1] + 1),
                          (coor[0] + 1, coor[1]),
                          (coor[0] + 1, coor[1] + 1),
                          (coor[0] + 1, coor[1] - 1),
                          (coor[0] - 1, coor[1]),
                          (coor[0] - 1, coor[1] + 1),
                          (coor[0] - 1, coor[1] - 1),
                          (coor[0], coor[1] - 1)]
        legal_moves = [x for x in possible_moves if 0 <= x[0] <= 7
                       and 0 <= x[1] <= 7
                       and not (self.chess_board[x[0]][x[1]] in self.black_piece)]
        castle_moves_list = self.castle_moves(False)
        if len(castle_moves_list) != 0:
            for x in castle_moves_list:
                legal_moves.append(x)
        return legal_moves

    def get_moves_wqu(self, coor: tuple) -> list:
        possible_moves = []

        # get left moves and right moves
        for x in range(coor[1]+1, 8):
            if self.chess_board[coor[0]][x] is None:
                possible_moves.append((coor[0], x))
            else:
                if self.chess_board[coor[0]][x] in self.black_piece:
                    possible_moves.append((coor[0], x))
                    break
                else:
                    break
        for x in range(coor[1] - 1, -1, -1):
            if self.chess_board[coor[0]][x] is None:
                possible_moves.append((coor[0], x))
            else:
                if self.chess_board[coor[0]][x] in self.black_piece:
                    possible_moves.append((coor[0], x))
                    break
                else:
                    break

        # get up moves and down moves
        for x in range(coor[0] + 1, 8):
            if self.chess_board[x][coor[1]] is None:
                possible_moves.append((x, coor[1]))
            else:
                if self.chess_board[x][coor[1]] in self.black_piece:
                    possible_moves.append((x, coor[1]))
                    break
                else:
                    break
        for x in range(coor[0] - 1, -1, -1):
            if self.chess_board[x][coor[1]] is None:
                possible_moves.append((x, coor[1]))
            else:
                if self.chess_board[x][coor[1]] in self.black_piece:
                    possible_moves.append((x, coor[1]))
                    break
                else:
                    break

        # get right up diag moves
        x, y = coor
        x += 1
        y += 1
        while x < 8 and y < 8:
            if self.chess_board[x][y] is None:
                possible_moves.append((x, y))
            else:
                if self.chess_board[x][y] in self.black_piece:
                    possible_moves.append((x, y))
                    break
                else:
                    break
            x += 1
            y += 1

        # get right down diag moves
        x, y = coor
        x += 1
        y += -1
        while x < 8 and y > -1:
            if self.chess_board[x][y] is None:
                possible_moves.append((x, y))
            else:
                if self.chess_board[x][y] in self.black_piece:
                    possible_moves.append((x, y))
                    break
                else:
                    break
            x += 1
            y += -1

        # get left down diag moves
        x, y = coor
        x += -1
        y += -1
        while x > -1 and y > -1:
            if self.chess_board[x][y] is None:
                possible_moves.append((x, y))
            else:
                if self.chess_board[x][y] in self.black_piece:
                    possible_moves.append((x, y))
                    break
                else:
                    break
            x += -1
            y += -1

        # get left up diag moves
        x, y = coor
        x += -1
        y += 1
        while x > -1 and y < 8:
            if self.chess_board[x][y] is None:
                possible_moves.append((x, y))
            else:
                if self.chess_board[x][y] in self.black_piece:
                    possible_moves.append((x, y))
                    break
                else:
                    break
            x += -1
            y += 1

        return possible_moves

    def get_moves_bqu(self, coor: tuple) -> list:
        possible_moves = []

        # get left moves and right moves
        for x in range(coor[1] + 1, 8):
            if self.chess_board[coor[0]][x] is None:
                possible_moves.append((coor[0], x))
            else:
                if self.chess_board[coor[0]][x] in self.white_piece:
                    possible_moves.append((coor[0], x))
                    break
                else:
                    break
        for x in range(coor[1] - 1, -1, -1):
            if self.chess_board[coor[0]][x] is None:
                possible_moves.append((coor[0], x))
            else:
                if self.chess_board[coor[0]][x] in self.white_piece:
                    possible_moves.append((coor[0], x))
                    break
                else:
                    break

        # get up moves and down moves
        for x in range(coor[0] + 1, 8):
            if self.chess_board[x][coor[1]] is None:
                possible_moves.append((x, coor[1]))
            else:
                if self.chess_board[x][coor[1]] in self.white_piece:
                    possible_moves.append((x, coor[1]))
                    break
                else:
                    break
        for x in range(coor[0] - 1, -1, -1):
            if self.chess_board[x][coor[1]] is None:
                possible_moves.append((x, coor[1]))
            else:
                if self.chess_board[x][coor[1]] in self.white_piece:
                    possible_moves.append((x, coor[1]))
                    break
                else:
                    break

        # get right up diag moves
        x, y = coor
        x += 1
        y += 1
        while x < 8 and y < 8:
            if self.chess_board[x][y] is None:
                possible_moves.append((x, y))
            else:
                if self.chess_board[x][y] in self.white_piece:
                    possible_moves.append((x, y))
                    break
                else:
                    break
            x += 1
            y += 1

        # get right down diag moves
        x, y = coor
        x += 1
        y += -1
        while x < 8 and y > -1:
            if self.chess_board[x][y] is None:
                possible_moves.append((x, y))
            else:
                if self.chess_board[x][y] in self.white_piece:
                    possible_moves.append((x, y))
                    break
                else:
                    break
            x += 1
            y += -1

        # get left down diag moves
        x, y = coor
        x += -1
        y += -1
        while x > -1 and y > -1:
            if self.chess_board[x][y] is None:
                possible_moves.append((x, y))
            else:
                if self.chess_board[x][y] in self.white_piece:
                    possible_moves.append((x, y))
                    break
                else:
                    break
            x += -1
            y += -1

        # get left up diag moves
        x, y = coor
        x += -1
        y += 1
        while x > -1 and y < 8:
            if self.chess_board[x][y] is None:
                possible_moves.append((x, y))
            else:
                if self.chess_board[x][y] in self.white_piece:
                    possible_moves.append((x, y))
                    break
                else:
                    break
            x += -1
            y += 1

        return possible_moves

    def get_moves_wro(self, coor: tuple) -> list:
        possible_moves = []

        # get left moves and right moves
        for x in range(coor[1] + 1, 8):
            if self.chess_board[coor[0]][x] is None:
                possible_moves.append((coor[0], x))
            else:
                if self.chess_board[coor[0]][x] in self.black_piece:
                    possible_moves.append((coor[0], x))
                    break
                else:
                    break
        for x in range(coor[1] - 1, -1, -1):
            if self.chess_board[coor[0]][x] is None:
                possible_moves.append((coor[0], x))
            else:
                if self.chess_board[coor[0]][x] in self.black_piece:
                    possible_moves.append((coor[0], x))
                    break
                else:
                    break

        # get up moves and down moves
        for x in range(coor[0] + 1, 8):
            if self.chess_board[x][coor[1]] is None:
                possible_moves.append((x, coor[1]))
            else:
                if self.chess_board[x][coor[1]] in self.black_piece:
                    possible_moves.append((x, coor[1]))
                    break
                else:
                    break
        for x in range(coor[0] - 1, -1, -1):
            if self.chess_board[x][coor[1]] is None:
                possible_moves.append((x, coor[1]))
            else:
                if self.chess_board[x][coor[1]] in self.black_piece:
                    possible_moves.append((x, coor[1]))
                    break
                else:
                    break
        return possible_moves

    def get_moves_bro(self, coor: tuple) -> list:
        possible_moves = []

        # get left moves and right moves
        for x in range(coor[1] + 1, 8):
            if self.chess_board[coor[0]][x] is None:
                possible_moves.append((coor[0], x))
            else:
                if self.chess_board[coor[0]][x] in self.white_piece:
                    possible_moves.append((coor[0], x))
                    break
                else:
                    break
        for x in range(coor[1] - 1, -1, -1):
            if self.chess_board[coor[0]][x] is None:
                possible_moves.append((coor[0], x))
            else:
                if self.chess_board[coor[0]][x] in self.white_piece:
                    possible_moves.append((coor[0], x))
                    break
                else:
                    break

        # get up moves and down moves
        for x in range(coor[0] + 1, 8):
            if self.chess_board[x][coor[1]] is None:
                possible_moves.append((x, coor[1]))
            else:
                if self.chess_board[x][coor[1]] in self.white_piece:
                    possible_moves.append((x, coor[1]))
                    break
                else:
                    break
        for x in range(coor[0] - 1, -1, -1):
            if self.chess_board[x][coor[1]] is None:
                possible_moves.append((x, coor[1]))
            else:
                if self.chess_board[x][coor[1]] in self.white_piece:
                    possible_moves.append((x, coor[1]))
                    break
                else:
                    break
        return possible_moves

    def get_moves_wbi(self, coor: tuple) -> list:
        possible_moves = []

        # get right up diag moves
        x, y = coor
        x += 1
        y += 1
        while x < 8 and y < 8:
            if self.chess_board[x][y] is None:
                possible_moves.append((x, y))
            else:
                if self.chess_board[x][y] in self.black_piece:
                    possible_moves.append((x, y))
                    break
                else:
                    break
            x += 1
            y += 1

        # get right down diag moves
        x, y = coor
        x += 1
        y += -1
        while x < 8 and y > -1:
            if self.chess_board[x][y] is None:
                possible_moves.append((x, y))
            else:
                if self.chess_board[x][y] in self.black_piece:
                    possible_moves.append((x, y))
                    break
                else:
                    break
            x += 1
            y += -1

        # get left down diag moves
        x, y = coor
        x += -1
        y += -1
        while x > -1 and y > -1:
            if self.chess_board[x][y] is None:
                possible_moves.append((x, y))
            else:
                if self.chess_board[x][y] in self.black_piece:
                    possible_moves.append((x, y))
                    break
                else:
                    break
            x += -1
            y += -1

        # get left up diag moves
        x, y = coor
        x += -1
        y += 1
        while x > -1 and y < 8:
            if self.chess_board[x][y] is None:
                possible_moves.append((x, y))
            else:
                if self.chess_board[x][y] in self.black_piece:
                    possible_moves.append((x, y))
                    break
                else:
                    break
            x += -1
            y += 1
        return possible_moves

    def get_moves_bbi(self, coor: tuple) -> list:
        possible_moves = []

        # get right up diag moves
        x, y = coor
        x += 1
        y += 1
        while x < 8 and y < 8:
            if self.chess_board[x][y] is None:
                possible_moves.append((x, y))
            else:
                if self.chess_board[x][y] in self.white_piece:
                    possible_moves.append((x, y))
                    break
                else:
                    break
            x += 1
            y += 1

        # get right down diag moves
        x, y = coor
        x += 1
        y += -1
        while x < 8 and y > -1:
            if self.chess_board[x][y] is None:
                possible_moves.append((x, y))
            else:
                if self.chess_board[x][y] in self.white_piece:
                    possible_moves.append((x, y))
                    break
                else:
                    break
            x += 1
            y += -1

        # get left down diag moves
        x, y = coor
        x += -1
        y += -1
        while x > -1 and y > -1:
            if self.chess_board[x][y] is None:
                possible_moves.append((x, y))
            else:
                if self.chess_board[x][y] in self.white_piece:
                    possible_moves.append((x, y))
                    break
                else:
                    break
            x += -1
            y += -1

        # get left up diag moves
        x, y = coor
        x += -1
        y += 1
        while x > -1 and y < 8:
            if self.chess_board[x][y] is None:
                possible_moves.append((x, y))
            else:
                if self.chess_board[x][y] in self.white_piece:
                    possible_moves.append((x, y))
                    break
                else:
                    break
            x += -1
            y += 1

        return possible_moves

    def get_moves_wkn(self, coor: tuple) -> list:
        possible_moves = [(coor[0] + 1, coor[1] + 2),
                          (coor[0] - 1, coor[1] + 2),
                          (coor[0] + 1, coor[1] - 2),
                          (coor[0] - 1, coor[1] - 2),
                          (coor[0] + 2, coor[1] + 1),
                          (coor[0] + 2, coor[1] - 1),
                          (coor[0] - 2, coor[1] + 1),
                          (coor[0] - 2, coor[1] - 1)]
        legal_moves = [x for x in possible_moves if 0 <= x[0] <= 7
                       and 0 <= x[1] <= 7
                       and not (self.chess_board[x[0]][x[1]] in self.white_piece)]
        return legal_moves

    def get_moves_bkn(self, coor: tuple) -> list:
        possible_moves = [(coor[0] + 1, coor[1] + 2),
                          (coor[0] - 1, coor[1] + 2),
                          (coor[0] + 1, coor[1] - 2),
                          (coor[0] - 1, coor[1] - 2),
                          (coor[0] + 2, coor[1] + 1),
                          (coor[0] + 2, coor[1] - 1),
                          (coor[0] - 2, coor[1] + 1),
                          (coor[0] - 2, coor[1] - 1)]
        legal_moves = [x for x in possible_moves if 0 <= x[0] <= 7
                       and 0 <= x[1] <= 7
                       and not (self.chess_board[x[0]][x[1]] in self.black_piece)]
        return legal_moves

    def get_moves_wpa(self, coor: tuple) -> list:
        possible_moves = []
        if coor[0] == 1:
            if self.chess_board[coor[0] + 2][coor[1]] is None:
                possible_moves.append((coor[0] + 2, coor[1]))
        if coor[0] + 1 <= 7 and self.chess_board[coor[0] + 1][coor[1]] is None:
            possible_moves.append((coor[0] + 1, coor[1]))
        if coor[0] + 1 <= 7 and coor[1] + 1 < 8:
            if self.chess_board[coor[0] + 1][coor[1] + 1] in self.black_piece:
                possible_moves.append((coor[0] + 1, coor[1] + 1))
        if coor[0] + 1 <= 7  and coor[1] - 1 > -1:
            if self.chess_board[coor[0] + 1][coor[1] - 1] in self.black_piece:
                possible_moves.append((coor[0] + 1, coor[1] - 1))
        return possible_moves

    def get_moves_bpa(self, coor: tuple) -> list:
        possible_moves = []
        if coor[0] == 6:
            if self.chess_board[coor[0] - 2][coor[1]] is None:
                possible_moves.append((coor[0] - 2, coor[1]))
        if coor[1] >= 0 and self.chess_board[coor[0] - 1][coor[1]] is None:
            possible_moves.append((coor[0] - 1, coor[1]))
        if coor[1] >= 0 and coor[1] + 1 < 8:
            if self.chess_board[coor[0] - 1][coor[1] + 1] in self.white_piece:
                possible_moves.append((coor[0] - 1, coor[1] + 1))
        if coor[1] >= 0 and coor[1] - 1 > -1:
            if self.chess_board[coor[0] - 1][coor[1] - 1] in self.white_piece:
                possible_moves.append((coor[0] - 1, coor[1] - 1))
        return possible_moves

    def replace_piece(self, old_piece: str, new_piece_type: str, agent: bool) -> None:
        gp_to_dk = {'WhiteQueen': 'q',
                    'BlackQueen': 'q',
                    'WhiteRook': 'r',
                    'BlackRook': 'r',
                    'WhiteBishop': 'b',
                    'BlackBishop': 'b',
                    'WhiteKnight': 'kn',
                    'BlackKnight': 'kn',
                    'WhitePawn': 'p',
                    'BlackPawn': 'p'}

        gp_to_enum = {'WhiteQueen': GamePiece.WQU,
                      'BlackQueen': GamePiece.BQU,
                      'WhiteRook': GamePiece.WRO,
                      'BlackRook': GamePiece.BRO,
                      'WhiteBishop': GamePiece.WBI,
                      'BlackBishop': GamePiece.BBI,
                      'WhiteKnight': GamePiece.WKI,
                      'BlackKnight': GamePiece.BKI,
                      'WhitePawn': GamePiece.WPA,
                      'BlackPawn': GamePiece.BPA}

        if agent:
            temp_coor = self.wagent_pieces[old_piece]
            self.wagent_piece_count[(self.get_board()[temp_coor[0]][temp_coor[1]]).value] -= 1
            self.wagent_piece_count[new_piece_type] += 1
            self.wagent_pieces[f'{gp_to_dk[new_piece_type]}{self.wagent_piece_count[new_piece_type]}'] = temp_coor
            self.get_board()[temp_coor[0]][temp_coor[1]] = gp_to_enum[new_piece_type]

        else:
            temp_coor = self.bagent_pieces[old_piece]
            self.bagent_piece_count[(self.get_board()[temp_coor[0]][temp_coor[1]]).value] -= 1
            self.bagent_piece_count[new_piece_type] += 1
            self.bagent_pieces[f'{gp_to_dk[new_piece_type]}{self.bagent_piece_count[new_piece_type]}'] = temp_coor
            self.get_board()[temp_coor[0]][temp_coor[1]] = gp_to_enum[new_piece_type]
