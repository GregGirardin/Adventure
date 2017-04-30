import math
from utils import *
from constants import *

class Party ():
  def __init__(self, w):
    self.w = w
    self.curX = INIT_WORLD_X
    self.curY = INIT_WORLD_Y
    self.transport = OnFoot (self, self.w, self.curX, self.curY)
    self.inventory = {}

    w.curMap ['objects'].append (self.transport)

  def processTurn (self, e):
    return True

  def processEvent (self, e):
    self.transport.processEvent (e)
    return True


# The party on foot
class OnFoot ():
  def __init__(self, p, w, x, y):
    self.p = p
    self.x = x
    self.y = y
    self.w = w
    self.icon = w.getTkImg (TILE_CHAR)

  def processTurn (self):
    return True

  def canGo (self, x, y):
    tileInfo = self.w.curMap ['tiles'].get_tile_image (x, y, LGROUND)
    txy = (tileInfo [0], tileInfo [1][0] / TW, tileInfo [1][1] / TW)
    print txy # debug
    if txy in (TILE_GRASS, TILE_TREES2):
      return True

    return False

  def processEvent (self, e):
    tx = self.p.curX
    ty = self.p.curY

    if e == EVENT_NORTH:
      ty += 1
    elif e == EVENT_EAST:
      tx += 1
    elif e == EVENT_SOUTH:
      ty -= 1
    elif e == EVENT_WEST:
      tx -= 1

    if self.canGo (tx, ty):
      self.p.curX = tx
      self.p.curY = ty

  def displayInfo (self):
    return (0, 0, self.icon)