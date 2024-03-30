'''
Defining the problem data for the example.
'''

INIT = ['init']
GOALS = ['goal']
int_1 = ('d1')
int_2 = ('d2')
int_3 = ('p1')
int_4 = ('p2')

INTS = {int_1: 'door_1', int_2: 'door_2', int_3: 'door_1', int_4: 'door_2'}

SYS_FORMULA = 'F(goal)'
TEST_FORMULA = 'F(door_1) & F(door_2)'

# map for simulation trace
MAP = {'init': (0,1), 'd1': (1,0), 'd2': (1,1), 'int_goal': (3,1), \
        'p1': (2,0), 'p2': (2,1), 'goal': (0,1)}
# init: in the lab
# d1, d2: at door 1 or 2 inside lab
# p1, p2: at door 1 and 2 in hallway
# int_goal: in hallway with beaver
# goal: in lab with beaver
