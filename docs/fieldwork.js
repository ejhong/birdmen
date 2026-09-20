import {readState,stateURL,presets,labels,filterObjects,yearLabel,escapeHTML as esc} from './fieldwork-model.mjs?v=1';

const $=s=>document.querySelector(s);
async function start() {
  const response=await fetch('data/pillar-moai/fieldwork/register.json?v=1');
  if(!response.ok)throw new Error('Fieldwork data unavailable');
  const data=await response.json(),idx=new Map(data.objects.map(o=>[o.id,o]));
  let state=readState(location.search,data);
  const narrowTimeline=window.matchMedia('(max-width:760px)');
  const refs=ids=>ids.map(id=>`<a href="#source-${esc(id)}">${esc(data.sources.find(s=>s.id===id).title)}</a>`).join(' · ');
  function photo(obj) {
    const im=obj.image;
    const marks=im.annotations.map((m,i)=>{const[x,y,w,h]=m.box;return `<g><title>${esc(m.label+': '+m.note)}</title><rect x="${x*1000}" y="${y*1000}" width="${w*1000}" height="${h*1000}"/><text x="${x*1000+5}" y="${y*1000+22}">${i+1}</text></g>`;}).join('');
    return `<div class="fw-photo"><div class="fw-image-plane" style="--image-ratio:${im.width/im.height}"><img src="${esc(im.path)}" width="${im.width}" height="${im.height}" alt="${esc(obj.label+'. '+obj.scope)}"><svg class="fw-overlay" viewBox="0 0 1000 1000" preserveAspectRatio="none" aria-hidden="true">${marks}</svg></div></div>`;
  }
  function panel(side) {
    const obj=idx.get(state[side]),im=obj.image;
    const options=data.objects.map(o=>`<option value="${o.id}"${o.id===obj.id?' selected':''}>${esc(o.label+' · '+o.number)}</option>`).join('');
    const marks=im.annotations.map((m,i)=>`<li><b>${i+1}. ${esc(m.label)}</b> ${esc(m.note)}</li>`).join('');
    $(`#panel-${side}`).innerHTML=`<label class="fw-select">${side==='left'?'First':'Second'} object<select id="select-${side}">${options}</select></label>${photo(obj)}<div class="fw-panel-copy"><div class="micro">${esc(obj.culture)}</div><h3>${esc(obj.label)}</h3><p class="fw-date">${esc(obj.date.label)}</p><p>${esc(obj.reading)}</p><button class="fw-zoom" type="button" data-side="${side}">Enlarge photograph ↗</button><details><summary>Image, annotations &amp; sources</summary><p class="fw-small">${esc(im.credit)} · ${esc(im.rights)} <a href="${esc(im.origin)}">Source image / record</a>.</p><ol class="fw-annotation-list">${marks}</ol><p class="fw-small">${refs(obj.sources)}</p><p class="fw-small">${esc(obj.date.note)}</p></details></div>`;
  }
  function matrix() {
    const objs=[idx.get(state.left),idx.get(state.right)];
    const rows=data.features.map(f=>`<tr><th scope="row">${esc(f.label)}</th>${objs.map(o=>{const c=o.observations[f.id];return `<td><span class="fw-state ${c.state}">${labels[c.state]}</span>${esc(c.note)}</td>`;}).join('')}</tr>`).join('');
    $('#comparison-matrix').innerHTML=`<div class="table-scroll"><table class="feature-matrix fw-matrix"><caption>Readings within the stated scene and photograph. “Not seen” is not absence from the whole object or culture.</caption><thead><tr><th>Relationship</th>${objs.map(o=>`<th>${esc(o.label)}</th>`).join('')}</tr></thead><tbody>${rows}</tbody></table></div>`;
  }
  function timeline() {
    const compact=narrowTimeline.matches;
    const min=state.era==='recent'?-2500:-10000,max=2026,x0=compact?8:305,x1=compact?352:1070;
    const x=y=>x0+(y-min)/(max-min)*(x1-x0);
    const events=data.events.filter(e=>e.end>=min);
    const step=compact?65:43;
    const ticks=compact?(state.era==='recent'?[-2000,1,2000]:[-10000,-4000,2000]):
      (state.era==='recent'?[-2000,-1000,1,1000,2000]:[-10000,-8000,-6000,-4000,-2000,1,2000]);
    const axis=ticks.map((t,i)=>`<line class="fw-axis" x1="${x(t)}" x2="${x(t)}" y1="30" y2="${compact?34:events.length*step+44}"/><text x="${x(t)}" y="18" text-anchor="${compact?(i===0?'start':i===ticks.length-1?'end':'middle'):'middle'}">${esc(yearLabel(t))}</text>`).join('');
    const rows=events.map((e,i)=>{
      const y=(compact?74:56)+i*step;let mark;
      if(e.start===null||e.start===e.end||['historical witness','collection','documentary observation'].includes(e.kind)) {
        const xx=x(e.end);mark=`<path class="fw-bound" d="M${xx},${y-6}l6,6l-6,6l-6,-6Z"/>`;
      } else {
        // Plot the selected objects separately; their endpoints do not imply continuity.
        const intervals=e.kind==='selected range'?e.objects.map(id=>idx.get(id).date):[e];
        mark=intervals.filter(d=>d.start!==null&&d.end>=min).map(d=>{
          const start=x(Math.max(min,d.start));
          return `<rect class="${e.kind==='context'?'fw-context':'fw-range'}" x="${start}" y="${y-5}" width="${Math.max(3,x(d.end)-start)}" height="10" rx="2"/>`;
        }).join('');
      }
      const baseline=compact?`<line class="fw-axis" x1="${x0}" x2="${x1}" y1="${y}" y2="${y}"/>`:'';
      return `<a href="#event-${e.id}"><title>${esc(e.label+'. '+e.when+'. '+e.limit)}</title><text class="fw-chart-label" x="0" y="${compact?y-19:y+4}">${esc(e.chart_label)}</text>${baseline}${mark}</a>`;
    }).join('');
    $('#evidence-timeline').innerHTML=`<svg viewBox="0 0 ${compact?360:1130} ${events.length*step+75}" role="img" aria-label="Dated contexts, object attributions and documentary bounds; these do not form a transmission route">${axis}${rows}</svg>`;
    document.querySelectorAll('[data-era]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.era===state.era)));
  }
  function render() {
    panel('left');panel('right');matrix();timeline();
    document.body.classList.toggle('fw-hide-guides',!state.guides);
    $('#show-guides').checked=state.guides;
    $('#motif-filter').value=state.filter;$('#include-uncertain').checked=state.uncertain;
    const visible=new Set(filterObjects(data,state).map(o=>o.id));
    document.querySelectorAll('.fw-card').forEach(el=>el.hidden=!visible.has(el.dataset.object));
    $('#collection-count').textContent=`${visible.size} of ${data.objects.length} selected objects${state.uncertain?' · uncertain readings included':''}. These counts are not worldwide motif frequencies.`;
    $('#collection-empty').hidden=visible.size>0;
    document.querySelectorAll('[data-preset]').forEach(b=>b.setAttribute('aria-pressed',String(presets[b.dataset.preset][0]===state.left&&presets[b.dataset.preset][1]===state.right)));
    document.querySelectorAll('.fw-interactive').forEach(el=>el.hidden=false);
  }
  function update(patch,hash=location.hash) {
    state={...state,...patch};
    history.pushState(null,'',location.pathname+stateURL(state)+hash);
    render();
  }
  function revealHash() {
    let id;try{id=decodeURIComponent(location.hash.slice(1));}catch{return;}
    const target=document.getElementById(id);if(!target)return;
    const card=target.closest('.fw-card');
    if(card?.hidden){state.filter='all';history.replaceState(null,'',location.pathname+stateURL(state)+location.hash);render();}
    for(let parent=target;parent;parent=parent.parentElement)if(parent.tagName==='DETAILS')parent.open=true;
    requestAnimationFrame(()=>target.scrollIntoView({block:'start'}));
  }
  document.addEventListener('change',event=>{
    const id=event.target.id;
    if(id==='select-left'||id==='select-right')update({[id.slice(7)]:event.target.value});
    if(id==='show-guides')update({guides:event.target.checked});
    if(id==='motif-filter')update({filter:event.target.value});
    if(id==='include-uncertain')update({uncertain:event.target.checked});
    // Rerendering must not leave keyboard users at the top of the document.
    document.getElementById(id)?.focus({preventScroll:true});
  });
  document.addEventListener('click',async event=>{
    const b=event.target.closest('button');if(!b)return;
    if(b.dataset.preset){const[left,right]=presets[b.dataset.preset];update({left,right});}
    if(b.dataset.choose){update({right:b.dataset.choose},'#compare');$('#compare').scrollIntoView({block:'start'});$('#select-right').focus({preventScroll:true});}
    if(b.dataset.era)update({era:b.dataset.era});
    if(b.id==='reset-collection')update({filter:'all',uncertain:false});
    if(b.dataset.side){
      const obj=idx.get(state[b.dataset.side]);$('#dialog-photo').innerHTML=photo(obj);
      $('#dialog-caption').textContent=`${obj.label} · ${obj.image.credit}. ${obj.image.rights}`;
      const original=document.createElement('a');original.href=obj.image.path;
      original.textContent='Open the full image ↗';original.target='_blank';original.rel='noopener';
      $('#dialog-caption').append(' · ',original);
      $('#photo-dialog').showModal();
    }
    if(b.id==='close-photo')$('#photo-dialog').close();
    if(b.id==='share-comparison'){
      try{await navigator.clipboard.writeText(location.href);$('#share-status').textContent='Link copied.';}
      catch{$('#share-status').textContent=location.href;}
    }
  });
  window.addEventListener('popstate',()=>{state=readState(location.search,data);render();revealHash();});
  window.addEventListener('hashchange',revealHash);
  narrowTimeline.addEventListener('change',timeline);
  render();document.body.dataset.fieldworkReady='true';if(location.hash)revealHash();
}
start().catch(()=>{document.body.dataset.fieldworkReady='fallback';});
