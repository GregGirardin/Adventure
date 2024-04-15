import { c } from './constants.js';
import { Party } from './party.js';
import { NPC } from './npc.js';
import { getActiveLayerByType, getGroupIdByName, getObjAtPostion, Point, positionIsOnMap, generateVisibilityMap, mapWrap } from './Utils.js'

export let gManager; // a single global instance. Everything uses this.

window.onload = gameInit;

class gameManager
{
  constructor()
  {
    this.canvas = document.getElementById( "myCanvas" );
    this.ctx = this.canvas.getContext( "2d" );
  
    this.canvas.width = c.SCREEN_WIDTH; // widen to check that we're not drawing far off screen
    this.canvas.height = c.SCREEN_HEIGHT;
    this.messages = []; // status messages
    this.mapStack = []; // nested stack of maps. 0 is the world, 1 is the town, 2 within the town, etc. you're active in the deepest one

    this.submap = []; // tile IDs that let you enter something
    this.landpassable = []; // all tile ids we can move over
    this.opaque = []; // tiles we can't see through
    this.levelchange = []; // ladders or things that take us to different layers (groups) of this map

    this.debugFlag = false;
    this.getMap( 'World', true );
    this.waterOff = 0; // use a vertical offset to animate water
    this.navMode = c.NAV_WORLD;
  }

  getMap( name, getTileSet = false )
  {
    fetch( './maps/' + name + '.json' ).then( ( response ) => response.json() ).then( ( json ) =>
    {
      let newMap = json;
      this.mapStack.push( newMap );
      this.processMap( newMap, getTileSet ); // unzip and fetch tile maps.
    } );
  }

   /*
    inflate the compressed map layers[].data
    Fetch the tile images and add them to the tilesets as a 'graphic' property.
   */
  processMap( map, getTileSet = false )
  {
    let index;

    if( getTileSet ) // get the sprite map only for the world map. We use that tileset for everything.
      for( index = 0;index < map.tilesets.length;index++ )
      {
        // Future: if we want each map to use it's own tileset, put the spirtemap in the map
        // For a single tilemap game just load it once.
        // map.tilesets[ index ].graphic = new Image();
        // map.tilesets[ index ].graphic.src  = "./maps/" + map.tilesets[ index ].image;

        // For now, only a single tileset we load once.
        gManager.graphic = new Image();
        gManager.graphic.src  = "./maps/" + map.tilesets[ index ].image;

        // go through the properties of all the tiles
       
        for( let tile of map.tilesets[ index ].tiles )
          for( let property of tile.properties )
          {
            let tid = tile.id + 1; // Tile ID are base 0 in the properties, but base 1 in the map
            switch( property.name )
            {
              case "landpassable":
                if( property.value == true )
                  gManager.landpassable.push( tid );
                break;

              case "opaque":
                if( property.value == true )
                  gManager.opaque.push( tid );
                break;

              case "submap":
                if( property.value == true )
                  gManager.submap.push( tid );
                break;

              case "levelchange":
                if( property.value == true )
                  gManager.levelchange.push( tid );
                break;
            }
          }
      }

    // Each map layer is a group (in Tiled) containing a tile layer and an objectgroup layer.
    for( let group of map.layers )
    {
      group.NPCs = []; // NPCs active in this layer. Some are spawned immediatly, some intermittently.
      group.OBJs = []; // dyanmic objects in this layer.. 
      for( let layer of group.layers )
      {
        if( layer.type == "tilelayer" )
        { // decompress
          let b64data = layer.data;
          let strData = atob( b64data );
          let charData = strData.split( '' ).map( function( x ){ return x.charCodeAt( 0 ); } );
          var binData = new Uint8Array( charData );
          var data = pako.inflate( binData ); // every grid ends up in 4 array entries, little endien? so grab the first.

          let gridSize = map.width * map.height;
          let mapData = [];
          for( let i = 0;i < gridSize;i++ )
            mapData[ i ] = data[ i * 4 ] + data[ i * 4 + 1 ] * 256;

          layer.data = mapData; // overwrite data with uncompressed data.
        }
        else if( layer.type == "objectgroup" )
          for( let obj of layer.objects )
          {
            // change the x,y coordiantes of the objects from pixels to grid since that what we use.
            obj.x = Math.floor( obj.x / 32 );
            obj.y = Math.floor( obj.y / 32 );
            // note that the property is 'type' but it's called 'class' in Tiled
            if( obj.type == "spawn" )
              switch( obj.name )
              {
                case "party":
                  map.partyPos = new Point( obj.x, obj.y );
                  map.activeGroupId = group.id;
                  break;
                case "NPC":
                  // spawn map's initial NPCs.
                  group.NPCs.push( new NPC( obj.NPCclass, new Point( obj.x, obj.y )  ) );
                  break;
              }
          }
      }
    }

    for( let prop of map.properties )
    {
      if( prop.name == 'NavWorld' )
        if( prop.value == true )
          this.navMode = c.NAV_WORLD;
        else
          this.navMode = c.NAV_STATIC;
    }
  }

