# HydroSIM Acoustic Lab — Consolidated Pedagogical Bibliography

Status: **canonical cross-lab reference index**

This file consolidates the recognized references already used by the modular Acoustic Lab treatises `D01`–`D17`.

It is **not** a replacement for the references recorded inside each lab file. Each lab remains independently implementation-ready and retains the exact sources supporting its pedagogy. This index exists for cross-lab traceability, deduplication and future source maintenance.

For normal UX work, read `00_overview.md` plus the active lab file. Read this bibliography only when cross-lab source provenance or source reuse is needed.

## Standards, competence frameworks and institutional guidance

| ID | Reference | Used in lab(s) |
|---|---|---|
| R01 | **International Hydrographic Organization (IHO), _S-5A — Standards of Competence for Category “A” Hydrographic Surveyors_, Ed. 2.0.0, Aug 2026.** Competence anchor used with lab-specific sections ranging from underwater acoustics and multibeam systems to sensor integration, survey planning and uncertainty. <https://portal.iho.int/share/api/files/AAAAAAABALI/Standard%20S-5A%20Ed.2.0.0/S-5A_Ed2.0.0_05May26.pdf> | **D1–D17** |
| R02 | **International Hydrographic Organization (IHO), _S-44 — Standards for Hydrographic Surveys_, Ed. 6.2.0, Oct 2024.** THU/TVU, whole-system uncertainty, confidence/coverage basis and a priori/a posteriori uncertainty assessment. <https://iho.int/uploads/user/pubs/standards/s-44/S-44_Edition_6.2.0_adopted.pdf> | **D17** |
| R03 | **NOAA Office of Coast Survey, _Hydrographic Surveys Specifications and Deliverables_, Version 2026.0.00 (2026).** Coverage, corrections, quality-control and uncertainty requirements. <https://nauticalcharts.noaa.gov/publications/documents/HSSD_2026-0-00.pdf> | **D11, D14, D15, D16, D17** |
| R04 | **NOAA Office of Coast Survey, _Field Procedures Manual_ (2020), §1.4 / §1.4.1.** Vessel reference frame, static offsets and sonar/GNSS/IMU measurement centres. <https://nauticalcharts.noaa.gov/publications/docs/standards-and-requirements/fpm/field_procedures_manual_2020.pdf> | **D10** |
| R05 | **NOAA Office of Coast Survey, _Field Procedures Manual_ (2014).** Motion/remote-heave processing and acquisition-system latency guidance. <https://www.nauticalcharts.noaa.gov/publications/docs/standards-and-requirements/fpm/2014-fpm-final.pdf> | **D11, D13** |
| R06 | **NOAA Office of Coast Survey, “Hydrographic Survey Equipment — Multibeam Echo Sounders.”** Institutional explanation of MBES swath acquisition and area coverage. <https://nauticalcharts.noaa.gov/learn/hydrographic-survey-equipment.html> | **D15, D16** |
| R07 | **International Hydrographic Review (2025), “Survey systems verification and calibration in the hydrospatial domain.”** Dimensional control, SRF alignment, lever arms, six-DOF motion and latency calibration. <https://ihr.iho.int/articles/survey-systems-verification-and-calibration-in-the-hydrospatial-domain/> | **D10, D11, D13** |
| R08 | **Canadian Hydrographic Service, _Hydrographic Survey Management Guidelines_, Ed. 4, Feb 2021.** A priori, real-time and post-survey uncertainty assessment and TPU error-budget practice. <https://www.chs.gc.ca/documents/data-gestion/guidelines-directrices/sg-ld-2021-eng.pdf> | **D17** |
| R09 | **National Marine Electronics Association (NMEA), _NMEA 0183 — Serial Data Networking_.** Public authoritative description of serial marine data transport/protocol layers. <https://www.nmea.org/nmea-0183.html> | **D12** |
| R10 | **National Marine Electronics Association (NMEA), _OneNet®_.** Standardized IP/Ethernet marine-device networking example. <https://www.nmea.org/nmea-onenet.html> | **D12** |

## Foundational acoustics, ocean mapping and peer-reviewed / academic sources

