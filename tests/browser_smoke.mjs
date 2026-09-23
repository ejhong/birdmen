/**
 * Dependency-free browser checks (Node 22+). Start the local site server first.
 * BIRDMEN_SITE_URL: default http://127.0.0.1:4173/
 * BIRDMEN_CHROME: Chrome/Chromium executable; macOS Chrome is the default on macOS.
 * BIRDMEN_SCREENSHOTS: optional output directory; otherwise a unique temporary folder.
 * Uses an isolated temporary browser profile, never a personal browsing session.
 */
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {mkdtemp, mkdir, writeFile} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';

const base = new URL(process.env.BIRDMEN_SITE_URL || 'http://127.0.0.1:4173/');
const executable = process.env.BIRDMEN_CHROME || (process.platform === 'darwin'
  ? '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' : 'chromium');
const workspace = await mkdtemp(join(tmpdir(), 'birdmen-browser-'));
const screenshots = process.env.BIRDMEN_SCREENSHOTS || workspace;
await mkdir(screenshots, {recursive: true});
const browser = spawn(executable, [
  '--headless', '--disable-gpu', '--no-first-run', '--no-default-browser-check',
  '--disable-background-networking', '--disable-extensions', '--remote-debugging-port=0',
  `--user-data-dir=${join(workspace, 'profile')}`, 'about:blank'
], {stdio: ['ignore', 'ignore', 'pipe']});

class CDP {
  constructor(socket) {
    this.socket = socket;
    this.sequence = 0;
    this.pending = new Map();
    this.events = [];
    socket.addEventListener('message', ({data}) => {
      const message = JSON.parse(data);
      if (!message.id) { this.events.push(message); return; }
      const pending = this.pending.get(message.id);
      if (!pending) return;
      clearTimeout(pending.timer);
      this.pending.delete(message.id);
      if (message.error) pending.reject(new Error(`${pending.method}: ${JSON.stringify(message.error)}`));
      else pending.resolve(message.result);
    });
  }
  static async connect(url) {
    const socket = new WebSocket(url);
    await new Promise((resolve, reject) => {
      socket.addEventListener('open', resolve, {once: true});
      socket.addEventListener('error', reject, {once: true});
    });
    return new CDP(socket);
  }
  send(method, params = {}) {
    const id = ++this.sequence;
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        this.pending.delete(id);
        reject(new Error(`Timed out: ${method}`));
      }, 15000);
      this.pending.set(id, {resolve, reject, timer, method});
      this.socket.send(JSON.stringify({id, method, params}));
    });
  }
  async evaluate(expression) {
    const result = await this.send('Runtime.evaluate', {expression, returnByValue: true, awaitPromise: true});
    if (result.exceptionDetails) throw new Error(JSON.stringify(result.exceptionDetails));
    return result.result.value;
  }
  close() { this.socket.close(); }
}

