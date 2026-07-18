# Math Game — Project Guide

## Architecture Overview

| File | Role |
|---|---|
| `index.html` | Single-file game app — all CSS, HTML, JS inline |
| `puzzles/*.json` | One JSON array per topic |
| `textbook_*.html` | One standalone textbook per topic |
| `math_<subject>_diagrams.html` | One interactive diagram page per subject (7 of 11 exist so far) |
| `diagrams.html` | Hub linking to every diagram page, in canonical curriculum order |
| `manual.html` | Player manual |
| `katex/` | KaTeX 0.16.9 vendored locally (js, css, fonts, auto-render) — no CDN dependency |
| `textbook-notes.js` | Shared script — per-box and per-section notes for all textbooks |
| `textbook-nav.js` | Shared script — wires `.toc-back` links with scroll-position memory |
| `textbook-switcher.js` | Shared script — injects the cross-textbook tab bar (also used on `index.html` and `diagrams.html`) |
| `textbook-glossary.js` | Shared script — hover/tap/keyboard glossary tooltips for `.key` terms |
| `textbook-ai.js` | Shared script — "Ask AI" tutor modal (Gemini) |
| `theme-toggle.js` | Shared script — light/dark theme toggle |

---

## Adding a New Topic — Checklist

When adding a new topic (e.g., Linear Algebra), update these locations:

1. **`textbook-switcher.js`'s `BOOKS` array** (NOT `index.html` — the header no longer
   lists textbooks individually; it just loads this shared script):
   ```js
   { file: 'textbook_TOPIC.html', label: 'TOPIC Name' },
   ```

2. **Topic select** (`<select id="topic-select">` in `index.html`):
   ```html
   <option value="TOPIC.json">TOPIC Name</option>
   ```

3. **`TOPIC_META`** object in `index.html` (used by concept-search tab AND as the
   single source of truth `preloadTopicCache()` derives its fetch list from —
   adding an entry here is enough, no second file list to keep in sync):
   ```js
   'PREFIX': { file: 'TOPIC.json', topicIndex: N },
   ```

4. **`TEXTBOOK_MAP`** object in `index.html` (used by the puzzle context bar's
   "📖 Read about this topic →" link):
   ```js
   'PREFIX': 'textbook_TOPIC.html',
   ```

5. **`DIAGRAMS_MAP`** object in `index.html` — only once this topic gets a
   `math_TOPIC_diagrams.html` page (see **Diagram Pages** below):
   ```js
   'PREFIX': 'math_TOPIC_diagrams.html',
   ```

### Current topicIndex assignments
`topicIndex` for the main "By Topic" browse flow is computed live as `topicSel.selectedIndex` — i.e. the option's position in `#topic-select`, not a hardcoded constant. **New topics must be appended as the last `<option>`**, never inserted mid-list, or every topic after the insertion point silently gets a new topicIndex and a different "global puzzle number."

| topicIndex | Topic | Puzzle prefix |
|---|---|---|
| 0 | algebra | alg |
| 1 | algebra2 | alg2 |
| 2 | arithmetic | arith |
| 3 | arithmetic2 | arith2 |
| 4 | combinatorics | comb |
| 5 | geometry | geo |
| 6 | trigonometry | trig |
| 7 | calculus | calc |
| 8 | statistics | stat |
| 9 | linearalgebra | linalg |
| 10 | graphtheory | graph |

**Global puzzle number formula:** `topicIndex * 30 + idxInTopic + 1`

`TOPIC_META` now covers all 11 topics with `topicIndex` values matching the table
above exactly, so a concept-loaded puzzle's "Problem #" always agrees with the
number the same puzzle shows in topic-browse mode. Keep it that way: whenever a
topic is appended to `#topic-select`, its `TOPIC_META` entry must get the matching
new `topicIndex`, not be left out or left stale.

---

## Puzzle JSON Schema

```json
{
  "id": "PREFIX-e-001",
  "topic": "topicname",
  "difficulty": "easy | medium | hard",
  "chapter": 3,
  "question": { "latex": "...", "plain": "..." },
  "symbols": { "x": "description" },
  "palette": [
    { "id": "p1", "latex": "...", "description": "..." }
  ],
  "steps": [
    {
      "id": "s1",
      "fromLatex": "equation shown to user WITH drop zones",
      "toLatex": "equation shown AFTER step completes",
      "paletteRef": "p1",
      "dropTargets": ["exact substring of fromLatex"],
      "dropSideLabels": ["left side", "right side"],
      "description": "explanation shown as green callout"
    }
  ]
}
```

