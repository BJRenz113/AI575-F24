# game.py
# -------
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


# game.py
# -------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

"""
Game agent
"""

#import os
import sys
import time
import traceback
from util import nearest_point, TimeoutFunction, TimeoutFunctionException

#######################
# Parts worth reading #
#######################

class Agent:
    """
    An agent must define a get_action method, but may also define the
    following methods which will be called if they exist:

    def registerInitialState(self, state): # inspects the starting state
    """
    def __init__(self, index=0):
        self.index = index

    def get_action(self, state):
        """
        The Agent will receive a GameState (from either {pacman, capture, sonar}.py) and
        must return an action from Directions.{North, South, East, West, Stop}
        """
        raiseNotDefined()

    def get_sensors(self, state):
        """
        The Agent will receive a GameState (from either {pacman, capture, sonar}.py) and
        must return the sensor inputs if and only if STOPPED
        """

        if self.index:
            return None # Wumpus does not sense

        return state.data.agent_states[0].get_sensors(state.data)

class Directions:
    NORTH = 'North'
    SOUTH = 'South'
    EAST = 'East'
    WEST = 'West'
    STOP = 'Stop'

    LEFT_TURN = {NORTH: WEST,
                 SOUTH: EAST,
                 EAST:  NORTH,
                 WEST:  SOUTH,
                 STOP:  STOP}

    RIGHT_TURN = dict([(y, x) for x, y in list(LEFT_TURN.items())])

    #REVERSE = {NORTH: SOUTH,  # Don't reverse in Wumpus
    #           SOUTH: NORTH,
    #           EAST: WEST,
    #           WEST: EAST,
    #           STOP: STOP}

class Configuration:
    """
    A Configuration holds the (x, y) coordinate of a character, along with its
    traveling direction.

    The convention for positions, like a graph, is that (0,0) is the lower left corner, x increases
    horizontally and y increases vertically.  Therefore, north is the direction of increasing y, or (0, 1).
    """

    def __init__(self, pos, direction):
        """
        Initialize
        """
        self.pos = pos
        self.direction = direction

    def get_position(self):
        """
        Get current position
        """
        return self.pos

    def get_direction(self):
        """
        Get directions reference
        """
        return self.direction

    def is_integer(self):
        """
        True if current position is integer grid value
        """
        x, y = self.pos
        xr = int(round(x, 4))
        yr = int(round(y, 4))
        return abs(x - xr) < 1e-6 and abs(y - yr) < 1e-6

    def __eq__(self, other):
        """
        Agent equal if position and direction are same
        """
        if other is None:
            return False
        return self.pos == other.pos and self.direction == other.direction

    def __hash__(self):
        """
        Hash based on position and direction
        """
        x = hash(self.pos)
        y = hash(self.direction)
        return hash(x + 13 * y)

    def __str__(self):
        """
        Return position and direction in string
        """
        return "(x, y)="+str(self.pos)+", "+str(self.direction)

    def generate_successor(self, vector):
        """
        Generates a new configuration reached by translating the current
        configuration by the action vector.  This is a low-level call and does
        not attempt to respect the legality of the movement.

        Actions are movement vectors.
        """
        x, y = self.pos
        dx, dy = vector
        direction = Actions.vector_to_direction(vector)
        if direction == Directions.STOP:
            direction = self.direction # There is no stop direction
        return Configuration((x + dx, y+dy), direction)

