
'''
Base class for characters
'''
from constants import *
from utils import *
from random import random, sample

def tileInfoFromtInfo( t ):
  return( t.filename, ( t.gx * TW, t.gy * TW, TW, TW ), None )

class Character():
  ''' Character in the party '''
  def __init__( self, name, w ):
    self.name = name
    self.w = w
    # icon
    self.image = []
    self.inventory = {}

    # character attributes
    self.experience = None
    self.strength = None
    self.intelligence = None
    self.dexterity = None
    self.hitPoints = None
    self.armor = None
    self.weapon = None

class cNPC():
  def __init__( self, c, w):
    self.w = w
    self.name = c.name
    self.x_home = int( c.x / TW ) # home base positionin map coords
    self.y_home = int( c.y / TW )
    self.x = self.x_home  # our actual position, some NPCs can meander
    self.y = self.y_home
    self.t = NPC_
    self.movement = M_MEANDER
    self.meanderDis = 3

  def processEvent( self, e ):
    if e.e == E_TURN:
      if self.movement == M_MEANDER:
        self.m_meander()
    return True

  def m_meander( self ):
    if random() < .25:
      e = sample( [ E_NORTH, E_EAST, E_SOUTH, E_WEST ], k=1 )
      gx, gy = coordInDir( self.x, self.y, e[ 0 ] )
      if abs( gx - self.x_home ) > self.meanderDis or \
         abs( gy - self.y_home ) > self.meanderDis:
         return
      if blocked( gx, gy, self.w ) == False:
        self.x = gx
        self.y = gy

''' NPC characters '''
class cMerchant( cNPC ):
  def __init__( self, c, w ):
    cNPC.__init__( self, c, w )
    self.icon = getTkImg( tilesA, 16, 10 )

  def displayInfo( self, px, py ):
    sx = self.x - px # convert to screen coords
    sy = self.y - py
    if math.fabs( sx ) <= VIEW_DIST and math.fabs( sy ) <= VIEW_DIST:
      return( sx, sy, self.icon )

    return None

  def processEvent( self, e ):
    cNPC.processEvent( self, e )
    return True

###
class cGuard( cNPC ):
  def __init__( self, c, w ):
    cNPC.__init__( self, c, w )
    self.icon = getTkImg( tilesA, 8, 10 )

  def processEvent( self, e ):
    cNPC.processEvent( self, e )

    return True

  def displayInfo( self, px, py ):
    sx = self.x - px # convert to screen coords
    sy = self.y - py
    if math.fabs( sx ) <= VIEW_DIST and math.fabs( sy ) <= VIEW_DIST:
      return( sx, sy, self.icon )

    return None

###
charClassMap = {
                "Merchant" : cMerchant,
                "Guard"    : cGuard,
                }

def NPCFactory( c, w ):
  cc = c.charClass
  if cc in charClassMap:
    return charClassMap[ cc ]( c, w )
  else:
    assert 0, ( "No factory for", cc )

  return None