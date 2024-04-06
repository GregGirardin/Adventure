import { gManager } from './main.js';

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

// in map, can an observer at observerPos see the thing at destinationPos?
export function positionIsVisible( map, observerPos, destinationPos )
{
  return true;
}