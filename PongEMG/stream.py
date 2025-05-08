from spikerbox_serial import read_arduino, process_data, init_serial
import numpy as np
import pygame
from pong import Pong

from multiprocessing import Process, Value
from ctypes import c_double

from flappy import Flappy


def emg_process_loop(shared_mean, cport, inputBufferSize):
    from spikerbox_serial import read_arduino, process_data, init_serial
    import numpy as np

    ser = init_serial(cport)
    while True:
        data = read_arduino(ser, inputBufferSize)
        processed = process_data(data)
        if len(processed) > 0:
            signal = np.abs(
                np.array(processed) - 500
            )  # this offset may need to be changed
            mean_val = np.mean(signal)
            shared_mean.value = mean_val


def running_mean(data, window_size):
    """Compute the running mean over a given window size."""
    cumsum = np.cumsum(np.insert(data, 0, 0))
    return (cumsum[window_size:] - cumsum[:-window_size]) / window_size


### SET SOME VARIABLES ###
cport = "COM3"  # set the correct port before you run it
inputBufferSize = 2000  # keep between 2000-20000
movementThreshold = 14  # start with 1 std above running mean
playerPaddle = 200  # refers to paddle size, default is 100
cpuPlayStyle = "following"  # options are 'following' or 'random'
game_choice = "pong"  # Choose your game! Options are "flappy" or "pong"
use_emg = True
###


##### If you want to modify the p1_handle_event function, go into the pong script and modify the p1_handle_event(running_mean_tmp)


def main():
    # Select game
    # game_choice = "flappy"  # or "pong"
    if game_choice == "flappy":
        game = Flappy()
    elif game_choice == "pong":
        game = Pong(cpuPlayStyle="following")
        game.set_new_paddle(playerPaddle)
    else:
        raise ValueError("Invalid game_choice")

    # Shared EMG signal value

    if use_emg:
        emg_mean = Value(c_double, 0.0)
        proc = Process(target=emg_process_loop, args=(emg_mean, cport, inputBufferSize))
        proc.start()
    else:
        emg_mean = None

    # Main game loop
    while True:

        if use_emg:
            emg_val = emg_mean.value
        else:
            keys = pygame.key.get_pressed()
            emg_val = movementThreshold + 10 if keys[pygame.K_SPACE] else 0

        # if use_emg:
        #     emg_val = emg_mean.value
        # else:
        #     keys = pygame.key.get_pressed()
        #     if keys[pygame.K_SPACE]:
        #         emg_val = movementThreshold + 10  # simulate a "spike"
        #     else:
        #         emg_val = 0  # simulate resting baseline

        game.handle_input(emg_val, movementThreshold)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if hasattr(game, "p2_handle_event"):  # only Pong has this
                game.p2_handle_event(event)

        # if hasattr(game, "p1_update"):
        #     game.p1_update()
        # if hasattr(game, "p2_update"):
        #     game.p2_update()

        game.update()
        game.draw()

        if getattr(game, "done", False):
            print("Game over!")
            pygame.time.wait(2000)
            pygame.quit()
            exit()


if __name__ == "__main__":
    main()


##### If you want to modify the p1_handle_event function, go into the pong script and modify the p1_handle_event(running_mean_tmp)


