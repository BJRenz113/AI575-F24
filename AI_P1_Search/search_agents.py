"""
search_agents.py
---------------
Licensing Information:  You are free to use or extend these projects for
educational purposes provided that (1) you do not distribute or publish
solutions, (2) you retain this notice, and (3) you provide clear
attribution to UC Berkeley, including a link to http://ai.berkeley.edu.

Attribution Information: The Pacman AI projects were developed at UC Berkeley.
The core projects and autograders were primarily created by John DeNero
(denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
Student side autograding was added by Brad Miller, Nick Hay, and
Pieter Abbeel (pabbeel@cs.berkeley.edu).

This file contains all of the agents that can be selected to control Pacman.  To
select an agent, use the '-p' option when running pacman.py.  Arguments can be
passed to your agent using '-a'.  For example, to load a SearchAgent that uses
depth first search (dfs), run the following command:

> python pacman.py -p SearchAgent -a fn=depth_first_search

Commands to invoke other search strategies can be found in the project
description.

Please only change the parts of the file you are asked to.  Look for the lines
that say:

    *** YOUR CODE HERE ***

The parts you fill in start about 3/4 of the way down.  Follow the project
description for details.

Good luck and happy searching!
"""

import time

import search
import util
from game import Actions
from game import Agent
from game import Directions


class GoWestAgent(Agent):
    """An agent that goes West until it can't."""

    def get_action(self, state):
        """The agent receives a GameState (defined in pacman.py)."""
        if Directions.WEST in state.get_legal_pacman_actions():
            return Directions.WEST
        return Directions.STOP


#######################################################
# This portion is written for you, but will only work #
#       after you fill in parts of search.py          #
#######################################################

class SearchAgent(Agent):
    """
    This very general search agent finds a path using a supplied search
    algorithm for a supplied search problem, then returns actions to follow that
    path.

    As a default, this agent runs DFS on a PositionSearchProblem to find
    location (1,1)

    Options for fn include:
      depth_first_search or dfs
      breadth_first_search or bfs


    Note: You should NOT change any code in SearchAgent
    """

    def __init__(self,
                 fn='depth_first_search',
                 prob='PositionSearchProblem',
                 heuristic='null_heuristic'):
        # Warning: some advanced Python magic is employed below to
        # find the right functions and problems

        # Get the search function from the name and heuristic
        super().__init__()
        self.action_index = 0
        if fn not in dir(search):
            raise AttributeError(fn + ' is not a search function in search.py.')
        func = getattr(search, fn)
        if 'heuristic' not in func.__code__.co_varnames:
            print(('[SearchAgent] using function ' + fn))
            self.search_function = func
        else:
            if heuristic in list(globals().keys()):
                heur = globals()[heuristic]
            elif heuristic in dir(search):
                heur = getattr(search, heuristic)
            else:
                raise AttributeError(heuristic +
                                     ' is not a function in search_agents.py or search.py.')
            print(('[SearchAgent] using function %s and heuristic %s' % (fn, heuristic)))
            # Note: this bit of Python trickery combines the search algorithm and the heuristic
            self.search_function = lambda x: func(x, heuristic=heur)

        # Get the search problem type from the name
        if prob not in list(globals().keys()) or not prob.endswith('Problem'):
            raise AttributeError(prob + ' is not a search problem type in SearchAgents.py.')
        self.search_type = globals()[prob]
        self.actions = None
        print(('[SearchAgent] using problem type ' + prob))

    def register_initial_state(self, state):
        """
        This is the first time that the agent sees the layout of the game
        board. Here, we choose a path to the goal. In this phase, the agent
        should compute the path to the goal and store it in a local variable.
        All of the work is done in this method!

        state: a GameState this_ojb (pacman.py)
        """
        if self.search_function is None:
            raise Exception('No search function provided for SearchAgent')
        start_time = time.time()
        problem = self.search_type(state)  # Makes a new search problem
        self.actions = self.search_function(problem)  # Find a path
        total_cost = problem.get_cost_of_actions(self.actions)
        print(('Path found with total cost of %d in %.1f seconds'
               % (total_cost, time.time() - start_time)))
        if '_expanded' in dir(problem):
            print(f'Search nodes expanded: {problem._expanded}')

    def get_action(self, state):
        """
        Returns the next action in the path chosen earlier (in
        register_initial_state).  Return Directions.STOP if there is no further
        action to take.

        state: a GameState this_ojb (pacman.py)
        """
        # if 'action_index' not in direction(self):
        #     self.action_index = 0

        i = self.action_index
        self.action_index += 1
        if i < len(self.actions):
            return self.actions[i]

        return Directions.STOP


