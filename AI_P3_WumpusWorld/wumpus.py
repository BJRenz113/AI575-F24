# wumpus.py based on pacman.py
# (c) 2016-2020 Christopher Newport University
#           David Conner (david.conner@cnu.edu)
#
# ---------
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
#

"""
Wumpus.py holds the logic for the classic Wumpus world logic puzzle along with the main
code to run a game.  This file is divided into three sections:

  (i)  Your interface to the Wumpus world:
          The wumpus is a simple bounded environment.
          Unfortuately, the environment contains bottomless pits and
          a deadly and stinky Wumpus, along with some glittery gold coins.
          You probably don't want to
          read through all of the code we wrote to make the game runs
          correctly.  This section contains the parts of the code
          that you will need to understand in order to complete the
          project.  There is also some code in game.py that you should
          understand.

  (ii)  The hidden secrets of wumpus:
          This section contains all of the logic code that the wumpus
          environment uses to decide who can move where, who dies when
          things collide, etc.  You shouldn't need to read this section
          of code, but you can if you want.

  (iii) Framework to start a game:
          The final section contains the code for reading the command
          you use to set up the game, then starting up a new game, along with
          linking in all the external parts (agent functions, graphics).
          Check this section out to see all the options available to you.

To play your first game, type 'python wumpus.py' from the command line.
The keys are 'a', 's', 'd', and 'w' to move (or arrow keys).  Have fun!
"""
import os
import random
import sys
import time

from game import GameStateData
from game import Game
from game import Directions
from game import Actions
from game import Configuration

from util import nearest_point
from util import manhattan_distance

import layout


###################################################
# YOUR INTERFACE TO THE WUMPUS WORLD: A GameState #
###################################################

