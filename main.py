import pandas as pd
from data import simulate
from game import Game
from gui import GUI


# TODO#Sounds for call,check,fold,raise
# TODO#(Human) Player buttons
# TODO#(Human) Player cards shown
# TODO# Cards moving animation
# TODO# Better table background, higher resolution
# TODO# Adjust seat positions for 1920/1080.

if __name__ == '__main__':
    game = Game(num_p=6)
    game.run_main(GUI(delay=0.2))

    # Simulate 5 common cards 1000 times,rank all 1326 starting hands based on ratio of 1326 hands they beat
    # df = simulate(n_hands=10, output_save_loc="Data/hand_rankings_100.xlsx")
    # df = pd.read_excel("Data/hand_rankings_1000.xlsx")
