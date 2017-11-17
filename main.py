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

class WorldEngine ():

  def __init__( self ):
    self.root = tk.Tk()
    self.root.title( "Rogue" )
    self.canvas = tk.Canvas( self.root, width=SCREEN_WIDTH, height=SCREEN_HEIGHT )
    self.canvas.pack()

    self.maps = {} # maps
    self.maps[ worldMap ] = openMap( worldMap, self )
    self.curMap = self.maps[ worldMap ]

    self.night = False # tbd / time of day .. night / dawn / day / dusk

    # Find the starting location. By default there should be an object of type Spawn called Start
    initX, initY = getSpawn( self.curMap )
    assert( initX ), "No Start Spawn!"

    self.party = Party( self, initX, initY )
    self.curMap[ 'objects' ].append( self.party )

    mainChar = Character( "Foobar", self )
    self.party.addMember( mainChar )

    hanTup = ( ( 'Left',  E_WEST,  'West',  None ),
               ( 'Right', E_EAST,  'East',  None ),
               ( 'Up',    E_NORTH, 'North', None ),
               ( 'Down',  E_SOUTH, 'South', None ),
               ( 'space', E_PASS,  'Pass',  None ) )

    self.keyHandlers = [ Binding( k, e, m, g ) for k, e, m, g in hanTup ]
    self.root.bind( "<Key>", self.kHandler )

    self.messages = []
    self.font = Font( family="Times New Roman", size=20 )

    # Ship( self, 26, 75 ) # temp
    self.newMessage( "Start." )

  def getObject( self, x, y ):
    '''
    returned a named tuple of ( o, i, t, s )
    o = object at x, y if present
    i = info at x, y if present
    t = terrain at x, y
    s = structure at x, y
    '''
    o = t = s = None
    i = []
    if x < 0 or x >= self.curMap[ 'tiles' ].width or y < 0 or y >= self.curMap[ 'tiles' ].height:
      x = y = 0 # use top left as the default 'off map' tile.

    for obj in self.curMap[ 'objects' ]:
      if obj.x == x and obj.y == y:
        o = obj
        break

    # Is there any info defined there?
    info = self.curMap[ 'tiles' ].get_layer_by_name( "info" )
    for t in info:
      obj_x = int( t.x / TW )
      obj_y = int( t.y / TW )
      obj_w = int( t.width / 32 )
      obj_h = int( t.height / 32 )

      if ( x >= obj_x ) and ( x <= obj_x + obj_w - 1 ) and \
         ( y >= obj_y ) and ( y <= obj_y + obj_h - 1 ):
        i.append( t )

    tileInfo = self.curMap[ 'tiles' ].get_tile_image( x, y, TERRAIN )
    if tileInfo:
      txy = ( tileInfo[ 0 ], tileInfo[ 1 ][ 0 ] / TW, tileInfo[ 1 ][ 1 ] / TW )
      t = tileProperty[ txy ]

    tileInfo = self.curMap[ 'tiles' ].get_tile_image( x, y, STRUCTURES )
    if tileInfo:
      txy = ( tileInfo[ 0 ], tileInfo[ 1 ][ 0 ] / TW, tileInfo[ 1 ][ 1 ] / TW )
      s = tileProperty[ txy ]

    return wObject( o, i, t, s )

  def processTurn( self ):
    e = Binding( None, E_TURN, "Turn", None )
    for c in self.curMap[ 'objects' ]:
      if not c.processEvent( e ):
        self.curMap[ 'objects' ].remove( c )
    self.drawScreen()

  def drawScreen( self ):
    v = self.visDict()
    c = self.canvas
    c.delete( "all" )

    # Tile map assumes black background
    c.create_rectangle( 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, fill='black' )
    # add some borders.
    c.create_rectangle( DISP_WIDTH, 0, DISP_WIDTH + 5, SCREEN_HEIGHT, fill='white' )
    c.create_rectangle( DISP_WIDTH, SCREEN_HEIGHT * .5, SCREEN_WIDTH, SCREEN_HEIGHT * .5 + 5, fill="white" )

    for layer in ( TERRAIN, STRUCTURES ):
      for y in range ( -VIEW_DIST, VIEW_DIST + 1 ):
        for x in range ( -VIEW_DIST, VIEW_DIST + 1 ):
          if v[ x, y ] <= 0.0:
            continue
          mX = self.party.x + x # map x,y
          mY = self.party.y + y
          if mX < 0 or mX >= self.curMap[ 'tiles' ].width or mY < 0 or mY >= self.curMap[ 'tiles' ].height:
            mX = mY = 0 # use whatever is at 0,0 as a default for 'off the map'. Could make it a custom property.
          tileInfo = self.curMap[ 'tiles' ].get_tile_image( mX, mY, layer )
          if tileInfo:
            c.create_image( 16 + TW * VIEW_DIST + x * TW,
                            16 + TW * VIEW_DIST + y * TW,
                            image=getTkImg( tileInfo[ 0 ], tileInfo[ 1 ][ 0 ] / TW, tileInfo[ 1 ][ 1 ] / TW ) )
    # draw objecgts
    for o in self.curMap[ 'objects' ]:
      d = o.displayInfo( self.party.x, self.party.y )
      if d:
        if v[ ( d[ 0 ], d[ 1 ] ) ] > 0.0:
          c.create_image( 16 + TW * ( d[ 0 ] + VIEW_DIST ),
                          16 + TW * ( d[ 1 ] + VIEW_DIST ),
                          image=d[ 2 ] )
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
    transfer to map 'name' starting it initX, initY if not provided
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
        for t in info:
          if t.type == 'NPC':
            map[ 'objects' ].append( NPCFactory( t, w ) )

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

  def checkOpacity( self, x, y ):
    o = self.getObject( x, y )
    if o.t == TREES_:
      op = .5
    elif o.t == HILLS_:
      op = .5
    elif o.t == MOUNTAINS_ or o.s == WALL_:
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
            v -= self.checkOpacity( self.party.x + p[ 0 ], self.party.y + p[ 1 ] )

    # handle direct up/down/left/right explicitly to fix results for u/d/l/r walls
    # That's the most annoying artifact of this algorithm
      for dir in ( DIR_NORTH, DIR_EAST, DIR_SOUTH, DIR_WEST ):
        visability = 1.0
        for i in range( 1, VIEW_DIST + 1 ):
          x = y = 0
          if dir == DIR_NORTH:
            y = -i
          elif dir == DIR_EAST:
            x = i
          elif dir == DIR_SOUTH:
            y = i
          elif dir == DIR_WEST:
            x = -i

          visability -= self.checkOpacity( self.party.x + x, self.party.y + y )
          if visability <= 0.0:
            continue

          if dir == DIR_NORTH:
            vis[ ( -1, -i ) ] = vis[ 1, -i ] = 1.0
          elif dir == DIR_EAST:
            vis[ ( i, 1 ) ] = vis[ i, -1 ] = 1.0
          elif dir == DIR_SOUTH:
            vis[ ( -1, i ) ] = vis[ 1, i ] = 1.0
          elif dir == DIR_WEST:
            vis[ ( -i, 1 ) ] = vis[ -i, -1 ] = 1.0

    return vis

  def kHandler( self, event ):
    for h in self.keyHandlers:
      if h.k == event.keysym:
        self.party.processEvent( h )
        self.processTurn()
        break

w = WorldEngine()

w.drawScreen()
w.visDict()

w.root.mainloop()