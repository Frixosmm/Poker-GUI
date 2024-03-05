import pandas as pd
from data import simulate
from game import Game
from gui import GUI

# TODO#Sounds for call,check,fold,raise

# TODO# Cards moving animation

# TODO# Adjust seat positions for 1920/1080.


if __name__ == '__main__':
    game = Game(num_p=6)
    game.run_main(GUI(delay=0.2))
    # game.new_game()
    # game.betting_round(gui=None)
