(function () {
  'use strict';

  /* ── Injected styles ───────────────────────────────────────────────── */
  var styleEl = document.createElement('style');
  styleEl.textContent = [
    '.formula, .example { position: relative; }',
    '.formula > .label, .example > .label { padding-right: 28px; }',
    '.note-btn {',
    '  position: absolute; top: 10px; right: 10px;',
    '  background: none; border: none;',
    '  color: var(--muted, #7070a0);',
    '  font-size: 0.9rem; line-height: 1; cursor: pointer;',
    '  padding: 2px 5px; border-radius: 3px;',
    '  opacity: 0.3; transition: opacity .15s, color .15s;',
    '  user-select: none; -webkit-user-select: none; z-index: 1;',
    '}',
    '.note-btn:hover { opacity: 1; color: var(--hint, #ffb830); }',
    '.note-btn.open { opacity: 1; color: var(--accent, #5c8aff); }',
    '.note-btn.has-note { opacity: 0.85; color: var(--hint, #ffb830); }',
    '.note-area {',
    '  display: none;',
    '  margin-top: 12px; padding-top: 10px;',
    '  border-top: 1px solid var(--border, #2e2e55);',
    '}',
    '.note-area.open { display: block; }',
    '.note-area textarea {',
    '  width: 100%; box-sizing: border-box;',
    '  background: var(--bg, #0d0d1a);',
    '  border: 1px solid var(--border, #2e2e55);',
    '  border-left: 3px solid var(--hint, #ffb830);',
    '  border-radius: 6px;',
    '  color: var(--text, #e0e0f0);',
    '  font-family: system-ui, sans-serif;',
    '  font-size: 0.85rem; line-height: 1.65;',
    '  padding: 8px 12px; resize: vertical; min-height: 64px;',
    '  outline: none;',
    '}',
    '.note-area textarea:focus { border-left-color: var(--accent, #5c8aff); }',
    '.note-area textarea::placeholder { color: var(--muted, #7070a0); }'
  ].join('\n');
  document.head.appendChild(styleEl);

  /* ── Storage ───────────────────────────────────────────────────────── */
  var PAGE_KEY = 'txtnotes\x1f' + location.pathname;

  function load() {
    try { return JSON.parse(localStorage.getItem(PAGE_KEY) || '{}'); }
    catch (e) { return {}; }
  }

  function save(notes) {
    try { localStorage.setItem(PAGE_KEY, JSON.stringify(notes)); } catch (e) {}
  }

  /* ── Stable key: sectionId + index of box within that section ─────── */
  function boxKey(el) {
    var sec = el.closest('section');
    var sid = sec ? (sec.id || '_') : '_';
    var scope = sec || document;
    var boxes = Array.from(scope.querySelectorAll('.formula, .example'));
    return sid + '\x1f' + boxes.indexOf(el);
  }

  /* ── Wire up one box ───────────────────────────────────────────────── */
  function wire(box, savedText) {
    var btn = document.createElement('button');
    btn.className = 'note-btn' + (savedText ? ' has-note' : '');
    btn.textContent = '✎'; // ✎ pencil
    btn.title = savedText ? 'Edit note' : 'Add note';
    btn.type = 'button';

    var area = document.createElement('div');
    area.className = 'note-area';

    var ta = document.createElement('textarea');
    ta.placeholder = 'Your notes…';
    ta.value = savedText || '';
    area.appendChild(ta);

    box.appendChild(btn);
    box.appendChild(area);

    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      var open = area.classList.toggle('open');
      btn.classList.toggle('open', open);
      if (open) ta.focus();
    });

    ta.addEventListener('input', function () {
      var key = boxKey(box);
      var notes = load();
      if (ta.value.trim()) {
        notes[key] = ta.value;
        btn.classList.add('has-note');
        btn.title = 'Edit note';
      } else {
        delete notes[key];
        btn.classList.remove('has-note');
        btn.title = 'Add note';
      }
      save(notes);
    });
  }

  /* ── Init ──────────────────────────────────────────────────────────── */
  function init() {
    var notes = load();
    document.querySelectorAll('.formula, .example').forEach(function (box) {
      wire(box, notes[boxKey(box)] || '');
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
}());
