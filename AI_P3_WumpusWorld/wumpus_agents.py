# wumpusAgents.py based on ghostAgents.py
# (c) 2016-2020 Christopher Newport University
#           David Conner (david.conner@cnu.edu)
#
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

"""
Simple stay put wumpus agent
"""
from game import Agent
from game import Directions
import util

class WumpusAgent(Agent):
    """
    Simple stay put wumpus agent
    """
    def __init__(self, index):
        super(WumpusAgent, self).__init__(index)
        self.index = index

    def get_action(self, state):
        """
        Get only valid action for wumpus (stop)
        """
        #print "The Wumpus is always stopped"
        return Directions.STOP

    def get_distribution(self, state):
        """
        Returns a Counter encoding a distribution over actions from the provided state.
        """
        dist = util.Counter()
        for action in state.get_legal_actions(self.index):
            dist[action] = 1.0
        dist.normalize()
        return dist
