import pygame
import random

class Pong():

    def __init__(self,cpuPlayStyle='following'):
        ### initialize game
        pygame.init()

        ### setup display
        self.DISPLAY_SIZE = self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT = 800, 600
        self.screen = pygame.display.set_mode(self.DISPLAY_SIZE)

        ### set window caption
        pygame.display.set_caption("Future Game by Kevin Narain")

        ### clock
        self.clock = pygame.time.Clock()

        ### hide cursor
        pygame.mouse.set_visible(False)

        ### game constants
        # buttons
        self.P1_UP = pygame.K_w
        self.P1_DOWN = pygame.K_s
        self.P2_UP = pygame.K_UP
        self.P2_DOWN = pygame.K_DOWN

        # other constants
        self.PLAYER_PAD_LENGTH = 100 # playerPaddle #100
        self.PLAYER_PAD2_LENGTH = 100
        self.PLAYER_PAD_SPEED = 10
        self.PLAYER_PAD_WIDTH = 10
        self.BALL_RADIUS = 6

        ### game variables
        ## player scores
        self.p1_score = 0
        self.p2_score = 0

        ## ball speed is split into x and y axes
        self.ball_speed_x = 5
        self.ball_speed_y = 5

        ## ball coordinates
        self.ball_x = 400
        self.ball_y = 300

        ## player pad y's
        self.p1_pad_y = 300
        self.p2_pad_y = 300

        ## player move flags
        self.p1_move_up = False
        self.p1_move_down = False
        self.p2_move_up = False
        self.p2_move_down = False

        ### choose second players

        p2_type = cpuPlayStyle

        if p2_type == 'random':    
            # computer will simulate random clicks
            self.p2_handle_event = self.random_handle_event
            self.p2_update = self.random_update
        elif p2_type == 'following':
            # computer will follor ball
            self.p2_handle_event = self.following_handle_event
            self.p2_update = self.following_update
        else:    
            # human will click keys
            self.p2_handle_event = self.human_handle_event
            self.p2_update = self.human_update
    
    def set_new_paddle(self, playerPaddle):
        self.PLAYER_PAD_LENGTH = playerPaddle

    # --- player2 - computer moves randomly

    def random_handle_event(self,event):
        # do nothing
        pass

    def random_update(self):
        global p2_move_up, p2_move_down

        move = random.randint(1, 2)

        if move == 1: # up
            self.p2_move_up = True
            self.p2_move_down = False
        elif move == 2: # down
            self.p2_move_up = False
            self.p2_move_down = True
        else: # stop        
            self.p2_move_up = False
            self.p2_move_down = False

    # --- player2 - computer follows ball

    def following_handle_event(self,event):
        # do nothing
        pass

    def following_update(self):
        global p2_move_up, p2_move_down

        if self.ball_y < self.p2_pad_y + 50:
            self.p2_move_up = True
            self.p2_move_down = False
        elif self.ball_y > self.p2_pad_y + 50:
            self.p2_move_up = False
            self.p2_move_down = True
        else: # stop        
            self.p2_move_up = False
            self.p2_move_down = False

    # --- player2 - human

    def human_handle_event(self,event):
        global p2_move_up, p2_move_down

        if event.type == pygame.KEYDOWN:
            if event.key == self.P2_UP:
                self.p2_move_up = True
                self.p2_move_down = False
            elif event.key == self.P2_DOWN:
                self.p2_move_down = True
                self.p2_move_up = False
        elif event.type == pygame.KEYUP:
            if event.key == self.P2_UP:
                self.p2_move_up = False
            elif event.key == self.P2_DOWN:
                self.p2_move_down = False

    def human_update(self):
        # do nothing
        pass

    def p1_handle_event(self,running_mean_tmp, movementThreshold):
        global p1_move_up, p1_move_down

        if running_mean_tmp>movementThreshold:
            self.p1_move_up = True
            self.p1_move_down = False
        else:
            self.p1_move_down = True
            self.p1_move_up = False


    def p1_update(self):
        # do nothing
        pass