class GameState:
    """
    A GameState specifies the full game state, including the treasure, pits, and the wumpus.
    The GameState is not visible to the agent, only sensory inputs at the current location

        Breezy if a pit is adjacent
        Stinky if the Wumpus is adjacent
        Glittery if the gold is found
        Scream if the Wumpus is shot with immobilizer ray

    GameStates are used by the Game object to capture the actual state of the game and
    can be used by agents to reason about the game.

    Much of the information in a GameState is stored in a GameStateData object.  We
    strongly suggest that you access that data via the accessor methods below rather
    than referring to the GameStateData object directly.

    """

    ####################################################
    # Accessor methods: use these to access state data #
    ####################################################

    # static variable keeps track of which states have had get_legal_actions called
    explored = set()

    @staticmethod
    def get_and_reset_explored():
        tmp = GameState.explored.copy()
        GameState.explored = set()
        return tmp
    #get_and_reset_explored = staticmethod(get_and_reset_explored)

    def get_legal_actions(self, agent_index=0):
        """
        Returns the legal actions for the agent specified.
        """
        if self.is_win() or self.is_lose():
            return []

        if agent_index == 0:  # Pacman is moving
            return PacmanRules.get_legal_actions(self)

        return WumpusRules.get_legal_actions(self, agent_index)

    def get_legal_directions(self, agent_index=0):
        """
        Returns the legal directions of motion for the agent specified.
        """
        if self.is_win() or self.is_lose(): return []

        if agent_index == 0:  # Pacman is moving
            return PacmanRules.get_legal_directions(self)

        return WumpusRules.get_legal_directions(self, agent_index)

    def generate_successor(self, agent_index, action):
        """
        Returns the successor state after the specified agent takes the action.
        """
        # Check that successors exist
        if self.is_win() or self.is_lose():
            raise Exception('Can\'t generate a successor of a terminal state.')

        # Copy current state
        state = GameState(self)

        # Let agent's logic deal with its action's effects on the board
        if agent_index == 0:  # Pacman is moving
            state.data._eaten = [False for i in range(state.get_num_agents())]
            PacmanRules.apply_action(state, action)
        else:                # Wumpus is moving
            WumpusRules.apply_action(state, action, agent_index)

        # Time passes
        if agent_index == 0:
            state.data.score_change += -TIME_PENALTY # Penalty for waiting around
        else:
            WumpusRules.decrementTimer(state.data.agent_states[agent_index])

        # Resolve multi-agent effects
        WumpusRules.check_immobilized(state, agent_index)

        # Book keeping
        state.data._agent_moved = agent_index
        state.data.score += state.data.score_change
        GameState.explored.add(self)
        GameState.explored.add(state)
        return state

    def get_legal_pacman_actions(self):
        return self.get_legal_actions(0)

    def get_legal_pacman_directions(self):
        return self.get_legal_directions(0)

    def generate_pacman_successor(self, action):
        """
        Generates the successor state after the specified pacman move
        """
        return self.generate_successor(0, action)

    def get_pacman_state(self):
        """
        Returns an AgentState object for pacman (in game.py)

        state.pos gives the current position
        state.direction gives the travel vector
        """
        return self.data.agent_states[0].copy()

    def get_pacman_position(self):
        return self.data.agent_states[0].get_position()

    def get_wumpus_states(self):
        return self.data.agent_states[1] # Only one Wumpus

    def get_wumpus_state(self, agent_index):
        if agent_index == 0 or agent_index >= self.get_num_agents():
            raise Exception("Invalid index passed to get_wumpus_state")
        return self.data.agent_states[agent_index]

    def get_wumpus_position(self, agent_index):
        if agent_index == 0:
            raise Exception("Pacman's index passed to get_wumpus_position")
        return self.data.agent_states[agent_index].get_position()

    def get_wumpus_positions(self):
        return [s.get_position() for s in self.get_wumpus_states()]

    def get_num_agents(self):
        return len(self.data.agent_states)

    def get_score(self):
        return float(self.data.score)

    def get_capsules(self):
        """
        Returns a list of positions (x,y) of the remaining capsules.
        """
        return self.data.capsules

    def get_num_food(self):
        return self.data.food.count()

    def get_food(self):
        """
        Returns a Grid of boolean food indicator variables.

        Grids can be accessed via list notation, so to check
        if there is food at (x,y), just call

        currentFood = state.get_food()
        if currentFood[x][y] == True: ...
        """
        return self.data.food

    def get_walls(self):
        """
        Returns a Grid of boolean wall indicator variables.

        Grids can be accessed via list notation, so to check
        if there is a wall at (x,y), just call

        walls = state.get_walls()
        if walls[x][y] == True: ...
        """
        return self.data.layout.walls

    def has_food(self, x, y):
        return self.data.food[x][y]

    def has_wall(self, x, y):
        return self.data.layout.walls[x][y]

    def is_lose(self):
        return self.data._lose

    def is_win(self):
        return self.data._win

    #############################################
    #             Helper methods:               #
    # You shouldn't need to call these directly #
    #############################################

    def __init__(self, prevState=None):
        """
        Generates a new state by copying information from its predecessor.
        """
        if prevState != None: # Initial state
            self.data = GameStateData(prevState.data)
        else:
            self.data = GameStateData()

    def deepCopy(self):
        state = GameState(self)
        state.data = self.data.deepCopy()
        return state

    def __eq__(self, other):
        """
        Allows two states to be compared.
        """
        return hasattr(other, 'data') and self.data == other.data

    def __hash__(self):
        """
        Allows states to be keys of dictionaries.
        """
        return hash(self.data)

    def __str__(self):

        return str(self.data)

    def initialize(self, world_layout, num_wumpus_agents=1):
        """
        Creates an initial game state from a layout array (see layout.py).
        """
        self.data.initialize(world_layout, num_wumpus_agents)

############################################################################
#                     THE HIDDEN SECRETS OF Wumpus                         #
#                                                                          #
# You shouldn't need to look through the code in this section of the file. #
############################################################################

