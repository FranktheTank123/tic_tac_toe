from __future__ import print_function, division
from abc import ABCMeta, abstractmethod
import numpy as np


class TwoPlayerGame(object):
    """Two player games interface."""
    __metaclass__ = ABCMeta

    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        if self.player1.id is None:
            self.player1.id = "X"
        if self.player2.id is None:
            self.player2.id = "O"

        self.active_player = None

        self.winner_reward = 1
        self.loser_reward = -1
        self.tie_reward = 0

        self.game_history = []
        self.state = {'board': None}
        self.winner = None

    @abstractmethod
    def init_state(self):
        pass

    @abstractmethod
    def get_possible_actions(self):
        """Return a list/set."""
        pass

    @abstractmethod
    def get_new_state(self, action):
        """Return new_state."""
        pass

    @abstractmethod
    def get_rewards_from_state(self, state):
        """Return reward_active, reward_inactive"""
        pass

    @abstractmethod
    def is_state_terminal(self):
        """Return True/False."""
        pass


    @property
    def state_id(self):
        return hash(frozenset(self.state.items()))

    def select_active_player(self):
        """Rotate positions."""
        if self.active_player is None:
            self.active_player, self.inactive_player = np.random.choice([self.player1, self.player2], 2, replace=False)
        self.active_player, self.inactive_player = self.inactive_player, self.active_player

    def play_turn(self):
        self.select_active_player()

        # Ask Player to Make a move
        possible_actions = self.get_possible_actions()

        action = self.active_player.select_action(self.state_id, possible_actions)
        self.state = self.get_new_state(action)
        reward_active, reward_inactive = self.get_rewards_from_state(self.state)

        # Give reward to player
        self.active_player.update(reward_active)
        self.inactive_player.update(reward_inactive)

    def play_one_game(self):
        self.init_state()
        self.select_active_player()  # this is a place holder for `is_state_terminal` to check

        while (not self.is_state_terminal()) and len(self.get_possible_actions()):
            self.play_turn()
            self.game_history.append(self.state['board'])

        if self.is_state_terminal():
            self.active_player.close(self.winner_reward, self.state_id)
            self.inactive_player.close(self.loser_reward, self.state_id)
            self.winner = self.active_player.id

        else:
            self.active_player.close(self.tie_reward, self.state_id)
            self.inactive_player.close(self.tie_reward, self.state_id)
            self.winner = None

class ClassicTicTacToe(TwoPlayerGame):
    """Classic Tic-Tac-Toe."""

    def __init__(self, player1, player2):
        super(self.__class__, self).__init__(player1, player2)

        self.terminal_condition = [(0, 1, 2),
                                   (3, 4, 5),
                                   (6, 7, 8),
                                   (0, 3, 6),
                                   (1, 4, 7),
                                   (2, 5, 8),
                                   (0, 4, 8),
                                   (2, 4, 6)]

    def init_state(self):
        self.state = {'board': tuple(' ' * 9)}

    def get_possible_actions(self):
        return [i for i in range(0, 9) if self.state['board'][i] == ' ']

    def get_new_state(self, action):
        new_state = self.state  # new_state to be updated
        lst = list(new_state['board'])
        lst[action] = self.active_player.id
        new_state['board'] = tuple(lst)
        return new_state

    def get_rewards_from_state(self, state):
        reward_active, reward_inactive = 0, 0
        return reward_active, reward_inactive


    def is_state_terminal(self):
        board = self.state['board']
        char = self.active_player.id
        for a, b, c in self.terminal_condition:
            if char == board[a] == board[b] == board[c]:
                return True
        return False

    def visualize_game_history(self, last=5):
        if len(self.game_history) > last:
            game_history = self.game_history[-5:]
        else:
            game_history = self.game_history

        for board in game_history:
            print("\n")
            print("\t".join(board[0:3]))
            print("\t".join(board[3:6]))
            print("\t".join(board[6:9]))