### CRITICAL: dropTargets must exactly match substrings of fromLatex

Every string in `dropTargets` is located via `fromLatex.indexOf(target)`. If it doesn't match character-for-character, the drop zone won't render.

**Always validate before committing:**
```python
import json
with open('puzzles/TOPIC.json') as f:
    d = json.load(f)
errors = []
for p in d:
    for s in p['steps']:
        fl = s.get('fromLatex', '')
        for t in s.get('dropTargets', []):
            if t not in fl:
                errors.append(f'{p["id"]} {s["id"]}: {repr(t[:50])} not in fromLatex')
print(errors or 'All dropTargets valid ✓')
```

### Coverage requirement
Every chapter must have **≥ 2 Easy, 2 Medium, 2 Hard** puzzles.
All new puzzles must include the `"chapter"` field (integer).

### Auto-steps vs. interactive steps
- `paletteRef: null` + `dropTargets: []` → auto-step (shown without user interaction)
- `paletteRef: "p1"` + `dropTargets: [...]` → interactive (user drags p1 to the zones)

---

## Textbook HTML Conventions

**File naming:** `textbook_TOPICNAME.html` (all lowercase, no spaces)

**Chapter anchor IDs:** `id="ch1"`, `id="ch2"`, ... `id="chN"`
- The game's textbook link bar uses `textbook_TOPIC.html#ch{puzzle.chapter}` to deep-link
- Do NOT use `id="chapter-1"` or other variants

**TOC navigation (required in every textbook):**

1. The `<nav>` element that holds the table of contents **must** have `id="toc"`:
   ```html
   <nav class="toc" id="toc">
   ```

2. Every chapter/section **must** end with a "↑ Table of Contents" back-link, placed immediately before `</section>`:
   ```html
   <p class="toc-back"><a href="#toc">↑ Table of Contents</a></p>
   </section>
   ```

3. Add this CSS (once per file, inside `<style>`):
   ```css
   .toc-back { text-align: right; margin-top: 1.5rem; padding-top: 0.9rem;
               border-top: 1px solid var(--panel, var(--border)); }
   .toc-back a { color: var(--muted); font-size: 0.82rem; text-decoration: none;
                 letter-spacing: 0.03em; }
   .toc-back a:hover { color: var(--accent); }
   ```

**Validation:** Run this to confirm every section has a matching back-link:
```python
body = src.split('</style>', 1)[1]
assert body.count('</section>') == body.count('toc-back'), "sections/links mismatch"
```

**Standard CSS classes:**
| Class | Use |
|---|---|
| `.chapter` | Wraps each chapter section |
| `.chapter-num` | "Chapter N" label (accent color) |
| `.definition` | Orange-bordered definition box |
| `.formula` | Blue-bordered formula box |
| `.example` | Green-bordered worked example |
| `.neural` | Purple-bordered neural architecture connection callout (Linear Algebra only) |
| `.ai-note` | Teal-bordered AI/ML-relevance sidebar (Graph Theory only) |

**The `.neural` callout** appears **only in Linear Algebra** and any advanced topics that branch from it (e.g., future advanced linear algebra, numerical methods). All other textbooks except Graph Theory — Arithmetic, Algebra, Geometry, Trigonometry, Statistics, Calculus — must **not** include `.neural` boxes or neural-network-specific content. General technology or computing references (binary, floating-point, cryptography) are acceptable in motivation paragraphs for those textbooks; explicit AI/ML/neural network framing is not.

**The `.ai-note` callout** appears **only in Graph Theory**, by explicit design: the chapters are standard, comprehensive graph theory (not an AI course), but each chapter carries one short sidebar connecting the concept to its use in neural nets/AI (computational graphs, GNNs, attention-as-graph, etc.). Visually distinct from `.neural` (own color, teal) so it doesn't read as a re-skin of the Linear Algebra callout. Do not use `.ai-note` in any other textbook — same containment principle as `.neural`.

**Motivation paragraph** — every chapter must open with a paragraph explaining *why* the concept matters before any definitions or formulas appear. The paragraph should answer at least one of: what problem does this solve, what would break without it, or how does it connect to something the reader already cares about. Real-world anchors (navigation, signal processing, robotics, ML) are preferred over abstract justification. This paragraph goes after `<h3>` and before the first technical `<p>`. (Exception: Linear Algebra uses `<h2>` for chapter titles and `<h3>` for sub-sections — insert after `<h2>` in that file.)

