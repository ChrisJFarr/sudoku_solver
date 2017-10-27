# Create Solution class


class Solution:
    def __init__(self):
        self.assignments = []
        self._rows = 'ABCDEFGHI'
        self._cols = '123456789'
        # Declare initial variables, set to None for now.
        self.boxes = None
        self.row_units = None
        self.column_units = None
        self.square_units = None
        self.diag_units = None
        self.unitlist = None
        self.units = None
        self.peers = None
        # Set values for initial variables
        self.setup()

    """
    Utility Methods
    """

    @staticmethod
    def cross(a, b):
        return [s + t for s in a for t in b]

    def setup(self):
        """
        Initial setup for building the game board variables.
        :return: None, all values are attributes which are set in this method.
        """
        # Pulling private attributes and setting to local variable for rows and cols
        rows = self._rows
        cols = self._cols

        # Create list of all boxes
        boxes = self.cross(rows, cols)

        # Create initial variables
        row_units = [self.cross(r, cols) for r in rows]
        column_units = [self.cross(rows, c) for c in cols]
        square_units = [self.cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]
        diag_units = list()
        diag_units.append([r + c for r, c in zip(rows, cols)])
        diag_units.append([r + c for r, c in zip(rows, "".join(sorted([i for i in cols], reverse=True)))])

        # Build unit list variations
        unitlist = row_units + column_units + square_units + diag_units
        units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
        peers = dict((s, set(sum(units[s], [])) - set([s])) for s in boxes)

        # Set class attributes
        self.boxes = boxes
        self.row_units = row_units
        self.column_units = column_units
        self.diag_units = diag_units
        self.unitlist = unitlist
        self.units = units
        self.peers = peers

        return None

    def assign_value(self, values, box, value):
        """
        Update a values dictionary.
        Assigns a value to a given box. If it updates the board record it.
        :arg values: The values dictionary to be updated
        :arg box: The name of the box to be updated within the values dictionary.
        :arg value: The new value to set
        :return: The updated values dictionary.
        """
        # If the value of values[box] equals the new value, stop and return values
        if values[box] == value:
            return values

        # Set values[box] to the new value
        values[box] = value
        # If it's now solved, store values dict in self.assignments
        if len(value) == 1:
            self.assignments.append(values.copy())

        return values

    def grid_values(self, grid):
        """
        Convert grid into a dict of {square: char} with '123456789' for empties.
        :argument: grid(string) - A grid in string form.
        :return: values

            A grid in dictionary form
                Keys: The boxes, e.g., 'A1'
                Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
        """
        chars = []
        digits = '123456789'

        for c in grid:
            # Replace periods with digits, add to chars list
            chars.append(c.replace(".", digits))

        assert len(chars) == 81
        values = dict(zip(self.boxes, chars))

        return values

    def display(self, values):
        """
        Display the values as a 2-D grid.
        Args: values(dict): The sudoku in dictionary form
        """
        width = 1 + max(len(values[s]) for s in self.boxes)
        line = '+'.join(['-' * (width * 3)] * 3)
        for r in self._rows:
            print(''.join(values[r + c].center(width) + ('|' if c in '36' else '')
                          for c in self._cols))
            if r in 'CF':
                print(line)
        return None

    """
    Solution Methods
    """

    def solve(self, grid):
        """
        Find the solution to a Sudoku grid.
        Args:
            grid(string): a string representing a sudoku grid.
                Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
        Returns:
            The dictionary representation of the final sudoku grid. False if no solution exists.
        """
        values = self.grid_values(grid)
        values = self.search(values)

        return values

    def search(self, values):
        """
        Use depth first searching when stuck using just the conventional methods of
        only-choice, eliminate, and naked-twins.
        :param values: Starting values dictionary
        :return: Solved values dictionary, or False if solution is not possible.
        """
        # First, reduce the puzzle using the previous function
        values = self.reduce_puzzle(values)
        if values is False:
            return False  # Failed earlier
        if all(len(values[s]) == 1 for s in self.boxes):
            return values  # Solved! Return self.values
        # Choose one of the unfilled squares with the fewest possibilities
        n, s = min((len(values[s]), s) for s in self.boxes if len(values[s]) > 1)
        # Now use recurrence to solve each one of the resulting sudokus, and
        for value in values[s]:
            new_sudoku = values.copy()
            new_sudoku[s] = value
            attempt = self.search(new_sudoku)
            if attempt:
                return attempt

    def reduce_puzzle(self, values):
        """
        Reduce the puzzle using three strategies as far as possible.
        Strategies include only-choice, eliminate, and naked twins.
        :return: Boolean, indicating if the puzzle is still solveable, values dictionary
        """
        if isinstance(values, dict):
            stalled = False
            while not stalled:
                solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
                values = self.only_choice(values)  # Set any values that are the only box to contain that digit
                values = self.eliminate(values)  # Eliminate any solved values from peer possibilities
                values = self.naked_twins(values)  # Perform naked twins strategy
                solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
                stalled = solved_values_before == solved_values_after
                if len([box for box in values.keys() if len(values[box]) == 0]):
                    return False
        else:
            # Ensuring the correct parameter type is passe
            raise TypeError("The values parameter must be of type dict.")

        return values

    def only_choice(self, values):
        """
        For each unit in unitlist, if any digit occurs as a possibility in only one box, set
        the value of that box to that digit
        :return: Updated values dictionary
        """
        for unit in self.unitlist:
            for digit in '123456789':
                dplaces = [box for box in unit if digit in values[box]]
                if len(dplaces) == 1:
                    values = self.assign_value(values, dplaces[0], digit)
        return values

    def eliminate(self, values):
        """
        Eliminate solved digits from their peers
        :return: Updated values dictionary
        """
        solved_values = [box for box in values.keys() if len(values[box]) == 1]
        for box in solved_values:
            digit = values[box]
            for peer in self.peers[box]:
                value = values[peer].replace(digit, "")
                if value != values[peer]:
                    values = self.assign_value(values, peer, value)
        return values

    def naked_twins(self, values):
        """Eliminate values using the naked twins strategy.
        :argument: self, values(dict): a dictionary of
        the form {'box_name': '123456789', ...}

        :return:values dictionary with the naked twins eliminated from peers.
        """
        # Search one unit at a time
        for unit in self.unitlist:

            # Create list of boxes for all that contain 2
            twos = [box for box in unit if len(values[box]) == 2]

            for item in twos:  # Loop through list of twos
                i = twos.index(item)  # Store the index of item
                twos.pop(i)  # Pop item from twos list using index

                for match_check in twos:  # Loop through remaining boxes in twos list
                    # Check to see if item values match with match_check
                    if values[item] == values[match_check]:
                        i = twos.index(match_check)  # Store the index of match_check in twos list
                        twos.pop(i)  # Pop the match_check element from the twos list
                        single_twin = values[item]  # Store the value of the naked twins

                        for box in [box for box in unit if box not in [item, match_check]]:  # Loop through the unit
                            # Remove twin values
                            value = "".join([v for v in values[box] if v not in single_twin])
                            values = self.assign_value(values, box, value)

        return values


# Since I used class had to pull out methods and store in variables
solution = Solution()
naked_twins = solution.naked_twins
solve = solution.solve
assign_value = solution.assign_value



if __name__ == '__main__':

    solution = Solution()
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    solved_puzzle = solution.solve(diag_sudoku_grid)
    solution.display(solved_puzzle)

    try:
        from visualize import visualize_assignments

        visualize_assignments(solution.assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')



