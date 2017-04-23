
PI = 3.14159
TAU = 2 * PI
EFFECTIVE_ZERO = .00001

SCREEN_WIDTH  = 640
SCREEN_HEIGHT = 400

INIT_WORLD_X = 13
INIT_WORLD_Y = 54

worldMap = "maps/world"
tiles = "maps/tiles.png"
LGROUND = 0 # layers
LROAD = 1
LTOWN = 2
LCHAR = 3

VIEW_DIST = 5 # in tiles
TW = 32
MAX_EDGE_LENGTH = 10

# these tuple's ID tiles by x,y in tiles.png
TILE_WATER2   = ("maps/tiles.png", 1, 0)
TILE_WATER    = ("maps/tiles.png", 2, 0)
TILE_GRASS    = ("maps/tiles.png", 5, 0)
TILE_TREES1   = ("maps/tiles.png", 8, 0)
TILE_TREES2   = ("maps/tiles.png", 9, 0)
TILE_TREES3   = ("maps/tiles.png", 10, 0)
TILE_HILLS1a  = ("maps/tiles.png", 14, 0)
TILE_HILLS1b  = ("maps/tiles.png", 15, 0)
TILE_HILLS1   = ("maps/tiles.png", 11, 0)
TILE_HILLS2   = ("maps/tiles.png", 12, 0)
TILE_HILLS3   = ("maps/tiles.png", 13, 0)
TILE_CHAR     = ("maps/tilesAlpha.png", 12, 10)
TILE_BOAT     = ("maps/tilesAlpha.png", 1, 9)