window.onload = mapGenInit;

let canvas;
let ctx;
let mapImage = new Image();
let tileImage = new Image();
let mapzoom = 1;

let MAP_WIDTH = 512;
let MAP_HEIGHT = 512;
let TILE_WIDTH = 512;
let TILE_HEIGHT = 512;

let tiles_per_row = 32;
let tileEdge = 32; // Assume square

let mapOffsetX = 256; // screen coordinates.
let mapOffsetY = 256;
let tileOffsetX = 0;
let tileOffsetY = 0;
let activeTile = undefined;
let tileMappings = {}; // RBG:TID
let tiles = [];

const TOLERANCE_STRICT = 1; // color must be exact match to tile
const TOLERANCE_MED = 2; // close match
const TOLERANCE_LOOSE = 3; // lose match

let mapping_tolerance = TOLERANCE_STRICT;

function mapGenInit()
{
  canvas = document.getElementById( "myCanvas" );
  ctx = canvas.getContext( "2d" );
  ctx.canvas.width = 1024;
  ctx.canvas.height = 1024;
  
  document.getElementById( 'openMapAction' ).addEventListener( 'change', openMapFile, false );
  document.getElementById( 'openTilesAction' ).addEventListener( 'change', openTileFile, false );
  document.getElementById( 'openMappingsAction' ).addEventListener( 'change', openMappingsFile, false );
  
  document.addEventListener( "keydown", keyDownHandler, false );
  mapImage.addEventListener('load', drawScreen );
  tileImage.addEventListener('load', tilesLoaded );
}

function tilesLoaded()
{
  tiles_per_row = tileImage.width / tileEdge;
  drawScreen();
}

function drawScreen()
{
  ctx.fillStyle = "black";
  ctx.fillRect( 0, 0, 1024 + 512, 1024 ); // this will be the UI's canvas

  // pixels in (mapImage pixels) above, below, left, right of point to show
  // fewer points if zoomed.
  // if zoom is 1, we want 1/2 of mapImage.with, so clicking in the center will show the whole thing
  // if zoom is 2 we want 1/4, etc.
  let zoomDistance = mapImage.width * .5 / mapzoom;

  // Show the zoomed portion of the map on the right

  // mapOffset are in screen coordinates, scale to mapImage coordinats
  let mapX = mapOffsetX * mapImage.width / 512;
  let mapY = mapOffsetY * mapImage.height / 512;
  ctx.drawImage( mapImage, mapX - zoomDistance, mapY - zoomDistance, zoomDistance * 2, zoomDistance * 2, 0, 0, 512, 512 );
  ctx.drawImage( tileImage, tileOffsetX, tileOffsetY, 512, 512, 512, 0, 512, 512 );

  // Separator
  ctx.strokeStyle = "white";
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo( 512, 0 );
  ctx.lineTo( 512, 512 );
  ctx.moveTo( 0, 512 );
  ctx.lineTo( 1024, 512 );
  ctx.stroke();

  if( activeTile) 
    if( activeTile.tid )
    {
      ctx.font = "22px Georgia";
      ctx.fillStyle = "white";

      ctx.fillText( "Active Tile:" + activeTile.tid.toString(), 10, 530 );
      ctx.drawImage( tileImage, activeTile.tileOffsetX, activeTile.tileOffsetY, tileEdge, tileEdge,
                    10, 550, tileEdge * 2, tileEdge * 2 );
      
      tileEditX = 10;

      for( key in activeTile.colors )
      {
        let obj = activeTile.colors[ key ];
        let fill = "#" + obj.r.toString( 16 ) + obj.g.toString( 16 ) + obj.b.toString( 16 );
        ctx.fillStyle = fill;

        ctx.fillRect( tileEditX, 700, 32, 32 ); // this will be the UI's canvas
        tileEditX += 40;
      }
    }
}

