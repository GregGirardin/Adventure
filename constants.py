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
DONTCARE   = 0 # nobody cares about what this is.
WATER_     = 1
GRASS_     = 2
TREES_     = 3
HILLS_     = 4
MOUNTAINS_ = 5
STRUCTURE_ = 6
PATH_      = 7
GATE_      = 8
BOAT_      = 10
ROAD_      = 11
PARTY_     = 12
FLOOR_     = 13
ROCKS_     = 14
WALL_      = 15
DOCK_      = 16
NPC_       = 20

tileProperty = \
  {
  # dict of ( file, tile-x, tile-y ) we can look up to get a general property
  ( tilesA, 0, 0 ) : WATER_,
  ( tiles,  5, 0 ) : GRASS_,
  ( tiles,  8, 0 ) : TREES_,
  ( tiles,  9, 0 ) : TREES_,
  ( tiles, 10, 0 ) : TREES_,
  ( tiles, 14, 2 ) : TREES_,
  ( tiles, 11, 0 ) : HILLS_,
  ( tiles, 12, 0 ) : HILLS_,
  ( tiles, 14, 0 ) : HILLS_,
  ( tiles, 15, 0 ) : HILLS_,
  ( tiles, 16, 0 ) : HILLS_,
  ( tiles, 13, 0 ) : MOUNTAINS_,
  ( tilesA,18, 0 ) : STRUCTURE_,
  ( tilesA,20, 0 ) : STRUCTURE_,
  ( tilesA,21, 0 ) : STRUCTURE_,
  ( tilesA,27, 0 ) : STRUCTURE_,
  ( tilesA, 0, 1 ) : PATH_,
  ( tilesA, 1, 1 ) : PATH_,
  ( tilesA, 2, 1 ) : PATH_,
  ( tilesA, 3, 1 ) : PATH_,
  ( tilesA, 4, 1 ) : PATH_,
  ( tilesA, 5, 1 ) : PATH_,
  ( tilesA, 6, 1 ) : PATH_,
  ( tiles,  8, 2 ) : FLOOR_,
  ( tiles,  9, 2 ) : FLOOR_,
  ( tiles,  0, 2 ) : FLOOR_,
  ( tiles, 14, 2 ) : WALL_,
  ( tiles, 15, 2 ) : WALL_,
  ( tilesA,10, 3 ) : DOCK_,
  ( tilesA,11, 3 ) : DOCK_,
  ( tilesA, 6, 4 ) : GATE_,
  ( tilesA,25, 4 ) : GATE_,
  }

# Events
E_NORTH = 1
E_EAST  = 2
E_SOUTH = 3
E_WEST  = 4
E_PASS  = 5
E_TURN  = 100

DIR_NORTH = 0
DIR_EAST  = 1
DIR_SOUTH = 2
DIR_WEST  = 3


# NPC movements
M_MEANDER = 1 # meander around in proximity to home point