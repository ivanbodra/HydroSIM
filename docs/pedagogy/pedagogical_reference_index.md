# HydroSIM Pedagogical Reference Index

Status: evidence-based recovery in progress  
Scope: teaching/visual inspiration, not scientific authority

## Purpose

This index records external lessons, courses, tutorials, simulators, and other teaching material that can be traced to the design history of HydroSIM and identifies the HydroSIM submodule(s) for which each source was actually used as pedagogical inspiration.

This document deliberately does **not** infer or invent references from subject similarity. A scientifically relevant publication, manufacturer manual, standard, or course is not listed here unless there is evidence that it was used as teaching/visual inspiration for HydroSIM.

Scientific references belong in the Scientific Registry or the corresponding science documentation. Operational/manufacturer references should likewise remain distinguishable from pedagogical inspiration.

## Evidence levels

- **Confirmed** — the source and its pedagogical use are explicitly preserved in HydroSIM discussion/repository history.
- **Recovered, mapping pending** — the source is demonstrably present in project history, but the exact pedagogical submodule/use has not yet been recovered strongly enough to assign it.
- Do not add speculative entries. If provenance is uncertain, leave the submodule without an external pedagogical reference until evidence is recovered.

## Confirmed pedagogical references

| HydroSIM submodule | External teaching reference | Pedagogical idea actually used | Evidence / project trace |
|---|---|---|---|
| **D6 — Beamforming & Electronic Steering** | **MIT OpenCourseWare — 2.682 Acoustical Oceanography — Lecture 11, simple beamformer material** | Plane-wave arrival offset across a fixed line array; electronic counter-delay / phase compensation; steering by processing rather than physical rotation; progression from channel offsets to coherent beam response. This informed the redesigned D6 narrative built around a small visible fixed array and `arrival offset → channel delays → aligned channels → coherent sum → steered response`. | HydroSIM issue #372 explicitly records the acoustics-class beamforming sequence as discussed from MIT OCW simple beamforming material. |

## Submodule reference map

This table is intentionally conservative. `Not yet recovered` means that no specific external *pedagogical* source has yet been recovered from project history for that submodule; it does **not** mean that the submodule lacks scientific references.

| Submodule | Pedagogical reference status |
|---|---|
| D1 — Acoustic Wave & Frequency | Not yet recovered |
| D2 — Pulse & Signal Processing | Not yet recovered |
| D3 — Sonar Equation & Propagation Loss | Not yet recovered |
| D4 — Sound Speed & Refraction | Not yet recovered |
| D5 — Transducer & Array Construction | Not yet recovered |
| D6 — Beamforming & Electronic Steering | **MIT OCW 2.682, Lecture 11 — confirmed** |
| D7 — Echosounders — SBES vs MBES | Not yet recovered |
| D8 — Bottom Detection | Not yet recovered |
| D9 — Multisector MBES | Not yet recovered |
| D10 — Vessel & Sensor Configuration | Not yet recovered |
| D11 — Vessel Motion | Not yet recovered |
| D12 — PU & Sensor Integration | Not yet recovered |
| D13 — Timing, Synchronization & Latency | Not yet recovered |
| D14 — Sounding Formation | Not yet recovered |
| D15 — Survey Planning | Not yet recovered |
| D16 — Survey Coverage & Acquisition Trade-offs | Not yet recovered |
| D17 — Uncertainty / TPU | Not yet recovered |

> Numbering above follows the pedagogical plan after retirement of the former standalone Acoustic Detection Fundamentals lesson. Preserve historical aliases where needed when tracing older issues/commits.

## Recovered project sources that are **not classified as pedagogical references here**

The project history contains important scientific/operational sources including the Ivan Guimaraes / UNH thesis context, Beaudoin–Hughes Clarke–Bartlett sound-speed work, Kongsberg documentation, IHR/Nistad/Westfeld ray-tracing/sound-speed material, IHO curriculum/standards, and other manufacturer/professional references. They are intentionally not promoted into this pedagogical-reference table merely because their subject matter overlaps a lesson. Their scientific or operational roles should remain separately traceable.

## Maintenance rule

When another historical teaching source is recovered, add it only with:

1. identifiable source (institution/author and course/lesson/material title where available);
2. link or durable bibliographic identifier when available;
3. HydroSIM submodule(s) in which it was actually used;
4. the specific teaching/visual idea borrowed or adapted;
5. project evidence showing that this was an inspiration rather than a retrospective association.

A single source may map to several submodules, and a submodule may use several pedagogical references. Do not force one-to-one mapping.
