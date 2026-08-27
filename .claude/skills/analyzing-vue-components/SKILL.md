---
name: analyzing-vue-components
description: Use when a Vue 3 component has grown large, feels slow, or looks similar to another component, and you need to find concrete performance bottlenecks or duplicated logic/markup before refactoring — technology-specific to this project's Vue 3 Composition API + Options-API-setup() style.
---

# Analyzing Vue Component Structure

## Overview

Systematic checklist for finding two categories of issues in a Vue 3 component:
**performance** (unnecessary recomputation, uncached template expressions, reactivity
misuse) and **code reuse** (logic or markup duplicated across files that should be a
shared composable/component). This is analysis only — it produces a report, it does
not edit files.

## When to Use

- A `.vue` file is large (300+ lines) or has grown substantially since last reviewed
- Before extracting a component/composable, to confirm what's actually duplicated
- A component "feels slow" (visible lag on filter/prop changes) and the cause isn't obvious
- Reviewing a PR that touches a view/component and you want a structured pass, not just a vibe check

## Procedure

1. Read the target component(s) in full — don't skim, the issues below hide in details (exact line counts, repeated substrings).
2. `grep -rn` every locally-defined helper/formatter function name (e.g. `formatDate`, `translateX`, `getXBadge`) across `client/src/views/` and `client/src/components/` to catch cross-file duplication — this is the single highest-value step and is easy to skip.
3. Diff the `setup()` return object's keys against actual usage in `<template>` to find dead exposed state.
4. Scan `<template>` for the same expression appearing more than once (e.g. the same calculation used for both a text label and a `:style` width).
5. Check every `watch(...)` that triggers an async reload for debounce/cancellation.
6. Write the report grouped by Performance / Code Reuse, each item as: file:line, what the issue is, why it matters, concrete fix. Rank a short "highest-value fixes" list at the top.

## Performance Checklist

| Check                                                                                   | How to find it                                                                                                                                             | Fix                                                                                                                                                   |
| --------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| Dead computed/ref exposed but unused                                                    | Diff `setup()` return keys vs template usage (grep each key in the template block)                                                                         | Delete the computed and its return entry                                                                                                              |
| Linear `.find()`/`.filter()` inside another loop (O(n·m))                               | Look for `.find(`/`.filter(` calls inside a `.map()`/`.forEach()`/`for` body                                                                               | Build a `Map` once as a computed (e.g. `inventoryBySku`), reuse for O(1) lookup                                                                       |
| Same expression computed more than once in the template                                 | Look for identical or near-identical inline expressions repeated across a card/row (e.g. a percentage used for both display text and a progress-bar width) | Hoist into a single `computed()`                                                                                                                      |
| Plain (non-computed) function called repeatedly from the template for cumulative values | Function invoked multiple times in the same template block, each call redoing prior work (e.g. chart segment offsets, running totals)                      | Wrap the whole derivation in one `computed()` that returns all needed values together                                                                 |
| Composable invoked inside a per-call/per-row function instead of once in `setup()`      | `use*()` called inside a helper function body rather than destructured at the top of `setup()`                                                             | Destructure once at the top of `setup()`, reference the ref directly                                                                                  |
| Multi-source `watch([...])` triggering async work with no debounce/cancellation         | `watch([a, b, c], () => loadData())` pattern with no `watchDebounced`/`AbortController`                                                                    | Debounce with `watchDebounced` (already a client convention — see client/CLAUDE.md); guard against out-of-order responses                             |
| Global objects exposed from `setup()`'s return                                          | `return { Math, ... }` or similar                                                                                                                          | Remove — Vue 3's compiler already allows bare `Math.foo()` in templates; move any calc into a computed instead                                        |
| Several independent full-array passes over the same large collection                    | Multiple `computed()`s each doing their own `.forEach`/`.filter`/`.reduce` over the same source ref                                                        | Only flag if the collection could realistically grow large; otherwise note as low-priority — merging hurts readability for little gain at small scale |

## Code Reuse Checklist

| Check                                                                                       | How to find it                                                                                                                | Fix                                                                                                                                                                               |
| ------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Same formatter/helper reimplemented across files with drifting behavior                     | `grep -rn "functionName"` across views/components — compare locale-handling, edge cases, fallback values between copies       | Centralize in `composables/useI18n.js` (for translate\* helpers) or a new `composables/useFormatters.js`; note any behavioral drift as a real bug (e.g. one copy ignoring locale) |
| Same status/severity classification derived from different input shapes                     | Same concept (e.g. stock badge, priority label) computed from raw fields in one file and from a pre-labeled string in another | Standardize on one function fed a consistent input shape (prefer the version built from raw source data)                                                                          |
| Near-identical markup blocks copy-pasted with only bound data varying                       | Visually scan `<template>` for repeated card/row/tile structures (e.g. 5 KPI cards with only label/value/goal differing)      | Extract a presentational component with props, drive with `v-for` over a data array                                                                                               |
| Redundant per-cell/per-row event listeners                                                  | Same `@click="handler(item)"` repeated on every `<td>` in a row instead of once on `<tr>`                                     | Move the handler to the parent row element; use `@click.stop` on any nested interactive elements that need to opt out                                                             |
| Bespoke complex markup with no current duplicate but an obviously reusable shape            | Custom SVG chart / widget built inline for one view                                                                           | Proactively extract into its own component now, before it gets copy-pasted for the next feature                                                                                   |
| Data-loading skeleton (`loading`/`error`/try-catch-finally/`Promise.all`) repeated per view | Compare the `loadData` function shape across views                                                                            | Extract into a shared composable (e.g. `useDashboardData()`-style) per the pattern already documented in client/CLAUDE.md                                                         |

## Report Format

```
## Performance
1. [file:line] Issue — why it matters — fix
...

## Code Reuse
1. [file:line] Issue — why it matters — fix
...

## Highest-value fixes
1. ...
2. ...
```

## Applying Fixes

This skill only produces the report. If the user wants the suggestions applied, that
means editing `.vue` files — delegate to the vue-expert subagent per this project's
CLAUDE.md rule, don't edit them directly from this analysis.
