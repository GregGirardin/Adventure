
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
  def __init__( self, c, w, tX, tY, num ):
    self.w = w
    self.c = c
    # break out some parameters for easier access
    self.name = c.name
    self.x_home = int( c.x / TW ) # home base position in map coords
    self.y_home = int( c.y / TW )
    self.x = self.x_home # our actual position
    self.y = self.y_home
    self.t = NPC_
    self.movement = M_MEANDER
    self.meanderDis = 3
    self.talking = False
    self.images = []
    for i in range ( 0, num ):
      self.images.append( getTkImg( tilesA, ( tX + i ) * TW, tY * TW ) )

  def processEvent( self, e ):
    if e.e == E_TURN:
      if self.talking == False:
        if self.movement == M_MEANDER:
          self.m_meander()
    return True

  def m_meander( self ):
    if random() < .25:
      e = sample( [ E_NORTH, E_EAST, E_SOUTH, E_WEST ], k=1 )
      gX, gY = coordInDir( self.x, self.y, e[ 0 ] )
      if abs( gX - self.x_home ) > self.meanderDis or \
         abs( gY - self.y_home ) > self.meanderDis:
         return

      i = self.w.getInfo( gX, gY )

      if not ( i.tp == MOUNTAINS_ or ( i.tp == WATER_ and i.sp != DOCK_ )
               or i.sp == WALL_ or i.o ):
        self.x = gX
        self.y = gY

  def talkHandler( self, e ):
    self.w.newMessage( "No response" )
    return None

'''
  NPC characters
'''
class cMerchant( cNPC ):
  def __init__( self, c, w ):
    cNPC.__init__( self, c, w, 16, 10, 4 )

  def displayInfo( self ):
    if random() < .2:
      ix = 1
    else:
      ix = 0
    return( self.images[ ix ] )

  def processEvent( self, e ):
    cNPC.processEvent( self, e )
    return True

  def talkHandler( self, e ):
    if self.talking == True:
      self.w.newMessage( "Bye Soy Boy" )
      self.talking = False
      return None
    elif self.talking == False:
      self.talking = True
      self.w.newMessage( "Hi Soy Boy" )
      return self
#
class cGuard( cNPC ):
  def __init__( self, c, w ):
    cNPC.__init__( self, c, w, 8, 10, 4 )

  def processEvent( self, e ):
    cNPC.processEvent( self, e )
    return True

  def displayInfo( self ):
    if random() < .2:
      ix = 1
    else:
      ix = 0
    return( self.images[ ix ] )

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