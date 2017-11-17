import math
from utils import *
from constants import *
from character import *

class Party():
  def __init__( self, w, x, y ):
    self.w = w
    self.x = x
    self.y = y
    self.inventory = {}
    self.transport = OnFoot( self )
    self.members = []

  def addMember(self, c):
    self.members.append( c )

  def processEvent( self, e ):
    self.transport.processEvent( e )
    return True

  def displayInfo( self, px, py ):
    return self.transport.displayInfo( px, py )

# The party on foot
class OnFoot():
  def __init__( self, p ):
    self.p = p
    self.t = PARTY_
    self.icon = getTkImg( tilesA, 28, 8 )

  def processEvent( self, e ):
    ev = e.e

    if ev == E_TURN:
      return True
    elif ev == E_PASS:
      self.p.w.newMessage( e.m )
    elif ev in ( E_NORTH, E_EAST, E_SOUTH, E_WEST ):
      tx, ty = coordInDir( self.p.x, self.p.y, ev  )

      o = self.p.w.getObject( tx, ty )

      if o.o:
        if o.o.t == BOAT_:
          o.o.sails = True
          self.p.transport = o.o
          self.p.x = tx
          self.p.y = ty
          return

      if o.i:
        for elem in o.i:
          if elem.type == "Transfer":
            mapX = mapY = None
            mapName = elem.properties[ 'map' ]
            if 'map_x' in elem.properties:
              # if not provided use Start Spawn
              mapX = int( elem.properties[ 'map_x' ] )
              mapY = int( elem.properties[ 'map_y' ] )
            self.p.w.transfer( mapName, mapX, mapY )
            return

      if blocked( tx, ty, self.p.w ):
        self.p.w.newMessage( "Blocked" )
      else:
        self.p.x = tx
        self.p.y = ty
        self.p.w.newMessage( e.m )

  def displayInfo( self, px, py ):
    return( 0, 0, self.icon )