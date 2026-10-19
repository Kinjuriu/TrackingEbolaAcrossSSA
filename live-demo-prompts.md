# Live demo prompts: building the Ebola Outbreak Monitor with Claude Opus 5.5

**Where:** VS Code, with the Claude Code extension, in the `TrackingEbolaAcrossSSA` repo.
**Model:** Claude Opus 5.5.
**What gets built live:** a smaller version of `docs/dashboard.html`, in a new `demo/` folder, from the data already in `data/`.
**Total run time:** about 15 to 20 minutes of prompting, spread across the talk. Each batch is sized to finish in 1 to 4 minutes, so you can talk while it works.

---

## Before the talk (do this the day before)

1. **Open a fresh branch, so the live build never touches the finished work:**
   ```bash
   cd ~/Downloads/TrackingEbolaAcrossSSA
   git checkout -b live-demo
   mkdir demo
   ```
2. **Do a full dry run of every batch below.** After each batch finishes, save a checkpoint:
   ```bash
   git add -A && git commit -m "demo: batch N"
   git tag demo-N
   ```
   Then reset for the real talk with `git checkout main && git branch -D live-demo` and recreate the branch.
3. **Your safety net:** if a batch fails on stage, run `git checkout demo-N -- demo/` to jump to the dry-run result for that step, and keep talking. The finished dashboard is always at `docs/dashboard.html`.
4. **Open a live preview:** in VS Code, install "Live Server" (or run `python3 -m http.server` in the repo) and keep `demo/index.html` open in a browser next to the editor.
5. **Pick your effort level:** set Claude Code to **medium**, which is Opus 5.5's default. Batch 1 and the effort comparison in Batch 7 change it on purpose.
6. **Check your connection:** run Batch 1 once on the venue Wi-Fi. If the network is unreliable, use your phone's hotspot.

---

## Batch 1 · Read before building (effort: low) · about 1 minute

> **Say while it runs:** "Before an LLM writes a single line, it reads. Everything it knows about this project right now is whatever fits in its context window."

```
You're helping me build a small public-health dashboard live, in front of an audience, so keep each step quick and visible.

Read these files and tell me, in five short bullets, what data we have and what each file contains:
- data/outbreaks.json
- data/timeline_2026.json
- data/africa_grid.json

Then propose a plan for a one-page dashboard in demo/index.html, in at most six steps. Don't write any code yet.
```

---

## Batch 2 · Skeleton and design system (effort: medium) · about 2 to 3 minutes

> **Say while it runs:** "Design is a set of decisions. I give it constraints: colours, type and layout. It turns them into tokens, then into code."

```
Create demo/index.html: one self-contained HTML page, with no build step. Load d3 v7.9.0 from cdnjs.

Design it like a plain, conservative analytics product:
- White page (#fcfefe), thin grey borders, 10px rounded cards.
- Headings in a typewriter-style monospace font (IBM Plex Mono from Google Fonts). Body text in IBM Plex Sans.
- Colours, as CSS variables: ink #010134, dark teal #07384c, royal blue #0536cf, blue #0461da, ocean #004d70, steel #7898bf, sand #c9a46a.
- A narrow left sidebar with links: Overview, Map, Outbreaks, Sources. Hide the sidebar under 860px wide.

In the main area, add:
- A title, "Ebola Outbreaks".
- One sentence about the 2026 Bundibugyo outbreak.
- A blue info note: "Data will be updated as the WHO shares new situation reports."

Load the three JSON files from ../data/ with fetch. Leave empty placeholder sections for the parts we'll add next.
```

---

## Batch 3 · Summary numbers (effort: medium) · about 2 minutes

> **Say while it runs:** "This is where hallucination would hurt. So the rule is: every number on the page has to be computed from the data, never typed in."

```
Add two things under the info note, side by side, stacking on narrow screens:

1. A dark teal "Current outbreak" card, with label and value pairs: virus, date declared, confirmed cases, deaths, case fatality, number of DR Congo provinces, countries affected.
   - Take cases and deaths from the 2026-10-14 row of timeline_2026.json.
   - Count provinces and countries from the 2026 rows of outbreaks.json.

2. A "Summary" card with four tiles: confirmed cases, deaths, case fatality and outbreak locations, for all outbreaks in outbreaks.json.

Compute every number from the data. Do not type any figure into the HTML. Format numbers with thousands separators.
```

---

## Batch 4 · The growth chart (effort: medium) · about 2 to 3 minutes

