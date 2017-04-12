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
    self.curMap = self.worldMap

    self.charImg = self.getTkImg (self.curMap.get_tile_image (0, 0, LCHAR))

    self.curX = INIT_WORLD_X
    self.curY = INIT_WORLD_Y

    self.root.bind ("<Left>",  self.leftHandler)
    self.root.bind ("<Right>", self.rightHandler)
    self.root.bind ("<Up>",    self.upHandler)
    self.root.bind ("<Down>",  self.downHandler)
    self.root.bind ("<Key>",   self.keyHandler)

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
    self.canvas.create_rectangle(0,0, SCREEN_WIDTH, SCREEN_HEIGHT, fill = "black")
    for layer in (LGROUND, LROAD, LTOWN):
      for y in range (-VIEW_DIST, VIEW_DIST + 1):
        for x in range (-VIEW_DIST, VIEW_DIST + 1):
          if v [x, y] == False:
            continue
          tX = self.curX + x # 'tile's x,y'
          tY = self.curY + y
          if tX < 0 or tX > self.curMap.width or \
             tY < 0 or tY > self.curMap.height:
            tX = 0 # 0, 0 is water
            tY = 0
          tileInfo = self.curMap.get_tile_image (tX, tY, layer)
          if tileInfo:
            self.canvas.create_image (16 + 32 * 5 + x * 32,
                                      16 + 32 * 5 + y * 32,
                                      image = self.getTkImg (tileInfo))
    self.canvas.create_image (16 + 32 * 5,
                              16 + 32 * 5,
                              image = self.charImg)
    self.root.update()

  def checkTransparent (self, x, y):
    tileInfo = self.curMap.get_tile_image (x, y, LGROUND)
    txy = (tileInfo [1][0], tileInfo [1][1])
    if txy in (TILE_TREES2, TILE_TREES3):
      return False
    return True

  def visDict (self):
    '''
    54321012345
    5
    4      -
    3 -   x
    2  -
    1   x
    0    C
    1 ...
    '''
    vis = {}
    for y in range (-VIEW_DIST, VIEW_DIST + 1):
      for x in range (-VIEW_DIST, VIEW_DIST + 1):
        vis [(x,y)] = True

    # go around from the edges.
    for p in range (-VIEW_DIST, VIEW_DIST + 1):
      for t in (1,): #, 2, 3, 4):
        if t == 1:
          borP = Point (p, -VIEW_DIST)
        elif t == 2:
          borP = Point (p, VIEW_DIST)
        elif t == 3:
          borP = Point (-VIEW_DIST, p)
        elif t == 4:
          borP = Point (VIEW_DIST, p)

        # test coords from 0,0 to borP
        theta = Point (0,0).directionTo (borP)
        dist = Point (0,0).distanceTo (borP) + .5
        v = True
        r = 1
        while r < dist:
          tx = int (r * math.cos (theta) + .5)
          ty = int (r * math.sin (theta) + .5)
          #print "p", tx, ty
          vis [(tx,ty)] = v
          r += .5
          if v:
            v = self.checkTransparent (self.curX + tx, self.curY + ty)

    return vis

  def canGo (self, testX, testY):
    tileInfo = self.curMap.get_tile_image (testX, testY, LGROUND)
    txy = (tileInfo [1][0], tileInfo [1][1])
    if txy in (TILE_GRASS,TILE_TREES2):
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
    self.tryMove (self.curX, self.curY - 1)
  def downHandler (self, event):
    self.tryMove (self.curX, self.curY + 1)

  def keyHandler (self, event):
    pass

w = WorldEngine ()
w.drawScreen ()
w.visDict()

w.root.mainloop()