function keyDownHandler( param )
{
  const pointOffset = 100 / mapzoom;

  switch( param.key )
  {
    case "Escape":
      activeTile = undefined; // delete any current entries.
      break;
    case "a": mapOffsetX -= pointOffset; break;
    case "d": mapOffsetX += pointOffset; break;
    case "w": mapOffsetY -= pointOffset; break;
    case "s": mapOffsetY += pointOffset; break;

    case "ArrowLeft":
      tileOffsetX -= 512;
      if( tileOffsetX < 0 )
        tileOffsetX = 0;
      break;
    case "ArrowRight":
      if( tileImage.width > tileOffsetX + 512 )
        tileOffsetX += 512;
      break;
    case "ArrowUp":
      tileOffsetY -= 512;
      if( tileOffsetY < 0 )
      tileOffsetY = 0;
      break;
    case "ArrowDown":
      if( tileImage.height > tileOffsetY + 512 )
        tileOffsetY += 512;
      break;

    case 'm': openMapClick(); break;
    case 't': openTilesClick(); break;
    case '1':
      if( mapzoom == 1 )
      { // center
        mapOffsetX = 256;
        mapOffsetY = 256;
      }
      else
        mapzoom = 1;
      break;
    case '2': mapzoom =  2; break;
    case '3': mapzoom =  4; break;
    case '4': mapzoom =  8; break;
    case '5': mapzoom = 16; break;
    case '6': mapzoom = 32; break;
    case '7': mapzoom = 64; break;
  }
  if( mapOffsetX < 0 )
    mapOffsetX = 0;
  if( mapOffsetX > 512 )
    mapOffsetX = 512;
  if( mapOffsetY < 0 )
    mapOffsetY = 0;
  if( mapOffsetY > 512 )
    mapOffsetY = 512;

  drawScreen();
}

function openMappingsClick() { document.getElementById( 'openMappingsAction' ).click(); }
function openMappingsFile( e )
{
  var file = e.target.files[ 0 ];
  if( !file )
    return;

  var reader = new FileReader();

  reader.onload = function( e )
  {
    tileMappings = JSON.parse(  e.target.result );
    drawScreen();
  }
  reader.readAsText(file);
}

function saveMappingsFile( )
{
  let mappingsFile = JSON.stringify( tileMappings );

  const a = document.createElement( 'a' );
  const file = new Blob( [ mappingsFile ], { type: 'text/plain' } );
  
  a.href = URL.createObjectURL( file );
  a.download = "mapping.json";
  a.click();

	URL.revokeObjectURL( a.href );
 }

function openMapClick() { document.getElementById( 'openMapAction' ).click(); }

function openMapFile( e )
{
  var file = e.target.files[ 0 ];
  if( !file )
    return;

  mapImage.src = file.name;
}

function openTilesClick() { document.getElementById( 'openTilesAction' ).click(); }

function openTileFile( e )
{
  var file = e.target.files[ 0 ];
  if( !file )
    return;

  tileImage.src = file.name;
}

class colorRange
{
  constructor( rgb, delta, tid )
  {
    this.rgb = rgb;
    this.r = rgb >> 16;
    this.g = (rgb >> 8) & 0xff;
    this.b = rgb & 0xff;
    this.tid = tid;

    this.rmin = this.r - delta;
    if( this.rmin < 0 )
      this.rmin = 0;
    this.gmin = this.g - delta;
    if( this.gmin < 0 )
      this.gmin = 0;
    this.bmin = this.b - delta;
    if( this.bmin < 0 )
      this.bmin = 0;

    this.rmax = this.r + delta;
    if( this.rmax > 0xff )
      this.rmax = 0xff;
    this.gmax = this.g + delta;
    if( this.gmax > 0xff )
      this.gmax = 0xff;
    this.bmax = this.b + delta;
    if( this.bmax > 0xff )
      this.bmax = 0xff;
  }

  match( r, g, b )
  {
    if( r < this.rmin || r > this.rmax )
      return false;
    if( g < this.gmin || g > this.gmax )
      return false;
    if( b < this.bmin || b > this.bmax )
      return false;
    return true;
  }
}

function generateTMX()
{
  console.log( "generateTMX" );
  if( !mapImage.width || !tileImage.width )
    return;

  const w = mapImage.width;
  const h = mapImage.height

  let tmpCanvas = document.createElement('canvas');
  tmpCanvas.width = w;
  tmpCanvas.height = h;
  let tmpCtx = tmpCanvas.getContext( '2d' );
  tmpCtx.drawImage( mapImage, 0, 0, mapImage.width, mapImage.height );

  let color_range = undefined;
  // generate ranges 
  if( mapping_tolerance == TOLERANCE_MED )
    color_range = 8;
  else if( mapping_tolerance == TOLERANCE_LOOSE )
    color_range = 32;

  let rangeMappings = [];
  ctx.fillStyle = "black";

  if( color_range )
    for( [ key, value ] of Object.entries( tileMappings ) )
      rangeMappings.push( new colorRange( key, color_range, value ) );

  let tidMappingArray = new Array( w * h );
  let hits = 0;
  for( let y = 0;y < h;y++ )
  {
    for( let x = 0;x < w;x++ )
    {
      let pixel = tmpCtx.getImageData( x, y, 1, 1 );
      let pixelVal = new mapcolor( pixel.data[ 0 ], pixel.data[ 1 ], pixel.data[ 2 ] );
      // exact match?
      let val = tileMappings[ pixelVal.rgb ]
      if( val )
      {
        hits++;
        ctx.fillRect( x / 2, y / 2, 1, 1 );
        tidMappingArray[ y * h + x ] = val; // exact mapping
      }
      else
        for( e in rangeMappings )
          if( e.match( pixel.data[ 0 ], pixel.data[ 1 ], pixel.data[ 2 ] ) )
          {
            ctx.fillRect( x / 2, y / 2, 1, 1 );
            hits++;
            tidMappingArray[ y * h + x ] = e.tid; // exact mapping
            break;
          }
    }
  }

  console.log( "Hit Rate:", hits * 100 / ( w * h ) );
}

