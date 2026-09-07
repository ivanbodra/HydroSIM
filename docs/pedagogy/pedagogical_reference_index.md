# HydroSIM Pedagogical Reference Index

Status: evidence-based recovery + candidate review sources  
Scope: teaching/visual inspiration, not scientific authority

## Purpose

This index has two deliberately separate roles:

1. preserve external teaching material that is demonstrably part of HydroSIM's pedagogical design history; and
2. maintain a curated list of reputable **candidate sources for the next pedagogical review**.

A candidate is not retroactively called an inspiration. It becomes an adopted pedagogical reference only after the HydroSIM review actually uses a teaching/visual idea from it.

Scientific references belong in the Scientific Registry or corresponding science documentation. Operational/manufacturer references should likewise remain distinguishable from pedagogical inspiration.

## Status vocabulary

- **Confirmed inspiration** — source and pedagogical use are explicitly preserved in HydroSIM history.
- **Candidate for review** — reputable source identified as potentially useful for reviewing one or more lessons; no claim that it historically inspired HydroSIM.
- **Not yet recovered** — no specific historical external pedagogical source has yet been recovered for that lesson.

## Confirmed pedagogical references

| HydroSIM submodule | External teaching reference | Pedagogical idea actually used | Evidence / project trace |
|---|---|---|---|
| **D6 — Beamforming & Electronic Steering** | **MIT OpenCourseWare — 2.682 Acoustical Oceanography — Lecture 11, simple beamformer material** | Plane-wave arrival offset across a fixed line array; electronic counter-delay / phase compensation; steering by processing rather than physical rotation; progression from channel offsets to coherent beam response. This informed the redesigned D6 narrative built around a small visible fixed array and `arrival offset → channel delays → aligned channels → coherent sum → steered response`. | HydroSIM issue #372 explicitly records the acoustics-class beamforming sequence as discussed from MIT OCW simple beamforming material. |

## Candidate source set for the next pedagogical review

These sources were selected because they come from established ocean-mapping/acoustics institutions or leading researchers and contain material likely to improve the *teaching experience* of existing HydroSIM lessons. Their presence in this table is a review hypothesis, not evidence of historical influence.

| Candidate source | Lessons to inspect | Review question / potentially useful teaching idea |
|---|---|---|
| **MIT OpenCourseWare — 2.682 Acoustical Oceanography (James Lynch), lecture sequence** | D1, D3, D4, D5, D6 | Are wave/propagation/array concepts introduced through a clearer causal or visual progression than HydroSIM currently uses? D6 Lecture 11 is already confirmed inspiration. |
| **John E. Hughes Clarke — “Multibeam Echosounders”** | D5–D9, D14, D16, D17 | Can HydroSIM better connect pulse bandwidth, beamwidth, beam spacing, stabilization, bottom detection, sound speed and sensor integration to the resulting resolution/fidelity of the seafloor representation? |
| **John E. Hughes Clarke — work on the impact of acoustic imaging geometry on multibeam bathymetry** | D7, D8, D11, D13, D14, D16, D17 | Can range, angle, azimuth, density and overlap become visible acquisition consequences rather than isolated parameters? Can vessel motion, speed, stabilization, beam spacing and detection leave understandable signatures in the acquired seafloor? |
| **Jonathan Beaudoin — real-time monitoring of uncertainty due to refraction / ray-tracing work** | D4, D17 | Can D4 progress from merely drawing refracted rays to showing how an incorrect/insufficient sound-speed description becomes a spatial sounding error across the swath? |
| **Jonathan Beaudoin — oceanographic pre-analysis / sound-speed planning work** | D4, D15, D16 | Can environmental variability be connected visually to where/when sound-speed observations are needed and to the acquisition consequences of inadequate sampling? |
| **Jonathan Beaudoin, John Hughes Clarke, Jonathan Bartlett — surface sound-speed / multisector MBES work** | D4, D6, D9, D14 | Can HydroSIM make the distinction between surface sound speed used in steering and water-column profile used in propagation/ray tracing especially clear? |
| **Thomas Weber, Jonathan Beaudoin et al. — MBES system optimization work** | D2, D6–D9, D16 | Can the learner see why system choices such as frequency encoding, sectors, sounding density, dual-swath behavior, FM pulse and transmit focusing exist, without turning the lesson into a vendor configuration panel? |
| **Brian Calder — uncertainty / completeness work, including “Use (and Potential Abuse) of Uncertainty”** | D17 | Does D17 teach uncertainty as more than an RSS/TPU calculation? Can it distinguish uncertainty of observed soundings from completeness/knowledge of the seafloor without expanding into bathymetric processing? |
| **UNB Ocean Mapping Group — Multibeam Sonar Theory / class reports and training material; John Hughes Clarke / Ian Church context** | D7–D17 | What established teaching sequences, diagrams or exercises make the transition from sonar physics to integrated multibeam acquisition easier to understand? |
| **DHN — NORMAM-501/DHN and associated hydrographic guidance** | D4, D10, D15–D17 | Do HydroSIM visual lessons lead naturally to the operational concepts a Brazilian hydrographer encounters: offsets, surface SV/SVP, swath, overlap/coverage, across-track uncertainty and integrated acquisition? Use as operational/pedagogical cross-check, not as authority for every physical model. |