COLLISION_TOLERANCE = 0.7 # How close the Wumpus must be to Pacman to kill
TIME_PENALTY = 1          # Number of points lost each round

class ClassicGameRules:
    """
    These game rules manage the control flow of a game, deciding when
    and how the game starts and ends.
    """
    def __init__(self, timeout=30):
        self.timeout = timeout

    def new_game(self, world_layout, pacman_agent, wumpus_agents,
                 display, quiet=False, catch_exceptions=False):
        agents = [pacman_agent] + wumpus_agents[:world_layout.getNumGhosts()]
        init_state = GameState()
        init_state.initialize(world_layout, len(wumpus_agents))
        game = Game(agents, display, self, catch_exceptions=catch_exceptions)
        game.state = init_state
        self.initialState = init_state.deepCopy()
        self.quiet = quiet
        return game

    def process(self, state, game):
        """
        Checks to see whether it is time to end the game.
        """
        if state.is_win():
            self.win(state, game)

        if state.is_lose():
            self.lose(state, game)

    def win(self, state, game):
        if not self.quiet: print("Pacman emerges victorious! Score: %d" % state.data.score)
        game.game_over = True

    def lose(self, state, game):
        if not self.quiet: print("Pacman died! Score: %d" % state.data.score)
        game.game_over = True

    def get_progress(self, game):
        return float(game.state.get_num_food()) / self.initialState.get_num_food()

    def agent_crash(self, game, agent_index):
        if agent_index == 0:
            print("Pacman crashed")
        else:
            print("The Wumpus crashed")

    def getMaxTotalTime(self, agent_index):
        return self.timeout

    def getMaxStartupTime(self, agent_index):
        return self.timeout

    def getMoveWarningTime(self, agent_index):
        return self.timeout

    def getMoveTimeout(self, agent_index):
        return self.timeout

    def getMaxTimeWarnings(self, agent_index):
        return 0

