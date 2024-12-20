'''
Defining the problem data for the example.
'''

MAZEFILE = 'maze.txt'
MAX_FUEL = 10

INIT = [((5,0),MAX_FUEL)] 
GOALS = [((0,0),k) for k in range(0,MAX_FUEL)]

LOW_FUEL = []

for z in range(0,6):
    for x in range(0,6):
        for f in range(1,min(z+x-1,MAX_FUEL)):
            LOW_FUEL.append(((z,x),f))

LOW_FUEL = list(set(LOW_FUEL))
# LOW_FUEL_S = [((z,x),f) for z in range(3,5) for x in range(0,5) for f in range(2)]
# LOW_FUEL = list(set(LOW_FUEL_S + [((z,x),f) for z in range(0,5) for x in range(3,5) for f in range(0,2)]))
EMPTY = [((x,y),0) for x in range(0,6) for y in range(0,6)]
ICE = [((1,4), f) for f in range(0,MAX_FUEL)]
ROCK = [((4,1), f) for f in range(0,MAX_FUEL)]
DROPOFF_1 = [((4,5), f) for f in range(0,MAX_FUEL)]
DROPOFF = DROPOFF_1 + [((3,0), f) for f in range(0,MAX_FUEL)]

SAMPLE = ICE + ROCK

INTS = {}
INTS.update({pos: 'lowfuel' for pos in LOW_FUEL})
INTS.update({pos: 'unsafe' for pos in EMPTY})
INTS.update({pos: 'ice' for pos in ICE})
INTS.update({pos: 'rock' for pos in ROCK})
INTS.update({pos: 'dropoff' for pos in DROPOFF})
# INTS.update({pos: 'sample' for pos in SAMPLE})

# SYS_FORMULA = 'F(goal) & G(!(unsafe)) & G((rock) -> F(dropoff))'
# TEST_FORMULA = 'F(lowfuel) & F(rock)'

SYS_FORMULA = 'F(goal) & G(!(unsafe)) & G((ice || rock) -> F(dropoff))'
TEST_FORMULA = 'F(lowfuel) & F(ice) & F(rock)'
