import sys
import numpy as np
from SudokuField import FIELD_SIZE, GROUP_SIZE


def has_duplicates(array):
    """
    Check whether array has duplicate values
    """
    return len(array) != len(dict.fromkeys(array))


def consistent(assignment):
    """
    Check assignment of sudoku grid for consistency
    """
    # reshade 1d assignment to 2d
    assignment = np.reshape(assignment, (FIELD_SIZE, FIELD_SIZE))
    rows = [[] for _ in range(FIELD_SIZE)]
    cols = [[] for _ in range(FIELD_SIZE)]
    groups = [[[] for _ in range(GROUP_SIZE)] for _ in range(GROUP_SIZE)]
    for index, entry in np.ndenumerate(assignment):
        if entry.value is not None:
            # add value to groups
            rows[index[0]].append(entry.value)
            cols[index[1]].append(entry.value)
            group_nr_x = index[0] // GROUP_SIZE
            group_nr_y = index[1] // GROUP_SIZE
            groups[group_nr_x][group_nr_y].append(entry.value)
            # check for duplicates numbers
            if has_duplicates(rows[index[0]]) or has_duplicates(cols[index[1]]) or \
                    has_duplicates(groups[group_nr_x][group_nr_y]):
                return False
    return True


def complete(assignment):
    """
    Check whether all variables in grid are set
    """
    for entry in assignment:
        if entry.value is None:
            return False
    return True


def get_relatives(position):
    """
    Get relatives of field (row, col and group)
    :return: List of relatives (1d coordinates)
    """
    if isinstance(position, int):
        # convert 1d position to 2d
        s_row = position // FIELD_SIZE
        s_col = position % FIELD_SIZE
        position = (s_row, s_col)

    relatives = []
    for row in range(FIELD_SIZE):
        relatives.append((position[0], row))
    for col in range(FIELD_SIZE):
        relatives.append((col, position[1]))
    group_x = position[0] // GROUP_SIZE
    group_y = position[1] // GROUP_SIZE
    for row in range(group_x * GROUP_SIZE, (group_x + 1) * GROUP_SIZE):
        for col in range(group_y * GROUP_SIZE, (group_y + 1) * GROUP_SIZE):
            relatives.append((row, col))

    # convert position of relatives to 1d
    for index, item in enumerate(relatives):
        relatives[index] = item[0] * GROUP_SIZE * GROUP_SIZE + item[1]
    return list(set([i for i in relatives]))


class SudokuCSP:
    def __init__(self, heu, deg, inf):
        self.USE_HEURISTIC = heu
        self.USE_DEGREE = deg
        self.USE_FORWARD_CHECKING = inf

    def variables(self, assignment):
        """
       Get unset variable for backtracking search
       :return: unset variable (first one or MRV)
       """
        if not self.USE_HEURISTIC:
            for index, var in enumerate(assignment):
                if var.value is None:
                    # first unset variable
                    return index
        # usage of MRV heuristic
        unset = []
        unset_min_possible = sys.maxsize
        for index, var in enumerate(assignment):
            if var.value is None:
                # iterate over all unset values
                possible_values = 0
                for val in var.domain:
                    # check all values for validity
                    assignment[index].setValue(val)
                    if consistent(assignment):
                        possible_values += 1
                    assignment[index].setValue(None)
                if possible_values < unset_min_possible:
                    # only keep the entry with the lowest amount of possible values
                    unset_min_possible = possible_values
                    unset.clear()
                    unset.append(index)
                elif possible_values == unset_min_possible:
                    unset.append(index)
        if self.USE_DEGREE and len(unset) > 1:
            unset_weight = {}
            for entry in unset:
                constraints_to_unset = 0
                for relative in get_relatives(entry):
                    if assignment[relative].value is None:
                        # only count unset neighbors
                        constraints_to_unset += 1
                unset_weight[entry] = constraints_to_unset
            unset_sorted = dict(sorted(unset_weight.items(), key=lambda item: item[1]))
            return list(unset_sorted)[-1]
        # otherwise return first element
        return unset[0]

    def inference(self, assignment, last_position):
        """
        Inference step for backtracking search
        """
        if self.USE_FORWARD_CHECKING:
            for relative_index in get_relatives(last_position):
                relative = assignment[relative_index]
                if relative.value is None:
                    valid_value = False
                    for value in relative.domain:
                        # check each value for validity
                        assignment[relative_index].setValue(value)
                        if consistent(assignment):
                            # relative has valid assignment
                            valid_value = True
                        assignment[relative_index].setValue(None)
                    if not valid_value:
                        return False
        return True