class PacmanRules:
    """
    These functions govern how pacman interacts with his environment under
    the classic game rules.
    """
    PACMAN_SPEED = 0.5

    @staticmethod
    def get_legal_actions(state):
        """
        Returns a list of possible actions.
        """
        return Actions.get_possible_actions(state.get_pacman_state().configuration,
                                            state.data.layout.walls)
    #get_legal_actions = staticmethod(get_legal_actions)

    @staticmethod
    def get_legal_directions(state):
        """
        Returns a list of valid directions for motion.
        """
        return Actions.get_possible_directions(
            state.get_pacman_state().configuration,
            state.data.layout.walls)
    #get_legal_directions = staticmethod(get_legal_directions)

    @staticmethod
    def apply_action(state, action):
        """
        Edits the state to reflect the results of the action.
        """

        pacman_state = state.data.agent_states[0]

        #print "Pacman action=", action
        #print "pacman: state=", state, "  action=", action
        #print "pac current config=", pacman_state.configuration
        #print "pacman_state.last_action=", pacman_state.last_action

        legal_actions = PacmanRules.get_legal_actions(state)
        legal_directions = PacmanRules.get_legal_directions(state)

        if action is None:
            action = pacman_state.last_action
        elif pacman_state.bumped and (action != pacman_state.last_action or action == Actions.STOP):
            # New action (or chosen STOP) so clear prior bump flag
            pacman_state.bumped = False

        if action == Actions.FWD:
            if pacman_state.configuration.get_direction() not in legal_directions:
                print("Bumped into a wall!")
                action = Actions.STOP
                pacman_state.bumped = True
            else:
                pacman_state.bumped = False

        else:
            if action not in legal_actions:
                print("Action was ", action)
                print("Legal actions are", legal_actions)
                raise Exception("Illegal action " + str(action))

        # Update Configuration
        if action == Actions.FWD:
            #print "Pacman move forward"
            vector = Actions.direction_to_vector(pacman_state.configuration.get_direction(),
                                                 PacmanRules.PACMAN_SPEED)
            pacman_state.configuration = pacman_state.configuration.generate_successor(vector)
        elif action == Actions.RIGHT:
            print("Pacman turn right and stop!")
            pacman_state.configuration.direction = \
                Directions.RIGHT_TURN[pacman_state.configuration.direction]
            action = Actions.STOP
        elif action == Actions.LEFT:
            print("Pacman turn left and stop!")
            pacman_state.configuration.direction = \
                Directions.LEFT_TURN[pacman_state.configuration.direction]
            action = Actions.STOP
        elif action == Actions.GRAB:
            if pacman_state.last_action == Actions.STOP:
                position = nearest_point(pacman_state.configuration.get_position())
                x, y = position
                if state.data.food[x][y]:
                    state.data.score_change += 250 # Minor elation, but need to escape
                    print("Got the gold!")
                    pacman_state.has_gold = True
                    #state.data.food = state.data.food.copy()
                    state.data.food[x][y] = False
                    state.data._food_eaten = position
                    # TODO: cache num_food?
                    num_food = state.get_num_food()
                else:
                    print("No gold here!")
                    state.data.score_change -= 50 # Discouragement
                action = Actions.STOP

            else:
                print("Cannot grab while moving!")
        elif action == Actions.SHOOT:
            if pacman_state.last_action == Actions.STOP:
                vector = Actions.direction_to_vector(pacman_state.configuration.get_direction(), 1)
                vx, vy = (int(vector[0]), int(vector[1]))
                ix, iy = nearest_point(pacman_state.configuration.get_position())

                if pacman_state.has_immobilizer:
                    ray_fly = True
                    try:
                        while not state.has_wall(ix, iy):
                            for wumpus in state.data.agent_states[1:]:
                                if manhattan_distance((ix, iy), wumpus.get_position()) <= 0.25:
                                    print("Horrible scream of Wumpus agony.")
                                    ray_fly = False # Hit our target
                                    pacman_state.scream = True
                                    wumpus.scared_timer = 100 # Wumpus is immobilized
                                    pacman_state.scared_timer = 100 # Flag the scream
                            ix = ix + vx
                            iy = iy + vy
                    except:
                        ray_fly = False

                    if ray_fly:
                        # We did not hit our target before hitting wall or exiting maze via entrance
                        print("ding!")
                else:
                    print("No immobilizer shot for you!")

                pacman_state.has_immobilizer = False
                action = Actions.STOP
            else:
                print("Cannot shoot while moving!")

        next = pacman_state.configuration.get_position()

        if pacman_state.configuration.is_integer() and action == Actions.FWD:
            #print "Stopping at integer cell!", next
            action = Actions.STOP
            pacman_state.configuration = Configuration((round(next[0]), round(next[1])),
                                                       pacman_state.configuration.get_direction())
            next = pacman_state.configuration.get_position()
            #print "         ", next

        # Store the current action
        pacman_state.last_action = action

        # Check to see if we fell into a pits
        nearest = nearest_point(next)
        if manhattan_distance(nearest, next) <= 0.5:
            if nearest in state.get_capsules():
                state.data.capsules.remove(nearest)
                state.data._capsule_eaten = nearest
                state.data._lose = True
                print("Fell into pit!")
                state.data.score_change -= 10000

        # Check escape
        if state.get_num_food() == 0 and not state.data._lose:
            x, y = nearest_point(next)
            sx, sy = pacman_state.start.pos
            if x == sx and y == sy:
                print("You escaped with the gold!  We have a winner!")
                state.data.score_change += 2000
                state.data._win = True


    #apply_action = staticmethod(apply_action)


