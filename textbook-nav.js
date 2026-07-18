(function () {
  'use strict';

  /* ── Styles ── */
  var styleEl = document.createElement('style');
  styleEl.textContent = [
    '#toc-back {',
    '  display: none;',
    '  margin-top: 16px;',
    '  padding-top: 14px;',
    '  border-top: 1px solid var(--border, #2e2e55);',
    '  text-align: right;',
    '}',
    '#toc-back button {',
    '  background: none;',
    '  border: 1px solid var(--border, #2e2e55);',
    '  color: var(--muted, #7070a0);',
    '  font-size: 0.82rem;',
    '  padding: 5px 14px;',
    '  border-radius: 6px;',
    '  cursor: pointer;',
    '  transition: border-color .15s, color .15s;',
    '}',
    '#toc-back button:hover { border-color: var(--accent, #5c8aff); color: var(--accent, #5c8aff); }'
  ].join('\n');
  document.head.appendChild(styleEl);

  var savedScrollY = null;
  var backContainer = null;

  function smoothScrollTo(target) {
    if (typeof target === 'number') {
      window.scrollTo({ top: target, behavior: 'smooth' });
    } else if (target && target.scrollIntoView) {
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  function init() {
    var nav = document.querySelector('#toc');
    if (!nav) return;

    /* "Back to where I was" button lives inside the nav */
    backContainer = document.createElement('div');
    backContainer.id = 'toc-back';
    var btn = document.createElement('button');
    btn.textContent = '↩ Back to where I was';
    btn.addEventListener('click', function () {
      if (savedScrollY !== null) {
        smoothScrollTo(savedScrollY);
        savedScrollY = null;
        backContainer.style.display = 'none';
      }
    });
    backContainer.appendChild(btn);
    nav.appendChild(backContainer);

    /* Wire existing .toc-back links to save scroll position before jumping */
    document.querySelectorAll('.toc-back a').forEach(function (a) {
      a.addEventListener('click', function (e) {
        e.preventDefault();
        savedScrollY = window.scrollY;
        backContainer.style.display = '';
        smoothScrollTo(nav);
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
}());
