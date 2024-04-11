window.onload = mapGenInit;

let canvas;
let ctx;
let mapImage = new Image();
let tileImage = new Image();
let mapzoom = 1;
let tilezoom = 1;
let tilewidth = 32;
let mapEdited = false;

let MAP_WIDTH = 512;
let MAP_HEIGHT = 512;
let TILE_WIDTH = 512;
let TILE_HEIGHT = 512;

let mapOffsetX = 256; // screen coordinates.
let mapOffsetY = 256;

function mapGenInit()
{
  canvas = document.getElementById( "myCanvas" );
  ctx = canvas.getContext( "2d" );
  ctx.canvas.width = 1024;
  ctx.canvas.height = 512;
  
  document.getElementById( 'openMapAction' ).addEventListener( 'change', openMapFile, false );
  document.getElementById( 'openTilesAction' ).addEventListener( 'change', openTileFile, false );
  document.getElementById( 'openMappingsAction' ).addEventListener( 'change', openMappingsFile, false );
  
  mapzoom = 2;
  tilezoom = 1;
  tilewidth = 32;
  mapEditedFlag = false;

  document.addEventListener( "keydown", keyDownHandler, false );
  mapImage.addEventListener('load', drawScreen );
  tileImage.addEventListener('load', drawScreen );

}

function drawScreen()
{
  ctx.fillStyle = "gray";
  ctx.fillRect( 0, 0, 1024, 512 ); // this will be the UI's canvas

  // pixels in (mapImage pixels) above, below, left, right of point to show
  // fewer points if zoomed.
  // if zoom is 1, we want 1/2 of mapImage.with, so clicking in the center will show the whole thing
  // if zoom is 2 we want 1/4, etc.
  let zoomDistance = mapImage.width * .5 / mapzoom;

  // draw entire map.
  ctx.drawImage( mapImage, 0, 0, 512, 512 );

  ctx.strokeStyle = "black";
  ctx.lineWidth = 2;
  
  // indicate zoomed portion
  // convert zoomDistance from mapImage pixels to screen pixels. We show the map in a 512x512 grid.
  let screenZoomDist = zoomDistance * 512 / mapImage.width;
  let rightEdge = mapOffsetX + screenZoomDist;
  let boxWidth = screenZoomDist * 2;
  // ( mapOffsetX - zoomDistance ) + boxWidth = 512
  if( rightEdge > 512 )
    boxWidth = 512 - ( mapOffsetX - screenZoomDist );
  ctx.rect( mapOffsetX - screenZoomDist, mapOffsetY - screenZoomDist, boxWidth, screenZoomDist * 2 ) ;

  ctx.stroke();

  // Show the zoomed portion of the map on the right

  // mapOffset are in screen coordinats, scale to mapImage coordinats
  let mapX = mapOffsetX * mapImage.width / 512;
  let mapY = mapOffsetY * mapImage.width / 512;
 
  ctx.drawImage( mapImage, mapX - zoomDistance, mapY - zoomDistance, zoomDistance * 2, zoomDistance * 2,
                           512, 0, 256, 256 );

  // Separator
  ctx.beginPath();
  ctx.moveTo( 512, 0 );
  ctx.lineTo( 512, 512 );
  ctx.stroke();
}

function loaded() { console.log( "Loaded" ); }

function keyDownHandler( param )
{
  const pointOffset = 100/mapzoom;

  switch( param.key )
  {
    case "ArrowLeft":
      mapOffsetX -= pointOffset;
      break;
    case "ArrowRight":
      mapOffsetX += pointOffset;
      break;
    case "ArrowUp":
      mapOffsetY -= pointOffset;
      break;
    case "ArrowDown":
      mapOffsetY += pointOffset;
      break;
    case 'm':
      openMapClick()
      break;
    case 't':
      openTilesClick()
      break;
    case '1': mapzoom = 2; break;
    case '2': mapzoom = 4; break;
    case '3': mapzoom = 8; break;
    case '4': mapzoom = 16; break;
    case '5': mapzoom = 32; break;
  }
  if( mapOffsetX < 0 )
    mapOffsetX = 0;
  if( mapOffsetX > 512)
    mapOffsetX = 512;
  if( mapOffsetY < 0 )
    mapOffsetY = 0;
  if( mapOffsetY > 512)
    mapOffsetY = 512;

  drawScreen();
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

function openMappingsClick() { document.getElementById( 'openMappingsClick' ).click(); }

function openMappingsFile( e )
{
  var file = e.target.files[ 0 ];
  if( !file )
    return;
}

function generateTMX() { }

function mapClick( event )
{
  var elem = document.getElementById( 'mapimage' );
  mapOffsetX = event.offsetX;
  mapOffsetY = event.offsetY;
  if( mapOffsetX > 512 )
    mapOffsetX = 512;
  if( mapOffsetY > 512 )
    mapOffsetY = 512;
  drawScreen();
}


/*
<section>
<div id='menupane' class='css_menu_pane'>
<input type='file' class='css_menuButton' id='openMapAction' style='display:none'>
<button class='css_menuButton' id='openMapButton'       onclick='openMapClick();'>Open Map Image</button>
<input type='file' class='css_menuButton' id='openTilesAction' style='display:none'>
<button class='css_menuButton' id='openTilesButton'     onclick='openTilesClick();'>Open Tiles</button>
<input type='file' class='css_menuButton' id='openMappingsAction' style='display:none'>
<button class='css_menuButton' id='openTileMappings'    onclick='openMappingsClick();'>Open Color-Tile Mappings</button>
<button class='css_menuButton' id='genTMXButton'        onclick='generateTMX();'>Generate</button>
</div>
</section>
*/