class WumpusRules:
    """
    These functions dictate how the Wumpus interacts with their environment.
    """
    WUMPUS_SPEED = 0.0 # The Wumpus does not move
    @staticmethod
    def get_legal_actions(state, wumpus_index):
        """
        The Wumpus does not move from his position
        """
        if wumpus_index != 1:
            print("ERROR: Only one Wumpus should be in the maze!")
        return [Actions.STOP]
    #get_legal_actions = staticmethod(get_legal_actions)

    @staticmethod
    def get_legal_directions(state, wumpus_index):
        """
        The Wumpus does not move from his position
        """
        if wumpus_index != 1:
            print("ERROR: Only one Wumpus should be in the maze!")
        return [Directions.STOP]
    #get_legal_directions = staticmethod(get_legal_directions)

    @staticmethod
    def apply_action(state, action, wumpus_index):
        pass # Wumpus takes no action

    #apply_action = staticmethod(apply_action)

    @staticmethod
    def decrementTimer(wumpus_state):
        pass # Wumpus is not scared

    #decrementTimer = staticmethod(decrementTimer)

    @staticmethod
    def check_immobilized(state, agent_index):
        pacman_position = state.get_pacman_position()
        if agent_index == 0: # Pacman just moved; Anyone can kill him
            for index in range(1, len(state.data.agent_states)):
                wumpus_state = state.data.agent_states[index]
                wumpus_position = wumpus_state.configuration.get_position()
                if WumpusRules.can_immobilize(pacman_position, wumpus_position):
                    WumpusRules.collide(state, wumpus_state, index)
        else:
            wumpus_state = state.data.agent_states[agent_index]
            wumpus_position = wumpus_state.configuration.get_position()
            if WumpusRules.can_immobilize(pacman_position, wumpus_position):
                WumpusRules.collide(state, wumpus_state, agent_index)
    #check_immobilized = staticmethod(check_immobilized)

    @staticmethod
    def collide(state, wumpus_state, agent_index):
        if wumpus_state.scared_timer > 0:
            if not state.data.agent_states[0].found_immobile:
                print("You found an immobilized wumpus!")
                state.data.score_change += 300 # The wumpus is immobilized.  Yeah!
                state.data.agent_states[0].found_immobile = True
        else:
            print("Oh no!  You were eaten by the Wumpus. What a horrible, stinky way to go!")
            state.data.score_change -= 20000 # eaten by the Wumpus.
            state.data._lose = True
    #collide = staticmethod(collide)

    @staticmethod
    def can_immobilize(pacman_position, wumpus_position):
        return manhattan_distance(wumpus_position, pacman_position) <= COLLISION_TOLERANCE
    #can_immobilize = staticmethod(can_immobilize)

    @staticmethod
    def place_wumpus(state, wumpus_state):
        wumpus_state.configuration = wumpus_state.start
#    place_wumpus = staticmethod(place_wumpus)

#############################
# FRAMEWORK TO START A GAME #
#############################

def default(str):
    return str + ' [Default: %default]'

def parse_agent_args(str):
    if str == None: return {}
    pieces = str.split(',')
    opts = {}
    for p in pieces:
        if '=' in p:
            key, val = p.split('=')
        else:
            key, val = p, 1
        opts[key] = val
    return opts

