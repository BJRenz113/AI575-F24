"""
graphics_grid_world_display.py
---------------------------
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

from functools import reduce

import util
from graphics_utils import *

# globals
__screen_width__ = None
__screen_height__ = None

__background_color__ = format_color(0, 0, 0)
__edge_color__ = format_color(1, 1, 1)
__obstacle_color__ = format_color(0.5, 0.5, 0.5)
__text_color__ = format_color(1, 1, 1)
__muted_text_color__ = format_color(0.7, 0.7, 0.7)
__location_color__ = format_color(0, 0, 1)

__window_size__ = -1
__grid_size__ = -1
__grid_height__ = -1
__margin__ = -1


class GraphicsGridWorldDisplay:

    def __init__(self, grid_world, size=120, speed=1.0):
        self.grid_world = grid_world
        self.size = size
        self.speed = speed

    def start(self):
        setup(self.grid_world, size=self.size)

    def pause(self):
        wait_for_keys()

    def display_values(self, agent, current_state=None, message='Agent Values'):
        values = util.Counter()
        policy = {}
        states = self.grid_world.get_states()
        for state in states:
            values[state] = agent.get_value(state)
            policy[state] = agent.get_policy(state)
        draw_values(self.grid_world, values, policy, current_state, message)
        sleep(0.05 / self.speed)

    def display_null_values(self, current_state=None, message=''):
        values = util.Counter()
        # policy = {}
        states = self.grid_world.get_states()
        for state in states:
            values[state] = 0.0
            # policy[state] = agent.get_policy(state)
        draw_null_values(self.grid_world, current_state, '')
        # draw_values(self.grid_world, values, policy, currentState, message)
        sleep(0.05 / self.speed)

    def display_q_values(self, agent, current_state=None, message='Agent Q-Values'):
        q_values = util.Counter()
        states = self.grid_world.get_states()
        for state in states:
            for action in self.grid_world.get_possible_actions(state):
                q_values[(state, action)] = agent.get_q_value(state, action)
        draw_q_values(self.grid_world, q_values, current_state, message)
        sleep(0.05 / self.speed)


def setup(grid_world, title="GridWorld Display", size=120):
    global __grid_size__, __margin__, __screen_width__, __screen_height__, __grid_height__
    grid = grid_world.grid
    __grid_size__ = size
    __grid_height__ = grid.height
    __margin__ = __grid_size__ * 0.75
    screen_width = (grid.width - 1) * __grid_size__ + __margin__ * 2
    screen_height = (grid.height - 0.5) * __grid_size__ + __margin__ * 2

    begin_graphics(screen_width,
                   screen_height,
                   __background_color__, title=title)


def draw_null_values(grid_world, current_state=None, message=''):
    grid = grid_world.grid
    blank()
    for x in range(grid.width):
        for y in range(grid.height):
            state = (x, y)
            grid_type = grid[x][y]
            is_exit = (str(grid_type) != grid_type)
            is_current = (current_state == state)
            if grid_type == '#':
                draw_square(x, y, 0, 0, 0, None, None, True, False, is_current)
            else:
                draw_null_square(grid_world.grid, x, y, False, is_exit, is_current)
    pos = to_screen(((grid.width - 1.0) / 2.0, - 0.8))
    text_on_canvas(pos, __text_color__, message, "Courier", -32, "bold", "c")


def draw_values(grid_world, values, policy, current_state=None, message='State Values'):
    grid = grid_world.grid
    blank()
    value_list = [values[state] for state in grid_world.get_states()] + [0.0]
    min_value = min(value_list)
    max_value = max(value_list)
    for x in range(grid.width):
        for y in range(grid.height):
            state = (x, y)
            grid_type = grid[x][y]
            is_exit = (str(grid_type) != grid_type)
            is_current = (current_state == state)
            if grid_type == '#':
                draw_square(x, y, 0, 0, 0, None, None, True, False, is_current)
            else:
                value = values[state]
                action = None
                if policy is not None and state in policy:
                    action = policy[state]
                    actions = grid_world.get_possible_actions(state)
                if action not in actions and 'exit' in actions:
                    action = 'exit'
                val_string = '%.2f' % value
                draw_square(x, y, value, min_value, max_value, val_string, action, False, is_exit,
                            is_current)
    pos = to_screen(((grid.width - 1.0) / 2.0, - 0.8))
    text_on_canvas(pos, __text_color__, message, "Courier", -32, "bold", "c")


def draw_q_values(grid_world, q_values, current_state=None, message='State-Action Q-Values'):
    grid = grid_world.grid
    blank()
    state_cross_actions = [[(state, action) for action in grid_world.get_possible_actions(state)] for
                           state in grid_world.get_states()]
    q_states = reduce(lambda x, y: x + y, state_cross_actions, [])
    q_value_list = [q_values[(state, action)] for state, action in q_states] + [0.0]
    min_value = min(q_value_list)
    max_value = max(q_value_list)
    for x in range(grid.width):
        for y in range(grid.height):
            state = (x, y)
            grid_type = grid[x][y]
            is_exit = (str(grid_type) != grid_type)
            is_current = (current_state == state)
            actions = grid_world.get_possible_actions(state)
            if not actions:
                actions = [None]
            best_q = max([q_values[(state, action)] for action in actions])
            best_actions = [action for action in actions if q_values[(state, action)] == best_q]

            q = util.Counter()
            val_strings = {}
            for action in actions:
                v = q_values[(state, action)]
                q[action] += v
                val_strings[action] = '%.2f' % v
            if grid_type == '#':
                draw_square(x, y, 0, 0, 0, None, None, True, False, is_current)
            elif is_exit:
                action = 'exit'
                value = q[action]
                val_string = '%.2f' % value
                draw_square(x, y, value, min_value, max_value, val_string, action, False, is_exit,
                            is_current)
            else:
                draw_square_q(x, y, q, min_value, max_value, val_strings, actions, is_current)
    pos = to_screen(((grid.width - 1.0) / 2.0, - 0.8))
    text_on_canvas(pos, __text_color__, message, "Courier", -32, "bold", "c")


def blank():
    clear_screen()


def draw_null_square(grid, x, y, is_obstacle, is_terminal, is_current):
    square_color = get_color(0, -1, 1)

    if is_obstacle:
        square_color = __obstacle_color__

    (screen_x, screen_y) = to_screen((x, y))
    square((screen_x, screen_y),
           0.5 * __grid_size__,
           color=square_color,
           filled=1,
           width=1)

    square((screen_x, screen_y),
           0.5 * __grid_size__,
           color=__edge_color__,
           filled=0,
           width=3)

    if is_terminal and not is_obstacle:
        square((screen_x, screen_y),
               0.4 * __grid_size__,
               color=__edge_color__,
               filled=0,
               width=2)
        text_on_canvas((screen_x, screen_y),
                       __text_color__,
                       str(grid[x][y]),
                       "Courier", -24, "bold", "c")

    text_color = __text_color__

    if not is_obstacle and is_current:
        circle((screen_x, screen_y), 0.1 * __grid_size__, __location_color__,
               fill_color=__location_color__)

    # if not isObstacle:
    #   text( (screen_x, screen_y), text_color, valStr, "Courier", 24, "bold", "c")


def draw_square(x, y, val, min_val, max_val, val_str, action, is_obstacle, is_terminal, is_current):
    square_color = get_color(val, min_val, max_val)

    if is_obstacle:
        square_color = __obstacle_color__

    (screen_x, screen_y) = to_screen((x, y))
    square((screen_x, screen_y),
           0.5 * __grid_size__,
           color=square_color,
           filled=1,
           width=1)
    square((screen_x, screen_y),
           0.5 * __grid_size__,
           color=__edge_color__,
           filled=0,
           width=3)
    if is_terminal and not is_obstacle:
        square((screen_x, screen_y),
               0.4 * __grid_size__,
               color=__edge_color__,
               filled=0,
               width=2)

    if action == 'north':
        polygon([(screen_x, screen_y - 0.45 * __grid_size__),
                 (screen_x + 0.05 * __grid_size__, screen_y - 0.40 * __grid_size__),
                 (screen_x - 0.05 * __grid_size__, screen_y - 0.40 * __grid_size__)],
                __edge_color__, filled=1,
                smoothed=False)
    if action == 'south':
        polygon([(screen_x, screen_y + 0.45 * __grid_size__),
                 (screen_x + 0.05 * __grid_size__, screen_y + 0.40 * __grid_size__),
                 (screen_x - 0.05 * __grid_size__, screen_y + 0.40 * __grid_size__)],
                __edge_color__, filled=1,
                smoothed=False)
    if action == 'west':
        polygon([(screen_x - 0.45 * __grid_size__, screen_y),
                 (screen_x - 0.4 * __grid_size__, screen_y + 0.05 * __grid_size__),
                 (screen_x - 0.4 * __grid_size__, screen_y - 0.05 * __grid_size__)], __edge_color__,
                filled=1,
                smoothed=False)
    if action == 'east':
        polygon([(screen_x + 0.45 * __grid_size__, screen_y),
                 (screen_x + 0.4 * __grid_size__, screen_y + 0.05 * __grid_size__),
                 (screen_x + 0.4 * __grid_size__, screen_y - 0.05 * __grid_size__)], __edge_color__,
                filled=1,
                smoothed=False)

    text_color = __text_color__

    if not is_obstacle and is_current:
        circle((screen_x, screen_y), 0.1 * __grid_size__, outline_color=__location_color__,
               fill_color=__location_color__)

    if not is_obstacle:
        text_on_canvas((screen_x, screen_y), text_color, val_str, "Courier", -30, "bold", "c")


def draw_square_q(x, y, q_vals, min_val, max_val, val_strs, best_actions, is_current):
    (screen_x, screen_y) = to_screen((x, y))

    center = (screen_x, screen_y)
    nw = (screen_x - 0.5 * __grid_size__, screen_y - 0.5 * __grid_size__)
    ne = (screen_x + 0.5 * __grid_size__, screen_y - 0.5 * __grid_size__)
    se = (screen_x + 0.5 * __grid_size__, screen_y + 0.5 * __grid_size__)
    sw = (screen_x - 0.5 * __grid_size__, screen_y + 0.5 * __grid_size__)
    n = (screen_x, screen_y - 0.5 * __grid_size__ + 5)
    s = (screen_x, screen_y + 0.5 * __grid_size__ - 5)
    w = (screen_x - 0.5 * __grid_size__ + 5, screen_y)
    e = (screen_x + 0.5 * __grid_size__ - 5, screen_y)

    actions = list(q_vals.keys())
    for action in actions:

        wedge_color = get_color(q_vals[action], min_val, max_val)

        if action == 'north':
            polygon((center, nw, ne), wedge_color, filled=1, smoothed=False)
            # text(n, text_color, val_str, "Courier", 8, "bold", "n")
        if action == 'south':
            polygon((center, sw, se), wedge_color, filled=1, smoothed=False)
            # text(s, text_color, val_str, "Courier", 8, "bold", "s")
        if action == 'east':
            polygon((center, ne, se), wedge_color, filled=1, smoothed=False)
            # text(e, text_color, val_str, "Courier", 8, "bold", "e")
        if action == 'west':
            polygon((center, nw, sw), wedge_color, filled=1, smoothed=False)
            # text(w, text_color, val_str, "Courier", 8, "bold", "w")

    square((screen_x, screen_y),
           0.5 * __grid_size__,
           color=__edge_color__,
           filled=0,
           width=3)
    line(ne, sw, color=__edge_color__)
    line(nw, se, color=__edge_color__)

    if is_current:
        circle((screen_x, screen_y), 0.1 * __grid_size__, __location_color__,
               fill_color=__location_color__)

    for action in actions:
        text_color = __text_color__
        if q_vals[action] < max(q_vals.values()): text_color = __muted_text_color__
        val_str = ""
        if action in val_strs:
            val_str = val_strs[action]
        h = -20
        if action == 'north':
            # polygon( (center, nw, ne), wedge_color, filled = 1, smooth = 0)
            text_on_canvas(n, text_color, val_str, "Courier", h, "bold", "n")
        if action == 'south':
            # polygon( (center, sw, se), wedge_color, filled = 1, smooth = 0)
            text_on_canvas(s, text_color, val_str, "Courier", h, "bold", "s")
        if action == 'east':
            # polygon( (center, ne, se), wedge_color, filled = 1, smooth = 0)
            text_on_canvas(e, text_color, val_str, "Courier", h, "bold", "e")
        if action == 'west':
            # polygon( (center, nw, sw), wedge_color, filled = 1, smooth = 0)
            text_on_canvas(w, text_color, val_str, "Courier", h, "bold", "w")


def get_color(val, min_val, max_val):
    r, g = 0.0, 0.0
    if val < 0 and min_val < 0:
        r = val * 0.65 / min_val
    if val > 0 and max_val > 0:
        g = val * 0.65 / max_val
    return format_color(r, g, 0.0)


def square(pos, size, color, filled, width):
    x, y = pos
    dx, dy = size, size
    return polygon([(x - dx, y - dy), (x - dx, y + dy), (x + dx, y + dy), (x + dx, y - dy)],
                   outline_color=color, fill_color=color, filled=filled, width=width,
                   smoothed=False)


def to_screen(point):
    (game_x, game_y) = point
    x = game_x * __grid_size__ + __margin__
    y = (__grid_height__ - game_y - 1) * __grid_size__ + __margin__
    return x, y


def to_grid(point):
    (x, y) = point
    x = int((y - __margin__ + __grid_size__ * 0.5) / __grid_size__)
    y = int((x - __margin__ + __grid_size__ * 0.5) / __grid_size__)
    print(point, "-->", (x, y))
    return x, y
