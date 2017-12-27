from collections import namedtuple

PI = 3.14159
TAU = 2 * PI
EFFECTIVE_ZERO = .00001

ANIM_SEQ_CT = 8 # cycle through 4 images for stuff we want to animate.

VIEW_DIST = 7 # In tiles
TW = 32 # Tile edge in pixels

INFO_WIDTH = 200 # With of dialog
DISP_WIDTH = ( VIEW_DIST * 2 + 1 ) * TW # width of world display
SCREEN_WIDTH  = DISP_WIDTH + INFO_WIDTH
SCREEN_HEIGHT = DISP_WIDTH

worldMap = "world"
tiles  = "maps/tiles.png"
tilesA = "maps/tilesA.png" # tiles with alpha to overlay

# map layers
TERRAIN    = 0
STRUCTURES = 1
INFO       = 2

MAX_EDGE_LENGTH = 10
MAX_MESSAGES    = 20 # Message history length

# Objects are a bit of a summary, all water tiles are WATER_ all grass tiles are GRASS_, etc.
DONTCARE   = 0
WATER_     = 1
WATER_R_   = 2 # Rough
GRASS_     = 3
TREES_     = 4
HILLS_     = 5
MOUNTAINS_ = 6
PATH_      = 8
GATE_      = 9
BOAT_      = 10
PARTY_     = 11
WALL_      = 12
DOCK_      = 13
NPC_       = 20

tileProperty = {
  # dict of ( file, tile-x, tile-y ) we can look up to get a general property
  ( tilesA,  0, 0 ) : WATER_,
  ( tilesA,  1, 0 ) : WATER_R_,
  ( tiles,   5, 0 ) : GRASS_,
  ( tiles,   8, 0 ) : TREES_,
  ( tiles,   9, 0 ) : TREES_,
  ( tiles,  10, 0 ) : TREES_,
  ( tiles,  14, 2 ) : TREES_,
  ( tiles,  11, 0 ) : HILLS_,
  ( tiles,  12, 0 ) : HILLS_,
  ( tiles,  14, 0 ) : HILLS_,
  ( tiles,  15, 0 ) : HILLS_,
  ( tiles,  16, 0 ) : HILLS_,
  ( tiles,  13, 0 ) : MOUNTAINS_,
  ( tilesA,  0, 1 ) : PATH_,
  ( tilesA,  1, 1 ) : PATH_, # Only move 'fast' along these PATH_s
  ( tiles,  11, 2 ) : WALL_, # Actually a window...
  ( tiles,  14, 2 ) : WALL_,
  ( tiles,  15, 2 ) : WALL_,
  ( tilesA, 10, 3 ) : DOCK_,
  ( tilesA, 11, 3 ) : DOCK_,
  ( tilesA,  6, 4 ) : GATE_,
  ( tilesA, 25, 4 ) : GATE_,
}

# Events
E_NORTH = 0
E_EAST  = 1
E_SOUTH = 2
E_WEST  = 3
E_CHAT  = 4

E_PASS  = 10
E_TURN  = 100

# Talking
T_NO = 0
T_BSL = 1 # buy / sell / leave
T_BUY = 2
T_SELL = 3


# NPC movements
M_MEANDER = 1 # meander around in proximity to home point

'''
Items will have a durability of 0-100%, 0% = useless.
Enchanted = %10%, increasing durability.

1PP=10GP=100SP=1000CP, platinum, gold, silver, copper each weighs .1

Magic
M - Missile
F - Fireball
C - Coldness
E - Earthquake
'''

class Item():
  def __init__( self, key, name, weight, nomCost ):

    self.key = key # a shorthand ID
    self.name = name
    self.weight = weight
    self.nomCost = nomCost # in GP

    # variables...
    self.quality = 100.0 # float 0.0 = 100.0%
    self.actualBuyCost = nomCost
    self.actualSellCost = nomCost
    self.selectChar = None
    self.count = 1 # Generic items (e.g. coins) may be aggregated using a count.

class Armor( Item ):
  def __init__( self, key, name, weight, nomCost, defense ):
    Item.__init__( self, key, name, weight, nomCost )
    self.defense = defense

class Weapon( Item ):
  def __init__( self, key, name, weight, nomCost, damage ):
    Item.__init__( self, key, name, weight, nomCost )
    self.damage = damage

armors = \
  [
  Armor( 'AC', 'Cloth',          1,  1.0,  1 ),
  Armor( 'AL', 'Leather',        5, 30.0,  5 ),
  Armor( 'AM', 'Chain Mail',    10, 60.0, 20 ),
  Armor( 'AP', 'Plate Mail',    20, 80.0, 50 ),
  Armor( 'AW', 'Wooden Shield',  5, 20.0,  3 ),
  Armor( 'AI', 'Iron Shield',   20, 40.0, 15 )
  ]

weapons = \
  [
  Weapon( 'WS', 'Staff',            1,  1.0,  1 ),
  Weapon( 'WD', 'Dagger',           2,  2.0,  2 ),
  Weapon( 'WW', 'Short Sword',      4,  4.0, 10 ),
  Weapon( 'WL', 'Long Sword',       6,  8.0, 20 ),
  Weapon( 'W2', 'Two Handed Sword', 8, 14.0, 50 ),
  Weapon( 'WA', 'Axe',              6,  8.0, 15 ),
  Weapon( 'WM', 'Mace',             5,  6.0, 12 ),
  Weapon( 'WB', 'Bow',              4,  3.0, 20 ),
  Weapon( 'WX', 'Crossbow',         4,  6.0, 50 )
  ]

items = \
  [
  Item( 'IT', 'Torch',          1,  2.0 ),
  Item( 'IL', 'Lantern',        2, 10.0 ),
  Item( 'IO', 'Lantern Oil',    1,  1.0 ),
  Item( 'IS', 'Silver Piece',   1,  0.0 ),
  Item( 'IG', 'Gold Piece',     1,  0.0 ),
  Item( 'IP', 'Platinum Piece', 1,  0.0 ),
  ]

def itemFromKey( key ):

  for iList in ( armors, weapons, items ):
    for item in iList:
      if item.key == key:
        return item

  return None