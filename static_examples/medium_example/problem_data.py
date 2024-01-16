'''
Defining the problem data for the example.
'''

MAZEFILE = 'maze.txt'

INIT = [(2,2)]
GOALS = [(0,0), (0,4)]
INT = [(0,2), (2,0), (2,4)]

INTS = {pos: 'int' for pos in INT}

SYS_FORMULA = 'F(goal)'
TEST_FORMULA = 'F(int)'