let client;
let browserClient;
try {
  const endpoint = await new Promise((resolve, reject) => {
    let output = '';
    const timer = setTimeout(() => reject(new Error(`Chrome did not start: ${output.slice(-2000)}`)), 15000);
    const fail = error => { clearTimeout(timer); reject(error); };
    browser.once('error', fail);
    browser.once('exit', code => fail(new Error(`Chrome exited ${code}: ${output.slice(-2000)}`)));
    browser.stderr.on('data', chunk => {
      output += chunk;
      const match = output.match(/DevTools listening on (ws:\/\/[^\s]+)/);
      if (match) { clearTimeout(timer); resolve(match[1]); }
    });
  });
  const debuggerOrigin = new URL(endpoint);
  browserClient = await CDP.connect(endpoint);
  const {targetId} = await browserClient.send('Target.createTarget', {url: 'about:blank'});
  const targets = await (await fetch(`http://${debuggerOrigin.host}/json/list`)).json();
  client = await CDP.connect(targets.find(target => target.id === targetId).webSocketDebuggerUrl);
  await client.send('Page.enable');
  await client.send('Runtime.enable');
  await client.send('Network.enable');
  await client.send('Emulation.setEmulatedMedia', {features: [{name: 'prefers-reduced-motion', value: 'reduce'}]});

  async function poll(check, description) {
    const deadline = Date.now() + 12000;
    do {
      try {
        if (await check()) return;
      } catch (error) {
        // Redirects can replace a document between two CDP messages. Retry only
        // those transient contexts; ordinary script and protocol errors fail.
        if (!/Execution context was destroyed|Cannot find context with specified id|Inspected target navigated or closed/.test(error.message)) throw error;
      }
      await new Promise(resolve => setTimeout(resolve, 100));
    } while (Date.now() < deadline);
    throw new Error(`Page condition did not resolve: ${description}`);
  }
  async function waitFor(expression) {
    await poll(() => client.evaluate(expression), expression);
  }
  async function navigate(path, width = 1440, height = 1050) {
    await client.send('Emulation.setDeviceMetricsOverride', {width, height, deviceScaleFactor: 1, mobile: false});
    const firstEvent = client.events.length;
    const navigation = await client.send('Page.navigate', {url: new URL(path, base).href});
    assert.ok(!navigation.errorText, `${path}: ${navigation.errorText}`);
    if (navigation.loaderId) {
      // Do not mistake the outgoing document's readyState for the new page.
      await poll(() => client.events.slice(firstEvent).some(event =>
        event.method === 'Page.frameNavigated' && event.params.frame.id === navigation.frameId &&
        event.params.frame.loaderId === navigation.loaderId), `${path}: navigation committed`);
    }
    await waitFor(`document.readyState === 'complete'`);
    await waitFor(`document.readyState === 'complete' && Promise.race([document.fonts.ready, new Promise(resolve => setTimeout(resolve, 2500))]).then(() => true)`);
    assert.ok(await client.evaluate(`document.documentElement.scrollWidth <= innerWidth + 1`), `${path}: horizontal page overflow at ${width}px`);
  }
  async function screenshot(name, full = false) {
    const {data} = await client.send('Page.captureScreenshot', {format: 'png', captureBeyondViewport: full,
      ...(full ? {clip: {...await client.evaluate(`({x:0,y:0,width:innerWidth,height:Math.min(document.documentElement.scrollHeight,16000)})`), scale: 1}} : {})});
    await writeFile(join(screenshots, name), Buffer.from(data, 'base64'));
  }

  await navigate('submerged.html?region=northsea&depth=30');
  await waitFor(`document.body.dataset.waterReady==='true' && document.querySelector('#water-status').textContent.includes('North Sea')`);
  assert.equal(await client.evaluate(`document.querySelectorAll('.water-project').length`),6);
  assert.equal(await client.evaluate(`document.querySelectorAll('.water-dataset').length`),7);
  assert.equal(await client.evaluate(`document.querySelector('#modern-canvas').width`),381);
  assert.equal(await client.evaluate(`document.querySelector('#water-depth').value`),'30');
  await screenshot('submerged-desktop.png');
  await client.evaluate(`document.querySelector('#landscape').scrollIntoView(); document.querySelector('#water-depth').value=0; document.querySelector('#water-depth').dispatchEvent(new Event('input'))`);
  assert.ok(await client.evaluate(`document.querySelector('#modern-canvas').toDataURL()===document.querySelector('#depth-canvas').toDataURL()`),'Zero depth must match the modern elevation baseline');
  await client.evaluate(`document.querySelector('#water-depth').value=60; document.querySelector('#water-depth').dispatchEvent(new Event('input'))`);
  assert.ok(await client.evaluate(`document.querySelector('#modern-canvas').toDataURL()!==document.querySelector('#depth-canvas').toDataURL()`),'A depth change must change the map');
  assert.equal(await client.evaluate(`new URLSearchParams(location.search).get('depth')`),'60');
  assert.equal(await client.evaluate(`document.querySelectorAll('.water-project-locations a:not([hidden])').length`),2);
  await screenshot('submerged-northsea-desktop.png');
  await client.evaluate(`document.querySelector('[data-water-region=sunda]').click()`);
  await waitFor(`document.querySelector('#water-status').textContent.includes('Sunda shelf ·')`);
  assert.equal(await client.evaluate(`document.querySelector('#modern-canvas').width`),261);
  await client.evaluate(`history.back()`);
  await waitFor(`document.querySelector('#water-status').textContent.includes('North Sea ·')`);
  assert.equal(await client.evaluate(`document.querySelector('#water-depth').value`),'60');
  await navigate('submerged.html?region=world&depth=90',390,844);
  await waitFor(`document.body.dataset.waterReady==='true'`);
  await screenshot('submerged-mobile.png');
  await client.evaluate(`document.querySelector('#landscape').scrollIntoView()`);
  assert.ok(await client.evaluate(`document.documentElement.scrollWidth<=innerWidth+1`));
  await screenshot('submerged-map-mobile.png');
  await client.evaluate(`document.querySelector('[data-water-region=khambhat]').click()`);
  await waitFor(`document.querySelector('#water-status').textContent.includes('Gujarat / Khambhat ·')`);
  assert.equal(await client.evaluate(`document.querySelector('#modern-canvas').width`),181);
  await client.evaluate(`document.querySelector('#projects').scrollIntoView()`);
  await screenshot('submerged-projects-mobile.png');
  await client.send('Network.setBlockedURLs',{urls:['*data/submerged/northsea.i16']});
  await navigate('submerged.html?region=northsea');
  await waitFor(`document.body.dataset.waterReady==='fallback'`);
  assert.ok(await client.evaluate(`!document.querySelector('#depth-fallback').hidden && document.querySelector('#scenario-title').textContent.includes('static world fallback')`));
  await client.send('Network.setBlockedURLs',{urls:[]});

  await navigate('catalogue.html');
  await waitFor(`document.body.classList.contains('catalogue-ready')`);
  assert.equal(await client.evaluate(`document.body.dataset.catalogueView`), 'families');
  assert.equal(await client.evaluate(`document.querySelectorAll('.family-card:not([hidden])').length`),19);
  await waitFor(`[...document.querySelectorAll('.feature-visual img')].every(image => image.complete && image.naturalWidth > 0)`);
  await screenshot('catalogue-desktop.png');
  await client.evaluate(`document.querySelector('#explore').scrollIntoView()`);
  await waitFor(`[...document.querySelectorAll('.family-card:not([hidden]) img')].slice(0,4).every(image=>image.complete&&image.naturalWidth>0)`);
  await screenshot('catalogue-families-desktop.png');
  await client.evaluate(`document.querySelector('[data-view=gallery]').click()`);
  assert.equal(await client.evaluate(`document.querySelectorAll('.catalogue-card:not([hidden])').length`),20);
  await waitFor(`[...document.querySelectorAll('.catalogue-card:not([hidden]) img')].slice(0,6).every(image=>image.complete&&image.naturalWidth>0)`);
  await screenshot('catalogue-gallery-desktop.png');
  await client.evaluate(`document.querySelector('#more-filters').click(); document.querySelector('#culture').value='neolithic-anatolia'; document.querySelector('#culture').dispatchEvent(new Event('input',{bubbles:true})); document.querySelector('#with-culture').value='rapanui'; document.querySelector('#with-culture').dispatchEvent(new Event('input',{bubbles:true}));`);
  assert.equal(await client.evaluate(`document.querySelectorAll('.catalogue-card:not([hidden])').length`), 4);
  await client.evaluate(`document.querySelector('[data-view=cultures]').click()`);
  assert.equal(await client.evaluate(`document.querySelectorAll('#cultures-view .cluster-row').length`),1);
  assert.ok(await client.evaluate(`document.querySelector('#cultures-view .cluster-copy h3').textContent.includes('Rapanui')`));
  assert.ok(await client.evaluate(`document.querySelector('#cultures-view .cluster-foot').textContent.includes('3 lines of comparison')`));
  assert.equal(await client.evaluate(`document.querySelectorAll('#cultures-view .cluster-ledger li').length`),3);
  await waitFor(`[...document.querySelectorAll('#cultures-view .plate img')].every(image=>image.complete&&image.naturalWidth>0)`);
  await screenshot('catalogue-clusters-desktop.png');
  await client.evaluate(`document.querySelector('[data-view=map]').click()`);
  await waitFor(`!!document.querySelector('#map-view svg')`);
  assert.ok(await client.evaluate(`document.querySelectorAll('.map-connection').length > 0`));
  await screenshot('catalogue-map-desktop.png');
  await client.evaluate(`document.querySelector('[data-view=time]').click()`);
  assert.ok(await client.evaluate(`document.querySelectorAll('.time-row').length >= 6`));
  assert.ok(await client.evaluate(`document.querySelector('.time-table').textContent.includes('Later birdman carving episode')`));
  await screenshot('catalogue-time-desktop.png');
  await client.evaluate(`document.querySelector('[data-scale=recent]').click(); history.back()`);
  await waitFor(`document.querySelector('[data-scale=all]').getAttribute('aria-pressed')==='true'`);
  await client.evaluate(`document.querySelector('#reset-filters').click(); document.querySelector('#search').value='impossible-collection-xyz'; document.querySelector('#search').dispatchEvent(new Event('input',{bubbles:true}))`);
  await waitFor(`!document.querySelector('#empty-state').hidden`);
  await client.evaluate(`document.querySelector('#empty-reset').click(); document.querySelector('#controls').click()`);
  assert.equal(await client.evaluate(`document.querySelectorAll('.catalogue-card:not([hidden])').length`), 24);
  await navigate('catalogue.html?view=gallery&culture=rapanui&with=neolithic-anatolia',390,844);
  await waitFor(`document.body.classList.contains('catalogue-ready')`);
  assert.equal(await client.evaluate(`document.querySelectorAll('.catalogue-card:not([hidden])').length`),4);
  assert.ok(await client.evaluate(`getComputedStyle(document.querySelector('nav a[href="submerged.html"]')).display!=='none'`));
  await client.evaluate(`document.querySelector('.catalogue-card:not([hidden]) .card-link').click()`);
  await waitFor(`!!document.querySelector('.back-link') && document.querySelector('.back-link').textContent.includes('your collection')`);
  await client.evaluate(`document.querySelector('.back-link').click()`);
  await waitFor(`document.body.classList.contains('catalogue-ready')`);
  assert.equal(await client.evaluate(`document.querySelectorAll('.catalogue-card:not([hidden])').length`),4);
  await screenshot('catalogue-gallery-mobile.png');
  await client.evaluate(`document.querySelector('[data-view=cultures]').click()`);
  assert.ok(await client.evaluate(`document.documentElement.scrollWidth <= innerWidth+1`));
  await screenshot('catalogue-clusters-mobile.png');
  await client.evaluate(`document.querySelector('[data-view=map]').click()`);
  await waitFor(`!!document.querySelector('#map-view svg')`);
  assert.ok(await client.evaluate(`document.documentElement.scrollWidth <= innerWidth+1`));
  await screenshot('catalogue-map-mobile.png');
  await client.evaluate(`document.querySelector('[data-view=time]').click()`);
  assert.ok(await client.evaluate(`document.documentElement.scrollWidth <= innerWidth+1`));
  await screenshot('catalogue-time-mobile.png');
  await navigate('corpus.html');
  assert.equal(await client.evaluate(`document.querySelectorAll('.wall').length`),2);
  assert.equal(await client.evaluate(`document.querySelectorAll('.wall-item').length`),72);
  await waitFor(`[...document.querySelectorAll('.wall-item img')].slice(0,12).every(i=>i.complete&&i.naturalWidth>0)`);
  await screenshot('corpus-desktop.png');
  // Filtering highlights and never removes: every stone stays on the wall.
  await client.evaluate(`document.querySelector('[data-feature=bird]').click()`);
  assert.equal(await client.evaluate(`document.querySelectorAll('.wall-item').length`),72);
  assert.ok(await client.evaluate(`document.querySelectorAll('.wall-item.is-hit').length>0`));
  assert.ok(await client.evaluate(`document.querySelectorAll('.wall-item.is-dim').length>0`));
  assert.ok(await client.evaluate(`document.querySelector('#wall-readout').textContent.includes('Neolithic Anatolia')`));
  await client.evaluate(`document.querySelector('[data-feature=round]').click()`);
  assert.equal(await client.evaluate(`[...document.querySelectorAll('.wall[data-corpus=anatolia] .wall-item.is-hit')].length`),3);
  await screenshot('corpus-filtered-desktop.png');
  await client.evaluate(`document.querySelector('#wall-reset').click()`);
  assert.equal(await client.evaluate(`document.querySelectorAll('.wall-item.is-dim').length`),0);
  await navigate('corpus.html',390,844);
  assert.ok(await client.evaluate(`document.documentElement.scrollWidth <= innerWidth+1`));
  await screenshot('corpus-mobile.png');
  await navigate('clusters.html');
  assert.equal(await client.evaluate(`document.querySelectorAll('.cluster-list .cluster-row').length`),23);
  assert.ok(await client.evaluate(`document.querySelector('.cluster-row .cluster-link').getAttribute('href')==='clusters/neolithic-anatolia--rapanui.html'`));
  assert.equal(await client.evaluate(`document.querySelectorAll('.cluster-matrix tbody tr').length`),21);
  assert.ok(await client.evaluate(`document.querySelectorAll('.matrix-cell').length===46`));
  await waitFor(`[...document.querySelectorAll('.flagship-plates img')].every(image=>image.complete&&image.naturalWidth>0)`);
  await screenshot('clusters-desktop.png');
  await navigate('clusters.html',390,844);
  assert.ok(await client.evaluate(`document.documentElement.scrollWidth <= innerWidth+1`));
  await screenshot('clusters-mobile.png');
  await navigate('clusters/neolithic-anatolia--rapanui.html');
  assert.equal(await client.evaluate(`document.querySelectorAll('.cluster-line').length`),3);
  assert.ok(await client.evaluate(`document.querySelector('.line-children').textContent.includes('not as separate evidence')`));
  await waitFor(`[...document.querySelectorAll('.line-plates img')].every(image=>image.complete&&image.naturalWidth>0)`);
  await screenshot('cluster-dossier-desktop.png');
  await navigate('clusters/neolithic-anatolia--rapanui.html',390,844);
  await screenshot('cluster-dossier-mobile.png');
  await navigate('catalogue/birdmen-worlds.html');
  assert.equal(await client.evaluate(`document.querySelectorAll('.dossier-group').length`),2);
  assert.equal(await client.evaluate(`document.querySelectorAll('.group-member').length`),9);
  assert.equal(await client.evaluate(`document.querySelectorAll('.alternate-views').length`),2);
  await client.evaluate(`document.querySelector('.alternate-views').open=true`);
  await waitFor(`document.querySelector('.alternate-views img').complete && document.querySelector('.alternate-views img').naturalWidth>0`);
  await screenshot('catalogue-dossier-desktop.png');
  await navigate('catalogue/birdmen-worlds.html',390,844);
  await screenshot('catalogue-dossier-mobile.png');
  await navigate('catalogue.html?view=themes',390,844);
  await waitFor(`document.body.classList.contains('catalogue-ready')`);
  assert.ok(await client.evaluate(`document.querySelectorAll('.theme-card').length >= 9`));
  await navigate('catalogue.html?q=San+Agustin',390,844);
  await waitFor(`document.body.classList.contains('catalogue-ready')`);
  assert.equal(await client.evaluate(`document.querySelectorAll('.family-card:not([hidden])').length`),1);
  await client.evaluate(`document.querySelector('#explore').scrollIntoView()`);
  await screenshot('catalogue-family-search-mobile.png');
  await client.evaluate(`document.querySelector('.family-card:not([hidden]) .family-link').click()`);
  await waitFor(`document.querySelector('.back-link')?.textContent.includes('your collection')`);
  await client.evaluate(`document.querySelector('.back-link').click()`);
  await waitFor(`document.body.classList.contains('catalogue-ready')`);
  assert.equal(await client.evaluate(`document.querySelector('#search').value`),'San Agustin');
  await navigate('families/bird-figures.html');
  assert.ok(await client.evaluate(`document.querySelectorAll('.family-culture').length > 3`));
  await screenshot('motif-family-desktop.png');
  await navigate('families/bird-round-form.html',390,844);
  await client.evaluate(`document.querySelector('.family-matrix').open=true`);
  assert.equal(await client.evaluate(`document.querySelectorAll('.family-member').length`),3);
  assert.ok(await client.evaluate(`document.documentElement.scrollWidth<=innerWidth+1`));
  await screenshot('motif-family-mobile.png');
  await navigate('families/enclosing-creature.html',390,844);
  await client.evaluate(`document.querySelector('.intake-lead details').open=true; document.querySelector('.intake-lead').scrollIntoView()`);
  await waitFor(`document.querySelector('.intake-images img').complete&&document.querySelector('.intake-images img').naturalWidth>0`);
  await screenshot('input-correction-mobile.png');
  await navigate('input-audit.html');
  await client.evaluate(`document.querySelector('.coverage-register').open=true`);
  assert.equal(await client.evaluate(`document.querySelectorAll('.coverage-register tbody tr').length`),68);
  await screenshot('input-audit-desktop.png');
  await navigate('fieldwork.html');
  await waitFor(`document.body.dataset.fieldworkReady==='true'`);
  assert.equal(await client.evaluate(`document.querySelectorAll('.fw-card:not([hidden])').length`),22);
  await waitFor(`[...document.querySelectorAll('.fw-comparison img')].every(im=>im.complete&&im.naturalWidth>0)`);
  await screenshot('fieldwork-desktop.png');
  await client.evaluate(`document.querySelector('#compare').scrollIntoView();document.querySelector('[data-preset=moai]').click()`);
  await waitFor(`document.querySelector('#panel-right img').complete&&document.querySelector('#panel-right img').naturalWidth>0`);
  assert.equal(await client.evaluate(`document.querySelector('#select-right').value`),'rn-hoa');
  assert.ok(await client.evaluate(`document.querySelector('#panel-right').textContent.includes('egg')`));
  assert.equal(await client.evaluate(`document.querySelectorAll('#comparison-matrix .uncertain').length`),2);
  assert.ok(await client.evaluate(`[...document.querySelectorAll('.fw-comparison .fw-image-plane')].every(plane=>{const im=plane.querySelector('img'),svg=plane.querySelector('svg'),a=im.getBoundingClientRect(),b=svg.getBoundingClientRect();return Math.abs(a.width/a.height-im.naturalWidth/im.naturalHeight)<.002&&Math.abs(a.x-b.x)<1&&Math.abs(a.y-b.y)<1&&Math.abs(a.height-b.height)<1;})`),'Annotation regions must stay aligned with original image proportions');
  await screenshot('fieldwork-moai-desktop.png');
  await client.evaluate(`document.querySelector('#show-guides').click()`);
  assert.ok(await client.evaluate(`getComputedStyle(document.querySelector('.fw-overlay')).display==='none'`));
  await client.evaluate(`document.querySelector('[data-side=right]').click()`);
  assert.ok(await client.evaluate(`document.querySelector('#photo-dialog').open`));
  await client.send('Input.dispatchKeyEvent',{type:'keyDown',key:'Escape',code:'Escape',windowsVirtualKeyCode:27});
  await client.send('Input.dispatchKeyEvent',{type:'keyUp',key:'Escape',code:'Escape',windowsVirtualKeyCode:27});
  await waitFor(`!document.querySelector('#photo-dialog').open`);
  await client.evaluate(`document.querySelector('#motif-filter').value='relation';document.querySelector('#motif-filter').dispatchEvent(new Event('change',{bubbles:true}))`);
  assert.equal(await client.evaluate(`document.querySelectorAll('.fw-card:not([hidden])').length`),2);
  await client.evaluate(`document.querySelector('#include-uncertain').click()`);
  assert.equal(await client.evaluate(`document.querySelectorAll('.fw-card:not([hidden])').length`),4);
  await client.evaluate(`history.back()`);
  await waitFor(`document.querySelectorAll('.fw-card:not([hidden])').length===2`);
  await client.evaluate(`history.forward()`);
  await waitFor(`document.querySelectorAll('.fw-card:not([hidden])').length===4`);
  const comparisonURL=await client.evaluate(`location.href`);
  await navigate(comparisonURL);
  await waitFor(`document.body.dataset.fieldworkReady==='true'`);
  assert.equal(await client.evaluate(`document.querySelectorAll('.fw-card:not([hidden])').length`),4);
  assert.equal(await client.evaluate(`document.querySelector('#select-right').value`),'rn-hoa');
  assert.ok(await client.evaluate(`document.body.classList.contains('fw-hide-guides')`));
  await client.evaluate(`document.querySelector('#collection').scrollIntoView()`);
  await waitFor(`[...document.querySelectorAll('.fw-card:not([hidden]) img')].every(im=>im.complete&&im.naturalWidth>0)`);
  await screenshot('fieldwork-relation-desktop.png');
  await client.evaluate(`document.querySelector('[data-choose="met-322614"]').click()`);
  assert.equal(await client.evaluate(`location.hash`),'#compare');
  assert.equal(await client.evaluate(`document.activeElement.id`),'select-right');
  assert.equal(await client.evaluate(`document.querySelector('#select-right').value`),'met-322614');
  await client.evaluate(`document.querySelector('#history').scrollIntoView()`);
  assert.equal(await client.evaluate(`document.querySelectorAll('#evidence-timeline svg a').length`),9);
  assert.equal(await client.evaluate(`document.querySelectorAll('#evidence-timeline a[href="#event-egypt"] rect').length`),4,'Separate object ranges must not become one continuous Egyptian sequence');
  assert.ok(await client.evaluate(`[...document.querySelectorAll('.fw-chart-label')].every(el=>el.getBBox().x+el.getBBox().width<290)`),'Chart labels must stay clear of the chronological axis');
  await screenshot('fieldwork-history-desktop.png');
  await client.evaluate(`document.querySelector('[data-era=recent]').click()`);
  assert.equal(await client.evaluate(`document.querySelectorAll('#evidence-timeline svg a').length`),7);
  await client.evaluate(`location.hash='source-pitts2014'`);
  await waitFor(`document.querySelector('.fw-sources').open`);
  await navigate('fieldwork.html?right=rn-hoa#compare',390,844);
  await waitFor(`document.body.dataset.fieldworkReady==='true'`);
  await waitFor(`[...document.querySelectorAll('.fw-comparison img')].every(im=>im.complete&&im.naturalWidth>0)`);
  await screenshot('fieldwork-compare-mobile.png');
  await client.evaluate(`document.querySelector('#panel-right').scrollIntoView()`);
  await screenshot('fieldwork-moai-mobile.png');
  await client.evaluate(`document.querySelector('#collection').scrollIntoView()`);
  await screenshot('fieldwork-collection-mobile.png');
  await client.evaluate(`document.querySelector('#history').scrollIntoView()`);
  assert.ok(await client.evaluate(`document.documentElement.scrollWidth<=innerWidth+1`));
  assert.ok(await client.evaluate(`document.querySelector('#evidence-timeline').scrollWidth<=document.querySelector('#evidence-timeline').clientWidth+1`),'The mobile timeline must show its complete date axis');
  await screenshot('fieldwork-history-mobile.png');
  await navigate('fieldwork.html?filter=relation#object-met-243744',390,844);
  await waitFor(`document.body.dataset.fieldworkReady==='true'`);
  assert.ok(await client.evaluate(`!document.querySelector('#object-met-243744').hidden`),'An object deep link must reveal a filtered-out record');
  await client.send('Network.setBlockedURLs',{urls:['*data/pillar-moai/fieldwork/register.json*']});
  await navigate('fieldwork.html',390,844);
  await waitFor(`document.body.dataset.fieldworkReady==='fallback'`);
  assert.equal(await client.evaluate(`document.querySelectorAll('.fw-card:not([hidden])').length`),22);
  assert.ok(await client.evaluate(`[...document.querySelectorAll('.fw-interactive')].every(el=>el.hidden)`));
  await client.send('Network.setBlockedURLs',{urls:[]});
  await navigate('bathymetry-lab.html');
  await client.evaluate(`document.querySelector('.survey-figure').scrollIntoView()`);
  await waitFor(`document.querySelector('.survey-figure img').complete&&document.querySelector('.survey-figure img').naturalWidth>0`);
  await screenshot('bathymetry-lab-desktop.png');
  await navigate('bathymetry-lab.html',390,844);
  await screenshot('bathymetry-lab-mobile.png');
  await navigate('signal-audit.html',390,844);
  assert.equal(await client.evaluate(`document.querySelectorAll('.signal-table tbody tr').length`),11);
  await screenshot('signal-audit-mobile.png');
  await navigate('index.html');
  assert.equal(await client.evaluate(`document.querySelectorAll('.investigation').length`), 5);
  assert.equal(await client.evaluate(`document.querySelectorAll('.cover-pair img').length`), 2);
  assert.equal(await client.evaluate(`document.querySelectorAll('.research-path').length`),2);
  await waitFor(`[...document.querySelectorAll('.cover-pair img')].every(image => image.complete && image.naturalWidth > 0)`);
  assert.ok(await client.evaluate(`getComputedStyle(document.body).fontFamily.includes('Newsreader')`));
  await screenshot('home-desktop.png');
  await client.evaluate(`document.querySelector('#programmes').scrollIntoView()`);
  await waitFor(`[...document.querySelectorAll('.research-path img')].every(image=>image.complete&&image.naturalWidth>0)`);
  assert.ok(await client.evaluate(`[...document.querySelectorAll('.path-objects img')].every(image=>image.getBoundingClientRect().height<=image.parentElement.getBoundingClientRect().height+1)`),'Homepage evidence photos must fit their panels');
  await screenshot('programmes-desktop.png');
  await client.evaluate(`document.querySelector('#investigations').scrollIntoView()`);
  await screenshot('investigations-desktop.png');
  await navigate('index.html', 390, 844);
  await screenshot('home-mobile.png');

  await navigate('pillar-and-moai.html');
  await waitFor(`[...document.querySelectorAll('.compare-panel img')].every(image => image.complete && image.naturalWidth > 0)`);
  await client.evaluate(`document.querySelector('#compare').scrollIntoView()`);
  await screenshot('case-desktop.png');
  for (const mode of ['alternate', 'boulder', 'archive', 'local', 'whole']) {
    await client.evaluate(`document.querySelector('#comparison-select').value = '${mode}'; document.querySelector('#comparison-select').dispatchEvent(new Event('change'));`);
    await waitFor(`[...document.querySelectorAll('.compare-panel img')].every(image => image.complete && image.naturalWidth > 0)`);
    assert.ok(await client.evaluate(`document.querySelector('#compare-note').textContent.length > 40`));
  }
  await client.evaluate(`document.querySelector('#zoom').value = 200; document.querySelector('#zoom').dispatchEvent(new Event('input')); document.querySelector('#show-annotations').click();`);
  assert.equal(await client.evaluate(`document.querySelector('#zoom-value').value`), '200%');
  assert.equal(await client.evaluate(`document.querySelector('#annotation-key').hidden`), false);
  assert.ok(await client.evaluate(`document.querySelectorAll('.marker:not([hidden])').length >= 4`));
  await client.evaluate(`document.querySelector('#sync-scroll').click(); document.querySelector('.compare-window').scrollTop = 250;`);
  await waitFor(`document.querySelectorAll('.compare-window')[1].scrollTop > 0`);
  await client.evaluate(`document.querySelector('#reset-view').click()`);
  assert.equal(await client.evaluate(`document.querySelector('#zoom-value').value`), '100%');
  assert.equal(await client.evaluate(`document.querySelector('.compare-window').scrollTop`), 0);
  await client.evaluate(`document.querySelector('[data-hyp="contact"]').click()`);
  assert.equal(await client.evaluate(`document.querySelector('#hyp-contact').hidden`), false);
  assert.equal(await client.evaluate(`document.querySelector('#hyp-inheritance').hidden`), true);
  await navigate('pillar-and-moai.html', 390, 844);
  await client.evaluate(`document.querySelector('#compare').scrollIntoView()`);
  await screenshot('case-mobile.png');
  await client.evaluate(`document.querySelector('#comparison-select').value = 'boulder'; document.querySelector('#comparison-select').dispatchEvent(new Event('change'));`);
  await waitFor(`[...document.querySelectorAll('.compare-panel img')].every(image => image.complete && image.naturalWidth > 0)`);
  await screenshot('boulder-mobile.png');

  await navigate('recognition.html');
  assert.equal(await client.evaluate(`document.querySelectorAll('.recognition-record').length`), 10);
  assert.ok(await client.evaluate(`document.querySelector('#results .lab-summary').textContent.includes('19 of 20')`));
  await client.evaluate(`document.querySelector('#result-boulder-1919').open = true; document.querySelector('#result-boulder-1919').scrollIntoView()`);
  await waitFor(`document.querySelector('#result-boulder-1919 img').complete && document.querySelector('#result-boulder-1919 img').naturalWidth > 0`);
  await client.evaluate(`document.querySelector('#result-boulder-1919 [data-box]').click()`);
  assert.equal(await client.evaluate(`document.querySelector('#result-boulder-1919 .model-box').hidden`), false);
  await screenshot('recognition-desktop.png');
  await client.evaluate(`document.querySelector('#result-boulder-1919 .clear-box').click()`);
  assert.equal(await client.evaluate(`document.querySelector('#result-boulder-1919 .model-box').hidden`), true);
  await navigate('recognition.html#result-hoa-back', 390, 844);
  await waitFor(`document.querySelector('#result-hoa-back').open`);
  await screenshot('recognition-mobile.png');
  await navigate('research-review.html', 390, 844);
  await screenshot('review-mobile.png');
  await navigate('local-context.html');
  await waitFor(`[...document.querySelectorAll('.context-gallery img')].every(image => image.complete && image.naturalWidth > 0)`);
  assert.equal(await client.evaluate(`document.querySelectorAll('.context-record').length`), 9);
  await client.evaluate(`document.querySelector('#neighbours').scrollIntoView()`);
  await screenshot('local-context-desktop.png');
  await navigate('local-context.html', 390, 844);
  await client.evaluate(`document.querySelector('#object-rn-mapse-1312').open = true; document.querySelector('#object-rn-mapse-1312').scrollIntoView()`);
  await screenshot('context-record-mobile.png');
  await navigate('view-trial.html');
  assert.equal(await client.evaluate(`document.querySelectorAll('.trial-condition').length`), 4);
  assert.equal(await client.evaluate(`document.querySelectorAll('.recognition-record').length`), 24);
  await client.evaluate(`document.querySelector('#results').scrollIntoView()`);
  await screenshot('view-trial-desktop.png');
  await client.evaluate(`document.querySelector('#location').scrollIntoView()`);
  await waitFor(`[...document.querySelectorAll('.audit-photos img')].every(image => image.complete && image.naturalWidth > 0)`);
  assert.equal(await client.evaluate(`document.querySelectorAll('.audit-model').length`), 3);
  assert.equal(await client.evaluate(`document.querySelectorAll('.audit-source').length`), 3);
  await screenshot('location-audit-desktop.png');
  await navigate('view-trial.html#request-p43-high-paired-1', 390, 844);
  await waitFor(`document.querySelector('#request-p43-high-paired-1').open`);
  assert.equal(await client.evaluate(`document.querySelectorAll('#request-p43-high-paired-1 img').length`), 2);
  await client.evaluate(`document.querySelector('#request-p43-high-paired-1 [data-box]').click()`);
  assert.equal(await client.evaluate(`document.querySelector('#request-p43-high-paired-1 .model-box').hidden`), false);
  await client.evaluate(`document.querySelector('#request-p43-high-paired-1 .clear-box').click()`);
  assert.equal(await client.evaluate(`document.querySelector('#request-p43-high-paired-1 .model-box').hidden`), true);
  await screenshot('view-request-mobile.png');
  await navigate('view-trial.html', 390, 844);
  await client.evaluate(`document.querySelector('#results').scrollIntoView()`);
  await screenshot('view-trial-mobile.png');
  await navigate('fenton.html', 390, 844);
  await screenshot('fenton-mobile.png');

  await navigate('civilisers.html');
  await waitFor(`document.querySelector('#evidence-count').textContent.includes('29 of 29')`);
  await screenshot('civilisers-desktop.png');
  await client.evaluate(`document.querySelector('#comparison').scrollIntoView()`);
  await screenshot('comparison-desktop.png');
  await client.evaluate(`document.querySelector('#figure-filter').value = 'oannes'; document.querySelector('#figure-filter').dispatchEvent(new Event('change'));`);
  assert.equal(await client.evaluate(`document.querySelectorAll('.evidence-card:not([hidden])').length`), 4);
  await client.evaluate(`document.querySelector('#passage-search').value = 'impossible-query-xyz'; document.querySelector('#passage-search').dispatchEvent(new Event('input'));`);
  assert.equal(await client.evaluate(`document.querySelectorAll('.evidence-card:not([hidden])').length`), 0);
  assert.equal(await client.evaluate(`document.querySelector('#no-evidence').hidden`), false);
  await client.evaluate(`location.hash = '#V4'`);
  await waitFor(`!document.querySelector('#V4').hidden`);
  assert.equal(await client.evaluate(`document.querySelector('#figure-filter').value`), 'all');
  await client.evaluate(`document.querySelector('#figure-filter').value = 'bochica'; document.querySelector('#figure-filter').dispatchEvent(new Event('change')); document.querySelector('#evidence-tools').reset()`);
  assert.equal(await client.evaluate(`document.querySelectorAll('.evidence-card:not([hidden])').length`), 29);
  await navigate('civilisers.html', 390, 844);
  await client.evaluate(`document.querySelector('#passages').scrollIntoView()`);
  await screenshot('passages-mobile.png');
  await navigate('narrative.html', 390, 844);
  await waitFor(`!location.pathname.endsWith('/narrative.html') && location.hash === '#pattern' && !!document.querySelector('#pattern')`);
  await screenshot('narrative-mobile.png');
  await client.evaluate(`document.querySelector('#animals').scrollIntoView()`);
  await screenshot('animals-mobile.png');
  await client.evaluate(`document.querySelector('#sources').scrollIntoView()`);
  await waitFor(`document.querySelector('#credits').children.length > 0`);
  assert.ok(await client.evaluate(`document.documentElement.scrollWidth <= innerWidth + 1`), 'Source credits cause mobile overflow');

  const rendered = {
    'rongo/': `document.querySelector('[data-v=rank_best24]').textContent.length > 0`,
    'myths.html': `document.querySelector('#class-tables').children.length > 0`,
    'pictures.html': `document.querySelector('#verdict-b').textContent.length > 40`,
    'heroes.html': `document.querySelector('#verdict-p').textContent.includes('62.5')`,
    'floods.html': `document.querySelector('#verdict-p').textContent.length > 40`
  };
  for (const [path, condition] of Object.entries(rendered)) {
    await navigate(path);
    await waitFor(condition);
  }
  await navigate('index.html#birdmen');
  await waitFor(`location.pathname.endsWith('/atlas.html') && location.hash === '#birdmen'`);
  await navigate('narrative.html#handbags');
  await waitFor(`!location.pathname.endsWith('/narrative.html') && location.hash === '#handbags' && !!document.querySelector('#handbags')`);
  await navigate('index.html#new-comparisons');
  await waitFor(`location.hash === '#animals'`);

  await navigate('index.html#fenton-bird');
  await waitFor(`location.pathname.endsWith('/fenton.html') && location.hash === '#fenton-bird'`);
  // Core evidence remains available when scripting is disabled.
  await client.send('Emulation.setScriptExecutionDisabled', {value: true});
  await navigate('submerged.html',390,844);
  assert.ok(await client.evaluate(`document.querySelector('#water-tools').hidden && !document.querySelector('#depth-fallback').hidden`));
  assert.equal(await client.evaluate(`document.querySelectorAll('.water-project').length`),6);
  await waitFor(`document.querySelector('#depth-fallback').complete && document.querySelector('#depth-fallback').naturalWidth>0`);
  await navigate('catalogue.html',390,844);
  assert.equal(await client.evaluate(`document.querySelectorAll('.family-card').length`),19);
  assert.ok(await client.evaluate(`!document.querySelector('#families-view').hidden`));
  assert.ok(await client.evaluate(`document.querySelector('#catalogue-filters').hidden`));
  await navigate('catalogue/birdmen-worlds.html',390,844);
  assert.equal(await client.evaluate(`document.querySelectorAll('.group-member').length`),9);
  assert.ok(await client.evaluate(`document.querySelector('#sources').textContent.includes('Pillar 43')`));
  await navigate('pillar-and-moai.html', 390, 844);
  assert.equal(await client.evaluate(`document.querySelectorAll('.hypothesis:not([hidden])').length`), 4);
  assert.equal(await client.evaluate(`document.querySelectorAll('.compare-panel img').length`), 2);
  await navigate('view-trial.html', 390, 844);
  assert.equal(await client.evaluate(`document.querySelectorAll('.trial-condition').length`), 4);
  assert.equal(await client.evaluate(`document.querySelectorAll('.audit-source').length`), 3);
  await navigate('fieldwork.html',390,844);
  assert.equal(await client.evaluate(`document.querySelectorAll('.fw-card:not([hidden])').length`),22);
  assert.equal(await client.evaluate(`document.querySelectorAll('.fw-event').length`),9);
  assert.ok(await client.evaluate(`[...document.querySelectorAll('.fw-interactive')].every(el=>el.hidden)`));
  await client.send('Emulation.setScriptExecutionDisabled', {value: false});

  const exceptions = client.events.filter(event => event.method === 'Runtime.exceptionThrown');
  assert.deepEqual(exceptions, [], 'Uncaught browser JavaScript exceptions');
  const failedLocalResponses = client.events.filter(event => event.method === 'Network.responseReceived' &&
    event.params.response.url.startsWith(base.origin) && event.params.response.status >= 400 &&
    !event.params.response.url.endsWith('/favicon.ico')).map(event => event.params.response.url);
  assert.deepEqual(failedLocalResponses, [], 'Failed local asset requests');
  console.log(`Browser smoke checks passed: catalogue views, cluster index, the two repertoire walls and pair dossiers, shared filters and return links, submerged grids and depth changes, network fallback, desktop/mobile layouts, comparison controls, recognition trials, five studies, legacy bookmarks and no-script evidence.\nScreenshots: ${screenshots}`);
} finally {
  client?.close();
  browserClient?.close();
  browser.kill('SIGTERM');
}
