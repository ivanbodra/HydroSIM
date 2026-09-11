# HydroSIM Acoustic Lab — Modular Pedagogical Specification

The Acoustic Lab pedagogical specification is now maintained as **modular canonical files** under:

`docs/pedagogy/acoustic_lab/`

Start with:

- [`acoustic_lab/00_overview.md`](acoustic_lab/00_overview.md)

Then load only the active lab file (`D01_...md` through `D17_...md`) plus neighboring labs when an explicit dependency requires it.

## Canonical editing policy

- `acoustic_lab/00_overview.md` + individual lab files are the active source of truth.
- Do **not** rebuild or maintain a monolithic working specification during active development.
- UX, Scientific Core, QA and implementation agents should work from the relevant lab block to reduce context/token cost and avoid unrelated edits.
- Historical pre-split content is preserved at `acoustic_lab/archive/acoustic_lab_specification_pre_split_2026-09-10.md` for traceability only; it is **not canonical**.

This file is intentionally kept small as a compatibility/index entry point for links that previously targeted the monolithic specification.
