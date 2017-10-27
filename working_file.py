from tests.test_solution import TestNakedTwins, TestDiagonalSudoku

testing = TestNakedTwins()
testing.test_naked_twins()

testing = TestDiagonalSudoku()
testing.test_solve()

import solution
solution.naked_twins()

# Testing
values = solution.solution.grid_values("9.1....8.8.5.7..4.2.4....6...7......5..............83.3..6......9................")
solution.solution.display(solution.naked_twins(values))
