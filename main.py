#!/usr/bin/python

from PIL import Image, ImageTk
import pytmx
import Tkinter as tk
from tkFont import Font
import time
from constants import *
from utils import *
from ship import *
from party import *
import math

class WorldEngine ():

  def __init__( self ):
    self.root = tk.Tk()
    self.root.title( "Rogue" )
    self.canvas = tk.Canvas( self.root, width=SCREEN_WIDTH, height=SCREEN_HEIGHT )
    self.canvas.pack()

    self.images = []
    self.tkImages = {}
    self.worldMap = openMap( worldMap )
    self.curMap = self.worldMap

    self.party = Party( self )
    self.mainChar = Character( "Foobar", self )
    self.party.addMember( self.mainChar )
    self.party.addMember( Character( "Twobar", self ) )

    hanTup = (
      ( "Left",  None, E_WEST,  'West',  None ),
      ( "Right", None, E_EAST,  'East',  None ),
      ( "Up",    None, E_NORTH, 'North', None ),
      ( "Down",  None, E_SOUTH, 'South', None ),
      ( "e",     None, E_ENTER, 'Enter', None )
      )
    self.keyHandlers = [ Binding( k, f, e, m, g ) for k, f, e, m, g  in hanTup ]
    self.root.bind( "<Key>", self.kHandler )

    self.messages = []
    self.font = Font( family="Times New Roman", size=20 )

    Ship( self, 26, 75 ) # temp
    self.newMessage( "Start.")

  def getObject( self, x, y ):
    '''
    returned a named tuple of ( o, i, t )
    o = object at x, y if present
    i = info at x, y if present
    t = terrain at x, y
    '''
    o = i = t = None

    for obj in self.curMap[ 'objects' ]:
      if obj.x == x and obj.y == y:
        o = obj
        break

    # Is there any info defined there?
    info = self.curMap[ 'tiles' ].get_layer_by_name( "info" )
    for t in info:
      if float( x * TW ) == t.x and float( y * TW ) == t.y:
        i = t.name
        break # can only be one

    tileInfo = self.curMap[ 'tiles' ].get_tile_image( x, y, TERRAIN )
    if tileInfo:
      txy = ( tileInfo[ 0 ], tileInfo [ 1 ][ 0 ] / TW, tileInfo[ 1 ][ 1 ] / TW )
      t = tileProperty[ txy ]

    return wObject( o, i, t )

  def addWorldObject( self, o ):
    self.curMap[ 'objects' ].append( o )

  def getTkImg( self, t ):
    # t is a tileInfo,tuple of ( filename, (tile x, y, width, height), flags )
    if t is None:
      return None
    if not t[ 0 ] in self.tkImages:
      self.tkImages[ t[ 0 ] ] = {} # a dictionary of tk images. Key is filename
    d = self.tkImages[ t[ 0 ] ]

    if not( t[ 1 ][ 0 ], t[ 1 ][ 1 ]) in d: # Keyed by x,y tuple.
      spriteMap = Image.open( t[ 0 ] )
      img = spriteMap.crop( box = ( t[ 1 ][ 0 ],
                                    t[ 1 ][ 1 ],
                                    t[ 1 ][ 0 ] + t[ 1 ][ 2 ],
                                    t[ 1 ][ 1 ] + t[ 1 ][ 3 ] ) )
      tkImg = ImageTk.PhotoImage( img )
      self.images.append( tkImg )
      d[ ( t[ 1 ][ 0 ], t[ 1 ][ 1 ] ) ] = tkImg

    return d[ ( t[ 1 ][ 0 ],t[ 1 ][ 1 ] ) ] # dict keyed by x, y tuple

  def processTurn( self ):
    for c in self.curMap[ 'objects' ]:
      if not c.processEvent( E_TURN ):
        self.curMap[ 'objects' ].remove( c )
    self.drawScreen()

  def drawScreen( self ):
    v = self.visDict()
    c = self.canvas
    c.delete( "all" )

    # Tile map assumes black background
    c.create_rectangle( 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, fill="black" )
    # add some borders.
    c.create_rectangle( DISP_WIDTH, 0, DISP_WIDTH + 5, SCREEN_HEIGHT, fill="white" )
    c.create_rectangle( DISP_WIDTH, SCREEN_HEIGHT * .5, SCREEN_WIDTH, SCREEN_HEIGHT * .5 + 5, fill="white" )

    for layer in ( TERRAIN, STRUCTURES ):
      for y in range( -VIEW_DIST, VIEW_DIST + 1 ):
        for x in range( -VIEW_DIST, VIEW_DIST + 1 ):
          if v[ x, y ] <= 0.0:
            continue
          tX = self.party.x + x # 'tile's x,y'
          tY = self.party.y + y
          if tX < 0 or tX >= self.curMap[ 'tiles' ].width or tY < 0 or tY >= self.curMap[ 'tiles' ].height:
            tX = 0 # 0, 0 is water
            tY = 0
          tileInfo = self.curMap[ 'tiles' ].get_tile_image( tX, tY, layer )
          if tileInfo:
            c.create_image( 16 + TW * VIEW_DIST + x * TW,
                            16 + TW * VIEW_DIST - y * TW, # screen y is flipped
                            image = self.getTkImg( tileInfo ) )
    for o in self.curMap[ 'objects' ]:
      d = o.displayInfo()
      if d:
        if v[ ( d[ 0 ], d[ 1 ] ) ] > 0.0:
          c.create_image( 16 + TW * ( d[ 0 ] + VIEW_DIST ),
                          16 + TW * ( d[ 1 ] + VIEW_DIST ),
                          image=d[ 2 ] )
    # Party
    index = 0
    for char in self.party.members:
      c.create_text( DISP_WIDTH + 10,
                     10 + 20 * index,
                     font=self.font,
                     text=char.name,
                     anchor=tk.W,
                     fill="gray" )
      index += 1
    # Status
    index = 0
    for msg in self.messages[ -10 : ]:
      c.create_text( DISP_WIDTH + 10,
                     SCREEN_HEIGHT * .5 + + 20 + 20 * index,
                     font=self.font,
                     text= msg,
                     anchor=tk.W,
                     fill="gray" )
      index += 1

    self.root.update()

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
    elif o.t == MOUNTAINS_:
      op = 1.0
    else:
      op = 0
    # op =+ .4 # night

    return op

  def visDict( self ):
    # Generate a dictionary of visibility. key(x, y) screen coords
    vis = {}
    # Go around from the edges.
    for i in range( -VIEW_DIST, VIEW_DIST + 1 ):
      for ept in( ( i, -VIEW_DIST ),( i, VIEW_DIST ),( -VIEW_DIST, i ),( VIEW_DIST, i ) ):
        l = getLine( ( 0, 0 ), ( ept[ 0 ], ept[ 1 ] ) ) # ray from center out
        v = 1.0
        for p in l:
          vis[ p ] = v
          if v > 0.0:
            v -= self.checkOpacity( self.party.x + p[ 0 ], self.party.y + p[ 1 ] )
    return vis

  def kHandler( self, event ):
    for h in self.keyHandlers:
      if h.k == event.keysym:
        if h.f:
          h.f()
        if h.e:
          self.party.processEvent( h.e )
        if h.m:
          self.newMessage( h.m )
        self.processTurn()
        break

w = WorldEngine()

w.drawScreen()
w.visDict()

w.root.mainloop()