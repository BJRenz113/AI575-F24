# test_pysat.py
# ---------
# Simple test of pysat interface using AI:MA style encodings

from pysat_wrapper import pysat_solver

#-------------------------------------------------------------------------------
# Test MiniSat connection
#-------------------------------------------------------------------------------

def run_pysat_test():
    """
    Test connection to PySat
    """
    import logic

    queries = [("(P | ~P)", True), # SAT
               ("(P & ~P)", False), # UNSAT
               ("(P | R) <=> (~(Q | R) & (R >> ~(S <=> T)))", True) # SAT
               ]

    print("Running simple PySat test:")
    t = 1
    failed = []
    for query, expected_result in queries:
        print("-----------------------------------------------------")
        print("Test {0}".format(t))
        print("  Query:      '{0}'".format(query))
        query = logic.conjuncts(logic.to_cnf(logic.expr(query)))
        result = pysat_solver(query, None, variable=None, value=True, verbose_level=10)
        if result.success != expected_result:
            print("    FAILURE: unexpected result.")
            failed.append(t)
        if result.success:
            print("  Variable Assignment: {0}".format(result.varmap))
        t += 1
    print("-----------------------------------------------------")
    if not failed:
        print("Successfully passed {0} tests.".format(len(queries)))
    else:
        print("Passed {0} test(s).".format(len(queries) - len(failed)))
        print("The following tests failed: {0}".format(failed))
    print("DONE.")


if __name__ == '__main__':
    """
    The main function called when test_pysat.py is run from the command line:
    > python test_pysat.py
    """
    run_pysat_test()
