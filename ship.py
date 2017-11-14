import math
from party import *
from utils import *
from constants import *

class Ship ():
  def __init__( self, w, x, y ):
    self.w = w # world engine
    self.x = x # initial position
    self.y = y
    self.t = BOAT_
    self.sails = False
    self.direction = DIR_EAST
    self.status = 100.0
    self.images = {}
    for ix in range( 0, 8 ):
      self.images[ ix ] = w.getTkImg( tileInfoFromtInfo( tInfo( alTiles, ix, 9 ) ))

    '''
    p1 = w.worldMap[ 'water' ][ 'aIDMap' ][ ( 43, 25 ) ]
    p2 = w.worldMap[ 'water' ][ 'aIDMap' ][ ( 168, 10 ) ]
    print p1, p2, len (w.worldMap ['water']['edges']), len (w.worldMap ['water']['aIDMap']) # debug

    self.path = spf( w.worldMap ['water']['edges'], p1, p2)
    print w.worldMap ['water']['edges']
    print "Path:", self.path
    '''
    self.w.addWorldObject( self )

  def displayInfo( self ):
    sx = self.x - self.w.party.x
    sy = self.w.party.y - self.y
    if math.fabs( sx ) <= VIEW_DIST and math.fabs( sy ) <= VIEW_DIST:
      off = 0 if self.sails else 4
      return( sx, sy, self.images[ self.direction + off ] )

    return None

  def processEvent( self, e ):

    if e == E_TURN:
      return True

    tx = self.w.party.x
    ty = self.w.party.y

    if e == E_NORTH:
      if self.direction != DIR_NORTH:
        self.direction = DIR_NORTH
      else:
        ty += 1
    elif e == E_EAST:
      if self.direction != DIR_EAST:
        self.direction = DIR_EAST
      else:
        tx += 1
    elif e == E_SOUTH:
      if self.direction != DIR_SOUTH:
        self.direction = DIR_SOUTH
      else:
        ty -= 1
    elif e == E_WEST:
      if self.direction != DIR_WEST:
        self.direction = DIR_WEST
      else:
        tx -= 1

    if tx != self.w.party.x or ty != self.w.party.y:
      o = self.w.getObject( tx, ty )

      if o.t == GRASS_:
        self.w.party.x = tx
        self.w.party.y = ty
        self.sails = False
        self.w.party.transport = OnFoot( self.w.party )

      if o.t == WATER_:
        self.w.party.x = tx
        self.w.party.y = ty
        self.x = tx
        self.y = ty