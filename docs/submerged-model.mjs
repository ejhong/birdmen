export function readWaterState(search, grids) {
  const p=new URLSearchParams(search), region=p.get('region'), n=Number(p.get('depth'));
  return {region:grids.some(g=>g.id===region)?region:'world',depth:p.get('depth')?.trim()&&Number.isFinite(n)?Math.max(0,Math.min(120,Math.round(n/5)*5)):60};
}
export function classifyElevation(z,depth,nodata=32767) {
  if(z===nodata||!Number.isFinite(z))return 'missing';
  if(z>=0)return 'land';
  return z>=-depth?'shelf':'water';
}
export function decodeGrid(buffer,grid) {
  if(buffer.byteLength!==grid.width*grid.height*2)throw Error('Grid dimensions do not match');
  const view=new DataView(buffer),values=new Int16Array(grid.width*grid.height);
  for(let i=0;i<values.length;i++)values[i]=view.getInt16(i*2,true);
  return values;
}
