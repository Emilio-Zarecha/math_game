(function () {
  'use strict';

  // Not textbooks, but the switcher is the only nav that persists across every
  // page, so it doubles as the site's back-to-game / diagrams shortcut too.
  var EXTRAS = [
    { file: 'index.html',      label: '◂ Game',  extra: true },
    { file: 'diagrams.html',   label: 'Diagrams', extra: true },
  ];

  var BOOKS = [
    { file: 'textbook_arithmetic.html',    label: 'Arithmetic' },
    { file: 'textbook_arithmetic2.html',   label: 'Intermediate Arithmetic' },
    { file: 'textbook_algebra.html',       label: 'Algebra' },
    { file: 'textbook_algebra2.html',      label: 'Algebra 2' },
    { file: 'textbook_geometry.html',      label: 'Geometry' },
    { file: 'textbook_trigonometry.html',  label: 'Trigonometry' },
    { file: 'textbook_calculus.html',      label: 'Calculus' },
    { file: 'textbook_statistics.html',    label: 'Statistics' },
    { file: 'textbook_linearalgebra.html', label: 'Linear Algebra' },
    { file: 'textbook_combinatorics.html', label: 'Combinatorics' },
    { file: 'textbook_graphtheory.html',   label: 'Graph Theory' },
  ];

  var style = document.createElement('style');
  style.textContent = [
    '.textbook-switcher-wrap {',
    '  display: flex;',
    '  align-items: stretch;',
    '  width: 100%;',
    '  background: var(--panel);',
    '  border-bottom: 1px solid var(--border);',
    '}',
    'nav.textbook-switcher {',
    '  display: flex;',
    '  flex-wrap: nowrap;',
    '  overflow-x: auto;',
    '  scrollbar-width: none;',
    '  gap: 0;',
    '  flex: 1;',
    '  min-width: 0;',
    '  padding: 0 1rem;',
    /* Hints that the bar scrolls, since the scrollbar itself is hidden above. */
    '  mask-image: linear-gradient(to right, transparent, black 20px, black calc(100% - 20px), transparent);',
    '  -webkit-mask-image: linear-gradient(to right, transparent, black 20px, black calc(100% - 20px), transparent);',
    '}',
    'nav.textbook-switcher::-webkit-scrollbar { display: none; }',
    'nav.textbook-switcher a {',
    '  color: var(--muted);',
    '  text-decoration: none;',
    '  font-size: 0.78rem;',
    '  font-family: system-ui, sans-serif;',
    '  padding: 8px 13px;',
    '  border-bottom: 2px solid transparent;',
    '  letter-spacing: 0.02em;',
    '  white-space: nowrap;',
    '  transition: color .15s, border-color .15s;',
    '}',
    'nav.textbook-switcher a:hover {',
    '  color: var(--accent);',
    '  border-bottom-color: var(--border);',
    '}',
    'nav.textbook-switcher a.current {',
    '  color: var(--text);',
    '  border-bottom-color: var(--accent);',
    '  font-weight: 600;',
    '}',
    'nav.textbook-switcher a.extra {',
    '  border-right: 1px solid var(--border);',
    '}',
    '.ts-scroll-btn {',
    '  flex: 0 0 auto;',
    '  display: flex;',
    '  align-items: center;',
    '  justify-content: center;',
    '  width: 28px;',
    '  background: var(--panel);',
    '  border: none;',
    '  color: var(--muted);',
    '  cursor: pointer;',
    '  font-size: 1rem;',
    '  line-height: 1;',
    '  padding: 0;',
    '  transition: color .15s, opacity .15s;',
    '}',
    '.ts-scroll-btn:hover:not(:disabled) { color: var(--accent); }',
    '.ts-scroll-btn:focus-visible { outline: 2px solid var(--accent); outline-offset: -2px; }',
    '.ts-scroll-btn:disabled { opacity: 0; pointer-events: none; }',
  ].join('\n');
  document.head.appendChild(style);

  function init() {
    var current = window.location.pathname.split('/').pop();

    var nav = document.createElement('nav');
    nav.className = 'textbook-switcher';
    nav.setAttribute('aria-label', 'Switch textbook');

    EXTRAS.concat(BOOKS).forEach(function (b) {
      var a = document.createElement('a');
      a.href = b.file;
      a.textContent = b.label;
      var classes = [];
      if (b.extra) classes.push('extra');
      if (b.file === current) {
        classes.push('current');
        a.setAttribute('aria-current', 'page');
      }
      if (classes.length) a.className = classes.join(' ');
      nav.appendChild(a);
    });

    var wrap = document.createElement('div');
    wrap.className = 'textbook-switcher-wrap';

    var prevBtn = document.createElement('button');
    prevBtn.type = 'button';
    prevBtn.className = 'ts-scroll-btn';
    prevBtn.setAttribute('aria-label', 'Scroll textbooks left');
    prevBtn.textContent = '‹';

    var nextBtn = document.createElement('button');
    nextBtn.type = 'button';
    nextBtn.className = 'ts-scroll-btn';
    nextBtn.setAttribute('aria-label', 'Scroll textbooks right');
    nextBtn.textContent = '›';

    wrap.appendChild(prevBtn);
    wrap.appendChild(nav);
    wrap.appendChild(nextBtn);

    var header = document.querySelector('header');
    if (header) {
      header.parentNode.insertBefore(wrap, header.nextSibling);
    }

    function updateButtons() {
      prevBtn.disabled = nav.scrollLeft <= 0;
      nextBtn.disabled = nav.scrollLeft + nav.clientWidth >= nav.scrollWidth - 1;
    }

    prevBtn.addEventListener('click', function () {
      nav.scrollBy({ left: -160, behavior: 'smooth' });
    });
    nextBtn.addEventListener('click', function () {
      nav.scrollBy({ left: 160, behavior: 'smooth' });
    });
    nav.addEventListener('scroll', updateButtons);
    window.addEventListener('resize', updateButtons);
    updateButtons();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
}());
