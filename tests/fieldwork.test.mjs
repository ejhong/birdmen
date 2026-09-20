import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {defaults, readState, stateURL, matches, filterObjects, yearLabel, escapeHTML} from '../docs/fieldwork-model.mjs';

const data = JSON.parse(readFileSync(new URL('../research/pillar-moai/fieldwork/register.json', import.meta.url)));
const object = id => data.objects.find(o => o.id === id);

test('shared comparisons retain choices and reject unknown URL values', () => {
  const state = {...defaults, left:'met-322614', right:'rn-hoa', guides:false,
    filter:'relation', uncertain:true, era:'recent'};
  assert.deepEqual(readState(stateURL(state), data), state);
  assert.deepEqual(readState('?left=missing&right=%3Cscript%3E&filter=all-cultures&era=0&uncertain=true', data), defaults);
});

test('a relation filter preserves the moai and cone uncertainties', () => {
  const strict = filterObjects(data, {...defaults, filter:'relation'}).map(o=>o.id);
  const possible = filterObjects(data, {...defaults, filter:'relation', uncertain:true}).map(o=>o.id);
  assert.deepEqual(strict, ['gt-p43','rn-boulder']);
  assert.deepEqual(possible, ['gt-p43','rn-boulder','rn-hoa','met-322614']);
  assert.equal(matches(object('met-321613'), 'relation', true), false, 'Missing arms cannot become a relation');
});

test('nearby circles and human variants do not complete a beaked figure bundle', () => {
  assert.equal(matches(object('met-243746'), 'round', true), false, 'Suspension hole is not a depicted round object');
  assert.equal(matches(object('met-322486'), 'relation', true), false, 'A human cone-holder is a useful alternative, not a beaked figure');
  assert.equal(matches(object('met-329907'), 'relation', true), false, 'A beaked figure does not borrow a cone from another object');
  assert.equal(matches(object('met-544093'), 'round', true), false, 'The feather has its own form');
});

test('paired scenes and per-view absence stay distinct', () => {
  assert.deepEqual(filterObjects(data, {...defaults, filter:'pairs'}).map(o=>o.id), ['rn-hoa','rn-mapse-1312']);
  assert.equal(object('gt-p33').observations.round.state, 'not-seen');
  assert.equal(object('met-321613').observations.round.state, 'unresolved');
  assert.equal(filterObjects(data, defaults).length, 22);
});

test('dates and source text render without markup injection', () => {
  assert.equal(yearLabel(-883), '883 BCE');
  assert.equal(yearLabel(1914), '1914 CE');
  assert.equal(escapeHTML('<img src="x" onerror=\'x\'>&'), '&lt;img src=&quot;x&quot; onerror=&#39;x&#39;&gt;&amp;');
});
