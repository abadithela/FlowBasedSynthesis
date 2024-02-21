"""
File to test the abstract plotting utilities in plotting.py and illustrate cuts on the graph
"""

import networkx as nx
from products import async_example, sync_example
from plotting import GraphPlot
import pdb

example = "sync"
if example == "async":
    system, aut, prod_graph = async_example()
    graph_plot = GraphPlot(prod_graph, system, aut)

    # edge to cut:
    # (x,y) is the node where x increases along the right hand side of the grid, and y increases downwards
    edge = ((1,1), (1,2))
    graph_plot.plot_cut_prod_graph(edge)
    pdb.set_trace()

# Edge to cuts:
else:
    system, aut, prod_graph = sync_example()
    graph_plot = GraphPlot(prod_graph, system, aut)

    # edge to cut:
    # (x,y) is the node where x increases along the right hand side of the grid, and y increases downwards
    edge = ((1,1), (1,2))
    graph_plot.plot_cut_prod_graph(edge)
    pdb.set_trace()