**SVG diagram** — every chapter must include exactly one diagram, placed in a `.formula` div immediately after the motivation paragraph:
```html
<div class="formula" style="display:flex;flex-direction:column;align-items:center;gap:0;padding-bottom:8px;">
  <div class="label" style="align-self:flex-start;">Diagram — [description]</div>
  <svg width="260" height="N" viewBox="0 0 260 N" aria-label="[full description for screen readers]">
    ...
  </svg>
</div>
```
SVG rules:
- All coordinate points must fall within the declared `viewBox`; verify with a script after writing (see Lessons)
- Polygons labeled as "squares" must have all four sides equal — compute distances explicitly before committing
- Use the project palette: `#5c8aff` blue, `#3ecf8e` green, `#ffb830` amber, `#ff6b6b` red, `#8a8ab5` muted
- Always include `aria-label` on the `<svg>` element

**Required structure per textbook:**
1. `<a class="back-link" href="index.html">← Back to Math Game</a>`
2. `<h1>`, `.subtitle`, optional `.tagline`
3. `<nav class="toc">` with ordered list linking to `#ch1` ... `#chN`
4. One `<section class="chapter" id="chN">` per chapter
5. Appendix section (after the last chapter, before any footer):
   ```html
   <section class="chapter" id="appendix-resources">
     <div class="chapter-num">Appendix</div>
     <h3>Interactive Resources</h3>
     <p>...</p>
     <ul>
       <li><a href="URL" target="_blank" rel="noopener">Name</a> — description</li>
     </ul>
     <p class="toc-back"><a href="#toc">↑ Table of Contents</a></p>
   </section>
   ```
6. `.attribution` footer
7. All five shared scripts at the bottom of `<body>`, plus the glossary data + script
   if this textbook has `.key` terms (see **Glossary tooltips** below):
   ```html
   <script src="textbook-switcher.js"></script>
   <script src="textbook-notes.js"></script>
   <script src="textbook-nav.js"></script>
   <script src="theme-toggle.js"></script>
   <script src="textbook-ai.js"></script>
   <script>
   var GLOSSARY = { 'term': 'one-sentence definition', ... };
   </script>
   <script src="textbook-glossary.js"></script>
   ```

**Interactive Resources appendix** — each textbook's appendix links to free, interactive tools that let readers explore the same concepts dynamically. Keep 2–4 links; prefer tools that closely match the textbook's specific topic arc rather than generic math sites.

**Textbook switcher nav bar** (`textbook-switcher.js`) — injected dynamically after the first `<header>` element on the page (works on any page that has one — every textbook, plus `index.html` and `diagrams.html`, each of which now wraps its title in `<header>` specifically so this script has an anchor point). Renders as a horizontal carousel (single row, `overflow-x: auto`, hidden scrollbar, edge-fade `mask-image` since the scrollbar itself is hidden) constrained to the same `.page`/`#layout` max-width as the surrounding content. An `EXTRAS` array prepends "◂ Game" and "Diagrams" entries (visually separated by a border) before the `BOOKS` list, so this bar doubles as the site's one persistent nav, not just a textbook-to-textbook switcher. Active page marked with `class="current"` and `aria-current="page"`.

**AI tutor modal** (`textbook-ai.js`) — injects an "Ask AI" button into the textbook header. On click, opens a modal that detects the most-visible `section.chapter` on screen, sends its `innerText` (capped at 12 000 chars) as system context to Google Gemini 2.5 Flash, and streams back a plain-text answer. API key stored in `localStorage` under `gemini-api-key`; first-time use shows a key-entry pane with a link to aistudio.google.com/apikey. The conversation transcript (`history`) persists across opening/closing the modal within the same page load — only the chapter context (`chapterCtx`) refreshes on each open, to whatever section is currently most visible. Click "new conversation" in the modal's footer to clear the transcript explicitly. Script must be loaded after `theme-toggle.js` so its button appends to the header after the theme toggle.

---

## Diagram Pages (`math_<subject>_diagrams.html`)

One diagram page per textbook, named `math_<subject>_diagrams.html` (e.g. `math_calculus_diagrams.html`).

**Current coverage (7 of 11 subjects):** Arithmetic, Intermediate Arithmetic, Calculus,
Combinatorics, Graph Theory, Linear Algebra, Statistics. Algebra, Algebra 2, Geometry,
and Trigonometry don't have one yet — they show as a dimmed "soon" card on the hub.

