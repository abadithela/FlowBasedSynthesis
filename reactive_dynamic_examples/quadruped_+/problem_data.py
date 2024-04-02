'''
Defining the problem data for the example.
'''

MAZEFILE = 'maze.txt'

INIT = [(4,0)]
GOALS = [(0,4)]
int_1 = (3,4)
int_2 = (1,0)

INTS = {int_1: 'I_1', int_2: 'I_2'}

SYS_FORMULA = 'F(goal)'
TEST_FORMULA = 'F(I_1) & F(I_2)'

static_area = [(0,0), (0,1), (1,0), (3,0), (4,0), (4,1), (0,3), (0,4), (1,4), (3,4), (4,4), (4,3)]

STATIC_AREA = static_area
