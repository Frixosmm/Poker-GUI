import pandas as pd

from card import draw_cards, combinations
from data import *

from game import Game
from gui import GUI

# TODO#Sounds for call,check,fold,raise

# TODO# Cards moving animation



if __name__ == '__main__':
    game = Game(num_p=6)
    game.run_main(GUI(delay=0))
    #game.new_game()
    # game.betting_round(gui=None)
    #simulate(10000,output_save_loc="Data/hand_rankings_10000.xlsx")
    #plot_frequencies(data_loc="Data/hand_rankings_10000.xlsx")