**`diagrams.html` (the hub)** lists every subject in the same curriculum order as
`textbook-switcher.js`'s `BOOKS` array — live subjects get a full card linking to
their page, subjects without one yet get a `.diagram-card.soon` placeholder in
their correct position. Don't reintroduce a separate trailing "Coming Soon"
section — a past version of this page did that and it made a finished page
(Statistics) look unfinished by sitting below the placeholder block.

**Reciprocal links:** every textbook that has a diagram page links to it via a
"Diagrams →" header link, and every diagram page links back via a "Textbook →"
header link. When a new topic gets its diagram page written, add both links and
the `DIAGRAMS_MAP` entry in `index.html` (see checklist above) so the puzzle
context bar's "🖼 See diagrams →" link appears too.

## Diagram Viewer — `math_calculus_diagrams.html`

A standalone page for SVG diagram walkthroughs. Two diagram types coexist:

**Step-through** (`.step-viewer`): static SVG steps, one visible at a time. Navigation: Prev/Next buttons + progress dots + arrow-key support. Add steps by appending `.step` divs; update `.tot` span and `.step-dots` count. Each step-through has its own IIFE controller at the bottom (`document.querySelectorAll('.step-viewer').forEach(...)`).

**Interactive** (`.interactive-diagram`): live SVG redrawn on slider input. The Riemann sum diagram uses `<g id="r-rects">` for dynamic rectangle injection; JS reads the slider, recomputes the left Riemann sum, sets `innerHTML` on the rect group, and updates the convergence bar. Add new interactive sets with their own slider ids and a separate IIFE.

**SVG coordinate systems:**
- Derivative diagram: `viewBox="0 0 260 200"`, `sx(x)=40+x*46`, `sy(y)=170-y*7.5` (x∈[0,4.5], y∈[0,16])
- Riemann diagram: `viewBox="0 0 300 240"`, `sx(x)=40+x*80`, `sy(y)=210-y*21` (x∈[0,3], y∈[0,9])

Always verify coordinate bounds with a Python script before committing new SVG content.

---

## Light / Dark Theme System

All HTML pages (textbooks, game, manual) share a single theme toggle.

**Files involved:**
- `theme-toggle.js` — injects the toggle button, light-theme CSS override, and localStorage persistence
- Anti-FOUC inline script in every `<head>` — applies saved theme before first paint to prevent flash

**Adding theme support to a new page** — add both of these:

1. Anti-FOUC script (inside `<head>`, after `<style>`):
```html
<script>(function(){var t=localStorage.getItem('math-theme')||((window.matchMedia&&window.matchMedia('(prefers-color-scheme:light)').matches)?'light':'dark');document.documentElement.setAttribute('data-theme',t);}());</script>
```

2. Light-theme CSS override (inside `<style>`, at the end):
```css
[data-theme="light"] {
  --bg:      #f5f0e4;
  --surface: #faf7ee;
  --panel:   #ede8d8;
  --border:  #ccc6b4;
  --text:    #18140c;
  --muted:   #3e3c60;
  --accent:  #2858c8;
  --correct: #115238;
  --hint:    #6e4a00;
  --wrong:   #cc2040;
}
[data-theme="light"] section h3 { color: #18140c; }
[data-theme="light"] .chapter-num { color: #3e3c60; }
```

3. Script tag at the bottom of `<body>` (after other shared scripts):
```html
<script src="theme-toggle.js"></script>
```

**Button placement:** `theme-toggle.js` looks for a `<header>` element and appends the button there with `margin-left:auto` — this requires `header { display:flex; ... }` on that page (every textbook has this; `index.html` and `manual.html` do too, specifically so this works). If no `<header>` is found, it falls back to a fixed position at top-right — currently only `textbook_linearalgebra.html` and `textbook_statistics.html` use the older `<a class="back-link">` pattern instead of `<header>`, so they hit this fallback.

**Storage key:** `localStorage` key is `math-theme`, values `'light'` or `'dark'`.

---

## Textbook Shared Scripts

### `textbook-notes.js`
Injects note-taking UI into every textbook. No HTML changes needed beyond the `<script>` tag.

- **Per-box notes**: every `.formula`, `.example`, and `.definition` block gets a `✎` button (top-right, absolutely positioned). Click to open a textarea; saves to `localStorage` keyed by section ID + box index.
- **Per-section notes**: a `📝 Section Notes` button is injected after the `h2`/`h3` heading of each `<section>`. Click to expand a textarea for chapter-level notes.
- **Toolbar**: a fixed bottom bar (↓ Export / ✕ Clear all) slides up whenever any note exists.
- **Export**: downloads all notes as a `.txt` file, section notes first then per-box notes in reading order.

