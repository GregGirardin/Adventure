import { c } from './Constants.js';
import { gManager } from './main.js';

let outsideEdges = undefined;
let radialLines = undefined; // array of lines from (0,0) to all outside edges.

export class Point
{
  constructor( x, y )
  {
    this.x = x;
    this.y = y;
  }
}

export function positionIsOnMap( map, p )
{
  if( ( p.y < 0 ) || ( p.y >= map.height ) || ( p.x < 0 ) || ( p.x >= map.width ) )
     return false;
  return true;
}

export function mapWrap( map, p )
{
  return new Point( ( p.x + map.width ) % map.width,( p.y + map.height ) % map.height );
}

export function generateVisibilityMap( map, distance, observerPos )
{
  if( !outsideEdges )
  {
    // first time. calculate some things that don't change.
    outsideEdges = []; // array of points of the outside edges of the displayable area
    radialLines = [];

    outsideEdges = outsideEdges.concat( getLine( new Point( -distance,    -distance ),     new Point(  distance,    -distance ) ) ); // Top edge
    outsideEdges = outsideEdges.concat( getLine( new Point(  distance,    -distance + 1 ), new Point(  distance,     distance ) ) ); // Right
    outsideEdges = outsideEdges.concat( getLine( new Point( -distance,    -distance + 1 ), new Point( -distance,     distance ) ) ); // Left
    outsideEdges = outsideEdges.concat( getLine( new Point( -distance + 1, distance ),     new Point(  distance - 1, distance ) ) ); // Bottom

    const c = new Point( 0, 0 );

    // Create array of lines from the center to the outside edges.
    for( let p of outsideEdges )
    {
      let l = getLine( c, p );
      l.shift();      // delete the first point of the line at (0, 0) where the party is
      radialLines.push( l );
    }
  }

  let visibility = {}; // an object keyed by [ screenX, screenY ] where 'true' means the grid is visible.
  for( let x = -distance;x <= distance;x++ )
    for( let y = -distance;y <= distance;y++ )
      visibility[ [ x, y ] ] = false; // use array as object key, TBD: much slower than a 2D array?

  visibility[ [ 0, 0 ] ] = true;
  // now trace allong each radial line from inside out, once you hit something opaque the rest of the line is shadowed.
  let tileLayer = getActiveLayerByName( map, "Terrain" );

  let mapPos = new Point( 0, 0 );
  for( let l of radialLines )
    for( let p of l ) // for the points in the line
    {
      visibility[ [ p.x, p.y ] ] = true;
      mapPos.x = observerPos.x + p.x;
      mapPos.y = observerPos.y + p.y;
      mapPos = mapWrap( map, mapPos );
      let tileId = tileLayer.data[ mapPos.y * map.width + mapPos.x ];
      if( gManager.getTileProperty( tileId, "opaque" ) == true )
        break;
    }
  return( visibility );
}

// Maps have activeGroupId at the root. In that group there are multiple layers.
// Typically a world map of tiles called "Terrain" and area information called "Locations".  
export function getActiveLayerByName( map, name )
{
  for( let group of map.layers )
    if( group.id == map.activeGroupId )
    {
      for( let layer of group.layers )
        if( layer.name == name )
          return layer;
    }
  
  return undefined;
}

export function getGroupIdByName( map, name )
{
  for( let group of map.layers )
    if( group.name == name )
      return( group.id );

  return undefined;
}

export function getObjsAtPostion( objects, pos )
{
  let objs = [];
  for( let obj of objects )
    if( ( pos.x >= obj.x ) && ( pos.x <= ( obj.x + obj.width ) ) &&
        ( pos.y >= obj.y ) && ( pos.y <= ( obj.y + obj.height ) ) )
      objs.push( obj );

  return objs;
}

// returns array of Point
export function getLine( from, to )
{
  let p = new Point( from.x, from.y ); // don't want to modify parameters.

  const dx = Math.abs( to.x - p.x );
  const dy = Math.abs( to.y - p.y );
  const sx = Math.sign( to.x - p.x );
  const sy = Math.sign( to.y - p.y );
  let err = dx - dy;
  let line = []; // array of points
  
  while( true )
  {
    line.push( new Point( p.x, p.y ) );
    if( p.x === to.x && p.y === to.y )
      break;

    const e2 = 2 * err;
    if( e2 > -dy ) { err -= dy; p.x += sx; }
    if( e2 <  dx ) { err += dx; p.y += sy; }
  }

  return( Array.from( line ) );
}


// Grabbed from  https://algodaily.com/lessons/an-illustrated-guide-to-dijkstras-algorithm/javascript
const graph =
{
  a : { b : 5, c : 2 },
  b : { a : 5, c : 7, d : 8 },
  c : { a : 2, b : 7, d : 4, e : 8 },
  d : { b : 8, c : 4, e : 6, f : 4 },
  e : { c : 8, d : 6, f : 3 },
  f : { e : 3, d : 4 },
};

function printTable( table )
{
  return Object.keys( table ).map( ( vertex ) => {
      var { vertex: from, cost } = table[ vertex ];
      return `${ vertex } : ${ cost } via ${ from }`;
    })
    .join( "\n" );
};

function tracePath( table, start, end )
{
  var path = [];
  var next = end;
  while( true )
  {
    path.unshift( next );
    if( next === start )
      break;
    
    next = table[ next ].vertex;
  }

  return path;
};

function formatGraph( g )
{
  const tmp = {};
  Object.keys( g ).forEach( ( k ) =>
  {
    const obj = g[ k ];
    const arr = [];
    Object.keys( obj ).forEach( ( v ) => arr.push( { vertex: v, cost: obj[v] } ) );
    tmp[ k ] = arr;
  });
  return tmp;
};

function dijkstra( graph, start, end )
{
  var map = formatGraph( graph );
  var visited = [];
  var unvisited = [ start ];
  var shortestDistances = { [ start ]: { vertex : start, cost : 0 } };

  var vertex;
  while( ( vertex = unvisited.shift() ) )
  {
    // Explore unvisited neighbors
    var neighbors = map[ vertex ].filter( ( n ) => !visited.includes( n.vertex ) );

    // Add neighbors to the unvisited list
    unvisited.push( ...neighbors.map( ( n ) => n.vertex ) );

    var costToVertex = shortestDistances[ vertex ].cost;

    for( let { vertex: to, cost } of neighbors )
    {
      var currCostToNeighbor = shortestDistances[ to ] && shortestDistances[ to ].cost;
      var newCostToNeighbor = costToVertex + cost;
      if ( currCostToNeighbor == undefined || newCostToNeighbor < currCostToNeighbor )
        shortestDistances[ to ] = { vertex, cost : newCostToNeighbor };
    }

    visited.push( vertex );
  }

  console.log( "Table of costs:" );
  console.log( printTable( shortestDistances ) );

  const path = tracePath( shortestDistances, start, end );

  console.log( "Shortest path is: ", path.join(" -> "), " with weight ", shortestDistances[ end ].cost );
};

export function doSPF()
{
  dijkstra( graph, "a", "f" );
}