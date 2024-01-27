# script to interface with the quadruped

def quadruped_move(name, move_to):
    print('Quadruped '+name+' move to {}'.format(move_to))
    # change orientation towards next cell first? Then move one grid cell forward.
