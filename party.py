import math
from utils import *
from constants import *
from character import *

class Party():
  def __init__( self, w, x, y ):
    self.w = w
    self.x = x
    self.y = y
    self.talking = None # NPC we're talking to
    self.inventory = {}
    self.transport = OnFoot( self )
    self.members = []
    self.talk = None # NPC I'm talking to

  def addMember( self, c ):
    self.members.append( c )

  def processEvent( self, e ):
    self.transport.processEvent( e )
    return True

  def displayInfo( self ):
    return self.transport.displayInfo()

# The party on foot
class OnFoot():
  def __init__( self, p ):
    self.p = p
    self.t = PARTY_
    self.icon = getTkImg( tilesA, 28 * TW, 8 * TW )

  def processEvent( self, e ):
    ev = e.e

    if ev == E_TURN:
      return True

    if self.p.talk:
      self.p.talk = self.p.talk.talkHandler( e )
      return

    if ev == E_PASS:
      self.p.w.newMessage( e.m )
    elif ev in ( E_NORTH, E_EAST, E_SOUTH, E_WEST ):
      sX, sY = coordInDir( 0, 0, ev )

      i = self.p.w.localInfo[ ( sX, sY ) ]

      if i.o:
        if i.o.t == BOAT_:
          i.o.sails = True
          self.p.transport = i.o
          self.p.x += sX # screen x/y are basically the offset to where we're going
          self.p.y += sY
          return
        elif i.o.t == NPC_:
          self.p.talk = i.o.talkHandler( e )
      else:
        if i.i:
          for elem in i.i:
            if elem.type == "Transfer":
              mapX = mapY = None
              mapName = elem.properties[ 'map' ]
              if 'map_x' in elem.properties:
                # if not provided transfer will use the new map's Start Spawn
                mapX = int( elem.properties[ 'map_x' ] )
                mapY = int( elem.properties[ 'map_y' ] )
              self.p.w.transfer( mapName, mapX, mapY )
              return

        if i.sp == PATH_ and i.o == None:
          sX2, sY2 = coordInDir( 0, 0, ev, dist=2 )

          i2 = self.p.w.localInfo[ ( sX2, sY2 ) ]
          if i2.sp == PATH_:
            sX = sX2
            sY = sY2

        if i.tp == MOUNTAINS_ or ( i.tp == WATER_ and i.sp != DOCK_ ) or i.sp == WALL_ or i.o:
          self.p.w.newMessage( "Blocked" )
        else:
          self.p.x += sX
          self.p.y += sY
          self.p.w.newMessage( e.m )

  def displayInfo( self ):
    return( self.icon )