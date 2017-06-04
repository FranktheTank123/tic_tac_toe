from __future__ import print_function, division
import numpy as np
import pdb

def updateQ(Q, S, A, S_1, a, gamma, alpha, R, default_val):
    maxQ = np.max([Q.get((S_1,_a),default_val) for _a in a])
    Q[(S,A)] += alpha*(R+gamma*maxQ-Q[(S,A)])
    return Q

class TwoPlayerGame(object):
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        if self.player1.id is None:
            self.player1.id = 'X'
        if self.player2.id is None:
            self.player2.id = 'O'
        self.init_state()
        self.active_player = None
        self.inactive_player = None
        self.select_active_player()
        self.winner_reward = 1
        self.loser_reward = -1
        self.tie_reward = 0
        self.game_history = []
    
    ###############################################################
    ############## NEED TO UPDATE THESE METHODS ###################
    ###############################################################
    def init_state(self):
        self.state = {'board': None}
    
    def get_possible_actions(self):
        # Given State and Turn
        return []

    def get_new_state(self, action):
        new_state = None
        reward_active, reward_inactive = 0, 0
        return new_state, reward_active, reward_inactive

    def is_state_terminal(self):
        return True

    ###############################################################
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

        active_player = self.active_player
        inactive_player = self.inactive_player
        
        # Ask Player to Make a move
        possible_actions = self.get_possible_actions()

        action = active_player.select_action(self.state_id, possible_actions)
        new_state, reward_active, reward_inactive = self.get_new_state(action)

        # Give reward to player
        active_player.update(reward_active)
        inactive_player.update(reward_inactive)
        self.state = new_state

    def play_one_game(self):
        self.game_history = []
        self.init_state()
        self.active_player = None
        self.select_active_player() # this is a place holder for `is_state_terminal` to check

        while (not self.is_state_terminal()) and len(self.get_possible_actions()):
            self.play_turn()
            self.game_history.append(self.state['board'])

        if self.is_state_terminal():
            self.active_player.close(self.winner_reward, self.state_id)
            self.inactive_player.close(self.loser_reward, self.state_id)
            return self.active_player.id

        else:
            self.active_player.close(self.tie_reward, self.state_id)
            self.inactive_player.close(self.tie_reward, self.state_id)
            return None
        
class ClassicTicTacToe(TwoPlayerGame):
    
    def init_state(self):
        self.state = {'board':tuple(' '*9)}
    
    def get_possible_actions(self):
        board = self.state['board']
        return [i for i in range(0,9) if board[i] == ' ']
    
    def get_new_state(self, action):
        new_state = self.state # new_state to be updated
        lst = list(new_state['board'])
        lst[action] = self.active_player.id
        new_state['board'] = tuple(lst)

        reward_active, reward_inactive = 0, 0
        return new_state, reward_active, reward_inactive

    def is_state_terminal(self):
        board = self.state['board']
        char = self.active_player.id
        for a,b,c in [(0,1,2), (3,4,5), (6,7,8),
                      (0,3,6), (1,4,7), (2,5,8),
                      (0,4,8), (2,4,6)]:
            if char == board[a] == board[b] == board[c]:
                return True
        return False

    def visualize_game_history(self):
        for board in self.game_history:
            print("\n")
            print("".join(board[0:3]))
            print("".join(board[3:6]))
            print("".join(board[6:9]))



class Player(object):
    """Abstract interface for Player."""
    def __init__(self,_id=None):
        self.id = _id
    
    def select_action(self, state, possible_actions):
        raise ValueError("Please implement the select_action method.")
    
    def update(self, reward):
        pass
    
    def close(self, game_reward, terminal_state):
        pass


