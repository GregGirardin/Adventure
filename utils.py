import math
import random
from collections import defaultdict
PI = 3.14159
TAU = 2 * PI
EFFECTIVE_ZERO = .00001

class Point():
  def __init__ (self, x, y):
    self.x = float(x)
    self.y = float(y)

  def distanceTo (self, p): # p is another Point
     return math.sqrt ((self.x - p.x) ** 2 + (self.y - p.y) ** 2)

  def directionTo (self, p): # p is another point
    cx = p.x - self.x
    cy = p.y - self.y

    magnitude = math.sqrt (cx ** 2 + cy ** 2)

    if magnitude < EFFECTIVE_ZERO:
      direction = 0
    else:
      if math.fabs (cx) < EFFECTIVE_ZERO:
        if cy > 0:
          direction = -PI / 2
        else:
          direction = PI / 2
      elif cx > 0:
        direction = math.atan (cy / cx)
      else:
        direction = PI + math.atan (cy / cx)

    return direction

# https://gist.github.com/kachayev/5990802
from collections import defaultdict
from heapq import *

def spf (edges, f, t):
  g = defaultdict (list)
  for l,r,c in edges:
    g [l].append ((c,r))

  q, seen = [(0,f,())], set()
  while q:
    (cost, v1, path) = heappop(q)
    if v1 not in seen:
      seen.add(v1)
      path = (v1, path)
      if v1 == t:
        return (cost, path)

      for c, v2 in g.get(v1, ()):
        if v2 not in seen:
          heappush(q, (cost + c, v2, path))

  return float("inf")

def testSPF():
  edges = [
      ("A", "B", 7),
      ("A", "D", 5),
      ("B", "C", 8),
      ("B", "D", 9),
      ("B", "E", 7),
      ("C", "E", 5),
      ("D", "E", 15),
      ("D", "F", 6),
      ("E", "F", 8),
      ("E", "G", 9),
      ("F", "G", 11)
  ]

  print "=== Dijkstra ==="
  print edges
  print "F -> G:"
  print spf(edges, "F", "G")