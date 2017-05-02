#!/usr/bin/python
from PIL import Image, ImageTk
import pytmx
import Tkinter as tk
import time
from constants import *
from utils import *
from ship import *
from party import *
import math

class WorldEngine ():
  def __init__ (self):
    self.root = tk.Tk()
    self.root.title ("Rogue")
    self.canvas = tk.Canvas (self.root, width = SCREEN_WIDTH, height = SCREEN_HEIGHT)
    self.canvas.pack()

    self.images = []
    self.tkImages = {}
    self.worldMap = openMap (worldMap)
    self.curMap = self.worldMap

    self.p = Party (self)
    self.p.transport = OnFoot (self)

    self.root.bind ("<Left>",  self.leftHandler)
    self.root.bind ("<Right>", self.rightHandler)
    self.root.bind ("<Up>",    self.upHandler)
    self.root.bind ("<Down>",  self.downHandler)
    self.root.bind ("<Key>",   self.keyHandler)

    Ship (self, 10, 54)

  def getObject (self, x, y):
    # if there's a character there, return that, else return the topology at x,y
    for obj in self.curMap ['objects']:
      if obj.x == x and obj.y == y:
        return obj

    for layer in (LTOWN, LROAD, LGROUND):
      tileInfo = self.curMap ['tiles'].get_tile_image (x, y, layer)
      if tileInfo:
        txy = (tileInfo [0], tileInfo [1][0] / TW, tileInfo [1][1] / TW)
        return Terrain (TILE_OBJ_DICT [txy])
    return None

  def addWorldObject (self, o):
    self.curMap ['objects'].append (o)

  def getTkImg (self, t):
    # t is a tuple of (filename, grid x, grid y)
    t = (t[0], (t[1] * TW, t[2] * TW, TW, TW), None)
    return self.getTkImgTI (t)

  def getTkImgTI (self, t):
    # t is a tileinfo
    # a tuple of filename, (tile x, y, width,  height), flags
    if t is None:
      return None
    if not t [0] in self.tkImages:
      self.tkImages [t [0]] = {} # a dictionary of tk images. Key is filename
    d = self.tkImages [t [0]]

    if not (t [1][0],t [1][1]) in d: # keyed by x,y tuple.
      spriteMap = Image.open (t [0])
      img = spriteMap.crop (box = (t[1][0],
                                   t[1][1],
                                   t[1][0] + t[1][2],
                                   t[1][1] + t[1][3]))
      tkImg = ImageTk.PhotoImage (img)
      self.images.append (tkImg)
      d [(t[1][0], t[1][1])] = tkImg

    return d [(t[1][0],t[1][1])] # dict keyed by x, y tuple

  def processTurn (self):
    for c in self.curMap ['objects']:
      if not c.processTurn ():
        self.curMap ['objects'].remove (c)
    self.drawScreen()

  def drawScreen (self):
    v = self.visDict()
    self.canvas.delete ("all")
    # tile map assumes black background
    self.canvas.create_rectangle (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, fill = "black")
    for layer in (LGROUND, LROAD, LTOWN):
      for y in range (-VIEW_DIST, VIEW_DIST + 1):
        for x in range (-VIEW_DIST, VIEW_DIST + 1):
          if v [x, y] <= 0.0:
            continue
          tX = self.p.x + x # 'tile's x,y'
          tY = self.p.y + y
          if tX < 0 or tX >= self.curMap ['tiles'].width or tY < 0 or tY >= self.curMap['tiles'].height:
            tX = 0 # 0, 0 is water
            tY = 0
          tileInfo = self.curMap ['tiles'].get_tile_image (tX, tY, layer)
          if tileInfo:
            self.canvas.create_image (16 + TW * 5 + x * TW,
                                      16 + TW * 5 - y * TW, # screen y is flipped
                                      image = self.getTkImgTI (tileInfo))
    for obj in self.curMap ['objects']:
      d = obj.displayInfo()
      if d:
        if v [d[0], d[1]]:
          self.canvas.create_image (16 + TW * (d [0] + 5),
                                    16 + TW * (d [1] + 5),
                                    image = d [2])
    self.root.update()

  def checkOpacity (self, x, y):
    o = self.getObject (x, y)
    if o.t == OBJ_TREES:
      return .4
    if o.t == OBJ_HILLS:
      return .3
    if o.t == OBJ_MOUNTAINS:
      return .8

    return 0.0

  def visDict (self):
    # Generate a dictionary of visibility. key (x, y) screen coords, value is Boolean
    vis = {}
    # go around from the edges.
    for i in range (-VIEW_DIST, VIEW_DIST + 1):
      for ept in ((i, -VIEW_DIST), (i, VIEW_DIST), (-VIEW_DIST, i), (VIEW_DIST, i)):
        l = getLine ((0,0), (ept [0], ept [1])) # ray from center out
        v = 1.0
        for p in l:
          if v > 0.0:
            v -= self.checkOpacity (self.p.x + p[0], self.p.y + p[1])
          vis [p] = v
    return vis

  def leftHandler (self, event):
    self.p.processEvent (EVENT_WEST)
    self.processTurn()
  def rightHandler (self, event):
    self.p.processEvent (EVENT_EAST)
    self.processTurn()
  def upHandler (self, event):
    self.p.processEvent (EVENT_NORTH)
    self.processTurn()
  def downHandler (self, event):
    self.p.processEvent (EVENT_SOUTH)
    self.processTurn()

  def keyHandler (self, event):
    pass

w = WorldEngine ()


w.drawScreen ()
w.visDict()

w.root.mainloop()
