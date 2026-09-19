/* Progressive enhancement: the original photographs and essays remain readable offline. */
(() => {
  const viewer = document.querySelector('[data-comparison]');
  const sources = {
    p43: {src: 'img/case/pillar43.jpg', w: 778, h: 1181, title: 'Pillar 43 · Enclosure D', alt: 'Whole decorated western surface of Pillar 43, with birds, a round disc, three arched forms and a scorpion', credit: 'Göbekli Tepe. Photograph © DAI / K. Schmidt.', markers: [
      [10, 24, 36, 27, '1', 'Prominent bird and nearby disc; the meaning of the disc is open.'],
      [18, 53, 43, 24, '2', 'Scorpion on the lower shaft.']
    ]},
    hoa: {src: 'img/case/hoa-back.jpg', w: 1280, h: 1933, title: 'Hoa Hakananai’a · back', alt: 'Back of Hoa Hakananai’a, with birdman carvings, a large ring and curved bands', credit: 'James Miles / CC BY-SA 4.0.', markers: [
      [23, 17, 46, 35, '1', 'Area containing the birdman composition; some carved lines are faint.'],
      [38, 50, 20, 11, '2', 'Large ring below the principal figures.'],
      [56, 82, 6, 5, '3', 'Small modern sampling plug; distinct from the large central ring.']
    ]},
    p43alt: {src: 'img/case/pillar43-alt.jpg', w: 676, h: 967, title: 'Pillar 43 · another view', alt: 'Pillar 43 photographed from a different angle in softer light', credit: 'DAI / Göbekli Tepe Project; attribution retained from the original study.', markers: [[25, 29, 25, 23, '1', 'Bird and disc, in softer light.'], [29, 54, 26, 22, '2', 'Scorpion, less strongly lit than in the first photograph.']]},
    hoaalt: {src: 'img/case/hoa-back-alt.jpg', w: 1280, h: 1920, title: 'Hoa Hakananai’a · another view', alt: 'The moai’s carved back photographed with warm lighting by Sanjay ach', credit: 'Sanjay ach / CC BY-SA 4.0.', markers: [[24, 25, 47, 25, '1', 'The birdman carving under different lighting.'], [40, 49, 19, 10, '2', 'Large central ring.'], [53, 80, 7, 6, '3', 'Modern sampling plug.']]},
    detail: {src: 'img/motifs/pillar43_bird.jpg', w: 900, h: 863, title: 'Pillar 43 · bird detail', alt: 'A close view of the prominent bird and disc on Pillar 43', credit: 'Existing crop from Sue Fleckney / CC BY-SA 2.0. Other motifs are outside this crop.', markers: []},
    boulder: {src: 'img/case/orongo-1919.jpg', w: 950, h: 631, title: 'Orongo boulder · published 1919', alt: 'Historic photograph of a low-relief bird-headed figure with a rounded object at its hand', credit: 'Routledge, The Mystery of Easter Island, fig. 112. Public domain.', markers: [[57, 51, 28, 31, '1', 'Hand and rounded object, interpreted as an egg in the published caption.']]},
    modern: {src: 'img/inputs/bird-figure.jpeg', title: 'Orongo boulder · supplied photograph', alt: 'Modern photograph of the Orongo birdman boulder with dark markings around the figure', credit: 'Object matched to BM Oc1920,0506.1. Photographer and history of dark markings unresolved.', markers: []},
    local: {src: 'img/motifs/orongo.jpg', w: 1100, h: 840, title: 'Mata Ngarau, Orongo · local comparison', alt: 'Historic photograph of three birdman figures carved on an Orongo rock surface', credit: 'Mana Expedition photograph, British Museum Oc,G.T.1647; public domain.', markers: []}
  };
  const modes = {
    whole: ['p43', 'hoa', 'Two whole photographed surfaces. Equal display width is not equal physical scale. Zoom, then scroll each image to inspect details. Guides locate features; they do not reconstruct faint lines.'],
    alternate: ['p43alt', 'hoaalt', 'The same two objects in different photographs. Lighting and viewpoint alter legibility; this is not an additional pair of independent artefacts.'],
    boulder: ['detail', 'boulder', 'A selected detail on the left; a whole small object on the right. The wing–disc relation and hand–egg interpretation can be inspected without assuming they mean the same thing.'],
    archive: ['boulder', 'modern', 'Two records of the same boulder. Compare the relief in the 1919 photograph with the dark lines in the circulating image. The history of those markings remains unresolved.'],
    local: ['hoa', 'local', 'Two Rapanui surfaces. A local comparison helps establish the range of the birdman tradition; resemblance between them is not a calibrated measure of distant similarity.']
  };
  if (viewer) {
    const panels = [...viewer.querySelectorAll('.compare-panel')];
    const windows = panels.map(p => p.querySelector('.compare-window'));
    const zoom = viewer.querySelector('#zoom');
    const annotations = viewer.querySelector('#show-annotations');
    const key = viewer.querySelector('#annotation-key');
    const select = viewer.querySelector('#comparison-select');
    let selected = [];
    let syncing = false;
    const guides = () => {
      key.replaceChildren();
      key.hidden = !annotations.checked;
      selected.forEach((item, i) => {
        const layer = panels[i].querySelector('.markers');
        layer.replaceChildren();
        const entry = document.createElement('div');
        entry.textContent = `${i === 0 ? 'Left' : 'Right'}: `;
        if (!item.markers.length) entry.append('No location guides for this view.');
        item.markers.forEach(([x, y, w, h, number, label]) => {
          const box = document.createElement('div');
          box.className = 'marker'; box.hidden = !annotations.checked;
          Object.assign(box.style, {left: `${x}%`, top: `${y}%`, width: `${w}%`, height: `${h}%`});
          const tag = document.createElement('span'); tag.textContent = number; box.append(tag); layer.append(box);
          const description = document.createElement('div'); description.textContent = `${number}. ${label}`; entry.append(description);
        });
        key.append(entry);
      });
    };
    const setZoom = () => {
      for (let i = 0; i < panels.length; i++) {
        const img = panels[i].querySelector('img');
        const ratio = img.naturalWidth / img.naturalHeight;
        const fit = Math.min(windows[i].clientWidth, windows[i].clientHeight * (ratio || 1));
        panels[i].querySelector('.compare-image').style.width = `${fit * Number(zoom.value) / 100}px`;
      }
      viewer.querySelector('#zoom-value').value = `${zoom.value}%`;
    };
    const reset = () => {
      zoom.value = 100; setZoom();
      for (const win of windows) win.scrollTo(0, 0);
    };
    const change = () => {
      const [left, right, note] = modes[select.value] || modes.whole;
      viewer.dataset.mode = select.value;
      selected = [sources[left], sources[right]];
      selected.forEach((item, i) => {
        const img = panels[i].querySelector('img');
        img.alt = item.alt;
        if (item.w) { img.width = item.w; img.height = item.h; }
        else { img.removeAttribute('width'); img.removeAttribute('height'); }
        img.src = item.src;
        const caption = panels[i].querySelector('figcaption');
        const title = document.createElement('b'); title.textContent = item.title;
        const link = document.createElement('a'); link.href = item.src; link.textContent = 'Open full photograph ↗';
        caption.replaceChildren(title, document.createTextNode(item.credit + ' '), link);
      });
      viewer.querySelector('#compare-note').textContent = note;
      reset(); guides();
    };
    windows.forEach((win, i) => win.addEventListener('scroll', () => {
      if (syncing || !viewer.querySelector('#sync-scroll').checked) return;
      syncing = true;
      const other = windows[1 - i];
      const fraction = (pos, max) => max > 0 ? pos / max : 0;
      other.scrollTop = fraction(win.scrollTop, win.scrollHeight - win.clientHeight) * (other.scrollHeight - other.clientHeight);
      other.scrollLeft = fraction(win.scrollLeft, win.scrollWidth - win.clientWidth) * (other.scrollWidth - other.clientWidth);
      requestAnimationFrame(() => { syncing = false; });
    }, {passive: true}));
    zoom.addEventListener('input', setZoom);
    annotations.addEventListener('change', guides);
    select.addEventListener('change', change);
    viewer.querySelector('#reset-view').addEventListener('click', reset);
    panels.forEach(panel => panel.querySelector('img').addEventListener('load', setZoom));
    new ResizeObserver(setZoom).observe(viewer);
    change();
  }
  for (const group of document.querySelectorAll('[data-hypotheses]')) {
    const buttons = [...group.querySelectorAll('[data-hyp]')];
    const activate = button => {
      for (const item of buttons) {
        const active = item === button;
        item.setAttribute('aria-pressed', String(active));
        document.getElementById(item.getAttribute('aria-controls')).hidden = !active;
      }
    };
    buttons.forEach(button => button.addEventListener('click', () => activate(button)));
    activate(buttons[0]);
  }
})();
