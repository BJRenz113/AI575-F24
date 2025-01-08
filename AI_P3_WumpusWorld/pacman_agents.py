# pacman_agents.py
# (c) 2016-2022 Christopher Newport University
#           David Conner (david.conner@cnu.edu)
#
# ---------------
# Based on pacman_agents from ai.berkeley.edu
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
Defines agents for Wumpus world exercise
"""
import random
import sys

from game import Agent
from game import Actions
from game import Directions

import util
#from pysat_wrapper import pysat_solver #did this according to email

# AI:MA code
from logic import expr, to_cnf, conjuncts
from logic import dpll_satisfiable, Expr, PropKB

class GoForwardAgent(Agent):
    """
    An agent that goes forward or
    turns right at every opportunity
    """

    def get_action(self, state):
        """
        Get valid action given state
        """

        # Get the sensor data to help make a rational decision
        sensors = self.get_sensors(state)
        if sensors:
            # Show sensors on the console
            print(sensors)

        # This agent ignores his sensors, and stumbles about the cave without concern for sensors
        #legal_actions = state.get_legal_pacman_actions()
        legal_directions = state.get_legal_pacman_directions()
        current_dir = state.get_pacman_state().configuration.direction
        current_action = state.get_pacman_state().last_action

        if current_action == Actions.STOP:
            current_action = Actions.FWD

        if current_action == Actions.FWD and current_dir in legal_directions:
            #print "Go forward blindly ..."
            return Actions.FWD # Continue moving forward if legal

        # If can't move forward, then try a right turn.
        # This agent never tries to grab gold or shoot arrow
        return Actions.RIGHT

class LogicalAgent(Agent):
    """
    An agent that uses propositional logic
    to determine its actions
    """

    def __init__(self, index=0):
        """
        Initialize the agent
        """
        super(LogicalAgent, self).__init__(index)
        self.__kb = PropKB()
        self.__kb.tell("WA")          # The wumpus is active!
        self.wumpus_active = True     # Assumes only one Wumpus
        self.have_immobilizer = True  # Track whether we have our arrow
        self.listen_for_scream = None # Track location to listen for Wumpus scream
                                      #    to see if we immobilized it
        self.starting_position = None # Track where we started in this world (for escape)
        self.visited = set()          # Track cells that we've expanded into KB
        self.unvisited = set()        # Track neighbors we've discovered but not yet expanded
        self.walls = set()            # Map our wall locations
        self.unsafe = set()           # Track known unsafe cells for return planning
        self.safe = set()             # Track known safe cells for planning
        self.current_plan = None      # Plan to execute

        #print "Ask: "
        #for exp in self.__kb.ask_generator(expr("WA")):
        #    print " exp:", exp

    def ask_entailed(self, negative_query, verbose_flag=False):
        """
        Assumes query is a single negative
        (i.e. formulated as the contradiction) proposition
        """

        cnf = to_cnf(negative_query)

        if True:  # Make this False to use pysat setup
            # Or true to use the AI:MA dpll_satisfiable which is MUCH slower!

            #print " negative query conjugates :", conjs
            #print "  KB clauses:", self.__kb.clauses

            test = Expr('&', cnf, *self.__kb.clauses)

            if verbose_flag:
                print("negative query: ", negative_query)

            result = dpll_satisfiable(test) # can we satisfy the contradiction
            if result:
                if verbose_flag:
                    print("query ", negative_query, " is satisfiable -> not entailed")
                return False

            if verbose_flag:
                print("query ", negative_query, " is NOT satisfiable -> entailed!")
            return True

        # Use the pysat setup (much, much faster)
        conjs = conjuncts(cnf)
        if verbose_flag:
            print("Negative Query <", negative_query, ">  conjuncts<", conjs, ">")

        if isinstance(conjs, str):
            conjs = expr(conjs)

        verbose_level = 0
        if verbose_flag:
            verbose_level = 1

        sat_result = pysat_solver(self.__kb.clauses, conjs, variable=None,
                                  value=True, verbose_level=verbose_level)
        if sat_result and sat_result.success:# == sF.success:
            if verbose_flag:
                print("query ", negative_query, " is satisfiable ->  Not entailed!")
                print("   vars:", sat_result.varmap)

            return False

        if verbose_flag:
            sat_neg_result = pysat_solver(self.__kb.clauses, conjs,
                                          variable=None, value=False,
                                          verbose_level=verbose_level)
            print("query ", negative_query,
                  " is NOT satisfiable -> entailed!")
            print("     sat_result vars:", sat_result.varmap)
            print("     sat_neg_result vars:", sat_neg_result.varmap)
            print("     sat_neg_result.success=", sat_neg_result.success,
                  "   sat_result=", sat_result.success)
            print("  KB", self.__kb.clauses)
        return True

    def get_action(self, state):
        """
        This method chooses the safest action
        given the reasoning in HybridWumpusAgent
        """

        # ******************************************
        # This check for entailed with TRUE checks
        # that the KB is consistent, and no
        # contradictory or elements were introduced anywhere in code.
        # We can use this as a debugging aid as needed.
        # Disabled here, but can enable if using pysat with minimal penalty.
        # It does NOT work with dpll_satisfiable.
        if False:
            if self.ask_entailed(expr("True")):
                print("Knowledge base has an issue at start " +
                      "of get_action - True should always be satisfiable!")
                self.ask_entailed(expr("True"), verbose_flag=True)
                sys.exit(-1)

        # Get the current pacman position.
        # We are assuming we have localization and don't need to logically track our position
        location = state.get_pacman_state().configuration.pos

        if self.starting_position is None:
            # Remember where we started from
            self.starting_position = (int(location[0]), int(location[1]))
            self.unvisited.add(self.starting_position) # temporary for bookkeeping below

        # Get the sensor data to help make a rational decision
        sensors = self.get_sensors(state)
        if sensors is None:
            # No sensors - no action!
            # As this gets called during pacman motion
            return None

        # We should have whole numbers at this point, so make integers to store
        i_loc = (int(location[0]), int(location[1]))
        if i_loc not in self.visited:
            # On first visit to a cell add all the relevant world knowledge to our knowledge base
            self.update_kb_visit(i_loc)

            self.visited.add(i_loc)  # Only need to add this once
            self.safe.add(i_loc)
            if i_loc in self.unvisited:
                self.unvisited.remove(i_loc)

            # Enable this block to draw (an annoying)
            # display of visited cells
            if False:
                import __main__
                if '_display' in dir(__main__):
                    if 'drawExpandedCells' in dir(__main__._display): #@UndefinedVariable
                        __main__._display.drawExpandedCells(self.visited) #@UndefinedVariable


        # legal_actions = state.get_legal_pacman_actions()
        legal_directions = state.get_legal_pacman_directions()
        current_dir = state.get_pacman_state().configuration.direction
        current_action = state.get_pacman_state().last_action

        # Show sensors on the console
        print("sensors(", i_loc, ")=", sensors)

        # Update the KB based on what we sensed at this location
        self.update_kb_percepts(i_loc, sensors,
                                current_dir, current_action)


        # If we have glitter, then grab the gold!
        if "Glitter" in sensors:
            print("Saw glitter - plan path to escape to ",
                  self.starting_position, " and grab the gold")
            self.current_plan, final_state = \
                self.get_safe_plan(i_loc, current_dir,
                                   [self.starting_position]) # The escape plan

            print("     escape plan to ", final_state, ": ", self.current_plan)
            return Actions.GRAB

        # We have a known safe plan in place, so continue to execute it
        if self.current_plan is not None:
            print("current plan :", self.current_plan)

            action = self.current_plan[0]
            if len(self.current_plan) > 1:
                self.current_plan = self.current_plan[1:]
            else:
                self.current_plan = None # No more plan to execute

            if action == Actions.SHOOT:
                # If we shoot,
                # then no more immobilizer ray
                self.have_immobilizer = False
            return action


        # Looking for a new plan
        action_plan = None
        if state.get_pacman_state().is_pacman and state.get_pacman_state().has_gold:
            # If we have already grabbed the gold, then see if we can now find
            # a safe path to the outlet
            print(" We have gold - need safe exit plan ...")
            action_plan, _ = self.get_safe_plan(i_loc, current_dir, [self.starting_position])

        if action_plan is None:
            # No plan
            #print "no plan at ", i_loc, " current=", current_dir, " - legal directions", legal_directions
            action_plan, _ = self.get_safe_plan(i_loc, current_dir, self.unvisited)

        if action_plan is None:
            # No safe plan to an unvisited node
            if self.have_immobilizer and self.wumpus_active: # Easier to track outside the KB
                # It is possible that any of the unvisited cells have the Wumpus
                print("     Have arrow and the Wumpus is on the prowl " +
                      " - is there a shot worth taking?")
                action_plan = self.shot_available(i_loc, current_dir, self.unvisited)

        if action_plan is None:
            # OK, will need to risk it
            print("     No known safe options - gotta risk it." +
                  " No guts no glory!") # Not necessarily good advice for your life
            action_plan, _ = self.get_unsafe_plan(i_loc, current_dir, self.unvisited)

        if action_plan is None:
            # We've looked everywhere, so may as well give up
            print("     No where to look - go home")
            action_plan, _ = self.get_safe_plan(i_loc, current_dir, [self.starting_position])

        if action_plan is None:
            print("     Something is whacked!")
            self.current_plan = None

            if current_action == Actions.STOP:
                if not "Bump" not in sensors and current_dir in legal_directions:
                    print("     Move forward blindly ...")
                    return Actions.FWD

            print("     Don't know what else to do, so just turn RIGHT")
            return Actions.RIGHT
        else:
            print("     New action plan :", action_plan)
            if len(action_plan) > 1:
                self.current_plan = action_plan[1:]
            else:
                self.current_plan = None
            return action_plan[0]


    def get_safe_plan(self, current_location, current_dir, goal_set):
        """
        Get a known safe plan to first node in goal set.
            We will use a simple A* search with goal test
        """

        # Get the known safe goals
        safe_goals = [goal for goal in goal_set if self.is_location_safe(goal)]
        #print " potential goals :", goal_set
        #print "     known safe goals: ", safe_goals

        if not safe_goals:
            print("         No verifiably safe unvisited cells!")
            return (None, None)

        # Get plan with only verified safe goals
        return self.get_plan(current_location, current_dir, safe_goals)

    def get_unsafe_plan(self, current_location, current_dir, possible_goal_set):
        """
        Get a known safe plan from current location to an uncertain goal location
        """

        # Anything that is "unvisited" was first discovered from a safe cell
        # Plan a provably safe path from current location to closest unvisited cell,
        # but that last step may be a killer!
        #
        # At this point the possible goal set should not contain known walls.
        # Let's reason about if we can show they are definitely Pits!

        goal_set = []
        logically_pits = []
        for loc in possible_goal_set:
            " Check for definite Pit (definite Wumpus considered in plan shot)"
            negative_query = expr(make_loc_proposition("~P", loc))
            result = self.ask_entailed(negative_query)
            if not result:
                # The KB does NOT entail that a Pit IS here
                goal_set.append(loc) # it might be safe
            else:
                # The KB entails that this is a pit!
                print("         Logically ", loc, " is a Pit!")
                logically_pits.append(loc)

        # Update our world knowledge after reasoning about pits
        for loc in logically_pits:
            self.unsafe.add(loc)
            if loc in self.unvisited:
                self.unvisited.remove(loc) # Never going here
            self.__kb.tell(expr(make_loc_proposition("P", loc)))

        if not self.have_immobilizer and self.wumpus_active:
            # We must have missed the wumpus earlier
            # Let's check for any certainty with Wumpus location now
            wumpus_locations = []
            for loc in goal_set:
                # Check for certainty
                negative_query = expr(make_loc_proposition("~W", loc))
                result = self.ask_entailed(negative_query)
                if result:
                    # The Wumpus is there!
                    self.__kb.tell(expr(make_loc_proposition("W", loc))) # Wumpus is here!
                    self.__kb.tell(expr(make_loc_proposition("~P", loc))) # No pit with Wumpus!
                    wumpus_locations.append(loc)

            if not wumpus_locations:
                for loc in wumpus_locations:
                    print("     wumpus is logically at ", loc)
                    goal_set.remove(loc)
                    self.unvisited.remove(loc)
                    self.unsafe.add(loc)

        # For now, we won't consider reasoning about beliefs about which
        # of remaining cells is the least risky
        print("     Original uncertain set: ", possible_goal_set)
        print("     Uncertain cells remaining :", goal_set)

        # Add some random choice if we don't know what to do
        random.shuffle(goal_set)
        if len(goal_set) > 1:
            goal_set = goal_set[0:int(len(goal_set)/2)] # gets 1/2 of elements

        print("     go to closest of   :", goal_set)
        # just go to the closest cell
        return self.get_plan(current_location, current_dir, goal_set)

    def get_plan(self, current_location, current_dir, goal_set):
        """
        Plan from current location along a veriably safe path to final (uncertain) cell
        This uses an implementation of A* with specific goal tests and successor
        generation for this Wumpus world problem.
        """
        from util import manhattan_distance
        # Set up the basic A* planner
        closed_set = set()
        fringe = util.PriorityQueue()
        fringe.push(((current_location, current_dir), [], 0), min([manhattan_distance(current_location, goal) for goal in goal_set]))
        while not fringe.isEmpty():
            state, action_plan, cost = fringe.pop() # state is posn and dir

            #print " "*cost, "state{", state, "}  cost(", cost, ") actions{", action_plan, "}  goal set{", goal_set, "}"
            if state[0] in goal_set:
                return (action_plan, state)
            if state not in closed_set:
                closed_set.add(state)
                for action in (Actions.FWD, Actions.LEFT, Actions.RIGHT):
                # Possible motion actions
                    succ_posn = state[0]
                    succ_dir = state[1]
                    if action == Actions.FWD:
                        vec = Actions.direction_to_vector(state[1])
                        succ_posn = (state[0][0]+int(vec[0]),
                                     state[0][1]+int(vec[1]))
                    else:
                        succ_dir = Actions.get_rotation_successor(succ_dir, action)

                    if self.is_location_safe(succ_posn) or succ_posn in goal_set:
                        # Only considering safe or terminal positions in plan
                        new_plan = action_plan[:]
                        new_plan.append(action)
                        new_cost = cost + 1

                        #print(" "*cost, "     Adding ", succ_posn, " ",
                        #      succ_dir, " from ", action, " to fringe with f=g+h",
                        #      new_cost, "+",h_cost)
                        h_cost = min([manhattan_distance(succ_posn, goal) for goal in goal_set])
                        f_cost = new_cost + h_cost

                        fringe.push(((succ_posn, succ_dir), new_plan, new_cost), f_cost)
                    #else:
                    #    print(" "*cost, "     Cannot add ", succ_posn, " ", succ_dir,
                    #          " from ", action, " to the fringe as not safe")

        print("failed to find plan to any goal set", goal_set)

        return (None, None)

    def shot_available(self, i_loc, current_dir, potential_wumpus_locations):
        """
        Do any of these locations potentially contain a wumpus.
        If so, do we want to try a shot?
        """

        might_be_wumpus = []
        for loc in potential_wumpus_locations:
            "~Wumpus"
            negative_query = expr(make_loc_proposition("W", loc))
            result = self.ask_entailed(negative_query)
            if not result:
                # The KB does NOT entail that the Wumpus is NOT here
                might_be_wumpus.append(loc) # it might be

                # Check for certainty
                negative_query = expr(make_loc_proposition("~W", loc))
                result = self.ask_entailed(negative_query)
                if result:
                    # The Wumpus is there!
                    self.__kb.tell(expr(make_loc_proposition("W", loc))) # Wumpus is here!
                    self.__kb.tell(expr(make_loc_proposition("~P", loc))) # No pit with Wumpus!
                    #Plan to one step short of Wumpus then face Wumpus and shoot (better hope you are logically correct)
                    return self.plan_shot(i_loc, current_dir, loc)

        # Don't know for sure, we some some guesses
        # This picks one and takes a shot in the dark.
        if might_be_wumpus:
            print("     Potential wumpus locations: ", might_be_wumpus)
            # Just pick a potential wumpus location and return the first valid
            # shot plan
            random.shuffle(might_be_wumpus) # Shuffle the up
            for loc in might_be_wumpus:
                shot_plan = self.plan_shot(i_loc, current_dir, loc)
                if shot_plan is not None:
                    print("     Attempting shot to location", loc)
                    return shot_plan

        # No shot to take
        return None

    def plan_shot(self, i_loc, current_dir, loc):
        """
        Given potential wumpus location,
        plan a path to get close, then shoot
        """

        goal_set = get_neighbors(loc) # Move to one of neighbors
        action_plan, final_state = self.get_plan(i_loc, current_dir, goal_set)
        if action_plan is None:
            return None

        final_pos, final_dir = final_state

        print(" Move to final ", final_pos, " ", final_dir, " for shot")

        # Need to rotate to face Wumpus
        vector = (loc[0] - final_pos[0], loc[1] - final_pos[1])
        required_dir = Actions.vector_to_direction(vector)
        while required_dir != final_dir:
            action = Actions.get_rotation_action(final_dir, required_dir)# Need to rotate
            final_dir = Actions.get_rotation_successor(final_dir, action)
            action_plan.append(action)

        # Shoot action
        action_plan.append(Actions.SHOOT)
        action_plan.append(Actions.STOP) # Listen for two turns
        action_plan.append(Actions.STOP)
        self.listen_for_scream = loc
        return action_plan

    def is_location_safe(self, iloc):
        """
        Ask the knowledge base if a given location is safe
        """

        if iloc[0] < 0 or iloc[1] < 0:
            return False # only consider points in bounds for our world

        if iloc in self.safe:
            # Quick lookup in our map
            return True

        # Check our map
        if iloc in self.walls:
            #print " Cave wall at ", iloc
            return False # We know this to be a cave wall, so not safe for travel

        #  We need to check if the KB to see if the cell is safe
        # That is not a pit or active Wumpus
        #  Create a query expression using expr( ) from
        # propositions, and then
        #@TODO - make a proposition and see if it is entailed by the KB
        #        The proposition should be in the negative form that is
        #        used to show the contradiction of what we are trying to
        #        prove.
        #       e.g. return self.ask_entailed(neg_query)

        pitThere = self.ask_entailed(expr(make_loc_proposition("~P", iloc)))
        wumpusThere = self.ask_entailed(expr(make_loc_proposition("~W", iloc)))
        breezeThere = self.ask_entailed(expr(make_loc_proposition("~B", iloc))) #pacman was diregarding breezes

        return pitThere and wumpusThere and breezeThere

    def update_kb_visit(self, position):
        """
        Update the KB with knowledge about the surrounding Wumpus world
        We will incrementally build our KB as we explore the space and not depend
        on prior knowledge of the world size
        """

        # If we arrive at this cell, it is safe.
        #@TODO - make some propositions (see the make_proposition examples below)
        #        and "tell" the knowledge base
        #   NOTE: an inactive Wumpus might be present,
        #         but an active wumpus cannot be
        #  This will require two propositions with some logical
        #     as to apply one or both in different states

        self.__kb.tell(expr(make_loc_proposition('~P', position)))
        self.__kb.tell(expr(make_loc_proposition('~W', position)))

        # Get list of 4 adjacent neighbors
        neighbors = get_neighbors(position)
        #print "neighbors: ", neighbors

        # Will sense breeze iff pit is adjacent
        #e.g. (B11 <=> (P12 | P21))
        prop = expr(make_loc_proposition('B', position)+ "<=> " + make_or_proposition('P', neighbors))
        self.__kb.tell(prop)

        # Will sense stench iff wumpus is here or adjacent
        prop = expr(make_loc_proposition('S', position)+ "<=> (" +
                    make_loc_proposition('W', position) + " | " +
                    make_or_proposition('W', neighbors)[1:])
        self.__kb.tell(prop)


        #  Will sense glitter iff gold is present in this square"
        #  NOTE: We are currently tracking has_gold and
        #  glitter outside the KB for simplicity in hybrid agent
        #    #prop = make_loc_proposition('GL', position)+ "<=> " + make_loc_proposition('G', position)
        #    #self.__kb.tell(expr(prop))

        # Only one wumpus - which means that W | ~W  is true for all neighbors"
        #     We can only have one Wumpus between current cell and neighbors,
        #     or pairwise between neighbors.
        #     This does not preclude having multiple wumpii in world,
        #     but does require that they be scattered.
        for nbor in neighbors:

            # Keep track of unvisited neighbors
            if nbor not in self.visited and nbor not in self.unvisited:
                # Keep track of cells on boundary that we have not explored
                self.unvisited.add(nbor)

            #@TODO - add proposition that says wumpus cannot be in two places at once (current and neighbors)
            self.__kb.tell(expr("~W{0}_{1} | ~W{2}_{3}".format(position[0], position[1], nbor[0], nbor[1])))

            for other_nbor in neighbors:
                if other_nbor != nbor:
                    self.__kb.tell(expr("~W{0}_{1} | ~W{2}_{3}".format(nbor[0], nbor[1], other_nbor[0], other_nbor[1])))



        # Only one wumpus among all neighbors
        import itertools #?
        for pairs in itertools.product(*[neighbors, neighbors]):
            if pairs[0] != pairs[1]:
                self.__kb.tell(expr(make_or_proposition("~W", pairs)))


        # Enable this check for entailed with TRUE
        # This checks that the KB is still consistent,
        # and no contradictory elements were introduced by
        # visited method.
        # Disabled here, but can enable if using pysat with
        # minimal penalty.
        # It does NOT work with dpll_satisfiable.
        if False:
            if self.ask_entailed(expr("True")):
                print("Knowledge base has an issue at start of get_action - True should always be satisfiable!")
                self.ask_entailed(expr("True"), verbose_flag=True)
                sys.exit(-1)

    def update_kb_percepts(self, iloc, sensors, current_dir, current_action):
        """
        This method updates the KB based on our current sensed precepts
        """
        #print "Sensors: ", sensors
        #print " current direction=", current_dir, " action=", current_action
        if "Bump" in sensors:
            vec = Actions.direction_to_vector(current_dir)
            nloc = (iloc[0]+int(vec[0]), iloc[1]+int(vec[1]))
            if nloc[0] >= 0 and nloc[1] >= 0:
                print("   Bumped into a cave boundary at ", nloc)
                self.walls.add(nloc)        # add to map of boundaries
                self.visited.add(nloc)      # we have shown the contents of cell,
                if nloc in self.unvisited:
                    self.unvisited.remove(nloc) #     so we have effectively visited the cell
                self.__kb.tell(expr(make_loc_proposition("~P", nloc))) # no pit if wall
                self.__kb.tell(expr(make_loc_proposition("~W", nloc))) # no Wumpus if wall
                self.current_plan = None # Clear any existing plan to force replanning

        # Tell if we sense glitter
        #  No need to track ~GL for us
        if "Glitter" in sensors:
            self.__kb.tell(expr(make_loc_proposition("GL", iloc)))

        if "Scream" in sensors:
            print("Wumpus screamed - add not active to knowledge base")
            self.__kb.retract("WA") # The Wumpus is no longer active
            self.__kb.tell(expr("~WA")) # The Wumpus is immobile, Jim
            self.wumpus_active = False # Simplify our checks
            if self.listen_for_scream is not None:
                self.__kb.tell(expr(make_loc_proposition("W", self.listen_for_scream))) # We hit it here!
                self.listen_for_scream = None
        elif not self.have_immobilizer:
            if self.listen_for_scream is not None:
                print(" don't have arrow - current action=", current_action, " listen=", self.listen_for_scream)
                if current_action != Actions.SHOOT:
                    # We missed
                    print("Oh no! We must have missed!  The Wumpus wasn't there.")
                    self.__kb.tell(expr(make_loc_proposition("~W", self.listen_for_scream))) # No Wumpus here!
                    self.listen_for_scream = None
                else:
                    print("Waiting in hopeful anticipation to see if we got the dreaded Wumpus ...")

        #  Better add something if we smell a Stench (or not)
        #   or detect a breeze (or not)
        #@TODO - handle the Stench and Breeze precepts

        if "Breeze" in sensors:
            self.__kb.tell(expr(make_loc_proposition('B', iloc))) #Yes breeze
        else:
            self.__kb.tell(expr(make_loc_proposition('~B', iloc))) #No breeze
        if "Stench" in sensors:
            self.__kb.tell(expr(make_loc_proposition('S', iloc))) #Yes stench
        else:
            self.__kb.tell(expr(make_loc_proposition('~S', iloc))) #No stench

       #inference: nearby cells do not hold wumpus
        if "Stench" not in sensors:
            for nloc in get_neighbors(iloc):
                self.__kb.tell(expr(make_loc_proposition("~W", nloc)))

        #inference: no pit nearby
        if "Breeze" not in sensors:
            for nloc in get_neighbors(iloc):
                self.__kb.tell(expr(make_loc_proposition("~P", nloc)))

        if not self.wumpus_active: #pacman would get confused after grabbing treasure
            self.__kb.tell(expr("~W"))

        # Enable this check for entailed with TRUE
        # which checks that the KB is still consistent
        # after we added knowledge based on percepts, and no contradictory elements
        # were introduced.
        # It is a sanity check that our code is correct.
        # Disabled here, but can enable if using pysat
        # with minimal penalty.
        # It does NOT work with dpll_satisfiable.
        if False:
            if self.ask_entailed(expr("True")):
                print("Knowledge base has an issue at start of get_action " +
                      " - True should always be satisfiable!")
                self.ask_entailed(expr("True"), verbose_flag=True)
                sys.exit(-1)


def get_neighbors(position):
    """
    Get the four adjancent neighbors that are
    relevant to our grid world
    """
    neighbors = []
    for i in range(-1, 2):
        for j in range(-1, 2):
            if (i != 0 or j != 0) and (i*j == 0):
                # Don't consider same cell or diagonals
                pos = (position[0]+i, position[1]+j)
                if pos[0] >= 0 and pos[1] >= 0:
                    # Only positive values
                    neighbors.append(pos)
    return neighbors

def make_loc_proposition(symbol, position):
    """
    Make a simple proposition from prefix symbol and x_y format
    """
    return symbol+"{0}_{1}".format(position[0], position[1])

def make_or_proposition(symbol, positions):
    """
    Make a disjuntive proposition with parenthesis
    from common prefix and list of relevant positions
    """
    prop = "("
    for pos in positions:
        prop += symbol+"{0}_{1}".format(pos[0], pos[1])+ " | "
    return prop[:-3]+")" # remove the last |

def make_and_proposition(symbol, positions):
    """
    Make an conjuctive proposition with parenthesis
    from common prefix and list of relevant positions
    """
    prop = "("
    for pos in positions:
        prop += symbol+"{0}_{1}".format(pos[0], pos[1])+ " & "
    return prop[:-3]+")" # remove the last &
