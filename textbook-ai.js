(function () {
  'use strict';

  var LS_KEY     = 'gemini-api-key';
  var MODEL_URL  = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=';

  // ── CSS ──────────────────────────────────────────────────────────────────
  var style = document.createElement('style');
  style.textContent = [
    '#ai-btn {',
    '  background: none;',
    '  border: 1px solid var(--border);',
    '  color: var(--muted);',
    '  font-family: system-ui, sans-serif;',
    '  font-size: 0.78rem;',
    '  padding: 4px 12px;',
    '  border-radius: 6px;',
    '  cursor: pointer;',
    '  letter-spacing: 0.03em;',
    '  margin-left: 8px;',
    '  transition: border-color .15s, color .15s;',
    '  white-space: nowrap;',
    '  flex-shrink: 0;',
    '}',
    '#ai-btn:hover { border-color: var(--accent); color: var(--accent); }',

    '#ai-overlay {',
    '  display: none;',
    '  position: fixed;',
    '  inset: 0;',
    '  background: rgba(0,0,0,0.55);',
    '  z-index: 9000;',
    '  align-items: center;',
    '  justify-content: center;',
    '}',
    '#ai-overlay.open { display: flex; }',

    '#ai-panel {',
    '  background: var(--surface);',
    '  border: 1px solid var(--border);',
    '  border-radius: 14px;',
    '  width: min(640px, 92vw);',
    '  max-height: 82vh;',
    '  display: flex;',
    '  flex-direction: column;',
    '  overflow: hidden;',
    '}',

    '#ai-header {',
    '  display: flex;',
    '  align-items: center;',
    '  gap: 8px;',
    '  padding: 14px 18px;',
    '  border-bottom: 1px solid var(--border);',
    '  flex-shrink: 0;',
    '}',
    '#ai-title {',
    '  font-size: 0.82rem;',
    '  font-weight: 700;',
    '  letter-spacing: 0.08em;',
    '  text-transform: uppercase;',
    '  color: var(--accent);',
    '  flex-shrink: 0;',
    '}',
    '#ai-chapter-label {',
    '  font-size: 0.78rem;',
    '  color: var(--muted);',
    '  flex: 1;',
    '  overflow: hidden;',
    '  text-overflow: ellipsis;',
    '  white-space: nowrap;',
    '}',
    '#ai-close {',
    '  background: none;',
    '  border: none;',
    '  color: var(--muted);',
    '  font-size: 1rem;',
    '  cursor: pointer;',
    '  padding: 2px 6px;',
    '  border-radius: 4px;',
    '  flex-shrink: 0;',
    '  line-height: 1;',
    '}',
    '#ai-close:hover { color: var(--text); }',

    /* key pane */
    '#ai-key-pane {',
    '  padding: 30px 24px;',
    '  display: flex;',
    '  flex-direction: column;',
    '  gap: 14px;',
    '}',
    '#ai-key-pane p { font-size: 0.88rem; color: var(--muted); line-height: 1.65; }',
    '#ai-key-pane a { color: var(--accent); }',
    '#ai-key-input {',
    '  width: 100%;',
    '  background: var(--panel);',
    '  border: 1px solid var(--border);',
    '  color: var(--text);',
    '  font-family: monospace;',
    '  font-size: 0.85rem;',
    '  padding: 9px 12px;',
    '  border-radius: 6px;',
    '  outline: none;',
    '}',
    '#ai-key-input:focus { border-color: var(--accent); }',
    '#ai-key-save {',
    '  background: var(--accent);',
    '  border: none;',
    '  color: #fff;',
    '  font-size: 0.85rem;',
    '  padding: 9px 22px;',
    '  border-radius: 6px;',
    '  cursor: pointer;',
    '  align-self: flex-start;',
    '}',
    '#ai-key-save:hover { opacity: 0.88; }',

    /* chat pane */
    '#ai-chat-pane {',
    '  display: flex;',
    '  flex-direction: column;',
    '  flex: 1;',
    '  min-height: 0;',
    '}',
    '#ai-history {',
    '  flex: 1;',
    '  overflow-y: auto;',
    '  padding: 16px 18px;',
    '  display: flex;',
    '  flex-direction: column;',
    '  gap: 14px;',
    '  min-height: 120px;',
    '}',
    '.ai-q {',
    '  background: var(--panel);',
    '  border-radius: 8px 8px 2px 8px;',
    '  padding: 10px 14px;',
    '  font-size: 0.88rem;',
    '  color: var(--text);',
    '  align-self: flex-end;',
    '  max-width: 85%;',
    '}',
    '.ai-a {',
    '  font-size: 0.88rem;',
    '  color: var(--muted);',
    '  line-height: 1.7;',
    '  white-space: pre-wrap;',
    '  max-width: 92%;',
    '}',
    '.ai-err { color: #ff6b6b; font-size: 0.85rem; }',
    '.ai-thinking {',
    '  font-size: 0.82rem;',
    '  color: var(--muted);',
    '  font-style: italic;',
    '  animation: ai-pulse 1.2s ease-in-out infinite;',
    '}',
    '@keyframes ai-pulse { 0%,100%{opacity:.35} 50%{opacity:1} }',

    '#ai-input-row {',
    '  border-top: 1px solid var(--border);',
    '  padding: 12px 14px;',
    '  display: flex;',
    '  gap: 8px;',
    '  flex-shrink: 0;',
    '}',
    '#ai-textarea {',
    '  flex: 1;',
    '  background: var(--panel);',
    '  border: 1px solid var(--border);',
    '  color: var(--text);',
    '  font-family: system-ui, sans-serif;',
    '  font-size: 0.88rem;',
    '  padding: 8px 12px;',
    '  border-radius: 6px;',
    '  resize: none;',
    '  outline: none;',
    '  min-height: 38px;',
    '  max-height: 120px;',
    '  line-height: 1.4;',
    '}',
    '#ai-textarea:focus { border-color: var(--accent); }',
    '#ai-send {',
    '  background: var(--accent);',
    '  border: none;',
    '  color: #fff;',
    '  font-size: 0.85rem;',
    '  padding: 8px 18px;',
    '  border-radius: 6px;',
    '  cursor: pointer;',
    '  white-space: nowrap;',
    '  align-self: flex-end;',
    '  flex-shrink: 0;',
    '}',
    '#ai-send:disabled { opacity: 0.45; cursor: default; }',
    '#ai-send:not(:disabled):hover { opacity: 0.88; }',

    '#ai-footer {',
    '  padding: 6px 14px 10px;',
    '  font-size: 0.72rem;',
    '  color: var(--muted);',
    '  display: flex;',
    '  justify-content: space-between;',
    '  flex-shrink: 0;',
    '}',
    '#ai-change-key { cursor: pointer; text-decoration: underline; }',
    '#ai-change-key:hover { color: var(--accent); }',
    '#ai-footer-right { display: flex; gap: 12px; }',
    '#ai-new-convo { cursor: pointer; text-decoration: underline; }',
    '#ai-new-convo:hover { color: var(--accent); }',
  ].join('\n');
  document.head.appendChild(style);

  // ── Chapter context ───────────────────────────────────────────────────────
  function getCurrentChapter() {
    var sections = Array.from(document.querySelectorAll('section.chapter'));
    if (!sections.length) return { title: '', text: document.body.innerText.slice(0, 12000) };

    var best = null, bestPx = -1;
    sections.forEach(function (s) {
      var r   = s.getBoundingClientRect();
      var vis = Math.min(r.bottom, window.innerHeight) - Math.max(r.top, 0);
      if (vis > bestPx) { bestPx = vis; best = s; }
    });
    if (!best) best = sections[0];

    var titleEl = best.querySelector('h3') || best.querySelector('h2');
    var title   = titleEl ? titleEl.textContent.trim() : '';
    var text    = (best.innerText || best.textContent || '').trim();
    if (text.length > 12000) text = text.slice(0, 12000) + '\n[…truncated]';
    return { title: title, text: text };
  }

  // ── Gemini API call ───────────────────────────────────────────────────────
  var history    = [];   // [{role, parts:[{text}]}]
  var chapterCtx = '';

  function askGemini(apiKey, question) {
    var systemPrompt =
      'You are a patient, clear mathematics tutor. The student is reading a math textbook ' +
      'and has a question about the chapter shown below. Answer correctly and concisely. ' +
      'Show step-by-step working where it helps. Write in plain text only — ' +
      'do not use markdown symbols such as **, *, #, or backticks.\n\n' +
      'CHAPTER CONTENT:\n' + chapterCtx;

    history.push({ role: 'user', parts: [{ text: question }] });

    return fetch(MODEL_URL + apiKey, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        system_instruction: { parts: [{ text: systemPrompt }] },
        contents: history,
        generationConfig: { temperature: 0.25, maxOutputTokens: 900 }
      })
    }).then(function (resp) {
      return resp.json().then(function (data) {
        if (!resp.ok) throw new Error(data.error && data.error.message || 'HTTP ' + resp.status);
        var answer = (data.candidates &&
                      data.candidates[0] &&
                      data.candidates[0].content &&
                      data.candidates[0].content.parts &&
                      data.candidates[0].content.parts[0].text) || '(no response)';
        history.push({ role: 'model', parts: [{ text: answer }] });
        return answer;
      });
    });
  }

  // ── Build DOM ─────────────────────────────────────────────────────────────
  var triggerBtn = document.createElement('button');
  triggerBtn.id   = 'ai-btn';
  triggerBtn.type = 'button';
  triggerBtn.textContent = 'Ask AI';

  var overlay = document.createElement('div');
  overlay.id = 'ai-overlay';
  overlay.setAttribute('role', 'dialog');
  overlay.setAttribute('aria-modal', 'true');
  overlay.setAttribute('aria-label', 'Ask AI tutor');
  overlay.innerHTML =
    '<div id="ai-panel">' +

    /* header */
    '<div id="ai-header">' +
    '<span id="ai-title">Ask AI</span>' +
    '<span id="ai-chapter-label"></span>' +
    '<button id="ai-close" aria-label="Close">×</button>' +
    '</div>' +

    /* API key pane */
    '<div id="ai-key-pane">' +
    '<p>Enter your free <strong>Google Gemini API key</strong> to enable AI tutoring.<br>' +
    'Get one at <a href="https://aistudio.google.com/apikey" target="_blank" rel="noopener">aistudio.google.com/apikey</a> — no credit card required.</p>' +
    '<input id="ai-key-input" type="password" placeholder="AIza…" autocomplete="off" spellcheck="false" />' +
    '<button id="ai-key-save">Save &amp; Continue</button>' +
    '</div>' +

    /* chat pane */
    '<div id="ai-chat-pane" style="display:none">' +
    '<div id="ai-history"></div>' +
    '<div id="ai-input-row">' +
    '<textarea id="ai-textarea" rows="2" placeholder="Ask about this chapter…"></textarea>' +
    '<button id="ai-send">Send</button>' +
    '</div>' +
    '<div id="ai-footer">' +
    '<span>Gemini 2.5 Flash · current chapter as context</span>' +
    '<span id="ai-footer-right">' +
    '<span id="ai-new-convo">new conversation</span>' +
    '<span id="ai-change-key">change key</span>' +
    '</span>' +
    '</div>' +
    '</div>' +

    '</div>'; /* #ai-panel */

  document.body.appendChild(overlay);

  // ── Helpers ───────────────────────────────────────────────────────────────
  var apiKey = localStorage.getItem(LS_KEY) || '';

  function el(id) { return document.getElementById(id); }

  function showKeyPane() {
    el('ai-key-pane').style.display  = '';
    el('ai-chat-pane').style.display = 'none';
  }
  function showChatPane() {
    el('ai-key-pane').style.display  = 'none';
    el('ai-chat-pane').style.display = '';
    setTimeout(function () { el('ai-textarea').focus(); }, 60);
  }

  function appendBubble(text, cls) {
    var div = document.createElement('div');
    div.className   = cls;
    div.textContent = text;
    el('ai-history').appendChild(div);
    div.scrollIntoView({ block: 'nearest' });
    return div;
  }

  function openModal() {
    var ch    = getCurrentChapter();
    chapterCtx = ch.text;
    el('ai-chapter-label').textContent = ch.title ? '· ' + ch.title : '';
    overlay.classList.add('open');
    apiKey ? showChatPane() : showKeyPane();
  }
  function closeModal() { overlay.classList.remove('open'); }

  function startNewConversation() {
    history = [];
    el('ai-history').innerHTML = '';
  }

  // ── Events ────────────────────────────────────────────────────────────────
  triggerBtn.addEventListener('click', openModal);
  el('ai-close').addEventListener('click', closeModal);
  overlay.addEventListener('click', function (e) { if (e.target === overlay) closeModal(); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeModal(); });

  el('ai-key-save').addEventListener('click', function () {
    var val = el('ai-key-input').value.trim();
    if (!val) return;
    apiKey = val;
    localStorage.setItem(LS_KEY, val);
    showChatPane();
  });
  el('ai-key-input').addEventListener('keydown', function (e) {
    if (e.key === 'Enter') el('ai-key-save').click();
  });

  el('ai-change-key').addEventListener('click', showKeyPane);
  el('ai-new-convo').addEventListener('click', startNewConversation);

  function sendQuestion() {
    var ta       = el('ai-textarea');
    var sendBtn  = el('ai-send');
    var question = ta.value.trim();
    if (!question || !apiKey) return;

    ta.value = '';
    ta.style.height = '';
    sendBtn.disabled = true;

    appendBubble(question, 'ai-q');

    var thinking = document.createElement('div');
    thinking.className   = 'ai-thinking';
    thinking.textContent = 'Thinking…';
    el('ai-history').appendChild(thinking);
    thinking.scrollIntoView({ block: 'nearest' });

    askGemini(apiKey, question).then(function (answer) {
      thinking.remove();
      appendBubble(answer, 'ai-a');
    }).catch(function (err) {
      thinking.remove();
      appendBubble('Error: ' + err.message, 'ai-a ai-err');
      if (/API_KEY|401|403/.test(err.message)) {
        apiKey = '';
        localStorage.removeItem(LS_KEY);
        setTimeout(showKeyPane, 1400);
      }
    }).then(function () {
      sendBtn.disabled = false;
      ta.focus();
    });
  }

  el('ai-send').addEventListener('click', sendQuestion);
  el('ai-textarea').addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendQuestion(); }
  });
  el('ai-textarea').addEventListener('input', function () {
    this.style.height = '';
    this.style.height = Math.min(this.scrollHeight, 120) + 'px';
  });

  // ── Inject trigger button into header ────────────────────────────────────
  function init() {
    var header = document.querySelector('header');
    if (header) header.appendChild(triggerBtn);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
}());