class AgentState:
    """
    AgentStates hold the state of an agent (configuration, speed, scared, etc).
    """

    def __init__(self, startConfiguration, is_pacman):
        self.start = startConfiguration
        self.configuration = startConfiguration
        self.is_pacman = is_pacman
        self.scared_timer = 0
        self.num_carrying = 0
        self.num_returned = 0
        if self.is_pacman: # Sensor data for Pacman
            self.last_action = Directions.STOP
            self.has_immobilizer = True
            self.has_gold = False
            self.bumped = False
            self.scream = False
            self.found_immobile = False

    def __str__(self):
        if self.is_pacman:
            return "Pacman: " + str(self.configuration)
        else:
            return "Ghost: " + str(self.configuration)

    def __eq__(self, other):
        if other is None:
            return False
        return self.configuration == other.configuration and self.scared_timer == other.scared_timer

    def __hash__(self):
        return hash(hash(self.configuration) + 13 * hash(self.scared_timer))

    def copy(self):
        state = AgentState(self.start, self.is_pacman)
        state.configuration = self.configuration
        state.scared_timer = self.scared_timer
        state.num_carrying = self.num_carrying
        state.num_returned = self.num_returned
        if self.is_pacman: # Sensor data for Pacman
            state.last_action = self.last_action
            state.has_immobilizer = self.has_immobilizer
            state.has_gold = self.has_gold
            state.bumped = self.bumped
            state.scream = self.scream
            state.found_immobile = self.found_immobile

        return state

    def get_position(self):
        """
        Get position
        """
        if self.configuration is None:
            return None
        return self.configuration.get_position()

    def get_direction(self):
        """
        get direction
        """
        return self.configuration.get_direction()

    def get_sensors(self, state_data):
        """
        Get sensors for this configuration (when STOP)
        """
        if (self.last_action != Directions.STOP):
            return None # only sense when stopped

        sensors = []

        if self.is_pacman:
            if self.bumped:
                sensors.append("Bump")
                #self.bumped = False - wait to clear on new action choice
            if self.scream:
                sensors.append("Scream")
                if self.scared_timer > 98:
                    # Scream a couple of samples
                    self.scared_timer -= 1
                else:
                    self.scream = False

            ix, iy = nearest_point(self.get_position())
            if state_data.food[ix][iy]:
                sensors.append("Glitter")
            # Check the neighbors
            stench = False
            breezy = False
            for dx in range(-1, 2, 1):
                for dy in range(-1, 2, 1):
                    if dx*dy == 0:
                        # Do not sense diagonals
                        xx = ix+dx
                        yy = iy+dy

                        # Check for Wumpus
                        for wumpus in state_data.agent_states[1:]:
                            xw, yw = wumpus.get_position()
                            if (abs(xw-xx) < 1e-6) and (abs(yw-yy) < 1e-6):
                                stench = True

                        for xp, yp in state_data.capsules:
                            if (abs(xp-xx) < 1e-6) and (abs(yp-yy) < 1e-6):
                                breezy = True
            if breezy:
                sensors.append("Breezy")

            if stench:
                sensors.append("Stench")

        #print "Sensed: ", sensors
        return sensors

class Grid:
    """
    A 2-dimensional array of objects backed by a list of lists.  Data is accessed
    via grid[x][y] where (x, y) are positions on a Pacman map with x horizontal,
    y vertical and the origin (0,0) in the bottom left corner.

    The __str__ method constructs an output that is oriented like a pacman board.
    """
    def __init__(self, width, height,
                 initialValue=False,
                 bit_representation=None):
        if initialValue not in [False, True]:
            raise Exception('Grids can only contain booleans')
        self.CELLS_PER_INT = 30

        self.width = width
        self.height = height
        self.data = [[initialValue for y in range(height)] for x in range(width)]
        if bit_representation:
            self._unpack_bits(bit_representation)

    def __getitem__(self, i):
        """
        get data item
        """
        return self.data[i]

    def __setitem__(self, key, item):
        """
        set data item
        """
        self.data[key] = item

    def __str__(self):
        """
        string output
        """
        out = [[str(self.data[x][y])[0] for x in range(self.width)] for y in range(self.height)]
        out.reverse()
        return '\n'.join([''.join(x) for x in out])

    def __eq__(self, other):
        """
        equality check
        """
        if other is None:
            return False
        return self.data == other.data

    def __hash__(self):
        """
        Hashing function
        """
        # return hash(str(self))
        base = 1
        h = 0
        for l in self.data:
            for i in l:
                if i:
                    h += base
                base *= 2
        return hash(h)

    def copy(self):
        """
        Copy grid
        """
        g = Grid(self.width, self.height)
        g.data = [x[:] for x in self.data]
        return g

    def deepCopy(self):
        """
        Deep copy grid
        """
        return self.copy()

    def shallowCopy(self):
        """
        Shallow copy grid data
        """
        g = Grid(self.width, self.height)
        g.data = self.data
        return g

    def count(self, item=True):
        """
        Count items
        """
        return sum([x.count(item) for x in self.data])

    def asList(self, key=True):
        """
        Return grid as list
        """
        list = []
        for x in range(self.width):
            for y in range(self.height):
                if self[x][y] == key:
                    list.append((x, y))
        return list

    def pack_bits(self):
        """
        Returns an efficient int list representation

        (width, height, bitPackedInts...)
        """
        bits = [self.width, self.height]
        currentInt = 0
        for i in range(self.height * self.width):
            bit = self.CELLS_PER_INT - (i % self.CELLS_PER_INT) - 1
            x, y = self._cell_index_to_position(i)
            if self[x][y]:
                currentInt += 2 ** bit
            if (i + 1) % self.CELLS_PER_INT == 0:
                bits.append(currentInt)
                currentInt = 0
        bits.append(currentInt)
        return tuple(bits)

    def _cell_index_to_position(self, index):
        """
        linear index to x, y position
        """
        x = index / self.height
        y = index % self.height
        return x, y

    def _unpack_bits(self, bits):
        """
        Fills in data from a bit-level representation
        """
        cell = 0
        for packed in bits:
            for bit in self._unpack_int(packed, self.CELLS_PER_INT):
                if cell == self.width * self.height: break
                x, y = self._cell_index_to_position(cell)
                self[x][y] = bit
                cell += 1

    def _unpack_int(self, packed, size):
        """
        Unpack integer data
        """
        bools = []
        if packed < 0:
            raise ValueError("must be a positive integer")
        for i in range(size):
            n = 2 ** (self.CELLS_PER_INT - i - 1)
            if packed >= n:
                bools.append(True)
                packed -= n
            else:
                bools.append(False)
        return bools

