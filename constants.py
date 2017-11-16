from collections import namedtuple

tInfo = namedtuple( 'tInfo', 'filename gx gy' )

PI = 3.14159
TAU = 2 * PI
EFFECTIVE_ZERO = .00001

VIEW_DIST = 7 # In tiles
TW = 32 # Tile edge in pixels

INFO_WIDTH = 200 # With of dialog
DISP_WIDTH = ( VIEW_DIST * 2 + 1 ) * TW # width of world display
SCREEN_WIDTH  = DISP_WIDTH + INFO_WIDTH
SCREEN_HEIGHT = DISP_WIDTH

INIT_WORLD_X = 27
INIT_WORLD_Y = 75

worldMap = "world"
tiles = "maps/tiles.png"
alTiles = "maps/tilesA.png" # tiles with alpha to overlay
# map layers
TERRAIN = 0
STRUCTURES = 1
INFO = 2

MAX_EDGE_LENGTH = 10
MAX_MESSAGES = 20 # message history length

# These tuple's ID tiles by x,y in tiles.png
TILE_CHAR = tInfo( alTiles, 12, 10 )

# Objects are a bit of a summary, all water tiles are WATER_
# all grass tiles are GRASS_, etc.
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


tileProperty = {
  # dict of (file, tile-x, tile-y) we can look up to get a tie's general property
  ( tiles,  1, 0 ) : WATER_,
  ( tiles,  2, 0 ) : WATER_,
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
  ( tiles, 20, 0 ) : STRUCTURE_,
  ( tiles,  0, 1 ) : PATH_,
  ( tiles,  1, 1 ) : PATH_,
  ( tiles,  2, 1 ) : PATH_,
  ( tiles,  3, 1 ) : PATH_,
  ( tiles,  4, 1 ) : PATH_,
  ( tiles,  6, 1 ) : PATH_,
  ( tiles,  6, 4 ) : GATE_,
  ( tiles,  8, 2 ) : FLOOR_,
  ( tiles,  9, 2 ) : FLOOR_,
  ( tiles,  0, 2 ) : FLOOR_,
  ( tiles, 12, 2 ) : ROCKS_,
  ( tiles, 15, 2 ) : WALL_,
  ( tiles, 15, 2 ) : WALL_,

}

# Events
E_NORTH = 1
E_EAST  = 2
E_SOUTH = 3
E_WEST  = 4
E_ENTER = 5
E_TURN = 100

DIR_NORTH = 0
DIR_EAST  = 1
DIR_SOUTH = 2
DIR_WEST  = 3