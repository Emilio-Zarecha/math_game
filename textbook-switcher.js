(function () {
  'use strict';

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
    'nav.textbook-switcher {',
    '  display: flex;',
    '  flex-wrap: nowrap;',
    '  overflow-x: auto;',
    '  scrollbar-width: none;',
    '  gap: 0;',
    '  background: var(--panel);',
    '  border-bottom: 1px solid var(--border);',
    '  padding: 0 1rem;',
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
  ].join('\n');
  document.head.appendChild(style);

  function init() {
    var current = window.location.pathname.split('/').pop();

    var nav = document.createElement('nav');
    nav.className = 'textbook-switcher';
    nav.setAttribute('aria-label', 'Switch textbook');

    BOOKS.forEach(function (b) {
      var a = document.createElement('a');
      a.href = b.file;
      a.textContent = b.label;
      if (b.file === current) {
        a.className = 'current';
        a.setAttribute('aria-current', 'page');
      }
      nav.appendChild(a);
    });

    var header = document.querySelector('header');
    if (header) {
      header.parentNode.insertBefore(nav, header.nextSibling);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
}());
