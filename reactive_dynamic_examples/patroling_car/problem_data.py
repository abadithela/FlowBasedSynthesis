'''
Defining the problem data for the example.
'''

MAZEFILE = 'maze.txt'
MAX_FUEL = 10

INIT = [((5,5), MAX_FUEL)]
GOALS = [((5,0),f) for f in range(0, MAX_FUEL)]

LOW_FUEL = []
for z in range(0,6):
    for x in range(0,6):
        for f in range(1,min(((5-z)+x-1), MAX_FUEL)):
            LOW_FUEL.append(((z,x),f))

LOW_FUEL = list(set(LOW_FUEL))
EMPTY = [((x,y),0) for x in range(0,6) for y in range(0,6)]

INTS = {}
INTS.update({pos: 'lowfuel' for pos in LOW_FUEL})
INTS.update({pos: 'empty' for pos in EMPTY})

SYS_FORMULA = 'F(goal) & G!(empty)'
TEST_FORMULA = 'F(lowfuel)'

STATIC_AREA = [((z,x),f) for z in range(0,6) for x in range(0,6) for f in range(0, MAX_FUEL+1) if not x == 2]