| ID | Reference | Used in lab(s) |
|---|---|---|
| R11 | **MIT OpenCourseWare, 2.682 _Acoustical Oceanography_, James Lynch, Spring 2012.** First-principles wave, propagation and refraction background. <https://ocw.mit.edu/courses/2-682-acoustical-oceanography-spring-2012/> | **D1, D3, D4** |
| R12 | **MIT OpenCourseWare, 2.682 _Acoustical Oceanography_, Lecture 11, James Lynch, Spring 2012.** Array beamforming, steering and grating-lobe fundamentals. <https://ocw.mit.edu/courses/2-682-acoustical-oceanography-spring-2012/resources/mit2_682s12_lec11/> | **D5, D6** |
| R13 | **Schock, Steven G.; LeBlanc, Lester R.; Mayer, Larry A. (2000), “The Development of Chirp Sonar Technology and Its Applications.”** FM chirp energy and wideband resolution. <https://scholars.unh.edu/ccom/541/> | **D2** |
| R14 | **Hughes Clarke, John E. (2017), “Multibeam Echosounders,” in _Submarine Geomorphology_.** MBES signal, beam/swath geometry, bottom detection, resolution and survey-sampling context. <https://scholars.unh.edu/ccom/1370/> ; DOI: <https://doi.org/10.1007/978-3-319-57852-1_3> | **D2, D3, D5, D6, D7, D8, D14, D16** |
| R15 | **Schmidt, Val E.; Weber, Thomas C.; Lurton, Xavier (2013), “Optimizing Resolution and Uncertainty in Bathymetric Sonar Systems.”** SNR, spatial resolution and measurement-uncertainty trade-offs. <https://scholars.unh.edu/ccom/848/> | **D3** |
| R16 | **Beaudoin, Jonathan (2010), “Real-time Monitoring of Uncertainty due to Refraction in Multibeam Echo Sounding.”** Refraction-driven sounding uncertainty. <https://scholars.unh.edu/ccom/1050/> | **D4** |
| R17 | **Beaudoin, Jonathan; Calder, Brian R.; Hiebert, J.; Imahori, Gretchen (2009), “Estimation of Sounding Uncertainty from Measurements of Water Mass Variability.”** Water-mass variability and sounding uncertainty. <https://scholars.unh.edu/ccom/481/> | **D4** |
| R18 | **Beaudoin, J. D.; Hughes Clarke, J. E.; Bartlett, J. E. (2004), “Application of surface sound speed measurements in post-processing for multi-sector multibeam echosounders.”** Surface sound-speed steering, sector timing/boundaries and multisector association. <https://scholars.unh.edu/ccom/1335/> | **D4, D9** |
| R19 | **de Moustier, Christian; Kraft, Barbara J.; McGillicuddy, Glenn (2008), “Multibeam Sonar Calibration Techniques.”** TX/RX patterns, element spacing, beam pointing and steering calibration. <https://scholars.unh.edu/ccom/610/> | **D5, D6** |
| R20 | **Lanzoni, Carlo; Weber, Thomas C. (2010), “High Resolution Calibration of a Multibeam Echo Sounder.”** Measured 3-D transmit/receive patterns and sidelobe behaviour. <https://scholars.unh.edu/ccom/789/> | **D5** |
| R21 | **University of New Brunswick Ocean Mapping Group, “Publications & Multibeam Sonar Theory class reports.”** Institutional multibeam theory and ocean-mapping reference collection. <https://www.omg.unb.ca/publications/> | **D7** |
| R22 | **Gomes de Araujo, Leonardo (2020), _Potential for Non-Conventional Use of Split-Beam Phase Data in Bottom Detection_, M.S. thesis, University of New Hampshire.** PDI and complementary time-angle detections. <https://scholars.unh.edu/thesis/1421/> | **D8** |
| R23 | **Hamel, Jonathan (2020), _Effects of Transmission Side Lobe Interference on Multibeam Echosounder Phase Ramps_, M.S. thesis, University of New Hampshire.** Phase-ramp quality/support and bottom-detection uncertainty. <https://scholars.unh.edu/thesis/1425/> | **D8** |
| R24 | **Beaudoin, Jonathan; Weber, Thomas C.; Jerram, Kevin W.; Rice, Glen; Malik, Mashkoor A.; Mayer, Larry A. (2013), “Multibeam Echosounder System Optimization for Water Column Mapping of Undersea Gas Seeps.”** Frequency-encoded multisector systems and sounding-spacing geometry. <https://scholars.unh.edu/ccom/693/> | **D9** |
| R25 | **de Moustier, Christian (2001), “Field Evaluation of Sounding Accuracy in Deep Water Multibeam Swath Bathymetry,” MTS/IEEE OCEANS.** Wide-swath sounding sensitivity to motion integration and synchronization. <https://scholars.unh.edu/ccom/218/> | **D14** |
| R26 | **Maingot, Brandon; Hughes Clarke, John E.; Calder, Brian R. (2019), “High Frequency Motion Residuals in Multibeam Data: Identification and Estimation.”** Systematic bathymetric residuals caused by integration errors in orientation, space, sound speed and time. <https://scholars.unh.edu/ccom/1683/> | **D14** |
| R27 | **Hare, R.; Godin, A.; Mayer, L. A. (1995), _Accuracy Estimation of Canadian Swath (Multibeam) and Sweep (Multitransducer) Sounding Systems_. Canadian Hydrographic Service / Ocean Mapping Group, University of New Brunswick.** Foundational swath-sounding error-budget / uncertainty treatment. <https://gge.ext.unb.ca/Pubs/TR190.pdf> | **D17** |
| R28 | **Center for Coastal and Ocean Mapping / Joint Hydrographic Center (CCOM/JHC), University of New Hampshire, _CUBE — Combined Uncertainty and Bathymetric Estimator_.** Downstream uncertainty-aware bathymetric estimation bridge. <https://www.ccom.unh.edu/research/research-areas/data-processing/cube> | **D17** |
| R29 | **Joint Committee for Guides in Metrology (JCGM), JCGM 100:2008(E), _Evaluation of measurement data — Guide to the expression of uncertainty in measurement (GUM)_.** Standard, combined and expanded uncertainty and first-order propagation. <https://doi.org/10.59161/JCGM100-2008E> | **D17** |
| R30 | **JCGM 100:2008/Amd.1:2026, _Evaluation of measurement data — Guide to the expression of uncertainty in measurement — Amendment 1: Nonlinearity in measurement models_.** Limits of first-order linear propagation. <https://doi.org/10.59161/PPDI3267> | **D17** |

