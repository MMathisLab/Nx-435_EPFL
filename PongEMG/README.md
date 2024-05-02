# PongEMGDecoding

Welcome to the EMG_Pong game for the NX-435 Course!

Setting up the game takes only a few simple steps:

1. Create a conda environment:
    ```
    conda create -n EMGPong python=3.8 numpy matplotlib jupyter pyserial scipy pygame
    ```
    Note, if pygame will not build with conda, just run the command without it then pip install pygame in the environment.

2. Plug in the Muscle SpikerBox to a USB port on the computer. Set up the box and contacts following this [link](https://backyardbrains.com/experiments/muscleSpikerbox).
    Note, while not needed for the pong game, you should also download the SpikerBox PC app, its super cool ([Download here](http://www.backyardbrains.com/experiments/files/Backyard_Brains_Neuron_Recorder_Install.air.zip)).

3. Activate the environment and open the spike_stream_threshold notebook.

4. Run through the notebook and determine some thresholds you want to try for game control.

5. Open the stream.py file and edit the variables at the top of the code.

6. Run the script, and start playing!
