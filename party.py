import math
from utils import *
from constants import *
from character import *

class Party():
  def __init__( self, w ):
    self.w = w
    self.x = INIT_WORLD_X
    self.y = INIT_WORLD_Y
    self.inventory = {}
    self.transport = OnFoot( self )
    self.members = []

  def addMember(self, c):
    self.members.append( c )

  def processEvent( self, e ):
    self.transport.processEvent( e )
    return True

# The party on foot
class OnFoot():
  def __init__( self, p, icon = TILE_CHAR ):
    self.w = p.w
    self.x = p.x
    self.y = p.y
    self.t = PARTY_
    self.icon = p.w.getTkImg( tileInfoFromtInfo( icon ) )
    self.w.curMap[ 'objects' ].append( self )

  def processTurn( self ):
    # print self.x, self.y # debug
    return True

  def processEvent( self, e ):
    if e == E_TURN:
      return True

    tx = self.w.party.x
    ty = self.w.party.y
    if e == E_NORTH:
      ty += 1
    elif e == E_EAST:
      tx += 1
    elif e == E_SOUTH:
      ty -= 1
    elif e == E_WEST:
      tx -= 1

    o = self.w.getObject( tx, ty )

    if e == E_ENTER:
      if o.i:
        self.w.newMessage( 'Enter ' + o.i )
    if o.o:
      if o.o.t == BOAT_:
        o.o.sails = True
        self.w.party.transport = o.o
        self.w.party.x = tx
        self.w.party.y = ty
        self.w.curMap[ 'objects' ].remove( self ) # Delete the party object
        return

    if o.t in( GRASS_, TREES_, HILLS_ ):
      self.w.party.x = tx
      self.w.party.y = ty
      self.x = self.w.party.x
      self.y = self.w.party.y

  def displayInfo( self ):
    return( 0, 0, self.icon )