### `textbook-nav.js`
Enhances the `.toc-back` links already in the HTML — does **not** inject its own links.

- Wires each `.toc-back a` with a click handler that saves the current scroll position, then smooth-scrolls to the `<nav id="toc">`.
- Injects a `↩ Back to where I was` button inside the TOC nav that returns the user to their saved position.

**CRITICAL — never inject duplicate TOC links.** The `.toc-back` HTML links are the single source of truth. `textbook-nav.js` wires them; it must never create additional `<a>` elements for the same purpose. Past mistake: an earlier version appended `<a href="#">↑ Table of Contents</a>` to every section, creating a visible duplicate alongside the HTML `.toc-back`.

### `textbook-glossary.js`
Optional — only activates if the page defines a global `GLOSSARY` object before this script loads (`{ 'term': 'definition', ... }`, keyed by the exact trimmed `.textContent` of each `.key` span). No-ops harmlessly if `GLOSSARY` is undefined, so it's safe to include in every textbook's script list even before that textbook has any glossary content.

- Injects its own CSS (`.key` gets `cursor: help` + dotted underline; `#glossary-tip` floating box) and the `#glossary-tip` div — no manual HTML/CSS needed per textbook beyond the `GLOSSARY` object itself.
- **Desktop** (`hover: hover` media query true at load): standard `mouseenter`/`mousemove`/`mouseleave`, tooltip follows the cursor.
- **Touch** (`hover: none`, e.g. iPad): tap-to-toggle via `touchend` — tap a term to open it, tap it again or tap anywhere else on the page to close. Deliberately does **not** use `click`: WebKit only synthesizes a click event reliably for elements that already look interactive (own listener / `cursor: pointer`), so a tap on a plain paragraph elsewhere on the page never produced one, leaving the tooltip stuck open with the old mouseenter/mouseleave-only approach. `touchend` fires unconditionally regardless of element type. `hover: hover` is checked once at load, not tracked live — not worth handling a mouse/trackpad being attached mid-session on a hybrid device.
- **Keyboard**: every glossary-backed `.key` term also gets `tabindex="0"` plus `focus`/`blur` handlers, wired once up front regardless of which pointer branch above applies. The tooltip positions itself under the element's bounding rect (no mouse coordinates available on focus) rather than following a cursor.
- **Coverage**: every unique `.key` term in a textbook must have a matching `GLOSSARY` entry. Validate with a script comparing `re.findall(r'<span class="key">([^<]*)</span>', html)` (unique, trimmed) against the `GLOSSARY` object's keys — mismatches in either direction are bugs (missing = silently no tooltip; extra = dead entry, usually means the term's wording changed in the prose).
- **Line-wrap trap**: if a `<span class="key">` gets wrapped across multiple source lines during editing, its `.textContent` includes the embedded newline/indentation, so it will never match a clean `GLOSSARY` key. Keep every `.key` span on one line, or verify with the coverage script above (it will surface these as "missing").

---

## Game Mechanic Notes

### Drop zone rendering
`buildDropZoneEquation(fromLatex, targets, container)` finds each target string in `fromLatex`, wraps it in `\htmlClass{dz-N}{...}` via KaTeX, then promotes those elements to `.drop-zone` spans, each `tabindex`-managed (see **Palette interaction** below).

### Hover behavior
`#step-eq:hover .drop-zone:not(.done)` reveals all pending drop zones in blue (8% opacity) when the cursor is anywhere in the equation block.

### Drop stamp
Correct drops append a `.drop-stamp` badge (green, positioned above the zone) rendering the palette item's LaTeX — so the user sees the operation applied to both sides.

### Step description callout
`step.description` renders in `#step-desc` as a green left-bordered callout box (`aria-live="polite"`, along with `#side-message` and `#completion`, so screen readers hear step/feedback changes). Always write descriptions that explain the **why**, not just the what. Neural architecture context is welcome here.

### Palette interaction: drag, tap, and keyboard
Three input paths all funnel into the same `handleDrop(dz, dzIdx, paletteId)`:
- **Mouse drag**: native HTML5 drag-and-drop (`draggable`, `dragstart`/`dragend` on palette items; `dragover`/`drop` on drop zones).
- **Tap-to-select** (mouse click or touch tap — deliberately just a `click` listener, not touch-specific handlers, so it never blocks page scroll): tap a palette item to select it (`.touch-selected` highlight), tap a drop zone to place it. A wrong placement keeps the selection so you can immediately retry a different zone; a correct one clears it.
- **Keyboard**: palette items and drop zones are `role="button"` with `tabindex` kept in sync (`-1` once `.used`/`.done`, `0` otherwise); Enter/Space triggers the identical select/place logic as tap.

