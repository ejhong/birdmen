/* Progressive enhancement: every passage and source link works without JavaScript. */
(() => {
  const form = document.getElementById('evidence-tools');
  const figure = document.getElementById('figure-filter');
  const search = document.getElementById('passage-search');
  const count = document.getElementById('evidence-count');
  const empty = document.getElementById('no-evidence');
  const cards = [...document.querySelectorAll('.evidence-card')];
  if (!form || !figure || !search || !count || !empty) return;

  const searchable = new Map(cards.map(card => [card, card.textContent.toLocaleLowerCase()]));
  const filter = () => {
    const words = search.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    let shown = 0;
    for (const card of cards) {
      card.hidden = !(figure.value === 'all' || card.dataset.figure === figure.value) ||
        !words.every(word => searchable.get(card).includes(word));
      if (!card.hidden) shown += 1;
    }
    count.textContent = `${shown} of ${cards.length} passages shown`;
    empty.hidden = shown !== 0;
  };

  const revealLinkedPassage = () => {
    let id;
    try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
    const target = document.getElementById(id);
    if (!target || !target.classList.contains('evidence-card') || !target.hidden) return;
    figure.value = 'all';
    search.value = '';
    filter();
    target.scrollIntoView({block: 'start'});
  };

  form.hidden = false;
  form.addEventListener('submit', event => event.preventDefault());
  form.addEventListener('reset', event => {
    event.preventDefault();
    figure.value = 'all';
    search.value = '';
    filter();
  });
  figure.addEventListener('change', filter);
  search.addEventListener('input', filter);
  window.addEventListener('hashchange', revealLinkedPassage);
  document.addEventListener('click', event => {
    const link = event.target.closest('a[href^="#"]');
    if (link && link.hash === location.hash) revealLinkedPassage();
  });
  filter();
  revealLinkedPassage();
})();
