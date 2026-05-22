# App UI kit — autoagent/optimizer workbench

Workbench app. A run inspector: sidebar (runs, architectures, components, traces, evidence) + top bar (run identity, budget, status) + main area showing the architecture comparison and the white-box trace for the selected case + an inspector rail with intervention suggestions.

**Structure**
- `index.html` — full app shell, assembled
- `Sidebar.jsx` — left nav with run list
- `TopBar.jsx` — current run identity, budget meter, status
- `MetricStrip.jsx` — four-up metric callout
- `ArchList.jsx` — list of compared architectures (champion at top)
- `TraceView.jsx` — white-box trace timeline (dark surface)
- `InterventionRail.jsx` — bottleneck + suggested interventions
- `CommandPalette.jsx` — Cmd-K palette overlay
