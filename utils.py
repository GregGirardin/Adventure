import io, sys, pytmx, pickle, math
from collections import defaultdict, namedtuple
from constants import *

terrain = namedtuple( 'terrain', 'x y c' ) # coords in the tile map and the transit cost
wObject = namedtuple( 'wObject', 'o i t s' ) # Object, info, terrain structure
Binding = namedtuple( 'Binding', 'k f e m g') # keysym, func, event, message, flags

class Point():
  def __init__ ( self, x, y ):
    self.x = float( x )
    self.y = float( y )

  def distanceTo( self, p ): # p is another Point
     return math.sqrt( ( self.x - p.x ) ** 2 + ( self.y - p.y ) ** 2 )

  def directionTo( self, p ): # p is another point
    cx = p.x - self.x
    cy = p.y - self.y

    magnitude = math.sqrt( cx ** 2 + cy ** 2 )

    if magnitude < EFFECTIVE_ZERO:
      direction = 0
    else:
      if math.fabs( cx ) < EFFECTIVE_ZERO:
        if cy > 0:
          direction = -PI / 2
        else:
          direction = PI / 2
      elif cx > 0:
        direction = math.atan( cy / cx )
      else:
        direction = PI + math.atan( cy / cx )

    return direction

class terrainMap():
  '''
  A list of terrainMapEntry's that represent a collection of terrains (tiles) that we want to generate SPF maps
  for. So all the tiles that represent water (for boats or sea creatures) would be a map. All the passable forms of land
  (grass, hills, forest) would be another map... etc.
  Terrains not in this Map won't be included so are impassable (mountains for ships, water for creatures, etc)
  '''
  def __init__( self, name, terrains ):
    self.name = name
    self.terrains = terrains # terrain of (x, y, c) tuples

def openMap( name ):
  '''
  Return a dict of the tile map and the mappings for spf generate mappings if the map file is newer than the pickle
  spf will all us to route entities around the map.
  Ex:
  map {}
    [ 'tiles' ]
    [ 'objects' ]
    [ 'water' ] <- dict
      [ 'areaMap' ] <-
      [ 'aIDMap' ]
      [ 'edges' ]
    [ 'ground' ] <- dict
      [ 'areaMap' ]
      [ 'aIDMap' ]
      [ 'edges' ]
  '''

  map = {}
  map[ 'tiles' ] = pytmx.TiledMap( "maps/" + name + ".tmx" )
  map[ 'objects' ] = [] # characters, objects, etc

  # We need entities to be able to navigate water and ground, so two separate maps.
  terrainMaps = []

  tMapWater = terrainMap( 'water', # All the terrains that qualify as water and their cost.
                          ( terrain( 2, 0, 1 ),
                            terrain( 3, 0, 1 ),
                            terrain( 4, 0, 2 ) )
                        )
  tMapGround = terrainMap( 'ground',
                          ( terrain(  5, 0,  1 ),  # Grass 1
                            terrain(  6, 0,  1 ),  # Grass 2
                            terrain(  7, 0,  1 ),  # Grass w/ shrubs
                            terrain(  9, 0,  2 ),  # Lt shrubs
                            terrain( 10, 0,  2 ),  # Small trees
                            terrain( 11, 0,  3 ),  # Trees
                            terrain( 12, 0,  4 ),  # Hills
                            terrain( 13, 0,  5 ),  # Med hills
                            terrain( 14, 0, 10 ) ) # Mountains
                           )
  terrainMaps.append( tMapWater )
  terrainMaps.append( tMapGround )

  for mapping in terrainMaps:
    mFileName = "maps/" + name + "." + mapping.name + ".pk"
    try:
      print "Loading", mapping.name, "mapping info."
      map[ mapping.name ] = pickle.load( open( mFileName, 'rb' ) )
    except:
      print "Can't open", mFileName, "generating mappings."
      print "Coalesce start..."

      map[ mapping.name ] = {}
      w = map[ mapping.name ]
      w[ 'areaMap' ] = subdivideMap( map[ 'tiles' ], mapping )
      w[ 'aIDMap' ] = areaIdMap( w[ 'areaMap' ] )
      w[ 'edges' ] = mapEdges( w[ 'areaMap' ], w[ 'aIDMap' ] )
      with open( mFileName, 'wb' ) as f:
        pickle.dump( w, f, protocol=pickle.HIGHEST_PROTOCOL )

  return map

