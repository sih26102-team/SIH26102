# Frontend Dashboard — Owner: Chandana

Investigation dashboard for **SIH26102**: AI-Powered System to Detect
Anomalies, Fraud, and Inefficiencies in MPLADS Scheme Implementation.

This is stage 8 (**Investigation Dashboard**) and stage 9 (**Officer
Review**) of the pipeline described in the team's Context Briefing —
plus the case management (stage 10) and audit trail (stage 11) views.
It's the part of the system a human reviewer actually sits in front of.

> **Reminder baked into the UI, not just this file:** a flagged project
> means *worth a closer look*, never *confirmed fraud*. Every screen —
> table, detail page, explanation panel — sticks to that language on
> purpose. Don't add a "FRAUD DETECTED" label anywhere, even for demo
> flair.

## Quick start

```bash
npm install
npm run dev        # → http://localhost:5173
```

No backend required to try it — see **Mock mode** below. To run the
test suite:

```bash
npm test            # single run
npm run test:watch  # watch mode
```

## Mock mode (default) vs. real backend

Every service file (`src/services/*.js`) has two code paths controlled
by `VITE_USE_MOCK` in `.env` (copy from `.env.example`):

| `VITE_USE_MOCK` | Behaviour |
|---|---|
| `true` (default) | Reads from `src/utils/mockData.js` — 42 synthetic MPLADS-style project records, generated with a seeded random so the dataset is stable across reloads. Every record carries `isSynthetic: true` and the UI labels it as such (see Section 7 of the Context Briefing: real and synthetic data must stay clearly distinguished). |
| `false` | Calls `VITE_API_BASE_URL` (default `http://localhost:8000`) — i.e. Mokshagna's `backend-data-api` and Poornesh's `backend-case-management`. |

This means the frontend can be built, demoed, and tested **completely
standalone**, and switching to the real backends later is a one-line
env change, not a rewrite. The expected request/response shape each
service assumes is documented in a comment at the top of that file —
useful as an informal API contract to compare against `docs/api-contracts.md`
once the backend team writes the real routes.

## What's built

Maps directly to the MVP scope in Section 6 of the Context Briefing:

**Must-have (done):**
- Login (`LoginForm`, `LoginPage`, JWT-ready auth flow via `useAuth`)
- Investigation dashboard with stat cards + filters (`DashboardPage`)
- Flagged works table, sortable, risk-first (`FlaggedWorksTable`)
- Explanation of why a project was flagged (`RiskExplanationPanel`) —
  mirrors the sample structured output format in Section 5 exactly:
  score, level, reasons, recommended action
- Project investigation view (`ProjectDetailPage`)
- Basic case management with status transitions (`CasesPage`)
- Audit trail (`AuditTrailList`)

**Should-have (done):**
- Geographic visualization (`FlaggedMap`, Leaflet + OpenStreetMap tiles)
- Trend analysis (`TrendChart`, Recharts)
- Advanced filtering (`FilterBar` — search, state, risk level, status, category)
- Data quality indicators (`DataQualityBadge`)

**Not built** (nice-to-have / out of MVP scope per Section 6): advanced
network analysis, NLP, computer vision. Correctly out of scope for the
hackathon MVP — don't build these under time pressure.

## Design system

Chosen deliberately against the "generic AI dashboard" defaults (cream
+ terracotta, or dark mode + neon accent) — this is a government
oversight tool, so the palette reads as *trustworthy and legible under
pressure*, not trendy:

- **Colors** — deep navy chrome (`navy-900` → `navy-50`) for
  structure/chrome, and a strict semantic red/amber/green scale
  (`risk-high` / `risk-medium` / `risk-low`) that is used **only** for
  risk, never decoratively. If you see red anywhere in this UI outside
  a risk context, that's a bug.
- **Type** — Space Grotesk for headings (`font-display`), Inter for UI
  and body text (`font-sans`), JetBrains Mono for anything that's data
  — project IDs, risk scores, currency (`font-mono`). Numbers should
  always look like data, not prose.
- **Signature element** — `RiskScoreRing`. Every risk score in the app,
  everywhere, is a ring whose fill fraction *is* the score — never a
  bare number or a flat pill. It's the one visual idea this product
  should be remembered by, because investigators are triaging a list,
  not reading digits one at a time.

All tokens live in `tailwind.config.js` under `theme.extend.colors` /
`fontFamily` — change them there, not per-component.

## Folder structure

```
frontend-dashboard/
├── src/
│   ├── components/     # presentational + reusable pieces
│   ├── pages/           # one file per route
│   ├── services/        # API layer (mock/real toggle lives here)
│   ├── hooks/            # useAuth (context), useFlaggedWorks (data + filters)
│   ├── utils/             # riskUtils, formatters, mockData
│   ├── App.jsx             # routes
│   ├── main.jsx             # entry point
│   └── index.css             # Tailwind directives + tiny overrides
├── public/
├── tests/                # vitest + React Testing Library
├── tailwind.config.js
├── vite.config.js
└── .env.example
```

## Known gaps / next steps for the team

- No real auth token verification — `authService.login` in mock mode
  accepts any non-empty username/password. Do not treat this as secure;
  it exists purely so the rest of the app can be built before Poornesh's
  `/auth/login` endpoint exists.
- `FlaggedMap` plots district-level coordinates with a small random
  jitter for readability when multiple projects share a district —
  it's illustrative positioning, not a precise geocode. Swap in real
  lat/lng once the data pipeline provides it.
- Role-based view differences (Section 8: monitoring official vs.
  audit personnel vs. scheme administrator vs. implementing authority)
  are not yet implemented — everyone currently sees the same views.
  `user.role` is already captured at login if this needs building later.
- No pagination on the flagged-works table yet — fine for the ~40-row
  mock dataset and probably fine for a hackathon demo dataset, but flag
  it if the real dataset is large.

## For whoever picks this up next (including future Chandana)

Every service file's top comment states the exact request/response
shape it expects from the real backend. Before wiring up
`VITE_USE_MOCK=false`, diff that comment against whatever Mokshagna and
Poornesh actually shipped in `docs/api-contracts.md` — that's the
fastest way to find integration mismatches before demo day.
