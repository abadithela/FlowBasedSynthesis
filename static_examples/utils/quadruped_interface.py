# script to interface with the quadruped
from ipdb import set_trace as st

def quadruped_move(move_to):
    print('Quadruped move to {}'.format(move_to))
    # change orientation towards next cell first? Then move one grid cell forward.