def reconstitute_grid(bitRep):
    """
    Reconstitue grid data
    """
    if type(bitRep) is not type((1, 2)):
        return bitRep
    width, height = bitRep[:2]
    return Grid(width, height, bit_representation=bitRep[2:])

####################################
# Parts you shouldn't have to read #
####################################

class Actions:
    """
    A collection of static methods for manipulating move actions.
    """

    FWD = 'Forward'
    LEFT = 'Left'
    RIGHT= 'Right'
    STOP = 'Stop'
    GRAB = 'Grab'
    SHOOT= 'Shoot'


    # Direction vectors
    _directions = {Directions.NORTH: (0, 1),
                   Directions.SOUTH: (0,-1),
                   Directions.EAST:  (1, 0),
                   Directions.WEST:  (-1, 0),
                   Directions.STOP:  (0, 0)}

    _rotate_actions = {Directions.NORTH: {Directions.SOUTH: RIGHT, Directions.WEST:  LEFT, Directions.EAST:  RIGHT },
                       Directions.SOUTH: {Directions.NORTH: RIGHT, Directions.WEST:  RIGHT, Directions.EAST:  LEFT },
                       Directions.EAST:  {Directions.NORTH: LEFT, Directions.WEST:  RIGHT, Directions.SOUTH: RIGHT },
                       Directions.WEST:  {Directions.NORTH: RIGHT, Directions.SOUTH: LEFT, Directions.EAST:  RIGHT } }

    _rotate_successors = {Directions.NORTH: {RIGHT: Directions.EAST, LEFT: Directions.WEST  },
                          Directions.SOUTH: {RIGHT: Directions.WEST, LEFT: Directions.EAST  },
                          Directions.EAST:  {RIGHT:Directions.SOUTH, LEFT: Directions.NORTH },
                          Directions.WEST:  {RIGHT:Directions.NORTH, LEFT: Directions.SOUTH } }

    _directionsAsList = list(_directions.items())

    TOLERANCE = .001

    @staticmethod
    def get_rotation_action(current, desired):

        if (current == desired):
            print(" Invalid rotation - current= desired ",current)
            return Actions.STOP

        current_dict = Actions._rotate_actions[current]
        return current_dict[desired]

    @staticmethod
    def get_rotation_successor(current, action):

        if action not in (Actions.RIGHT, Actions.LEFT):
            print(" Invalid rotation action -  ",action)
            return current

        current_dict = Actions._rotate_successors[current]
        #print " current ",current,"   succ dict",current_dict, "action=",action
        return current_dict[action]


    @staticmethod
    def vector_to_direction(vector):
        dx, dy = vector
        if dy > 0:
            return Directions.NORTH
        if dy < 0:
            return Directions.SOUTH
        if dx < 0:
            return Directions.WEST
        if dx > 0:
            return Directions.EAST
        return Directions.STOP

    @staticmethod
    def direction_to_vector(direction, speed = 1.0):
        dx, dy = Actions._directions[direction]
        return (dx * speed, dy * speed)

    @staticmethod
    def get_possible_directions(config, walls):
        possible = []
        x, y = config.pos
        x_int, y_int = int(x + 0.5), int(y + 0.5)

        # In between grid points, all agents must continue straight
        if (abs(x - x_int) + abs(y - y_int)  > Actions.TOLERANCE):
            return [config.get_direction()]

        for dir, vec in Actions._directionsAsList:
            dx, dy = vec
            next_y = y_int + dy
            next_x = x_int + dx
            if not walls[next_x][next_y]: possible.append(dir)

        return possible

    @staticmethod
    def get_possible_actions(config, walls):

        x, y = config.pos
        x_int, y_int = int(x + 0.5), int(y + 0.5)

        # In between grid points, all agents must continue straight without stopping
        if (abs(x - x_int) + abs(y - y_int)  > Actions.TOLERANCE):
            return [Actions.FWD]

        # All actions are allowed at grid points, but may not be relevant and might cause you to bump a wall
        possible = [Actions.FWD, Actions.LEFT, Actions.RIGHT, Actions.STOP, Actions.GRAB, Actions.SHOOT]
        return possible

    @staticmethod
    def get_legal_neighbors(position, walls):
        x, y = position
        x_int, y_int = int(x + 0.5), int(y + 0.5)
        neighbors = []
        for dir, vec in Actions._directionsAsList:
            dx, dy = vec
            next_x = x_int + dx
            if next_x < 0 or next_x == walls.width: continue
            next_y = y_int + dy
            if next_y < 0 or next_y == walls.height: continue
            if not walls[next_x][next_y]: neighbors.append((next_x, next_y))
        return neighbors

    @staticmethod
    def get_successor(position, action):
        dx, dy = Actions.direction_to_vector(action)
        x, y = position
        return (x + dx, y + dy)

