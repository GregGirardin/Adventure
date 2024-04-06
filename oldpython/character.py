
from constants import *
from utils import *
from random import random, sample

# def tileInfoFromtInfo( t ):
#   return( t.filename, ( t.gx * TW, t.gy * TW, TW, TW ), None )



class cNPC():
  def __init__( self, w, c, tX, tY, numIcons ):
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
    self.talkState = T_NO
    self.numIcons = numIcons
    self.images = []
    for i in range ( 0, numIcons ):
      self.images.append( getTkImg( tilesA, ( tX + i ) * TW, tY * TW ) )

  def processEvent( self, e ):
    if e.e == E_TURN:
      if self.talkState == T_NO:
        if self.movement == M_MEANDER:
          self.m_meander()
    return True

  def displayInfo( self ):
    # Generic display method, show the first icon and randomly the
    # 2nd one if there is more than one. This works for lots of NPCs.
    ix = 1 if random() < .2 and self.numIcons > 1 else 0
    return( self.images[ ix ] )

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
    # Called when you speak to NPC
    # default NPCs don't talk, override.
    self.w.newMessage( "No response" )
    return None

'''
  NPC characters
'''
class cMerchant( cNPC ):
  def __init__( self, w, c, npc ):
    cNPC.__init__( self, w, c, 16, 10, 4 )
    self.npc = npc
    self.items = []

    chars = 'abcdefghijklmnop'
    index = 0

    for iKey in npc[ 2 ]:
      item = itemFromKey( iKey )
      item.quality = random() * 50 + 50.0
      item.actualBuyCost  = item.nomCost * ( random() / 2 + .7 ) * item.quality
      item.selectChar = chars[ index ]
      self.items.append( item )
      index += 1

  def processEvent( self, e ):
    cNPC.processEvent( self, e )
    return True

  def talkHandler( self, e ):
    chat = []
    txt = None
    hello = "Would you like to:"
    bs = [ cMessage( 'b', "Buy" ),
           cMessage( 's', "Sell" ) ]

    if self.talkState != T_NO and e.k == 'q':
      self.w.newMessage( "Bye." )
      self.talkState = T_NO
      self.w.chatConfig( None, None )
      return None

    if self.talkState == T_NO:
      self.talkState = T_BSL
      txt = hello
      chat = bs
    elif self.talkState == T_BSL: # buy / sell / leave
      if e.k == 'b':
        self.talkState = T_BUY
        txt = "Buy:"
        for item in self.items:
          chat.append( cMessage( item.selectChar,
                                 "%s Q %d C %d" %
                                ( item.name, item.quality, item.actualBuyCost ) ) )
      elif e.k == 's':
        self.talkState = T_SELL
        txt = "Sell:"
        # only include items in inventory that merchant sells.
        # price based on quality of item.
    elif self.talkState == T_BUY:
      self.talkState = T_BSL

      txt = hello
      chat = bs
    elif self.talkState == T_SELL:
      self.talkState = T_BSL
      txt = hello
      chat = bs

    chat.append( cMessage( 'q', 'Leave' ) ) # include in all chat

    self.w.chatConfig( txt, chat )
    return self

#
class cGuard( cNPC ):
  def __init__( self, w, c, npc ):
    cNPC.__init__( self, w, c, 8, 10, 4 )
    self.npc = npc

  def processEvent( self, e ):
    cNPC.processEvent( self, e )
    return True

# define all the NPCs in the world.
npcDict = {
  "Gonk"   : ( cGuard, # class
               "Gonk", # name
               ( 'AL', 'WL' ) ),
  "Dio"    : ( cMerchant, "Dio",  ( 'AC', 'AL', 'AM' ) ),
}

def NPCFactory( cInfo, wObject ):
  assert cInfo.name in npcDict

  npc = npcDict[ cInfo.name ]
  return npc[ 0 ]( wObject, cInfo, npc )