import { c } from './Constants.js';
import { Point } from './Utils.js'

export class Party
{
  constructor( worldPos )
  {
    this.location = undefined;
    this.worldPos = worldPos;
    this.localPos = new Point( 0, 0 );
  }

}