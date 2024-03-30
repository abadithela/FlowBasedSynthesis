'''
Defining the problem data for the example.
'''

INIT = ['init']
GOALS = ['goal']
jumps = ['jump1']
lies = ['lie3']
stands = ['stand1', 'stand2', 'stand3']

INTS = {}
INTS.update({jump: 'jump' for jump in jumps})
INTS.update({lie: 'lie' for lie in lies})
INTS.update({stand: 'stand' for stand in stands})


SYS_FORMULA = 'F(goal)'
TEST_FORMULA = 'F(jump) & F(lie) & F(stand)'

# map for simulation trace
MAP = {'init': (0,1), 'p1': (1,0), 'p2': (1,1), 'p3': (1,2), 'jump1': 'jump', 'stand1': 'stand', \
    'stand2': 'stand', 'stand3': 'stand', 'lie3': 'lie',\
    'd1_j': (1,0), 'd1_s': (1,0), 'd2_s': (1,1), 'd3_s': (1,2), 'd3_l': (1,2), 'goal': (2,1)} # to be modified for actual hardware implementation

# init: in the lab
# p1, p2, p3: at door 1, 2, or 3
# stand, lie, jump: motionprims at location
# d1, d2, d3: at door 1, 2, or 3 after motionprim "s,l,j"
# goal: in hallway
