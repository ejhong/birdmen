import {readWaterState,classifyElevation,decodeGrid} from './submerged-model.mjs';
const $=s=>document.querySelector(s);
let manifest,state,current,loadVersion=0;
const cache=new Map();
const locations=[...document.querySelectorAll('[data-project-lat]')].map(link=>({
  link,lat:+link.dataset.projectLat,lon:+link.dataset.projectLon,number:link.dataset.projectNumber
}));
const inGrid=(p,g)=>p.lon>=g.west&&p.lon<=g.east&&p.lat>=g.south&&p.lat<=g.north;
const coordinate=(n,positive,negative)=>`${Math.abs(n).toFixed(1)}°${n<0?negative:positive}`;
function paint(canvas,grid,values,depth) {
  canvas.width=grid.width;canvas.height=grid.height;
  const ctx=canvas.getContext('2d'),image=ctx.createImageData(grid.width,grid.height);
  for(let i=0;i<values.length;i++) {
    const z=values[i],category=classifyElevation(z,depth,grid.nodata);
    let rgb;
    if(category==='land') {const h=Math.min(1,Math.max(0,z)/3500);rgb=[214-h*47,212-h*43,185-h*35];}
    else if(category==='shelf') rgb=[212,167,99];
    else if(category==='missing') rgb=[120,120,120];
    else {const h=Math.min(1,Math.abs(z)/4500);rgb=[36-h*18,79-h*29,86-h*27];}
    image.data.set([...rgb.map(Math.round),255],i*4);
  }
  ctx.putImageData(image,0,0);
  const radius=Math.max(4,grid.width/85);
  for(const p of locations.filter(p=>inGrid(p,grid))) {
    const x=(p.lon-grid.west)/(grid.east-grid.west)*(grid.width-1),y=(grid.north-p.lat)/(grid.north-grid.south)*(grid.height-1);
    ctx.beginPath();ctx.arc(x,y,radius,0,Math.PI*2);ctx.fillStyle='#f3ecda';ctx.fill();
    ctx.lineWidth=Math.max(.6,grid.width/1400);ctx.strokeStyle='#173b45';ctx.stroke();
    ctx.fillStyle='#173b45';ctx.font=`${radius*1.25}px monospace`;ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(p.number,x,y+.1);
  }
  // Coordinate bounds convey location without inventing ancient place names.
  ctx.textAlign='left';ctx.textBaseline='alphabetic';
  ctx.fillStyle='#f4eee1';ctx.font=`${Math.max(7,grid.width/90)}px monospace`;
  ctx.fillText(`${coordinate(grid.west,'E','W')}–${coordinate(grid.east,'E','W')} · ${coordinate(grid.south,'N','S')}–${coordinate(grid.north,'N','S')}`,grid.width*.025,grid.height*.955);
  canvas.hidden=false;
  canvas.setAttribute('aria-label',`${grid.label}. ${depth?`Elevations from zero to minus ${depth} metres highlighted in gold. No date assigned.`:'Modern relief baseline.'}`);
}
function draw() {
  if(!current)return;
  paint($('#modern-canvas'),current.grid,current.values,0);
  paint($('#depth-canvas'),current.grid,current.values,state.depth);
  $('#modern-fallback').hidden=true;$('#depth-fallback').hidden=true;
  $('#depth-output').value=`${state.depth} m`;$('#scenario-title').textContent=`0 to −${state.depth} m`;
  $('#water-depth').value=state.depth;
  for(const p of locations)p.link.hidden=!inGrid(p,current.grid);
  const spacing=Math.round(current.grid.step_degrees*60);
  $('#water-status').textContent=`${current.grid.label} · ${spacing} arc-minute sampling · NOAA ETOPO1 (2009). Depth screen: ${state.depth} m below the model’s mean sea level. No ancient date assigned.`;
  document.body.dataset.waterReady='true';
  for(const b of document.querySelectorAll('[data-water-region]'))b.setAttribute('aria-pressed',b.dataset.waterRegion===state.region);
}
async function loadRegion() {
  const version=++loadVersion,grid=manifest.grids.find(g=>g.id===state.region);
  $('#water-status').textContent=`Loading ${grid.label}…`;
  $('#water-depth').disabled=true;
  for(const b of document.querySelectorAll('[data-water-region]'))b.setAttribute('aria-pressed',b.dataset.waterRegion===state.region);
  try {
    if(!cache.has(grid.id))cache.set(grid.id,fetch(grid.path).then(r=>{if(!r.ok)throw Error('Relief unavailable');return r.arrayBuffer();}).then(buffer=>decodeGrid(buffer,grid)));
    const values=await cache.get(grid.id);if(version!==loadVersion)return;
    current={grid,values};draw();$('#water-depth').disabled=false;
  } catch {
    if(version!==loadVersion)return;
    cache.delete(grid.id);current=null;
    $('#modern-canvas').hidden=true;$('#depth-canvas').hidden=true;
    $('#modern-fallback').hidden=false;$('#depth-fallback').hidden=false;
    for(const p of locations)p.link.hidden=false;
    $('#scenario-title').textContent='0 to −60 m · static world fallback';
    $('#water-status').textContent='This regional grid could not load. Showing the static world view at 60 m; source records and datasets remain available below.';
    document.body.dataset.waterReady='fallback';
  }
}
function save(replace=false) {
  const params=new URLSearchParams({region:state.region,depth:String(state.depth)});
  history[replace?'replaceState':'pushState']({},'',`${location.pathname}?${params}${location.hash}`);
}
async function start() {
  try {
    const r=await fetch('data/submerged/grids.json');if(!r.ok)throw Error();manifest=await r.json();
    state=readWaterState(location.search,manifest.grids);$('#water-tools').hidden=false;
    await loadRegion();
  } catch {$('#water-status').textContent='Interactive data could not load. The static world maps above show the baseline and a 60 m depth screen; all records remain readable.';return;}
  $('#water-depth').addEventListener('input',e=>{state.depth=+e.target.value;save(true);draw();});
  document.addEventListener('click',e=>{
    const b=e.target.closest('[data-water-region]'),link=e.target.closest('[data-region-link]');
    if(link&&(e.metaKey||e.ctrlKey||e.shiftKey||e.altKey))return;
    const region=b?.dataset.waterRegion||link?.dataset.regionLink;if(!region)return;
    if(link)e.preventDefault();state.region=region;save();loadRegion();
    if(link)$('#landscape').scrollIntoView();
  });
  window.addEventListener('popstate',()=>{state=readWaterState(location.search,manifest.grids);loadRegion();});
}
start();
