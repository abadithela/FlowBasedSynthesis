'''
Defining the problem data for the example.
'''

MAZEFILE = 'maze.txt'

INIT = [((4,0),10)]
GOALS = [((0,0),k) for k in range(0,10)]
INT = [((x,y),z) for x in range(0,4) for y in range(2,5) for z in range(2)]
unsafes = [((x,y),0) for x in range(0,4) for y in range(0,4)]

INTS = {pos: 'int' for pos in INT}
INTS.update({pos: 'unsafe' for pos in unsafes})

SYS_FORMULA = 'F(goal) & G(!(unsafe))'
TEST_FORMULA = 'F(int)'
