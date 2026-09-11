# D4 — Sound Speed & Refraction

Status: **Mapped**

**Decision:** `KEEP + REFINE + ADD EXPERIENCE`  
**Current:** `web/pedagogical-explorer/src/RefractionLab.tsx`

## Purpose
Build intuition for why the water-column sound-speed profile matters to sounding position. Connect profile/gradient to ray bending, then connect a wrong/stale processing profile to systematic spatial error in reconstructed soundings.

## Dominant discovery

```text
sound-speed gradient -> refraction -> acoustic path changes
wrong processing SVP -> wrong reconstructed ray -> sounding endpoint error
same SVP mismatch -> error generally grows with obliquity / outer-swath geometry
```

## Inputs
Primary: launch/beam angle from vertical; Truth/reference sound-speed profile; Processing profile, matched by default then deliberately mismatched. Secondary: layer/gradient parameters, target depth, presets. Surface/transducer sound speed is a separate experiment because its steering role differs from water-column SVP.

## Outputs / visual response
- explicit `c(z)` plot;
- Truth/reference and Processing/reconstructed rays on same fixed geometry;
- visible bottom/target;
- reference and reconstructed endpoints;
- error vector `Δx`, `Δz`;
- supporting travel time/path values;
- recommended error-vs-angle curve or small swath fan from the same Scientific Core.

## Interaction
Start constant; vary angle. Introduce a gradient; vary it while geometry stays fixed. Then compare identical Truth/Processing profiles, mismatch Processing only, and increase angle to expose endpoint-error evolution. Reset to matched profiles.

## Operational intuition / trade-offs
Representative SVP supports faithful reconstruction; stale/sparse sampling can generate coherent refraction errors, often more evident toward outer swath. Wider angular coverage gains area but generally increases sensitivity to propagation/profile error. Surface sound speed does not replace the water-column profile.

Desired learner message: **the water column bends the acoustic path; using the wrong sound-speed profile reconstructs the correct travel-time observation along the wrong path, moving the sounding endpoint.**

## Scientific guardrails
Use the registered ray tracer and sign/angle convention. Never let Processing SVP modify Truth propagation. Do not state a universal `Δx/Δz` sign without specified geometry/model. Layered profiles are pedagogical simplifications. Do not expand into physical oceanography or formal uncertainty propagation.

## Dependencies / forward reuse
Consumes D1 sound-speed/wavelength intuition. Passes propagation-path and reconstruction sensitivity to D7/D8 geometry, D14 sounding formation and D17 uncertainty.

## Implementation delta
Retain scenario progression and endpoint-error comparison. Add `c(z)` and bottom reference; preserve fixed geometry and explicit Truth/Processing semantics; add optional error-vs-angle view; reduce prominence of ray-parameter/per-layer diagnostics.

## Recognized references
- **IHO S-5A Ed. 2.0.0 (Aug 2026), H2.1e** — sound-speed profiles, refraction and hydrographic application: <https://portal.iho.int/share/api/files/AAAAAAABALI/Standard%20S-5A%20Ed.2.0.0/S-5A_Ed2.0.0_05May26.pdf>
- **MIT OpenCourseWare, 2.682 Acoustical Oceanography (James Lynch, Spring 2012)** — first-principles acoustic propagation/refraction background: <https://ocw.mit.edu/courses/2-682-acoustical-oceanography-spring-2012/>
- **Beaudoin, Jonathan (2010), “Real-time Monitoring of Uncertainty due to Refraction in Multibeam Echo Sounding”**: <https://scholars.unh.edu/ccom/1050/>
- **Beaudoin, Jonathan; Calder, Brian R.; Hiebert, J.; Imahori, Gretchen (2009), “Estimation of Sounding Uncertainty from Measurements of Water Mass Variability”**: <https://scholars.unh.edu/ccom/481/>
- **Beaudoin, J. D.; Hughes Clarke, J. E.; Bartlett, J. E. (2004), “Application of surface sound speed measurements in post-processing for multi-sector multibeam echosounders”** — useful for preserving the distinction between surface steering sound speed and water-column refraction: <https://scholars.unh.edu/ccom/1335/>
