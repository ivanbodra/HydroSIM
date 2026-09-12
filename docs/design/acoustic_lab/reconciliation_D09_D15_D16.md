# Late-brief reconciliation — D9, D15, D16

This record closes the late-arriving visual-specification reconciliation required by issue #418.

Authority order used here:
1. Product Owner decisions.
2. Canonical pedagogy / learner effect.
3. Scientific Core / API contracts.
4. Current production/runtime constraints.
5. Visual implementation brief.

The rule is intentionally conservative: when production already achieves the intended learner-visible relationship by a different but effective mechanism, that implementation is accepted as equivalent. Follow-up is requested only for an `ESSENTIAL` gap or an unusually high-value / low-cost `PREFERRED` improvement.

## D9 — Multisector MBES

Visual brief: `D09_multisector_visual.md`  
Production: `web/pedagogical-explorer/src/MultisectorLab.tsx`  
Relevant merged production PR: #407

### What production already satisfies

PR #407 and current `main` already provide the essential pedagogical progression:
- one-TX-sector baseline first;
- reveal of the three-sector configuration on the same angular scale;
- dominant `TX SECTORS != RX BEAMS` distinction;
- sector centre, angular support and TX delay as primary controls;
- frequency and pulse duration behind secondary disclosure;
- sound-speed and relative-power controls removed from the primary surface;
- no opacity-as-power encoding;
- authoritative Python/API outputs retained for supports, TX groups/timing and wavelength;
- fixed baseline/current angular comparison;
- transmit timeline linked to sector identity.

The current horizontal fixed-scale coverage bands are accepted as an **equivalent implementation** of the required sector-support comparison. They visibly preserve one-sector versus multisector angular support and can reveal gaps/overlaps through the geometry itself.

### Delta classification

**ESSENTIAL:** none.

**PREFERRED:**
- evolve flat support bands into the spatial wedge/fan composition from the brief;
- add explicit sector selection so one sector is edited at a time instead of presenting three repeated control stacks;
- add a faint conceptual RX-fan reference so `TX sectors != RX beams` is demonstrated visually rather than primarily by text;
- add explicit gap/overlap annotation when supports separate/intersect.

These are high-value visual improvements but do not justify invalidating the already-correct learner progression on their own.

**OPTIONAL:**
- short `motion/react` wedge/timeline transitions;
- transient one-sector ghost during the single -> multisector reveal.

### Reconciliation decision

D9 is **accepted as pedagogically equivalent for the current production state**. No blocking design correction is required by #418.

---

## D15 — Survey Planning

Visual brief: `D15_survey_planning_visual.md`  
Production: `web/pedagogical-explorer/src/SurveyPlanningLab.tsx`  
Relevant merged production PR: #429

### What production already satisfies

PR #429 and current `main` already implement the key learner-visible relationships:
- persistent distinction between planned/nominal and achieved/verified field coverage;
- survey area, reference depth/usable swath, line direction and spacing/overlap as the primary planning controls;
- beam count demoted to secondary disclosure;
- requested spacing and actual edge-anchored spacing displayed separately;
- explicit intentional-gap experiment using the authoritative planner;
- speed stated and implemented as an on-line-time-only consequence;
- authoritative Core-generated planned lines and coverage strips remain in the plan SVG;
- baseline/current comparison preserved;
- no planning science duplicated in React.

This already satisfies the dominant pedagogical effect: the learner can manipulate planning geometry, deliberately create a bad plan, and see the effort consequence while retaining the nominal-versus-achieved boundary.

### Delta classification

**ESSENTIAL:** none.

**PREFERRED:**
- make the plan map visually more dominant and reduce competing metric-card weight;
- draw gap/overlap and requested-versus-actual spacing directly on the plan SVG with brackets/annotations;
- show an optional baseline ghost in the same map coordinate system rather than relying mainly on numeric comparison;
- rename legacy `d16-*` CSS namespace to D15-specific classes when safe.

**OPTIONAL:**
- pointer direction handle as an input proxy to the existing direction control;
- pointer spacing bracket in explicit-spacing mode;
- short `motion/react` cross-fades between authoritative plan states.

### Reconciliation decision

D15 is **accepted as pedagogically equivalent for the current production state**. No blocking design correction is required by #418.

---

## D16 — Survey Coverage & Acquisition Trade-offs

Visual brief: `D16_survey_coverage_tradeoffs_visual.md`  
Production: `web/pedagogical-explorer/src/TradeoffLab.tsx`  
Relevant merged production PR: #431

### What production already satisfies

Current production has a strong canonical API-backed basis:
- speed and effective ping rate are available and visually elevated as the guided entry experiment;
- echosounder, multisector, bottom-detection and survey-density APIs are chained rather than reimplemented in React;
- actual retained sounding positions/spacings and finite-footprint coverage outputs are available;
- High Density state and API-backed added detections are available;
- baseline/current snapshot comparison exists;
- coverage classification, covered width, gaps, retained sounding counts and along/across spacing metrics exist.

PR #431 was explicitly a bounded first slice and states that later D16 work should still make coverage versus density versus resolution versus efficiency explicit and strengthen the connected acquisition-strip presentation.

### Delta classification

**ESSENTIAL:**

A single connected learner-visible acquisition scene is still required to make the central D16 distinction perceptually obvious:

`INSONIFIED COVERAGE != SOUNDING DENSITY != RESOLUTION != EFFICIENCY`

The current production surfaces expose the required quantities, but they remain too fragmented across controls, pattern panels and readouts. The UX must implement a dominant top-down local survey strip on fixed/shared physical scales using current API-backed data, with:
- along-track ping origins positioned from authoritative `along_track_ping_spacing_m`;
- across-track retained soundings shown at their actual positions;
- finite footprint support / merged coverage shown from authoritative `footprint_intervals` and `merged_coverage_intervals`;
- visible internal gaps from `internal_gap_intervals`;
- High Density adding points **inside unchanged coverage geometry**;
- a compact evidence rail naming Coverage / Density / Resolution / Efficiency without synthesizing a universal quality or efficiency score.

The scene may replicate API-backed ping rows for illustration, but must not add a second cadence or footprint model in React.

This is an `ESSENTIAL` design delta because the canonical D16 learner effect depends on visually separating four often-confused concepts in one physical coordinate system. The existing first slice does not yet make that relationship sufficiently direct.

**PREFERRED:**
- progressive disclosure for upstream multisector/pulse/frequency controls;
- baseline ghost on the same physical scene;
- fixed-scale gap brackets and sounding selection/inspection;
- rename legacy `d17-*` styling namespace to D16-specific classes when safe.

**OPTIONAL:**
- `motion/react` transitions for ping-row spacing, sounding movement and High Density point reveal;
- pointer selection of a sounding/footprint for inspection.

### Reconciliation decision

D16 is **not rejected**; the current production slice is useful and should be preserved. The connected acquisition-strip scene above is the one remaining `ESSENTIAL` visual correction and should be implemented by Production UX Line B as a focused follow-up rather than by rewriting the lab.

---

## #418 completion assessment

All D1-D17 implementation-ready visual briefs now exist under `docs/design/acoustic_lab/`.

The late-arriving briefs have been explicitly reconciled against production:
- D9: accepted equivalence, no `ESSENTIAL` gap;
- D15: accepted equivalence, no `ESSENTIAL` gap;
- D16: one focused `ESSENTIAL` gap identified and routed to Production UX Line B.

Therefore the Concept Designer completion condition for #418 is satisfied once the D16 correction is routed to the existing UX-B ownership. The production correction itself remains UX work and is not a reason to keep #418 open.