# pysat_wrapper.py
# (c) 2016-2022 Christopher Newport University
#           David Conner (david.conner@cnu.edu)
#
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
# ---------------
# Based on minisat.py from
# Licensing Information:
# Please DO NOT DISTRIBUTE OR PUBLISH solutions to this project.
# You are free to use and extend these projects for EDUCATIONAL PURPOSES ONLY.
# The Hunt The Wumpus AI project was developed at University of Arizona
# by Clay Morrison (clayton@sista.arizona.edu), spring 2013.
# This project extends the python code provided by Peter Norvig as part of
# the Artificial Intelligence: A Modern Approach (AIMA) book example code;
# see http://aima.cs.berkeley.edu/code.html
# In particular, the following files come directly from the AIMA python
# code: ['agents.py', 'logic.py', 'search.py', 'utils.py']
# ('logic.py' has been modified by Clay Morrison in locations with the
# comment 'CTM')
# The file ['pysa.py'] implements a slim system call wrapper to the minisat
# (see http://minisat.se) SAT solver, and is directly based on the satispy
# python project, see https://github.com/netom/satispy .

from logic import *
from pysat.formula import CNF
from pysat.solvers import Solver

from subprocess import call
from tempfile import NamedTemporaryFile

def pysat_solver(clauses, query=None, variable=None, value=True, verbose_level=0):
    """ Interface to pysat
    <query> is simply added as to the list of <clauses>

    Set <variable> to a particular <value> in order to test SAT
    assuming any instance of that variable has that value.

    Otherwise, with defaults, will perform normal SAT on <clauses>+<query>
    """

    aima_clauses = list(clauses)
    if query is not None:
        assert isinstance(query, list)
        aima_clauses = aima_clauses + query

    solver = PySatWrapper()
    try:
        if verbose_level > 0:
            print(f"Calling PySat solver with query = <{query}>")
        solution = solver.solve(aima_clauses, variable=variable, value=value, verbose_level=verbose_level)
        if verbose_level > 0:
            print(f"PySat Solver result: {solution}")
        return solution
    except Exception as exc:
        print(f"Solver Exception: {exc}")
        raise exc

def literal_name(literal):
    if literal.op == '~':
        return literal.args[0].op
    else:
        return literal.op

def clauses_to_conjunct(clause_list):
    """ coerce a list of clauses into a conjunction """
    conj = Expr('&')
    conj.args = clause_list
    return conj
    #return ' & '.join(map(lambda(i): '{0}'.format(KB.clauses[i]), list))

def prop_symbols_from_clause_list(clause_list):
    return prop_symbols(clauses_to_conjunct(clause_list))

# The following is a fairly direct adaptation of the very nice,
# slim wrapper to minisat provided by https://github.com/netom/satispy
# I'm not using satispy directly b/c it implements its own cnf rep.
# so I'm adapting the aima rep to communication with minisat.