  logMessage( message ) 
  {
    this.messages.push( message ); // newest at the end of array
    if( this.messages.length > c.NUM_MESSAGES )
      this.messages.shift();
  }

  goUpMap()
  {
    if( this.mapStack.length > 1 )
    {
      this.logMessage( "Exiting" );
      this.mapStack.pop();

      let map = this.mapStack[ this.mapStack.length - 1 ];
      for( let prop of map.properties )
      {
        if( prop.name == 'NavWorld' )
          if( prop.value == true )
            this.navMode = c.NAV_WORLD;
          else
            this.navMode = c.NAV_STATIC;
      }
    }
    else
    {
      console.log( "Can't exit World Map." );
    }
  }

  keyDownHandler( param )
  {
    // handle movement
    let curMap = this.mapStack[ this.mapStack.length - 1 ];

    let tLayer = getActiveLayerByType( curMap, "tilelayer" ); 

    let partyPos = new Point( curMap.partyPos.x, curMap.partyPos.y );
    let moved = true;

    let message = "Pass";

    switch( param.key )
    {
      case "ArrowLeft":   message = "West";   partyPos.x--; break;
      case "ArrowRight":  message = "East";   partyPos.x++; break;
      case "ArrowUp":     message = "North";  partyPos.y--; break;
      case "ArrowDown":   message = "South";  partyPos.y++; break;
      default:
        moved = false;
    }

    // check if we can move to the new position
    if( moved )
    {
      if( !positionIsOnMap( curMap, partyPos.x, partyPos.y ) )
      {
        // if this is world, wrap. Else exit to the containing map.
        this.goUpMap();
        return;
      }

      let p = mapWrap( curMap, partyPos );
      let newTileId = tLayer.data[ p.y * curMap.width + p.x ];
      let objLayer = getActiveLayerByType( curMap, "objectgroup" );
      let objInfo = getObjAtPostion( objLayer.objects, partyPos ); // get any object info that might be there.

      if( this.submap.includes( newTileId ) ) // this tile indicates something we enter. Town, castle, etc.
      {
        curMap.partyPos = partyPos;

        let destName = objInfo.name; // name is the new map name.
        if( destName ) // there should be an object at that position indicating where it leads
        {
          this.logMessage( "Entering..." + destName );
          this.getMap( destName );
        }
      }
      else if( this.levelchange.includes( newTileId ) ) // Changing layers in map. Ladders, staircases, etc
      {
        curMap.partyPos = partyPos;

        // party x,y doesn't change. We're going to a new layer
        let newLayer = getGroupIdByName( curMap, objInfo.name );
        if( newLayer )
          curMap.activeGroupId = getGroupIdByName( curMap, objInfo.name );
        else
          this.logMessage( " Can't find level " + objInfo.name );
      }
      else
      {
        if( this.landpassable.includes( newTileId ) )
          curMap.partyPos = partyPos;
        else
          message += " - Impassable!";

        this.logMessage( message );
      }
    }
    else
    {
      switch( param.key )
      {
        case "d":
          //this.debugFlag = !this.debugFlag;
          this.getMap( "smap_grass" );
          /*
          if( this.debugFlag )
            this.logMessage( "Debug" );
          else
            this.logMessage( "Debug Off" );
          */
          break;
      }
    }
  }

  update()
  {
  }

