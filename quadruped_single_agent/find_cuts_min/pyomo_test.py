import pyomo.environ as pe
import pao

M = pe.ConcreteModel()

M.w = pe.Var([1,2], within=pe.Binary)
M.x = pe.Var(bounds=(2,6))
M.y = pe.Var()
M.z = pe.Var(bounds=(0,None))

M.o = pe.Objective(expr=M.x + 3*M.z+5*M.w[1], sense=pe.minimize)
M.c1 = pe.Constraint(expr= M.x + M.y == 10)
M.c2 = pe.Constraint(expr= M.w[1] + M.w[2] >= 1)

M.L = pao.pyomo.SubModel(fixed=[M.x,M.y,M.w])
M.L.o = pe.Objective(expr=M.z, sense=pe.maximize)
M.L.c1 = pe.Constraint(expr= M.x + M.w[1]*M.y + M.w[2]*M.y <= 8)
M.L.c2 = pe.Constraint(expr= M.x + 4*M.z >= 8)
M.L.c3 = pe.Constraint(expr= M.x + 2*M.w[2]*M.z <= 13)
# M.L.c4 = pe.Constraint(expr= sum(M.w[i]*M.y for i in range(1,3)) <= M.z)

opt = pao.Solver("pao.pyomo.FA", linearize_bigm=100)
results = opt.solve(M)
print(M.x.value, M.y.value, M.z.value, M.w[1].value, M.w[2].value)
