export const defaults = {left:'gt-p43',right:'rn-boulder',guides:true,filter:'all',uncertain:false,era:'all'};
export const presets = {
  boulder:['gt-p43','rn-boulder'],moai:['gt-p43','rn-hoa'],
  local:['gt-p43','gt-p33'],assyria:['met-322614','met-322486']
};
export const labels = {present:'Observed',uncertain:'Uncertain','not-seen':'Not seen in this view',unresolved:'Unresolved','not-applicable':'Does not apply'};
export function readState(search,data) {
  const q=new URLSearchParams(search),ids=new Set(data.objects.map(o=>o.id));
  return {
    left:ids.has(q.get('left'))?q.get('left'):defaults.left,
    right:ids.has(q.get('right'))?q.get('right'):defaults.right,
    guides:q.get('guides')!=='0',
    filter:['all','beaks','round','relation','pairs'].includes(q.get('filter'))?q.get('filter'):'all',
    uncertain:q.get('uncertain')==='1',era:q.get('era')==='recent'?'recent':'all'
  };
}
export function stateURL(state) {
  const q=new URLSearchParams();
  for(const k of ['left','right','filter','era'])if(state[k]!==defaults[k])q.set(k,state[k]);
  if(!state.guides)q.set('guides','0');if(state.uncertain)q.set('uncertain','1');
  return q.size?'?'+q.toString():'';
}
export function matches(obj,filter,includeUncertain=false) {
  const required={all:[],beaks:['beak'],round:['beak','round'],relation:['beak','reach','round','relation'],pairs:['beak','pair']}[filter]||[];
  return required.every(id=>obj.observations[id]?.state==='present'||
    (includeUncertain&&obj.observations[id]?.state==='uncertain'));
}
export function filterObjects(data,state) {
  return data.objects.filter(o=>matches(o,state.filter,state.uncertain));
}
export function yearLabel(year) { return year<0?`${Math.abs(year).toLocaleString('en-US')} BCE`:`${year} CE`; }
export function escapeHTML(value) {
  return String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}