class PositionSearchProblem(search.SearchProblem):
    """
    A search problem defines the state space, start state, goal test, successor
    function and cost function.  This search problem can be used to find paths
    to a particular point on the pacman board.

    The state space consists of (x,y) positions in a pacman game.

    Note: this search problem is fully specified; you should NOT change it.
    """

    def __init__(self,
                 game_state,
                 cost_fn=lambda x: 1,
                 goal=(1, 1),
                 start=None,
                 warn=True,
                 visualize=True):
        """
        Stores the start and goal.

        game_state: A GameState this_ojb (pacman.py)
        costFn: A function from a search state (tuple) to a non-negative number
        goal: A position in the game_state
        """
        self.walls = game_state.get_walls()
        self.start_state = game_state.get_pacman_position()
        if start is not None:
            self.start_state = start
        self.goal = goal
        self.cost_fn = cost_fn
        self.visualize = visualize
        if warn and (game_state.get_num_food() != 1 or not game_state.has_food(*goal)):
            print('Warning: this does not look like a regular search maze')

        # For display purposes
        self._visited, self._visitedlist, self._expanded = {}, [], 0  # DO NOT CHANGE

    def get_start_state(self):
        return self.start_state

    def is_goal_state(self, state):
        is_goal = state == self.goal

        # For display purposes only
        if is_goal and self.visualize:
            self._visitedlist.append(state)
            import __main__
            if '_display' in dir(__main__):
                if 'draw_expanded_cells' in dir(__main__._display):  # @UndefinedVariable
                    __main__._display.draw_expanded_cells(self._visitedlist)  # @UndefinedVariable

        return is_goal

    def get_successors(self, state):
        """
        Returns successor states, the actions they require, and a cost of 1.

         As noted in search.py:
             For a given state, this should return a list of triples,
         (successor, action, stepCost), where 'successor' is a
         successor to the current state, 'action' is the action
         required to get there, and 'stepCost' is the incremental
         cost of expanding to that successor
        """

        successors = []
        for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            x, y = state
            dx, dy = Actions.direction_to_vector(action)
            next_x, next_y = int(x + dx), int(y + dy)
            if not self.walls[next_x][next_y]:
                next_state = (next_x, next_y)
                cost = self.cost_fn(next_state)
                successors.append((next_state, action, cost))

        # Bookkeeping for display purposes
        self._expanded += 1  # DO NOT CHANGE
        if state not in self._visited:
            self._visited[state] = True
            self._visitedlist.append(state)

        return successors

    def get_cost_of_actions(self, actions):
        """
        Returns the cost of a particular sequence of actions. If those actions
        include an illegal move, return 999999.
        """
        if actions is None:
            return 999999
        x, y = self.get_start_state()
        cost = 0
        for action in actions:
            # Check figure out the next state and see whether its' legal
            dx, dy = Actions.direction_to_vector(action)
            x, y = int(x + dx), int(y + dy)
            if self.walls[x][y]:
                return 999999
            cost += self.cost_fn((x, y))
        return cost


