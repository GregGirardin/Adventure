
'''
Base class for characters
'''
from constants import *
from utils import *

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

  def processEvent( self, e ):
    return True

''' NPC characters '''
class cMerchant():
  def __init__( self, c, w ):
    self.w = w
    self.name = c.name
    self.x = int(c.x / TW) # in map coords
    self.y = int(c.y / TW)
    self.t = NPC_
    ti = tInfo( tilesA, 16, 10 )
    self.icon = getTkImg( tileInfoFromtInfo( ti ) )

  def processEvent( self, e ):
    return True

  def displayInfo( self, px, py ):
    sx = self.x - px # convert to screen coords
    sy = self.y - py
    if math.fabs( sx ) <= VIEW_DIST and math.fabs( sy ) <= VIEW_DIST:
      return( sx, sy, self.icon )

    return None

#################################

class cGuard():
  def __init__( self, c, w ):
    self.name = c.name
    self.x = int( c.x / TW ) # in map coords
    self.y = int( c.y / TW )
    self.icon = getTkImg( tileInfoFromtInfo( tInfo( tilesA, 8, 10 ) ) )
    self.t = NPC_

  def processEvent( self, e ):
    return True

  def displayInfo( self, px, py ):
    sx = self.x - px # convert to screen coords
    sy = self.y - py
    if math.fabs( sx ) <= VIEW_DIST and math.fabs( sy ) <= VIEW_DIST:
      return( sx, sy, self.icon )

    return None

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