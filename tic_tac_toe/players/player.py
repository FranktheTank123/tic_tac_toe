from __future__ import print_function, division
from abc import ABCMeta, abstractmethod
import numpy as np
import pdb

class Player(object):
    """Player interface."""
    __metaclass__ = ABCMeta

    def __init__(self,_id=None):
        self.id = _id
        self.total_wins = 0
        self.total_loses = 0
        self.total_ties = 0

    @abstractmethod
    def select_action(self, state, possible_actions):
        pass

    def update(self, reward):
        pass

    def close(self, game_reward, terminal_state):
        pass

class RandomPlayer(Player):
    """Random player who will randomly selection actions from all the possible actions."""

    def __str__(self):
        return "Random Player"

    def select_action(self, state, possible_actions):
        return np.random.choice(possible_actions)


class HumanPlayer(Player):
    """Human player who will always execute the optimal strategy."""
    def __str__(self):
        return "Human Player"

    def __init__(self, _id=None):
        super(self.__class__, self).__init__(_id)
        self.made_actions = []
        self.opponent_actions = []

        self.completes = ([0, 3, 6],
                         [1, 4, 7],
                         [2, 5, 8],
                         [0, 1, 2],
                         [3, 4, 5],
                         [6, 7, 8],
                         [0, 4, 8],
                         [2, 4, 6])

    def close(self, game_reward, terminal_state):
        self.made_actions = []
        self.opponent_actions = []

    def _get_winning_action(self, possible_actions):
        # Offensive play to win
        for complete in self.completes:
            if (len(set(complete) & set(self.made_actions)) == 2):
                winning_action = list(set(complete) - set(self.made_actions))[0]
                if winning_action in possible_actions:
                    return winning_action
        return None

    def _get_not_losing_action(self, possible_actions):
        # Defensive play to prevent lose
        for complete in self.completes:
            if (len(set(complete) & set(self.opponent_actions)) == 2):
                opponent_winning_action = list(set(complete) - set(self.opponent_actions))[0]
                if opponent_winning_action in possible_actions:
                    return opponent_winning_action
        return None

    def _get_optimal_action(self, possible_actions):
        # if nothing is directly related to win/lose, go with rank order:

        center = set([4])
        corners = set([0, 2, 6, 8])
        sides = set([1, 3, 5, 7])

        best_choice = list(center & set(possible_actions))
        good_choice = list(corners & set(possible_actions))
        okay_choice = list(sides & set(possible_actions))

        if len(best_choice):
            return np.random.choice(best_choice)
        elif len(good_choice):
            return np.random.choice(good_choice)
        else:
            return np.random.choice(okay_choice)

    def select_action(self, state, possible_actions):
        self.opponent_actions = list(set(range(9)) - set(possible_actions) - set(self.made_actions))

        action = self._get_winning_action(possible_actions)

        if action is None:
            action = self._get_not_losing_action(possible_actions)

        if action is None:
            action = self._get_optimal_action(possible_actions)

        self.made_actions.append(action)

        return action


class QPlayer(Player):

    def __str__(self):
        return "Q Player"

    def __init__(self, _id=None, Qmap={}, game_played=0, gamma=0.9, alpha=0.3, epsilon=0.1):
        super(self.__class__, self).__init__(_id)
        self.prev_state = None
        self.prev_action = None
        self.prev_possible_actions = []

        self.state = None
        self.action = None
        self.reward = 0
        self.gamma = gamma
        self.alpha = alpha
        self.epsilon = epsilon
        self.Qmap = Qmap
        self.Qinit = 0.8
        self.game_played = game_played

    def _getQ(self, state, action):
        if (state, action) not in self.Qmap:
            self.Qmap[(state, action)] = self.Qinit
        return self.Qmap[(state, action)]

    def _explore_and_exploit(self, state, possible_actions):
        # Explore
        if np.random.rand() < self.epsilon/(self.game_played+1):
            return np.random.choice(possible_actions)

        # Exploit
        Q_list = [self._getQ(state, a) for a in possible_actions]

        return possible_actions[np.argmax(Q_list)]

    def _updateQ(self, prev_state, prev_action, curr_state, possible_actions, reward):
        maxQ = np.max([self._getQ(curr_state, _action) for _action in possible_actions])

        self._getQ(prev_state, prev_action)
        self.Qmap[(prev_state, prev_action)] += self.alpha * (reward + self.gamma * maxQ - self.Qmap[(prev_state, prev_action)])

    def select_action(self, state, possible_actions):
        if self.prev_state is not None:
            self._updateQ(prev_state=self.prev_state,
                          prev_action=self.prev_action,
                          curr_state=state,
                          possible_actions=possible_actions,
                          reward=self.reward)

        action = self._explore_and_exploit(state, possible_actions)

        self.prev_state = state
        self.prev_action = action
        return action

    def update(self, reward):
        self.reward = reward

    def close(self, game_reward, terminal_state):
        self.game_played += 1
        self.Qmap[(terminal_state, None)] = 0
        self._updateQ(prev_state=self.prev_state,
                      prev_action=self.prev_action,
                      curr_state=terminal_state,
                      possible_actions=[None],
                      reward=game_reward)



