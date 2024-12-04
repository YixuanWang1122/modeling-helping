# ALL STATES ARE TUPLE FORM
# must be unpacked in farmgame.py for object level methods

# imports
from random import randint
import numpy as np
import random
import datetime # for limiting calculation to wall clock time
from math import log, sqrt
import copy
import shortuuid
try:
    from utils import *
except:
    from modeling.utils import *
# from farmgame import getstatefromhash
# import shelve

# # import state hash dictionary
# # print(hash(tuple(self)))
# def getstatefromhash(shash):
#     with shelve.open('farmstatehash') as shelf:
#         # tupstate = shelf[shash]
#         state = shelf[str(shash)]
#     return state

class MCTS(object):
    
    def __init__(self, **kwargs):
        self.id = shortuuid.uuid()
        self.states = []
        self.tupstates = []
        self.shashes = []
        self.identity = kwargs.get('color','red')
        self.agent_type="mcts"
        self.policy = kwargs.get('policy',"selfish") # altruistic, or collaborative
        seconds = kwargs.get('time',5) # default 5s of simulations
        self.calculation_time = datetime.timedelta(seconds=seconds)
        self.nsims=kwargs.get('nsims',1000000) # will stop when first of the two (calc time and nsims) is reached
        self.max_moves = kwargs.get('max_moves')
        self.C = kwargs.get('C', 100)
        self.verbose = kwargs.get('verbose',False) 
        self.rewards = {}
        self.plays = {}
        self.farmstatehash = {}
        self.agent_information = {"color":self.identity, "agent_type":self.agent_type,"time":self.calculation_time,"max_moves":self.max_moves,"C":self.C}
        self.max_moves = 100

    def get_reward(self, state, player_color):
        """
        Compute the reward for the given player in the given state.
        """
        return state.reward(player_color)  # Uses the reward method from Farm

        
    # Take a game state and append it to the history
    def update(self,state):
        self.states.append(state)
        self.tupstates.append(tuple(state))
        
    # calculates best move and returns it
    def choose_action(self):
        self.max_depth = 0
        state = self.states[-1]
        player = self.identity
        legal = state.legal_actions()

        if not legal:
            print("No legal actions available!")
            return None
        if len(legal) == 1:
            return legal[0]

        games = 0
        begin = datetime.datetime.utcnow()

        while (datetime.datetime.utcnow() - begin) < self.calculation_time and games < self.nsims:
            self.run_simulation()
            games += 1

        moves_states = [(action, self.hash_and_store(state.take_action(action, inplace=False))) for action in legal]

        log_total = log(sum(self.plays.get((player, S), 0) for _, S in moves_states) + 1)

        competitors = [
            ((self.rewards.get((player, shash), 0) / self.plays.get((player, shash), 1)) +
            self.C * sqrt(log_total / self.plays.get((player, shash), 1)),
            action, shash)
            for action, shash in moves_states
            if (player, shash) in self.plays
        ]

        if competitors:
            # Ensure `best_action` is the Action object, not its ID
            value, best_action, shash = max(competitors, key=lambda x: x[0])
        else:
            # Fallback to a random action
            best_action, shash = random.choice(moves_states)
            value = 0  # Default value for unexplored actions

        print(f"Best Action: {best_action}, Percent Wins: {value}")
        return best_action



#     # this don't do anything yet
#     def print_tree(self):
#         board = self.game.tamagotchi_game
#         pass
    
    # play out a "random" game from the current position, then update stats with result
#     def run_simulation(self):
#         plays, rewards = self.plays, self.rewards
        
#         visited_qs = set()
#         states_copy = copy.deepcopy(self.states[:])
#         simstate = states_copy[-1]
#         player = simstate.players[simstate.turn]["name"] #self.identity #self.game.current_player_color(state)
        
#         expand = True # you only expand once #YOEO
#         for t in range(self.max_moves):
#             legal = simstate.legal_actions() #self.game.legal_actions(states_copy) # get valid actions
 
#             moves_states = [(a['id'], self.hash_and_store(simstate.take_action(a,inplace=False))) for a in legal]

#             if all(plays.get((player, S)) for a, S in iter(moves_states)):
#                 # if we have statistics on all legal moves, use them.
#                 # upper confidence bound (UCB) algorithm
# #                 print("UCB choice")
#                 log_total = log(
#                     sum(plays[(player, S)] for a, S in moves_states)
#                 )
#                 # list of value, action, shash tuples
#                 competitors = [((rewards[(player, S)] / plays[(player, S)]) +
#                     self.C * sqrt(log_total / plays[(player, S)]), a, S)
#                     for a, S in moves_states]
#                 highestval = max(competitors, key=lambda x: x[0])[0]
#                 # there could be equivalent actions (multiple maxima) so let us choose between those
#                 finalists = [x for x in competitors if x[0]==highestval]
#                 value, action, shash = random.choice(finalists)
#                 # # value of best
#                 # value, action, shash = max(
#                 #     (((rewards[(player, S)] / plays[(player, S)]) +
#                 #     self.C * sqrt(log_total / plays[(player, S)]), a, S)
#                 #     for a, S in moves_states),
#                 #     key = lambda x: x[0]
#                 # )
#             else:
#                 # if we don't have stats on all legal moves, randomly pick one
# #                 print("Random choice") (TODO: smarter default choice algo)
#                 action, shash = random.choice(moves_states)
#                 # # NEW let's have default policy be colorblind nearestneighbor
#                 # myplayer = simstate.players[simstate.turn]
#                 # sorted_legal = sorted(legal, key=lambda x: getManhattanDistance(myplayer,x))
#                 # # after sorting, first object is always pillow
#                 # chosen_legal = sorted_legal[1] # pick nearest object that is not the self lol 
#                 # action, shash = (chosen_legal['id'], self.hash_and_store(simstate.take_action(chosen_legal,inplace=False)))
                    

