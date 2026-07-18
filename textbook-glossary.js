(function () {
  'use strict';

  if (typeof GLOSSARY === 'undefined' || !GLOSSARY) return;

  /* ── Injected styles ───────────────────────────────────────────────── */
  var styleEl = document.createElement('style');
  styleEl.textContent = [
    /* Only terms with an actual GLOSSARY entry get the hover affordance —
     * some textbooks use .key for header-style emphasis ("Why this order?")
     * rather than true vocabulary, and those shouldn't look hoverable. */
    '.key-has-glossary { cursor: help; border-bottom: 1px dotted var(--muted, #7070a0); }',
    '#glossary-tip {',
    '  position: fixed;',
    '  background: var(--panel, #1c1c35);',
    '  border: 1px solid var(--border, #2e2e55);',
    '  border-radius: 6px;',
    '  padding: 8px 12px;',
    '  font-size: 0.8rem;',
    '  color: var(--text, #e0e0f0);',
    '  z-index: 300;',
    '  pointer-events: none;',
    '  white-space: normal;',
    '  max-width: 280px;',
    '  line-height: 1.5;',
    '  box-shadow: 0 4px 16px rgba(0,0,0,0.5);',
    '  display: none;',
    '}'
  ].join('\n');
  document.head.appendChild(styleEl);

  var tip = document.createElement('div');
  tip.id = 'glossary-tip';
  document.body.appendChild(tip);

  function moveTip(e){
    tip.style.left = (e.clientX + 14) + 'px';
    tip.style.top  = (e.clientY - 10) + 'px';
  }

  /* Devices with no real hover (touch, e.g. iPad) get synthesized mouseenter
   * on tap but never a reliable mouseleave — the tooltip would get stuck
   * open. Checked once at load: good enough for this site, not worth
   * tracking a live mouse/trackpad being attached mid-session. */
  var HOVER_CAPABLE = window.matchMedia('(hover: hover)').matches;

  if (HOVER_CAPABLE) {
    document.querySelectorAll('.key').forEach(function(el){
      var term = el.textContent.trim();
      var def = GLOSSARY[term];
      if(!def) return;
      el.classList.add('key-has-glossary');
      el.addEventListener('mouseenter', function(ev){
        tip.textContent = def;
        tip.style.display = 'block';
        moveTip(ev);
        el.addEventListener('mousemove', moveTip);
      });
      el.addEventListener('mouseleave', function(){
        tip.style.display = 'none';
        el.removeEventListener('mousemove', moveTip);
      });
    });
  } else {
    /* Tap-to-toggle: tap a term to open it (closing any other open term),
     * tap it again or tap anywhere else to close. Uses touchend directly
     * rather than 'click' — WebKit only synthesizes a click reliably for
     * elements that already look interactive (own listener / cursor:pointer),
     * so a tap on a plain paragraph elsewhere on the page never produced a
     * click event at all, leaving the tooltip stuck open. */
    var openEl = null;
    document.querySelectorAll('.key').forEach(function(el){
      var term = el.textContent.trim();
      var def = GLOSSARY[term];
      if(!def) return;
      el.classList.add('key-has-glossary');
      el.addEventListener('touchend', function(ev){
        ev.preventDefault();
        ev.stopPropagation();
        if (openEl === el) {
          tip.style.display = 'none';
          openEl = null;
        } else {
          var touch = ev.changedTouches[0];
          tip.textContent = def;
          tip.style.display = 'block';
          tip.style.left = (touch.clientX + 14) + 'px';
          tip.style.top  = (touch.clientY - 10) + 'px';
          openEl = el;
        }
      }, { passive: false });
    });
    document.addEventListener('touchend', function(){
      if (openEl) {
        tip.style.display = 'none';
        openEl = null;
      }
    });
  }
})();
