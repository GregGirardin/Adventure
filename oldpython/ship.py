import math
from party import *
from utils import *
from constants import *

class Ship():
  def __init__( self, p ):
    self.p = p
    self.t = BOAT_
    self.sails = False
    self.direction = E_EAST
    self.status = 100.0
    self.images = {}
    for ix in range( 0, 8 ):
      self.images[ ix ] = w.getTkImg( tilesA, ix, 9 )

    # need to add to map

  def displayInfo( self ):
    off = 0 if self.sails else 4
    return( self.images[ self.direction + off ] )

  def processEvent( self, e ):
    if e == E_TURN:
      return True

    if self.direction != e:
      self.direction = e
    else:
      sX, sY = coordInDir( 0, 0, e )
      i = self.p.w.localInfo[ ( sX, sY ) ]

      if i.tp == GRASS_:
        self.p.x += sX
        self.p.y += sY
        self.sails = False
        self.p.transport = OnFoot( self.p )

      if i.tp == WATER_ or i.t == WATER_R:
        self.p.x += sX
        self.p.y += sY