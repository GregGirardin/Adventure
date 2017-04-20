import math
import random
from collections import defaultdict
from constants import *

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

# Check if rectangles r1 and r2 overlap
def checkOverlap (r1a,  r1b,  r2a,  r2b):
  # If one rectangle is on left side of other
  if ((r1a.x >= r2a.x and r1a.x < r2b.x) or
      (r2a.x >= r1a.x and r2a.x < r1b.x)) and \
     ((r1a.y > r2b.y and r1a.y <= r2a.y) or
      (r2a.y > r1b.y and r2a.y <= r1a.y )):
    return False
  return True

'''
Subdivide into squares of equal cost. This is expensive.

Group into square areas of the same cost
WAY fewer vertices though each can have more edges

Ex: turn 16 vertices into 4
1 1 2 2
1 1 2 2
3 3 4 4
3 3 4 4

Actual world map is 200x200 = 40,000 vertices. Want to cut down to ~1000
'''
def subdivideMap (tmxMap, costList):

  pointMap = {} # Dict (x,y) = cost for every valid tile
  for x in range (0, tmxMap.width):
    for y in range (0, tmxMap.height):
      tileInfo = tmxMap.get_tile_image (x, y, LGROUND)
      if tileInfo:
        txy = (tileInfo [1][0] / TW, tileInfo [1][1] / TW)
        for tCost in costList:
          if txy == (tCost [0], tCost [1]):
            pointMap [(x, y)] = tCost [2]
            break
  print len(pointMap), "Map coordinates."

  # now coalesce pointMap into coalMap
  coalMap = {} # Dict (x,y) = (size, cost)

  # both lists have the same info, just keyed differently
  sizeMap = {} # Dict [size] = list of (x,y) blocks
  posMap  = {} # Dict [(x,y)] = size, same info as sizeMap
  # Used for finding edges and determining the area a point is in.

  # Determine biggest square from every point in map
  for size in range (1, MAX_EDGE_LENGTH + 1):
    sizeMap [size] = []

  print "Subdividing."
  for y in range (0, tmxMap.height):
    if not y % 10:
      print ".", # debug
    for x in range (0, tmxMap.width):
      maxFound = False
      xy = (x,y)
      # find size of block at (x,y)
      if not xy in pointMap.keys():
        continue
      cost = pointMap [xy]
      for edgeLen in range (1, MAX_EDGE_LENGTH + 1):
        for ix in range (0, edgeLen):
          check1 = (x + edgeLen - 1, y + ix)
          check2 = (x + ix, y + edgeLen - 1)
          if not check1 in pointMap.keys() or not check2 in pointMap.keys() or \
            pointMap [check1] != cost or pointMap [check2] != cost:
            maxFound = True
            break
        if maxFound:
          break
      if maxFound:
        edgeLen -= 1
      if edgeLen > MAX_EDGE_LENGTH - 2:
        # process large blocks immediately to speed things up.
        coalMap [xy] = (edgeLen, edgeLen * cost)
        for checkX in range (x, x + edgeLen):
          for checkY in range (y, y + edgeLen):
            del pointMap [(checkX, checkY)]
      else:
        sizeMap [edgeLen].append (xy)
        posMap [xy] = edgeLen
  print
  for size in range (MAX_EDGE_LENGTH, 0, -1):
    print len (sizeMap [size]), size, "blocks"
    while len (sizeMap [size]) > 0:
      block = sizeMap [size].pop (0)
      del posMap [block]
      coalMap [block] = (size, size * pointMap [block])
      # Prune all overlapping blocks.
      # only need to check blocks within a distance that could overlap
      for checkX in range (block [0] - MAX_EDGE_LENGTH, block [0] + size):
        for checkY in range (block [1] - MAX_EDGE_LENGTH, block [1] + size):
          if checkX == block [0] and checkY == block [1]:
            continue # this is us
          xy = (checkX, checkY)
          if xy in posMap.keys():
            chkSize = posMap [xy]
            if checkOverlap (Point (block [0], block [1]),
                             Point (block [0] + size, block [1] + size),
                             Point (checkX, checkY),
                             Point (checkX + chkSize - 1, checkY + chkSize - 1)):
              del posMap [xy]
              sizeMap [chkSize].remove (xy)
  print len (coalMap), "Vertices."
  return coalMap

def areaIdMap (aMap):
  # aMap is a dictionary of areas. return a dictionary of the area ID of every point

  aidMap = {} # Dict [(x,y)] = (x,y) of top left (the area's ID).
  for k,v in aMap.items():
    for x in range (k[0], k[0] + v[0]):
      for y in range (k[1], k[1] + v[0]):
        aidMap [(x,y)] = (k[0], k[1])

  return aidMap

'''
  Return a list of edges

  #(k [0] - 1, k [1] + e), # left # only need a edge per pair, so just go right / down
  #(k [0] + e, k [1] - 1), # above
'''
def mapEdges (aMap, aidMap = None):
  if not aidMap:
    aidMap = areaIdMap (aMap)
  totalEdges = 0
  edges = []
  for k, v in aMap.items():
    for e in range (0, v[0]):
      for p in ((k[0] + v[0] + 1, k[1] + e), # right
                (k[0] + e,        k[1] + v[0] + 1)): # below
        if p in aidMap.keys():
          aid = aidMap [p]
          edge = (k, aid, aMap [k][0] + aMap [aid][0])
          if not edge in edges:
            edges.append (edge)
            totalEdges += 1

  print totalEdges, "edges."
  return edges

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

# def testSPF():
#   edges = [
#       ("A", "B", 7),
#       ("A", "D", 5),
#       ("B", "C", 8),
#       ("B", "D", 9),
#       ("B", "E", 7),
#       ("C", "E", 5),
#       ("D", "E", 15),
#       ("D", "F", 6),
#       ("E", "F", 8),
#       ("E", "G", 9),
#       ("F", "G", 11)
#   ]
#
#   print "=== Dijkstra ==="
#   print edges
#   print "F -> G:"
#   print spf(edges, "F", "G")