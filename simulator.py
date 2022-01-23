"""
Python script to simulate the offense side of a baseball game,
such that we can compare different lineup possibilities.

by Bram Grooten
"""
from batter import Batter
from baseball import Game
import pandas as pd
import numpy as np
import plotille


def setup():
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
    return lineup


def play_many_games(lineup, nr_games=10_000):
    game = Game(lineup, printing=False)
    game.print_lineup()
    scores = []
    for game_idx in range(nr_games):
        game.reset_game_state()
        game.play()
        scores.append(game.get_score())
        if (game_idx + 1) % 1000 == 0:
            print(f"Played {game_idx+1} games")

    print(f"\nAfter {nr_games} games we have:")
    print(f"avg score: \t{np.mean(scores)}")
    print(f"median: \t{np.median(scores)}")
    print(f"std dev: \t{np.std(scores):.2f}")
    print(plotille.hist(scores, bins=int(np.max(scores)), width=50))


def play_one_game(lineup):
    game = Game(lineup, printing=True)
    game.print_lineup()
    game.reset_game_state()
    game.play()
    score = game.get_score()
    if score == 1:
        print(f"\nThe final score is: 1 run.\n")
    else:
        print(f"\nThe final score is: {score} runs.\n")


if __name__ == '__main__':
    lineup = setup()

    play_many_games(lineup, nr_games=10_000)
    # play_one_game(lineup)

