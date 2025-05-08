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


# Running mean volage is just one of several ways you could use the data from this stream.
# Discuss some other ways you might want to parse the datastream, and
def running_mean(data, window_size):
    """Compute the running mean over a given window size."""
    cumsum = np.cumsum(np.insert(data, 0, 0))
    return (cumsum[window_size:] - cumsum[:-window_size]) / window_size


### SET SOME VARIABLES ###
cport = "COM3"  # set the correct port before you run it
inputBufferSize = 2000  # keep between 2000-20000
movementThreshold = 24  # start with 1 std above running mean
playerPaddle = 200  # refers to paddle size, default is 100
cpuPlayStyle = "following"  # options are 'following' or 'random'
game_choice = "flappy"  # Choose your game! Options are "flappy" or "pong"
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


if __name__ == "__main__":
    main()
