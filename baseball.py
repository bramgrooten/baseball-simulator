"""
Python script to simulate the offense side of a baseball game,
such that we can compare different lineup possibilities.
"""
from batter import Batter
import pandas as pd
import numpy as np
from numpy.random import rand


class Game:
    def __init__(self, lineup, nr_innings=9, printing=False,
                 prob_advance_runner_on_out=0.2):
        self.lineup = lineup
        self.nr_innings = nr_innings
        self.printing = printing
        self.game_state = {}
        self.reset_game_state()

        self.prob_advance_runner_on_out = prob_advance_runner_on_out


    def reset_game_state(self):
        self.game_state = {'score': 0, 'inning':    1,
                           'outs':  0, 'batter_up': 1,
                           'bases_occupied': [False, False, False]}
                           # '1st_base_occupied': False,
                           # '2nd_base_occupied': False,
                           # '3rd_base_occupied': False}

    def play(self):
        if self.printing:
            self.print_lineup()
        for inning in range(self.nr_innings):
            if self.printing:
                print(f"\nInning {inning+1}")
            self.play_inning()
            self.game_state['inning'] += 1

    def play_inning(self):
        self.game_state['bases_occupied'] = [False, False, False]
        self.game_state['outs'] = 0
        while self.game_state['outs'] < 3:
            self.steal()
            self.play_batter()
            self.double_play()
            self.next_batter()

    def play_batter(self):
        batter = self.lineup[self.game_state['batter_up']]
        outcome = batter.swing()
        # options = ["strike-out", "in-play-out", "walk",
        #            "single", "double", "triple", "homerun"]
        if outcome == 'strike-out':
            self.strike_out()
        elif outcome == 'in-play-out':
            self.in_play_out()
        elif outcome == 'walk':
            self.walk()
        elif outcome == 'single':
            self.single()
        elif outcome == 'double':
            self.double()
        elif outcome == 'triple':
            self.triple()
        elif outcome == 'homerun':
            self.homerun()

    def strike_out(self):
        self.game_state['outs'] += 1

    def in_play_out(self):
        self.game_state['outs'] += 1
        if rand() < self.prob_advance_runner_on_out:
            self.sac_fly_or_bunt()

        .idea/
        __pycache__/


    def steal(self):
        # todo
        pass

    def double_play(self):
        # todo
        pass

    def sac_fly_or_bunt(self):
        # todo
        # runners might advance even if batter is out
        pass

    def next_batter(self):
        if self.game_state['batter_up'] < 9:
            self.game_state['batter_up'] += 1
        else:
            self.game_state['batter_up'] = 1

    def print_lineup(self):
        print("The lineup for today's game is:\n")
        for batter in self.lineup:
            print(batter.name)
        print("\nPLAY BALL!\n")

    def get_score(self):
        return self.game_state['score']




if __name__ == '__main__':
    dataset = pd.read_excel("mlb2019.xls", sheet_name=0, header=0)
    # marteke01
    # lemahdj01
    # moncayo01
    # urshegi01
    # reynobr01
    # alvaryo01
    # brantmi02

    lineup_id = [
        'anderti01',
        'bogaexa01',
        'yelicch01',

        'tatisfe02',
        'deverra01',
        'cruzne02',

        'arenano01',
        'blackch02',
        'rendoan01',
        ]
    assert len(lineup_id) == 9

    lineup = []
    for batter_id in lineup_id:
        batter = Batter(player_id=batter_id, dataset=dataset)
        lineup.append(batter)

    # game = Game(lineup)
    # game.print_lineup()
    # scores = []
    # nr_games = 100
    # for _ in range(nr_games):
    #     game.reset_game_state()
    #     game.play()
    #     scores.append(game.get_score())
    # avg_score = np.mean(scores)
    #
    # print(f"\nAverage score after {nr_games} games is: {avg_score} runs.\n")


