import math
from utils import *
from constants import *
from party import *

class Pirate ():

  def __init__( self, w, x, y ):
    self.w = w
    self.x = x
    self.y = y
    self.transport = OnFoot( w, TILE_PIRATE )
    self.inventory = {}

  def processTurn( self, e ):

    return True