# keyboardAgents.py
# updated for Wumpus world
#
# (c) 2016 Christopher Newport University
#           David Conner (david.conner@cnu.edu)
#
# ------------------
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
Provide basic keyboard play for Wumpus game
"""
from game import Agent
from game import Actions

class KeyboardAgent(Agent):
    """
    An agent controlled by the keyboard.
    """
    # NOTE: Arrow keys also work.
    LEFT_KEY = 'a'
    RIGHT_KEY = 'd'
    FWD_KEY = 'w'
    STOP_KEY = 's'
    HALT_KEY = 'q'
    GRAB_KEY = 'g'
    SHOOT_KEY = 'x'

    def __init__(self, index=0):
        """
        Initialize the keyboard agent
        """
        super(KeyboardAgent, self).__init__(index)
        self.last_cmd = None
        self.keys = []

    def get_action(self, state):
        """
        Get a legal action command
        """

        assert self.index == 0
        ## Pacman
        #pacman_state = state.data.agent_states[0]
        #from game import Directions
        #if pacman_state.last_action == Directions.STOP:
        #    sensors = self.get_sensors(state)
        #    if (sensors is not None):
        #        print "Sensors: ", sensors

        from graphics_utils import keys_waiting
        from graphics_utils import keys_pressed
        keys = keys_waiting() + keys_pressed()

        if not keys:
            # Nothing to process
            return None

        self.keys = keys

        legal = state.get_legal_actions(self.index)
        #print("legal actions =", legal)

        cmd = self.get_cmd(legal)
        #print("legal command=", cmd)

        if cmd is None:
            return None

        if cmd not in legal:
            return None

        self.last_cmd = cmd
        return cmd


    def get_cmd(self, legal):
        """
        Get command from valid operations
        """
        move = None
        if (self.LEFT_KEY in self.keys or 'Left' in self.keys) and \
            Actions.LEFT in legal:
            move = Actions.LEFT

        if (self.RIGHT_KEY in self.keys or 'Right' in self.keys) and \
            Actions.RIGHT in legal:
            move = Actions.RIGHT

        if (self.FWD_KEY in self.keys or 'Up' in self.keys) and \
            Actions.FWD in legal:
            move = Actions.FWD

        if (self.STOP_KEY in self.keys or self.HALT_KEY in self.keys or \
            'Down' in self.keys) and Actions.STOP in legal:
            move = Actions.STOP

        if self.GRAB_KEY in self.keys and Actions.GRAB in legal:
            move = Actions.GRAB

        if self.SHOOT_KEY in self.keys and Actions.SHOOT in legal:
            move = Actions.SHOOT

        return move
