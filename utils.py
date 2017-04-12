__author__ = 'ggirardin'

import math

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