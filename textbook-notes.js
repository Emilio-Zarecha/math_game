(function () {
  'use strict';

  /* ── Injected styles ───────────────────────────────────────────────── */
  var styleEl = document.createElement('style');
  styleEl.textContent = [
    /* per-box notes (formula / example / definition) */
    '.formula, .example, .definition { position: relative; }',
    '.formula > .label, .example > .label { padding-right: 28px; }',
    '.definition > .definition-label { padding-right: 28px; }',
    '.note-btn {',
    '  position: absolute; top: 10px; right: 10px;',
    '  background: none; border: none;',
    '  color: var(--muted, #7070a0);',
    '  font-size: 0.9rem; line-height: 1; cursor: pointer;',
    '  padding: 2px 5px; border-radius: 3px;',
    '  opacity: 0.45; transition: opacity .15s, color .15s;',
    '  user-select: none; -webkit-user-select: none; z-index: 1;',
    '}',
    '.note-btn:hover { opacity: 1; color: var(--hint, #ffb830); }',
    '.note-btn.open  { opacity: 1; color: var(--accent, #5c8aff); }',
    '.note-btn.has-note { opacity: 0.85; color: var(--hint, #ffb830); }',
    /* No hover on touch devices — the resting state has to announce itself on its own */
    '@media (hover: none) {',
    '  .note-btn { opacity: 0.7; }',
    '  .note-btn.has-note { opacity: 1; }',
    '}',
    '.note-area { display: none; margin-top: 12px; padding-top: 10px;',
    '             border-top: 1px solid var(--border, #2e2e55); }',
    '.note-area.open { display: block; }',
    '.note-area textarea, .sn-body textarea {',
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
    '.note-area textarea:focus, .sn-body textarea:focus { border-left-color: var(--accent, #5c8aff); }',
    '.note-area textarea::placeholder, .sn-body textarea::placeholder { color: var(--muted, #7070a0); }',

    /* per-section notes — sits above .toc-back with no extra border */
    '.section-notes-btn {',
    '  background: none; border: none; cursor: pointer;',
    '  color: var(--muted, #7070a0); font-size: 0.82rem;',
    '  letter-spacing: 0.03em; padding: 0;',
    '  display: inline-flex; align-items: center; gap: 6px;',
    '  transition: color .15s;',
    '}',
    '.section-notes-btn:hover { color: var(--hint, #ffb830); }',
    '.section-notes-btn.has-note { color: var(--hint, #ffb830); }',
    '.sn-dot {',
    '  width: 6px; height: 6px; border-radius: 50%;',
    '  background: var(--hint, #ffb830);',
    '  display: none; flex-shrink: 0;',
    '}',
    '.section-notes-btn.has-note .sn-dot { display: inline-block; }',
    '.section-notes { margin-bottom: 1.2rem; }',
    '.sn-body { display: none; margin-top: 8px; }',
    '.sn-body.open { display: block; }',
    '.sn-body textarea { min-height: 80px; }',

    /* toolbar */
    '.notes-toolbar {',
    '  position: fixed; bottom: 0; left: 0; right: 0;',
    '  background: var(--surface, #151528);',
    '  border-top: 1px solid var(--border, #2e2e55);',
    '  padding: 9px 24px;',
    '  display: flex; align-items: center; justify-content: center; gap: 10px;',
    '  z-index: 200;',
    '  transform: translateY(100%); transition: transform 0.2s ease;',
    '}',
    '.notes-toolbar.visible { transform: translateY(0); }',
    '.notes-toolbar .tb-label {',
    '  font-size: 0.72rem; letter-spacing: .12em; text-transform: uppercase;',
    '  color: var(--muted, #7070a0); margin-right: 6px;',
    '}',
    '.notes-toolbar button {',
    '  background: var(--panel, #1c1c35);',
    '  border: 1px solid var(--border, #2e2e55);',
    '  color: var(--text, #e0e0f0);',
    '  font-size: 0.82rem; padding: 5px 14px;',
    '  border-radius: 6px; cursor: pointer;',
    '  transition: border-color .15s, color .15s;',
    '}',
    '.notes-toolbar .tb-export:hover { border-color: var(--accent, #5c8aff); color: var(--accent, #5c8aff); }',
    '.notes-toolbar .tb-clear:hover  { border-color: #ff6b6b; color: #ff6b6b; }'
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

  /* ── Key helpers ───────────────────────────────────────────────────── */
  var BOX_SEL = '.formula, .example, .definition';

  function boxKey(el) {
    var sec   = el.closest('section');
    var sid   = sec ? (sec.id || '_') : '_';
    var scope = sec || document;
    var boxes = Array.from(scope.querySelectorAll(BOX_SEL));
    return sid + '\x1f' + boxes.indexOf(el);
  }

  function sectionKey(sec) {
    return 'sec\x1f' + (sec.id || '_');
  }

  /* ── Toolbar ───────────────────────────────────────────────────────── */
  var toolbar = null;

  function buildToolbar() {
    var bar = document.createElement('div');
    bar.className = 'notes-toolbar';

    var lbl = document.createElement('span');
    lbl.className = 'tb-label';
    lbl.textContent = 'Notes';

    var btnExport = document.createElement('button');
    btnExport.className = 'tb-export';
    btnExport.textContent = '↓ Export';
    btnExport.title = 'Download all notes as a text file';
    btnExport.addEventListener('click', exportNotes);

    var btnClear = document.createElement('button');
    btnClear.className = 'tb-clear';
    btnClear.textContent = '✕ Clear all';
    btnClear.title = 'Delete all notes for this textbook';
    btnClear.addEventListener('click', clearNotes);

    bar.appendChild(lbl);
    bar.appendChild(btnExport);
    bar.appendChild(btnClear);
    document.body.appendChild(bar);
    return bar;
  }

  function syncToolbar() {
    if (!toolbar) toolbar = buildToolbar();
    toolbar.classList.toggle('visible', Object.keys(load()).length > 0);
  }

  /* ── Export ────────────────────────────────────────────────────────── */
  function exportNotes() {
    var notes = load();
    if (!Object.keys(notes).length) return;

    var h1    = document.querySelector('h1');
    var title = h1 ? h1.textContent.trim() : document.title.trim();
    var lines = ['=== ' + title + ' — Notes ===',
                 'Exported: ' + new Date().toLocaleDateString(), ''];

    document.querySelectorAll('section').forEach(function (sec) {
      var sk = sectionKey(sec);
      if (!notes[sk]) return;
      var h3     = sec.querySelector('h3, h2');
      var chNum  = sec.querySelector('.chapter-num');
      var head   = (chNum ? chNum.textContent.trim() + ' — ' : '') +
                   (h3 ? h3.textContent.trim() : sec.id);
      lines.push('--- ' + head + ' (Section Notes) ---');
      lines.push(notes[sk].trim());
      lines.push('');
    });

    var lastSid = null;
    document.querySelectorAll(BOX_SEL).forEach(function (box) {
      var key = boxKey(box);
      if (!notes[key]) return;

      var sec     = box.closest('section');
      var sid     = sec ? (sec.id || '_') : '_';
      var chNum   = sec ? sec.querySelector('.chapter-num') : null;
      var h3      = sec ? sec.querySelector('h3') : null;
      var secHead = (chNum ? chNum.textContent.trim() + ' — ' : '') +
                    (h3 ? h3.textContent.trim() : sid);

      if (sid !== lastSid) {
        lines.push('--- ' + secHead + ' ---');
        lines.push('');
        lastSid = sid;
      }

      var labelEl  = box.querySelector('.label, .definition-label, .example-label');
      var boxType  = box.classList.contains('formula')    ? 'Formula'    :
                     box.classList.contains('example')    ? 'Example'    : 'Definition';
      var boxLabel = labelEl ? labelEl.textContent.trim() : boxType;
      lines.push('[' + boxType + '] ' + boxLabel);
      lines.push(notes[key].trim());
      lines.push('');
    });

    var blob = new Blob([lines.join('\n')], { type: 'text/plain' });
    var url  = URL.createObjectURL(blob);
    var a    = document.createElement('a');
    a.href     = url;
    a.download = title.replace(/[^a-z0-9]+/gi, '_').toLowerCase() + '_notes.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  /* ── Clear all ─────────────────────────────────────────────────────── */
  function clearNotes() {
    if (!window.confirm('Clear all notes for this textbook? This cannot be undone.')) return;
    save({});
    document.querySelectorAll('.note-btn').forEach(function (btn) {
      btn.classList.remove('has-note', 'open');
      btn.title = 'Add note';
    });
    document.querySelectorAll('.note-area').forEach(function (area) {
      area.classList.remove('open');
      var ta = area.querySelector('textarea');
      if (ta) ta.value = '';
    });
    document.querySelectorAll('.section-notes-btn').forEach(function (btn) {
      btn.classList.remove('has-note');
    });
    document.querySelectorAll('.sn-body').forEach(function (body) {
      body.classList.remove('open');
      var ta = body.querySelector('textarea');
      if (ta) ta.value = '';
    });
    syncToolbar();
  }

  /* ── Wire one formula / example / definition box ───────────────────── */
  function wireBox(box, savedText) {
    var btn = document.createElement('button');
    btn.className = 'note-btn' + (savedText ? ' has-note' : '');
    btn.textContent = '✎';
    btn.title = savedText ? 'Edit note' : 'Add note';
    btn.type  = 'button';

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
      var key   = boxKey(box);
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
      syncToolbar();
    });
  }

  /* ── Wire one section ──────────────────────────────────────────────── */
  function wireSection(sec, savedText) {
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'section-notes-btn' + (savedText ? ' has-note' : '');

    var dot = document.createElement('span');
    dot.className = 'sn-dot';
    btn.appendChild(dot);
    btn.appendChild(document.createTextNode('📝 Section Notes'));

    var body = document.createElement('div');
    body.className = 'sn-body';

    var ta = document.createElement('textarea');
    ta.placeholder = 'Your notes for this section…';
    ta.value = savedText || '';
    body.appendChild(ta);

    var wrapper = document.createElement('div');
    wrapper.className = 'section-notes';
    wrapper.appendChild(btn);
    wrapper.appendChild(body);

    // Place notes after the chapter heading, not at the bottom near the TOC link
    var heading = sec.querySelector('h2, h3');
    if (heading) {
      heading.insertAdjacentElement('afterend', wrapper);
    } else {
      sec.appendChild(wrapper);
    }

    btn.addEventListener('click', function () {
      var open = body.classList.toggle('open');
      if (open) ta.focus();
    });

    ta.addEventListener('input', function () {
      var key   = sectionKey(sec);
      var notes = load();
      if (ta.value.trim()) {
        notes[key] = ta.value;
        btn.classList.add('has-note');
      } else {
        delete notes[key];
        btn.classList.remove('has-note');
      }
      save(notes);
      syncToolbar();
    });
  }

  /* ── Init ──────────────────────────────────────────────────────────── */
  function init() {
    var notes = load();
    document.querySelectorAll(BOX_SEL).forEach(function (box) {
      wireBox(box, notes[boxKey(box)] || '');
    });
    document.querySelectorAll('section').forEach(function (sec) {
      wireSection(sec, notes[sectionKey(sec)] || '');
    });
    syncToolbar();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
}());