## Authoritative manufacturer / operational architecture references

Manufacturer documents are retained as evidence of real controls, interfaces and architectures. They must not be generalized into universal hydrographic laws.

| ID | Reference | Used in lab(s) |
|---|---|---|
| R31 | **Kongsberg, EM 2040 MKII product/documentation portal.** Broadband operation, TX/RX architecture, modern MBES modes, multisector operation and density/dual-swath examples. <https://www.kongsberg.com/what-we-do/ocean-space/seafloor-mapping/em/EM2040-Mk2/> | **D2, D5, D7, D9, D15** |
| R32 | **Kongsberg Discovery, EM 2040 MKII current product portal.** Current High Density / Ultra High Density and dual-swath operational evidence. <https://www.kongsberg.com/discovery/seafloor-mapping/em/EM2040-Mk2/> | **D16** |
| R33 | **Kongsberg, “Sector coverage and beam spacing modes for multibeam echosounders” (2013).** Equiangular/equidistant/High Density modes and architecture-specific sounding-distribution behaviour. <https://www.kongsberg.com/contentassets/058cd4fb2f1d417dab5f444f8f5cbf9a/em-sector-coverage-beam-spacing-modes.pdf> | **D7, D8** |
| R34 | **Kongsberg, EM 2040 Instruction Manual.** Three-sector/frequency architecture, TX steering/focusing and PU/external-interface examples. <https://www.kongsberg.com/globalassets/kongsberg-maritime/km-products/product-documents/346210_em2040_instruction_manual.pdf> | **D9, D12** |
| R35 | **Kongsberg, EM 2040 MKII Installation Manual.** Vessel coordinate system, origin, waterline, sensor locations and installation angles. <https://www.kongsberg.com/globalassets/kongsberg-discovery/commerce/seafloor-mapping/em2040-mkii/472405ab_em2040mk2_installation_manual_en.pdf> | **D10** |
| R36 | **Kongsberg, EM 304 Installation Manual.** Electronically steered multibeam architecture, external position/clock/motion/sound-speed interfaces and 1PPS synchronization. <https://www.kongsberg.com/globalassets/kongsberg-maritime/km-products/product-documents/427620_em304_installation_manual_en.pdf> | **D6, D12, D13** |
| R37 | **Kongsberg, EM 2040 Slim PU installation documentation.** External synchronization, GPS 1PPS and external sensor interfaces. <https://www.kongsberg.com/contentassets/098bb8dd6793498c8deb72431583958e/391932ad_em2040_slim_pu_installation.pdf> | **D13** |
| R38 | **Kongsberg, EM multibeam output datagram format, document 160692.** Operational sounding fields, angles, travel-time/range, motion and sound-speed/ray-bending conventions. <https://www.kongsberg.com/globalassets/kongsberg-discovery/seafloor-mapping/em-multibeams/documents/160692_em_datagram_formats.pdf> | **D14** |
| R39 | **Kongsberg Discovery, “Multibeam survey planning — The key to success,” EM Technical Note.** Survey-planning factors, achievable coverage, overlap and line direction. <https://www.kongsberg.com/globalassets/kongsberg-discovery/commerce/seafloor-mapping/em2040-mkii/em-technical-note-multibeam-survey-planning-the-key-to-success.pdf> | **D15** |
| R40 | **Kongsberg, EM 2040 MKII Data Sheet.** System-specific frequency, ping-rate, swath, beam-count and spacing-mode examples. <https://www.kongsberg.com/globalassets/kongsberg/1.-what-we-do/2.-ocean-space/5.-seafloor-mapping/em-multibeams/em2040/em-2040---mkii-data-sheet.pdf> | **D16** |
| R41 | **Kongsberg, EM 304 MKII / EM 124 / EM 712 product documentation.** Architecture-specific examples of TX yaw/pitch stabilization and RX roll stabilization. <https://www.kongsberg.com/what-we-do/ocean-space/seafloor-mapping/em/em304-mkii/> ; <https://www.kongsberg.com/what-we-do/ocean-space/seafloor-mapping/em/em124/> ; <https://www.kongsberg.com/what-we-do/ocean-space/seafloor-mapping/em/em712/> | **D11** |
| R42 | **Kongsberg, MRU 5.** Roll, pitch, heave and configurable motion monitoring points / lever arms. <https://www.kongsberg.com/what-we-do/ocean-space/inertial-solutions/mru/mru-5/> | **D11** |
| R43 | **Kongsberg, Seapath 385.** Six-DOF navigation/motion outputs, multiple monitoring points and time-critical output/timestamp examples. <https://www.kongsberg.com/what-we-do/ocean-space/inertial-solutions/seapath/seapath-385/> | **D11, D13** |
| R44 | **Trimble Applanix, POS MV.** Hydrographic GNSS/INS example with time-tagged position, attitude, heave and velocity data. <https://applanix.trimble.com/en/products/hardware/applanix-pos-mv> | **D13** |

