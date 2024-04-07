import { c } from './Constants.js';
import { Party } from './Party.js';
import { getLine, Point, positionIsOnMap, positionIsVisible, generateVisibilityMap } from './Utils.js'
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
    this.terrainLayer = undefined;
    this.canvas.width = c.SCREEN_WIDTH; // widen to check that we're not drawing far off screen
    this.canvas.height = c.SCREEN_HEIGHT;
    this.messages = []; // status messages
    this.mapStack = []; // arry of maps. 0 is the world, 1 is the town, 2 within the town, etc.
                        // you're in the deepest one

    fetch( './maps/World.json' ).then( ( response ) => response.json() ).then( ( json ) =>
    {
      this.mapStack.push( json );
      this.processMap( this.mapStack[ 0 ] ); // unzip and fetch tile maps.
    } );

  }

   /*
    inflate the compressed map layers[].data
    Fetch the tile images and add them to the tilesets as a 'graphic' property.
   */
  processMap( map )
  {
    let index;

    map.objects = [];
    // get the sprite map
    for( index = 0;index < map.tilesets.length;index++ )
    {
      map.tilesets[ index ].graphic = new Image();
      map.tilesets[ index ].graphic.src  = "./maps/" + map.tilesets[ index ].image;
    }

    // decompress the Terrain layer
    for( index = 0;index < map.layers.length;index++ )
    {
      if( map.layers[ index ].name == "Terrain" )
      { // decompress
        map.terrainLayer = index;
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
      else if( map.layers[ index ].name == "Objects" )
      {
        // change the x,y coordiantes of the objects from pixels to grid
        for( let obj of map.layers[ index ].objects )
        {
          obj.x = Math.floor( obj.x / 32 );
          obj.y = Math.floor( obj.y / 32 );
          if( obj.name == "spawn" )
            map.partyPos = new Point( obj.x, obj.y );
          map.objects[ [ obj.x, obj.y ] ] = obj; // allow us to directly get the object if we have the x and y
                                                  // instead of iterating though array.
        }
      }
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
    let curMap = this.mapStack[ this.mapStack.length - 1 ];
    if( !curMap )
      return;

    let partyPos = new Point( curMap.partyPos.x, curMap.partyPos.y );
    let moved = true;

    let message = "Pass";
    
    switch( param.key )
    {
      case "ArrowLeft":
        message = "West";
        partyPos.x--;
        break;
      case "ArrowRight":  
        message = "East";
        partyPos.x++;
        break;
      case "ArrowUp":
        message = "North";
        partyPos.y--;
        break;
      case "ArrowDown": 
        message = "South";
        partyPos.y++;
        break;
      default:
        moved = false;
    }
    // check if we can go to the new position
    if( moved )
    {
      let newTileId  = curMap.layers[ curMap.terrainLayer ].data[ partyPos.y * curMap.layers[ curMap.terrainLayer ].width + partyPos.x ];

      const enterable = [ c.TID_VILLAGE, c.TID_TOWN, c.TID_CASTLE, c.TID_DUNGEON ];
      if( enterable.includes( newTileId ) )
      {
        curMap.partyPos = partyPos;
        this.logMessage( "Entering..." + curMap.objects[ [ partyPos.x, partyPos.y ] ].name );
      }
      else
      {
        const passable = [ c.TID_GRASS1, c.TID_GRASS2, c.TID_FOREST1, c.TID_FOREST2, c.TID_HILLS ]; // all tile ids we can pass though
        if( passable.includes( newTileId ) )
        {
          curMap.partyPos = partyPos;
          this.logMessage( message );
        }
        else
        {
          this.logMessage( message + " - Impassable!" );
        }
      }
    }

  }

  update()
  {
  }

  draw()
  {
    let curMap = this.mapStack[ this.mapStack.length - 1];

    if( !curMap )
      return;

    this.ctx.fillStyle = "black";
    this.ctx.fillRect( 0, 0, c.SCREEN_WIDTH, c.SCREEN_HEIGHT );

    let img = curMap.tilesets[ 0 ].graphic;
    // display our section of the map
    const DISP_RADIUS = 5; // how many grid points away from the party, up-d-l-r, to display
    const SPRITE_PIXELS = 32; // sides of a sprite both in the spritemap (tilewidth) and on screen.
    const spriteMapCols = curMap.tilesets[ 0 ].columns;
    const tileWidth = curMap.tilesets[ 0 ].tilewidth;
    const tileHeight = curMap.tilesets[ 0 ].tileheight;

    let visibility = generateVisibilityMap( curMap, DISP_RADIUS, curMap.partyPos );

    for( let y = -DISP_RADIUS;y <= DISP_RADIUS;y++ )
      for( let x = -DISP_RADIUS;x <= DISP_RADIUS;x++ )
      {
        let mapx = curMap.partyPos.x + x;
        let mapy = curMap.partyPos.y + y;

        // determine if this grid position is visible from the party at 0,0.
        if( !visibility[ [ x, y ] ] )
          continue;

        let tileId = 1; // use water by default

        if( ( x == 0 ) && ( y == 0 ) )
          tileId = 329; // icon for the party
        else if( positionIsOnMap( curMap, mapx, mapy ) )
          tileId = curMap.layers[ 0 ].data[ mapy * curMap.layers[ 0 ].width + mapx ];

        let sourceX = ( ( tileId - 1 ) % spriteMapCols ) * tileWidth;
        let sourceY = Math.floor( ( tileId - 1 ) / spriteMapCols ) * tileHeight;
        let screenX = SPRITE_PIXELS * DISP_RADIUS + x * SPRITE_PIXELS;
        let screenY = SPRITE_PIXELS * DISP_RADIUS + y * SPRITE_PIXELS;

        this.ctx.drawImage( img,
                            sourceX, sourceY,
                            curMap.layers[ 0 ].width, curMap.layers[ 0 ].height,
                            screenX, screenY,
                            SPRITE_PIXELS, SPRITE_PIXELS );
        }

    // borders
    this.ctx.fillStyle = "gray";
    this.ctx.fillRect(  ( DISP_RADIUS * 2 + 1 ) * SPRITE_PIXELS, 0, 10, c.SCREEN_HEIGHT );
    this.ctx.fillRect( 0, ( DISP_RADIUS * 2 + 1 ) * SPRITE_PIXELS, c.SCREEN_WIDTH, 10 );

    // display messages
    this.ctx.fillStyle = "white";
    this.ctx.font = "20px Arial";
    const textYPos = ( DISP_RADIUS * 2 + 2 ) * SPRITE_PIXELS;

    for( let index = 0;index < this.messages.length;index++ )
      this.ctx.fillText( "> " + this.messages[ index ], 10, textYPos + index * 20 );
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
  sleep( 100 ).then(() => { window.requestAnimationFrame( gameLoop ); } );
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
