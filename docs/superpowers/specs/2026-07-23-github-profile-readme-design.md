# GitHub Profile README — "Beamline Console" Design

**Date:** 2026-07-23
**Target repo:** `ronpandolfi/ronpandolfi` (GitHub profile magic repo)
**Audience:** professional peers (scientific software / controls community) and promotion-case visibility.

## Goals

- Data-driven and self-updating (scheduled GitHub Action), but visually designed — no third-party stat widgets, no badge walls, no typing SVGs, no contribution snake.
- Covers work GitHub can't see (Lightfall, CSM on ALS GitLab) via a hand-curated data file.
- Reads as senior-engineer craftsmanship: restrained, typographic, one accent color, instrument-console flavor.

## Page layout (top to bottom)

1. **Header SVG** — theme-aware via `<picture>` (dark/light variants). Name + one-line role: "Scientific software · beamline controls — Advanced Light Source, LBNL". Background motif: thin-line storage-ring arc cropped at left edge, tangent beam line extracting rightward through small tick marks (magnets/optics), terminating near the name. ~1000×220 viewBox. Static — designed once, not regenerated.
2. **Intro prose** — 2–3 plain-markdown sentences in Ron's voice. No emoji headers.
3. **Now** — rendered from `data/profile.yaml`: current projects (Lightfall, CSM, …), each with name, one-line description, optional link. Includes "updated <date>" stamp.
4. **Activity panel SVG** — regenerated each run, ~1000×170, theme-aware pair:
   - Left third: 12-month contribution sparkline (thin area fill, 1.5px line).
   - Middle: three numbers with small-caps labels — commits · PRs · repos contributed (past year, across ronpandolfi + orgs).
   - Right: single stacked proportional language bar with small labels.
   - Hairline border `#30363d` (dark) / `#d0d7de` (light), GitHub-native corner radius.
5. **Selected projects** — 4–6 hand-curated entries from `profile.yaml` (Xi-CAM, Tsuchinoko, bluesky ecosystem, Lightfall noted as internal, …). Plain markdown; descriptions sell, not star counts.
6. **Publications** — top ~5 from ORCID (`0000-0003-0824-8548`) with venue, year, citation count as plain text (e.g. `· cited 142×`), plus "see all on Google Scholar" link. Auto-refreshed.
7. **Footer** — plain text links (ORCID, Scholar, LinkedIn, lbl.gov page) + one line: "this page regenerates itself weekly via GitHub Actions" linking to the build script.

## Repo structure

```
ronpandolfi/
├── README.md                 # generated — never hand-edited
├── data/profile.yaml         # hand-curated: intro, now, projects, links
├── templates/README.md.j2    # Jinja2 template
├── scripts/build.py          # single uv-run script (PEP 723 inline deps)
├── assets/
│   ├── header-dark.svg / header-light.svg      # static
│   └── activity-dark.svg / activity-light.svg  # regenerated
└── .github/workflows/build.yml
```

## Pipeline (`scripts/build.py`)

1. **GitHub data** — GraphQL API with the Action's built-in `GITHUB_TOKEN`: 12-month contribution calendar, commit/PR counts, language breakdown across own repos + org contributions.
2. **Publications** — ORCID public API (no auth) for the works list; Crossref `is-referenced-by-count` for citations. No Google Scholar scraping. On any fetch failure, keep previous values (cache last-good JSON in repo) rather than publish a broken panel.
3. **Render** — draw activity SVGs by direct string-building (no matplotlib; hand-controlled typography), render `README.md.j2`, commit only if changed.

**Workflow triggers:** weekly cron (Monday morning Pacific) + `workflow_dispatch` + push to `data/**` or `templates/**`. The weekly self-commit keeps Actions from being auto-disabled after 60 days of inactivity.

## Visual system

- **Fonts (SVG-safe stacks, no webfonts — GitHub camo strips external requests):** data/labels `"SF Mono", "Segoe UI Mono", "Cascadia Code", monospace`; name/prose `"Segoe UI", "Helvetica Neue", sans-serif`.
- **Dark:** bg `#0d1117`, text `#e6edf3`, accent `#4dd0e1`-family cyan, secondary grays, border `#30363d`.
- **Light:** bg `#ffffff`, text `#1f2328`, accent `#0e7490`, border `#d0d7de`.
- One accent color only. No gradients except a subtle glow-fade on the beam line.
- Publications and projects remain selectable markdown text, never SVG.

## Error handling

- Fetch failures → reuse cached last-good data; never commit a README with empty panels.
- Workflow commit step is a no-op when nothing changed (except SVG timestamps — exclude volatile timestamps from diff-noise by only stamping the README's "updated" line from the Action run date).

## Testing

- `build.py` runnable locally (`uv run scripts/build.py`) with a PAT env var for GraphQL; renders full README + SVGs for visual inspection before pushing.
- Golden-file check: template renders with a fixtures JSON without network.
- Visual verification of both SVG themes in GitHub dark and light before first publish.

## Out of scope

- Google Scholar scraping, third-party widgets, animations, AI-written sections, metrics dashboards.