## Review priorities

### Priority A — foundational acoustics: D1–D4

Use MIT material as the primary pedagogical benchmark, complemented by CCOM/UNH material where it directly connects acoustic physics to hydrographic consequence.

Questions:
- Does each lesson have one dominant physical discovery?
- Are controls tied immediately to observable consequences?
- Are common/fixed plot scales used where autoscaling would hide the effect?
- Does D4 connect ray geometry to sounding consequence rather than stop at ray visualization?

### Priority B — arrays, beamforming and MBES: D5–D9

Use MIT for first-principles array/beamforming teaching and Hughes Clarke / Beaudoin / Weber / UNB-OMG for the transition into real multibeam behavior.

Questions:
- Are array construction and beamforming kept pedagogically distinct?
- Does each new control introduce a genuinely new concept?
- Can the learner trace signal/channel behavior into beam response and then into acquisition geometry?
- Are multisector, multiple virtual RX beams and bottom detection introduced only where they add a new idea?

### Priority C — integrated acquisition: D10–D17

Use CCOM/UNH and UNB/OMG as the main pedagogical references, with DHN as a Brazilian operational cross-check.

Questions:
- Do installation, motion, timing, sound speed and sonar settings visibly propagate into sounding position/quality?
- Can the learner recognize acquisition signatures rather than memorize parameter definitions?
- Do planning/coverage lessons synthesize previous concepts instead of repeating them?
- Does uncertainty remain connected to the physical/acquisition causes already experienced in earlier lessons?

## Review decision vocabulary

For each D1–D17 lesson, compare the current HydroSIM implementation with the candidate material and record one or more of:

- **KEEP** — current pedagogical experience already communicates the concept well.
- **REFINE** — retain the lesson and scientific scope, but improve a visualization, causal sequence, interaction or explanation.
- **MERGE / MOVE** — the concept is duplicated or is taught more effectively in another existing lesson.
- **ADD EXPERIENCE** — a missing interactive experiment would materially improve understanding without adding a new standalone subject.

The review is **not** an invitation to expand HydroSIM into every topic found in the source material. New material must support the existing product definition: a hydrographic acquisition simulator with a didactic module.

## Current submodule reference map