class AIMA_to_Dimacs_Translator(object):

    def __init__(self):
        self.varname_dict = {}
        self.varobj_dict = {}

    def varname(self, vo):
        return self.varname_dict[vo]

    def varobj(self, v):
        return self.varobj_dict[v]

    def to_dimacs_string(self, clauses):
        """Convert AIMA cnf expression to Dimacs cnf string

        clauses: list of clauses in AIMA cnf

        In the converted Cnf there will be only numbers for
        variable names. The conversion guarantees that the
        variables will be numbered alphabetically.
        """
        self.varname_dict = {}
        self.varobj_dict = {}
        variables = prop_symbols_from_clause_list(clauses)
        ret = 'p cnf %d %d' % (len(variables), len(clauses))
        varis = dict(list(zip(sorted(variables, key=lambda v: v.op),
                         list(map(str, list(range(1, len(variables) + 1)))))))
        for var in varis:
            self.varname_dict[var] = varis[var]
            self.varobj_dict[varis[var]] = var

        for clause in clauses:
            ret += '\n'
            dimacs_vlist = []
            if clause.op == '|':
                for var in clause.args:
                    dimacs_vlist.append(('-' if var.op == '~' else '') \
                                        + self.varname_dict[var.args[0]
                                                            if var.op == '~' else var])

                ret += ' '.join(dimacs_vlist)
            elif clause.op == '~':
                ret += '-' + self.varname_dict[clause.args[0]]
            else:
                ret += self.varname_dict[clause]
            ret += ' 0'

        return ret

    def to_dimacs_string_set_variable_value(self, clauses, variable, value):
        """
        Same as above, but returns dimacs for the clauses for SAT test
             with variable set to value as follows:
        (1) If value = True, then all clauses containing a literal made true
             by that value will be removed
             (because any disjunctive clause with a True literal is SAT)
        (2) If value = False, then any clauses containing that literal have
             the literal removed ; if the literal is singular, then return
             no clauses, indicating that setting to that value is UNSAT
        """
        self.varname_dict = {}
        self.varobj_dict = {}
        variables = prop_symbols_from_clause_list(clauses)
        if variable in variables:
            variables.remove(variable)
        varis = dict(list(zip(sorted(variables, key=lambda v: v.op),
                         list(map(str, list(range(1, len(variables) + 1)))))))
        for var in varis:
            self.varname_dict[var] = varis[var]
            self.varobj_dict[varis[var]] = var

        ret_clauses = ''
        clause_count = 0
        for clause in clauses:
            clause_exists = True
            dimacs_vlist = []
            ret_clause = ''
            if clause.op == '|':
                for var in clause.args:
                    if literal_name(var) == literal_name(variable):
                        if value and not var.op == '~' or not value and var.op == '~':
                            clause_exists = False
                    else:
                        dimacs_vlist.append(('-' if var.op == '~' else '') \
                                            + self.varname_dict[var.args[0]
                                                                if var.op == '~' else var])

                if clause_exists:
                    ret_clause += ' '.join(dimacs_vlist)
            elif clause.op == '~':
                if literal_name(clause) == literal_name(variable):
                    if value:
                        return None
                    clause_exists = False
                else:
                    ret_clause += '-' + self.varname_dict[clause.args[0]]
            elif literal_name(clause) == literal_name(variable):
                if value:
                    clause_exists = False
                else:
                    return None
            else:
                ret_clause += self.varname_dict[clause]
            if clause_exists:
                clause_count += 1
                ret_clauses += ret_clause + ' 0\n'

        ret_header = 'p cnf %d %d\n' % (len(variables), clause_count)
        ret = ret_header + ret_clauses
        return ret

    @staticmethod
    def to_pysat_cnf(dimacs):
        """ Input dimacs string, return list of lists in PySat format
        """

        lines = dimacs.split("\n")
        pysat_cnf = []
        for line in lines[1:]:
            pysat_cnf.append([int(val) for val in line.split(" ")[:-1]])
        return pysat_cnf

class Solution(object):

    def __init__(self, success = False, varmap = {}):
        self.success = success
        self.varmap = varmap

    def __repr__(self):
        return '<PySat.Sol {0}>'.format(self.success)

    def __getitem__(self, i):
        return self.varmap[i]

    def pprint(self):
        print(self.success)
        print(self.varmap)

    def __str__(self):
        return f" {self.success}: {self.varmap}"

class PySatWrapper(object):
    DEFAULT_SOLVER = 'minisat22'

    def __init__(self, solver_name = DEFAULT_SOLVER):
        self.solver_name = solver_name

    def solve(self, aima_cnf, variable=None, value=True,
              translator=AIMA_to_Dimacs_Translator,
              verbose_level=0):

        # if there are no clauses, then can't infer anything, so by default query result is unknown
        # return Solution with success == None
        # Note that this could be treated the same as failure.
        # In PropKB_SAT.ask, this is OK as it will test if sT.success == sF.success
        #     and therefore will also return None
        if not aima_cnf:
            print("No cnf clauses - nothing to infer!")
            return Solution(None)


        # Translate from AI:MA notation to DIMACS
        # https://people.sc.fsu.edu/~jburkardt/data/cnf/cnf.html
        io = translator()
        if variable:
            dimacs_cnf = io.to_dimacs_string_set_variable_value(aima_cnf, variable, value)
            if not dimacs:
                return Solution() # Failed
        else:
            dimacs_cnf = io.to_dimacs_string(aima_cnf)

        pysat_cnf = io.to_pysat_cnf(dimacs_cnf)


        if verbose_level > 1:
            print(f"AI:MA CNF: {aima_cnf}")
            print(30*"-")
            print(f"Dimac CNF: \n{dimacs_cnf}")
            print(30*"-")
            print(f"PySat CNF: {pysat_cnf}")
            print(30*"=")

        solution = Solution()
        with Solver(name=self.solver_name, bootstrap_with=pysat_cnf, use_timer=True) as solver:
            solver_ret = solver.solve()

            if solver_ret:
                solution.success = True

                model = solver.get_model()
                for varz in model:
                    v = str(abs(varz))
                    value = varz > 0
                    vo = io.varobj(v)
                    solution.varmap[vo] = value

        return solution
