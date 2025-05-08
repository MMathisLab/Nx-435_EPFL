"""
Flappy Bird game adapted from:

  https://github.com/TimoWilken/flappy-bird-pygame
  Original author: Timo Wilken
  License: MIT

This version has been modified for use with EMG input in a neuroscience course project.
Modifications include: class structure for modular use, EMG decoding input, and main loop integration.
"""

import os
import pygame
from collections import deque
from random import randint
from pygame.locals import *
import math

WIN_WIDTH = 284 * 2
WIN_HEIGHT = 512
FPS = 60
ANIMATION_SPEED = 0.18  # px/ms


def frames_to_msec(frames, fps=FPS):
    return 1000.0 * frames / fps


class Bird(pygame.sprite.Sprite):
    WIDTH = HEIGHT = 32
    SINK_SPEED = 0.18
    CLIMB_SPEED = 0.3
    CLIMB_DURATION = 333.3

    def __init__(self, x, y, msec_to_climb, images):
        super().__init__()
        self.x, self.y = x, y
        self.msec_to_climb = msec_to_climb
        self._img_wingup, self._img_wingdown = images
        self._mask_wingup = pygame.mask.from_surface(self._img_wingup)
        self._mask_wingdown = pygame.mask.from_surface(self._img_wingdown)

    def update(self, delta_frames=1):
        if self.msec_to_climb > 0:
            frac = 1 - self.msec_to_climb / Bird.CLIMB_DURATION
            self.y -= (
                Bird.CLIMB_SPEED
                * frames_to_msec(delta_frames)
                * (1 - math.cos(frac * math.pi))
            )
            self.msec_to_climb -= frames_to_msec(delta_frames)
        else:
            self.y += Bird.SINK_SPEED * frames_to_msec(delta_frames)

    @property
    def image(self):
        return (
            self._img_wingup
            if pygame.time.get_ticks() % 500 >= 250
            else self._img_wingdown
        )

    @property
    def mask(self):
        return (
            self._mask_wingup
            if pygame.time.get_ticks() % 500 >= 250
            else self._mask_wingdown
        )

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, Bird.WIDTH, Bird.HEIGHT)


class PipePair(pygame.sprite.Sprite):
    """Represents an obstacle.

    A PipePair has a top and a bottom pipe, and only between them can
    the bird pass -- if it collides with either part, the game is over.

    Attributes:
    x: The PipePair's X position.  This is a float, to make movement
        smoother.  Note that there is no y attribute, as it will only
        ever be 0.
    image: A pygame.Surface which can be blitted to the display surface
        to display the PipePair.
    mask: A bitmask which excludes all pixels in self.image with a
        transparency greater than 127.  This can be used for collision
        detection.
    top_pieces: The number of pieces, including the end piece, in the
        top pipe.
    bottom_pieces: The number of pieces, including the end piece, in
        the bottom pipe.

    Constants:
    WIDTH: The width, in pixels, of a pipe piece.  Because a pipe is
        only one piece wide, this is also the width of a PipePair's
        image.
    PIECE_HEIGHT: The height, in pixels, of a pipe piece.
    ADD_INTERVAL: The interval, in milliseconds, in between adding new
        pipes.
    """

    WIDTH = 80
    PIECE_HEIGHT = 32
    ADD_INTERVAL = 3000

    def __init__(self, pipe_end_img, pipe_body_img):
        """Initialises a new random PipePair.

        The new PipePair will automatically be assigned an x attribute of
        float(WIN_WIDTH - 1).

        Arguments:
        pipe_end_img: The image to use to represent a pipe's end piece.
        pipe_body_img: The image to use to represent one horizontal slice
            of a pipe's body.
        """
        self.x = float(WIN_WIDTH - 1)
        self.score_counted = False

        self.image = pygame.Surface((PipePair.WIDTH, WIN_HEIGHT), SRCALPHA)
        self.image.convert()  # speeds up blitting
        self.image.fill((0, 0, 0, 0))
        total_pipe_body_pieces = int(
            (
                WIN_HEIGHT  # fill window from top to bottom
                - 6 * Bird.HEIGHT  # make room for bird to fit through
                - 3 * PipePair.PIECE_HEIGHT
            )  # 2 end pieces + 1 body piece
            / PipePair.PIECE_HEIGHT  # to get number of pipe pieces
        )
        self.bottom_pieces = randint(1, total_pipe_body_pieces)
        self.top_pieces = total_pipe_body_pieces - self.bottom_pieces

        # bottom pipe
        for i in range(1, self.bottom_pieces + 1):
            piece_pos = (0, WIN_HEIGHT - i * PipePair.PIECE_HEIGHT)
            self.image.blit(pipe_body_img, piece_pos)
        bottom_pipe_end_y = WIN_HEIGHT - self.bottom_height_px
        bottom_end_piece_pos = (0, bottom_pipe_end_y - PipePair.PIECE_HEIGHT)
        self.image.blit(pipe_end_img, bottom_end_piece_pos)

        # top pipe
        for i in range(self.top_pieces):
            self.image.blit(pipe_body_img, (0, (i * PipePair.PIECE_HEIGHT)))
        top_pipe_end_y = self.top_height_px
        self.image.blit(pipe_end_img, (0, top_pipe_end_y))

        # compensate for added end pieces
        self.top_pieces += 1
        self.bottom_pieces += 1

        # for collision detection
        self.mask = pygame.mask.from_surface(self.image)

    @property
    def top_height_px(self):
        """Get the top pipe's height, in pixels."""
        return self.top_pieces * PipePair.PIECE_HEIGHT

    @property
    def bottom_height_px(self):
        """Get the bottom pipe's height, in pixels."""
        return self.bottom_pieces * PipePair.PIECE_HEIGHT

    @property
    def visible(self):
        """Get whether this PipePair on screen, visible to the player."""
        return -PipePair.WIDTH < self.x < WIN_WIDTH

    @property
    def rect(self):
        """Get the Rect which contains this PipePair."""
        return Rect(self.x, 0, PipePair.WIDTH, PipePair.PIECE_HEIGHT)

    def update(self, delta_frames=1):
        """Update the PipePair's position.

        Arguments:
        delta_frames: The number of frames elapsed since this method was
            last called.
        """
        self.x -= ANIMATION_SPEED * frames_to_msec(delta_frames)

    def collides_with(self, bird):
        """Get whether the bird collides with a pipe in this PipePair.

        Arguments:
        bird: The Bird which should be tested for collision with this
            PipePair.
        """
        return pygame.sprite.collide_mask(self, bird)


