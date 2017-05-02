import math
from utils import *
from constants import *

class Party ():

  def __init__(self, w):
    self.w = w
    self.x = INIT_WORLD_X
    self.y = INIT_WORLD_Y
    self.transport = None
    self.inventory = {}

  def processTurn (self, e):
    return True

  def processEvent (self, e):
    self.transport.processEvent (e)
    return True

# The party on foot
class OnFoot ():
  def __init__ (self, w):
    self.w = w
    self.x = self.w.p.x
    self.y = self.w.p.y
    self.t = OBJ_PARTY
    self.icon = w.getTkImg (TILE_CHAR)
    self.w.curMap ['objects'].append (self)

  def processTurn (self):
    return True

  def processEvent (self, e):
    tx = self.w.p.x
    ty = self.w.p.y

    if e == EVENT_NORTH:
      ty += 1
    elif e == EVENT_EAST:
      tx += 1
    elif e == EVENT_SOUTH:
      ty -= 1
    elif e == EVENT_WEST:
      tx -= 1

    o = self.w.getObject (tx, ty)

    if o.t == OBJ_BOAT:
      o.sails = True
      self.w.p.transport = o
      self.w.p.x = tx
      self.w.p.y = ty
      self.w.curMap ['objects'].remove (self) # delete the party object
      return

    if o.t in (OBJ_GRASS, OBJ_TREES, OBJ_HILLS):
      self.w.p.x = tx
      self.w.p.y = ty
      self.x = self.w.p.x
      self.y = self.w.p.y

  def displayInfo (self):
    return (0, 0, self.icon)