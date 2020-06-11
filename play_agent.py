from agents import *
from chess_game import *
import pygame as p


class TestAgentGame:
    game: ChessGame = None
    agent: Agent = None
    WIDTH = HEIGHT = 512
    DIMENSION = 8
    SQ_SIZE = HEIGHT // DIMENSION
    MAX_FPS = 15
    IMAGES = {}

    def __init__(self, agent=Agent.MM):
        self.game = ChessGame()
        self.agent = agent

    def load_images(self):
        image_dict = {'WhiteKing': 'wki', 'BlackKing': 'bki', 'WhiteQueen': 'wq', 'BlackQueen': 'bq',
                      'WhiteRook': 'wro', 'BlackRook': 'bro', 'WhiteBishop': 'wbi', 'BlackBishop': 'bbi',
                      'WhiteKnight': 'wkn', 'BlackKnight': 'bkn', 'WhitePawn': 'wpa', 'BlackPawn': 'bpa'}
        for x in image_dict.keys():
            self.IMAGES[x] = p.transform.scale(p.image.load(f'sprites/{image_dict[x]}.png'),
                                               (self.SQ_SIZE, self.SQ_SIZE))

    def draw_game_state(self, screen, gs):
        self.draw_board(screen)
        # Can add highlighting and stuff here
        self.draw_peices(screen, gs.get_board())

    def draw_board(self, screen):
        colors = [p.Color('white'), p.Color('gray')]
        for row in range(self.DIMENSION):
            [p.draw.rect(screen, colors[(row + col) % 2],
                         p.Rect(col * self.SQ_SIZE, row * self.SQ_SIZE, self.SQ_SIZE, self.SQ_SIZE))
             for col in range(self.DIMENSION)]

    def draw_peices(self, screen, board):
        for row in range(self.DIMENSION):
            for col in range(self.DIMENSION):
                piece = board[row][col]
                if piece is not None:
                    screen.blit(self.IMAGES[piece.value], p.Rect(col * self.SQ_SIZE, row * self.SQ_SIZE, self.SQ_SIZE,
                                                                 self.SQ_SIZE))

    def agent_game(self):
        p.init()
        screen = p.display.set_mode((self.WIDTH, self.HEIGHT))
        clock = p.time.Clock()
        screen.fill(p.Color("white"))
        gs = self.game
        self.load_images()
        # (<row>,<col>)
        sq_selected = ()
        # [<first_coor>,<second_coor>]
        player_clicks = []
        selected_piece = None
        running = True
        agent = self.agent

        while running:
            for e in p.event.get():
                if e.type == p.QUIT:
                    running = False
                if e.type == p.MOUSEBUTTONDOWN:
                    if gs.which_turn:
                        # print("==================================Your Turn==================================")
                        pass
                    # click piece you want to move if not valid then it won't input it
                    location = p.mouse.get_pos()
                    col = location[0] // self.SQ_SIZE
                    row = location[1] // self.SQ_SIZE
                    if sq_selected == (row, col):
                        print('undid the move')
                        sq_selected = ()
                        player_clicks = []
                        selected_piece = None
                    else:
                        sq_selected = (row, col)
                        player_clicks.append(sq_selected)
                    if len(player_clicks) == 2:
                        # validate if the move is valid
                        is_valid_move = False
                        selected_piece = gs.get_board()[player_clicks[0][0]][player_clicks[0][1]]
                        if selected_piece in gs.get_ptype(gs.which_turn):
                            valid_move_dict = gs.get_val_moves()
                            for x in gs.get_pieces(gs.which_turn):
                                if gs.get_pieces(gs.which_turn)[x] == (player_clicks[0][0], player_clicks[0][1]):
                                    if (player_clicks[1][0], player_clicks[1][1]) in valid_move_dict[x]:
                                        is_valid_move = True
                        if is_valid_move:
                            # make the move
                            if gs.which_turn:
                                piece_to_move = [x for x in gs.wagent_pieces.keys()
                                                 if gs.wagent_pieces[x] == (player_clicks[0][0], player_clicks[0][1])][
                                    0]
                                gs.move_piece(piece_to_move,
                                              (player_clicks[1][0], player_clicks[1][1]), gs.which_turn)
                                sq_selected = ()
                                player_clicks = []
                                selected_piece = None
                                gs.end_turn()

                                # Agent Move
                                tmp_agent = ChessAgent(gs, agent)
                                move = tmp_agent.pick_move(2)
                                gs.move_piece(move[0], move[1], gs.which_turn)
                                gs.end_turn()

                        else:
                            print(f'{player_clicks} is not valid')
                            sq_selected = ()
                            player_clicks = []
                            selected_piece = None
                    if gs.check_game_over(gs.which_turn):
                        print('checkmate?')
                        running = False

            self.draw_game_state(screen, gs)
            clock.tick(self.MAX_FPS)
            p.display.flip()


if __name__ == '__main__':
    test = TestAgentGame(agent=Agent.MM)
    test.agent_game()
