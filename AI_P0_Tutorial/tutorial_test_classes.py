"""
tutorial_test_classes.py
----------------------
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

import test_classes


# Simple test case which evals an arbitrary piece of python code.
# The test is correct if the output of the code given the student's
# solution matches that of the instructor's.
class EvalTest(test_classes.TestCase):

    def __init__(self, question, test_dict):
        super(EvalTest, self).__init__(question, test_dict)
        self.preamble = compile(test_dict.get('preamble', ""), "%s.preamble" % self.get_path(),
                                'exec')
        self.test = compile(test_dict['test'], "%s.test" % self.get_path(), 'eval')
        self.success = test_dict['success']
        self.failure = test_dict['failure']


    def eval_code(self, module_dict):
        bindings = dict(module_dict)
        exec(self.preamble, bindings)
        return str(eval(self.test, bindings))

    def execute(self, grades, module_dict, solution_dict):
        result = self.eval_code(module_dict)
        if result == solution_dict['result']:
            grades.add_message('PASS: %s' % self.path)
            grades.add_message('\t%s' % self.success)
            return True

        grades.add_message('FAIL: %s' % self.path)
        grades.add_message('\t%s' % self.failure)
        grades.add_message('\tstudent result: "%s"' % result)
        grades.add_message('\tcorrect result: "%s"' % solution_dict['result'])

        return False

    def write_solution(self, module_dict, file_path):
        handle = open(file_path, 'w')
        handle.write('# This is the solution file for %s.\n' % self.path)
        handle.write(
            '# The result of evaluating the test must equal the below when cast to a string.\n')

        handle.write('result: "%s"\n' % self.eval_code(module_dict))
        handle.close()
        return True
