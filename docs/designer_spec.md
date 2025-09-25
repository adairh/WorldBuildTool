# TL-Forge — AAA Designer Command Desk

This guide reframes TL-Forge entirely from the perspective of a AAA MMORPG design team that is building a vast Vietnam Wuxia experience set in Thăng Long. It avoids implementation detail and focuses on what designers need to see, operate, and approve in order to ship content at scale.

---

## 1. Roles, Expectations, and Success Signals

### Lead Game Designer (LGD)
- **North-star dashboard:** stacked views of civic, religious, economic, and military health across the capital.
- **Gap radar:** automatically highlights empty hubs, under-length questlines, or unbalanced systems.
- **Data discipline:** every card, grid, and export is locked to canonical schemas; violations surface immediately.

### World & Level Designer (WLD)
- **Living map studio:** paint shrines, markets, docks, alleys, fortifications with realistic placement tools.
- **Overlay control:** toggle NPC density, patrol routes, trade corridors, celebration zones, floodplains.
- **Travel evaluator:** click two hubs to see walking time heatbands and the slowest-safe path.

### Narrative Designer (ND)
- **Quest graph atelier:** branch, condition, and dialogue nodes visualized as animated graphs.
- **Story-on-map:** every node projects its itinerary on the city map for spatial storytelling.
- **Narrative QA:** instant warnings for orphaned nodes, repetitive fetch streaks, tonal imbalance.

### Systems Designer (SD)
- **Rulebook engine:** dial in age limits, hub density, quest variety, faction gates, travel caps.
- **Visual linting:** red hubs, orange quest nodes, flashing overlays whenever rules break.
- **Global sweeps:** re-run the entire rule suite after a single adjustment.

### Economy Designer (ED)
- **Commodity control room:** monitor goods, origin hubs, markets, taxes, trade posts.
- **Shock simulator:** trigger storms, raids, embargoes and watch flows re-balance in real time.
- **Quest prompt forge:** auto-suggest mitigation quest hooks when shortages emerge.

### Content Designer (CD)
- **Household foundry:** seed-driven generator spins up interconnected families, disciples, neighbors.
- **Relationship galaxy:** clusters show kin, guild, martial lineage, rivalries, apprenticeships.
- **Hub audit:** ensure each location hits vendor/guard/quest quotas before lock-in.

### QA Designer (QA)
- **Triaged reports:** categorized by error, warning, info with owner tags.
- **Context jumps:** clicking a defect opens the relevant hub, NPC, or quest card instantly.
- **Diff view:** compare data snapshots to identify additions, removals, or edits.

---

## 2. Expected Experiences

### Mandatory Visualizations
- **Layered map:** economy, religion, military, transport, quest heat, patrol grid, disaster zones.
- **Heatmaps:** quest density, vendor coverage, guard distribution, faction presence.
- **Isochrones:** travel rings at 5/10/15 minute walking speeds from any anchor hub.
- **Graphs:** social connections, quest dependencies, faction reputation ladders.
- **Timelines:** dynastic events, agricultural cycles, festivals, invasions.
- **Coverage matrix:** hubs crossed with quest hooks, vendors, guards, events, faction reps.
- **Dashboards:** economy flow, rule violations, export readiness, approval backlog.

### Standardized Workflow
1. **Spin up a hub** → draw parcels, auto-generate households, assign vendors/guards, seed hooks.
2. **Compose a questline** → drag nodes, bind map stages, validate gameplay cadence.
3. **Schedule events** → add festivals or calamities, preview economic and narrative repercussions.
4. **Run the checker** → apply the full rulebook, resolve highlighted issues inline.
5. **Review dashboards** → confirm coverage, errors, readiness metrics are within thresholds.
6. **Secure approval** → LGD signs off on hubs or questlines that meet studio policy.
7. **Export in one click** → packaging refuses to proceed if blockers remain.

### Rulebook Coverage
- **Age compliance** for NPC participation.
- **Geographic consistency** for professions, patrols, and quests.
- **Density quotas** for vendors, guards, and quest hooks per hub.
- **Narrative variety** preventing fetch mission streaks and ensuring combat/social/traversal beats.
- **Faction reputation** gates and escalation ladders.
- **Travel limits** ensuring stage durations stay within approved minutes.
- **Economic resilience** detecting shortages that extend beyond two cycles.
- **Quest composition** verifying multi-modal gameplay across lengthy arcs.

### Quality Gates
- **Zero blocking errors**, ≤5 warnings across the project.
- **Coverage matrix green** for critical hubs.
- **Questline completeness** (>5 steps requires mapped path and timeline placement).
- **Economic stability** (no persistent red alerts).
- **Export hygiene** (no orphan data, manifests validated).

---

## 3. User Stories (Given–When–Then)
- **Given** a new district, **when** I render it and spawn twenty households, **then** density and heatmaps refresh immediately.
- **Given** a seven-node questline, **when** I validate it, **then** there are no dangling nodes and quest heat radiates from its hubs.
- **Given** I log a typhoon event, **when** the simulation runs, **then** economic dashboards flag shortages and propose relief quests.
- **Given** I run the checker, **when** it finds a five-year-old in combat content, **then** I see a named error and jump to the NPC card.
- **Given** I prep a release, **when** I open Export Readiness, **then** coverage exceeds 95%, errors are zero, manifests show green.

---

## 4. Prioritized Backlog

### P0 — Must Deliver
- Map overlays (quest heat, densities, isochrones).
- Household generator with social graph exploration.
- Quest graph editor plus automated validator.
- Comprehensive checker rulebook.
- Coverage matrix across hubs.
- Export readiness dashboard with blocking checks.

### P1 — Should Deliver
- Faction territories and reputation gating surfaces.
- Economic simulation with event shocks.
- NPC day/night schedules.
- Commenting, approvals, revision history.
- Sandbox branches with diff/merge workflows.

### P2 — Future Opportunities
- Localization coverage analytics.
- Seasonal planning tools.
- Authoring telemetry and productivity insights.

---

## 5. Definition of Done
- Visualization review passes for every major overlay and graph.
- Checker reports 0 errors and ≤5 warnings.
- Coverage matrix meets or exceeds studio thresholds.
- Export dry-run produces clean manifests with no orphaned references.
- LGD approval recorded for the release candidate.

---

## 6. Vision Statement
TL-Forge is the living command desk of the Thăng Long project. Designers sketch, spawn, validate, and ship rich content without touching code. Every insight, warning, or approval is surfaced through intuitive overlays, graphs, and dashboards so the world feels alive long before it lands in the engine.