class Flappy:
    def __init__(self):
        pygame.init()
        self.DISPLAY_SIZE = WIN_WIDTH, WIN_HEIGHT
        self.screen = pygame.display.set_mode(self.DISPLAY_SIZE)
        pygame.display.set_caption("Flappy EMG Bird")

        self.clock = pygame.time.Clock()
        self.images = self.load_images()
        self.bird = Bird(
            50,
            WIN_HEIGHT // 2,
            0,
            (self.images["bird-wingup"], self.images["bird-wingdown"]),
        )
        self.pipes = deque()
        self.frame_clock = 0
        self.score = 0
        self.done = False
        self.score_font = pygame.font.SysFont(None, 32, bold=True)

    def load_images(self):
        def load(name):
            path = os.path.join(os.path.dirname(__file__), "images", name)
            return pygame.image.load(path).convert_alpha()

        return {
            "background": load("background.png"),
            "pipe-end": load("pipe_end.png"),
            "pipe-body": load("pipe_body.png"),
            "bird-wingup": load("bird_wing_up.png"),
            "bird-wingdown": load("bird_wing_down.png"),
        }

    def handle_input(self, emg_value, threshold):
        if emg_value > threshold and self.bird.msec_to_climb <= 0:
            self.bird.msec_to_climb = Bird.CLIMB_DURATION

    def update(self):
        if self.done:
            return

        if self.frame_clock % (PipePair.ADD_INTERVAL * FPS // 1000) == 0:
            self.pipes.append(
                PipePair(self.images["pipe-end"], self.images["pipe-body"])
            )

        pipe_collision = any(p.collides_with(self.bird) for p in self.pipes)
        if pipe_collision or self.bird.y < 0 or self.bird.y > WIN_HEIGHT - Bird.HEIGHT:
            self.done = True

        while self.pipes and not self.pipes[0].visible:
            self.pipes.popleft()

        for pipe in self.pipes:
            pipe.update()

        self.bird.update()
        for pipe in self.pipes:
            if pipe.x + PipePair.WIDTH < self.bird.x and not pipe.score_counted:
                self.score += 1
                pipe.score_counted = True

        self.frame_clock += 1

    def draw(self):
        for x in (0, WIN_WIDTH // 2):
            self.screen.blit(self.images["background"], (x, 0))

        for pipe in self.pipes:
            self.screen.blit(pipe.image, pipe.rect)

        self.screen.blit(self.bird.image, self.bird.rect)

        score_surf = self.score_font.render(str(self.score), True, (255, 255, 255))
        score_x = WIN_WIDTH // 2 - score_surf.get_width() // 2
        self.screen.blit(score_surf, (score_x, PipePair.PIECE_HEIGHT))

        pygame.display.flip()
        self.clock.tick(FPS)
