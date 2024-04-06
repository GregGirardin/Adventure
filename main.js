import { c } from './Constants.js';
import { Party } from './Party.js';
import { Point, positionIsOnMap, positionIsVisible } from './Utils.js'
// import worldMap from '/maps/world.json' with { type: 'json' };

export let gManager; // a single global instance. Everything uses this.
export let gDebugFlag = true; // console log debug stuff.

window.onload = gameInit;

class gameManager
{
  constructor()
  {
    this.canvas = document.getElementById( "myCanvas" );
    this.ctx = this.canvas.getContext( "2d" );

    this.canvas.width = c.SCREEN_WIDTH; // widen to check that we're not drawing far off screen
    this.canvas.height = c.SCREEN_HEIGHT;
    this.worldMap = undefined;
    this.messages = []; // status messages

    this.party = new Party( new Point( 16, 16 ) );

    this.objects = [];

    fetch( './maps/world.json' ).then( ( response ) => response.json() ).then( ( json ) =>
    {
      this.worldMap = json;
      this.processMap( this.worldMap ); // unzip and fetch tile maps.
    } );

    this.objects = [];
  }

   /*
    inflate the compressed map layers[].data
    Fetch the tile images and add them to the tilesets as a 'graphic' property.
   */
  processMap( map )
  {
    let index;

    // get the sprite map
    for( index = 0;index < map.tilesets.length;index++ )
    {
      map.tilesets[ index ].graphic = new Image();
      map.tilesets[ index ].graphic.src  = "./maps/" + map.tilesets[ index ].image;
    }

    // decompress the layers
    for( index = 0;index < map.layers.length;index++ )
    {
      let b64data = map.layers[ index ].data;
      let strData = atob( b64data );
      let charData = strData.split( '' ).map( function( x ){ return x.charCodeAt( 0 ); } );
      var binData = new Uint8Array( charData );
      var data = pako.inflate( binData ); // every grid ends up in 4 array entries, little endien? so grab the first.

      let gridSize = map.layers[ index ].width * map.layers[ index ].height;
      let mapData = [];
      for( let i = 0;i < gridSize;i++ )
        mapData[ i ] = data[ i * 4 ]; // TBD: is this limited to an 8 bit value?

      map.layers[ index ].data = mapData; // overwrite data with uncompressed data.
    }
  }

  addObj( obj )
  {
    this.objects.push( obj );
  }

  logMessage( message ) 
  {
    this.messages.push( message ); // newest at the end of array
    if( this.messages.length > c.NUM_MESSAGES )
      this.messages.shift();
  }

  keyDownHandler( param )
  {
    // handle movement
    let party_x = this.party.worldPos.x;
    let party_y = this.party.worldPos.y;
    let moved = true;

    let message = "Pass";
    
    switch( param.key )
    {
      case "ArrowLeft":
        message = "West";
        party_x--;
        break;
      case "ArrowRight":  
        message = "East";
        party_x++;
        break;
      case "ArrowUp":
        message = "North";
        party_y--;
        break;
      case "ArrowDown": 
        message = "South";
        party_y++;
        break;
      default:
        moved = false;
    }
    // check if we can go to the new position
    if( moved )
    {

      const passable = [ c.TID_GRASS1, c.TID_GRASS2, c.TID_FOREST1, c.TID_FOREST2, c.TID_HILLS ]; // all tile ids we can pass though
      let newTileId  = this.worldMap.layers[ 0 ].data[ party_y * this.worldMap.layers[ 0 ].width + party_x ];
      if( passable.includes( newTileId ) )
      {
        this.party.worldPos.x = party_x;
        this.party.worldPos.y = party_y;
        this.logMessage( message );
      }
      else
      {
        this.logMessage( message + " Impassable!" );
      }

    }

  }

  update()
  {
  }


  getPositionInfo( map, x, y ) { }

  draw()
  {
    var obj;
    if( !this.worldMap )
      return;

    this.ctx.clearRect( 0, 0, c.SCREEN_WIDTH, c.SCREEN_HEIGHT );

    let img = this.worldMap.tilesets[ 0 ].graphic;
    // display our section of the map
    const DISP_RADIUS = 5; // how many grid points away from the party, up-d-l-r, to display
    const SPRITE_PIXELS = 32; // sides of a sprite both in the spritemap (tilewidth) and on screen.
    const spriteMapCols = this.worldMap.tilesets[ 0 ].columns;
    const tileWidth = this.worldMap.tilesets[ 0 ].tilewidth;
    const tileHeight = this.worldMap.tilesets[ 0 ].tileheight;

    for( let y = -DISP_RADIUS;y <= DISP_RADIUS;y++ )
      for( let x = -DISP_RADIUS;x <= DISP_RADIUS;x++ )
      {
        let mapx = this.party.worldPos.x + x;
        let mapy = this.party.worldPos.y + y;

        // determine if this grid position is visible from the party at 0,0.
        if( !positionIsVisible( this.worldMap, this.party.worldPos, new Point( mapx, mapy ) ) )
          continue;

        let tileId = 1; // use water by default

        if( ( x == 0 ) && ( y == 0 ) )
          tileId = 329; // icon for the party
        else if( positionIsOnMap( this.worldMap, mapx, mapy ) )
          tileId = this.worldMap.layers[ 0 ].data[ mapy * this.worldMap.layers[ 0 ].width + mapx ];

        let sourceX = ( ( tileId - 1 ) % spriteMapCols ) * tileWidth;
        let sourceY = Math.floor( ( tileId - 1 ) / spriteMapCols ) * tileHeight;
        let screenX = SPRITE_PIXELS * DISP_RADIUS + x * SPRITE_PIXELS;
        let screenY = SPRITE_PIXELS * DISP_RADIUS + y * SPRITE_PIXELS;

        this.ctx.drawImage( img,
                            sourceX, sourceY,
                            this.worldMap.layers[ 0 ].width, this.worldMap.layers[ 0 ].height,
                            screenX, screenY,
                            SPRITE_PIXELS, SPRITE_PIXELS );

        }

    // display messages
    let index = 0;
    this.ctx.font = "20px Arial";
    const textYPos = ( DISP_RADIUS * 2 + 2 ) * SPRITE_PIXELS;

    for( index = 0;index < this.messages.length;index++ )
      this.ctx.fillText( "> " + this.messages[ index ], 10, textYPos + index * 20 );

    for( obj of this.objects )
      obj.draw();
  }

  loop( delta ) // The game loop
  {
    this.update();
    this.draw();
  }
}

let lastTimestamp = 0;
function gameLoop( timeStamp )
{
  if( !lastTimestamp )
    lastTimestamp = timeStamp;

  var delta = timeStamp - lastTimestamp;
  lastTimestamp = timeStamp;
  gManager.loop( delta );
  sleep( 50 ).then(() => { window.requestAnimationFrame( gameLoop ); } );
}

function keyDownHandler( e ) { gManager.keyDownHandler( e ); }
// function keyUpHandler( e ) { gManager.keyUpHandler( e ); }

function gameInit()
{
  gManager = new gameManager();

  document.addEventListener( "keydown", keyDownHandler, false );
  // document.addEventListener( "keyup", keyUpHandler, false );

  window.requestAnimationFrame( gameLoop );
}

function sleep( ms ) { return new Promise( resolve => setTimeout( resolve, ms ) ); }
