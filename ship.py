import math
from party import *
from utils import *
from constants import *

class Ship ():
  def __init__( self, p ):
    self.p = p
    self.t = BOAT_
    self.sails = False
    self.direction = DIR_EAST
    self.status = 100.0
    self.images = {}
    for ix in range( 0, 8 ):
      self.images[ ix ] = w.getTkImg( tileInfoFromtInfo( tInfo( alTiles, ix, 9 ) ) )

    # need to add to map

  def displayInfo( self, px, py ):
    sx = self.x - px
    sy = self.y - py
    if math.fabs( sx ) <= VIEW_DIST and math.fabs( sy ) <= VIEW_DIST:
      off = 0 if self.sails else 4
      return( sx, sy, self.images[ self.direction + off ] )

    return None

  def processEvent( self, e ):
    if e == E_TURN:
      return True

    tx = self.p.x
    ty = self.p.y

    if e == E_NORTH:
      if self.direction != DIR_NORTH:
        self.direction = DIR_NORTH
      else:
        ty -= 1
    elif e == E_EAST:
      if self.direction != DIR_EAST:
        self.direction = DIR_EAST
      else:
        tx += 1
    elif e == E_SOUTH:
      if self.direction != DIR_SOUTH:
        self.direction = DIR_SOUTH
      else:
        ty += 1
    elif e == E_WEST:
      if self.direction != DIR_WEST:
        self.direction = DIR_WEST
      else:
        tx -= 1

    if tx != self.p.x or ty != self.p.y:
      o = self.w.getObject( tx, ty )

      if o.t == GRASS_:
        self.p.x = tx
        self.p.y = ty
        self.sails = False
        self.p.transport = OnFoot( self.p )

      if o.t == WATER_:
        self.p.x = tx
        self.p.y = ty