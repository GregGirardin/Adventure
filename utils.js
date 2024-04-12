import { c } from './constants.js';
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

export function positionIsOnMap( map, x, y )
{
  if( ( y < 0 ) || ( y >= map.height ) || ( x < 0 ) || ( x >= map.width ) )
     return false;
  return true;
}

// When we go to the edge of a map we wrap to see what's on the other side.
// Design maps accordingly.
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

    outsideEdges = outsideEdges.concat( getLine( new Point( -distance, -distance ), new Point( distance, -distance ) ) ); // Top edger
    outsideEdges = outsideEdges.concat( getLine( new Point( distance, -distance + 1 ), new Point( distance, distance ) ) ); // Right
    outsideEdges = outsideEdges.concat( getLine( new Point( -distance, -distance + 1 ), new Point( -distance, distance ) ) ); // Left
    outsideEdges = outsideEdges.concat( getLine( new Point( -distance + 1, distance ), new Point( distance - 1, distance ) ) ); // Bottom

    const c = new Point( 0, 0 );

    // craete array of lines from the center to the outside edges.
    for( let p of outsideEdges )
    {
      let l = getLine( c, p );
      // delete the first point of the line at (0, 0) where the party is
      l.shift();
      radialLines.push( l );
    }
  }

  let visibility = {}; // an object keyed by [screenX, screenY] where 'true' means the grid is visible.
  for( let x = -distance;x <= distance;x++ )
    for( let y = -distance;y <= distance;y++ )
      visibility[ [ x, y ] ] = false; // use array as object key, TBD: much slower than a 2D array?

  visibility[ [ 0, 0 ] ] = true;
  // now trace allong each radial line from inside out, once you hit something opaque the rest of the line is shadowed.
  let tileLayer = getActiveLayerByType( map, "tilelayer" );

  for( let l of radialLines )
  {
    let visible = true;
    for( let p of l ) // for the points in the line
    {
      if( visible )
        visibility[ [ p.x, p.y ] ] = true;
      if( visible )
      {
        let q = new Point( observerPos.x + p.x, observerPos.y + p.y );
        q = mapWrap( map, q );
        let tileId = tileLayer.data[ q.y * map.width + q.x ];
        if( gManager.opaque.includes( tileId ) )
          visible = false;
      }
    }
  }
  return( visibility );
}

// maps have an activeGroupId at the root
// in that group there is one tile layer and one object layer
export function getActiveLayerByType( map, type )
{
  for( let group of map.layers )
    if( group.id == map.activeGroupId )
    {
      for( let layer of group.layers )
        if( layer.type == type )
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

// Assume one object at a position for now.
export function getObjAtPostion( objects, pos )
{
  for( let obj of objects )
    if( ( obj.x == pos.x ) && ( obj.y == pos.y ) )
      return obj;

  return undefined;
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