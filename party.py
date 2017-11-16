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
    return True

  def processEvent( self, e ):
    ev = e.e

    if ev == E_TURN:
      return True

    if e.e == E_ENTER:
      o = self.p.w.getObject( self.p.x, self.p.y )
      if o.i:
        for elem in o.i:
          if elem.type == "Town":
            self.p.w.enterLocale( elem )
            return
      self.p.w.newMessage( "Nothing to enter." )

    if ev in ( E_NORTH, E_EAST, E_SOUTH, E_WEST ):
      tx = self.p.x
      ty = self.p.y
      if e.e == E_NORTH:
        ty -= 1
      elif e.e == E_EAST:
        tx += 1
      elif e.e == E_SOUTH:
        ty += 1
      elif e.e == E_WEST:
        tx -= 1

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
          if elem.type == "Exit":
            self.p.w.exitLocale()
            return
          if e == E_ENTER:
            if elem.type == "Town":
              self.p.w.enterLocale( elem )
              return

      blocked = False
      if o.t == MOUNTAINS_ or ( o.t == WATER_ and o.s != DOCK_ ) or o.s == WALL_:
        self.p.w.newMessage( "Blocked" )
      else:
        self.p.x = tx
        self.p.y = ty
        self.p.w.newMessage( e.m )

  def displayInfo( self ):
    return( 0, 0, self.icon )