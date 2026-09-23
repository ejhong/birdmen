import {defaults,views,makeIndex,readState,stateURL,filterClaims,filterFamilies,visibleEntities,clusters,OPEN_TRANSMISSION,yearLabel,escapeHTML as esc,project,coastPath} from './catalogue-model.mjs?v=3';

const $=s=>document.querySelector(s);
const form=$('#catalogue-filters');
let data,idx,state,coastPromise;
let mapVersion=0;
const path=id=>`catalogue/${encodeURIComponent(id)}.html${stateURL(state)?`?from=${encodeURIComponent(stateURL(state))}`:''}`;
const sourceLink=s=>`<a href="${esc(s.url)}">${esc(s.title)}</a>`;
const resultNodes=[...document.querySelectorAll('[data-claim]')];
const familyNodes=[...document.querySelectorAll('[data-family]')];
const controls={q:$('#search'),motif:$('#motif'),culture:$('#culture'),with:$('#with-culture'),region:$('#region'),review:$('#review'),diffusion:$('#diffusion'),from:$('#date-from'),to:$('#date-to'),unknown:$('#unknown'),controls:$('#controls')};

function setState(changes,{replace=false,scroll=false}={}) {
  state={...state,...changes};
  if(state.view==='families'){state.review='';state.diffusion='';}
  if(state.culture && state.culture===state.with) state.with='';
  const url=stateURL(state);
  if(location.search!==url) history[replace?'replaceState':'pushState']({},'',location.pathname+url+location.hash);
  syncForm(); render();
  if(scroll) $('#explore').scrollIntoView({behavior:'auto'});
}
function syncForm() {
  for(const [key,node] of Object.entries(controls)) {
    if(node.type==='checkbox') node.checked=state[key]; else node.value=state[key];
  }
  controls.review.disabled=state.view==='families';
  controls.diffusion.disabled=state.view==='families';
}
function selected(claims) {return claims.find(c=>c.id===state.focus)||claims[0];}
function claimSelect(claims,label='Inspect a comparison') {
  const chosen=selected(claims);
  return `<label class="micro">${label}<select data-focus aria-label="${label}">${claims.map(c=>`<option value="${esc(c.id)}" ${c===chosen?'selected':''}>${esc(c.title)}</option>`).join('')}</select></label>`;
}
function threadList(claims) {
  return `<div class="thread-list">${claims.map(c=>`<a class="thread-item" href="${path(c.id)}"><strong>${esc(c.title)}</strong><span>${esc(c.dek)}</span></a>`).join('')}</div>`;
}
function render() {
  const claims=filterClaims(data,state,idx), ids=new Set(claims.map(c=>c.id));
  const families=filterFamilies(data,state,idx),familyIDs=new Set(families.map(f=>f.id)),isFamily=state.view==='families';
  const hasResults=isFamily?families.length:claims.length;
  document.body.dataset.catalogueView=state.view;
  for(const node of resultNodes) {
    node.hidden=!ids.has(node.dataset.claim);
    node.querySelector('.card-link').href=path(node.dataset.claim);
  }
  for(const node of familyNodes){
    node.hidden=!familyIDs.has(node.dataset.family);
    node.querySelector('.family-link').href=`families/${node.dataset.family}.html${stateURL(state)?`?from=${encodeURIComponent(stateURL(state))}`:''}`;
  }
  for(const view of views) $(`#${view}-view`).hidden=state.view!==view||!hasResults;
  for(const button of document.querySelectorAll('[data-view]')) button.setAttribute('aria-pressed',button.dataset.view===state.view);
  const counts=claims.filter(c=>c.kind==='claim').length, extra=claims.length-counts;
  $('#result-count').textContent=isFamily?`${families.length} motif ${families.length===1?'family':'families'} · open one to explore its cultures and sources`:`${counts} comparison ${counts===1?'thread':'threads'}${extra?` · ${extra} context controls`:''} · ${visibleEntities(claims,idx).length} records`;
  const labels=[state.culture&&idx.cultures.get(state.culture).label,state.with&&'↔ '+idx.cultures.get(state.with).label,state.motif&&idx.motifs.get(state.motif).label,state.region,state.review&&state.review.replace('-',' '),state.controls&&'Context controls included'].filter(Boolean);
  $('#active-filters').textContent=labels.join(' · ');
  $('#active-filters').hidden=!labels.length;
  $('#empty-state').hidden=!!hasResults;
  $('#date-filter-note').hidden=!(state.from||state.to||!state.unknown);
  $('#date-filter-note').textContent=`Includes a ${isFamily?'family':'comparison'} if any ${isFamily?'attested episode':'recorded interval'} overlaps ${state.from?yearLabel(+state.from):'the earliest date'} to ${state.to?yearLabel(+state.to):'the latest date'}.${state.unknown?' Undated records and leads are included.':''} This does not imply that the traditions coexisted.`;
  if(!hasResults||isFamily) return;
  if(state.view==='map') renderMap(claims);
  if(state.view==='time') renderTime(claims);
  if(state.view==='cultures') renderCultures(claims);
  if(state.view==='themes') renderThemes(claims);
}
const STATUS_LABEL={examined:'Evidence examined','source-check':'Sources partly checked',lead:'Research lead',corrected:'Claim corrected'};
const DIFFUSION_LABEL={unestablished:'No route established in this review',unassessed:'Transmission not yet assessed',plausible:'Regional transmission remains possible',local:'Documented local context',documented:'Independent contact evidence'};
function plate(entity) {
  if(!entity) return '<figure class="plate plate-empty"><div class="plate-mount"><i aria-hidden="true">∿</i></div></figure>';
  const media=idx.media.get(entity.media);
  const inner=media?`<img src="${esc(media.path)}" alt="${esc(media.alt)}" loading="lazy" decoding="async">`
    :`<div class="text-specimen"><span>${entity.kind==='account'?'Account · editorial paraphrase':'Research evidence'}</span><p>${esc(entity.text||entity.label)}</p><i aria-hidden="true">∿</i></div>`;
  return `<figure class="plate"><div class="plate-mount">${inner}</div></figure>`;
}
function sideRecords(cluster,culture) {
  const seen=new Set();
  return cluster.threads.flatMap(id=>idx.claims.get(id).members).map(id=>idx.entities.get(id))
    .filter(e=>e.culture===culture&&!seen.has(e.id)&&seen.add(e.id));
}
function representative(cluster,culture) {
  const records=sideRecords(cluster,culture);
  return records.find(e=>e.media)||records[0]||null;
}
function clusterCounts(cluster) {
  const lines=cluster.lines.length, families=cluster.families.length;
  return `${lines} line${lines===1?'':'s'} of comparison · ${cluster.open} without an established route · ${families} motif famil${families===1?'y':'ies'} · ${cluster.records} registered object${cluster.records===1?'':'s'}`;
}
function ledger(cluster) {
  return `<ol class="cluster-ledger">${cluster.lines.map(line=>{
    const c=idx.claims.get(line.root), open=OPEN_TRANSMISSION.includes(c.diffusion.status);
    return `<li class="line-${open?'open':'context'}"><b>${esc(c.title)}</b><span>${esc(STATUS_LABEL[c.status])} · ${esc(DIFFUSION_LABEL[c.diffusion.status])}</span></li>`;
  }).join('')}</ol>`;
}
/** The cluster view: culture pairs ranked by open comparisons, never by evidence strength. */
function renderCultures(claims) {
  // A chosen pair stays the subject: its threads may also reach a third tradition.
  const rows=clusters(claims,data,idx).filter(cluster=>
    (!state.culture||cluster.a===state.culture||cluster.b===state.culture) &&
    (!state.with||cluster.a===state.with||cluster.b===state.with));
  const heading=`<div class="panel-heading"><div><h3>Where the questions concentrate.</h3><p>Culture pairs in this selection, ordered by how many separate comparisons stay open after a source check. Counting comparisons never makes them independent, and no pairing below establishes that two traditions met.</p></div></div>`;
  if(!rows.length) {$('#cultures-view').innerHTML=heading+'<p class="view-note">No two identified traditions are joined in this selection. Open a thread to follow its unresolved records.</p>'+threadList(claims); return;}
  $('#cultures-view').innerHTML=heading+`<ol class="cluster-list">${rows.map((cluster,n)=>{
    const depth=cluster.examined?'examined in depth':cluster.checked?'source checks begun':'awaiting identification';
    const families=cluster.families.map(id=>esc(idx.families.get(id).label)).join(' · ')||'No motif family assigned yet';
    return `<li class="cluster-row"><a class="cluster-link" href="clusters/${esc(cluster.id)}.html">
      <div class="cluster-plates">${plate(representative(cluster,cluster.a))}<span class="plate-join" aria-hidden="true">↔</span>${plate(representative(cluster,cluster.b))}</div>
      <div class="cluster-copy"><div class="micro">${String(n+1).padStart(2,'0')} · ${depth}</div>
      <h3>${esc(idx.cultures.get(cluster.a).label)} ↔ ${esc(idx.cultures.get(cluster.b).label)}</h3><p>${families}</p>${ledger(cluster)}
      <div class="cluster-foot">${esc(clusterCounts(cluster))}<span>Open the cluster →</span></div></div></a>
      <div class="cluster-actions"><button type="button" data-pair="${esc(cluster.a)},${esc(cluster.b)}">Show its ${cluster.threads.length} thread${cluster.threads.length===1?'':'s'} in this view →</button></div></li>`;
  }).join('')}</ol>
  <p class="view-note">A line of comparison is one proposed resemblance; its subcomparisons are counted inside it, because they are not separate evidence. “Open” records the state of this review, and an unchecked lead is weaker than a checked one, not stronger.${state.culture||state.with?' A thread listed here may also reach a third tradition; its cluster page names them.':''}</p>
  <p class="view-note"><a href="clusters.html">Open the full cluster index, with the table of resemblances →</a></p>`;
}
async function renderMap(claims) {
  const version=++mapVersion, c=selected(claims), allEntities=visibleEntities(claims,idx);
  const places=[...new Set(allEntities.map(e=>e.place).filter(Boolean))].map(id=>idx.places.get(id));
  const chosenPlaces=[...new Set(c.members.map(id=>idx.entities.get(id).place).filter(Boolean))].map(id=>idx.places.get(id));
  const chosenIDs=new Set(chosenPlaces.map(p=>p.id));
  const unavailable=c.members.filter(id=>!idx.entities.get(id).place);
  $('#map-view').innerHTML=`<div class="panel-heading"><div><h3>Where the comparisons meet.</h3><p>Approximate original contexts, with one comparison highlighted. Open circles mark regional or provisional locations. Lines are comparisons, not voyages.</p></div>${claimSelect(claims)}</div>
    <div class="map-layout"><div class="map-canvas"><p class="view-note">Loading the coastline…</p></div><aside class="map-side"><div class="micro">Selected thread</div><h3>${esc(c.title)}</h3><p>${esc(c.dek)}</p><ul>${chosenPlaces.map(p=>`<li>${esc(p.name)}${p.precision==='region'?' · regional anchor':''}</li>`).join('')}</ul>${unavailable.length?`<p class="micro">${unavailable.length} record(s) have no verified map location.</p>`:''}<a href="${path(c.id)}">Inspect the groups and evidence →</a></aside></div>
    <div class="map-legend"><span>Approximate site</span><span>Region / provisional context</span><span>Proposed comparison</span></div>
    <p class="view-note">Natural Earth, public domain · modern coastlines. The connecting strokes have no chronological or directional meaning. Nearby records may share a marker at this world scale.</p>
    <details class="map-locations"><summary>All ${places.length} locations in this filtered collection</summary><ul>${places.map(p=>`<li><b>${esc(p.name)}</b> · ${esc(p.region)}<br>${esc(p.note)}</li>`).join('')}</ul></details>${threadList(claims)}`;
  try {
    coastPromise ||= fetch('data/catalogue-coast.json').then(r=>{if(!r.ok)throw Error('Coastline unavailable');return r.json();});
    const coast=await coastPromise;
    if(version!==mapVersion||state.view!=='map') return;
    const grid=[-120,-60,0,60,120].map(lon=>{const [x]=project(lon,0);return `<path d="M${x} 0V500"/>`;}).join('')+[-60,-30,0,30,60].map(lat=>{const [,y]=project(0,lat);return `<path d="M0 ${y}H1000"/>`;}).join('');
    const lines=chosenPlaces.slice(1).map(p=>{const [x1,y1]=project(chosenPlaces[0].lon,chosenPlaces[0].lat),[x2,y2]=project(p.lon,p.lat);return `<path class="map-connection" d="M${x1} ${y1} Q${(x1+x2)/2} ${Math.max(8,Math.min(y1,y2)-75)} ${x2} ${y2}"/>`;}).join('');
    // Cluster co-located site markers visually, retain every named place in the list.
    const labels=[];
    const dots=places.map(p=>{const [x,y]=project(p.lon,p.lat),active=chosenIDs.has(p.id);const overlap=labels.some(([a,b])=>Math.hypot(a-x,b-y)<36);if(active&&!overlap)labels.push([x,y]);return `<circle class="map-dot ${p.precision==='region'?'region':''} ${active?'selected':''}" cx="${x}" cy="${y}" r="${p.precision==='region'?10:active?6:4}"><title>${esc(p.name)} · ${esc(p.note)}</title></circle>${active&&!overlap?`<text class="map-label" x="${Math.min(940,Math.max(60,x))}" y="${y-17}" text-anchor="middle">${esc(p.name)}</text>`:''}`;}).join('');
    $('#map-view .map-canvas').innerHTML=`<svg viewBox="0 0 1000 500" role="img" aria-labelledby="map-title map-desc"><title id="map-title">${esc(c.title)}</title><desc id="map-desc">${esc(chosenPlaces.map(p=>p.name).join(' compared with '))}. Text descriptions and a location list accompany the map.</desc><g class="map-grid">${grid}</g><path class="map-coast" d="${coastPath(coast.lines)}"/>${lines}${dots}</svg>`;
  } catch {if(version===mapVersion) $('#map-view .map-canvas').innerHTML='<p class="catalogue-message">The coastline could not load. The locations and comparison records remain available alongside this panel.</p>'; coastPromise=null;}
}
function renderTime(claims) {
  const c=selected(claims), entities=c.members.map(id=>idx.entities.get(id));
  const lower=state.scale==='recent'?-1000:-10000, upper=2026;
  const pos=n=>100*(n-lower)/(upper-lower);
  const labels=state.scale==='recent'?[-1000,-250,500,1250,2026]:[-10000,-7000,-4000,-1000,2026];
  const rows=entities.flatMap(e=>e.dates.map(d=>{
    const out=d.start!==null&&(d.end<lower||d.start>upper);
    const witness=['witness','composition','recording'].includes(d.kind);
    const context=d.kind.includes('context')||d.kind.includes('estimate')||d.kind.includes('interval');
    const bar=d.start===null?'<span class="time-unknown">Date unresolved — retained in the comparison</span>':out?'<span class="time-unknown">Outside this zoom window</span>':`<span class="time-band ${witness?'witness':context?'context':''}" style="left:${Math.max(0,pos(d.start))}%;width:${Math.max(.4,Math.min(100,pos(d.end))-Math.max(0,pos(d.start)))}%" title="${esc(d.label+' · '+d.kind+' · '+d.note)}"></span>`;
    return `<div class="time-row"><div class="time-label">${esc(e.label)}<span>${esc(d.label)} · ${esc(d.kind)}</span></div><div class="time-track">${bar}</div></div>`;
  }));
  $('#time-view').innerHTML=`<div class="panel-heading"><div><h3>The resemblance has a chronology.</h3><p>Each band is a recorded episode, not a culture’s entire lifetime. Orange marks a composition or textual witness; hatched bands mark context, estimates or modelled intervals.</p></div>${claimSelect(claims)}</div>
  <div class="panel-heading"><a class="text-link" href="${path(c.id)}">${esc(c.title)} →</a><div class="timeline-controls" aria-label="Timeline zoom"><button type="button" data-scale="all" aria-pressed="${state.scale==='all'}">Full span</button><button type="button" data-scale="recent" aria-pressed="${state.scale==='recent'}">Last 3,000 years</button></div></div>
  <div class="time-scroll" tabindex="0" aria-label="Chronology; scroll horizontally on small screens"><div class="time-chart"><div class="time-axis">${labels.map(n=>`<span>${yearLabel(n)}</span>`).join('')}</div>${rows.join('')}</div></div>
  <p class="view-note">Open or expand the dated records below for the source and qualification of every interval. An early statue date is not automatically the date of later carvings. A manuscript date is not a story’s origin.</p>
  <details class="time-register" open><summary>Dates, unknowns and their sources</summary><div class="time-scroll"><table class="time-table"><thead><tr><th>Record</th><th>Dated episode</th><th>Basis and qualification</th></tr></thead><tbody>${entities.flatMap(e=>e.dates.map(d=>`<tr><th scope="row">${esc(e.label)}</th><td>${esc(d.label)}<br>${esc(d.kind)}</td><td>${esc(d.note)} ${d.source?sourceLink(idx.sources.get(d.source)):''}</td></tr>`)).join('')}</tbody></table></div></details>${threadList(claims)}`;
}
function renderThemes(claims) {
  $('#themes-view').innerHTML=`<div class="panel-heading"><div><h3>Different ways to notice a pattern.</h3><p>Themes gather questions across cultures. A broad category such as “bird” is not itself a match for a specific pose or scene.</p></div></div><div class="theme-grid">${data.motifs.map(m=>{const count=claims.filter(c=>c.motifs.includes(m.id)).length;return count?`<a class="theme-card" href="catalogue.html${esc(stateURL({...state,motif:m.id,view:'gallery'}))}" data-theme="${m.id}"><span class="micro">${count} comparison ${count===1?'thread':'threads'}</span><h3>${esc(m.label)}</h3><p>${esc(m.note)}</p></a>`:'';}).join('')}</div>`;
}
async function start() {
  try {
    const response=await fetch('data/catalogue.json?v=3'); if(!response.ok) throw Error('Catalogue unavailable');
    data=await response.json(); idx=makeIndex(data); state=readState(location.search,data);
    syncForm(); render();
    form.hidden=false; $('#view-toolbar').hidden=false; $('#copy-view').hidden=false;
    document.body.classList.add('catalogue-ready');
    if(location.search) $('#explore').scrollIntoView({behavior:'auto'});
  } catch {$('#load-error').hidden=false; return;}
  $('#more-filters').addEventListener('click',()=>{const open=$('#filter-details').hidden;$('#filter-details').hidden=!open;$('#more-filters').setAttribute('aria-expanded',String(open));});
  let timer;
  form.addEventListener('submit',e=>e.preventDefault());
  form.addEventListener('input',e=>{
    clearTimeout(timer);
    const apply=()=>{
      const changes=Object.fromEntries(Object.entries(controls).map(([key,node])=>[key,node.type==='checkbox'?node.checked:node.value]));
      const invalid=(changes.from!==''&&(Number(changes.from)===0||!controls.from.validity.valid))||(changes.to!==''&&(Number(changes.to)===0||!controls.to.validity.valid))||(changes.from!==''&&changes.to!==''&&Number(changes.from)>Number(changes.to));
      $('#filter-error').hidden=!invalid; $('#filter-error').textContent=invalid?'Use a valid interval: from must precede to, within 12,000 BCE–2026 CE, with no year zero.':'';
      if(!invalid) setState(changes,{replace:e.target===controls.q||e.target.type==='number'});
    };
    if(e.target.type==='search'||e.target.type==='number') timer=setTimeout(apply,180); else apply();
  });
  document.addEventListener('click',e=>{
    const view=e.target.closest('[data-view]'),pair=e.target.closest('[data-pair]'),theme=e.target.closest('[data-theme]'),scale=e.target.closest('[data-scale]');
    if(view) setState({view:view.dataset.view});
    if(scale) setState({scale:scale.dataset.scale});
    if(pair) {e.preventDefault(); const [culture,other]=pair.dataset.pair.split(',');setState({culture,with:other,view:'gallery'});}
    if(theme && !e.metaKey && !e.ctrlKey && !e.shiftKey && !e.altKey) {e.preventDefault();setState({motif:theme.dataset.theme,view:'gallery'});}
  });
  document.addEventListener('change',e=>{if(e.target.matches('[data-focus]')) setState({focus:e.target.value});});
  const reset=()=>{clearTimeout(timer);$('#filter-error').hidden=true;setState({...defaults,view:state.view});};
  $('#reset-filters').addEventListener('click',reset); $('#empty-reset').addEventListener('click',reset);
  $('#copy-view').addEventListener('click',async()=>{
    try {await navigator.clipboard.writeText(location.href); $('#copy-view').textContent='Link copied';}
    catch {$('#copy-view').textContent='Copy the address in your browser';}
    setTimeout(()=>$('#copy-view').textContent='Copy this view ↗',2500);
  });
  window.addEventListener('popstate',()=>{clearTimeout(timer);state=readState(location.search,data);syncForm();render();});
}
start();
