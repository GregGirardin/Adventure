#!/usr/bin/python
from PIL import Image, ImageTk
import pytmx
import Tkinter as tk
import time
from constants import *
from utils import *
import math

class WorldEngine ():
  def __init__ (self):
    self.root = tk.Tk()
    self.root.title ("Rogue")
    self.canvas = tk.Canvas (self.root, width = SCREEN_WIDTH, height = SCREEN_HEIGHT)
    self.canvas.pack()

    self.images = []
    self.tkImages = {}
    self.worldMap = pytmx.TiledMap (worldMap)
    self.worldMap.wObjects = [] # characters, objects, etc
    self.curMap = self.worldMap

    self.charImg = self.getTkImg (self.curMap.get_tile_image (0, 0, LCHAR))

    self.curX = INIT_WORLD_X
    self.curY = INIT_WORLD_Y

    self.root.bind ("<Left>",  self.leftHandler)
    self.root.bind ("<Right>", self.rightHandler)
    self.root.bind ("<Up>",    self.upHandler)
    self.root.bind ("<Down>",  self.downHandler)
    self.root.bind ("<Key>",   self.keyHandler)

  # Use SPF to calculate paths by land / water
  # Subdivide into squares which we can directly traverse to next edge.
  # This is expensive so just do at Init.
  def subdivideMap (self, tmxMap, costList):
    '''
    100 nodes, ~400 vertices (real map could be a 200x200=40000 nodes, 160000 edges.
    w w w w w w w w w w
    w w w w w w w w w w
    w w X w w w w w w w
    w w X X w w w w w w
    w w w w X w w w w w
    w w w w w w w w w w
    w w w w w w w w w w
    w w w w w w w w w w

    Group into square areas of the same cost
    WAY fewer nodes though each can have more edges

    16 nodes, ? vertices
    1 1 2 2 3 3 3 3 4 4
    1 1 2 2 3 3 3 3 4 4
    5 5 X 6 3 3 3 3 7 7
    5 5 X X 3 3 3 3 7 7
    8 8 8 8 X 9 9 9 9 a
    8 8 8 8 b 9 9 9 9 c
    8 8 8 8 d 9 9 9 9 e
    8 8 8 8 f 9 9 9 9 g

    If more than one border, use spf to calculate intranode path,
    otherwise routing is straight line within square to edge.

    8 has edges to 5(2), b, d and f.
    Since there are two edges to 5 the route is not determined so use SPF

    '''
    pointMap = {} # Dict (x,y) = cost for every valid tile
    for x in range (0, 50): # tmxMap.width):
      for y in range (0, 50): # tmxMap.height):
        tileInfo = tmxMap.get_tile_image (x, y, LGROUND)
        if tileInfo:
          txy = (tileInfo [1][0] / TW, tileInfo [1][1] / TW)
          for tCost in costList:
            if txy == (tCost [0], tCost [1]):
              print x,y, tCost [2] # debug
              pointMap [(x, y)] = tCost [2]
              break
    print len(pointMap), "Vertices."

    # now coalesce pointMap into coalMap
    coalMap = {} # Dict (x,y) = (size,cost)

    sizeMap = {} # Dict [size] = list of (x,y) blocks
    posMap = {}  # Dict [(x,y)] = size, same info as sizeMap

    # find biggest square fro m every point in map
    # Use the biggest remaing and prune others affeced.
    # Imperfect but much faster than finding biggest, choosing, and re-finding a biggest again.
    #   xxxxxo 113210
    #   xpxxxo 103210
    #   xxxxxo # etc.
    #   xxxxxo
    #   xxxxxo
    for size in range (1, MAX_EDGE_LENGTH + 1):
      sizeMap [size] = []

    for y in range (0, 50):
      for x in range (0, 50):
        maxFound = False
        # find size of block at (x,y)
        if not (x,y) in pointMap.keys():
          continue
        cost = pointMap [(x,y)]
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
        sizeMap [edgeLen].append ((x,y))
        posMap [(x,y)] = edgeLen

        #print "Block at", x,y, edgeLen # debug

    # for size in range (MAX_EDGE_LENGTH, 0, -1):
    #   while size in sizeMap:
    #     print size, len (sizeMap [size])
    #     block = sizeMap [size].pop (0)
    #     coalMap [block] = (size, size * pointMap [block])
    #     '''
    #     Prune all overlapping blocks.
    #     only need to check blocks within a distance that could overlap
    #
    #     aaaaaaxxxx
    #     aaaaaaxxxx
    #     aaaaaaxxxx
    #     aaaaoobbbb if we chose a we have to remove b and vice versa
    #     aaaaoobbbb
    #     aaaaoobbbb
    #     '''


  def getTkImg (self, t): # t is a tileinfo
    if t is None:
      return None
    if not t [0] in self.tkImages:
      self.tkImages [t [0]] = {} # a dictionary of tk images. Key is filename
    d = self.tkImages [t [0]]

    if not (t [1][0],t [1][1]) in d: # keyed by x,y tuple.
      spriteMap = Image.open (t [0])
      img = spriteMap.crop (box = (t [1][0],
                                   t [1][1],
                                   t [1][0] + t [1][2],
                                   t [1][1] + t [1][3]))
      tkImg = ImageTk.PhotoImage (img)
      self.images.append (tkImg)
      d [(t [1][0], t [1][1])] = tkImg

    return d [(t [1][0],t [1][1])] # dict keyed by x, y tuple

  def drawScreen (self):
    v = self.visDict()
    self.canvas.delete ("all")
    # tile map assumes black background
    self.canvas.create_rectangle (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, fill = "black")
    for layer in (LGROUND, LROAD, LTOWN):
      for y in range (-VIEW_DIST, VIEW_DIST + 1):
        for x in range (-VIEW_DIST, VIEW_DIST + 1):
          if v [x, y] < 0.0:
            continue
          tX = self.curX + x # 'tile's x,y'
          tY = self.curY + y
          if tX < 0 or tX > self.curMap.width or \
             tY < 0 or tY > self.curMap.height:
            tX = 0 # 0, 0 is water
            tY = 0
          tileInfo = self.curMap.get_tile_image (tX, tY, layer)
          if tileInfo:
            self.canvas.create_image (16 + TW * 5 + x * TW,
                                      16 + TW * 5 - y * TW, # screen y is flipped
                                      image = self.getTkImg (tileInfo))
    self.canvas.create_image (16 + TW * 5,
                              16 + TW * 5,
                              image = self.charImg)
    self.root.update()

  def checkOpacity (self, x, y):
    tileInfo = self.curMap.get_tile_image (x, y, LGROUND)
    txy = (tileInfo [1][0] / TW, tileInfo [1][1] / TW)
    if txy == TILE_TREES1:
      return 1.0
    if txy == TILE_TREES2:
      return 1.0
    if txy == TILE_TREES3:
      return 1.0
    return 0.0

  def visDict (self):
    '''
    Generate a dictionary of visibility
    key (x, y) screen coords, value is Boolean
    '''
    vis = {}
    for y in range (-VIEW_DIST, VIEW_DIST + 1):
      for x in range (-VIEW_DIST, VIEW_DIST + 1):
        vis [(x,y)] = 1.0

    # go around from the edges.
    for p in range (-VIEW_DIST, VIEW_DIST + 1):
      for pt in ((p, -VIEW_DIST), (p, VIEW_DIST), (-VIEW_DIST, p), (VIEW_DIST, p)):
        borP = Point (pt [0], pt [1])

        # test coords from 0,0 to borP
        theta = Point (0.5,0.5).directionTo (borP)
        dist  = Point (0.5,0.5).distanceTo (borP) + 1
        #print theta, dist
        v = 1.0
        r = .2
        while r < dist:
          r += 1
          tx = int (r * math.cos (theta) + .5)
          ty = int (r * math.sin (theta) + .5)
          # print "p", tx, ty, r
          vis [(tx,ty)] = v
          if v > 0.0:
            v -= self.checkOpacity (self.curX + tx, self.curY + ty)

    return vis

  def canGo (self, testX, testY):
    tileInfo = self.curMap.get_tile_image (testX, testY, LGROUND)
    txy = (tileInfo [1][0] / TW, tileInfo [1][1] / TW)
    print txy
    if txy in (TILE_GRASS, TILE_TREES2):
      return True
    return True

  def tryMove (self, tryX, tryY):
    if self.canGo (tryX, tryY):
      self.curX = tryX
      self.curY = tryY

    self.drawScreen()
    # print self.curX, self.curY

  def leftHandler (self, event):
    self.tryMove (self.curX - 1, self.curY)
  def rightHandler (self, event):
    self.tryMove (self.curX + 1, self.curY)
  def upHandler (self, event):
    self.tryMove (self.curX, self.curY + 1)
  def downHandler (self, event):
    self.tryMove (self.curX, self.curY - 1)

  def keyHandler (self, event):
    pass

w = WorldEngine ()
w.drawScreen ()
w.visDict()

print "Coalesce start"
w.subdivideMap (w.worldMap, ((2, 0, 1),))
print "Coalesce end"


# testSPF()

w.root.mainloop()