def main():

    pong = Pong(cpuPlayStyle="following")
    pong.set_new_paddle(playerPaddle)
    ser = init_serial(cport)

    ### main game loop
    while True:

        data = read_arduino(ser, inputBufferSize)
        data_temp = process_data(data)
        data_preproc = np.abs(data_temp - 500)

        # print(data_preproc)
        running_mean_tmp = running_mean(data_preproc, 500)
        running_tmp_time = np.mean(running_mean_tmp)

        ## detect and process main events
        pong.p1_handle_event(running_tmp_time, movementThreshold)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            # get players keys
            pong.p2_handle_event(event)

        # get other changes
        pong.p1_update()
        pong.p2_update()

        ## move player pads according to player move flags
        if pong.p1_move_up:
            pong.p1_pad_y -= pong.PLAYER_PAD_SPEED
            if pong.p1_pad_y < 0:
                pong.p1_pad_y = 0
        elif pong.p1_move_down:
            pong.p1_pad_y += pong.PLAYER_PAD_SPEED
            if pong.p1_pad_y > pong.DISPLAY_HEIGHT - pong.PLAYER_PAD_LENGTH:
                pong.p1_pad_y = pong.DISPLAY_HEIGHT - pong.PLAYER_PAD_LENGTH
        if pong.p2_move_up:
            pong.p2_pad_y -= pong.PLAYER_PAD_SPEED
            if pong.p2_pad_y < 0:
                pong.p2_pad_y = 0
        elif pong.p2_move_down:
            pong.p2_pad_y += pong.PLAYER_PAD_SPEED
            if pong.p2_pad_y > pong.DISPLAY_HEIGHT - pong.PLAYER_PAD2_LENGTH:
                pong.p2_pad_y = pong.DISPLAY_HEIGHT - pong.PLAYER_PAD2_LENGTH

        ## move ball
        pong.ball_x += pong.ball_speed_x
        pong.ball_y += pong.ball_speed_y

        ## check ball position
        # if out screen vertically, flip pong.ball_speed_y
        if pong.ball_y < 0 or pong.ball_y > pong.DISPLAY_HEIGHT - pong.BALL_RADIUS:
            pong.ball_speed_y = -pong.ball_speed_y

        # if out screen horizontally, check whether player pad is there or not
        # if not, release the ball at the center towards scoring player
        if pong.ball_x < 0:
            if pong.p1_pad_y < pong.ball_y < pong.p1_pad_y + pong.PLAYER_PAD_LENGTH:
                pong.ball_speed_x = -pong.ball_speed_x
            else:
                pong.p2_score += 1
                pong.ball_x = 400
                pong.ball_y = 300
                pong.ball_speed_x = 5
                pong.ball_speed_y = 5
        elif pong.ball_x > pong.DISPLAY_WIDTH:
            if pong.p2_pad_y < pong.ball_y < pong.p2_pad_y + pong.PLAYER_PAD2_LENGTH:
                pong.ball_speed_x = -pong.ball_speed_x
            else:
                pong.p1_score += 1
                pong.ball_x = 400
                pong.ball_y = 300
                pong.ball_speed_x = -5
                pong.ball_speed_y = -5

        ## clear the screen
        pong.screen.fill(pygame.Color(0, 0, 0, 255))

        ## draw ball
        pygame.draw.circle(
            pong.screen,
            pygame.Color(255, 255, 255, 255),
            (pong.ball_x, pong.ball_y),
            pong.BALL_RADIUS,
        )

        ## draw P1 pad
        pygame.draw.rect(
            pong.screen,
            pygame.Color(255, 255, 255, 255),
            (0, pong.p1_pad_y, pong.PLAYER_PAD_WIDTH, pong.PLAYER_PAD_LENGTH),
        )

        ## draw P2 pad
        pygame.draw.rect(
            pong.screen,
            pygame.Color(255, 255, 255, 255),
            (
                pong.DISPLAY_WIDTH - pong.PLAYER_PAD_WIDTH,
                pong.p2_pad_y,
                pong.PLAYER_PAD_WIDTH,
                pong.PLAYER_PAD2_LENGTH,
            ),
        )

        ## draw center line
        pygame.draw.rect(
            pong.screen,
            pygame.Color(255, 255, 255, 255),
            (pong.DISPLAY_WIDTH / 2, 0, 1, pong.DISPLAY_HEIGHT),
        )

        ## draw player scores
        # create font
        score_font = pygame.font.Font(None, 30)

        # draw p1 score
        p1_score_text = str(pong.p1_score)
        p1_score_render = score_font.render(
            p1_score_text, 1, pygame.Color(255, 255, 255, 255)
        )
        pong.screen.blit(p1_score_render, (pong.DISPLAY_WIDTH / 2 - 50, 50))

        # draw p2 score
        p2_score_text = str(pong.p2_score)
        p2_score_render = score_font.render(
            p2_score_text, 1, pygame.Color(255, 255, 255, 255)
        )
        pong.screen.blit(p2_score_render, (pong.DISPLAY_WIDTH / 2 + 50, 50))

        ## pygame.display.flip() is called in order to update graphics properly
        pygame.display.flip()

        ## tick the clock so we have 60 fps game
        pong.clock.tick(60)


if __name__ == "__main__":
    main()
