from tests.test_solution import TestNakedTwins, TestDiagonalSudoku

testing = TestNakedTwins()
testing.test_naked_twins()

testing = TestDiagonalSudoku()
testing.test_solve()


