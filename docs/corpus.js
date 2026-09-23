/** Filtering highlights; it never removes. The unmatched stones are the comparison's control. */
const items = [...document.querySelectorAll('.wall-item')];
const buttons = [...document.querySelectorAll('[data-feature]')];
const readout = document.querySelector('#wall-readout');
const walls = [...document.querySelectorAll('.wall')];
const active = new Set();

const legible = (item, feature) => item.dataset.state.includes(`${feature}-1`);

function render() {
  const chosen = [...active];
  document.body.classList.toggle('wall-filtered', chosen.length > 0);
  for (const item of items) {
    const hit = chosen.length > 0 && chosen.every(f => legible(item, f));
    item.classList.toggle('is-hit', hit);
    item.classList.toggle('is-dim', chosen.length > 0 && !hit);
  }
  for (const button of buttons) button.setAttribute('aria-pressed', String(active.has(button.dataset.feature)));
  if (!chosen.length) {
    readout.textContent = 'Nothing selected. Both walls show every registered photograph.';
    return;
  }
  const labels = buttons.filter(b => active.has(b.dataset.feature)).map(b => b.textContent.toLowerCase());
  readout.innerHTML = walls.map(wall => {
    const own = [...wall.querySelectorAll('.wall-item')];
    const hits = own.filter(i => i.classList.contains('is-hit')).length;
    return `${wall.querySelector('h2').textContent}: <b>${hits}</b> of ${own.length}`;
  }).join(' · ') + ` &nbsp;—&nbsp; photographs in which ${labels.join(' and ')} ${labels.length > 1 ? 'are' : 'is'} legible.`;
}

for (const button of buttons) {
  button.addEventListener('click', () => {
    const f = button.dataset.feature;
    active.has(f) ? active.delete(f) : active.add(f);
    render();
  });
}
document.querySelector('#wall-reset').addEventListener('click', () => { active.clear(); render(); });
render();
