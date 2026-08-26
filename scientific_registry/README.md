# HydroSIM Scientific Registry

This directory stores the scientific metadata used to document, validate and version the models implemented by HydroSIM.

The registry is separate from the executable code so that scientific assumptions, references and model versions remain auditable.

## Planned structure

```text
scientific_registry/
├── models/
│   ├── geometry/
│   ├── propagation/
│   ├── acoustics/
│   ├── beamforming/
│   └── signal_processing/
├── references/
│   └── bibliography.yaml
└── validation/
    └── golden_values/
```

## Minimum metadata for a scientific model

Each model record should contain:

- stable ID;
- semantic version;
- scientific status;
- formula or algorithm definition;
- input variables and units;
- output variables and units;
- coordinate/sign conventions where applicable;
- validity domain;
- assumptions and simplifications;
- primary scientific references;
- secondary references or manuals;
- implementation path;
- numerical validation cases;
- alternatives;
- known limitations.

## Scientific implementation rule

A scientific equation must not be changed merely to satisfy a software test.

When implementation and reference results disagree, the discrepancy must be investigated and documented before the model or test is modified.

## Versioning

Scientific model versions are independent from the HydroSIM application version.

A simulation session should eventually record the exact Scientific Model Set used to generate its results.
