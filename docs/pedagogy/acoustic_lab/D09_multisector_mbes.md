# D9 — Multisector MBES

**Decision:** `KEEP + REFINE + ADD EXPERIENCE`  
**Current:** `web/pedagogical-explorer/src/MultisectorLab.tsx`  
**Historical implementation alias:** `PED-D10` / `D10Multisector*`; pedagogical numbering here is authoritative.

## Purpose
Teach why a modern MBES may divide one swath into multiple transmit sectors and why sector identity matters downstream. A sector is a transmit event/configuration with its own angular support, steering, timing and potentially frequency/pulse characteristics; it is not an RX beam.

## Dominant discovery

```text
one swath / ping
  -> one or more distinct TX sectors
  -> sector-specific angle + TX epoch + signal configuration
  -> RX beams/detections must reference the correct TX sector
  -> sector design changes coverage / sounding distribution / interference behavior
```

## Inputs
Primary: TX sector count/layout, beginning with one-sector baseline then a three-sector example; each sector centre/angular support; TX timing/delay/transmit group; per-sector frequency where supported by the selected architecture.

Secondary/advanced: pulse duration per sector; relative/source-level setting only with exact Scientific-Core semantics; along-track sector steering/yaw-pitch stabilization as bridge to D11; focusing only with validated model; surface sound speed only as steering-input bridge from D4.

## Outputs / visual response
**A. TX sector geometry** — physical TX reference, distinct sector supports, centres, gaps/overlaps; faint RX fan only to reinforce `TX sectors ≠ RX beams`.

**B. Transmit timeline** — one ping with TX epochs, pulse start/end, simultaneous groups and staggered sectors; selected sector TX epoch available to downstream TWTT reasoning.

**C. Sector identity/configuration** — frequency/wavelength where configured, pulse duration, source-level/relative-power only with exact semantics, sector identifier preserved for later detection association.

Recommended: selected RX detection mapped to parent TX sector when core supports it; small coverage strip; one-sector vs multisector comparison.

## Interaction
1. Single TX sector baseline.
2. Split same swath into three sectors while keeping receive fan conceptually unchanged.
3. Move sector centres/widths to create gap then overlap.
4. Put sectors at same epoch; if architecture supports frequency coding, assign different frequencies without inventing unsupported crosstalk physics.
5. Stagger one sector; geometry may remain, timeline changes. Show correct sector epoch requirement for TWTT.
6. Vary frequency per sector only within registered architecture; reuse D1/D3 intuition.
7. Vary pulse duration per sector with only supported consequences.
8. Advanced: sector-specific steering/stabilization/focusing only with validated core response.

## Operational intuition / trade-offs
Multiple sectors allow differentiated steering/signal treatment across wide swath but add timing/identity complexity. Frequency-coded simultaneous sectors are architecture-specific and have frequency-dependent behavior. Staggered timing separates TX events but requires correct epoch association. More sectors are not more RX beams or more soundings.

## Guardrails
A TX sector is not an RX beam. Multisector does not universally mean three sectors, different frequencies or simultaneous transmission. Do not infer acoustic power from UI opacity. Different frequencies do not inherently improve coverage or resolution. Sector delay is a timing reference; D13/D14 own general synchronization/latency and sounding formation. Surface sound speed and water-column SVP remain distinct. Motion stabilization belongs primarily to D11.

## Dependencies / forward reuse
Consumes D1 frequency/wavelength, D2 pulse, D3 acoustic trade-offs, D4 surface-vs-water-column sound speed distinction, D6 steering/RX beams, D7 TX×RX swath geometry, D8 detection/TWTT. Passes installation/orientation context to D10, sector stabilization to D11, multiple TX epochs to D13, correct TX epoch/identity to D14, sector-dependent coverage to D15/D16.

## Implementation delta
Begin with one-sector baseline, then reveal three-sector configuration. Make `TX SECTORS ≠ RX BEAMS` dominant. Make gaps/overlaps and timeline/sector-specific epoch equally prominent. Reduce sound speed and relative power from primary controls. Never use opacity as physical power proxy. Add one-sector ↔ multisector fixed-scale comparison. Any sector-to-RX association must live in Scientific Core/API.

## References
- IHO S-5A Ed. 2.0.0 H2.4a/H2.4b.
- Beaudoin, Hughes Clarke & Bartlett (2004), multi-sector surface sound-speed application.
- Beaudoin, Weber et al. (2013), MBES optimization for water-column mapping.
- Kongsberg EM 2040 Instruction Manual and EM 2040 MkII current documentation as architecture-specific evidence.
