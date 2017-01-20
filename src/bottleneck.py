import argparse
import numpy as np
from matplotlib import pyplot as plt
from ortools.graph import pywrapgraph

import utils


def get_args():
  parser = argparse.ArgumentParser(description='Compute bottleneck distance')
  parser.add_argument('--galaxy1', dest='galaxy1', default='train/diags/galaxy1.p')
  parser.add_argument('--galaxy2', dest='galaxy2', default='train/diags/galaxy2.p')
  parser.add_argument('--ignore-near-diag', dest='ignore_near_diag', action='store_true',
                      help="Ignore entries just above diagonal")

  return parser.parse_args()


# vertices = coords of non zero entries
def get_verts(diag):
   return [(ix, val.item()) for (ix, val) in np.ndenumerate(diag) if val > 0]


# multiplied by 2 to keep unit costs
def dist_from_diag(p):
  return p[1] - p[0]


# multiplied by 2 to keep unit costs
def dist(p1, p2):
  return 2 * max(abs(p1[0] - p2[0]), abs(p1[1] - p2[1]))


# used for debugging
def write_flow(solver, parts):
  num_to_vertex = parts[0] + parts[1] + ["d0"] + ["d1"]

  print(' Edge    Flow   Cost')
  for i in range(solver.NumArcs()):
    if solver.Flow(i) > 0:
      tail = num_to_vertex[solver.Tail(i)]
      head = num_to_vertex[solver.Head(i)]
      cost = solver.Flow(i) * solver.UnitCost(i)
      print('{} -> {}   {}    {}'.format(
          tail,
          head,
          solver.Flow(i),
          cost))


# used when ignore-near-diag is set
# I wrote why I added this function in a comment inside utils.get_diagram
def remove_near_diag(diag):
  res = np.copy(diag)
  for ((x,y), val) in np.ndenumerate(diag):
    if x + 1 == y:
      res[x,y] = 0
  return res


def get_distance(diag1, diag2, ignore_near_diag=False):
  diags = [diag1, diag2]
  if ignore_near_diag:
    diags = [remove_near_diag(d) for d in diags]
  solver = pywrapgraph.SimpleMinCostFlow()

  # this will be a bipartite graph
  parts = [get_verts(d) for d in diags]
  ns = [len(p) for p in parts]
  n = sum(ns)
  tot_vals = [sum(val for (_, val) in p) for p in parts]
  tot_val = sum(tot_vals)
  # we don't need larger infinity
  INF = tot_val + 1

  diags = [n, n + 1]
  
  # these functions are described here: https://developers.google.com/optimization/flow/maxflow
  solver.SetNodeSupply(diags[0], -tot_vals[0])
  solver.SetNodeSupply(diags[1], tot_vals[1])
  # thanks to this edge the min cost flow is also a maximal flow, a requirement of the solver
  solver.AddArcWithCapacityAndUnitCost(diags[1], diags[0], INF, 0)
  
  for i, (ix, val) in enumerate(parts[0]):
    solver.SetNodeSupply(i, val)
    solver.AddArcWithCapacityAndUnitCost(i, diags[0], INF, dist_from_diag(ix))

  for j, (jx, val) in enumerate(parts[1], ns[0]):
    solver.SetNodeSupply(j, -val)
    solver.AddArcWithCapacityAndUnitCost(diags[1], j, INF, dist_from_diag(jx))
  
  for i, (ix, val) in enumerate(parts[0]):
    for j, (jx, val) in enumerate(parts[1], ns[0]):
      solver.AddArcWithCapacityAndUnitCost(i, j, INF, dist(ix, jx))
  

  assert (solver.Solve() == solver.OPTIMAL)

  # write_flow(solver, parts) 

  return solver.OptimalCost() / 2.0


if __name__ == '__main__':
  args = get_args()
  diags = [utils.read_diagram(fn) for fn in (args.galaxy1, args.galaxy2)]
  for d in diags:
    print(d)
  
  distance = get_distance(d[0], d[1], ignore_near_diag=args.ignore_near_diag)
  print(distance)