class QPlayer(Player):
    def __init__(self, _id=None, gamma=0.9, alpha=0.3, epsilon=0.1):
        self.id = _id
        self.prev_state = None
        self.prev_action = None
        self.prev_possible_actions = []
        
        self.state = None
        self.action = None
        self.reward = None
        self.gamma = gamma
        self.alpha = alpha
        self.epsilon = epsilon
        self.Qmap = {}
        self.Qinit = 0.8

    def getQ(self, state, action):        
        if (state,action) not in self.Qmap:
            self.Qmap[(state,action)] = self.Qinit
        return self.Qmap[(state,action)]
            
    def select_action(self, state, possible_actions):
        if self.prev_state is not None:
            self.Qmap = updateQ(Q=self.Qmap, 
                               S=self.prev_state,
                               A=self.prev_action,
                               S_1=state,
                               a=possible_actions,
                               gamma=self.gamma,
                               alpha=self.alpha,
                               R=self.reward,
                               default_val=self.Qinit)
        # Explore
        if np.random.rand() < self.epsilon:
            return np.random.choice(possible_actions)
        # Exploit
        Q_list = [self.getQ(state, a) for a in possible_actions]
        
        action_idx = np.argmax(Q_list)
        action = possible_actions[action_idx]
        self.prev_state = state
        self.prev_action = action
        return action

    def update(self, reward):
        self.reward = reward

    def close(self, game_reward, terminal_state):
        self.Qmap[(terminal_state,None)] = 0
        self.Qmap = updateQ(Q=self.Qmap, 
                            S=self.prev_state,
                            A=self.prev_action,
                            S_1=terminal_state,
                            a=[None],
                            gamma=self.gamma,
                            alpha=self.alpha,
                            R=game_reward,
                            default_val=self.Qinit)

class RandomPlayer(Player):
    """Random player who will randomly selection actions from all the possible actions."""
    def select_action(self, state, possible_actions):
        return np.random.choice(possible_actions)
    

class CommonPlayer(Player):
    def __init__(self,_id=None):
        self.id = _id
        self.aiturn = 0
        self.made_actions = []
       
    def close(self, game_reward, terminal_state):
        self.aiturn = 0
        self.made_actions = []
    
    def select_action(self, state, possible_actions):
        self.aiturn += 1
        aiturn = self.aiturn
        impossible_actions = list(set(range(9)) - set(possible_actions))
        opponent_actions = list(set(impossible_actions) - set(self.made_actions))
        
        center = set([4])
        corners = set([0, 2, 6, 8])
        sides = set([1, 3, 5, 7])
        best_choice =  list(center & set(possible_actions))
        good_choice =  list(corners & set(possible_actions))
        okay_choice =  list(sides & set(possible_actions))


        action = None
        completes = ([0, 3, 6],
                     [1, 4, 7],
                     [2, 5, 8],
                     [0, 1, 2],
                     [3, 4, 5],
                     [6, 7, 8],
                     [0, 4, 8],
                     [2, 4, 6])

        # Offensive play to win
        for one_possible_complete in completes: 
                if (len(set(one_possible_complete) & set(self.made_actions)) == 2):
                    winning_action = list(set(one_possible_complete) - set(self.made_actions))[0]
                    if winning_action in possible_actions:
                        action = winning_action
                
        # Defensive play to prevent lose
        if action is None:
            for one_possible_complete in completes:
                if (len(set(one_possible_complete) & set(opponent_actions)) == 2):
                    opponent_winning_action = list(set(one_possible_complete) - set(opponent_actions))[0]
                    if opponent_winning_action in possible_actions:
                        action = opponent_winning_action

        # if nothing is directly related to win/lose, go with rank order:
        if action is None:
            if len(best_choice):
                action = np.random.choice(best_choice)
            elif len(good_choice):
                action = np.random.choice(good_choice)
            else:
                action = np.random.choice(okay_choice)


        self.made_actions.append(action)
        return action


if __name__ == '__main__':
    # pdb.set_trace() 
    pX = CommonPlayer('Q')
    #pO = QPlayer('Q')
    pO = CommonPlayer('C')
    rand_wins = 0
    qbot_wins = 0
    common_wins = 0
    g = ClassicTicTacToe(pX,pO)
    for i in range(5):

        winner = g.play_one_game().__str__()[0]
        if winner == 'Q':
            qbot_wins += 1
        elif winner == 'C':
            common_wins += 1
        if i % 5000 == 0:
            print ('Game {0} won by {1}\t Q-Bot Wins:{2} \t Common Wins:{3}'.format(i+1, winner, qbot_wins, common_wins))