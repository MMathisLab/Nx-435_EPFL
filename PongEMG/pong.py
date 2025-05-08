import pygame
import random


class Pong:

    def __init__(self, cpuPlayStyle="following"):
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
        self.PLAYER_PAD_LENGTH = 100  # playerPaddle #100
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

        if p2_type == "random":
            # computer will simulate random clicks
            self.p2_handle_event = self.random_handle_event
            self.p2_update = self.random_update
        elif p2_type == "following":
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

    def random_handle_event(self, event):
        # do nothing
        pass

    def random_update(self):
        global p2_move_up, p2_move_down

        move = random.randint(1, 2)

        if move == 1:  # up
            self.p2_move_up = True
            self.p2_move_down = False
        elif move == 2:  # down
            self.p2_move_up = False
            self.p2_move_down = True
        else:  # stop
            self.p2_move_up = False
            self.p2_move_down = False

    # --- player2 - computer follows ball

    def following_handle_event(self, event):
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
        else:  # stop
            self.p2_move_up = False
            self.p2_move_down = False

    # --- player2 - human

    def human_handle_event(self, event):
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

    def handle_input(self, emg_val, threshold):
        self.p1_handle_event(emg_val, threshold)

    ### Alter this block if you want to expand gameplay options ###
    ###############################################################
    def p1_handle_event(self, running_mean_tmp, movementThreshold):
        global p1_move_up, p1_move_down

        if running_mean_tmp > movementThreshold:
            self.p1_move_up = True
            self.p1_move_down = False
        else:
            self.p1_move_down = True
            self.p1_move_up = False

    ###############################################################

    def p1_update(self):
        # do nothing
        pass

    def draw(self):

        ## clear the screen
        self.screen.fill(pygame.Color(0, 0, 0, 255))

        ## draw ball
        pygame.draw.circle(
            self.screen,
            pygame.Color(255, 255, 255, 255),
            (self.ball_x, self.ball_y),
            self.BALL_RADIUS,
        )

        ## draw P1 pad
        pygame.draw.rect(
            self.screen,
            pygame.Color(255, 255, 255, 255),
            (0, self.p1_pad_y, self.PLAYER_PAD_WIDTH, self.PLAYER_PAD_LENGTH),
        )

        ## draw P2 pad
        pygame.draw.rect(
            self.screen,
            pygame.Color(255, 255, 255, 255),
            (
                self.DISPLAY_WIDTH - self.PLAYER_PAD_WIDTH,
                self.p2_pad_y,
                self.PLAYER_PAD_WIDTH,
                self.PLAYER_PAD2_LENGTH,
            ),
        )

        ## draw center line
        pygame.draw.rect(
            self.screen,
            pygame.Color(255, 255, 255, 255),
            (self.DISPLAY_WIDTH / 2, 0, 1, self.DISPLAY_HEIGHT),
        )

        ## draw player scores
        # create font
        score_font = pygame.font.Font(None, 30)

        # draw p1 score
        p1_score_text = str(self.p1_score)
        p1_score_render = score_font.render(
            p1_score_text, 1, pygame.Color(255, 255, 255, 255)
        )
        self.screen.blit(p1_score_render, (self.DISPLAY_WIDTH / 2 - 50, 50))

        # draw p2 score
        p2_score_text = str(self.p2_score)
        p2_score_render = score_font.render(
            p2_score_text, 1, pygame.Color(255, 255, 255, 255)
        )
        self.screen.blit(p2_score_render, (self.DISPLAY_WIDTH / 2 + 50, 50))

        ## pygame.display.flip() is called in order to update graphics properly
        pygame.display.flip()

        ## tick the clock so we have 60 fps game
        self.clock.tick(60)

    def update(self):

        # get other changes
        self.p1_update()
        self.p2_update()

        ## move player pads according to player move flags
        if self.p1_move_up:
            self.p1_pad_y -= self.PLAYER_PAD_SPEED
            if self.p1_pad_y < 0:
                self.p1_pad_y = 0
        elif self.p1_move_down:
            self.p1_pad_y += self.PLAYER_PAD_SPEED
            if self.p1_pad_y > self.DISPLAY_HEIGHT - self.PLAYER_PAD_LENGTH:
                self.p1_pad_y = self.DISPLAY_HEIGHT - self.PLAYER_PAD_LENGTH
        if self.p2_move_up:
            self.p2_pad_y -= self.PLAYER_PAD_SPEED
            if self.p2_pad_y < 0:
                self.p2_pad_y = 0
        elif self.p2_move_down:
            self.p2_pad_y += self.PLAYER_PAD_SPEED
            if self.p2_pad_y > self.DISPLAY_HEIGHT - self.PLAYER_PAD2_LENGTH:
                self.p2_pad_y = self.DISPLAY_HEIGHT - self.PLAYER_PAD2_LENGTH

        ## move ball
        self.ball_x += self.ball_speed_x
        self.ball_y += self.ball_speed_y

        ## check ball position
        # if out screen vertically, flip self.ball_speed_y
        if self.ball_y < 0 or self.ball_y > self.DISPLAY_HEIGHT - self.BALL_RADIUS:
            self.ball_speed_y = -self.ball_speed_y

        # if out screen horizontally, check whether player pad is there or not
        # if not, release the ball at the center towards scoring player
        if self.ball_x < 0:
            if self.p1_pad_y < self.ball_y < self.p1_pad_y + self.PLAYER_PAD_LENGTH:
                self.ball_speed_x = -self.ball_speed_x
            else:
                self.p2_score += 1
                self.ball_x = 400
                self.ball_y = 300
                self.ball_speed_x = 5
                self.ball_speed_y = 5
        elif self.ball_x > self.DISPLAY_WIDTH:
            if self.p2_pad_y < self.ball_y < self.p2_pad_y + self.PLAYER_PAD2_LENGTH:
                self.ball_speed_x = -self.ball_speed_x
            else:
                self.p1_score += 1
                self.ball_x = 400
                self.ball_y = 300
                self.ball_speed_x = -5
                self.ball_speed_y = -5