def read_command(argv):
    """
    Processes the command used to run pacman from the command line.
    """

    from optparse import OptionParser

    usageStr = \
    """
    USAGE:      python wumpus.py <options>
                     - starts an interactive game

    """
    parser = OptionParser(usageStr)

    parser.add_option('-n', '--num_games', dest='num_games', type='int',
                      help=default('the number of GAMES to play'), metavar='GAMES', default=1)
    parser.add_option('-l', '--layout', dest='world_layout',
                      help=default('the LAYOUT_FILE from which to load the map layout'),
                      metavar='LAYOUT_FILE', default='wumpus2')
    parser.add_option('-p', '--pacman', dest='pacman',
                      help=default('the agent TYPE in the pacman_agents module to use'),
                      metavar='TYPE', default='KeyboardAgent')
    parser.add_option('-t', '--textGraphics', action='store_true', dest='text_graphics',
                      help='Display output as text only', default=False)
    parser.add_option('-q', '--quietTextGraphics', action='store_true', dest='quiet_graphics',
                      help='Generate minimal output and no graphics', default=False)
    parser.add_option('-z', '--zoom', type='float', dest='zoom',
                      help=default('Zoom the size of the graphics window'), default=1.0)
    parser.add_option('-f', '--fixRandomSeed', action='store_true', dest='fixRandomSeed',
                      help='Fixes the random seed to always play the same game', default=False)
    parser.add_option('-r', '--recordActions', action='store_true', dest='record',
                      help='Writes game histories to a file (named by the time they were played)', default=False)
    parser.add_option('--replay', dest='game_to_replay',
                      help='A recorded game file (pickle) to replay', default=None)
    parser.add_option('-a', '--agentArgs', dest='agentArgs',
                      help='Comma separated values sent to agent. e.g. "opt1=val1,opt2,opt3=val3"')
    parser.add_option('--frameTime', dest='frameTime', type='float',
                      help=default('Time to delay between frames; <0 means keyboard'), default=0.1)
    parser.add_option('-c', '--catch_exceptions', action='store_true', dest='catch_exceptions',
                      help='Turns on exception handling and timeouts during games', default=False)
    parser.add_option('--timeout', dest='timeout', type='int',
                      help=default('Maximum length of time an agent can spend computing in a single game'), default=30)
    parser.add_option('-s', '--showWumpusWorld', action='store_true', dest='show_wumpus_world',
                      help='Turns a light on in the cave to show the world', default=False)
    parser.add_option('--randomize', dest='randomize', action='store_true',
                      help=default('Randomize the position of pits, Wumpus, and gold within the walls'), default=False)

    options, otherjunk = parser.parse_args(argv)
    if otherjunk:
        raise Exception('Command line input not understood: ' + str(otherjunk))
    args = dict()

    # Fix the random seed
    if options.fixRandomSeed:
        random.seed('cpsc471')

    # Choose a layout
    args['world_layout'] = layout.getLayout(options.world_layout)
    if args['world_layout'] == None:
        raise Exception("The layout " + options.layout + " cannot be found")

    if options.randomize:
        args['world_layout'].radomize()


    # Choose a Pacman agent
    noKeyboard = options.game_to_replay is None and (options.text_graphics or options.quiet_graphics)
    pacman_type = loadAgent(options.pacman, noKeyboard)
    agent_opts = parse_agent_args(options.agentArgs)
    pacman = pacman_type(**agent_opts) # Instantiate Pacman with agentArgs

    args['pacman'] = pacman

    # Choose a wumpus agent
    wumpus_type = loadAgent("WumpusAgent", noKeyboard)
    args['wumpus'] = [wumpus_type(i+1) for i in range(1)] # Only one Wumpus in maze

    # Choose a display format
    if options.quiet_graphics:
        import text_display
        args['display'] = text_display.NullGraphics()
    elif options.text_graphics:
        import text_display
        text_display.SLEEP_TIME = options.frameTime
        args['display'] = text_display.WumpusGraphics()
    else:
        import graphics_display
        args['display'] = \
            graphics_display.WumpusGraphics(options.zoom,
                                            frameTime=options.frameTime,
                                            show_wumpus_world=options.show_wumpus_world)
    args['num_games'] = options.num_games
    args['record'] = options.record
    args['catch_exceptions'] = options.catch_exceptions
    args['timeout'] = options.timeout

    # Special case: recorded games don't use the run_games method or args structure
    if options.game_to_replay:
        print('Replaying recorded game %s.' % options.game_to_replay)
        import pickle
        fin = open(options.game_to_replay)
        try:
            recorded = pickle.load(fin)
        finally:
            fin.close()
        recorded['display'] = args['display']
        replay_game(**recorded)
        sys.exit(0)

    return args

