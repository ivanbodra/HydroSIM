# CAHO mapping roadmap

Status: provisional analysis/reuse backlog; **course-based laboratory priorities not yet established**.
Date: 2026-10-16.

## Immediate work and exit conditions

| Order | Work | Evidence required to finish | Dependency |
|---|---|---|---|
| 1 | Obtain readable CAHO folder listing and identify course cohort/revision | Actual folder/file names and source links; explicit record of incomplete visibility | Course-source access |
| 2 | Inventory subjects and lesson materials | One traceable source entry per observed material, with reading state | Step 1 |
| 3 | Read the syllabus/lesson sequence and a bounded first subject | Page/slide-level notes distinguishing stated content from interpretation | Step 2 |
| 4 | Map existing HydroSIM coverage to those lessons | Source-backed objective, prerequisite, lab semantic name, timing within class and assessment evidence | Step 3 |
| 5 | Rank reuse/refinement and genuine gaps | Rationale against the ten priority criteria below, including expected classroom value and cost | Step 4 |
| 6 | Specify the highest-value unblocked activity | Required specification fields from README; existing contracts reused; remaining dependencies routed precisely | Step 5 |

Do not mark this first curricular cycle complete until steps 1–5 have evidence. The repository inventory is a checkpoint, not completion of course absorption.

## Provisional reuse order for source analysis

This is an efficient order for examining potential matches once course access works. It does **not** assign priorities to unseen CAHO lessons or authorize implementation.

| Reuse group | Existing HydroSIM capital | Why inspect it | Appropriate initial treatment |
|---|---|---|---|
| Essential classroom support candidates | Waves/pulses; refraction; array/beamforming; sensor frames/motion/timing | Strong visual cause-and-effect relationships; existing modular specifications and production routes | Short interactive demonstration, expanded only when interpretation requires it |
| High-value complementary candidates | Detection; sounding formation; planning/coverage; uncertainty | Supports decisions and interpretation across several acquisition concepts | Guided full activity with prediction, comparison and explanation |
| Integrative candidates | P1–P5 calibration sequence; acquisition planning trade-offs | Reuses earlier concepts in an operational task | Integrated scenario after prerequisites |
| Advanced/deferred candidates | P6 forward-model residuals; richer acquisition/export | P6 has bounded authorization and an open UX correction; acquisition delivery/compatibility needs verification | Optional advanced demonstration or deferred experience |

The first actual subject to map should follow the observed CAHO materials and learning need. Do not force the course into the order above.

## Prioritization after source reading

For each source-backed opportunity, record a short rationale for:

1. Relevance to the CAHO learning objective.
2. Difficulty of visualizing the relationship.
3. Operational importance.
4. Likely misconceptions and their consequences.
5. Added value over the actual slide, diagram or exercise already supplied.
6. Reuse of existing scientific capability.
7. Feasibility and development cost.
8. Prerequisite/dependency burden.
9. Suitability for direct classroom use.
10. Value for later study/review.

No numerical ranking is assigned without the course evidence or knowledge of the classroom difficulty. Instructor reports of misconceptions must be distinguished from pedagogical hypotheses.

## Decisions and dependencies at this checkpoint

| Item | Disposition | Next action / owner |
|---|---|---|
| Course content unavailable | Blocks curricular reconstruction and exact classroom priorities | Restore a permitted reading path, then caho-pedagogy inventories and reads sources |
| Existing HydroSIM breadth | Reuse before creating new labs | caho-pedagogy checks each candidate against actual lesson objectives |
| Conflicting document/file numbering | Preserve evidence and use semantic crosswalk | technical-lead reconciles governance where needed; this work does not renumber existing artifacts |
| Old completion/gate wording | Not reliable current operational state | technical-lead resolves only the concrete inconsistency; current handoffs/heads govern work |
| P6 residual plot defect | Already routed by QA #605 | interface-ux corrects; QA validates exact replacement head |
| P6 estimator | Outside current authorized release | No estimator handoff from this roadmap |
| CAHO topics outside current HydroSIM scope | No verified gap yet | Read the lesson, evaluate smaller treatment, then submit any extension proposal to Product Owner |

## Next report to Product Owner

Report separately: material listed/read; verified subjects/lessons; source-backed existing coverage; ranked visual opportunities; gaps; blockers; next bounded reading/specification task. Never report the number of HydroSIM routes as a percentage of CAHO coverage.