class StayEastSearchAgent(SearchAgent):
    """
    An agent for position search with a cost function that penalizes being in
    positions on the West side of the board.

    The cost function for stepping into a position (x,y) is 1/2^x.
    """

    def __init__(self):
        super().__init__()
        self.search_function = search.uniform_cost_search
        self.action_index = 0
        cost_fn = lambda pos: .5 ** pos[0]
        self.search_type = lambda state: PositionSearchProblem(state, cost_fn, (1, 1), None, False)


class StayWestSearchAgent(SearchAgent):
    """
    An agent for position search with a cost function that penalizes being in
    positions on the East side of the board.

    The cost function for stepping into a position (x,y) is 2^x.
    """

    def __init__(self):
        super().__init__()
        self.search_function = search.uniform_cost_search
        self.action_index = 0
        cost_fn = lambda pos: 2 ** pos[0]
        self.search_type = lambda state: PositionSearchProblem(state, cost_fn)


def manhattan_heuristic(position, problem, info=None):
    """The Manhattan distance heuristic for a PositionSearchProblem"""
    xy1 = position
    xy2 = problem.goal
    return abs(xy1[0] - xy2[0]) + abs(xy1[1] - xy2[1])


def euclidean_heuristic(position, problem, info=None):
    """The Euclidean distance heuristic for a PositionSearchProblem"""
    xy1 = position
    xy2 = problem.goal
    return ((xy1[0] - xy2[0]) ** 2 + (xy1[1] - xy2[1]) ** 2) ** 0.5


#####################################################
# This portion is incomplete.  Time to write code!  #
#####################################################

class CornersProblem(search.SearchProblem):
    """
    This search problem finds paths through all four corners of a layout.

    You must select a suitable state space and successor function
    """

    def __init__(self, starting_game_state):
        """
        Stores the walls, pacman's starting position and corners.
        """
        self.walls = starting_game_state.get_walls()
        self.starting_position = starting_game_state.get_pacman_position()
        top, right = self.walls.height - 2, self.walls.width - 2
        self.corners = ((1, 1), (1, top), (right, 1), (right, top))
        for corner in self.corners:
            if not starting_game_state.has_food(*corner):
                print('Warning: no food in corner ' + str(corner))
        self._expanded = 0  # DO NOT CHANGE; Number of search nodes expanded

    def get_start_state(self):
        """
        Returns the start state (in your state space, not the full Pacman state
        space)
        """

        # *** YOUR CODE HERE ***
        return (self.starting_position, (False, False, False, False))

    def is_goal_state(self, state):
        """
        Returns whether this search state is a goal state of the problem.
        """

        # *** YOUR CODE HERE ***

        return all(state[1]) #indicates full visitation

    def get_successors(self, state):
        """
        Returns successor states, the actions they require, and a cost of 1.

         As noted in search.py:
            For a given state, this should return a list of triples, (successor,
            action, stepCost), where 'successor' is a successor to the current
            state, 'action' is the action required to get there, and 'stepCost'
            is the incremental cost of expanding to that successor
        """

        successors = []
        x,y = state[0]
        visited = state[1]

        for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            dx, dy = Actions.direction_to_vector(action)
            xplus, yplus = int(x+dx), int(y+dy)

            if not self.walls[xplus][yplus]:
                recent = list(visited)
                if (xplus, yplus) in self.corners:

                    i = self.corners.index((xplus, yplus))
                    recent[i] = True
                successors.append((((xplus,yplus), tuple(recent)), action, 1))

        # DO NOT CHANGE BELOW
        self._expanded += 1
        return successors

    def get_cost_of_actions(self, actions):
        """
        Returns the cost of a particular sequence of actions.  If those actions
        include an illegal move, return 999999.  This is implemented for you.
        """
        if actions is None:
            return 999999

        x, y = self.starting_position

        for action in actions:
            dx, dy = Actions.direction_to_vector(action)
            x, y = int(x + dx), int(y + dy)
            if self.walls[x][y]:
                return 999999

        return len(actions)


