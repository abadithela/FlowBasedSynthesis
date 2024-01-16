'''
Defining the problem data for the example.
'''

MAZEFILE = 'maze.txt'

INIT = [(4,4)]
GOALS = [(4,0)]

GOLD = (0,2)
BANK = (4,2)

INTS = {GOLD: 'gold', BANK: 'bank'}

SYS_FORMULA = 'G(gold -> F(bank)) & (F(goal))'
TEST_FORMULA = 'F(gold)'
