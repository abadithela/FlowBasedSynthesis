from automata import Automata
from example_automata import *
import pdb

Q, qinit, AP, tau, Acc = eventually()
Aut_ev = Automata(Q, qinit, AP, tau, Acc)

Q, qinit, AP, tau, Acc, AccSets_dict, Qdict = async_eventually()
Aut_async_ev = Automata(Q, qinit, AP, tau, Acc)
pdb.set_trace()