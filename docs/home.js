/* The study collection and narrative share one page. Keep older bookmarks usable. */
(() => {
  const aliases = {
    '#tests': '#investigations',
    '#study3': '#investigations',
    '#study45': '#investigations',
    '#new-comparisons': '#animals'
  };
  const followAlias = () => {
    const target = aliases[location.hash];
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
