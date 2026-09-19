/* The boxes show what the model claimed to locate, not an endorsed tracing. */
document.querySelectorAll('.recognition-record').forEach(record => {
  const box = record.querySelector('.model-box');
  record.querySelectorAll('[data-box]').forEach(button => {
    button.addEventListener('click', () => {
      const [x1, y1, x2, y2] = button.dataset.box.split(',').map(Number);
      if (![x1, y1, x2, y2].every(v => Number.isFinite(v) && v >= 0 && v <= 1) || x1 >= x2 || y1 >= y2) return;
      Object.assign(box.style, {left: `${x1 * 100}%`, top: `${y1 * 100}%`, width: `${(x2-x1) * 100}%`, height: `${(y2-y1) * 100}%`});
      box.hidden = false;
      record.querySelectorAll('[data-box]').forEach(b => b.setAttribute('aria-pressed', String(b === button)));
    });
  });
  record.querySelector('.clear-box').addEventListener('click', () => {
    box.hidden = true;
    record.querySelectorAll('[data-box]').forEach(b => b.setAttribute('aria-pressed', 'false'));
  });
});

(() => {
  const follow = () => {
    const target = document.getElementById(decodeURIComponent(location.hash.slice(1)));
    if (target?.matches('.recognition-record')) { target.open = true; target.scrollIntoView(); }
  };
  addEventListener('hashchange', follow); follow();
})();
