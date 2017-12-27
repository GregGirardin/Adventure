#!/usr/bin/python

import pytmx
import Tkinter as tk
from tkFont import Font
import time
from constants import *
from utils import *
from ship import *
from party import *
from character import *
import math
import time

class WorldEngine ():

  def __init__( self ):
    self.root = tk.Tk()
    self.root.title( "Rogue" )
    self.canvas = tk.Canvas( self.root, width=SCREEN_WIDTH, height=SCREEN_HEIGHT )
    self.canvas.pack()

    self.animSeqNum = 0 # cycle 0-3 for things we want to animate

    self.maps = {} # maps
    self.maps[ worldMap ] = openMap( worldMap, self )
    self.curMap = self.maps[ worldMap ]

    self.night = False # tbd / time of day .. night / dawn / day / dusk

    # Find the starting location. By default there should be an object of type Spawn called Start
    initX, initY = getSpawn( self.curMap )
    assert( initX ), "No Start Spawn!"

    self.party = Party( self, initX, initY )
    self.curMap[ 'objects' ].append( self.party )

    mainChar = Member( "Foobar", self )
    self.party.addMember( mainChar )

    hanTup = ( ( 'Left',  E_WEST,  'West'  ),
               ( 'Right', E_EAST,  'East'  ),
               ( 'Up',    E_NORTH, 'North' ),
               ( 'Down',  E_SOUTH, 'South' ),
               ( 'space', E_PASS,  'Pass'  ) )

    self.navKeyHandlers = [ Binding( k, e, m ) for k, e, m in hanTup ]
    self.keyHandlers = self.navKeyHandlers
    self.chatHandlers = None # These vary based on conversation
    self.root.bind( "<Key>", self.kHandler )

    self.messages = []
    self.font = Font( family="Times New Roman", size=15 )
    self.tfont = Font( family="Times New Roman", size=15 ) # smaller font for talking.

    # create water to animate
    self.water = [ [], [] ] # calm / rough

    for w in ( 0, 1 ):
      for sn in range ( 0, ANIM_SEQ_CT ):
        self.water[ w ].append( getTkImg( tilesA, ( 7 + w ) * TW, 32 - sn * 2 ) )

    self.localInfo = {} # dict of wObjects keyed by screen (x, y)
    self.calcInfo()
    # Ship( self, 26, 75 ) # temp
    self.newMessage( "Start." )
    self.drawScreen()
    self.timer()

  def timer( self ):
    # Will be used to animate stuff
    self.root.after( 250, self.timer )
    self.animSeqNum += 1
    if self.animSeqNum >= ANIM_SEQ_CT:
      self.animSeqNum = 0
    self.calcInfo()
    self.drawScreen()

  def calcInfo( self ):
    '''
    Find the map objects on the screen and put them in a dict. This allows us to just do this once per turn.

    populate localInfo[ ( sX, sY ) ] # keyed by screen x,y
    o = object at sX, sY if present
    i = list of infos at x, y if present
    t = terrain at x, y
    s = structure at x, y
    '''
    localInfo = {}

    for sX in range ( -VIEW_DIST, VIEW_DIST + 1 ): # screen x, y relative to center ( 0, 0 )
      for sY in range ( -VIEW_DIST, VIEW_DIST + 1 ):
        localInfo[ ( sX, sY ) ] = self.getInfo( sX + self.party.x, sY + self.party.y )

    self.localInfo = localInfo

  def getInfo( self, mX, mY ):
    # Get the info at a particular map x,y coord
    o = s = t = None
    tp = DONTCARE
    sp = DONTCARE
    iList = []

    if mX < 0 or mX >= self.curMap[ 'tiles' ].width or mY < 0 or mY >= self.curMap[ 'tiles' ].height:
      mX = mY = 0 # use top left as the default 'off map' tile.
    else: # no info or objects off map
      for obj in self.curMap[ 'objects' ]:
        if obj.x == mX and obj.y == mY:
          o = obj
          break
      # Are there any infos defined there?
      infoList = self.curMap[ 'tiles' ].get_layer_by_name( "info" )
      for iElem in infoList:
        obj_x = int( iElem.x / TW )  # convert pixels to grid coords
        obj_y = int( iElem.y / TW )
        obj_w = int( iElem.width / TW )
        obj_h = int( iElem.height / TW )

        if ( mX >= obj_x ) and ( mX <= obj_x + obj_w - 1 ) and \
           ( mY >= obj_y ) and ( mY <= obj_y + obj_h - 1 ):
          iList.append( iElem )

    ti = self.curMap[ 'tiles' ].get_tile_image( mX, mY, TERRAIN )
    if ti:
      tup = ( ti[ 0 ], ti[ 1 ][ 0 ] / TW, ti[ 1 ][ 1 ] / TW )
      if tup in tileProperty:
        tp = tileProperty[ tup ]
      if tp == WATER_:
        ti = self.water[ 0 ][ self.animSeqNum ]
      elif tp == WATER_R_:
        ti = self.water[ 1 ][ self.animSeqNum ]
      else:
        ti = getTkImg( ti[ 0 ], ti[ 1 ][ 0 ], ti[ 1 ][ 1 ] ) # image from info
    si = self.curMap[ 'tiles' ].get_tile_image( mX, mY, STRUCTURES )
    if si:
      tup = ( si[ 0 ], si[ 1 ][ 0 ] / TW, si[ 1 ][ 1 ] / TW )
      if tup in tileProperty:
        sp = tileProperty[ ( si[ 0 ], si[ 1 ][ 0 ] / TW, si[ 1 ][ 1 ] / TW ) ]
      si = getTkImg( si[ 0 ], si[ 1 ][ 0 ], si[ 1 ][ 1 ] ) # image from info

    return wObject( o, iList, ti, si, tp, sp )

  def processTurn( self ):
    e = Binding( None, E_TURN, "Turn" )
    for c in self.curMap[ 'objects' ]:
      if not c.processEvent( e ):
        self.curMap[ 'objects' ].remove( c )
    self.calcInfo()
    self.drawScreen()

  def drawScreen( self ):
    v = self.visDict()
    c = self.canvas
    c.delete( "all" )

    # transparent images assume black background
    c.create_rectangle( 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, fill='black' )
    # add some borders.
    c.create_rectangle( DISP_WIDTH,                  0, DISP_WIDTH + 5, SCREEN_HEIGHT, fill='white' )
    c.create_rectangle( DISP_WIDTH, SCREEN_HEIGHT * .5, SCREEN_WIDTH,   SCREEN_HEIGHT * .5 + 5, fill="white" )

    for sX in range( -VIEW_DIST, VIEW_DIST + 1 ):
      for sY in range( -VIEW_DIST, VIEW_DIST + 1 ):
        if v[ sX, sY ] <= 0.0:
          continue
        i = self.localInfo[ ( sX, sY ) ]

        if i.o:
          oImage = i.o.displayInfo()
        else:
          oImage = None

        for img in ( i.ti, i.si, oImage ):
          if img:
            c.create_image( 16 + TW * ( VIEW_DIST + sX ), 16 + TW * ( VIEW_DIST + sY ), image=img )

    # Party
    index = 0
    for char in self.party.members:
      c.create_text( DISP_WIDTH + 10, 10 + 20 * index,
                     font=self.font, text=char.name, anchor=tk.W, fill='gray' )
      index += 1
    # Status
    index = 0
    for msg in self.messages[ -10 : ]:
      c.create_text( DISP_WIDTH + 10, SCREEN_HEIGHT * .5 + 20 + 20 * index,
                     font=self.font, text=msg, anchor=tk.W, fill='gray' )
      index += 1

    self.root.update()

  def transfer( self, name, x, y ):
    '''
    Transfer to map 'name' starting it initX, initY if not provided
    the map must have a spawn
    '''
    # Attempt to open map.
    if name in self.maps: # do we already have it?
      self.curMap = self.maps[ name ]
    else: # need to load it
      map = openMap( name, self )
      if map:
        # Add objects
        info = map[ 'tiles' ].get_layer_by_name( "info" )
        for i in info:
          if i.type == 'NPC':
            map[ 'objects' ].append( NPCFactory( i, self ) )

        self.maps[ name ] = map
        self.newMessage( 'Enter ' + name )
        self.curMap = map
        self.curMap[ 'objects' ].append( self.party )
      else:
        self.w.newMessage( 'Could not enter.' )
        return

    if x == None:
      x, y = getSpawn( self.curMap )

    self.party.x = x
    self.party.y = y

  def newMessage( self, msg):
    self.messages.append( msg )
    if len( self.messages ) > MAX_MESSAGES:
      # slow, but not a big list
      self.messages = self.messages[ -MAX_MESSAGES : ]

  def checkOpacity( self, sX, sY ):
    # check opacity at screen x,y
    i = self.localInfo[ ( sX, sY ) ]
    if i.tp == TREES_:
      op = .5
    elif i.tp == HILLS_:
      op = .5
    elif i.tp == MOUNTAINS_ or i.sp == WALL_:
      op = 1.0
    else:
      op = 0.0
    if self.night:
      op += .4

    return op

  def visDict( self ):
    '''
    Generate a dictionary of visibility. key( x, y ) screen coords

    You can use an algorithm or hard coded. Hard coding would be a pain to scale but you'd only have to
    calcuate a visibility matrix for one quadrant.
    '''
    vis = {}

    for x in range ( -VIEW_DIST, VIEW_DIST + 1 ):
      for y in range ( -VIEW_DIST, VIEW_DIST + 1 ):
        vis[ ( x, y ) ] = 0.0 # start with invisible

    # Go around from the edges.
    for i in range ( -VIEW_DIST, VIEW_DIST + 1 ):
      for ept in ( ( i, -VIEW_DIST ), ( i, VIEW_DIST ), ( -VIEW_DIST, i ), ( VIEW_DIST, i ) ):
        l = getLine( ( 0, 0 ), ( ept[ 0 ], ept[ 1 ] ) ) # ray from center out
        v = 1.0
        for p in l:
          if v > vis[ p ]: # choose the 'best' ray
            vis[ p ] = v
          if v > 0.0:
            v -= self.checkOpacity( p[ 0 ], p[ 1 ] )

    # handle direct up/down/left/right explicitly to fix results for u/d/l/r walls
    # That's the most annoying artifact of this algorithm
      for dir in ( E_NORTH, E_EAST, E_SOUTH, E_WEST ):
        visability = 1.0
        for i in range( 1, VIEW_DIST + 1 ):
          x = y = 0
          if dir == E_NORTH:
            y = -i
          elif dir == E_EAST:
            x = i
          elif dir == E_SOUTH:
            y = i
          elif dir == E_WEST:
            x = -i

          visability -= self.checkOpacity( x, y )
          if visability <= 0.0:
            continue

          if dir == E_NORTH:
            vis[ ( -1, -i ) ] = vis[ 1, -i ] = 1.0
          elif dir == E_EAST:
            vis[ ( i, 1 ) ] = vis[ i, -1 ] = 1.0
          elif dir == E_SOUTH:
            vis[ ( -1, i ) ] = vis[ 1, i ] = 1.0
          elif dir == E_WEST:
            vis[ ( -i, 1 ) ] = vis[ -i, -1 ] = 1.0

    return vis

  def chatConfig( self, txt, c ):
    # NPC calls this to 'say' something and put the responses in self.chatHandlers.
    # txt is what the NPC wants to say "Hey there goy."
    # c is list of cMessage
    if txt:
      self.newMessage( txt )
    if c:
      self.keyHandlers = []
      for ch in c:
        self.keyHandlers += ( Binding( ch.k, E_CHAT, None ), )
        self.newMessage( ch.k + ":" + ch.v )
    else:
      self.keyHandlers = self.navKeyHandlers

  def kHandler( self, event ):

    for h in self.keyHandlers:
      if h.k == event.keysym:
        self.party.processEvent( h )
        self.processTurn()
        break

w = WorldEngine()
w.root.mainloop()