## Lab-to-reference quick index

This section is intentionally compact so an agent can find the cross-lab source set without loading every treatise.

| Lab | Consolidated references |
|---|---|
| **D1 — Acoustic Wave & Frequency** | R01, R11 |
| **D2 — Pulse & Signal Processing** | R01, R13, R14, R31 |
| **D3 — Sonar Equation & Propagation Loss** | R01, R11, R14, R15 |
| **D4 — Sound Speed & Refraction** | R01, R11, R16, R17, R18 |
| **D5 — Transducer & Array Construction** | R01, R12, R14, R19, R20, R31 |
| **D6 — Beamforming & Electronic Steering** | R01, R12, R14, R19, R36 |
| **D7 — Echosounders: SBES vs MBES** | R01, R14, R21, R31, R33 |
| **D8 — Bottom Detection** | R01, R14, R22, R23, R33 |
| **D9 — Multisector MBES** | R01, R18, R24, R31, R34 |
| **D10 — Vessel & Sensor Configuration** | R01, R04, R07, R35 |
| **D11 — Vessel Motion** | R01, R03, R05, R07, R41, R42, R43 |
| **D12 — PU & Sensor Integration** | R01, R09, R10, R34, R36 |
| **D13 — Timing, Synchronization & Latency** | R01, R05, R07, R36, R37, R43, R44 |
| **D14 — Sounding Formation** | R01, R03, R14, R25, R26, R38 |
| **D15 — Survey Planning** | R01, R03, R06, R31, R39 |
| **D16 — Survey Coverage & Acquisition Trade-offs** | R01, R03, R06, R14, R32, R40 |
| **D17 — Uncertainty / TPU** | R01, R02, R03, R08, R27, R28, R29, R30 |

## Maintenance rule

- Keep implementation-driving citations in the individual `Dxx_*.md` treatise where the scientific/pedagogical claim is made.
- Add or update this file only when a reference is added, removed, superseded or its cross-lab usage changes.
- Do not require UX/engineering agents to load this file for routine work on one lab.
- Prefer a stable institutional/DOI/document URL over search-result URLs.
- Treat manufacturer material as architecture/operational evidence, not universal scientific authority.
- If a consolidated entry and an individual lab disagree, the active lab treatise controls the implementation until the discrepancy is explicitly reconciled.
