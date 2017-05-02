import math
from party import *
from utils import *
from constants import *

class Ship ():
  def __init__(self, w, x, y):
    self.w = w # world engine
    self.x = x # initial position
    self.y = y
    self.t = OBJ_BOAT
    self.sails = False
    self.direction = DIR_EAST
    self.status = 100.0
    self.i = {}
    for ix in range (0, 8):
      self.i [ix] = w.getTkImg ((alTiles, ix, 9))

    # p1 = w.worldMap ['water']['aIDMap'] [(43, 25)]
    # p2 = w.worldMap ['water']['aIDMap'] [(168, 10)]
    # print p1, p2, len (w.worldMap ['water']['edges']), len (w.worldMap ['water']['aIDMap']) # debug

    # self.path = spf (w.worldMap ['water']['edges'], p1, p2)
    # print w.worldMap ['water']['edges']
    # print "Path:", self.path
    self.w.addWorldObject (self)

  def processTurn (self):
    return True

  def displayInfo (self):
    sx = self.x - self.w.p.x
    sy = self.w.p.y - self.y
    if math.fabs(sx) <= 5 and math.fabs(sy) <= 5:
      off = 0 if self.sails else 4
      return (sx, sy, self.i [self.direction + off])

    return None

  def processEvent (self, e):
    tx = self.w.p.x
    ty = self.w.p.y

    if e == EVENT_NORTH:
      if self.direction != DIR_NORTH:
        self.direction = DIR_NORTH
      else:
        ty += 1
    elif e == EVENT_EAST:
      if self.direction != DIR_EAST:
        self.direction = DIR_EAST
      else:
        tx += 1
    elif e == EVENT_SOUTH:
      if self.direction != DIR_SOUTH:
        self.direction = DIR_SOUTH
      else:
        ty -= 1
    elif e == EVENT_WEST:
      if self.direction != DIR_WEST:
        self.direction = DIR_WEST
      else:
        tx -= 1

    if tx != self.w.p.x or ty != self.w.p.y:
      o = self.w.getObject (tx, ty)

      if o.t == OBJ_GRASS:
        self.w.p.x = tx
        self.w.p.y = ty
        self.sails = False
        self.w.p.transport = OnFoot (self.w)

      if o.t == OBJ_WATER:
        self.w.p.x = tx
        self.w.p.y = ty
        self.x = tx
        self.y = ty
