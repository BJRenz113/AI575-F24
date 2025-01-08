"""
graphics_crawler_display.py
-------------------------
Licensing Information:  You are free to use or extend these projects for
educational purposes provided that (1) you do not distribute or publish
solutions, (2) you retain this notice, and (3) you provide clear
attribution to UC Berkeley, including a link to http://ai.berkeley.edu.

Attribution Information: The Pacman AI projects were developed at UC Berkeley.
The core projects and autograders were primarily created by John DeNero
(denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
Student side autograding was added by Brad Miller, Nick Hay, and
Pieter Abbeel (pabbeel@cs.berkeley.edu).

Licensing Information: Please do not distribute or publish solutions to this
project. You are free to use and extend these projects for educational
purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
Student side autograding was added by Brad Miller, Nick Hay, and Pieter
Abbeel in Spring 2013.
For more info, see http://inst.eecs.berkeley.edu/~cs188/pacman/pacman.html
"""

import sys
import threading
import time
import tkinter

import crawler
import q_learning_agents

# globals
__root__ = None

# constants
ROBOT_TYPE = 'crawler'


class Application:

    @staticmethod
    def sigmoid(x):
        return 1.0 / (1.0 + 2.0 ** (-x))

    def increment_speed(self, inc):
        self.tick_time *= inc
        #        self.epsilon = min(1.0, self.epsilon)
        #        self.epsilon = max(0.0,self.epsilon)
        #        self.learner.setSpeed(self.epsilon)
        self.speed_label['text'] = 'Step Delay: %.5f' % self.tick_time

    def increment_epsilon(self, inc):
        self.ep += inc
        self.epsilon = self.sigmoid(self.ep)
        self.learner.set_epsilon(self.epsilon)
        self.epsilon_label['text'] = 'Epsilon: %.3f' % self.epsilon

    def increment_gamma(self, inc):
        self.ga += inc
        self.gamma = self.sigmoid(self.ga)
        self.learner.set_discount(self.gamma)
        self.gamma_label['text'] = 'Discount: %.3f' % self.gamma

    def increment_alpha(self, inc):
        self.al += inc
        self.alpha = self.sigmoid(self.al)
        self.learner.set_learning_rate(self.alpha)
        self.alpha_label['text'] = 'Learning Rate: %.3f' % self.alpha

    def __init_gui(self, win):
        # Window
        self.win = win

        # Initialize Frame
        win.grid()
        self.dec = -.5
        self.inc = .5
        self.tick_time = 0.1

        # Epsilon Button + Label
        self.setup_speed_button_and_label(win)

        self.setup_epsilon_button_and_label(win)

        # Gamma Button + Label
        self.set_up_gamma_button_and_label(win)

        # Alpha Button + Label
        self.setup_alpha_button_and_label(win)

        # Exit Button
        # self.exit_button = Tkinter.Button(win,text='Quit', command=self.exit)
        # self.exit_button.grid(row=0, column=9)

        # Simulation Buttons
        #        self.setupSimulationButtons(win)

        # Canvas
        self.canvas = tkinter.Canvas(__root__, height=200, width=1000)
        self.canvas.grid(row=2, columnspan=10)

    def setup_alpha_button_and_label(self, win):
        self.alpha_minus = tkinter.Button(win,
                                          text="-",
                                          command=(lambda: self.increment_alpha(self.dec)))
        self.alpha_minus.grid(row=1, column=3, padx=10)

        self.alpha = self.sigmoid(self.al)
        self.alpha_label = tkinter.Label(win, text='Learning Rate: %.3f' % (self.alpha))
        self.alpha_label.grid(row=1, column=4)

        self.alpha_plus = tkinter.Button(win,
                                         text="+",
                                         command=(lambda: self.increment_alpha(self.inc)))
        self.alpha_plus.grid(row=1, column=5, padx=10)

    def set_up_gamma_button_and_label(self, win):
        self.gamma_minus = tkinter.Button(win,
                                          text="-",
                                          command=(lambda: self.increment_gamma(self.dec)))
        self.gamma_minus.grid(row=1, column=0, padx=10)

        self.gamma = self.sigmoid(self.ga)
        self.gamma_label = tkinter.Label(win, text='Discount: %.3f' % (self.gamma))
        self.gamma_label.grid(row=1, column=1)

        self.gamma_plus = tkinter.Button(win,
                                         text="+", command=(lambda: self.increment_gamma(self.inc)))
        self.gamma_plus.grid(row=1, column=2, padx=10)

    def setup_epsilon_button_and_label(self, win):
        self.epsilon_minus = tkinter.Button(win,
                                            text="-",
                                            command=(lambda: self.increment_epsilon(self.dec)))
        self.epsilon_minus.grid(row=0, column=3)

        self.epsilon = self.sigmoid(self.ep)
        self.epsilon_label = tkinter.Label(win, text='Epsilon: %.3f' % (self.epsilon))
        self.epsilon_label.grid(row=0, column=4)

        self.epsilon_plus = tkinter.Button(win,
                                           text="+",
                                           command=(lambda: self.increment_epsilon(self.inc)))
        self.epsilon_plus.grid(row=0, column=5)

    def setup_speed_button_and_label(self, win):
        self.speed_minus = tkinter.Button(win,
                                          text="-", command=(lambda: self.increment_speed(.5)))
        self.speed_minus.grid(row=0, column=0)

        self.speed_label = tkinter.Label(win, text='Step Delay: %.5f' % (self.tick_time))
        self.speed_label.grid(row=0, column=1)

        self.speed_plus = tkinter.Button(win,
                                         text="+", command=(lambda: self.increment_speed(2)))
        self.speed_plus.grid(row=0, column=2)

    def skip_5k_steps(self):
        self.steps_to_skip = 5000

    def __init__(self, win):

        self.ep = 0
        self.ga = 2
        self.al = 2
        self.step_count = 0

        # Define calculated attributes
        self.epsilon = self.sigmoid(self.ep)
        self.gamma = self.sigmoid(self.ga)
        self.alpha = self.sigmoid(self.al)

        # Define GUI widget handles
        self.alpha_minus = None
        self.alpha_label = None
        self.alpha_plus = None
        self.gamma_minus = None
        self.gamma_label = None
        self.gamma_plus = None
        self.epsilon_minus = None
        self.epsilon_label = None
        self.epsilon_plus = None
        self.speed_minus = None
        self.speed_label = None
        self.speed_plus = None
        # Init Gui

        self.__init_gui(win)

        # Init environment
        if ROBOT_TYPE == 'crawler':
            self.robot = crawler.CrawlingRobot(self.canvas)
            self.robot_environment = crawler.CrawlingRobotEnvironment(self.robot)
        else:
            raise Exception("Unknown RobotType")

        # Init Agent
        action_fn = \
            lambda state: self.robot_environment.get_possible_actions(state)

        self.learner = q_learning_agents.QLearningAgent(actionFn=action_fn)

        self.learner.set_epsilon(self.epsilon)
        self.learner.set_learning_rate(self.alpha)
        self.learner.set_discount(self.gamma)

        # Start GUI
        self.running = True
        self.stopped = False
        self.steps_to_skip = 0
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def exit(self):
        self.running = False
        for i in range(5):
            if not self.stopped:
                time.sleep(0.1)
        try:
            self.win.destroy()
        except Exception:
            pass
        sys.exit(0)

    def step(self):

        self.step_count += 1

        state = self.robot_environment.get_current_state()
        actions = self.robot_environment.get_possible_actions(state)
        if not actions:
            self.robot_environment.reset()
            state = self.robot_environment.get_current_state()
            actions = self.robot_environment.get_possible_actions(state)
            print('Reset!')
        action = self.learner.get_action(state)
        if action is None:
            raise Exception('None action returned: Code Not Complete')
        next_state, reward = self.robot_environment.do_action(action)
        self.learner.observe_transition(state, action, next_state, reward)

    def run(self):
        self.step_count = 0
        self.learner.start_episode()
        while True:
            min_sleep = .01
            tm = max(min_sleep, self.tick_time)
            time.sleep(tm)
            self.steps_to_skip = int(tm / self.tick_time) - 1

            if not self.running:
                self.stopped = True
                return
            for i in range(self.steps_to_skip):
                self.step()
            self.steps_to_skip = 0
            self.step()
        #          self.robot.draw()
        # todo investigate unreachable code
        self.learner.stop_episode()

    def start(self):
        self.win.mainloop()


def run():
    global __root__
    __root__ = tkinter.Tk()
    __root__.title('Crawler GUI')
    __root__.resizable(0, 0)

    #  root.mainloop()

    app = Application(__root__)

    def update_gui():
        app.robot.draw(app.step_count, app.tick_time)
        __root__.after(10, update_gui)

    update_gui()

    __root__.protocol('WM_DELETE_WINDOW', app.exit)
    try:
        app.start()
    except Exception:
        app.exit()
