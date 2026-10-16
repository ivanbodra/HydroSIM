# Initial CAHO curricular map

Status: source-backed partial map of the supplied shared collection; not the official complete course syllabus.
Evidence and exact source paths: [reading log](reading_log.md) and [inventory](source_inventory.csv).

## Explicit acoustic unit structure

CAHO-AC-01 p.13 supplies this structure. Candidate HydroSIM links are pedagogical interpretations; the individual unit files remain unread unless explicitly noted.

| Unit in course material | Displayed TA | Existing HydroSIM candidate | Initial treatment / evidence level |
|---|---:|---|---|
| Noções de Acústica | 7 | PED-D1 waves; later PED-D6/PED-D7 interference | Interactive demonstration; introductory wave vocabulary is read in CAHO-AC-01 pp.29–38, interference pp.49–52 |
| Fundamentos de Acústica Submarina | 13 | PED-D3 losses/noise; PED-D4 refraction | Interactive demonstration or full activity; unit existence confirmed, individual lessons not yet read |
| Introdução ao processamento de sinais acústicos | 8 | PED-D2 pulse/processing; PED-D9 detection as later application | Interactive demonstration; PDS file titles listed, detailed sequence pending |
| A Equação Sonar | 4 | PED-D3 | Interactive demonstration; dedicated lesson listed, not read |
| Sistemas Acústicos (Trabalho e Seminário) | 15 | Reuse selected prior experiences if relevant | No new simulation by default; read the assignment before proposing support |

CAHO-AC-01 p.53 already directs learners to existing acoustic animations. Historical background, course administration and bibliography need no additional simulator treatment.

## Source-backed learning connections

These links use course content actually read. Learning questions, assessment evidence and classroom treatment are pedagogical interpretations.

| Link ID | Course source / PDF pages | Course-explicit content | HydroSIM reuse | Treatment and classroom position | Evidence of learning |
|---|---|---|---|---|---|
| C01 | CAHO-AC-01 pp.29–38 | Pressure-wave representation; frequency/period/amplitude/phase vocabulary | PED-D1 | Short interactive demonstration during the opening foundations lesson | Predict a frequency/period/wavelength change and distinguish particle oscillation from propagation |
| C02 | CAHO-AC-01 pp.49–52 | Phase-dependent reinforcement/cancellation | PED-D6/PED-D7 as later application, not a complete substitute for basic superposition | Interactive demonstration; compare to an existing animation before adding a new surface | Explain why changing relative phase changes a sum while the sources remain fixed |
| C03 | CAHO-HYD-05 pp.2, 27–43, 51, 53–54 | Profile-based ray tracing, mismatch consequences, prediction-first simulation and XYZ reconstruction | PED-D4; later PED-D15 | Guided full classroom activity during/after the refraction explanation | Predict then observe a ray/endpoint change; compare matched and mismatched reconstruction of the same observation |
| C04 | CAHO-HYD-05 pp.23, 45–47, 51 | Sound speed near the transducer and beam direction; distinction from water-column profile | PED-D4/PED-D7 science capital, but the inspected PED-D4 UI does not expose this independent surface-speed control | Separate interactive demonstration candidate; continue existing classroom tool until its exact HydroSIM path is verified | Explain which measurement affects steering and which profile describes propagation |
| C05 | CAHO-HYD-09 pp.2, 16–33 | CW/chirp, duration/bandwidth, matched filter and range resolution | PED-D2; PED-D3 only when processing/SNR behavior is scientifically available | Interactive demonstration before the integrated resolution/density activity | Compare two pulses with a stated normalization; explain which change affects resolving response |
| C06 | CAHO-HYD-09 pp.5–15, 34, 39–47 | Angular geometry, beamwidth and footprint in spatial resolution | PED-D6/PED-D8 | Interactive demonstration; retrieve prior beam concepts rather than teach them twice | Explain why denser beam centres do not themselves shrink physical footprints |
| C07 | CAHO-HYD-09 pp.34, 48–55, 65–68 | Along/across sampling; speed, sector, beam spacing and High Density | PED-D17; PED-D16 only for line-layout extension | Full laboratory after individual controls; integrated scenario for a later survey decision | Choose a configuration and justify separate consequences for spacing, footprint support and data density |
| C08 | CAHO-HYD-12 pp.2–3, 6–23 | Calibration objectives; installation/frame prerequisites; residual offsets vs dynamic problems | PED-D11/PED-D12/PED-D14 as prerequisites; P1 for signatures | Brief prerequisite check and signature demonstration before P2 | Distinguish a conventional calibration bias from an unresolved installation/environment/timing problem |
| C09 | CAHO-HYD-12 pp.27–30, 35–52, 68–69 | Area/feature selection; line direction/speed/overlap; compact four-line exercise | P2/P3 | Integrated planning/acquisition stage before the SIS/CARIS practical | Defend an observable line/segment choice and explain why a weak geometry gives little information |
| C10 | CAHO-HYD-12 pp.60–74 | Applying residual corrections; checking repeatability/QC; subsequent practical and independent repeat | P4/P5 | Calibration activity and debrief supporting the existing professional-software practical | Submit an estimate, inspect residual/holdout evidence and justify acceptance or recollection |
| C11 | CAHO-HYD-12 pp.7–10 | Dynamic residuals can require different checks from constant biases | Optional P6 forward-model demonstration only | Advanced complementary demonstration after P1–P5, subject to current UX/QA readiness | Explain why a plausible residual pattern is not a unique cause diagnosis |

