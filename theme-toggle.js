(function () {
  'use strict';

  /* ── Light-theme CSS override ──────────────────────────────────────── */
  var styleEl = document.createElement('style');
  styleEl.textContent = [
    '[data-theme="light"] {',
    '  --bg:      #f5f0e4;',
    '  --surface: #faf7ee;',
    '  --panel:   #ede8d8;',
    '  --border:  #ccc6b4;',
    '  --text:    #18140c;',
    '  --muted:   #3e3c60;',
    '  --accent:  #2858c8;',
    '  --correct: #115238;',
    '  --hint:    #6e4a00;',
    '  --wrong:   #cc2040;',
    '}',
    '[data-theme="light"] section h3 { color: #18140c; }',
    '[data-theme="light"] .chapter-num { color: #3e3c60; }',
    '#theme-toggle {',
    '  background: none;',
    '  border: 1px solid var(--border);',
    '  color: var(--muted);',
    '  font-family: system-ui, sans-serif;',
    '  font-size: 0.78rem;',
    '  padding: 4px 12px;',
    '  border-radius: 6px;',
    '  cursor: pointer;',
    '  letter-spacing: 0.03em;',
    '  transition: border-color .15s, color .15s;',
    '  white-space: nowrap;',
    '  flex-shrink: 0;',
    '}',
    '#theme-toggle:hover { border-color: var(--accent); color: var(--accent); }'
  ].join('\n');
  document.head.appendChild(styleEl);

  /* ── Button ────────────────────────────────────────────────────────── */
  var btn = document.createElement('button');
  btn.type = 'button';
  btn.id = 'theme-toggle';

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('math-theme', theme);
    btn.textContent = theme === 'light' ? '☾ Dark' : '☀ Light';
    btn.title = theme === 'light' ? 'Switch to dark theme' : 'Switch to light theme';
  }

  btn.addEventListener('click', function () {
    var cur = document.documentElement.getAttribute('data-theme') || 'dark';
    applyTheme(cur === 'light' ? 'dark' : 'light');
  });

  function init() {
    var header = document.querySelector('header');
    if (header) {
      /* Textbooks: header is a flex row — push button to the far right */
      btn.style.marginLeft = 'auto';
      header.appendChild(btn);
    } else {
      /* Game (no <header>): fixed top-right corner */
      btn.style.position = 'fixed';
      btn.style.top = '14px';
      btn.style.right = '18px';
      btn.style.zIndex = '900';
      document.body.appendChild(btn);
    }
    var cur = document.documentElement.getAttribute('data-theme') || 'dark';
    applyTheme(cur);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
}());