class GameStateData:
    """

    """
    def __init__(self, prevState = None):
        """
        Generates a new data packet by copying information from its predecessor.
        """
        if prevState is not None:
            self.food = prevState.food.shallowCopy()
            self.capsules = prevState.capsules[:]
            self.agent_states = self.copy_agent_states(prevState.agent_states)
            self.layout = prevState.layout
            self._eaten = prevState._eaten
            self.score = prevState.score

        self._food_eaten = None
        self._food_added = None
        self._capsule_eaten = None
        self._agent_moved = None
        self._lose = False
        self._win = False
        self.score_change = 0

    def deepCopy(self):
        state = GameStateData(self)
        state.food = self.food.deepCopy()
        state.layout = self.layout.deepCopy()
        state._agent_moved = self._agent_moved
        state._food_eaten = self._food_eaten
        state._food_added = self._food_added
        state._capsule_eaten = self._capsule_eaten
        return state

    def copy_agent_states(self, agent_states):
        copied_states = []
        for agent_state in agent_states:
            copied_states.append(agent_state.copy())
        return copied_states

    def __eq__(self, other):
        """
        Allows two states to be compared.
        """
        if other is None:
            return False
        # TODO Check for type of other
        if not self.agent_states == other.agent_states: return False
        if not self.food == other.food: return False
        if not self.capsules == other.capsules: return False
        if not self.score == other.score: return False
        return True

    def __hash__(self):
        """
        Allows states to be keys of dictionaries.
        """
        for i, state in enumerate(self.agent_states):
            try:
                int(hash(state))
            except TypeError as e:
                print(e)
                #hash(state)
        return int((hash(tuple(self.agent_states)) + 13*hash(self.food) + 113* hash(tuple(self.capsules)) + 7 * hash(self.score)) % 1048575)

    def __str__(self):
        width, height = self.layout.width, self.layout.height
        map = Grid(width, height)
        if type(self.food) == type((1, 2)):
            self.food = reconstitute_grid(self.food)
        for x in range(width):
            for y in range(height):
                food, walls = self.food, self.layout.walls
                map[x][y] = self._food_wall_str(food[x][y], walls[x][y])

        for agent_state in self.agent_states:
            if agent_state is None:
                continue
            if agent_state.configuration is None:
                continue
            x, y = [int(i) for i in nearest_point(agent_state.configuration.pos)]
            agent_dir = agent_state.configuration.direction
            if agent_state.is_pacman:
                map[x][y] = self._pac_str(agent_dir)
            else:
                map[x][y] = self._ghost_str(agent_dir)

        for x, y in self.capsules:
            map[x][y] = 'o'

        return str(map) + ("\nScore: %d\n" % self.score)

    def _food_wall_str(self, has_food, has_wall):
        if has_food:
            return '.'
        elif has_wall:
            return '%'
        else:
            return ' '

    def _pac_str(self, dir):
        if dir == Directions.NORTH:
            return 'v'
        if dir == Directions.SOUTH:
            return '^'
        if dir == Directions.WEST:
            return '>'
        return '<'

    def _ghost_str(self, dir):
        return 'G'
        if dir == Directions.NORTH:
            return 'M'
        if dir == Directions.SOUTH:
            return 'W'
        if dir == Directions.WEST:
            return '3'
        return 'E'

    def initialize(self, layout, num_ghost_agents):
        """
        Creates an initial game state from a layout array (see layout.py).
        """
        self.food = layout.food.copy()
        #self.capsules = []
        self.capsules = layout.capsules[:]
        self.layout = layout
        self.score = 0
        self.score_change = 0

        self.agent_states = []
        num_ghosts = 0
        for is_pacman, pos in layout.agentPositions:
            if not is_pacman:
                if num_ghosts == num_ghost_agents:
                    continue # Max ghosts reached already
                else:
                    num_ghosts += 1
            self.agent_states.append(AgentState(Configuration(pos, Directions.EAST), is_pacman))
        self._eaten = [False for a in self.agent_states]

