import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {defaults,readState,stateURL,makeIndex,filterClaims,filterFamilies,hasRecordedBundle,dateOverlaps,culturalEdges,clusters,escapeHTML} from '../docs/catalogue-model.mjs';
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
  assert.equal(invalid.culture,'');assert.equal(invalid.from,'');assert.equal(invalid.view,'families');assert.equal(invalid.controls,false);
});
test('cultural edges preserve group relationships and deduplicate nested comparison families',()=>{
  const edges=culturalEdges(filterClaims(data,defaults,idx));
  const edge=edges.find(e=>e.a==='neolithic-anatolia'&&e.b==='rapanui');
  assert.ok(edge.claims.includes('bird-and-disc'));
  assert.ok(edge.claims.includes('birdmen-worlds'));
  assert.equal(edge.claims.length,4);assert.equal(edge.families.length,3);
});
test('the published cluster index matches the browser model exactly',async()=>{
  const published=JSON.parse(await readFile(new URL('../docs/data/clusters.json',import.meta.url),'utf8'));
  assert.deepEqual(published.clusters,clusters(filterClaims(data,defaults,idx),data,idx));
  const top=published.clusters[0];
  assert.equal(top.id,'neolithic-anatolia--rapanui');
  // A subcomparison shares its parent's line; it is never counted as separate evidence.
  assert.equal(top.threads.length,4);
  assert.equal(top.lines.length,3);
  assert.deepEqual(top.lines[0],{root:'birdmen-worlds',children:['bird-and-disc']});
  assert.equal(top.open,3);
  assert.ok(published.clusters.every(c=>c.a<c.b));
});
test('filters narrow the clusters, and controls never become comparison lines',()=>{
  const birds=clusters(filterClaims(data,{...defaults,motif:'bodies'},idx),data,idx);
  assert.ok(!birds.some(c=>c.lines.some(l=>l.root==='birdmen-worlds')));
  const withControls=clusters(filterClaims(data,{...defaults,controls:true},idx),data,idx);
  assert.deepEqual(withControls.map(c=>c.id),clusters(filterClaims(data,defaults,idx),data,idx).map(c=>c.id));
  assert.equal(clusters(filterClaims(data,{...defaults,culture:'delphi',with:'olmec'},idx),data,idx).length,0);
});
test('untrusted source text is rendered as text',()=>{
  assert.equal(escapeHTML('<img src=x onerror="alert(1)">'), '&lt;img src=x onerror=&quot;alert(1)&quot;&gt;');
});
test('families span many cultures and retain unresolved input leads without inventing cultures',()=>{
  const all=filterFamilies(data,defaults,idx);
  assert.equal(all.length,data.families.length);
  assert.ok(all.some(f=>f.id==='animal-on-human'));
  assert.ok(filterFamilies(data,{...defaults,q:'San Agustin'},idx).some(f=>f.id==='animal-on-human'));
  assert.ok(!filterFamilies(data,{...defaults,q:'San Agustin',culture:'neolithic-anatolia'},idx).some(f=>f.id==='animal-on-human'));
  const selected=filterFamilies(data,{...defaults,culture:'rapanui',with:'assyria'},idx);
  assert.ok(selected.some(f=>f.id==='bird-figures'));
  assert.ok(!filterFamilies(data,{...defaults,unknown:false},idx).some(f=>f.id==='animal-on-human'));
});
test('bundle membership needs one explicit observation scope, not culture or claim tag unions',()=>{
  assert.equal(hasRecordedBundle(data,'bird-round-form','pillar43',['bird','round','wing']),true);
  assert.equal(hasRecordedBundle(data,'bird-round-form','hoa-back',['bird','hand']),false);
  assert.equal(hasRecordedBundle(data,'handled-forms','pillar43',['arched','held']),false);
  assert.equal(hasRecordedBundle(data,'teaching-figures','bochica',['teaching']),false);
  assert.equal(hasRecordedBundle(data,'teaching-figures','bochica',['teaching'],{provisional:true}),true);
  const split={attestations:[{family:'f',entity:'e',features:['bird'],status:'documented'}, {family:'f',entity:'e',features:['disc'],status:'documented'}]};
  assert.equal(hasRecordedBundle(split,'f','e',['bird','disc']),false);
});
test('family date filtering uses the selected carving episode, not an older object date',()=>{
  const fixture=structuredClone(data);
  fixture.families=fixture.families.filter(f=>f.id==='bird-round-form');
  fixture.leads=[];
  fixture.attestations=[{family:'bird-round-form',entity:'hoa-back',features:['bird'],status:'documented',date_indices:[0]}];
  fixture.entities.find(e=>e.id==='hoa-back').dates=[{start:1700,end:1800},{start:-9500,end:-9000}];
  assert.deepEqual(filterFamilies(fixture,{...defaults,from:'-10000',to:'-8000',unknown:false}),[]);
});
test('context and modern reception leads do not silently enter the anomaly search',()=>{
  assert.equal(filterFamilies(data,{...defaults,q:'Sydney'},idx).length,0);
  assert.ok(filterFamilies(data,{...defaults,q:'Sydney',controls:true},idx).some(f=>f.id==='paired-flankers'));
});