def getLine( start, end ):
  # Bresenham's Line Algorithm

  # Setup initial conditions
  x1, y1 = start
  x2, y2 = end
  dx = x2 - x1
  dy = y2 - y1

  # Determine how steep the line is
  is_steep = abs( dy ) > abs( dx )

  # Rotate line
  if is_steep:
    x1, y1 = y1, x1
    x2, y2 = y2, x2

  # Swap start and end points if necessary and store swap state
  swapped = False
  if x1 > x2:
    x1, x2 = x2, x1
    y1, y2 = y2, y1
    swapped = True

  # Recalculate differentials
  dx = x2 - x1
  dy = y2 - y1

  # Calculate error
  error = int( dx / 2.0 )
  ystep = 1 if y1 < y2 else -1

  # Iterate over bounding box generating points between start and end
  y = y1
  points = []
  for x in range ( x1, x2 + 1 ):
    coord = ( y, x ) if is_steep else ( x, y )
    points.append( coord )
    error -= abs( dy )
    if error < 0:
      y += ystep
      error += dx

  # Reverse the list if the coordinates were swapped
  if swapped:
    points.reverse()
  return points

def getSpawn( map ):
  ''' Most maps have a Spawn type object called Start '''
  initX = initY = None
  info = map[ 'tiles' ].get_layer_by_name( "info" )
  for t in info:
    if t.type == "Spawn" and t.name == "Start":
      initX = int( t.x / TW )
      initY = int( t.y / TW )
      break

  return initX, initY

def checkOverlap( r1a, r1b, r2a, r2b ):
  # Check if rectangles r1 and r2 overlap
  # If one rectangle is on left side of other
  if( ( r1a.x >= r2a.x and r1a.x < r2b.x ) or
      ( r2a.x >= r1a.x and r2a.x < r1b.x ) ) and \
    ( ( r1a.y > r2b.y  and r1a.y <= r2a.y ) or
      ( r2a.y > r1b.y  and r2a.y <= r1a.y ) ):
    return False

  return True

def subdivideMap( tmxMap, tMap ):
  '''
  Subdivide into squares of equal cost. This takes time but only needs to be done once when the map is changed.

  Group into square areas of the same cost to reduce number of vertices.

            1 1 2 2
            1 1 2 2
            3 3 1 1 1  <-- pointMap
            3 3 1 1 1
                1 1 1

  Ex: represent ^ as:

  coalDict = ( LengthOfSide, cost ) # cost = 'cost' * size
      [ ( 1, 1 ) ] = ( 2, 2 )
      [ ( 3, 1 ) ] = ( 2, 4 )
      [ ( 1, 3 ) ] = ( 2, 6 )
      [ ( 3, 3 ) ] = ( 3, 3 )
  '''
  pointMap = {} # Dict[ ( x, y ) ) ] = cost. For every valid tile
  for x in range ( 0, tmxMap.width ):
    for y in range ( 0, tmxMap.height ):
      tileInfo = tmxMap.get_tile_image( x, y, TERRAIN )
      if tileInfo:
        txy = ( tileInfo[ 1 ][ 0 ] / TW, tileInfo[ 1 ][ 1 ] / TW )
        for t in tMap.terrains:
          if txy == ( t.x, t.y ):
            pointMap[ ( x, y ) ] = t.c
            break
  print len( pointMap ), "Map coordinates."

  # now coalesce pointMap into coalDict
  coalDict = {} # Dict[ ( x,y ) ] = ( size, cost )

  # Both lists have the same info, just keyed differently
  sizeMap = {} # Dict [ size ] = list of ( x, y ) blocks
  posMap  = {} # Dict [ ( x, y ) ] = size
  # Used for finding edges and determining the area a point is in.

  # Determine biggest square from every point in map
  for size in range( 1, MAX_EDGE_LENGTH + 1 ):
    sizeMap[ size ] = []

  print "Subdividing."
  for y in range( 0, tmxMap.height ):
    if not y % 10:
      print ".", # debug
    for x in range( 0, tmxMap.width ):
      maxFound = False
      xy = ( x, y )
      if not xy in pointMap.keys():
        continue # Not a valid coordinate for this map
      # Find size of block at ( x, y )
      cost = pointMap[ xy ]
      '''
      Find how big of an square of equal cost we can find with (x, y) as top left

      (x, y)
            C C C C C D <- this would produce 4 at (x, y), 3 at (x + 1, y )...
            C C C C C D    if C and D are different costs.
            C C C C C D
            C C C C D D
            D D D D D D
      '''
      for edgeLen in range( 1, MAX_EDGE_LENGTH + 1 ):
        for ix in range( 0, edgeLen ):
          check1 = ( x + edgeLen - 1, y + ix )
          check2 = ( x + ix, y + edgeLen - 1 )
          if not check1 in pointMap.keys() or not check2 in pointMap.keys() or \
            pointMap[ check1 ] != cost or pointMap[ check2 ] != cost:
            maxFound = True
            break
        if maxFound:
          break
      if maxFound:
        edgeLen -= 1 # edgeLen failed, last success is edgeLen - 1
      if edgeLen > MAX_EDGE_LENGTH - 2:
        # This is a big square. Process it immediately to speed things up by taking the block's points out of pointMap
        coalDict[ xy ] = ( edgeLen, edgeLen * cost )
        for checkX in range( x, x + edgeLen ):
          for checkY in range( y, y + edgeLen ):
            del pointMap[ ( checkX, checkY ) ] # These points have been coalesced into coalDict
      else:
        sizeMap[ edgeLen ].append( xy )
        posMap[ xy ] = edgeLen
  print
  # Now coalesce, largest blocks first.
  for size in range( MAX_EDGE_LENGTH, 0, -1 ):
    print len( sizeMap[ size ] ), size, "blocks"
    while len( sizeMap[ size ] ) > 0:
      block = sizeMap[ size ].pop( 0 )
      del posMap[ block ]
      coalDict[ block ] = ( size, size * pointMap[ block ] ) # add to coalDict
      # Prune overlapping blocks. Only need to check blocks within a distance that could overlap.
      for checkX in range( block[ 0 ] - MAX_EDGE_LENGTH, block[ 0 ] + size ):
        for checkY in range( block[ 1 ] - MAX_EDGE_LENGTH, block[ 1 ] + size ):
          if checkX == block[ 0 ] and checkY == block[ 1 ]:
            continue # this is us
          xy = ( checkX, checkY )
          if xy in posMap.keys():
            chkSize = posMap[ xy ]
            if checkOverlap( Point( block[ 0 ], block[ 1 ] ),
                             Point( block[ 0 ] + size, block[ 1 ] + size ),
                             Point( checkX, checkY ),
                             Point( checkX + chkSize - 1, checkY + chkSize - 1 ) ):
              del posMap[ xy ]
              sizeMap[ chkSize ].remove( xy )
  print len( coalDict ), "Vertices."

  return coalDict

