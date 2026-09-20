/** Pure catalogue queries. A comparison is an editorial relationship, not contact. */
export const views = ['families', 'gallery', 'cultures', 'map', 'time', 'themes'];
export const defaults = Object.freeze({q:'', motif:'', culture:'', with:'', region:'', review:'', diffusion:'', from:'', to:'', unknown:true, controls:false, view:'families', focus:'', hub:'', scale:'all'});
export function makeIndex(data) {
  return Object.fromEntries(['entities','groups','claims','cultures','motifs','media','places','sources','families','attestations','leads'].map(key => [key, new Map(data[key].map(row=>[row.id,row]))]));
}
export function readState(search, data) {
  const params = new URLSearchParams(search), state = {...defaults};
  for (const key of Object.keys(state)) if (params.has(key)) state[key] = params.get(key);
  state.unknown = params.get('unknown') !== '0';
  state.controls = params.get('controls') === '1';
  state.q = state.q.slice(0,200);
  if (!views.includes(state.view)) state.view = defaults.view;
  if (!['all','recent'].includes(state.scale)) state.scale='all';
  for (const [key,collection] of [['motif','motifs'],['culture','cultures'],['with','cultures'],['focus','claims'],['hub','cultures']]) {
    if (!data[collection].some(row=>row.id===state[key])) state[key]='';
  }
  if (state.with===state.culture) state.with='';
  if (!['','examined','source-check','lead','corrected'].includes(state.review)) state.review='';
  if (!['','unestablished','unassessed','plausible','local','documented'].includes(state.diffusion)) state.diffusion='';
  if (state.view==='families') {state.review='';state.diffusion='';}
  if (!data.places.some(p=>p.region===state.region)) state.region='';
  for (const key of ['from','to']) if (!/^-?\d{1,5}$/.test(state[key]) || Number(state[key])===0 || Number(state[key]) < -12000 || Number(state[key])>2026) state[key]='';
  return state;
}
export function stateURL(state) {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(defaults)) {
    if (state[key]===value || state[key]==='' || state[key]===undefined) continue;
    params.set(key, typeof state[key]==='boolean' ? Number(state[key]).toString() : state[key]);
  }
  return params.size ? `?${params}` : '';
}
export function normalize(value) {return value.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();}
export function dateOverlaps(date, from, to) {
  return date.start !== null && date.start <= to && date.end >= from;
}
export function filterClaims(data,state,idx=makeIndex(data)) {
  const from = state.from==='' ? -Infinity : Number(state.from), to = state.to==='' ? Infinity : Number(state.to);
  if (from > to) return [];
  const terms=normalize(state.q).split(/\s+/).filter(Boolean);
  return data.claims.filter(c=>{
    if (c.kind==='control' && !state.controls) return false;
    if (state.motif && !c.motifs.includes(state.motif)) return false;
    if (state.culture && !c.cultures.includes(state.culture)) return false;
    if (state.with && !c.cultures.includes(state.with)) return false;
    if (state.review && c.status!==state.review) return false;
    if (state.diffusion && c.diffusion.status!==state.diffusion) return false;
    const entities=c.members.map(id=>idx.entities.get(id));
    if (state.region && !entities.some(e=>idx.places.get(e.place)?.region===state.region)) return false;
    const dates=entities.flatMap(e=>e.dates);
    // This is ANY recorded interval, never implied simultaneous existence.
    if (!dates.some(d=>dateOverlaps(d,from,to)) && !(state.unknown && dates.some(d=>d.start===null))) return false;
    if (terms.length) {
      const sources=[c.origin.source,...c.sources].map(id=>idx.sources.get(id));
      const hay=normalize([c.title,c.dek,c.anomaly,c.origin.note,...c.features,...c.differences,
        ...c.motifs.map(id=>idx.motifs.get(id).label),...c.cultures.map(id=>idx.cultures.get(id).label),
        ...entities.flatMap(e=>[e.label,e.note,idx.places.get(e.place)?.name||'']),
        ...sources.flatMap(s=>[s.title,s.author])].join(' '));
      if (!terms.every(term=>hay.includes(term))) return false;
    }
    return true;
  });
}
export function visibleEntities(claims,idx) {
  return [...new Set(claims.flatMap(c=>c.members))].map(id=>idx.entities.get(id));
}
/** A family is an n-way collection of explicit observations, never a pairwise edge. */
export function familyObservations(data, family) {
  return data.attestations.filter(o=>o.family===family.id);
}
export function filterFamilies(data,state,idx=makeIndex(data)) {
  const from=state.from===''?-Infinity:Number(state.from),to=state.to===''?Infinity:Number(state.to);
  if(from>to)return [];
  const terms=normalize(state.q).split(/\s+/).filter(Boolean);
  return data.families.filter(f=>{
    if(state.motif&&!f.motifs.includes(state.motif))return false;
    const obs=familyObservations(data,f),entities=obs.map(o=>idx.entities.get(o.entity));
    const cultures=new Set(entities.map(e=>e.culture));
    if(state.culture&&!cultures.has(state.culture)||state.with&&!cultures.has(state.with))return false;
    if(state.region&&!entities.some(e=>idx.places.get(e.place)?.region===state.region))return false;
    const leads=data.leads.filter(l=>l.families.includes(f.id)&&(state.controls||l.kind==='claim'));
    // Only the attested episode's dates apply, not every date attached to the object.
    const dates=obs.flatMap(o=>o.date_indices.map(n=>idx.entities.get(o.entity).dates[n]));
    if(!dates.some(d=>dateOverlaps(d,from,to))&&!(state.unknown&&(dates.some(d=>d.start===null)||leads.length)))return false;
    if(terms.length){
      const hay=normalize([f.label,f.summary,...f.features.map(v=>v.label),...entities.flatMap(e=>[e.label,e.note,idx.cultures.get(e.culture).label]),...obs.map(o=>o.note),...leads.flatMap(l=>[l.title,l.note,...l.panels.map(p=>p.label)])].join(' '));
      if(!terms.every(t=>hay.includes(t)))return false;
    }
    return true;
  });
}
/** Features must occur in ONE recorded scope; a culture-wide union is not a bundle. */
export function hasRecordedBundle(data,family,entity,features,{provisional=false}={}) {
  if(!features.length)return false;
  return data.attestations.some(o=>o.family===family&&o.entity===entity&&(provisional||o.status==='documented')&&features.every(f=>o.features.includes(f)));
}
export function culturalEdges(claims) {
  const edges=new Map();
  for(const c of claims) for(let i=0;i<c.cultures.length;i++) for(let j=i+1;j<c.cultures.length;j++) {
    const [a,b]=[c.cultures[i],c.cultures[j]].sort(), key=`${a}|${b}`;
    if(!edges.has(key)) edges.set(key,{a,b,claims:[],families:new Set()});
    edges.get(key).claims.push(c.id);
    edges.get(key).families.add(c.parent||c.id);
  }
  return [...edges.values()].map(e=>({...e,families:[...e.families]}));
}
export function yearLabel(n) {return `${Math.abs(n).toLocaleString('en')} ${n<0?'BCE':'CE'}`;}
export function escapeHTML(value) {return String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
// Equirectangular map; display precision does not imply archaeological precision.
export function project(lon,lat) {return [(lon+180)*1000/360,(85-lat)*500/170];}
export function coastPath(lines) {
  return lines.map(line=>line.map(([lon,lat],i)=>`${!i||Math.abs(lon-line[i-1][0])>180?'M':'L'}${project(lon,lat).map(n=>n.toFixed(1)).join(' ')}`).join('')).join('');
}
