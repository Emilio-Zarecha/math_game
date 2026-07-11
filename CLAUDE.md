# Math Game — Project Guide

## Architecture Overview

| File | Role |
|---|---|
| `index.html` | Single-file game app — all CSS, HTML, JS inline |
| `puzzles/*.json` | One JSON array per topic |
| `textbook_*.html` | One standalone textbook per topic |
| `manual.html` | Player manual |

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

**Standard CSS classes:**
| Class | Use |
|---|---|
| `.chapter` | Wraps each chapter section |
| `.chapter-num` | "Chapter N" label (accent color) |
| `.definition` | Orange-bordered definition box |
| `.formula` | Blue-bordered formula box |
| `.example` | Green-bordered worked example |
| `.neural` | Purple-bordered neural architecture connection callout |

**The `.neural` callout** (added in Linear Algebra textbook) must appear in every chapter of every new textbook. It shows how the chapter's math connects to neural networks, LLMs, or World Models.

**Required structure per textbook:**
1. `<a class="back-link" href="index.html">← Back to Math Game</a>`
2. `<h1>`, `.subtitle`, optional `.tagline`
3. `<nav class="toc">` with ordered list linking to `#ch1` ... `#chN`
4. One `<section class="chapter" id="chN">` per chapter
5. `.attribution` footer

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
