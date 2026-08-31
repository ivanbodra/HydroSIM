# Propagation Explorer

Version: 0.1.0

## Purpose

The first Propagation Explorer lesson turns the existing layered-SVP sounding experiment into a guided interactive experience. It introduces no new propagation equation. The lesson reuses HydroSIM's existing piecewise-constant layered ray tracer and Truth-versus-processing sounding reconstruction.

The teaching question is:

> What happens when the physical water column is unchanged, but the lower-layer sound speed used during processing is wrong?

## Controlled scenario

The first lesson intentionally fixes most of the system:

- stationary monostatic principal-plane geometry;
- flat seabed at 60 m;
- two piecewise-constant sound-speed layers;
- interface at 20 m;
- Truth upper layer: 1500 m/s;
- Truth lower layer: 1480 m/s;
- ideal transducer sound-speed measurement;
- zero array tilt;
- signed fan from -60 to +60 degrees;
- nine configured beams.

The learner changes only the lower-layer sound-speed bias used in the Processing SVP.

## Causal chain

```text
fixed Truth SVP
      -> physical refraction
      -> Truth ray paths
      -> bottom intersections and TWTT

processing lower-layer bias
      -> Processing SVP mismatch
      -> reconstruction with the same observation
      -> reconstructed sounding displacement
      -> beamwise vertical/across-track error
```

The Truth profile, Truth ray paths, Truth bottom, and observations remain unchanged while the processing bias is varied. This makes the distinction between simulated reality and processing configuration visible.

## Visualization

The lesson uses the existing layered-SVP renderer with three panels:

1. **Sound-speed profiles** — Truth and Processing SVPs.
2. **Truth rays and reconstructed swath** — physical ray paths, Truth intersections, and reconstructed soundings.
3. **Beamwise sounding error** — calculated-minus-Truth vertical and across-track errors versus configured beam angle.

The renderer supports in-place redraw through `draw_layered_svp_explorer_snapshot(...)`, so the desktop application reuses the same axes and canvas on each interaction.

## Scientific boundary

This first lesson is a controlled reference experiment, not a general water-column model. It does not yet represent:

- continuous-gradient sound-speed profiles;
- frequency-dependent absorption;
- surface sound-speed sensor error;
- vessel motion;
- array installation error;
- uncertainty propagation;
- bottom scattering or target strength.

The underlying layered model conserves the horizontal ray parameter across horizontal interfaces according to the scientific documentation already maintained in HydroSIM.

## UX rule

Only one active scientific control is exposed in the first lesson: Processing lower-layer sound-speed bias. This is deliberate. The learner should first see that changing a processing assumption can move a reconstructed sounding even though the physical Truth state did not change.