def corners_heuristic(state, problem):
    """
    A heuristic for the CornersProblem that you defined.

      state:   The current search state
               (a data structure you chose in your search problem)

      problem: The CornersProblem instance for this layout.

    This function should always return a number that is a lower bound on the
    shortest path from the state to a goal of the problem; i.e.  it should be
    admissible (as well as consistent).
    """

    corners = problem.corners  # These are the corner coordinates
    walls = problem.walls  #unused but given
    #manhattan distances ignores walls

    position, visited = state
    unvisited = [corners[i] for i in range(4) if not visited[i]]

    if not unvisited:
        return 0

    curr = position
    total_dis = 0

    while unvisited:
        distance =[(util.manhattan_distance(curr, corner), corner) for corner in unvisited] #looking for min to next corner
        min_dis, nearcorner = min(distance)
        total_dis += min_dis
        curr = nearcorner
        unvisited.remove(nearcorner)
    return total_dis



class AStarCornersAgent(SearchAgent):
    """A SearchAgent for FoodSearchProblem using A* and your food_heuristic"""

    def __init__(self):
        super().__init__()
        self.search_function = lambda prob: search.a_star_search(prob, corners_heuristic)
        self.search_type = CornersProblem


class FoodSearchProblem:
    """
    A search problem associated with finding the a path that collects all of the
    food (dots) in a Pacman game.

    A search state in this problem is a tuple ( pacman_position, food_grid ) where
      pacman_position: a tuple (x,y) of integers specifying Pacman's position
      food_grid:       a Grid (see game.py) of either True or False, specifying remaining food
    """

    #TODO brennan.miller.20@cnu.edu

    def __init__(self, starting_game_state):
        self.start = (starting_game_state.get_pacman_position(), starting_game_state.get_food())
        self.walls = starting_game_state.get_walls()
        self.starting_game_state = starting_game_state
        self._expanded = 0  # DO NOT CHANGE
        self.heuristic_info = {}  # A dictionary for the heuristic to store information

    def get_start_state(self):
        return self.start

    @staticmethod
    def is_goal_state(state):
        return state[1].count() == 0

    def get_successors(self, state):
        """Returns successor states, the actions they require, and a cost of 1."""
        successors = []
        self._expanded += 1  # DO NOT CHANGE
        for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            x, y = state[0]
            dx, dy = Actions.direction_to_vector(direction)
            next_x, next_y = int(x + dx), int(y + dy)
            if not self.walls[next_x][next_y]:
                next_food = state[1].copy()
                next_food[next_x][next_y] = False
                successors.append((((next_x, next_y), next_food), direction, 1))
        return successors

    def get_cost_of_actions(self, actions):
        """Returns the cost of a particular sequence of actions.  If those actions
        include an illegal move, return 999999"""
        x, y = self.get_start_state()[0]
        cost = 0
        for action in actions:
            # figure out the next state and see whether it's legal
            dx, dy = Actions.direction_to_vector(action)
            x, y = int(x + dx), int(y + dy)
            if self.walls[x][y]:
                return 999999
            cost += 1
        return cost


class AStarFoodSearchAgent(SearchAgent):
    """A SearchAgent for FoodSearchProblem using A* and your food_heuristic"""

    def __init__(self):
        super().__init__()
        self.search_function = lambda prob: search.a_star_search(prob, food_heuristic)
        self.search_type = FoodSearchProblem