// copy activeTile.colors{} to tileMappings{}
function updateMappingDict()
{
  if( activeTile )
    for( [ key, value ] of Object.entries( activeTile.colors ) )
      tileMappings[ value.rgb ] = activeTile.tid;
}

class mapcolor
{
  constructor( r, g, b )
  {
    this.r = r;
    this.g = g;
    this.b = b;
    this.rgb = ( r << 16 ) + ( g << 8 ) + b;
  }
}

function mapClick( event )
{
  if( ( event.offsetX > 512 ) && ( event.offsetY < 512 ) ) // click in tiles area 
  {
    updateMappingDict();

    activeTile = {};
    activeTile.tid = ( tileOffsetY / tileEdge ) * tiles_per_row + Math.floor( event.offsetY / tileEdge ) * tiles_per_row +
                       tileOffsetX / tileEdge + Math.floor( ( event.offsetX - 512 ) / tileEdge ) + 1; // First tid is 1.
    activeTile.colors = {}; // colors that will be mapped to this tile. key:Val rgb:mapcolor

    // fill in any existing enteries from the tileMappings
    for( [ key, value ] of Object.entries( tileMappings ) )
    {
      if( value == activeTile.tid )
      {
        let r = ( key & 0xff0000 ) >> 16;
        let g = ( key & 0xff00 ) >> 8;
        let b = key & 0xff;
        let entry = new mapcolor( r, g, b );
        activeTile.colors[ entry.rgb ] = entry;
      }
    }

    activeTile.tileOffsetX = tileOffsetX + event.offsetX - 512;
    activeTile.tileOffsetX -= activeTile.tileOffsetX % tileEdge; // get to the top left pixel
    activeTile.tileOffsetY = tileOffsetY + event.offsetY;
    activeTile.tileOffsetY -= activeTile.tileOffsetY % tileEdge;
    // populate with any existing color mappings.
  }
  else if( ( event.offsetX < 512 ) && ( event.offsetY < 512 ) ) // map area, add this point to the activeTiles colors
  {
    if( activeTile )
    {
      let pixel = ctx.getImageData( event.offsetX, event.offsetY, 1, 1 );
      let pixelVal = new mapcolor( pixel.data[ 0 ], pixel.data[ 1 ], pixel.data[ 2 ] );
    
      activeTile.colors[ pixelVal.rgb ] = pixelVal; // key is RBG value, value is a full mapcolor instance
    }
  }
  else if( event.offsetY > 512 ) // in the tile color map. Delete the color we clicked
  {
    if( activeTile )
    {
      let pixel = ctx.getImageData( event.offsetX, event.offsetY, 1, 1 );
      let pixelVal = new mapcolor( pixel.data[ 0 ], pixel.data[ 1 ], pixel.data[ 2 ] );
      delete activeTile.colors[ pixelVal.rgb ];
      delete tileMappings[ pixelVal.rgb ]; // TBD.
    }
  }
  
  drawScreen();
}

// assume 16,32, or 64
function toggleTileWidth()
{
  tileEdge *= 2;
  if( tileEdge > 64 )
    tileEdge = 16;

  document.getElementById( 'tileWidthButton' ).innerHTML = tileWidth.toString();
  tiles_per_row = tileImage.width / tileEdge;
}

function toggleMappingTolerance()
{
  if( mapping_tolerance == TOLERANCE_LOOSE )
    mapping_tolerance = TOLERANCE_STRICT;
  else
    mapping_tolerance++;

  let str;
  switch( mapping_tolerance )
  {
    case TOLERANCE_STRICT: str = "Strict"; break;
    case TOLERANCE_MED: str = "Medium"; break;
    case TOLERANCE_LOOSE: str = "Loose"; break;
  }

  document.getElementById( 'toggleToleranceButton' ).innerHTML = str;
}