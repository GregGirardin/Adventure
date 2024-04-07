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

export function positionIsOnMap( map, x, y )
{
  if( ( y < 0 ) || ( y > map.layers[ 0 ].height ) ||
      ( x < 0 ) || ( x > map.layers[ 0 ].width ) )
     return false;
  return true;
}

// in map, can an observer at Point observerPos see the thing at Point destinationPos?
export function positionIsVisible( map, observerPos, destinationPos )
{
  return true;
}

/*
Generate a 2d array of which positions are visible
*/
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
      visibility[ [ x, y ] ] = true; // use array as object key, TBD: much slower than a 2D array?

  const opaque = [ c.TID_FOREST1, c.TID_FOREST2 ];
  // now trace allong each radial line from inside out, once you hit something opaque the rest of the line
  // is shadowed.
  for( let l of radialLines )
  {
    let visible = true;
    for( let p of l ) // for the points in the line
    {
      if( !visible )
        visibility[ [ p.x, p.y ] ] = false;
      if( visible )
      {
        let mapx = observerPos.x + p.x;
        let mapy = observerPos.y + p.y;
        if( positionIsOnMap( map, mapx, mapy ) )
        {
          let tileId = map.layers[ map.terrainLayer ].data[ mapy * map.layers[ map.terrainLayer ].width + mapx ];
          if( opaque.includes( tileId ) )
            visible = false;
        }
        else
          visible = false;
      }
    }
  }
  return( visibility );
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