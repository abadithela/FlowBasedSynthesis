'''
System and tester agents.
Josefine Graebener
July 2023
'''
from __future__ import print_function
import logging
from tulip import transys, spec, synth
from tulip import dumpsmach
from ipdb import set_trace as st
import random
# from quadruped_interface import quadruped_move

def dropStr(namestr, xstr, ystr, curpos, lo=0,hi=10,drop=0):
    dropstr = '('
    for i in range(lo+drop,hi+1):
        samestr = '(%s=%d && %s=%d && %s=%d)' % (namestr,i, xstr, curpos[0],ystr,curpos[1])
        dropstr += '('+samestr +' -> X('+ samestr +' || (!(%s=%d && %s=%d) && %s=%d))) && ' % (xstr, curpos[0],ystr,curpos[1],namestr,i-drop) # fuel level stays the same, drops if drop>0
    dropstr = dropstr[0:len(dropstr)-4] # remove trailing ' && '
    dropstr += ')'
    return dropstr

def refuelStr(namestr, xstr, ystr, curpos,hi=10,drop=0):
    dropstr = '('
    lowstr = '(%s<%d && %s=%d && %s=%d)' % (namestr, hi, xstr, curpos[0],ystr,curpos[1])
    fullstr = '(%s=%d && %s=%d && %s=%d)' % (namestr, hi, xstr, curpos[0],ystr,curpos[1])
    dropstr += '(('+lowstr+' -> X'+fullstr+') && ('+fullstr +' -> X('+ fullstr +' || (!(%s=%d && %s=%d) && %s=%d))))' % (xstr, curpos[0],ystr,curpos[1],namestr,hi-drop) # fuel level stays the same, drops if drop>0
    dropstr += ')'
    return dropstr

class Tester:
    def __init__(self, name, pos):
        self.name = name
        self.q = pos
        self.x = pos[0]
        self.y = pos[1]

    def move(self,cell):
        (self.x, self.y) = cell
        self.q = (self.x, self.y)

    def random_move(self, car):
        if self.x == 0:
            if random.random() < 0.5:
                if not (self.x + 1,self.y) == car:
                    self.x = self.x + 1
        elif self.x == 4:
            if random.random() < 0.5:
                if not (self.x - 1,self.y) == car:
                    self.x = self.x - 1
        else:
            p_rand = random.random()
            if p_rand < 0.3:
                if not (self.x - 1,self.y) == car:
                    self.x = self.x - 1
            elif p_rand < 0.6:
                    self.x = self.x
            else:
                if not (self.x + 1,self.y) == car:
                    self.x = self.x + 1
        self.q = (self.x, self.y)

