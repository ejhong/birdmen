import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readWaterState,classifyElevation,decodeGrid} from '../docs/submerged-model.mjs';

const grids=[{id:'world'},{id:'northsea'}];
test('shared depth views retain zero and recover safely from malformed URLs',()=>{
  assert.deepEqual(readWaterState('?region=northsea&depth=0',grids),{region:'northsea',depth:0});
  assert.deepEqual(readWaterState('?region=missing&depth=NaN',grids),{region:'world',depth:60});
  assert.equal(readWaterState('?depth=',grids).depth,60);
  assert.equal(readWaterState('?depth=999',grids).depth,120);
  assert.equal(readWaterState('?depth=-80',grids).depth,0);
  assert.equal(readWaterState('?depth=34',grids).depth,35);
});
test('the depth screen separates modern land, shelf, deeper water and missing data',()=>{
  assert.equal(classifyElevation(0,60),'land');
  assert.equal(classifyElevation(200,60),'land');
  assert.equal(classifyElevation(-60,60),'shelf');
  assert.equal(classifyElevation(-61,60),'water');
  assert.equal(classifyElevation(-1,0),'water');
  assert.equal(classifyElevation(32767,60),'missing');
  assert.equal(classifyElevation(NaN,60),'missing');
  assert.equal(classifyElevation(-32768,60,-32768),'missing');
});
test('retained grid bytes decode as signed little-endian values; truncation is rejected',()=>{
  const bytes=Uint8Array.from([0,0,196,255,232,3,255,127]);
  assert.deepEqual([...decodeGrid(bytes.buffer,{width:2,height:2})],[0,-60,1000,32767]);
  assert.throws(()=>decodeGrid(bytes.buffer,{width:3,height:2}),/dimensions/);
});