### Streak counter
`G.score.streak` increments only on clean puzzle solves (no hints). `G.cleanSolve` resets to `true` on `loadPuzzle()` and `reset-btn`. Both "Give Up This Step" (`activateHint()`) and the arrow-key animated auto-solve (`animatedSolve()`) route through the shared `markHintUsed()` helper, which sets `G.cleanSolve = false`, increments the hint counter, and persists the score — arrow-keying through a step costs a hint just like giving up does, it is not a free auto-solve.

### Score & progress persistence
`G.score` (`solved`/`hints`/`streak`/`bestStreak`) is persisted to `localStorage` under `math-score` via `saveScore()`/`loadScore()`; a `Set` of solved puzzle IDs is persisted under `math-solved-ids` via `markPuzzleSolved()`. Both the topic- and concept-browse puzzle dropdowns prefix a solved puzzle's option text with `✓`. The puzzle dropdown is also grouped with `<optgroup>` — by chapter when every puzzle in that topic file actually has one (currently only Graph Theory and Linear Algebra), otherwise by difficulty — with question text word-boundary-truncated (~50 chars) and the full text kept in the option's `title` attribute.

### Game notes export
The "📝 Notes" modal's footer has a "↓ Export all" button (`exportAllNotes()`) that dumps every `notes.<puzzle-id>` key in `localStorage` into one downloaded `.txt` file — the per-puzzle-notes equivalent of `textbook-notes.js`'s export.

### Accessibility
- `prefers-reduced-motion: reduce` disables the ghost-fly ArrowRight animation (jumps straight to the result), the palette/drop-zone hint pulse animation, and swaps `textbook-nav.js`'s smooth-scrolling for instant jumps.
- The Σ (sigma) expansion modal moves focus to its close button on open and restores focus to whatever triggered it on close.
- Dark-theme `--muted` is `#8a8ab5` (not the old `#7070a0`, which computed under WCAG AA contrast at the small sizes used for switcher tabs and TOC links) — keep this value if you add `--muted` to a new page.

### KaTeX is vendored locally
All pages load KaTeX from `katex/` (relative path), not a CDN — this is a self-hosted LAN site, so a missing internet connection must not break every equation on the page. If KaTeX needs a version bump, re-download the npm tarball's `dist/` folder (js, css, fonts, `contrib/auto-render.min.js`) into `katex/` rather than pointing back at `cdn.jsdelivr.net`.

---

## Lessons from Past Work

- **Don't add interactive features to textbooks** without explicit user request. The unit circle modal was added to `textbook_trigonometry.html` and then reverted. Keep textbooks as reading-only references.
- **Large puzzle JSON**: Write chapters 1–5 first, validate, then append chapters 6–10 via Python script rather than one massive Write call.
- **LaTeX in JSON**: Backslashes double in JSON strings (`\mathbf` → `"\\mathbf"`). Matrix row breaks `\\` become `"\\\\"`. Test in KaTeX playground if unsure.
- **Push after each major feature**: User expects a `git push` after completing a textbook, puzzle file, or significant game enhancement.
- **Never use `href="#"` for non-navigation actions**: Use `<button type="button">` instead. `<a href="#">` pollutes the browser status bar with a `#` URL and looks like a navigation link to the user.
- **Wire existing elements, don't duplicate them**: When a shared JS script needs to enhance links already in the HTML, add event listeners to those elements — never append new elements with the same visible text.
- **SVG coordinate verification**: After writing SVG diagrams, audit with:
  ```python
  import re
  with open('textbook_TOPIC.html') as f: src = f.read()
  for m in re.finditer(r'viewBox="0 0 (\d+) (\d+)"[^>]*>(.*?)</svg>', src, re.S):
      W, H = int(m.group(1)), int(m.group(2))
      for pt in re.findall(r'[\d.]+,[\d.]+', m.group(3)):
          x, y = map(float, pt.split(','))
          if x > W+5 or y > H+5: print(f'OOB ({x},{y}) in {W}×{H}')
  ```
  Past bugs caught this way: Pythagorean theorem polygons were rectangles (not squares), a discriminant Δ=0 parabola was a W-shape (two roots instead of one), and a critical-points curve clipped 14px below its viewBox.