try:
    import boinc
    _BOINC_ENABLED = True
except:
    _BOINC_ENABLED = False

class Game:
    """
    The Game manages the control flow, soliciting actions from agents.
    """

    def __init__(self, agents, display, rules,
                 starting_index=0, mute_agents=False,
                 catch_exceptions=False):
        self.agent_crashed = False
        self.agents = agents
        self.display = display
        self.rules = rules
        self.starting_index = starting_index
        self.game_over = False
        self.mute_agents = mute_agents
        self.catch_exceptions = catch_exceptions
        self.move_history = []
        self.total_agent_times = [0 for agent in agents]
        self.total_agent_time_warnings = [0 for agent in agents]
        self.agent_timeout = False
        self.state = None

        import io
        self.agent_output = [io.StringIO() for agent in agents]

    def get_progress(self):
        if self.game_over:
            return 1.0
        else:
            return self.rules.get_progress(self)

    def _agent_crash(self, agent_index, quiet=False):
        "Helper method for handling agent crashes"
        if not quiet: traceback.print_exc()
        self.game_over = True
        self.agent_crashed = True
        self.rules.agent_crash(self, agent_index)

    OLD_STDOUT = None
    OLD_STDERR = None

    def mute(self, agent_index):
        if not self.mute_agents: return
        global OLD_STDOUT, OLD_STDERR
        import io
        OLD_STDOUT = sys.stdout
        OLD_STDERR = sys.stderr
        sys.stdout = self.agent_output[agent_index]
        sys.stderr = self.agent_output[agent_index]

    def unmute(self):
        if not self.mute_agents: return
        global OLD_STDOUT, OLD_STDERR
        # Revert stdout/stderr to originals
        sys.stdout = OLD_STDOUT
        sys.stderr = OLD_STDERR


    def run(self):
        """
        Main control loop for game play.
        """
        self.display.initialize(self.state.data)
        self.num_moves = 0

        ###self.display.initialize(self.state.makeObservation(1).data)
        # inform learning agents of the game start
        for i in range(len(self.agents)):
            agent = self.agents[i]
            if not agent:
                self.mute(i)
                # this is a null agent, meaning it failed to load
                # the other team wins
                print("Agent %d failed to load" % i, file=sys.stderr)
                self.unmute()
                self._agent_crash(i, quiet=True)
                return
            if ("registerInitialState" in dir(agent)):
                self.mute(i)
                if self.catch_exceptions:
                    try:
                        timed_func = TimeoutFunction(agent.registerInitialState, int(self.rules.getMaxStartupTime(i)))
                        try:
                            start_time = time.time()
                            timed_func(self.state.deepCopy())
                            time_taken = time.time() - start_time
                            self.total_agent_times[i] += time_taken
                        except TimeoutFunctionException:
                            print("Agent %d ran out of time on startup!" % i, file=sys.stderr)
                            self.unmute()
                            self.agent_timeout = True
                            self._agent_crash(i, quiet=True)
                            return
                    except Exception as data:
                        self._agent_crash(i, quiet=False)
                        self.unmute()
                        return
                else:
                    agent.registerInitialState(self.state.deepCopy())
                ## TODO: could this exceed the total time
                self.unmute()

        agent_index = self.starting_index
        num_agents = len(self.agents)

        while not self.game_over:
            # Fetch the next agent
            agent = self.agents[agent_index]
            move_time = 0
            skip_action = False
            # Generate an observation of the state
            if 'observationFunction' in dir(agent):
                self.mute(agent_index)
                if self.catch_exceptions:
                    try:
                        timed_func = TimeoutFunction(agent.observationFunction, int(self.rules.getMoveTimeout(agent_index)))
                        try:
                            start_time = time.time()
                            observation = timed_func(self.state.deepCopy())
                        except TimeoutFunctionException:
                            skip_action = True
                        move_time += time.time() - start_time
                        self.unmute()
                    except Exception as data:
                        self._agent_crash(agent_index, quiet=False)
                        self.unmute()
                        return
                else:
                    observation = agent.observationFunction(self.state.deepCopy())
                self.unmute()
            else:
                observation = self.state.deepCopy()

            # Solicit an action
            action = None
            self.mute(agent_index)
            if self.catch_exceptions:
                try:
                    timed_func = TimeoutFunction(agent.get_action, int(self.rules.getMoveTimeout(agent_index)) - int(move_time))
                    try:
                        start_time = time.time()
                        if skip_action:
                            raise TimeoutFunctionException()
                        action = timed_func(observation)
                    except TimeoutFunctionException:
                        print("Agent %d timed out on a single move!" % agent_index, file=sys.stderr)
                        self.agent_timeout = True
                        self._agent_crash(agent_index, quiet=True)
                        self.unmute()
                        return

                    move_time += time.time() - start_time

                    if move_time > self.rules.getMoveWarningTime(agent_index):
                        self.total_agent_time_warnings[agent_index] += 1
                        print("Agent %d took too long to make a move! This is warning %d" % (agent_index, self.total_agent_time_warnings[agent_index]), file=sys.stderr)
                        if self.total_agent_time_warnings[agent_index] > self.rules.getMaxTimeWarnings(agent_index):
                            print("Agent %d exceeded the maximum number of warnings: %d" % (agent_index, self.total_agent_time_warnings[agent_index]), file=sys.stderr)
                            self.agent_timeout = True
                            self._agent_crash(agent_index, quiet=True)
                            self.unmute()
                            return

                    self.total_agent_times[agent_index] += move_time
                    #print "Agent: %d, time: %f, total: %f" % (agent_index, move_time, self.total_agent_times[agent_index])
                    if self.total_agent_times[agent_index] > self.rules.getMaxTotalTime(agent_index):
                        print("Agent %d ran out of time! (time: %1.2f)" % (agent_index, self.total_agent_times[agent_index]), file=sys.stderr)
                        self.agent_timeout = True
                        self._agent_crash(agent_index, quiet=True)
                        self.unmute()
                        return
                    self.unmute()
                except Exception as data:
                    self._agent_crash(agent_index)
                    self.unmute()
                    return
            else:
                action = agent.get_action(observation)
            self.unmute()

            # Execute the action
            self.move_history.append((agent_index, action))
            if self.catch_exceptions:
                try:
                    self.state = self.state.generate_successor(agent_index, action)
                except Exception as data:
                    self.mute(agent_index)
                    self._agent_crash(agent_index)
                    self.unmute()
                    return
            else:
                self.state = self.state.generate_successor(agent_index, action)

            # Change the display
            self.display.update(self.state.data)
            ###idx = agent_index - agent_index % 2 + 1
            ###self.display.update(self.state.makeObservation(idx).data)

            # Allow for game specific conditions (winning, losing, etc.)
            self.rules.process(self.state, self)
            # Track progress
            if agent_index == num_agents + 1:
                self.num_moves += 1
            # Next agent
            agent_index = (agent_index + 1) % num_agents

            if _BOINC_ENABLED:
                boinc.set_fraction_done(self.get_progress())

        # inform a learning agent of the game result
        for agent_index, agent in enumerate(self.agents):
            if "final" in dir(agent):
                try:
                    self.mute(agent_index)
                    agent.final(self.state)
                    self.unmute()
                except Exception as data:
                    if not self.catch_exceptions:
                        raise data
                    self._agent_crash(agent_index)
                    self.unmute()
                    return

        print(str(self.state))
        self.display.finish()
