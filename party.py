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

  def displayInfo( self ):
    return self.transport.displayInfo()

# The party on foot
class OnFoot():
  def __init__( self, p, icon=TILE_CHAR ):
    self.p = p
    self.t = PARTY_
    self.icon = p.w.getTkImg( tileInfoFromtInfo( icon ) )

  def processTurn( self ):
    # print self.x, self.y # debug
    return True

  def processEvent( self, e ):
    if e == E_TURN:
      return True

    tx = self.p.x
    ty = self.p.y
    if e == E_NORTH:
      ty -= 1
    elif e == E_EAST:
      tx += 1
    elif e == E_SOUTH:
      ty += 1
    elif e == E_WEST:
      tx -= 1

    o = self.p.w.getObject( tx, ty )

    if o.i:
      for elem in o.i:
        if elem.type == "Exit":
          self.p.w.exitLocale()
          return
        if e == E_ENTER:
          if elem.type == "Town":
            self.p.w.enterLocale( elem )
            return
    if o.o:
      if o.o.t == BOAT_:
        o.o.sails = True
        self.p.transport = o.o
        self.p.x = tx
        self.p.y = ty
        return

    if o.t in( GRASS_, TREES_, HILLS_ ):
      self.p.x = tx
      self.p.y = ty

  def displayInfo( self ):
    return( 0, 0, self.icon )