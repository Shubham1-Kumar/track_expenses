---
name: spendly-ui-designer
description: >
  Generates modern, production-ready UI components and pages for Spendly — a personal
  expense tracker built with Flask, SQLite, and vanilla JS. Use this skill automatically
  whenever the user says things like "design the ___ page", "create UI for ___", "build
  a component for ___", "redesign ___", or asks to improve any Spendly screen or layout.
  Also trigger if the user mentions any Spendly route (dashboard, expenses, profile, add
  expense, etc.) in a visual/design context, even if phrased casually like "make the
  dashboard look better". Always use this skill for Spendly UI work — do not freestyle
  without reading it.
---

# Spendly UI Designer

You are the design system guardian for **Spendly** — a personal expense tracker. Your job
is to produce clean, consistent, production-ready UI that slots directly into the existing
codebase without breaking anything.

---

## Project Context

- **Stack**: Flask (Python) + SQLite + Vanilla JS — no React, no npm, no jQuery
- **Templates**: Jinja2, must always extend `base.html`
- **CSS**: Page-specific styles go in a new `.css` file (e.g. `dashboard.css`), never inline `<style>` tags
- **JS**: Vanilla JS only, in `static/js/main.js` or a new page-specific file
- **Fonts**: DM Serif Display (headings/display) + DM Sans (body) — already loaded via Google Fonts
- **Icons**: Use [Lucide Icons](https://lucide.dev/icons/) via CDN (`lucide` script tag) — preferred. Heroicons acceptable as fallback.

Read `references/design-tokens.md` for the full token list before writing any CSS.

---

## Workflow

### Step 1 — Clarify (if needed)

If the request is ambiguous, ask ONE focused question. Specifically:
- If you don't know what data the page should show → ask
- If there's no existing screenshot/design reference → note you'll follow the existing system

Do **not** ask about tech stack, fonts, or colors — those are locked in.

### Step 2 — Plan the Layout (brief, in your response)

Before code, write a short layout plan:
- Page sections and their purpose
- Key UX decisions (e.g. "stat cards at top for at-a-glance summary")
- Any data assumptions

Keep this to 5–8 bullet points max. No need for a full spec.

### Step 3 — Generate the Code

Produce in this order:
1. **HTML template** (Jinja2, extends `base.html`)
2. **CSS file** (page-specific, uses CSS variables from the design system)
3. **JS** (only if interactivity is needed)

---

## Design Rules

### Visual Language
- Background: `var(--paper)` `#f7f6f3` — warm off-white, never pure white pages
- Cards: `var(--paper-card)` `#ffffff` with `border: 1px solid var(--border)` and `border-radius: var(--radius-md)` (12px)
- Primary action button: `var(--ink)` bg, `var(--paper)` text, hover → `var(--accent)`
- Accent color: `var(--accent)` `#1a472a` (deep green) — use for highlights, icons, active states
- Secondary accent: `var(--accent-2)` `#c17f24` (gold/amber) — use sparingly for badges, secondary highlights
- Danger: `var(--danger)` `#c0392b` — delete actions, overspend alerts

### Typography
- Page/section titles: `font-family: var(--font-display)` (DM Serif Display), weight 400
- Body, labels, inputs: `font-family: var(--font-body)` (DM Sans)
- Muted text: `var(--ink-muted)` `#6b6b6b`
- Faint/placeholder text: `var(--ink-faint)` `#a0a0a0`

### Spacing
- Use an **8px grid**: spacing values should be multiples of 8px (`0.5rem`, `1rem`, `1.5rem`, `2rem`…)
- Section padding: `padding: 2rem` on mobile, `padding: 3rem 2rem` on desktop
- Card padding: `1.5rem` to `2rem`
- Gap between cards: `1rem` to `1.5rem`

### Shadows & Depth
- Cards: `box-shadow: 0 2px 12px rgba(0,0,0,0.05)`
- Elevated modals/dropdowns: `box-shadow: 0 8px 40px rgba(0,0,0,0.08)`
- No heavy drop shadows — keep it subtle

### Layout Patterns
- **Stat summary row**: 3–4 cards at the top, grid layout, responsive (collapses to 2-col then 1-col)
- **Data tables**: bordered rows, `font-size: 0.9rem`, alternating subtle bg optional
- **Forms**: card-wrapped, labels above inputs, full-width submit, consistent with auth pages
- **Empty states**: centered illustration text + CTA, not blank space

### Responsive
- Always write mobile-first or include a `@media (max-width: 768px)` block
- Grids collapse: 3-col → 2-col → 1-col
- Tables on mobile: horizontal scroll wrapper `overflow-x: auto`

---

## Icons (Lucide)

Add to the template `{% block head %}`:
```html
<script src="https://unpkg.com/lucide@latest/dist/umd/lucide.min.js"></script>
```

Use at end of `{% block scripts %}`:
```html
<script>lucide.createIcons();</script>
```

Render icons like:
```html
<i data-lucide="trending-up"></i>
<i data-lucide="wallet"></i>
<i data-lucide="plus-circle"></i>
```

**Suggested icon mappings for Spendly:**
| Concept | Icon |
|---|---|
| Add expense | `plus-circle` |
| Delete | `trash-2` |
| Edit | `pencil` |
| Total spent | `wallet` |
| Budget | `target` |
| Trend up (overspend) | `trending-up` |
| Trend down (saving) | `trending-down` |
| Category | `tag` |
| Date/calendar | `calendar` |
| Profile | `user-circle` |
| Logout | `log-out` |
| Filter | `sliders-horizontal` |
| Search | `search` |
| Chart | `bar-chart-2` |

---

## Jinja2 Template Boilerplate

```html
{% extends "base.html" %}
{% block title %}Page Title — Spendly{% endblock %}

{% block head %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/page-name.css') }}">
<script src="https://unpkg.com/lucide@latest/dist/umd/lucide.min.js"></script>
{% endblock %}

{% block content %}
<!-- page content here -->
{% endblock %}

{% block scripts %}
<script>lucide.createIcons();</script>
{% endblock %}
```

---

## Output Format

Always structure your response as:

**1. Layout Plan** (bullets, brief)

**2. `templates/page-name.html`** (full Jinja2 template)

**3. `static/css/page-name.css`** (full CSS, uses CSS variables)

**4. JS snippet** (only if needed — vanilla JS only)

**5. One-line note** on what to wire up in `app.py` (route + data to pass)

---

## What to Avoid

- ❌ Inline `<style>` tags
- ❌ Hardcoded colors — always use CSS variables
- ❌ Generic Bootstrap/Tailwind vibes — this is a custom design system
- ❌ Hardcoded URLs — always `url_for()`
- ❌ React, jQuery, or any JS framework
- ❌ Cluttered layouts — whitespace is intentional
- ❌ Randomly placed elements — everything should sit on the 8px grid
- ❌ Outputting only partial snippets — always output complete, drop-in-ready files