# HydroSIM Language and Localization Policy

Version: 0.1.0
Status: Normative project convention

## 1. Principle

English is the canonical language of HydroSIM.

The scientific and software architecture must have one authoritative vocabulary. Translations are presentation layers and must not create alternative internal names, identifiers, schemas, or scientific semantics.

## 2. Canonical English layer

The following must be written in English:

- source code;
- package, module, class, function, method, variable, field, and enum names;
- API names and public programmatic interfaces;
- YAML, JSON, database, and interchange schema keys;
- scientific-registry identifiers and canonical scientific definitions;
- model and equation identifiers;
- tests and golden-value definitions;
- code comments and docstrings;
- internal/logical state names;
- internal diagnostic and machine-readable messages;
- scenario identifiers and configuration keys;
- canonical scientific and developer documentation.

Examples of canonical terminology include:

- `truth`, `observed`, `configured`, `estimated`, `derived`;
- `along_track`, `across_track`;
- `along_track_angle`, `across_track_angle`;
- `a_priori_uncertainty`;
- `truth_error` / `truth_error_vector` where appropriate;
- `crossline_residual`;
- `lever_arm`, `latency`, `sound_speed`, `water_level`, `waterline`.

Scientific terminology should preserve established English usage from the relevant literature whenever possible.

## 3. Software localization

HydroSIM user-facing applications must support bilingual presentation from the interface foundation.

The initial supported locales are:

- English (`en`), the default and fallback locale;
- Brazilian Portuguese (`pt-BR`).

Localization may translate user-facing labels, descriptions, help text, tutorials, exercises, warnings, graph titles, axes, legends, annotations, and other presentation content. It must not translate or alter canonical internal identifiers.

No user-facing string that participates in the supported application experience should be unnecessarily hard-coded inside UI components. Localization resources must remain separated from scientific and computational logic.

For example, the interface may display `Incerteza a priori`, while the underlying field remains `a_priori_uncertainty`.

A localized scenario editor may display `Ângulo across-track` or an approved Portuguese equivalent, but the persisted schema key remains `across_track_angle`.

Language switching must not require rebuilding scientific state and should not reset an active experiment unless a technical limitation is explicitly documented.

## 4. Documentation

The English documentation is canonical.

Portuguese documentation is a translated edition of a corresponding English version. A translation must identify the version of the canonical documentation to which it corresponds.

Recommended version presentation:

- `Scientific Documentation vX.Y.Z — English (canonical)`
- `Documentação Científica vX.Y.Z — Português (translation)`

If a translated document and its canonical English source disagree, the English canonical version governs the software/scientific definition until the discrepancy is reviewed.

Translations should preserve equations, symbols, identifiers, units, citations, and references unchanged unless localization specifically requires explanatory text.

## 5. Along-track and across-track terminology

HydroSIM adopts **along-track** and **across-track** as preferred geometric terms in its canonical vocabulary.

- **along-track**: longitudinal direction associated approximately with vessel/body `+X` (Forward);
- **across-track**: transverse direction associated with the vessel/body Y axis (`+Y` Starboard and `-Y` Port).

These terms describe geometry relative to the vessel/system and must not be interpreted as geographic horizontal/vertical directions.

Canonical identifiers use snake_case, for example:

- `along_track`
- `across_track`
- `along_track_angle`
- `across_track_angle`
- `along_track_error`
- `across_track_error`

Where sign conventions are relevant, they must be stated explicitly rather than inferred from the words along-track or across-track.

## 6. Scientific registry and bibliography

Scientific-registry entries are canonical in English. This includes model names, definitions, assumptions, validity limits, variable descriptions, implementation notes, and validation descriptions.

Bibliographic titles and quotations retain their source language. Established terminology from the literature, such as `wobble`, `motion residual`, `beam steering`, `matched filter`, and `crossline`, should not be translated inside canonical identifiers merely to support a localized interface.

Localized documentation may explain these terms in Portuguese while retaining the canonical English term where useful for traceability to the literature.

## 7. Compatibility rule

Localization must be reversible at the presentation boundary: changing the UI/documentation language must not change simulation results, stored scientific state, schema meaning, scenario identity, or reproducibility.

No scientific model may branch on the selected human language except for presentation formatting.

## 8. Change control

New canonical technical terms should be introduced in English and reused consistently across code, schemas, registry entries, tests, and documentation.

If terminology changes, compatibility and migration of public APIs or persisted schemas must be considered explicitly rather than silently renaming fields.