class Car:
    def __init__(self, name, pos, goal, maze):
        self.name = name
        self.s = pos
        self.x = pos[0]
        self.y = pos[1]
        self.init = pos
        self.goal = goal
        self.index = 0
        self.maze = maze
        self.fuelmax = 8
        self.fuel = self.fuelmax
        self.fuelmin = 0
        self.controller = self.find_controller(maze)

    def find_controller(self,maze):
        logging.basicConfig(level=logging.WARNING)
        logging.getLogger('tulip.spec.lexyacc').setLevel(logging.WARNING)
        logging.getLogger('tulip.synth').setLevel(logging.WARNING)
        logging.getLogger('tulip.interfaces.omega').setLevel(logging.WARNING)

        # system variables x,y, fuel
        sys_vars = {}
        sys_vars['x'] = (0,maze.len_x-1)
        sys_vars['y'] = (0,maze.len_y-1)
        sys_vars['fuel'] = (0,self.fuelmax)
        # Initial conditions
        sys_init = {'x = ' + str(self.x) +' && y = ' + str(self.y) +' && fuel = '+ str(self.fuel)}
        #
        sys_prog = set()
        sys_prog |= {'(x = ' + str(self.goal[0])+' && y = ' + str(self.goal[1]) + ')'}
        #
        sys_safe = set()
        # add the grid dynamics for the system
        dynamics_spec =  maze.transition_specs('x','y')
        sys_safe |= dynamics_spec
        # never run out of fuel
        sys_safe |= {'fuel > '+str(self.fuelmin)}
        # add collision constraints
        safe_spec = set()
        for x in range(0,maze.len_x):
            safe_spec |= {'(X_t = '+str(x)+' && Y_t = 1) -> X(!(x = '+str(x)+' && y = 1))'}
        sys_safe |= safe_spec
        #
        fuel_spec = set()
        for x in range(0,maze.len_x):
            for y in range(0,maze.len_y):
                if (x,y) == maze.refuel:
                    fuelstr = {refuelStr('fuel', 'x', 'y', (x,y), self.fuelmax, 1)}
                    # fuelstr = {'(x='+str(x)+' && y='+str(y)+' && fuel < '+str(self.fuelmax)+')-> X(x='+str(x)+' && y='+str(y)+' && fuel = '+str(self.fuelmax)+')'}
                else:
                    fuelstr = {dropStr('fuel', 'x', 'y', (x,y), self.fuelmin, self.fuelmax, 1)}
                fuel_spec |= fuelstr
        sys_safe |= fuel_spec


        # setup environment specs
        env_vars = {}
        env_vars['X_t'] = (0,maze.len_x-1)
        env_vars['Y_t'] = (0,maze.len_y-1)
        # init
        env_init = {'X_t = '+str(maze.tester_init[0])+' && Y_t = '+str(maze.tester_init[1])}
        # progress
        env_prog = set()
        # tester will patrol up and down the column
        env_prog |= {'(X_t = 0 && Y_t = 1) || (X_t = 4 && Y_t = 1)'}
        # safety
        env_safe = set()
        env_safe |= {'(Y_t = 1)'} # stick to column 1
        # tester will stick to grid dynamics
        dynamics_spec = set()
        for x in range(0,maze.len_x):
            next_str = ''
            for next_x in range(max(0,x-1),min(maze.len_x-1,x+1)+1):
                next_str += '(X_t = '+str(next_x)+') || '
            next_str = next_str[0:len(next_str)-4] # remove trailing ' || '
            dynamics_spec |= {'(X_t = '+str(x)+' && Y_t = 1) -> X(Y_t = 1 && ('+next_str+'))'}
        env_safe |= dynamics_spec
        #Tester will never crash into system
        collision_spec = set()
        for x in range(0,maze.len_x):
                collision_spec |= {'(x = '+str(x)+' && '+'y = 1) -> X(!(X_t = '+str(x)+' && '+'Y_t = 1))'}
        env_safe |= collision_spec


        # get GR1 spec
        spc = spec.GRSpec(env_vars, sys_vars, env_init, sys_init,
                        env_safe, sys_safe, env_prog, sys_prog)

        print(spc.pretty())

        spc.moore = False
        spc.qinit = r'\A \E'
        if not synth.is_realizable(spc, solver='omega'):
            print("Not realizable.")
            st()
        else:
            ctrl = synth.synthesize(spc, solver='omega')
        # dump the controller
        controller_namestr = "robot_controller"+str(self.index)+".py"
        dumpsmach.write_python_case(controller_namestr, ctrl, classname="AgentCtrl")
        # # load the controller
        # from controller_namestr import AgentCtrl
        # M = AgentCtrl()
        self.index += 1

        # print(dumpsmach.python_case(g, classname='AgentCtrl', start=))
        exe_globals = dict()
        exec(dumpsmach.python_case(ctrl, classname='AgentCtrl'), exe_globals)
        M = exe_globals['AgentCtrl']()  # previous line creates the class `AgentCtrl`
        return M

    def agent_move(self, tester_pos):
        # st()
        output = self.controller.move(tester_pos[0],tester_pos[1])
        self.x = output['x']
        self.y = output['y']
        self.fuel = output['fuel']
        self.s = (self.x,self.y)
        # quadruped_move((self.y,self.x))
