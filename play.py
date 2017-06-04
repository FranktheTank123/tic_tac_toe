from __future__ import print_function, division
from tic_tac_toe.games.games import ClassicTicTacToe
from tic_tac_toe.players.player import HumanPlayer, QPlayer, RandomPlayer
import sys
from tqdm import tqdm


def play_one_game_and_summarize(g, p1, p2):
    g.play_one_game()
    if g.winner == p1.id:
        p1.total_wins += 1
        p2.total_loses += 1
    elif g.winner == p2.id:
        p1.total_loses += 1
        p2.total_wins += 1
    else:
        p1.total_ties += 1
        p2.total_ties += 1

def main(config):
    num_games = config['num_games']
    print("Number of games are set to be {}.".format(num_games))

    p1 = config['p1']
    p2 = config['p2']
    g = ClassicTicTacToe(p1, p2)

    [play_one_game_and_summarize(g, p1, p2) for i in tqdm(range(num_games))]

    print ('{} games played. {} wins: {}, {} wins: {}, total ties: {}'.format(num_games, p1, p1.total_wins, p2, p2.total_wins, p1.total_ties))

if __name__ == '__main__':
    try:
        num_games = int(sys.argv[1])
    except:
        num_games = 100

    config={
        'p1': QPlayer(),
        'p2': HumanPlayer(),
        'num_games': num_games
    }

    main(config)