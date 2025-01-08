"""
value_iteration_agents.py
-----------------------
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

import util

from learning_agents import ValueEstimationAgent


class ValueIterationAgent(ValueEstimationAgent):
    """
        * Please read learning_agents.py before reading this.*

        A ValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs value iteration
        for a given number of iterations using the supplied
        discount factor.
    """

    def __init__(self, mdp, discount=0.9, iterations=100):
        """
          Your value iteration agent should take an mdp on
          construction, run the indicated number of iterations
          and then act according to the resulting policy.

          Some useful mdp methods you will use:
              mdp.get_states()
              mdp.get_possible_actions(state)
              mdp.get_transition_states_and_probs(state, action)
              mdp.get_reward(state, action, next_state)
              mdp.is_terminal(state)
        """
        super().__init__()
        self.mdp = mdp
        self.discount = discount
        self.iterations = iterations
        self.values = util.Counter()  # A Counter is a dict with default 0

        # Write value iteration code here
        # *** YOUR CODE HERE ***
        for _ in range(self.iterations):
            currValues = util.Counter()
            for state in self.mdp.get_states():
                if self.mdp.is_terminal(state):
                    currValues[state] = 0
                else:
                    action_values = [self.compute_q_value_from_values(state, action) for action in self.mdp.get_possible_actions(state) ]
                    if action_values:
                        currValues[state] = max(action_values)
            self.values = currValues


    def get_value(self, state):
        """
          Return the value of the state (computed in __init__).
        """
        return self.values[state]

    def compute_q_value_from_values(self, state, action):
        """
          Compute the Q-value of action in state from the
          value function stored in self.values.
        """

        # *** YOUR CODE HERE ***
        q_value = 0
        for next_state, probability in self.mdp.get_transition_states_and_probs(state, action):
            rewardGiven = self.mdp.get_reward(state, action, next_state)
            q_value += probability * (rewardGiven + self.discount * self.values[next_state])
        return q_value

    def compute_action_from_values(self, state):
        """
          The policy is the best action in the given state
          according to the values currently stored in self.values.

          You may break ties any way you see fit.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return None.
        """

        # *** YOUR CODE HERE ***
        currAction = None
        maxQ = float('-inf')
        if self.mdp.is_terminal(state):
            return None

        actions = self.mdp.get_possible_actions(state)
        if not actions:
            return None

        for action in actions: #looking for highest qval
            q_value = self.compute_q_value_from_values(state, action)
            if q_value > maxQ:
                maxQ = q_value
                currAction = action
        return currAction

    def get_policy(self, state):
        return self.compute_action_from_values(state)

    def get_action(self, state):
        """Returns the policy at the state (no exploration)."""
        return self.compute_action_from_values(state)

    def get_q_value(self, state, action):
        return self.compute_q_value_from_values(state, action)
