# CAHO curricular alignment

Status: first source-backed, partial curricular map; progressive absorption continues.
Inspection date: 2026-10-16.
HydroSIM implementation baseline: `eed7bedc19f654b9adc13275a249a57576720e5d`.

## Purpose and authority

`caho-pedagogy` connects HydroSIM to the actual lessons and objectives of the Curso de Aperfeiçoamento de Hidrografia para Oficiais (CAHO). The Product Owner is final authority. CAHO materials define curricular intent; HydroSIM scientific contracts define valid simulation behavior.

This role owns lesson alignment, objectives, prerequisites, learning activities, misconceptions, scaffolding and pedagogical acceptance. Science, software/API, production UX, final visual design, independent QA and integration retain their specialist owners.

This directory supplements the existing modular specifications. It does not replace them, certify runtime readiness or authorize new product scope.

## Read by purpose

- [Curricular map](curriculum_map.md): source-backed links, title-only candidates, prerequisites and treatment choices.
- [Source inventory](source_inventory.csv): 166 observed entries from 27 folder listings; exact relative paths, reading states and hashes for the five obtained PDFs.
- [Reading log](reading_log.md): exact pages and visual sampling examined; what remains unread.
- [Existing HydroSIM coverage](existing_coverage.md): semantic identifier crosswalk and inspected implementation evidence.
- [Prioritized roadmap](mapping_roadmap.md): classroom value, dependencies and next bounded work.
- [First classroom activity](activities/CAHO-HYD05-REFRACTION.md): a guided use of existing PED-D4, not a new scientific model or duplicated laboratory.

## Source access and extent

Course entry point: <https://bit.ly/CIAARA_CAHO>.
Direct shared-folder link supplied by the Product Owner: <https://1drv.ms/f/c/4403e8e210681632/IgDupVBOgdQ3RbudVK96ZlyEAcqE2t2MX0O8i1eJutLkv4Q>.

Direct HTTP/web retrieval failed earlier. Browser access to the supplied direct link succeeded without sign-in on 2026-10-16, and the course PDFs used here were obtained from the viewer. **The earlier course-access blocker is resolved.**

The root contains `Acústica Submarina`, `Hidrografia`, `Material de Apoio`, the 285-page July-2026 hydrography handout and a QR image. This establishes the extent of this shared collection, not the complete official CAHO syllabus. Materials span different years; filenames labelled CAHO24 must not silently become a 2026 syllabus.

The initial inventory lists all direct children of the root, acoustic subject and its PDS/TRACEO folders, all 19 displayed hydrography lesson folders, and the two supporting-reference folders. Deeper software, examples and calibration-data branches remain explicitly unexpanded. Counts are observed entries, not distinct lessons, fully read sources or curricular completion.

## Evidence labels and reading discipline

- **Course-explicit**: identified source page states a topic, objective or activity.
- **Pedagogical interpretation**: proposed learning question, prerequisite, misconception, assessment or treatment inferred from specified evidence.
- **Scientific inference**: scientific interpretation requiring the applicable contract or Scientific Lead.
- **Proposed extension**: beyond verified course content or current product/model scope.
- **Unresolved question**: incomplete or contradictory evidence.

Source states are `listed_unread`, `partially_read`, `read`, `mapped` and `needs_recheck`; folders additionally record whether their children were listed. Reading the text of a presentation with sampled figure checks is recorded as partial review, not full audiovisual analysis. Page locators are **1-based PDF pages**, not printed slide numbers.

A source-backed topic link is not evidence that a complete lesson has been mapped, implemented or assessed. No CAHO coverage percentage is claimed.

## Required records and activity specification

Maintain source identity/path, revision/cohort when stated, reading extent and next unread section. Preserve original Portuguese filenames/terminology; canonical analysis remains English. Do not commit teaching-source binaries, complete extracted texts, screenshots of teaching slides, installers or datasets.

Every new activity/laboratory specification must identify: stable ID/title; CAHO connection; target learners/prerequisites; learning problem; objectives; central phenomenon; pedagogical question; learning sequence; meaningful inputs; visible outputs; comparison states; guidance; misconceptions; assessment evidence; exact scientific/course sources; visual rationale; model boundaries; implementation dependencies; acceptance criteria.

Use the smallest effective treatment: no HydroSIM treatment, static visual, guided animation, interactive demonstration, full laboratory or integrated scenario. Reuse existing activities before adding simulations. Do not invent controls that lack meaningful, scientifically supported consequences.

## Routing

Use canonical GitHub handoffs: science → `scientific-lead`; visual concept → `concept-designer`; missing Core/API → `software-engineering`; approved learner implementation → `interface-ux`; integrated verification → `qa-scientific-validation`; sequencing/integration → `technical-lead`.

An open handoff must request executable bounded work. A reading backlog or a speculative scope extension is not an implementation order.
