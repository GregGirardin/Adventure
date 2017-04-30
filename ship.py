import math
from utils import *
from constants import *

class Ship ():
  def __init__(self, w, x, y):
    self.w = w # world engine
    self.x = x # initial position
    self.y = y
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
  def canGo (self):
    return True

  def processTurn (self):
    return True

  def displayInfo (self):
    sx = self.x - self.w.p.curX
    sy = self.w.p.curY - self.y
    if math.fabs(sx) <= 5 and math.fabs(sy) <= 5:
      off = 0 if self.sails else 4
      return (sx, sy, self.i [self.direction + off])

    return None