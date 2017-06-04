from __future__ import print_function, division
from tic_tac_toe.games.games import ClassicTicTacToe
from tic_tac_toe.players.player import HumanPlayer, QPlayer, RandomPlayer
import sys
from tqdm import tqdm
import pdb

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

    # first we let 2 Q players to play against each other to learn
    print("Number of games are set to be {}.".format(num_games))
    p1 = config['p1']
    p2 = config['p2']
    g = ClassicTicTacToe(p1, p2)

    [play_one_game_and_summarize(g, p1, p2) for i in tqdm(range(num_games))]

    print ('{} games played. {} win-rate: {:.2%}, {} win-rate: {:.2%}, tie-rate: {:.2%}'.format(num_games, p1,
                                                                                                p1.total_wins/num_games,
                                                                                                p2, p2.total_wins/num_games,
                                                                                                p1.total_ties/num_games))
    # then we let one of the trained Q players to play against human.
    print('Now, we let Q player to play against Human')
    p1.total_wins = 0
    p3 = config['p3']
    g2 = ClassicTicTacToe(p1, p3)
    [play_one_game_and_summarize(g2, p1, p3) for i in tqdm(range(num_games))]
    print('{} games played. {} win-rate: {:.2%}, {} win-rate: {:.2%}, tie-rate: {:.2%}'.format(num_games, p1,
                                                                                               p1.total_wins / num_games,
                                                                                               p3,
                                                                                               p3.total_wins / num_games,
                                                                                               p3.total_ties / num_games))

if __name__ == '__main__':
    try:
        num_games = int(sys.argv[1])
    except:
        num_games = 100

    config={
        'p1': QPlayer("Q1"),
        'p2': QPlayer("Q2"),
        'p3': HumanPlayer("H"),
        # 'p2': RandomPlayer("R"),
        'num_games': num_games
    }

    main(config)