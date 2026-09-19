/* Keep earlier bookmarks usable after separating the case, atlas and essays. */
(() => {
  const aliases = {
    '#tests': '#investigations',
    '#study3': '#investigations',
    '#study45': '#investigations',
    '#new-comparisons': 'atlas.html#animals',
    '#narrative': 'atlas.html#pattern',
    '#camps': '#explanations',
    '#approach': '#ai'
  };
  const followAlias = () => {
    const isHome = /\/(?:index\.html)?$/.test(location.pathname);
    if (!isHome) return;
    const hash = location.hash;
    const atlas = ['pattern', 'birdmen', 'bird-detail', 'bird-or-birdman', 'handbags', 'animals', 'pigs', 'navel', 'hands', 'serpents', 'civilisers', 'flood'];
    const target = aliases[hash] || (hash.startsWith('#fenton') ? 'fenton.html' + hash : atlas.includes(hash.slice(1)) ? 'atlas.html' + hash : null);
    if (target) location.replace(target);
  };
  window.addEventListener('hashchange', followAlias);
  followAlias();

  const box = document.getElementById('credits');
  if (!box) return;
  fetch('img/motifs/credits.json').then(response => {
    if (!response.ok) throw new Error('Image credits unavailable');
    return response.json();
  }).then(credits => {
    for (const value of Object.values(credits)) {
      const row = document.createElement('div');
      const link = document.createElement('a');
      link.href = value.page;
      link.textContent = value.file.replace(/\.(jpg|JPG|jpeg|png)$/, '');
      row.append(link, ` — ${value.artist || 'unknown'}, ${value.license}`);
      box.append(row);
    }
  }).catch(() => {
    const link = document.createElement('a');
    link.href = 'img/motifs/credits.json';
    link.textContent = 'Open the original image-credit register';
    box.append(link);
  });
})();
