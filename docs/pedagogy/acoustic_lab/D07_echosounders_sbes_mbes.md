# D7 — Echosounders: SBES vs MBES

**Decision:** `KEEP + REFINE + ADD EXPERIENCE`  
**Current:** `web/pedagogical-explorer/src/EchosounderLab.tsx`

## Purpose
Turn D5/D6 into actual MBES observation geometry. The learner must understand that a multibeam fan is not a set of identical rays: a transmitted pulse insonifies a region, the receiver forms many look directions from one physical aperture, and each TX×RX combination has its own two-way directional response and projected seafloor footprint.

## Dominant discovery

```text
TX pulse / TX directional pattern -> insonified sector
same RX array -> many simultaneous steered receive directions
TX response × RX response -> one two-way directional sampling cell per RX direction
many TX×RX cells -> MBES fan
beam angle across fan -> different slant range + incidence + projected footprint
```

## Inputs
Primary: system SBES/MBES; depth/sonar-to-bottom separation; TX along/across beamwidths or registered TX pattern; RX beamwidth and number of formed RX directions; angular sector/steering limit; beam-spacing mode.

Secondary/advanced: pulse duration when footprint model includes pulse-limited extent; bottom slope/incidence; frequency only through a linked transducer model.

## Outputs / visual response
Required synchronized views:

**A. Water-column / array** — physical TX/RX apertures and vessel axes; one TX pulse/directional envelope; multiple RX look directions from the same RX aperture; selected direction highlighted.

**B. Selected directional response** — TX one-way response; selected RX one-way response; Scientific-Core two-way TX×RX response using explicit amplitude/power convention.

**C. Seafloor** — per beam: beam centre/steering angle, slant range, incidence, along/across footprint dimensions or polygon/ellipse, detection location distinct from footprint; top-down footprint field. Nadir/intermediate/outer beams must be comparable on the same physical scale.

## Interaction
1. SBES finite footprint: one beam samples an area, not a mathematical point.
2. MBES: one TX event + multiple virtual RX directions from D6.
3. Select nadir beam: TX -> RX -> two-way response -> footprint.
4. Select more oblique beams without changing TX; show slant range/incidence/footprint changes.
5. Whole fan + footprint field: observation geometries differ across swath.
6. Increase sector at fixed depth/beam count.
7. Increase depth on fixed/shared axes.
8. Compare equiangular vs equidistant spacing.
9. Increase beam count at fixed sector: denser centres do not automatically narrow physical response.
10. Advanced: pulse duration/beamwidth and beam-limited vs pulse-limited footprint contributions.

## Operational intuition / trade-offs
More RX beams increase simultaneous directional sampling; wider sectors increase coverage but outer-beam geometric cost; greater depth increases projected footprint and spacing; more formed beams increase density but not independent acoustic resolution; equidistant spacing changes angle distribution rather than physical beamwidth.

## Guardrails
Do not model TX×RX as hard-edged polygon multiplication. Teach mechanism, not one vendor geometry as universal. Multisector sequencing belongs to D9. Keep beam centre, footprint and accepted bottom detection distinct; D8 owns detection. Footprint depends on beam shapes, range, incidence, pulse/time-gate effects where applicable and bottom geometry. Outer beams do not intrinsically have worse range resolution. Beam count/sounding density is not acoustic resolution.

## Dependencies / forward reuse
Consumes D2 pulse, D3 range/SNR, D5 TX/RX directivity, D6 beamforming/steering. Passes per-beam echo/footprint to D8; sector architecture to D9; installation to D10; stabilization to D11; range+angle to D14; footprint/spacing/swath to D15/D16; across-track geometry to D17.

## Implementation delta
Add one TX response + many RX directions; explicit D6 shared-array bridge; selected `TX one-way -> RX one-way -> two-way response -> seafloor footprint`; independent along/across footprint geometry; fixed-scale nadir/intermediate/outer comparison; synchronized top-down and cross-section views; per-beam variation primary.

## References
- IHO S-5A Ed. 2.0.0 H2.
- Hughes Clarke (2017), *Multibeam Echosounders*.
- UNB Ocean Mapping Group publications.
- Kongsberg EM beam-spacing note.
- Kongsberg EM 710 Mk2 and EM 2040 MkII documentation.
