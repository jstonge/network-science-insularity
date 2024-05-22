
# Experiment 1: 
# What if a 100 communities. 
# Assume that some communities start well connected, say network science and sociology.
# Then one community, network science, stop sending links to the other community.
# What is the effect of this on clustering?

import igraph as ig
import leidenalg as la
import matplotlib.pyplot as plt
import numpy as np

ig.Graph.SBM(n=100, pref_matrix=np.matrix([[0.9, 0.1], [0.1, 0.9]]), block_sizes=[50, 50])

partition = la.find_partition(G, la.ModularityVertexPartition)

ig.plot(partition) 