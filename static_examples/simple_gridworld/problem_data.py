'''
Defining the problem data for the example.
'''

MAZEFILE = 'maze.txt'

INIT = [(1,0)]
GOALS = [(0,2)]
int_1 = (0,0)
int_2 = (1,2)

INTS = {int_1: 'I_1', int_2: 'I_2'}

SYS_FORMULA = 'F(goal)'
TEST_FORMULA = 'F(I_1) & F(I_2)'
