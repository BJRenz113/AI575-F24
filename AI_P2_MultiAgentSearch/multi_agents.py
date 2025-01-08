"""
multiAgents.py
--------------
Licensing Information:  You are free to use or extend these projects for
educational purposes provided that (1) you do not distribute or publish
solutions, (2) you retain this notice, and (3) you provide clear
attribution to UC Berkeley, including a link to http://ai.berkeley.edu.

Attribution Information: The Pacman AI projects were developed at UC Berkeley.
The core projects and autograders were primarily created by John DeNero
(denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
Student side autograding was added by Brad Miller, Nick Hay, and
Pieter Abbeel (pabbeel@cs.berkeley.edu).
"""
import math
import random
import util

from util import manhattan_distance
from game import Agent, Directions


class ReflexAgent(Agent):
    """
      A reflex agent chooses an action at each choice point by examining
      its alternatives via a state evaluation function.

      The code below is provided as a guide.  You are welcome to change
      it in any way you see fit, so long as you don't touch our method
      headers.
    """

    def get_action(self, game_state):
        """
        You do not need to change this method, but you're welcome to.

        get_action chooses among the best options according to the evaluation function.

        Just like in the previous project, get_action takes a GameState and returns
        some Directions.X for some X in the set {North, South, West, East, Stop}
        """
        # Collect legal moves and successor states
        legal_moves = game_state.get_legal_actions()

        # Choose one of the best actions
        scores = [self.evaluation_function(game_state, action) for action in legal_moves]
        best_score = max(scores)
        best_indices = [index for index in range(len(scores)) if scores[index] == best_score]
        chosen_index = random.choice(best_indices)  # Pick randomly among the best

        # Add more of your code here if you want to

        return legal_moves[chosen_index]

    def evaluation_function(self, current_game_state, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (new_food) and Pacman position after moving (new_pos).
        new_scared_times holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """

        # Useful information you can extract from a GameState (pacman.py)
        successor_game_state = current_game_state.generate_pacman_successor(action)
        new_pos = successor_game_state.get_pacman_position()
        new_food = successor_game_state.get_food()
        new_ghost_states = successor_game_state.get_ghost_states()
        new_scared_times = [ghost_state.scared_timer for ghost_state in new_ghost_states]
        score = successor_game_state.get_score()

        # *** YOUR CODE HERE ***
        food = new_food.as_list()

        if food: #nearest food to pacman
            closest_food = min([manhattan_distance(new_pos, fooditem) for fooditem in food])
            score += 1.0 /closest_food

        for ghost, scared_time in zip(new_ghost_states, new_scared_times): #nearest ghost to pacman
            ghost_position = ghost.get_position()
            ghost_distance = manhattan_distance(new_pos, ghost_position)

            if scared_time <= 0: #being near dangerous ghosts=bad
                if ghost_distance < 2:
                    score -= 1000
            else: #being near killable ghosts = good
                score += 200/(ghost_distance +1)

        score -=len(food) * 10
        return score


def score_evaluation_function(current_game_state):
    """
      This default evaluation function just returns the score of the state.
      The score is the same one displayed in the Pacman GUI.

      This evaluation function is meant for use with adversarial search agents
      (not reflex agents).
    """
    return current_game_state.get_score()


class MultiAgentSearchAgent(Agent):
    """
      This class provides some common elements to all of your
      multi-agent searchers.  Any methods defined here will be available
      to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

      You *do not* need to make any changes here, but you can if you want to
      add functionality to all your adversarial search agents.  Please do not
      remove anything, however.

      Note: this is an abstract class: one that should not be instantiated.  It's
      only partially specified, and designed to be extended.  Agent (game.py)
      is another abstract class.
    """

    def __init__(self, eval_fn='score_evaluation_function', depth='2'):
        super().__init__()
        self.index = 0  # Pacman is always agent index 0
        self.evaluation_function = util.lookup(eval_fn, globals())
        self.depth = int(depth)


class MinimaxAgent(MultiAgentSearchAgent):
    """
      Your minimax agent (question 2)
    """

    def get_action(self, game_state):
        """
          Returns the minimax action from the current game_state using self.depth
          and self.evaluation_function.

          Here are some method calls that might be useful when implementing minimax.

          game_state.get_legal_actions(agent_index):
            Returns a list of legal actions for an agent
            agent_index=0 means Pacman, ghosts are >= 1

          game_state.generate_successor(agent_index, action):
            Returns the successor game state after an agent takes an action

          game_state.get_num_agents():
            Returns the total number of agents in the game
        """

        # *** YOUR CODE HERE ***#

        def max_val(index, depth, state):
            current_action = None
            current_value = -math.inf

            for action in state.get_legal_actions(index):
                next_state = state.generate_successor(index, action)
                miniValue = minimax(1, depth, next_state)
                if miniValue > current_value:
                    current_value = miniValue
                    current_action = action
            if depth == self.depth: #return best action
                return current_action
            else:
                return current_value

        def min_val(index, depth, state):
            current_value = math.inf
            next_index = (index +1) % game_state.get_num_agents()

            next_depth = depth
            if next_index ==0: #updating based on agent
                next_depth = depth-1
            for action in state.get_legal_actions(index):
                next_state = state.generate_successor(index, action)
                miniValue = minimax(next_index, next_depth, next_state)
                current_value = min(current_value, miniValue)
            return current_value

        def minimax(index, depth, state):
            if depth == 0 or state.is_lose() or state.is_win():
                return self.evaluation_function(state) #easy out cases
            if index !=0: #agent != pacman
                return min_val(index, depth, state)
            else:
                return max_val(index, depth, state)
        return minimax(0, self.depth, game_state) #final


class AlphaBetaAgent(MultiAgentSearchAgent):
    """
      Your minimax agent with alpha-beta pruning (question 3)
    """

    def get_action(self, game_state):
        """
          Returns the minimax action using self.depth and self.evaluation_function
        """

        # *** YOUR CODE HERE ***
        alpha = -math.inf
        beta = math.inf
        current_action = None

        for action in game_state.get_legal_actions(0):
            next_state = game_state.generate_successor(0, action)
            score = self.min_value(next_state, 1, 0, alpha, beta)
            if score > alpha:
                alpha = score
                current_action = action
        return current_action


    def max_value(self, state, index, depth, alpha, beta):
        if state.is_win() or state.is_lose() or depth == self.depth:
            return self.evaluation_function(state) #easy outs

        maxScore = -math.inf

        for action in state.get_legal_actions(index):
            next_state = state.generate_successor(index,action)
            score = self.min_value(next_state, index+1 , depth, alpha, beta) #(index+1)%state.get_num_agents()
            maxScore = max(maxScore, score)

            if maxScore > beta:
                return maxScore
            alpha = max(alpha, maxScore)
        return maxScore



    def min_value(self, state, index, depth, alpha, beta):
        if state.is_win() or state.is_lose() or depth == self.depth:
            return self.evaluation_function(state)  # easy outs

        minScore = math.inf

        for action in state.get_legal_actions(index):
            next_state = state.generate_successor(index, action)
            if index == (state.get_num_agents() -1):
                score = self.max_value(next_state, 0, depth+1, alpha, beta)
            else:
                score = self.min_value(next_state, index+1, depth, alpha, beta )

            minScore = min(minScore, score)
            if minScore < alpha:
                return minScore
            beta = min(beta, minScore)
        return minScore


class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def get_action(self, game_state):
        """
          Returns the expectimax action using self.depth and self.evaluation_function

          All ghosts should be modeled as choosing uniformly at random from their
          legal moves.
        """
        # *** YOUR CODE HERE ***
        def expectimax(state, index, depth): #helper to make max/expected simple
            if depth == self.depth or len(state.get_legal_actions(0)) == 0: #issues with is_win, lose
                return self.evaluation_function(state)
            if index == 0: #pacman (max)
                return max_value(state, index, depth)
            else: #ghost (expected)
                return expected_value(state, index, depth)

        def max_value(state, index, depth):
            current_value = -math.inf
            legal_moves = state.get_legal_actions(index)
            if not legal_moves:  #prevents nasty stuff happening
                return self.evaluation_function(state)
            for action in legal_moves:
                next_state = state.generate_successor(index, action)
                current_value = max(current_value, expectimax(next_state, 1, depth))
            return current_value

        def expected_value(state, index, depth):
            current_value = 0
            legalMoves = state.get_legal_actions(index)
            if not legalMoves:
                return self.evaluation_function(state)

            chanceCalc = 1.0/len(legalMoves) #expectation/probability

            nextIndex = index +1
            if nextIndex == state.get_num_agents():
                nextIndex = 0
                depth += 1

            for action in legalMoves:
                next_state = state.generate_successor(index, action)
                current_value += chanceCalc * expectimax(next_state, nextIndex, depth)
            return current_value

        legalMovesOUT = game_state.get_legal_actions(0)
        current_move = None
        current_score = -math.inf

        for actionOUT in legalMovesOUT:
            next_stateOUT = game_state.generate_successor(0, actionOUT)
            score = expectimax(next_stateOUT, 1, 0)
            if score > current_score:
                current_move = actionOUT
                current_score = score
        return current_move #final


def better_evaluation_function(current_game_state):
    """
      Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
      evaluation function (question 5).

      DESCRIPTION: Close to previous eval function, includes logic for desiring food but prioritizing survival by\
      staying away from active ghosts and chasing scared ghosts. Additionally, has code to drive pacman towards the power pellets
      /capsules
    """

    # *** YOUR CODE HERE ***
    # Useful information you can extract from a GameState (pacman.py)
    successor_game_state = current_game_state
    new_pos = successor_game_state.get_pacman_position()
    new_food = successor_game_state.get_food()
    new_ghost_states = successor_game_state.get_ghost_states()
    new_pellets = current_game_state.get_capsules()
    current_score = current_game_state.get_score()
    new_scared_times = [ghost_state.scared_timer for ghost_state in new_ghost_states]

    food = new_food.as_list()
    if food:
        closest_food = min([manhattan_distance(new_pos, food_pos) for food_pos in food])
        current_score += 1.0 /closest_food

    for i, ghost in enumerate(new_ghost_states): #enumerate = more robust
        ghost_position = ghost.get_position()
        ghost_distance = manhattan_distance(new_pos, ghost_position)

        if new_scared_times[i] > 0: #being near scared ghosts is good
            current_score += 200/ghost_distance
        else:
            if ghost_distance < 2: #being near active ghosts bad
                current_score-= 1000

    if new_pellets: #seek and use power pellets similar to food
        closest_pellets = min([manhattan_distance(new_pos, capsule) for capsule in new_pellets])
        current_score += 2.0 / (closest_pellets+1)

    current_score -= len(food) * 10 #leaving food on the board = bad

    if len(food) == 0:
        current_score += 1000.0 ##board clear = good

    return current_score

# Abbreviation
better = better_evaluation_function

#TODO brennan.miller.20@cnu.edu