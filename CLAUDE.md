# Math Game — Project Guide

## Architecture Overview

| File | Role |
|---|---|
| `index.html` | Single-file game app — all CSS, HTML, JS inline |
| `puzzles/*.json` | One JSON array per topic |
| `textbook_*.html` | One standalone textbook per topic |
| `manual.html` | Player manual |
| `textbook-notes.js` | Shared script — per-box and per-section notes for all textbooks |
| `textbook-nav.js` | Shared script — wires `.toc-back` links with scroll-position memory |

---

## Adding a New Topic — Checklist

When adding a new topic (e.g., Linear Algebra), update **all four** locations in `index.html`:

1. **Header links** (`<div class="header-links">`):
   ```html
   <a class="textbook-link" href="textbook_TOPIC.html">TOPIC Textbook</a>
   ```

2. **Topic select** (`<select id="topic-select">`):
   ```html
   <option value="TOPIC.json">TOPIC Name</option>
   ```

3. **`TOPIC_META`** object (used by concept-search tab):
   ```js
   'PREFIX': { file: 'TOPIC.json', topicIndex: N },
   ```

4. **`TEXTBOOK_MAP`** object (used by textbook link bar):
   ```js
   'PREFIX': 'textbook_TOPIC.html',
   ```

### Current topicIndex assignments
| topicIndex | Topic | Puzzle prefix |
|---|---|---|
| 0 | algebra | alg |
| 1 | algebra2 | alg2 |
| 2 | arithmetic | arith |
| 3 | geometry | geo |
| 4 | trigonometry | trig |
| 5 | calculus | calc |
| 6 | statistics | stat |
| 7 | linearalgebra | linalg |

**Global puzzle number formula:** `topicIndex * 30 + idxInTopic + 1`

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
| `.neural` | Purple-bordered neural architecture connection callout |

**The `.neural` callout** appears **only in Linear Algebra** and any advanced topics that branch from it (e.g., future advanced linear algebra, numerical methods). All other textbooks — Arithmetic, Algebra, Geometry, Trigonometry, Statistics, Calculus — must **not** include `.neural` boxes or neural-network-specific content. General technology or computing references (binary, floating-point, cryptography) are acceptable in motivation paragraphs for those textbooks; explicit AI/ML/neural network framing is not.

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
- Use the project palette: `#5c8aff` blue, `#3ecf8e` green, `#ffb830` amber, `#ff6b6b` red, `#7070a0` muted
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
7. All five shared scripts at the bottom of `<body>`:
   ```html
   <script src="textbook-switcher.js"></script>
   <script src="textbook-notes.js"></script>
   <script src="textbook-nav.js"></script>
   <script src="theme-toggle.js"></script>
   <script src="textbook-ai.js"></script>
   ```

**Interactive Resources appendix** — each textbook's appendix links to free, interactive tools that let readers explore the same concepts dynamically. Keep 2–4 links; prefer tools that closely match the textbook's specific topic arc rather than generic math sites.

**Textbook switcher nav bar** (`textbook-switcher.js`) — injected dynamically after `<header>` in every textbook. Renders as a horizontal carousel (single row, `overflow-x: auto`, hidden scrollbar) constrained to the same `.page` max-width (820px) as the chapter sections. Lists all 8 textbooks in curriculum order; active page marked with `class="current"` and `aria-current="page"`.

**AI tutor modal** (`textbook-ai.js`) — injects an "Ask AI" button into the textbook header. On click, opens a modal that detects the most-visible `section.chapter` on screen, sends its `innerText` (capped at 12 000 chars) as system context to Google Gemini 2.0 Flash, and streams back a plain-text answer. API key stored in `localStorage` under `gemini-api-key`; first-time use shows a key-entry pane with a link to aistudio.google.com/apikey. Multi-turn conversation resets each time the modal is opened. Script must be loaded after `theme-toggle.js` so its button appends to the header after the theme toggle.

---

## Diagram Pages (`math_<subject>_diagrams.html`)

One diagram page per textbook, named `math_<subject>_diagrams.html` (e.g. `math_calculus_diagrams.html`). Currently only the calculus page exists.

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

**Button placement:** `theme-toggle.js` looks for a `<header>` element and appends the button there (textbooks). If none is found (game, manual), it falls back to a fixed position at top-right.

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

---

## Game Mechanic Notes

### Drop zone rendering
`buildDropZoneEquation(fromLatex, targets, container)` finds each target string in `fromLatex`, wraps it in `\htmlClass{dz-N}{...}` via KaTeX, then promotes those elements to `.drop-zone` spans.

### Hover behavior
`#step-eq:hover .drop-zone:not(.done)` reveals all pending drop zones in blue (8% opacity) when the cursor is anywhere in the equation block.

### Drop stamp
Correct drops append a `.drop-stamp` badge (green, positioned above the zone) rendering the palette item's LaTeX — so the user sees the operation applied to both sides.

### Step description callout
`step.description` renders in `#step-desc` as a green left-bordered callout box. Always write descriptions that explain the **why**, not just the what. Neural architecture context is welcome here.

### Streak counter
`G.score.streak` increments only on clean puzzle solves (no hints). `G.cleanSolve` resets to `true` on `loadPuzzle()` and `reset-btn`. It is set to `false` in `activateHint()`.

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
