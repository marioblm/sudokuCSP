import numpy as np
import sys

from SudokuField import FIELD_SIZE
import SudokuCSP as sCSP
from SudokuReader import get_field_from_file, generate_templates

iteration = 0


def print_field(field):
    for row_index, row in enumerate(field):
        for index, value in enumerate(row):
            print("{} ".format(value), end="")
            if (index + 1) % 3 == 0 and index < FIELD_SIZE - 1:
                print(" | ", end="")
        print("")
        if (row_index + 1) % 3 == 0 and row_index < FIELD_SIZE - 1:
            print("- " * (FIELD_SIZE + 3))


def bt_search(assignment, csp):
    """
    Finds a valid assignment for problem if there is one
    """
    global iteration
    if sCSP.complete(assignment):
        return assignment
    iteration += 1
    var = csp.variables(assignment)  # select variable
    for value in assignment[var].domain:
        assignment[var].setValue(value)
        if sCSP.consistent(assignment):
            print("Iteration {}:".format(iteration))
            print_field(np.reshape(assignment, (FIELD_SIZE, FIELD_SIZE)))
            if csp.inference(assignment, var):
                # next step
                result = bt_search(assignment, csp)
                if type(result) is np.ndarray:
                    return np.reshape(result, (FIELD_SIZE, FIELD_SIZE))  # valid assignment
            # inference failed -> undo
            assignment[var].setValue(None)
        else:
            # invalid assignment -> undo
            assignment[var].setValue(None)
    return False


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Please provide a filename")
        exit()
    sudoku_file = sys.argv[1]
    if "generate-templates" in sys.argv:
        generate_templates(sudoku_file)
    else:
        use_mrv = "NO-MRV" not in sys.argv
        use_degree = use_mrv and "NO-DEG" not in sys.argv
        use_forward_checking = "NO-FC" not in sys.argv
        sudoku_csp = sCSP.SudokuCSP(use_mrv, use_degree, use_forward_checking)
        sf = get_field_from_file(sudoku_file)
        print_field(sf)
        input("Press enter to continue ")
        solution = bt_search(sf.flatten(), sudoku_csp)
        if type(solution) is np.ndarray:
            print("\nFinal Solution:")
            print_field(solution)
        else:
            print("No solution found")
