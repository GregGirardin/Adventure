
PI = 3.14159
TAU = 2 * PI
EFFECTIVE_ZERO = .00001

SCREEN_WIDTH  = 640
SCREEN_HEIGHT = 400

INIT_WORLD_X = 13
INIT_WORLD_Y = 54

worldMap = "maps/world"
tiles = "maps/tiles.png"
alTiles = "maps/tilesAlpha.png"
LGROUND = 0 # layers
LROAD = 1
LTOWN = 2
LCHAR = 3

VIEW_DIST = 5 # in tiles
TW = 32
MAX_EDGE_LENGTH = 10

# these tuple's ID tiles by x,y in tiles.png
TILE_WATER2   = (tiles, 1, 0)
TILE_WATER    = (tiles, 2, 0)
TILE_GRASS    = (tiles, 5, 0)
TILE_TREES1   = (tiles, 8, 0)
TILE_TREES2   = (tiles, 9, 0)
TILE_TREES3   = (tiles, 10, 0)
TILE_HILLS1a  = (tiles, 14, 0)
TILE_HILLS1b  = (tiles, 15, 0)
TILE_HILLS1   = (tiles, 11, 0)
TILE_HILLS2   = (tiles, 12, 0)
TILE_HILLS3   = (tiles, 13, 0)
TILE_CHAR     = (alTiles, 12, 10)
TILE_BOAT     = (alTiles, 1, 9)

EVENT_NORTH = 1
EVENT_EAST = 2
EVENT_SOUTH = 3
EVENT_WEST = 4

STATUS_WALKING = 1
STATUS_SHIP = 2
STATUS_HORSE = 3
STATUS_CARPET = 4

DIR_NORTH = 0
DIR_EAST = 1
DIR_SOUTH = 2
DIR_WEST = 3
