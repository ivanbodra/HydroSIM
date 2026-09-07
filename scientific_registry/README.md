# HydroSIM Scientific Registry

This directory stores the scientific metadata used to document, validate and version the models implemented by HydroSIM.

The registry is separate from the executable code so that scientific assumptions, references and model versions remain auditable.

English is the canonical language of the Scientific Registry. Localized documentation may translate explanations, but canonical model IDs, equations, variable names, source mappings, and validation semantics remain unchanged.

## Structure

```text
scientific_registry/
├── models/
│   ├── geometry/
│   ├── integration/
│   ├── propagation/
│   ├── acoustics/
│   ├── beamforming/
│   └── signal_processing/
├── references/
│   ├── bibliography.yaml
│   └── coverage.yaml
└── validation/
    └── golden_values/
```

Registry coverage is intentionally incremental. A directory listed above may remain empty until a model has reached sufficient scientific maturity to justify a stable record.

Current registered model sets include:

- `models/integration/dynamic_motion_residuals.yaml`;
- `models/integration/risc_maingot_2019.yaml`;
- `models/propagation/layered_snell_piecewise_constant.yaml`;
- `models/propagation/sound_speed_zero_thickness_boundary.yaml`.

Canonical explanatory documents currently include:

- `docs/science/dynamic_motion_residuals.md`;
- `docs/science/risc.md`;
- `docs/science/sound_speed_at_transducer.md`.

## Minimum metadata for a scientific model

Each model record should contain, where applicable:

- stable model ID;
- semantic model version;
- scientific status;
- physical quantity or cause domain;
- state category (`Truth`, `Observed`, `Configured`, `Estimated`, or `Derived`) where relevant;
- formula or algorithm definition;
- input variables and units;
- output variables and units;
- coordinate/sign conventions;
- validity domain;
- assumptions and simplifications;
- known limitations;
- observability requirements;
- confounding parameters or models;
- primary scientific references;
- supporting references or manuals;
- source mapping to section/equation/page/figure/table where possible;
- evidence level for each important scientific claim;
- implementation path;
- numerical validation cases;
- independent analytical validation where feasible;
- golden values where appropriate;
- related models;
- alternatives;
- `supersedes` / `superseded_by` relationships where applicable.

## Reference coverage rule

`references/bibliography.yaml` is the canonical store for external scientific, standards, and manufacturer references. `references/coverage.yaml` maps the active HydroSIM scientific domains and authoritative contracts to those stable bibliography IDs.

A scientific contract is traceability-complete only when every material external claim is covered by one of the following explicit provenance classes:

- a stable bibliography reference ID;
- `mathematical_identity` or `mathematical_geometry` for a direct mathematical consequence that does not depend on an empirical scientific source;
- `internal_contract` for a HydroSIM-defined state, sign, frame, naming, or API semantic convention;
- `derived_from_source` with the named upstream model/reference when HydroSIM deliberately defines a transparent pedagogical approximation from sourced behavior.

This distinction is important: HydroSIM must not create decorative citations for identities such as `distance = speed * time`, but it also must not leave empirical formulas, standards claims, manufacturer behavior, or literature-derived algorithms without a traceable source.

When adding or materially changing an authoritative scientific contract:

1. reuse an existing bibliography ID where it already supports the claim;
2. add any genuinely new external reference to `bibliography.yaml` once, with stable ID and scope;
3. add or update the relevant domain mapping in `coverage.yaml`;
4. use the narrowest useful source locator in a model record or contract when a specific equation, section, figure, or manual passage is important;
5. never use a manufacturer manual as evidence for universal MBES behavior unless the claim is explicitly limited to that named system or independently supported by general literature;
6. correct bibliographic attribution errors in the originating authoritative document, not only in downstream notes.

A passing software test does not compensate for missing scientific provenance.

## Evidence levels

HydroSIM distinguishes the provenance strength of scientific statements and equations.

- `direct_source`: the relationship, equation, classification, or statement is explicitly supported by the cited source.
- `derived_from_source`: HydroSIM derives a mathematical consequence, approximation, or implementation form from a source-supported relationship.
- `strongly_supported_reconstruction`: multiple source statements strongly support the interpretation, but the exact primary-source formulation has not yet been verified.
- `hypothesis`: retained for investigation and not suitable as a canonical implemented scientific claim.

A claim must not be silently promoted to a stronger evidence level merely because it appears plausible or is consistent with domain knowledge.

## Source mapping

References are stored once in `references/bibliography.yaml` and cited from model records by stable reference ID.

Whenever feasible, a model should map the scientific claim to the narrowest useful source locator, for example:

```yaml
source_mapping:
  - reference_id: hughes_clarke_2003_dynamic_motion_residuals
    locator: "(B) Time Delays in the Motion Sensor Output; Figure 2"
    evidence_level: direct_source
```

The target traceability chain is:

```text
Reference
  -> scientific claim/model
  -> equation or algorithm
  -> implementation
  -> validation
```

The chain should also be navigable in reverse so that any scientific implementation can be traced back to its assumptions and literature basis.

## Validation classes

HydroSIM should distinguish validation evidence rather than treating all passing tests as equivalent.

- `implementation_consistency`: checks API/state invariants and expected relationships internal to the implementation;
- `closure`: checks that forward/inverse or depth/time formulations return to the same state;
- `independent_analytical`: computes expected values directly from closed-form mathematics without calling the implementation under test as the expected-value generator;
- `source_golden_value`: compares with a value explicitly published by an authoritative source;
- `controlled_numerical_experiment`: explores a documented model where no sufficiently simple closed-form anchor is available.

Closure is valuable, but it must not be described as independent physical validation when both paths share the same governing implementation assumptions.

## Observability

For calibration and systematic-error models, existence of a hidden error does not imply that it is observable in every survey geometry or motion state.

Models may therefore include:

```yaml
observability:
  required_excitation: []
  preferred_geometry: []
  poor_conditions: []
  confounded_by: []
```

This metadata is part of the scientific model, not merely an exercise-design annotation.

## Scientific implementation rule

A scientific equation must not be changed merely to satisfy a software test.

When implementation and reference results disagree, the discrepancy must be investigated and documented before the model or test is modified.

Likewise, a visually convincing simulator effect must not substitute for a supported physical or mathematical model unless it is explicitly identified as a conceptual/didactic approximation.

## Versioning

Scientific model versions are independent from the HydroSIM application version.

Older scientifically valid model versions may remain available after a newer formulation supersedes them so that historical sessions remain reproducible.

A simulation session should eventually record the exact Scientific Model Set used to generate its results.
