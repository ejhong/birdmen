import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {defaults,readState,stateURL,makeIndex,filterClaims,dateOverlaps,culturalEdges,escapeHTML} from '../docs/catalogue-model.mjs';
const data=JSON.parse(await readFile(new URL('../research/catalogue/catalogue.json',import.meta.url),'utf8'));
const idx=makeIndex(data);
test('controls stay optional and filters combine across culture, motif and region',()=>{
  const all=filterClaims(data,defaults,idx);
  assert.ok(all.every(c=>c.kind==='claim'));
  assert.equal(filterClaims(data,{...defaults,controls:true},idx).length,data.claims.length);
  const both=filterClaims(data,{...defaults,culture:'rapanui',with:'neolithic-anatolia',motif:'bodies'},idx);
  assert.deepEqual(both.map(c=>c.id),['hands-across-torsos','ribs-across-oceans']);
  assert.equal(filterClaims(data,{...defaults,culture:'rapanui',region:'North Africa'},idx).length,0);
});
test('search handles accents and searches actual authors, not just website hosts',()=>{
  assert.ok(filterClaims(data,{...defaults,q:'gobekli'},idx).some(c=>c.id==='birdmen-worlds'));
  assert.ok(filterClaims(data,{...defaults,q:'Lee Paqui'},idx).some(c=>c.id==='ribs-across-oceans'));
  assert.equal(filterClaims(data,{...defaults,q:'<script>unlikely'},idx).length,0);
});
test('unknown dates never become zero; date match does not imply both sides coexist',()=>{
  assert.equal(dateOverlaps({start:null,end:null},-100,100),false);
  assert.equal(dateOverlaps({start:-100,end:-50},-50,10),true);
  assert.equal(dateOverlaps({start:100,end:200},-100,-1),false);
  const early=filterClaims(data,{...defaults,from:'-10000',to:'-8001',unknown:false},idx);
  assert.ok(early.some(c=>c.id==='birdmen-worlds'));
  assert.ok(!early.some(c=>c.id==='ribs-across-oceans'));
  assert.ok(filterClaims(data,{...defaults,from:'-10000',to:'-8001',unknown:true},idx).some(c=>c.id==='ribs-across-oceans'));
  assert.deepEqual(filterClaims(data,{...defaults,from:'1000',to:'-1000'},idx),[]);
});
test('shareable state preserves selection, booleans and date ranges; invalid IDs are removed',()=>{
  const state={...defaults,culture:'rapanui',with:'neolithic-anatolia',view:'time',focus:'birdmen-worlds',unknown:false,controls:true,from:'-10000',q:'bird & disc',scale:'recent'};
  assert.deepEqual(readState(stateURL(state),data),state);
  const invalid=readState('?culture=missing&view=script&from=0&controls=false&with=missing&focus=missing',data);
  assert.equal(invalid.culture,'');assert.equal(invalid.from,'');assert.equal(invalid.view,'gallery');assert.equal(invalid.controls,false);
});
test('cultural edges preserve group relationships and deduplicate nested comparison families',()=>{
  const edges=culturalEdges(filterClaims(data,defaults,idx));
  const edge=edges.find(e=>e.a==='neolithic-anatolia'&&e.b==='rapanui');
  assert.ok(edge.claims.includes('bird-and-disc'));
  assert.ok(edge.claims.includes('birdmen-worlds'));
  assert.equal(edge.claims.length,4);assert.equal(edge.families.length,3);
});
test('untrusted source text is rendered as text',()=>{
  assert.equal(escapeHTML('<img src=x onerror="alert(1)">'), '&lt;img src=x onerror=&quot;alert(1)&quot;&gt;');
});
