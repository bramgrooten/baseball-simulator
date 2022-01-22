"""
Python script to simulate the offense side of a baseball game,
such that we can compare different lineup possibilities.

Possible improvements:
- make double play prob depend on where runners are on base
- make double play prob depend on which runner it is
- make steal probs depend on which runner it is
- actually, make all probabilities depend on which runner it is
- make prob_advance_runner_on_out depend on where runners are on base
"""
from batter import Batter
import pandas as pd
import numpy as np


class Game:
    def __init__(self, lineup, nr_innings=9, printing=False,
                 prob_advance_runner_on_out=0.2,
                 prob_double_play=0.4,
                 prob_steal_2nd_base=0.05,
                 prob_steal_3rd_base=0.01,
                 prob_steal_home=0.001,
                 prob_1st_to_3rd=0.2,
                 prob_score_from_2nd_on_single=0.5,
                 prob_score_from_1st_on_double=0.3):
        self.lineup = lineup
        self.nr_innings = nr_innings
        self.printing = printing
        self.game_state = {}
        self.reset_game_state()

        self.prob_advance_runner_on_out = prob_advance_runner_on_out
        self.prob_double_play = prob_double_play

        self.prob_steal_2nd_base = prob_steal_2nd_base
        self.prob_steal_3rd_base = prob_steal_3rd_base
        self.prob_steal_home = prob_steal_home

        self.prob_1st_to_3rd = prob_1st_to_3rd
        self.prob_score_from_2nd_on_single = prob_score_from_2nd_on_single
        self.prob_score_from_1st_on_double = prob_score_from_1st_on_double


    def reset_game_state(self):
        self.game_state = {'score': 0, 'inning':    1,
                           'outs':  0, 'batter_up': 1,
                           # 'bases': [False, False, False]}
                           '1st_base': False,
                           '2nd_base': False,
                           '3rd_base': False}

    def reset_inning_state(self):
        self.game_state['1st_base'] = False
        self.game_state['2nd_base'] = False
        self.game_state['3rd_base '] = False
        self.game_state['outs'] = 0

    def play(self):
        if self.printing:
            self.print_lineup()
        for inning in range(self.nr_innings):
            if self.printing:
                print(f"\nInning {inning+1}")
            self.play_inning()
            self.game_state['inning'] += 1

    def play_inning(self):
        self.reset_inning_state()
        while self.game_state['outs'] < 3:
            self.steal()
            self.play_batter()
            self.double_play()
            self.next_batter()

    def play_batter(self):
        batter = self.lineup[self.game_state['batter_up']]
        if self.printing:
            print(f"Now up: {batter.name}")
        outcome = batter.swing()
        # options = ["strike-out", "in-play-out", "walk", "single", "double", "triple", "homerun"]
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
        if self.printing:
            print("Strike-out.")
        self.game_state['outs'] += 1

    def in_play_out(self):
        if self.printing:
            print("Ball in play, out.")
        self.game_state['outs'] += 1
        runners = [self.game_state['1st_base'], self.game_state['2nd_base'], self.game_state['3rd_base']].count(True)
        if runners > 0:
            coinflip = np.random.rand()
            if coinflip < self.prob_advance_runner_on_out:
                self.sac_fly_or_bunt()
            elif coinflip < self.prob_advance_runner_on_out + self.prob_double_play:
                self.double_play()

    def walk(self):
        if self.printing:
            print("Walk.")
        if self.game_state['1st_base'] and self.game_state['2nd_base'] and self.game_state['3rd_base']:
            self.game_state['score'] += 1
        elif self.game_state['1st_base'] and self.game_state['2nd_base'] and not self.game_state['3rd_base']:
            self.game_state['3rd_base'] = True
        elif self.game_state['1st_base'] and not self.game_state['2nd_base']:
            self.game_state['2nd_base'] = True
        elif not self.game_state['1st_base']:
            self.game_state['1st_base'] = True

    def single(self):
        if self.printing:
            print("Hits a single.")
        if self.game_state['1st_base'] and self.game_state['2nd_base'] and self.game_state['3rd_base']:
            # bases loaded
            self.game_state['score'] += 1
            if np.random.rand() < self.prob_score_from_2nd_on_single:
                self.game_state['score'] += 1
                self.game_state['3rd_base'] = False
                if np.random.rand() < self.prob_1st_to_3rd:
                    self.game_state['3rd_base'] = True
                    self.game_state['2nd_base'] = False
        elif self.game_state['1st_base'] and self.game_state['2nd_base'] and not self.game_state['3rd_base']:
            # 1st and 2nd
            self.game_state['3rd_base'] = True
            if np.random.rand() < self.prob_score_from_2nd_on_single:
                self.game_state['score'] += 1
                self.game_state['3rd_base'] = False
                if np.random.rand() < self.prob_1st_to_3rd:
                    self.game_state['3rd_base'] = True
                    self.game_state['2nd_base'] = False
        elif self.game_state['1st_base'] and not self.game_state['2nd_base'] and self.game_state['3rd_base']:
            # 1st and 3rd
            self.game_state['score'] += 1
            self.game_state['3rd_base'] = False
            self.game_state['2nd_base'] = True
            if np.random.rand() < self.prob_1st_to_3rd:
                self.game_state['3rd_base'] = True
                self.game_state['2nd_base'] = False
        elif self.game_state['1st_base'] and not self.game_state['2nd_base'] and not self.game_state['3rd_base']:
            # 1st only
            self.game_state['2nd_base'] = True
            if np.random.rand() < self.prob_1st_to_3rd:
                self.game_state['3rd_base'] = True
                self.game_state['2nd_base'] = False
        elif not self.game_state['1st_base'] and self.game_state['2nd_base'] and self.game_state['3rd_base']:
            # 2nd and 3rd
            self.game_state['1st_base'] = True
            self.game_state['score'] += 1
            self.game_state['2nd_base'] = False
            if np.random.rand() < self.prob_score_from_2nd_on_single:
                self.game_state['score'] += 1
                self.game_state['3rd_base'] = False
        elif not self.game_state['1st_base'] and self.game_state['2nd_base'] and not self.game_state['3rd_base']:
            # 2nd only
            self.game_state['1st_base'] = True
            self.game_state['2nd_base'] = False
            self.game_state['3rd_base'] = True
            if np.random.rand() < self.prob_score_from_2nd_on_single:
                self.game_state['score'] += 1
                self.game_state['3rd_base'] = False
        elif not self.game_state['1st_base'] and not self.game_state['2nd_base'] and self.game_state['3rd_base']:
            # 3rd only
            self.game_state['1st_base'] = True
            self.game_state['score'] += 1
            self.game_state['3rd_base'] = False
        else:
            # bases empty
            self.game_state['1st_base'] = True

    def double(self):
        if self.printing:
            print("Hits a double!")
        if self.game_state['1st_base'] and self.game_state['2nd_base'] and self.game_state['3rd_base']:
            # bases loaded
            self.game_state['score'] += 2
            self.game_state['1st_base'] = False
            if np.random.rand() < self.prob_score_from_1st_on_double:
                self.game_state['score'] += 1
                self.game_state['3rd_base'] = False
        elif self.game_state['1st_base'] and self.game_state['2nd_base'] and not self.game_state['3rd_base']:
            # 1st and 2nd
            self.game_state['1st_base'] = False
            self.game_state['3rd_base'] = True
            self.game_state['score'] += 1
            if np.random.rand() < self.prob_score_from_1st_on_double:
                self.game_state['score'] += 1
                self.game_state['3rd_base'] = False
        elif self.game_state['1st_base'] and not self.game_state['2nd_base'] and self.game_state['3rd_base']:
            # 1st and 3rd
            self.game_state['score'] += 1
            self.game_state['1st_base'] = False
            self.game_state['2nd_base'] = True
            if np.random.rand() < self.prob_score_from_1st_on_double:
                self.game_state['score'] += 1
                self.game_state['3rd_base'] = False
        elif self.game_state['1st_base'] and not self.game_state['2nd_base'] and not self.game_state['3rd_base']:
            # 1st only
            self.game_state['1st_base'] = False
            self.game_state['2nd_base'] = True
            self.game_state['3rd_base'] = True
            if np.random.rand() < self.prob_score_from_1st_on_double:
                self.game_state['score'] += 1
                self.game_state['3rd_base'] = False
        elif not self.game_state['1st_base'] and self.game_state['2nd_base'] and self.game_state['3rd_base']:
            # 2nd and 3rd
            self.game_state['score'] += 2
            self.game_state['3rd_base'] = False
        elif not self.game_state['1st_base'] and self.game_state['2nd_base'] and not self.game_state['3rd_base']:
            # 2nd only
            self.game_state['score'] += 1
        elif not self.game_state['1st_base'] and not self.game_state['2nd_base'] and self.game_state['3rd_base']:
            # 3rd only
            self.game_state['score'] += 1
            self.game_state['2nd_base'] = True
            self.game_state['3rd_base'] = False
        else:
            # bases empty
            self.game_state['2nd_base'] = True

    def triple(self):
        if self.printing:
            print("Hits a triple!")
        if self.game_state['1st_base'] and self.game_state['2nd_base'] and self.game_state['3rd_base']:
            # bases loaded
            self.game_state['score'] += 3
            self.game_state['1st_base'] = False
            self.game_state['2nd_base'] = False
        elif self.game_state['1st_base'] and self.game_state['2nd_base'] and not self.game_state['3rd_base']:
            # 1st and 2nd
            self.game_state['score'] += 2
            self.game_state['1st_base'] = False
            self.game_state['2nd_base'] = False
            self.game_state['3rd_base'] = True
        elif self.game_state['1st_base'] and not self.game_state['2nd_base'] and self.game_state['3rd_base']:
            # 1st and 3rd
            self.game_state['score'] += 2
            self.game_state['1st_base'] = False
        elif self.game_state['1st_base'] and not self.game_state['2nd_base'] and not self.game_state['3rd_base']:
            # 1st only
            self.game_state['score'] += 1
            self.game_state['1st_base'] = False
            self.game_state['3rd_base'] = True
        elif not self.game_state['1st_base'] and self.game_state['2nd_base'] and self.game_state['3rd_base']:
            # 2nd and 3rd
            self.game_state['score'] += 2
            self.game_state['2nd_base'] = False
        elif not self.game_state['1st_base'] and self.game_state['2nd_base'] and not self.game_state['3rd_base']:
            # 2nd only
            self.game_state['score'] += 1
            self.game_state['2nd_base'] = False
            self.game_state['3rd_base'] = True
        elif not self.game_state['1st_base'] and not self.game_state['2nd_base'] and self.game_state['3rd_base']:
            # 3rd only
            self.game_state['score'] += 1
        else:
            # bases empty
            self.game_state['3rd_base'] = True

    def homerun(self):
        if self.printing:
            print("Hits a home-run!")
        runners = [self.game_state['1st_base'], self.game_state['2nd_base'], self.game_state['3rd_base']].count(True)
        self.game_state['score'] += 1 + runners
        self.game_state['1st_base'] = False
        self.game_state['2nd_base'] = False
        self.game_state['3rd_base'] = False

    def steal(self):
        if self.game_state['1st_base'] and not self.game_state['2nd_base']:
            if np.random.rand() < self.prob_steal_2nd_base:
                self.game_state['2nd_base'] = True
                self.game_state['1st_base'] = False
                if self.printing:
                    print("Steal! Runner on 2nd base now.")
        if self.game_state['2nd_base'] and not self.game_state['3rd_base']:
            if np.random.rand() < self.prob_steal_3rd_base:
                if not self.game_state['1st_base']:
                    self.game_state['3rd_base'] = True
                    self.game_state['2nd_base'] = False
                    if self.printing:
                        print("Steal! Runner on 3rd base now.")
                else:
                    self.game_state['3rd_base'] = True
                    self.game_state['2nd_base'] = True
                    self.game_state['1st_base'] = False
                    if self.printing:
                        print("Double steal! Runners on 2nd and 3rd now.")
        if self.game_state['3rd_base']:
            if np.random.rand() < self.prob_steal_home:
                self.game_state['score'] += 1
                self.game_state['3rd_base'] = False
                if self.printing:
                    print("Steal home! Run scored!")

    def double_play(self):
        if self.game_state['outs'] < 3:
            self.game_state['outs'] += 1
            if self.printing:
                print("Double play!")
            if self.game_state['1st_base'] and self.game_state['2nd_base'] and self.game_state['3rd_base']:
                # bases loaded, dp over home and 1st
                self.game_state['1st_base'] = False
            elif self.game_state['1st_base'] and self.game_state['2nd_base'] and not self.game_state['3rd_base']:
                # 1st and 2nd, dp over 2nd and 1st
                self.game_state['1st_base'] = False
                self.game_state['2nd_base'] = False
                self.game_state['3rd_base'] = True
            elif self.game_state['1st_base'] and not self.game_state['2nd_base'] and self.game_state['3rd_base']:
                # 1st and 3rd, dp over 2nd and 1st
                if self.game_state['outs'] < 3:
                    self.game_state['score'] += 1
                self.game_state['1st_base'] = False
                self.game_state['3rd_base'] = False
            elif self.game_state['1st_base'] and not self.game_state['2nd_base'] and not self.game_state['3rd_base']:
                # 1st only, std dp
                self.game_state['1st_base'] = False
            elif not self.game_state['1st_base'] and self.game_state['2nd_base'] and self.game_state['3rd_base']:
                # 2nd and 3rd, sac fly out at home
                self.game_state['3rd_base'] = False
            elif not self.game_state['1st_base'] and self.game_state['2nd_base'] and not self.game_state['3rd_base']:
                # 2nd only, sac fly out at 3rd
                self.game_state['2nd_base'] = False
            elif not self.game_state['1st_base'] and not self.game_state['2nd_base'] and self.game_state['3rd_base']:
                # 3rd only, sac fly out at home
                self.game_state['3rd_base'] = False
            # else, bases empty, dp not possible

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