def food_heuristic(state, problem):
    """
    Your heuristic for the FoodSearchProblem goes here.

    This heuristic must be consistent to ensure correctness.  First, try to come
    up with an admissible heuristic; almost all admissible heuristics will be
    consistent as well.

    If using A* ever finds a solution that is worse uniform cost search finds,
    your heuristic is *not* consistent, and probably not admissible!  On the
    other hand, inadmissible or inconsistent heuristics may find optimal
    solutions, so be careful.

    The state is a tuple ( pacman_position, food_grid ) where food_grid is a Grid
    (see game.py) of either True or False. You can call food_grid.as_list() to get
    a list of food coordinates instead.

    If you want access to info like walls, capsules, etc., you can query the
    problem.  For example, problem.walls gives you a Grid of where the walls
    are.

    If you want to *store* information to be reused in other calls to the
    heuristic, there is a dictionary called problem.heuristic_info that you can
    use. For example, if you only want to count the walls once and store that
    value, try: problem.heuristic_info['wallCount'] = problem.walls.count()
    Subsequent calls to this heuristic can access
    problem.heuristic_info['wallCount']
    """

    position, food_grid = state

    # *** YOUR CODE HERE ***
    food_list = food_grid.as_list()
    if not food_list:
        return 0 #no food

    distance = [util.manhattan_distance(position, food) for food in food_list]
    closest_dist = min(distance)
    maximumdist = 0

    for i in range(len(food_list)): #looking at 2 closest dots and calc dist
        for j in range(i+1, len(food_list)):
            maximumdist = max(maximumdist, util.manhattan_distance(food_list[i], food_list[j]))
    return closest_dist + maximumdist



class ClosestDotSearchAgent(SearchAgent):
    """Search for all food using a sequence of searches"""

    def register_initial_state(self, state):
        self.actions = []
        current_state = state
        while current_state.get_food().count() > 0:
            next_path_segment = self.find_path_to_closest_dot(current_state)  # The missing piece
            self.actions += next_path_segment
            for action in next_path_segment:
                legal = current_state.get_legal_actions()
                if action not in legal:
                    t = (str(action), str(current_state))
                    raise Exception('find_path_to_closest_dot '
                                    'returned an illegal move: %s!\n%s' % t)
                current_state = current_state.generate_successor(0, action)
        self.action_index = 0
        print(f'Path found with cost {len(self.actions)}.')

    def find_path_to_closest_dot(self, game_state):
        """
        Returns a path (a list of actions) to the closest dot, starting from
        game_state.
        """
        problem = AnyFoodSearchProblem(game_state)

        # *** YOUR CODE HERE ***

        return search.breadth_first_search(problem) #shortest path


class AnyFoodSearchProblem(PositionSearchProblem):
    """
    A search problem for finding a path to any food.

    This search problem is just like the PositionSearchProblem, but has a
    different goal test, which you need to fill in below.  The state space and
    successor function do not need to be changed.

    The class definition above, AnyFoodSearchProblem(PositionSearchProblem),
    inherits the methods of the PositionSearchProblem.

    You can use this search problem to help you fill in the find_path_to_closest_dot
    method.
    """

    def __init__(self, game_state):
        """Stores information from the game_state.  You don't need to change this."""
        # Store the food for later reference
        super().__init__(game_state)
        self.food = game_state.get_food()

        # Store info for the PositionSearchProblem (no need to change this)
        self.walls = game_state.get_walls()
        self.start_state = game_state.get_pacman_position()
        self.cost_fn = lambda x: 1
        self._visited, self._visited_list, self._expanded = {}, [], 0  # DO NOT CHANGE

    def is_goal_state(self, state):
        """
        The state is Pacman's position. Fill this in with a goal test that will
        complete the problem definition.
        """

        x, y = state

        # *** YOUR CODE HERE ***

        return self.food[x][y]


def maze_distance(point1, point2, game_state):
    """
    Returns the maze distance between any two points, using the search functions
    you have already built. The game_state can be any game state -- Pacman's
    position in that state is ignored.

    Example usage: maze_distance( (2,4), (5,6), game_state)

    """
    x1, y1 = point1
    x2, y2 = point2
    walls = game_state.get_walls()
    assert not walls[x1][y1], 'point1 is a wall: ' + str(point1)
    assert not walls[x2][y2], 'point2 is a wall: ' + str(point2)
    prob = PositionSearchProblem(game_state, start=point1, goal=point2, warn=False, visualize=False)
    return len(search.bfs(prob))