def loadAgent(new_agent, nographics):
    # Looks through all pythonPath Directories for the right module,
    python_path_str = os.path.expandvars("$PYTHONPATH")
    if python_path_str.find(';') == -1:
        python_path_dirs = python_path_str.split(':')
    else:
        python_path_dirs = python_path_str.split(';')
    python_path_dirs.append('.')

    for module_dir in python_path_dirs:
        if not os.path.isdir(module_dir): continue
        module_names = [f for f in os.listdir(module_dir) if f.endswith('gents.py')]
        #print " Trying modules:", module_names

        for module_name in module_names:
            try:
                module = __import__(module_name[:-3])
                #print "Trying to load <", new_agent, "> from ", module
            except ImportError:
                print("Import error with module=<", module_name, "> (", module_name[:-3], ")")
                continue
            if new_agent in dir(module):
                if nographics and module_name == 'keyboard_agents.py':
                    raise Exception('Using the keyboard requires graphics (not text display)')

                print("Loading ", new_agent, " from", module_name)
                return getattr(module, new_agent)
    raise Exception('The agent ' + new_agent + ' is not specified in any *_agents.py.')

def replay_game(world_layout, actions, display):
    """
    Replay a saved game
    """

    import pacman_agents
    import wumpus_agents
    rules = ClassicGameRules()
    agents = [pacman_agents.GreedyAgent()] + \
             [wumpus_agents.WumpusAgent(i+1) for i in range(world_layout.getNumGhosts())]
    game = rules.new_game(world_layout, agents[0], agents[1:], display)
    state = game.state
    display.initialize(state.data)

    for action in actions:
            # Execute the action
        state = state.generate_successor(*action)
        # Change the display
        display.update(state.data)
        # Allow for game specific conditions (winning, losing, etc.)
        rules.process(state, game)

    display.finish()

def run_games(world_layout, pacman, wumpus, display,
              num_games, record, num_training=0,
              catch_exceptions=False, timeout=30):
    """
    Run the game
    """

    import __main__
    __main__.__dict__['_display'] = display

    rules = ClassicGameRules(timeout)
    games = []

    for i in range(num_games):
        be_quiet = i < num_training
        if be_quiet:
                # Suppress output and graphics
            import text_display
            game_display = text_display.NullGraphics()
            rules.quiet = True
        else:
            game_display = display
            rules.quiet = False

        game = rules.new_game(world_layout, pacman, wumpus,
                              game_display, be_quiet, catch_exceptions)
        game.run()
        if not be_quiet:
            games.append(game)

        if record:
            import pickle
            fname = ('recorded-game-%d' % (i + 1)) + \
                     '-'.join([str(t) for t in time.localtime()[1:6]])
            fout = open(fname, 'w')
            components = {'world_layout': world_layout,
                          'actions': game.moveHistory}
            pickle.dump(components, fout)
            fout.close()

    if (num_games-num_training) > 0:
        scores = [game.state.get_score() for game in games]
        wins = [game.state.is_win() for game in games]
        win_rate = wins.count(True)/ float(len(wins))
        print('Average Score:', sum(scores) / float(len(scores)))
        print('Scores:       ', ', '.join([str(score) for score in scores]))
        print('Win Rate:      %d/%d (%.2f)' % (wins.count(True), len(wins), win_rate))
        print('Record:       ', ', '.join([['Loss', 'Win'][int(w)] for w in wins]))

    return games

if __name__ == '__main__':
    """
    The main function called when wumpus.py is run
    from the command line:

    > python wumpus.py

    See the usage string for more details.

    > python wumpus.py --help
    """

    start_time = time.time()
    args = read_command(sys.argv[1:]) # Get game components based on input
    run_games(**args)
    end_time = time.time()

    #print "start=", start_time
    #print " end =", end_time
    print("Elapsed = ", end_time - start_time)

    # import cProfile
    # cProfile.run("run_games(**args)")
