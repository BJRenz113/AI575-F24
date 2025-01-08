"""
grid_world.py
------------
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

import argparse
import random
import sys

import environment
import mdp
import q_learning_agents
import util
import value_iteration_agents


class GridWorld(mdp.MarkovDecisionProcess):
    """
      GridWorld
    """

    def __init__(self, grid):
        # layout
        if isinstance(grid, list):
            grid = make_grid(grid)
        self.grid = grid

        # parameters
        self.living_reward = 0.0
        self.noise = 0.2

    def set_living_reward(self, reward):
        """
        The (negative) reward for exiting "normal" states.

        Note that in the R+N text, this reward is on entering
        a state and therefore is not clearly part of the state's
        future rewards.
        """
        self.living_reward = reward

    def set_noise(self, noise):
        """
        The probability of moving in an unintended direction.
        """
        self.noise = noise

    def get_possible_actions(self, state):
        """
        Returns list of valid actions for 'state'.

        Note that you can request moves into walls and
        that "exit" states transition to the terminal
        state under the special action "done".
        """
        if state == self.grid.terminal_state:
            return ()
        x, y = state
        if isinstance(self.grid[x][y], int):
            return ('exit',)
        return ('north', 'west', 'south', 'east')

    def get_states(self):
        """
        Return list of all states.
        """
        # The true terminal state.
        states = [self.grid.terminal_state]
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                if self.grid[x][y] != '#':
                    state = (x, y)
                    states.append(state)
        return states

    def get_reward(self, state, action, next_state):
        """
        Get reward for state, action, next_state transition.

        Note that the reward depends only on the state being
        departed (as in the R+N book examples, which more or
        less use this convention).
        """
        if state == self.grid.terminal_state:
            return 0.0
        x, y = state
        cell = self.grid[x][y]
        if isinstance(cell, (float, int)):
            return cell
        return self.living_reward

    def get_start_state(self):
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                if self.grid[x][y] == 'S':
                    return x, y
        raise Exception('Grid has no start state')

    def is_terminal(self, state):
        """
        Only the TERMINAL_STATE state is *actually* a terminal state.
        The other "exit" states are technically non-terminals with
        a single action "exit" which leads to the true terminal state.
        This convention is to make the grids line up with the examples
        in the R+N textbook.
        """
        return state == self.grid.terminal_state

    def get_transition_states_and_probs(self, state, action):
        """
        Returns list of (next_state, prob) pairs
        representing the states reachable
        from 'state' by taking 'action' along
        with their transition probabilities.
        """

        if action not in self.get_possible_actions(state):
            raise Exception("Illegal action!")

        if self.is_terminal(state):
            return []

        x, y = state

        if isinstance(self.grid[x][y], (float, int)):
            term_state = self.grid.terminal_state
            return [(term_state, 1.0)]

        successors = []

        north_state = (x, y + 1) if self.__is_allowed(y + 1, x) else state
        west_state = (x - 1, y) if self.__is_allowed(y, x - 1) else state
        south_state = (x, y - 1) if self.__is_allowed(y - 1, x) else state
        east_state = (x + 1, y) if self.__is_allowed(y, x + 1) else state

        if action in ('north', 'south'):
            if action == 'north':
                successors.append((north_state, 1 - self.noise))
            else:
                successors.append((south_state, 1 - self.noise))

            mass_left = self.noise
            successors.append((west_state, mass_left / 2.0))
            successors.append((east_state, mass_left / 2.0))

        if action in ('west', 'east'):
            if action == 'west':
                successors.append((west_state, 1 - self.noise))
            else:
                successors.append((east_state, 1 - self.noise))

            mass_left = self.noise
            successors.append((north_state, mass_left / 2.0))
            successors.append((south_state, mass_left / 2.0))

        successors = self.__aggregate(successors)

        return successors

    def __aggregate(self, states_and_probs):
        counter = util.Counter()
        for state, prob in states_and_probs:
            counter[state] += prob
        new_states_and_probs = []
        for state, prob in list(counter.items()):
            new_states_and_probs.append((state, prob))
        return new_states_and_probs

    def __is_allowed(self, y, x):
        if y < 0 or y >= self.grid.height: return False
        if x < 0 or x >= self.grid.width: return False
        return self.grid[x][y] != '#'


class GridWorldEnvironment(environment.Environment):

    def __init__(self, grid_world_):
        self.grid_world = grid_world_
        self.reset()

    def get_current_state(self):
        return self.state

    def get_possible_actions(self, state):
        return self.grid_world.get_possible_actions(state)

    def do_action(self, action):
        state = self.get_current_state()
        (next_state, reward) = self.get_random_next_state(state, action)
        self.state = next_state
        return next_state, reward

    def get_random_next_state(self, state, action, rand_obj=None):
        rand = -1.0
        if rand_obj is None:
            rand = random.random()
        else:
            rand = rand_obj.random()
        sum = 0.0
        successors = self.grid_world.get_transition_states_and_probs(state, action)
        for next_state, prob in successors:
            sum += prob
            if sum > 1.0:
                raise Exception('Total transition probability more than one; sample failure.')
            if rand < sum:
                reward = self.grid_world.get_reward(state, action, next_state)
                return next_state, reward
        raise Exception('Total transition probability less than one; sample failure.')

    def reset(self):
        self.state = self.grid_world.get_start_state()


class Grid:
    """
    A 2-dimensional array of immutables backed by a list of lists.  Data is accessed
    via grid[x][y] where (x,y) are cartesian coordinates with x horizontal,
    y vertical and the origin (0,0) in the bottom left corner.

    The __str__ method constructs an output that is oriented appropriately.
    """

    def __init__(self, width, height, initial_value=' '):
        self.width = width
        self.height = height
        self.data = [[initial_value for y in range(height)] for x in range(width)]
        self.terminal_state = 'TERMINAL_STATE'

    def __getitem__(self, i):
        return self.data[i]

    def __setitem__(self, key, item):
        self.data[key] = item

    def __eq__(self, other):
        if other is None:
            return False
        return self.data == other.data

    def __hash__(self):
        return hash(self.data)

    def copy(self):
        g = Grid(self.width, self.height)
        g.data = [x[:] for x in self.data]
        return g

    def deep_copy(self):
        return self.copy()

    def shallow_copy(self):
        g = Grid(self.width, self.height)
        g.data = self.data
        return g

    def _get_legacy_text(self):
        t = [[self.data[x][y] for x in range(self.width)] for y in range(self.height)]
        t.reverse()
        return t

    def __str__(self):
        return str(self._get_legacy_text())


def make_grid(grid_string):
    width, height = len(grid_string[0]), len(grid_string)
    grid = Grid(width, height)
    for ybar, line in enumerate(grid_string):
        y = height - ybar - 1
        for x, el in enumerate(line):
            grid[x][y] = el
    return grid


# todo rename these functions in solution and test files so that they can have the required PEP8
#  format
def get_cliff_grid():
    grid = [[' ', ' ', ' ', ' ', ' '],
            ['S', ' ', ' ', ' ', 10],
            [-100, -100, -100, -100, -100]]
    return GridWorld(make_grid(grid))


def get_cliff_grid2():
    grid = [[' ', ' ', ' ', ' ', ' '],
            [8, 'S', ' ', ' ', 10],
            [-100, -100, -100, -100, -100]]
    return GridWorld(grid)


def get_discount_grid():
    grid = [[' ', ' ', ' ', ' ', ' '],
            [' ', '#', ' ', ' ', ' '],
            [' ', '#', 1, '#', 10],
            ['S', ' ', ' ', ' ', ' '],
            [-10, -10, -10, -10, -10]]
    return GridWorld(grid)


def get_bridge_grid():
    grid = [['#', -100, -100, -100, -100, -100, '#'],
            [1, 'S', ' ', ' ', ' ', ' ', 10],
            ['#', -100, -100, -100, -100, -100, '#']]
    return GridWorld(grid)


def get_book_grid():
    grid = [[' ', ' ', ' ', +1],
            [' ', '#', ' ', -1],
            ['S', ' ', ' ', ' ']]
    return GridWorld(grid)


def get_maze_grid():
    grid = [[' ', ' ', ' ', +1],
            ['#', '#', ' ', '#'],
            [' ', '#', ' ', ' '],
            [' ', '#', '#', ' '],
            ['S', ' ', ' ', ' ']]
    return GridWorld(grid)


def getUserAction(state, action_function):
    """
    Get an action from the user (rather than the agent).

    Used for debugging and lecture demos.
    """
    import graphics_utils
    action = None
    while True:
        keys = graphics_utils.wait_for_keys()
        if 'Up' in keys:
            action = 'north'
        if 'Down' in keys:
            action = 'south'
        if 'Left' in keys:
            action = 'west'
        if 'Right' in keys:
            action = 'east'
        if 'q' in keys:
            sys.exit(0)
        if action is None:
            continue
        break
    actions = action_function(state)
    if action not in actions:
        action = actions[0]
    return action


def print_string(x):
    print(x)


def run_episode(agent, environment, discount, decision, display, message, pause, episode):
    return_val = 0
    total_discount = 1.0
    environment.reset()
    if 'start_episode' in dir(agent): agent.start_episode()
    message("BEGINNING EPISODE: " + str(episode) + "\n")
    while True:

        # DISPLAY CURRENT STATE
        state = environment.get_current_state()
        display(state)
        pause()

        # END IF IN A TERMINAL STATE
        actions = environment.get_possible_actions(state)
        if not actions:
            message("EPISODE " + str(episode) + " COMPLETE: RETURN WAS " + str(return_val) + "\n")
            return return_val

        # GET ACTION (USUALLY FROM AGENT)
        action = decision(state)
        if action is None:
            raise Exception('Error: Agent returned None action')

        # EXECUTE ACTION
        next_state, reward = environment.do_action(action)
        message("Started in state: " + str(state) +
                "\nTook action: " + str(action) +
                "\nEnded in state: " + str(next_state) +
                "\nGot reward: " + str(reward) + "\n")
        # UPDATE LEARNER
        if 'observe_transition' in dir(agent):
            agent.observe_transition(state, action, next_state, reward)

        return_val += reward * total_discount
        total_discount *= discount

    if 'stop_episode' in dir(agent):
        agent.stop_episode()


def parse_options():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-d', '--discount', action='store',
                            type=float, dest='discount', default=0.9,
                            help='Discount on future (default %default)')
    arg_parser.add_argument('-r', '--living_reward', action='store',
                            type=float, dest='living_reward', default=0.0,
                            metavar="R",
                            help='Reward for living for a time step (default %default)')
    arg_parser.add_argument('-n', '--noise', action='store',
                            type=float, dest='noise',
                            default=0.2, metavar="P",
                            help='How often action results in unintended direction '
                                 '(default %default)')
    arg_parser.add_argument('-e', '--epsilon', action='store',
                            type=float, dest='epsilon', default=0.3,
                            metavar="E",
                            help='Chance of taking a random action in q-learning '
                                 '(default %default)')
    arg_parser.add_argument('-l', '--learning_rate', action='store',
                            type=float, dest='learning_rate', default=0.5,
                            metavar="P", help='TD learning rate (default %default)')
    arg_parser.add_argument('-i', '--iterations', action='store',
                            type=int, dest='iters', default=10,
                            metavar="K",
                            help='Number of rounds of value iteration (default %default)')
    arg_parser.add_argument('-k', '--episodes', action='store',
                            type=int, dest='episodes', default=1,
                            metavar="K",
                            help='Number of epsiodes of the MDP to run (default %default)')
    arg_parser.add_argument('-g', '--grid', action='store',
                            metavar="G", type=str, dest='grid', default="book_grid",
                            help='Grid to use (case sensitive; options are book_grid, bridge_grid, '
                                 'cliff_grid, maze_grid, default %default)')
    arg_parser.add_argument('-w', '--windowSize', metavar="X", type=int, dest='gridSize',
                            default=150,
                            help='Request a window width of X pixels *per grid cell* (default '
                                 '%default)')
    arg_parser.add_argument('-a', '--agent', action='store', metavar="A",
                            type=str, dest='agent', default="random",
                            help='Agent type (options are \'random\', \'value\' and \'q\', '
                                 'default %default)')
    arg_parser.add_argument('-t', '--text', action='store_true',
                            dest='text_display', default=False,
                            help='Use text-only ASCII display')
    arg_parser.add_argument('-p', '--pause', action='store_true',
                            dest='pause', default=False,
                            help='Pause GUI after each time step when running the MDP')
    arg_parser.add_argument('-q', '--quiet', action='store_true',
                            dest='quiet', default=False,
                            help='Skip display of any learning episodes')
    arg_parser.add_argument('-s', '--speed', action='store', metavar="S", type=float,
                            dest='speed', default=1.0,
                            help='Speed of animation, S > 1.0 is faster, 0.0 < S < 1.0 is slower '
                                 '(default %default)')
    arg_parser.add_argument('-m', '--manual', action='store_true',
                            dest='manual', default=False,
                            help='Manually control agent')
    arg_parser.add_argument('-v', '--valueSteps', action='store_true', default=False,
                            help='Display each step of value iteration')

    args = arg_parser.parse_args()

    if args.manual and args.agent != 'q':
        print('## Disabling Agents in Manual Mode (-m) ##')
        args.agent = None

    # MANAGE CONFLICTS
    if args.text_display or args.quiet:
        # if args.quiet:
        args.pause = False
        # args.manual = False

    if args.manual:
        args.pause = True

    return args


if __name__ == '__main__':

    args = parse_options()

    ###########################
    # GET THE GRIDWORLD
    ###########################

    # investigate how to remove weird self import
    import grid_world

    mdp_function = getattr(grid_world, "get_" + args.grid)
    mdp = mdp_function()
    mdp.set_living_reward(args.living_reward)
    mdp.set_noise(args.noise)
    env = grid_world.GridWorldEnvironment(mdp)

    ###########################
    # GET THE DISPLAY ADAPTER
    ###########################

    import text_grid_world_display

    display = text_grid_world_display.TextGridWorldDisplay(mdp)
    if not args.text_display:
        import graphics_grid_world_display

        display = graphics_grid_world_display.GraphicsGridWorldDisplay(mdp,
                                                                       args.gridSize,
                                                                       args.speed)
    try:
        display.start()
    except KeyboardInterrupt:
        sys.exit(0)

    ###########################
    # GET THE AGENT
    ###########################

    a = None
    if args.agent == 'value':
        a = value_iteration_agents.ValueIterationAgent(mdp, args.discount, args.iters)
    elif args.agent == 'q':
        # env.get_possible_actions, args.discount, args.learning_rate, args.epsilon
        # simulationFn = lambda agent, state: simulation.GridWorldSimulation(agent,state,mdp)
        grid_world_env = GridWorldEnvironment(mdp)
        action_fn = lambda state: mdp.get_possible_actions(state)
        q_learn_opts = {'gamma': args.discount,
                        'alpha': args.learning_rate,
                        'epsilon': args.epsilon,
                        'actionFn': action_fn}
        a = q_learning_agents.QLearningAgent(**q_learn_opts)
    elif args.agent == 'random':
        # # No reason to use the random agent without episodes
        if args.episodes == 0:
            args.episodes = 10


        class RandomAgent:
            def get_action(self, state):
                return random.choice(mdp.get_possible_actions(state))

            def get_value(self, state):
                return 0.0

            def get_q_value(self, state, action):
                return 0.0

            def get_policy(self, state):
                "NOTE: 'random' is a special policy value; don't use it in your code."
                return 'random'

            def update(self, state, action, next_state, reward):
                pass


        a = RandomAgent()
    else:
        if not args.manual:
            raise Exception('Unknown agent type: ' + args.agent)

    ###########################
    # RUN EPISODES
    ###########################
    # DISPLAY Q/V VALUES BEFORE SIMULATION OF EPISODES
    try:
        if not args.manual and args.agent == 'value':
            if args.valueSteps:
                for i in range(args.iters):
                    tempAgent = value_iteration_agents.ValueIterationAgent(mdp, args.discount, i)
                    display.display_values(tempAgent,
                                           message="VALUES AFTER " + str(i) + " ITERATIONS")
                    display.pause()

            display.display_values(a, message="VALUES AFTER " + str(args.iters) + " ITERATIONS")
            display.pause()
            display.display_q_values(a, message="Q-VALUES AFTER " + str(args.iters) + " ITERATIONS")
            display.pause()
    except KeyboardInterrupt:
        sys.exit(0)

    # FIGURE OUT WHAT TO DISPLAY EACH TIME STEP (IF ANYTHING)
    display_callback = lambda x: None
    if not args.quiet:
        if args.manual and args.agent is None:
            display_callback = lambda state: display.display_null_values(state)
        else:
            if args.agent == 'random':
                display_callback = lambda state: display.display_values(a,
                                                                        state,
                                                                        "CURRENT VALUES")
            if args.agent == 'value':
                display_callback = lambda state: display.display_values(a,
                                                                        state,
                                                                        "CURRENT VALUES")
            if args.agent == 'q':
                display_callback = lambda state: display.display_q_values(a,
                                                                          state,
                                                                          "CURRENT Q-VALUES")

    message_callback = lambda x: print_string(x)
    if args.quiet:
        message_callback = lambda x: None

    # FIGURE OUT WHETHER TO WAIT FOR A KEY PRESS AFTER EACH TIME STEP
    pause_callback = lambda: None
    if args.pause:
        pause_callback = lambda: display.pause()

    # FIGURE OUT WHETHER THE USER WANTS MANUAL CONTROL (FOR DEBUGGING AND DEMOS)
    if args.manual:
        decision_callback = lambda state: getUserAction(state, mdp.get_possible_actions)
    else:
        decision_callback = a.get_action

    # RUN EPISODES
    if args.episodes > 0:
        print()
        print("RUNNING", args.episodes, "EPISODES")
        print()
    return_val = 0
    for episode in range(1, args.episodes + 1):
        return_val += run_episode(a, env, args.discount, decision_callback, display_callback,
                                  message_callback, pause_callback, episode)
    if args.episodes > 0:
        print()
        print("AVERAGE RETURNS FROM START STATE: " + str((return_val + 0.0) / args.episodes))
        print()
        print()

    # DISPLAY POST-LEARNING VALUES / Q-VALUES
    if args.agent == 'q' and not args.manual:
        try:
            display.display_q_values(a,
                                     message="Q-VALUES AFTER " + str(args.episodes) + " EPISODES")
            display.pause()
            display.display_values(a, message="VALUES AFTER " + str(args.episodes) + " EPISODES")
            display.pause()
        except KeyboardInterrupt:
            sys.exit(0)