def areaIdMap( aMap ):
  # aMap is a dictionary of areas. return a dictionary of the area ID of every point
  # So given any x,y, we can get the area without calculating it.

  aidMap = {} # Dict [(x,y)] = (x,y) of top left (the area's ID).
  for k,v in aMap.items():
    for x in range( k[ 0 ], k[ 0 ] + v[ 0 ] ):
      for y in range( k[ 1 ], k[ 1 ] + v[ 0 ] ):
        aidMap[ ( x, y ) ] = ( k[ 0 ], k[ 1 ] )

  return aidMap

def mapEdges( aMap, aidMap = None ):
  '''
  Return a list of edges. Areas are all rectangles.
  Ex:
  XXXXXZZAA
  XXXXXYYAA
  XXXXXYYAA
  has the following edges:
  XZ XY YX YZ YA ZY AZ YY
  '''
  if not aidMap:
    aidMap = areaIdMap( aMap )
  totalEdges = 0
  edges = []
  for k, v in aMap.items():
    for e in range( 0, v[ 0 ] ):
      for p in ( ( k[ 0 ] - 1,          k[ 1 ] + e ), # left
                 ( k[ 0 ] + e,          k[ 1 ] - 1 ), # above
                 ( k[ 0 ] + v[ 0 ] + 1, k[ 1 ] + e ), # right
                 ( k[ 0 ] + e,          k[ 1 ] + v[ 0 ] + 1 ) ): # below
        if p in aidMap.keys():
          aid = aidMap[ p ]
          edge = ( k, aid, aMap[ k ][ 0 ] + aMap[ aid ][ 0 ] )
          if not edge in edges:
            edges.append( edge )
            totalEdges += 1

  print totalEdges, "edges."
  return edges

def tileInfoFromtInfo( t ):
  return( t.filename, ( t.gx * TW, t.gy * TW, TW, TW ), None )

# https://gist.github.com/kachayev/5990802
from collections import defaultdict
from heapq import *

def spf( edges, f, t ):
  solution = []
  g = defaultdict( list )
  for l,r,c in edges:
    g[ l ].append( ( c, r ) )

  q, seen = [ ( 0, f, () ) ], set()
  while q:
    ( cost, v1, path ) = heappop( q )
    if v1 not in seen:
      seen.add(v1)
      path = ( v1, path )
      if v1 == t:
        while len ( path ):
          if path[ 0 ]:
            solution.insert( 0, path[ 0 ] )
          path = path[ 1 ]
        return cost, solution
      for c, v2 in g.get( v1, () ):
        if v2 not in seen:
          heappush( q, ( cost + c, v2, path ) )
  return None

def testSPF():
  edges = [ ("A", "B", 1 ),
            ("B", "C", 2 ),
            ("C", "D", 4 ) ]

  print "=== Dijkstra ==="
  print spf( edges, "A", "D" )

traceLevel = 3

def trace( level, msg ):
  if level > traceLevel:
    print msg