| Submodule | Historical pedagogical reference | Candidate review families |
|---|---|---|
| D1 — Acoustic Wave & Frequency | Not yet recovered | MIT |
| D2 — Pulse & Signal Processing | Not yet recovered | MIT; Weber/Beaudoin MBES optimization |
| D3 — Sonar Equation & Propagation Loss | Not yet recovered | MIT |
| D4 — Sound Speed & Refraction | Not yet recovered | MIT; Beaudoin; Beaudoin/Hughes Clarke/Bartlett; DHN |
| D5 — Transducer & Array Construction | Not yet recovered | MIT; Hughes Clarke |
| D6 — Beamforming & Electronic Steering | **MIT OCW 2.682 Lecture 11 — confirmed** | MIT; Hughes Clarke; Beaudoin/Hughes Clarke/Bartlett; Weber/Beaudoin |
| D7 — Echosounders — SBES vs MBES | Not yet recovered | Hughes Clarke; Weber/Beaudoin; UNB/OMG |
| D8 — Bottom Detection | Not yet recovered | Hughes Clarke; Weber/Beaudoin; UNB/OMG |
| D9 — Multisector MBES | Not yet recovered | Hughes Clarke; Beaudoin/Hughes Clarke/Bartlett; Weber/Beaudoin; UNB/OMG |
| D10 — Vessel & Sensor Configuration | Not yet recovered | UNB/OMG; DHN |
| D11 — Vessel Motion | Not yet recovered | Hughes Clarke; UNB/OMG |
| D12 — PU & Sensor Integration | Not yet recovered | UNB/OMG |
| D13 — Timing, Synchronization & Latency | Not yet recovered | Hughes Clarke; UNB/OMG |
| D14 — Sounding Formation | Not yet recovered | Hughes Clarke; Beaudoin/Hughes Clarke/Bartlett; UNB/OMG |
| D15 — Survey Planning | Not yet recovered | Beaudoin; UNB/OMG; DHN |
| D16 — Survey Coverage & Acquisition Trade-offs | Not yet recovered | Hughes Clarke; Beaudoin; Weber/Beaudoin; UNB/OMG; DHN |
| D17 — Uncertainty / TPU | Not yet recovered | Hughes Clarke; Beaudoin; Calder; UNB/OMG; DHN |

> Numbering follows the pedagogical plan after retirement of the former standalone Acoustic Detection Fundamentals lesson. Preserve historical aliases where needed while tracing older issues/commits.

## Source entry points for review

Use authoritative/institutional landing pages and durable repositories as the starting points for the review; resolve the exact lecture/paper/report before adopting a pedagogical idea.

- MIT OpenCourseWare, **2.682 Acoustical Oceanography**: <https://ocw.mit.edu/courses/2-682-acoustical-oceanography-spring-2012/>
- UNH Scholars Repository / Center for Coastal and Ocean Mapping: <https://scholars.unh.edu/ccom/>
- UNB Ocean Mapping Group publications and class reports: <https://www.omg.unb.ca/publications/>
- Brazilian Navy / DHN, NORMAM and hydrographic normative material: <https://www.marinha.mil.br/dhn/>

Specific CCOM items identified for review should be resolved through the UNH repository by author/title before they are promoted from candidate to adopted pedagogical reference.

## Recovered project sources that are not classified as pedagogical references here

The project history contains important scientific/operational sources including the Ivan Guimaraes / UNH thesis context, Beaudoin–Hughes Clarke–Bartlett sound-speed work, Kongsberg documentation, IHR/Nistad/Westfeld ray-tracing/sound-speed material, IHO curriculum/standards, and other manufacturer/professional references. They are not retroactively classified as historical pedagogical inspiration merely because their subject matter overlaps a lesson.

## Maintenance rule

When a candidate source actually changes or validates the teaching design of a HydroSIM lesson, promote that use into the confirmed/adopted pedagogical section and record:

1. identifiable source (institution/author and course/lesson/material title);
2. durable link or bibliographic identifier;
3. HydroSIM submodule(s) where it was used;
4. specific teaching/visual idea borrowed or adapted;
5. review decision (`KEEP`, `REFINE`, `MERGE / MOVE`, or `ADD EXPERIENCE`);
6. project issue/commit/PR preserving the resulting decision.

A single source may map to several submodules, and a submodule may use several pedagogical references. Do not force one-to-one mapping and do not promote candidates merely because they are scientifically authoritative.