C11 is a pedagogical extension from the course's dynamic-residual discussion. The inspected course source does not explicitly teach RISC.

## Remaining hydrography lessons: title-level inventory

These folders are verified; their individual lesson contents have **not** been read in this cycle. The links below are candidates, not validated learning-objective matches.

| Displayed lesson | Candidate treatment / existing capital | Reading decision |
|---|---|---|
| Aula 1 (4ha) | No additional treatment for history/administration by default; operational context may motivate later labs | Read the actual presentation |
| Aula 2 - S44 (5ha) | Static comparison or bounded PED-D18 uncertainty/PED-D16 planning example | Read actual standard edition and class framing; no compliance certification from a simulator |
| Aula 3 - SBES | PED-D8 comparison; selected PED-D2/PED-D9 signal/detection support | Read class objectives and existing exercises |
| Aula 4 - Princípios MBES | PED-D6/PED-D7/PED-D8/PED-D9 | Compare to existing MATLAB/beamsteering media |
| Aula 6 - Sensores de Movimento (6ha) | PED-D12/PED-D14/PED-D15 | Read sensor and dynamic-residual teaching, including existing videos |
| Aula 7 - Posicionamento e Orientação (4ha) | Static frame/reference explanation and acquisition-input reuse | Full GNSS teaching is outside current HydroSIM scope |
| Aula 8 - Alcance Sonar (3ha) | PED-D3 | Read its current MATLAB material before requesting a new calculator |
| Aula 10 - MBES - Instalação | PED-D11/PED-D13 | Read installation practice/video and distinguish physical survey from runtime calibration |
| Aula 11 - Medição de Offset | PED-D11 and an annotated frame/offset exercise | Read its exercise/report examples; preserve source conventions explicitly |
| Aula 13 - Side Scan Sonar | Static visual or demonstration candidate | Deferred scope evaluation after reading; current product does not cover full SSS |
| Aula 14 - Sistemas Alternativos de Batimetria (2ha) | Annotated comparison candidate | Read before choosing any simulation |
| Aula 15 - Perfilador de Subfundo | Guided animation or static comparison candidate | Deferred scope evaluation |
| Aula 16 - Sistemas Autônomos de Levantamento (2ha) | Static systems/mission diagram candidate | No automatic AUV/ROV simulator expansion |
| Aula 17 - Maré aplicada (3ha) | Static vertical-reference comparison candidate | Tide theory is outside current baseline; read the presentation first |
| Aula 19 - Protocolos de Comunicação (Antes do RECON) (8h) | PED-D13/PED-D14 | Read message/connection exercises before designing learner controls |
| Aula 23 - Planejamento de LH (14h) | PED-D16/PED-D17; later A5 | Read its operational task and constraints |

Lessons 5, 9 and 12 are mapped above. Missing numbers in the displayed folder sequence do not prove missing teaching. The collection is not a complete formal timetable.

## Prerequisites and use around class

Course-explicit anchors:
- CAHO-HYD-05 pp.4–5 revisits directivity, Mills Cross, focusing/steering, shading and detection before refraction.
- CAHO-HYD-12 p.3 revisits local/vessel frames and offsets; p.23 states preconditions concerning installation, timing, sound speed and sensor performance.
- CAHO-HYD-12 p.73 places a software calibration practical after its theory.

Pedagogical sequencing:
1. Before class, elicit a prediction or retrieve only the required earlier concept.
2. During explanation, isolate one control–consequence relationship.
3. After explanation, compare cases and require a causal explanation.
4. Before professional-software practice, use P2–P5 as preparation where current implementation is verified.
5. After practice, compare the student's decisions and remaining limitations; do not claim simulator success equals field competence.

The first pilot is C03. It uses the existing column-profile comparison while explicitly deferring C04's independent surface-speed experiment.
