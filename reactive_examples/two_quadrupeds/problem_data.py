'''
Defining the problem data for the example.
'''

MAZEFILE = 'maze.txt'

INIT = [(6,0)]
GOALS = [(0,0)]
int_1 = (1,4)
int_2 = (3,0)
int_3 = (5,4)

INTS = {int_1: 'int_1', int_2: 'int_2', int_3: 'int_3'}

SYS_FORMULA = 'F(goal)'
TEST_FORMULA = 'F(int_1) & F(int_2) & F(int_3)'