#             # NEXT STATE from selected action
#             simstate = self.get_state(shash)
#             states_copy.append(simstate) # record

#             # if we are in the expand phase and this is a new state-action pair
#             if expand and (player, self.hash_and_store(simstate)) not in plays: 
#                 expand = False # you only expand once so this is it
#                 plays[(player, self.hash_and_store(simstate))] = 0 # initialize
#                 rewards[(player, self.hash_and_store(simstate))] = 0
#                 if t > self.max_depth:
#                     self.max_depth = t
                    
#             visited_qs.add((player, self.hash_and_store(simstate))) # add this state as visited
            
#             # update the player
#             player = simstate.players[simstate.turn]["name"]
#             red_rwd, red_done = simstate.reward("red")
#             purple_rwd, purple_done = simstate.reward("purple")
#             done = red_done and purple_done
            
#             if done: 
#                 # print("finished a game")
#                 # print("red reward ",red_rwd)
#                 # print("purple reward ",purple_rwd)
#                 break
        
#         # print(visited_states, reward)
#         for player, q in visited_qs: # for each visited state
#             if (player, q) not in plays: # if we don't have stats on this state yet
#                 continue
#             self.plays[(player, q)]+=1 # increase plays

#             # the reward you consider depends on your reward policy - selfish, altruistic, or collaborative
#             # are you trying to maximize your own rwd, your partner's reward, or both?
#             if self.policy=="selfish": # IMPORTANT right now this assumes both players have selfish policy 
#                 if player=="red":
#                     self.rewards[(player, q)]+=red_rwd # add up the reward you got
#                 else:
#                     self.rewards[(player, q)]+=purple_rwd
#             elif self.policy=="altruistic":
#                 if player=="red":
#                     self.rewards[(player, q)]+=purple_rwd # add up the reward you got
#                 else:
#                     self.rewards[(player, q)]+=red_rwd
#             elif self.policy=="collaborative":
#                 self.rewards[(player, q)]+= red_rwd + purple_rwd # add up the reward you got

#             # everyone gets punished for slowness regardless of reward policy
#             # punish these bots for taking too long thoooooo
#             self.rewards[(player,q)]-= simstate.trial # TEMPORAL COST - THIS PENALTY MAY NEED TO BE TUNED

    def run_simulation(self):
        plays, rewards = self.plays, self.rewards

        visited_qs = set()
        states_copy = copy.deepcopy(self.states[:])
        simstate = states_copy[-1]
        player = simstate.players[simstate.turn]["name"]  # Current player color

        expand = True
        for t in range(self.max_moves):
            legal = simstate.legal_actions()  # Get valid actions
            moves_states = [(a.id, self.hash_and_store(simstate.take_action(a, inplace=False))) for a in legal]

            if all(plays.get((player, S), 0) for a, S in iter(moves_states)):
                # Upper Confidence Bound (UCB) algorithm
                log_total = log(
                    sum(plays.get((player, S), 0) for a, S in moves_states)
                )
                competitors = [
                    ((rewards.get((player, S), 0) / plays.get((player, S), 1)) +
                    self.C * sqrt(log_total / plays.get((player, S), 1)), a.id, S)
                    for a, S in moves_states
                ]
                value, action_id, shash = max(competitors, key=lambda x: x[0])
            else:
                # Random action if no stats exist
                action_id, shash = random.choice(moves_states)

            # Advance state
            simstate = self.get_state(shash)
            states_copy.append(simstate)

            # Expand tree for new state-action pairs
            if expand and (player, shash) not in plays:
                expand = False
                plays[(player, shash)] = 0
                rewards[(player, shash)] = 0

            visited_qs.add((player, shash))
            player = simstate.players[simstate.turn]["name"]

            # Check for game end
            if simstate.is_done():
                break

        for player, q in visited_qs:
            plays[(player, q)] = plays.get((player, q), 0) + 1
            rewards[(player, q)] = rewards.get((player, q), 0) + self.get_reward(simstate, player)


    # here, we use string representation of hash rather than int that hash() itself gives
    def hash_and_store(self, s):
        h = str(hash(s))  # Convert hash to string
        self.farmstatehash[h] = s
        return h


    def get_state(self, h):
        return self.farmstatehash[h]
