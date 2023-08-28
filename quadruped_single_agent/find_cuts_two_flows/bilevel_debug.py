'''
Script to debug pyomo and library not found error
'''
# Solve the bilevel optimization as LFP (Linear Fractional Program) to
# route the flow through the vertices satisfying the test specification
# J. Graebener, A. Badithela

from ipdb import set_trace as st
from pao.pyomo import *
import pyomo.environ as pyo
from pyomo.opt import SolverFactory
import pao

def solve_bilevel():
    model = pyo.ConcreteModel()
    # 'ft': tester flow, and d: cut values
    model.x = pyo.Var(bounds=(2,6))
    model.y = pyo.Var()

    # Introduce SUBMODEL
    # fixed variables defined by the upper level
    fixed_variables = [model.x, model.y]

    # Submodel - variables defined in the inner problem
    model.L = SubModel(fixed=fixed_variables)
    model.L.z = pyo.Var(bounds=(0,None)) 

    # Upper level objective and constraints:
    model.o = pyo.Objective(expr=model.x + 3*model.L.z, sense=pyo.minimize)
    model.c = pyo.Constraint(expr= model.x + model.y == 10)

    # Lower level objective and constraints:
    model.L.o = pyo.Objective(expr=model.L.z, sense=pyo.maximize)
    model.L.c1 = pyo.Constraint(expr= model.x + model.L.z <= 8)
    model.L.c2 = pyo.Constraint(expr= model.x + 4*model.L.z >= 8)
    model.L.c3 = pyo.Constraint(expr= model.x + 2*model.L.z <= 13)

    opt = pao.Solver("pao.pyomo.FA")
    results = opt.solve(model)

    # with Solver('pao.pyomo.REG') as solver:
    #     results = solver.solve(model, tee=True)

    # model.pprint()
    x = model.x.value
    y = model.y.value
    z = model.L.z.value

    return x,y,z

if __name__ == "__main__":
    solve_bilevel()