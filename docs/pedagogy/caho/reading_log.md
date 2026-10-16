# CAHO source-reading log

Date: 2026-10-16. Root and exact relative paths: source_inventory.csv.
Locators below are 1-based **PDF page numbers**. Printed slide numbers sometimes skip pages; they must not substitute for these locators.

## Obtained sources

| ID | Material / author as stated | Pages | Review in this cycle | Next reading |
|---|---|---:|---|---|
| CAHO-AC-01 | `Acústica Submarina/1 - Aula Inicial_3h.pdf`; CF Bruno Neves | 53 | Extracted text read on all PDF pages; visual checks on 5, 13, 29, 48 | Check remaining figures/animations and read the actual unit lessons |
| CAHO-HYD-05 | `Hidrografia/Aula 5 - Velocidade do Som e Refração (5ha)/Aula 5 Velocidade do Som e Refração.pdf`; CF Bruno Neves, CAHO2026 | 55 | Extracted text read on all pages; visual checks on 33, 39, 45, 51 | Inspect remaining figure-only explanations and reconcile with acoustic refraction/ray-tracing lessons |
| CAHO-HYD-09 | `Hidrografia/Aula 9 - Resolução/Aula 9 - Resolução e Densidade.pdf`; CF Bruno Neves, CAHO2026 | 71 | Extracted text read on all pages; visual checks on 34, 48, 55, 68 | Inspect remaining figures, MATLAB/Matched Filter/Chirp material, compare the earlier resolution PDF |
| CAHO-HYD-12 | `Hidrografia/Aula 12 - MBES - Patch Test/Aula 12 - Calibração (Patch Test).pdf`; CF Bruno Neves, CAHO2026 | 80 | Extracted text read on all pages; visual checks on 54, 56, 68, 69 | Inspect other geometry figures and pages 76–80 as images; read practical instructions/data and videos |
| CAHO-HYD-APOSTILA-2026-07-07 | `Apostila de Hidrografia_BNB_Mod3_07JUL2026.pdf`; Bruno Neves Baptista | 285 | Cover/credits/draft notice and contents, PDF 1–11; purpose 23; completion state 282–285; illustration index 12–21 only skimmed | Read substantive chapters incrementally; the chapter index is a locator, not proof that those chapters were analyzed |

The four presentations are recorded as `partially_read` because text review and four sampled visual pages do not establish complete review of every illustration, linked video or instructor explanation.

## File identity

- **CAHO-HYD-APOSTILA-2026-07-07**: SHA-256 `4c11d482bb1ab857220f7e2eee0792295514508f9c5f443c8999849c0127b851`.
- **CAHO-AC-01**: SHA-256 `a908d34f4253ec83bd2a7521648a8649009a97f92b9c6014ffa73fdba42ba286`.
- **CAHO-HYD-05**: SHA-256 `c775a7721889e66c00f2ba0e5a00fb75f7dcbc993236371607f9562df29a4458`.
- **CAHO-HYD-09**: SHA-256 `bdc4b7a015c156a02ba902ca8a5ace498711e7621f83179f26bac01eeae4637f`.
- **CAHO-HYD-12**: SHA-256 `07236fb43c067453333278ab4666d66b203050da8352eae17c908de42b7ee509`.

Hashes identify the copies actually examined. Source filenames, folder modification labels and revision statements are distinct evidence; a modification timestamp alone does not establish curricular precedence.

## Reading findings that constrain mapping

1. **Acoustic course structure.** CAHO-AC-01 p.5 states propagation and instrument-application objectives. P.13 lists five units with TA values 7, 13, 8, 4 and 15: acoustic foundations; underwater-acoustic foundations; acoustic signal processing; sonar equation; acoustic systems work/seminar. Retain the displayed TA label; this record does not infer its institutional definition.
2. **Explicit practical support already exists.** CAHO-HYD-05 pp.7 and 51 include simulation and SVP practice; p.51 requires prediction before simulation. CAHO-HYD-09 pp.29 and 62 refers to MATLAB and an EMX calculator. CAHO-HYD-12 p.73 prepares a subsequent calibration practical using SIS/CARIS and example data. Linked resources have not all been run or evaluated.
3. **Source scope is broader than current HydroSIM.** CAHO-HYD-05 p.3 and the visible lesson folders include side-scan, alternative bathymetry, sub-bottom, autonomous systems and other subjects. Listing them does not approve new HydroSIM modules.
4. **The handout is explicitly provisional.** Its p.4 discloses technical/editorial work remaining; p.285 describes continuing revision. The contents index and body numbering near p.282 differ, and p.282–283 contain incomplete headings/notes. Use the actual lesson presentation where available; do not conclude that the class omits a topic because the handout has a placeholder.
5. **Language must not silently become a new model.** CAHO-HYD-05 p.39 uses a temperature-related layer label while describing constant sound-speed segments. HydroSIM uses piecewise-constant sound speed: retain `isovelocidade` for that model and do not imply that constant temperature guarantees constant sound speed.
6. **Generalized shape rules need conditions.** CAHO-HYD-05 p.33 motivates smiling/crying swaths. HydroSIM must keep each result tied to its specified Truth, processing profile, geometry and sign convention; no universal sign table is inferred from the illustration.
7. **Density equations are bounded examples.** CAHO-HYD-09 p.48 presents a simplified geometric/cadence model. It is not a replacement for actual retained-position spacing, finite-footprint coverage or a validated achievable-ping-rate model. More points are not automatically more independent resolution.
8. **Calibration references present alternatives.** CAHO-HYD-12 pp.32, 54, 56 and 58 discuss different orders. P.68 includes same/opposite heading arrangements; P2 currently specifies a bounded same-direction reference geometry. Do not turn one convention into universal law or mark an unmodelled alternative physically invalid. Teaching additional configurations requires a separately justified scientific crosswalk.