  draw()
  {
    let curMap = this.mapStack[ this.mapStack.length - 1 ]; // outermost map

    if( !curMap )
      return;

    let tileLayer = getActiveLayerByType( curMap, "tilelayer" );
      
    this.ctx.fillStyle = "black";
    this.ctx.fillRect( 0, 0, c.SCREEN_WIDTH, c.SCREEN_HEIGHT );

    // display our section of the map
    const SPRITE_PIXELS = 32; // sides of a sprite both in the spritemap (tilewidth) and on screen.
    const spriteMapCols = 32;

    if( this.navMode == c.NAV_WORLD )
    {
      let visibility = generateVisibilityMap( curMap, c.DISP_RADIUS, curMap.partyPos );

      for( let y = -c.DISP_RADIUS;y <= c.DISP_RADIUS;y++ )
        for( let x = -c.DISP_RADIUS;x <= c.DISP_RADIUS;x++ )
        {
          let p = new Point( curMap.partyPos.x + x, curMap.partyPos.y + y );

          p = mapWrap( curMap, p );

          // determine if this grid position is visible from the party at 0,0.
          if( !visibility[ [ x, y ] ] )
            continue;

          let tileId = 1; // use water by default

          if( ( x == 0 ) && ( y == 0 ) )
            tileId = 329; // icon for the party
          else if( positionIsOnMap( curMap, p.x, p.y ) )
            tileId = tileLayer.data[ p.y * curMap.width + p.x ];

          let tileVoff = 0;
          if( ( tileId == 1 ) || ( tileId == 2 ) ) // water tiles
            tileVoff = this.waterOff;

          let sourceX = ( ( tileId - 1 ) % spriteMapCols ) * SPRITE_PIXELS;
          let sourceY = Math.floor( ( tileId - 1 ) / spriteMapCols ) * SPRITE_PIXELS + tileVoff;
          let screenX = SPRITE_PIXELS * c.DISP_RADIUS + x * SPRITE_PIXELS;
          let screenY = SPRITE_PIXELS * c.DISP_RADIUS + y * SPRITE_PIXELS;

          // Entire game uses one sprite map graphic
          this.ctx.drawImage( gManager.graphic, sourceX, sourceY, SPRITE_PIXELS, SPRITE_PIXELS,
                              screenX, screenY, SPRITE_PIXELS, SPRITE_PIXELS );
        }
      
      // NPCs

    }
    else // NAV_STATIC
    {
      for( let y = 0;y <= 2 * c.DISP_RADIUS;y++ )
        for( let x = 0;x <= 2 * c.DISP_RADIUS;x++ )
        {
          let tileId = 1;
          if( ( x == curMap.partyPos.x ) && ( y == curMap.partyPos.y ) )
            tileId = 329; // icon for the party
          else
            tileId = tileLayer.data[ y * curMap.width + x ];

          let tileVoff = 0;
          if( ( tileId == 1 ) || ( tileId == 2 ) ) // water tiles
            tileVoff = this.waterOff;

          let sourceX = ( ( tileId - 1 ) % spriteMapCols ) * SPRITE_PIXELS;
          let sourceY = Math.floor( ( tileId - 1 ) / spriteMapCols ) * SPRITE_PIXELS + tileVoff;

          this.ctx.drawImage( gManager.graphic, sourceX, sourceY,
                              SPRITE_PIXELS, SPRITE_PIXELS, x * SPRITE_PIXELS, y * SPRITE_PIXELS,
                              SPRITE_PIXELS, SPRITE_PIXELS );
        }
      }

    // borders
    this.ctx.fillStyle = "gray";
    this.ctx.fillRect( ( c.DISP_RADIUS * 2 + 1 ) * SPRITE_PIXELS, 0, 10, c.SCREEN_HEIGHT );
    this.ctx.fillRect( 0, ( c.DISP_RADIUS * 2 + 1 ) * SPRITE_PIXELS, c.SCREEN_WIDTH, 10 );

    // display messages
    this.ctx.fillStyle = "white";
    this.ctx.font = "20px Arial";
    const textYPos = ( c.DISP_RADIUS * 2 + 2 ) * SPRITE_PIXELS;

    for( let index = 0;index < this.messages.length;index++ )
      this.ctx.fillText( "> " + this.messages[ index ], 10, textYPos + index * 20 );

    // display party
  
    // display inventory

  }

  loop( delta ) // The game loop
  {
    this.waterOff--;
    if( this.waterOff < 0)
      this.waterOff = 32;

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
  sleep( 200 ).then(() => { window.requestAnimationFrame( gameLoop ); } );
}

function keyDownHandler( e ) { gManager.keyDownHandler( e ); }

function gameInit()
{
  gManager = new gameManager();

  document.addEventListener( "keydown", keyDownHandler, false );

  window.requestAnimationFrame( gameLoop );
}

function sleep( ms ) { return new Promise( resolve => setTimeout( resolve, ms ) ); }
