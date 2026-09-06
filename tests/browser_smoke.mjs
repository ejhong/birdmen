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
      if (message.error) pending.reject(new Error(JSON.stringify(message.error)));
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
      this.pending.set(id, {resolve, reject, timer});
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

  async function waitFor(expression) {
    const deadline = Date.now() + 12000;
    do {
      if (await client.evaluate(expression)) return;
      await new Promise(resolve => setTimeout(resolve, 100));
    } while (Date.now() < deadline);
    throw new Error(`Page condition did not resolve: ${expression}`);
  }
  async function navigate(path, width = 1440, height = 1050) {
    await client.send('Emulation.setDeviceMetricsOverride', {width, height, deviceScaleFactor: 1, mobile: false});
    await client.send('Page.navigate', {url: new URL(path, base).href});
    await waitFor(`document.readyState === 'complete'`);
    await client.evaluate(`Promise.race([document.fonts.ready, new Promise(resolve => setTimeout(resolve, 2500))]).then(() => true)`);
    assert.ok(await client.evaluate(`document.documentElement.scrollWidth <= innerWidth + 1`), `${path}: horizontal page overflow at ${width}px`);
  }
  async function screenshot(name, full = false) {
    const {data} = await client.send('Page.captureScreenshot', {format: 'png', captureBeyondViewport: full,
      ...(full ? {clip: {...await client.evaluate(`({x:0,y:0,width:innerWidth,height:Math.min(document.documentElement.scrollHeight,16000)})`), scale: 1}} : {})});
    await writeFile(join(screenshots, name), Buffer.from(data, 'base64'));
  }

  await navigate('index.html');
  assert.equal(await client.evaluate(`document.querySelectorAll('.investigation').length`), 5);
  assert.equal(await client.evaluate(`document.querySelector('main section').id`), 'investigations');
  assert.equal(await client.evaluate(`document.querySelector('#animals').previousElementSibling.id`), 'handbags');
  assert.equal(await client.evaluate(`document.querySelector('img[src="img/inputs/bird-figure.jpeg"]').closest('section').id`), 'birdmen');
  assert.ok(await client.evaluate(`getComputedStyle(document.body).fontFamily.includes('Newsreader')`));
  await screenshot('home-desktop.png');
  await client.evaluate(`document.querySelector('#investigations').scrollIntoView()`);
  await screenshot('investigations-desktop.png');
  await client.evaluate(`document.querySelector('#bird-detail').scrollIntoView()`);
  await waitFor(`[...document.querySelectorAll('#birdmen img[src^="img/inputs/"]')].every(image => image.complete && image.naturalWidth > 0)`);
  await screenshot('bird-detail-desktop.png');
  await client.evaluate(`document.querySelector('#pigs').scrollIntoView()`);
  await waitFor(`[...document.querySelectorAll('img[src*="boar-museum"], img[src*="lingjiatan"]')].every(image => image.complete && image.naturalWidth > 0)`);
  await screenshot('animals-desktop.png');
  await navigate('index.html', 390, 844);
  await screenshot('home-mobile.png');
  await client.evaluate(`document.querySelector('#investigations').scrollIntoView()`);
  await screenshot('investigations-mobile.png');
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
  await waitFor(`!location.pathname.endsWith('/narrative.html') && location.hash === '#narrative' && !!document.querySelector('#pattern')`);
  await screenshot('narrative-mobile.png');
  await client.evaluate(`document.querySelector('#animals').scrollIntoView()`);
  await screenshot('animals-mobile.png');
  await client.evaluate(`document.querySelector('#sources').scrollIntoView()`);
  await waitFor(`document.querySelector('#credits').children.length > 0`);
  assert.ok(await client.evaluate(`document.documentElement.scrollWidth <= innerWidth + 1`), 'Source credits cause mobile overflow');

  const rendered = {
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
  await waitFor(`location.pathname.endsWith('/index.html') && location.hash === '#birdmen'`);
  await navigate('narrative.html#handbags');
  await waitFor(`!location.pathname.endsWith('/narrative.html') && location.hash === '#handbags' && !!document.querySelector('#handbags')`);
  await navigate('index.html#new-comparisons');
  await waitFor(`location.hash === '#animals'`);

  const exceptions = client.events.filter(event => event.method === 'Runtime.exceptionThrown');
  assert.deepEqual(exceptions, [], 'Uncaught browser JavaScript exceptions');
  const failedLocalResponses = client.events.filter(event => event.method === 'Network.responseReceived' &&
    event.params.response.url.startsWith(base.origin) && event.params.response.status >= 400 &&
    !event.params.response.url.endsWith('/favicon.ico')).map(event => event.params.response.url);
  assert.deepEqual(failedLocalResponses, [], 'Failed local asset requests');
  console.log(`Browser smoke checks passed: desktop/mobile layout, 5 studies, passage filters, hash links, legacy charts and bookmarks.\nScreenshots: ${screenshots}`);
} finally {
  client?.close();
  browserClient?.close();
  browser.kill('SIGTERM');
}
