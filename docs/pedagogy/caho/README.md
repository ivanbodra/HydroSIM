# CAHO curricular alignment

Status: initial repository baseline; course-source access blocked; no CAHO lesson alignment verified.
Inspection date: 2026-10-16.
Repository baseline: `eed7bedc19f654b9adc13275a249a57576720e5d` (`main`).

## Purpose and ownership

`caho-pedagogy` connects HydroSIM activities to the actual lessons and learning objectives of the Curso de Aperfeiçoamento de Hidrografia para Oficiais (CAHO). The Product Owner is final authority. Course materials are curricular authority; HydroSIM science contracts remain scientific authority.

The role owns curricular analysis, prerequisite sequencing, learning objectives, activity structure, misconceptions, scaffolding, assessment intent and pedagogical acceptance criteria. It does not own scientific models, software/API implementation, production UX, final visual design, routine QA or integration.

This directory indexes and aligns existing specifications. It does not replace the canonical Acoustic Lab or Patch Test documents or authorize implementation.

## Reading order

- [Existing coverage](existing_coverage.md): repository evidence and identifiers, with CAHO links still pending.
- [Mapping roadmap](mapping_roadmap.md): the next source-analysis cycle and provisional reuse sequence.

For an active laboratory, read its existing modular specification rather than importing the whole course into one working context.

## Course source and access evidence

| Source | Observed result on 2026-10-16 | Reading status |
|---|---|---|
| Product Owner course entry point: <https://bit.ly/CIAARA_CAHO> | HTTP redirect to a personal OneDrive shared folder | Link resolution only |
| Redirect target: <https://1drv.ms/f/c/4403e8e210681632/IgDupVBOgdQ3RbudVK96ZlyEAcqE2t2MX0O8i1eJutLkv4Q?e=HTI5Zc> | Redirect to `onedrive.live.com`; direct retrieval ended in a proxy HTTP 502; web retrieval reported the source inaccessible | Folder contents unread |

The folder listing, course year, subjects, lesson order, instructors, presentations, exercises, page counts and revision dates have **not** been inspected. No inference about access permissions, authentication requirements, site availability or the course's contents follows from this retrieval failure.

No CAHO-specific mapping directory was found in the inspected repository tree. No CAHO issue/PR or open handoff addressed to `caho-pedagogy` was returned by the startup searches. These are inspection results, not proof that no relevant teaching content exists elsewhere.

## Initial curricular inventory

| Inventory level | Verified entries | Meaning |
|---|---:|---|
| Supplied course entry point | 1 | Root link only |
| Listed folders / subjects | 0 | Not inspected; not an empty-course claim |
| Lesson materials read | 0 | No course-content claims can be made |
| Source-backed lesson-to-lab links | 0 | All links await course evidence |
| Confirmed curricular gaps | 0 | Unknown until lesson mapping |

The HydroSIM topic inventory in `existing_coverage.md` must not be relabelled as a CAHO syllabus.

## Evidence vocabulary

Each future mapping must distinguish:

- **Course-explicit**: exact material and page/slide/section state the content or objective.
- **Pedagogical interpretation**: a proposed objective, prerequisite, misconception or activity inferred from identified teaching material.
- **Scientific inference**: a scientific interpretation that needs the applicable contract or Scientific Lead decision.
- **Proposed HydroSIM extension**: useful content beyond the verified lesson or approved product boundary.
- **Unresolved question**: missing or contradictory evidence.

A scientific reference or IHO competence anchor is not evidence that CAHO teaches a particular lesson.

## Source and mapping records

For each material, record: stable local source ID; exact title; original folder/path or item link; author/instructor when stated; course cohort/date/revision when stated; file type; page/slide count; relevant pages/slides; reading status; next unread section. Retain source filenames and Portuguese course terminology. Do not copy the complete teaching archive into the repository.

Reading states: `unlisted`, `listed_unread`, `partially_read`, `read`, `mapped`, `needs_recheck`. Record what was actually read; a title or folder name does not count as lesson analysis.

For each lesson-to-lab link, record: source ID and locator; subject/lesson/section; explicit course content; separately identified interpretation; intended learning outcome; prerequisites; existing HydroSIM semantic name and ID; treatment level; before/during/after-class use; assessment evidence; coverage or gap; unresolved dependencies. A link is verified only after its cited source section is read.

## Treatment and specification rule

Use the smallest useful treatment: no HydroSIM treatment, static visual, guided animation, interactive demonstration, full laboratory, or integrated scenario. Prefer existing activities when they already answer the lesson's learning question.

A new laboratory specification must include: stable ID/title; CAHO subject/lesson/section/source; target learners and prerequisites; learning problem; objectives; central phenomenon; pedagogical question; observe/manipulate/compare/explain/apply sequence; meaningful inputs; visible outputs; reference/comparison states; guidance; misconceptions; assessment evidence; exact scientific/course sources; visual rationale; model boundaries; implementation dependencies; concrete learner-facing acceptance criteria.

Do not issue an implementation handoff until curricular evidence, science, visual requirements and required capability are sufficiently resolved. Scope extensions require Product Owner sequencing rather than implicit expansion from the course's breadth.

## Operational routing

GitHub handoffs follow `docs/coordination/agent_handoffs.md` and #544 where Patch Test is involved.

- Scientific ambiguity, units, frames and model limits: `scientific-lead`.
- New visual concept: `concept-designer`.
- Missing Core/API capability: `software-engineering`.
- Approved production learner experience: `interface-ux`.
- Integrated verification: `qa-scientific-validation`.
- Integration, sequencing and ownership conflicts: `technical-lead`.

An open handoff must request a bounded executable action. Course-access failure is not a reason to open speculative development handoffs.