> **Say while it runs:** "Charts are just code. D3 is all over its training data, so it knows the patterns: scales, axes, a line, then the details that make a chart readable."

```
Add a card titled "2026 outbreak over time" with a d3 line chart from timeline_2026.json:
- x axis: date. y axis: cumulative confirmed cases, from 0 to 10,000.
- Royal blue cases line, with a light blue area fading down to the axis.
- Sand-coloured deaths line, only where deaths are reported.
- A small white circle with a blue outline on each reported date.
- A tooltip on hover showing the date, cases, deaths and source.

Size the chart from the card's width and redraw it when the window resizes. Faint gridlines, small grey tick labels.
```

---

## Batch 5 · The map (effort: high) · about 3 to 4 minutes

> **Say while it runs:** "Maps are harder. It has to turn latitude and longitude into pixels and keep the layers in the right order. That's why I've turned effort up: more thinking before it writes."

```
Add a "Where" card next to the growth chart, two columns on wide screens.

Draw Africa as a dot map from africa_grid.json:
- One small dot per point, positioned with a simple linear longitude/latitude projection.
- Steel-blue dots for most land. Darker blue dots for countries that have had an outbreak.

Over the dots, draw a circle for each outbreak in outbreaks.json:
- Circle area scales with cases (use d3.scaleSqrt).
- Active outbreaks: filled royal blue with a soft pulsing ring.
- Outbreaks declared over: white fill with a steel outline.
- A tooltip with the place, country, period, virus and cases.

Add a small legend: active, declared over.
```

---

## Batch 6 · Filters and the table (effort: medium) · about 3 minutes

> **Say while it runs:** "Now it's a dashboard rather than a page. State lives in one place, and every card redraws from it."

```
Add a filter bar under the info note:
- Period chips: All years, 2014–2019, 2020–2025, 2026.
- A country dropdown and a virus dropdown, both filled from the data.
- Status chips: Any, Active, Declared over.
- A "Clear all" button.

Keep the filter state in one object. When it changes, redraw the summary tiles, the map and a new table.

The table, "Outbreak locations", has these columns: location, country, period, virus, status (as a pill), cases, deaths, case fatality.
- Every column sorts when you click its header.
- Clicking a row filters by that row's country.
- In the cases column, show a 14-tab sand-coloured bar on a log scale before the number, with a one-line key under the table explaining it.
```

---

## Batch 7 · The effort comparison (on stage) · about 2 minutes

> **Say:** "Same prompt, two effort levels. Watch how long it thinks, how many steps it takes and what comes out."

Run this once at **low**, then undo it (`git checkout -- demo/`), then run it again at **high**.

```
Add a small "What changed this week" card at the top that compares the latest two rows of timeline_2026.json: new cases, new deaths, and the change in case fatality, each with a short plain-English sentence.
```

> **What to point out:**
> - Low usually answers straight away, with fewer steps and less checking.
> - High plans first, makes more tool calls, handles edge cases (for example a missing deaths value) and summarises what it changed.
> - Neither is "better". You're choosing how much thinking, time and money the task deserves.

---

## Batch 8 · Review its own work (effort: medium) · about 2 minutes

> **Say while it runs:** "The best habit is making it check itself. Models are much better at finding bugs when you ask them to look."

```
Review demo/index.html as if you were a careful reviewer:
1. Check that every number on the page comes from the data.
2. Check that the layout works at 400px wide.
3. Check that the tooltips stay inside the page.
4. Check that the colours have enough contrast on white.

List anything wrong, then fix it. Keep the fixes small.
```

---

## Batch 9 (optional) · The wow moment (effort: high) · about 3 minutes

```
On the map, add the 2026 travel route of Kenya's first case, from WHO's week 41 report: Buta → Kisangani → Beni → Kampala → Nairobi.

Draw it as a dashed line that draws itself in over two seconds when the page loads, with small handwritten-style labels at each stop (Sacramento font from Google Fonts).

Respect prefers-reduced-motion.

Coordinates:
- Buta 24.73, 2.80
- Kisangani 25.19, 0.52
- Beni 29.47, 0.49
- Kampala 32.58, 0.31
- Nairobi 36.82, -1.29
```

---

## If something goes wrong on stage

- **It's taking too long:** keep talking. The talk is about what it's doing, so narrating it is the content.
- **It breaks the page:** say "This is real", then run `git checkout demo-N -- demo/` and carry on from that checkpoint.
- **The network drops:** switch to the finished version, `docs/dashboard.html`, and the video, `media/ebola-across-africa.mp4`.
