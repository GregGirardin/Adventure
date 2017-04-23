import math
from utils import *
from constants import *

class Ship ():
  def __init__(self, w):
    self.x = 10 # initial position
    self.y = 54
    self.i = w.getTkImg (TILE_BOAT)

  def processTurn (self, e):
    return True

  def displayInfo (self, w):
    sx = self.x - w.curX
    sy = w.curY - self.y
    if math.fabs(sx) <= 5 and math.fabs(sy) <= 5:
      return (sx, sy, self.i)

    return None