# Physics / Architecture Review 1

Date: 2026-08-28
Status: completed checkpoint
Scope: dynamic acquisition from Tx event through receive-element coherent summation

## Purpose

This review checks whether the current HydroSIM acquisition chain is physically interpretable, internally consistent, and suitable as a foundation for later element-factor, array-factor, beam-pattern, SSP/refraction, sector, and Mills-Cross models.

Reviewed chain:

```text
Truth vessel motion
    ↓
Tx epoch and sensor pose
    ↓
ideal geometric pencil ray
    ↓
Truth terrain interaction point
    ↓
beam-specific TWTT with moving receiver
    ↓
receive-array pose
    ↓
element-specific arrival epochs
    ↓
ideal receive steering delays
    ↓
narrowband element phase
    ↓
equal-weight coherent sum
```

## Overall conclusion

The current chain is suitable as a reference foundation, with one important interpretation correction: the existing `BeamRay` propagation is a **geometric pencil-ray proxy**, not yet a complete physical MBES transmit-beam model. In particular, it must not be described as if a finite TX beam alone uniquely defined the final sounding in a Mills-Cross system.

The current bottom-return calculation is physically coherent when interpreted as a **point-scattering reference model** in a homogeneous medium. The terrain intersection fixes the Truth interaction point; received energy is then allowed to propagate from that point to the displaced receiver. This is not a specular reflection model and does not assume that the received path retraces the outbound path.

The receive steering and narrowband phase signs are internally consistent under the declared complex-signal convention. Independent closed-form tests were added so that this conclusion no longer rests only on one implementation reproducing another implementation.

## Finding 1 — `BeamRay` semantics were too strong

Previous wording referred to the propagated ray as a transmitted beam. That is acceptable for an intentionally ideal pencil-beam sonar, but it is too strong for the planned MBES architecture.

A typical hydrographic Mills-Cross system forms different transmit and receive apertures; the final two-way response is governed by their combination. NOAA metadata for systems such as the EM302 explicitly describes separate linear transmit and receive arrays in a Mills-Cross configuration, with beam focusing on both transmission and reception.

Reference:
- NOAA/NCEI EM302 metadata: https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=gov.noaa.ncei%3ANA138_EM302%3Bview%3Diso

Decision:
- retain `BeamRay` for the current reference geometry;
- interpret it as an ideal **pencil-ray proxy** in the current propagation function;
- do not infer physical TX/RX aperture behavior from `BeamDefinition.role` at this layer;
- later introduce explicit finite TX and RX beam patterns and their two-way intersection/response.

## Finding 2 — bottom return must be described as scattering, not mirror retracing

The current outbound ray intersects the terrain and fixes one Truth bottom point. The receiver moves while sound is in flight, so the inbound distance is solved to the receive sensor at its later position:

\[
t_{Rx}=t_{Tx}+\frac{R_{out}+R_{in}(t_{Rx})}{c}.
\]

This is not equivalent to saying that the echo necessarily retraces the outbound ray. For an oblique incidence on a flat ideal specular reflector, the mirror-reflected ray would generally not return to a displaced monostatic receiver. Hydrographic seafloor echoes are instead treated through scattering/backscatter and finite footprint physics at more advanced fidelity.

The present reference model therefore adopts an explicit point-scatterer interpretation: once the Truth interaction point is established, a return path from that point to the receiver is geometrically possible. Scattering strength and angular dependence are not yet modeled.

Reference context:
- NOAA Ocean Exploration multibeam overview describes transmitted sound returning as an echo from the seafloor: https://oceanexplorer.noaa.gov/technology/sonar-multibeam/
- NOAA Office of Coast Survey similarly describes MBES as transmitting sound energy and analyzing echoes returned from the seafloor or objects: https://nauticalcharts.noaa.gov/learn/hydrographic-survey-equipment.html

Decision:
- document the current model as point scattering;
- reserve specular/diffuse scattering laws, footprint integration, target strength, and backscatter amplitude for later models.

## Finding 3 — moving receiver fixed-point state needed tighter consistency

The previous fixed-point implementation detected convergence using an updated epoch but returned the vessel/element state sampled at the immediately preceding estimate. The difference was bounded by the very small convergence tolerance, but the stored time and stored state were not mathematically the same epoch.

Decision:
- return the state evaluated at the same epoch stored in `return_time` / `arrival_time`;
- record the remaining implicit-equation error explicitly as `fixed_point_residual_seconds`.

This makes numerical approximation visible rather than silently hiding it.

## Finding 4 — receive steering sign is consistent

HydroSIM defines a unit vector \(\mathbf{u}\) from the array centre toward the source point. For element position \(\mathbf{r}_i\), the ideal far-field arrival offset is

\[
\Delta t_i=-\frac{\mathbf{u}\cdot\mathbf{r}_i}{c}.
\]

An element displaced toward the source therefore receives earlier, giving a negative time offset. The delay needed to align the element to the centre reference is

\[
\tau_i=-\Delta t_i.
\]

This is consistent with the declared Port-positive across-track convention and the physical element ordering used by `TransducerArray`.

Manufacturer documentation also confirms the general physical processing sequence of phase-adjusting/weighting and summing element signals for bathymetric beamforming.

Reference:
- RESON SeaBat 8101 Operator's Manual, NOAA-hosted copy: https://data.ngdc.noaa.gov/instruments/remote-sensing/active/profilers-sounders/acoustic-sounders/reson_seabat_8101_OpMan_302.pdf

## Finding 5 — narrowband phase convention is consistent

HydroSIM declares

\[
s(t)=e^{i2\pi f t}.
\]

For an arrival offset \(\Delta t_i\), evaluating the received component at the common centre epoch gives

\[
\phi_i^{Truth}=-2\pi f\Delta t_i.
\]

Applying a positive delay \(\tau_i\) to a signal produces

\[
\phi_i^{steer}=-2\pi f\tau_i.
\]

Because matched steering uses \(\tau_i=-\Delta t_i\), the two terms cancel. The resulting coherent sum reaches unity after normalization.

Decision:
- keep the current sign convention;
- keep the complex-signal convention explicitly documented wherever phase formulas are introduced.

## Finding 6 — tests needed independent analytical anchors

Several previous tests were internally useful but partly circular: synthetic Truth arrivals were generated using the same ideal steering law later evaluated by the beamformer.

Independent analytical checks were added for a two-element array with

\[
d=\lambda/2.
\]

For a source at +30° and steering at 0°, the inter-element residual phase is

\[
\Delta\phi=\pi\sin 30^\circ=\frac{\pi}{2},
\]

so the normalized magnitude must be

\[
\left|\cos\frac{\Delta\phi}{2}\right|=\frac{\sqrt{2}}{2},
\]

and normalized power must be 0.5.

For a +30° source steered to -30°, the residual inter-element phase becomes \(\pi\), so two equal elements cancel ideally.

These tests are independent closed-form anchors for the sign and coherent-sum implementation.

## Finding 7 — Truth / processing separation remains sound

The current layering remains appropriate:

```text
Truth motion and terrain
        ↓
Truth physical interaction and element arrivals
        ↓
processing hypothesis: steering
        ↓
signal-domain phase and coherent summation
```

The steering hypothesis does not modify the Truth interaction point or re-intersect erroneous geometry with Truth terrain. This preserves the same fundamental invariant already used by HydroSIM for Truth versus Configured sounding reconstruction.

## Known approximations retained intentionally

The review does not promote the current model beyond its intended fidelity. The following remain intentionally absent:

- finite TX footprint;
- explicit TX/RX two-way beam-pattern intersection;
- element directivity;
- shading/weights other than unity;
- spherical-wave near-field steering corrections;
- layered SSP/refraction;
- scattering strength and incidence-angle dependence;
- waveform envelope and bandwidth;
- matched filtering;
- amplitude/phase channel mismatch;
- electronic noise;
- detection algorithms;
- multipath.

## Gate for the next stage

The codebase is ready to proceed to physical **element factor** and then **array factor**, provided the following invariant is retained:

\[
\text{two-way sonar response} \neq \text{one geometric ray}.
\]

The planned progression is:

```text
single-element geometry
    ↓
element directivity / element factor
    ↓
array factor from element positions and complex weights
    ↓
receive beam pattern
    ↓
TX × RX two-way response
    ↓
Mills-Cross and sector geometry
```

Ray tracing and bottom interaction should remain separate from beam-pattern physics so that propagation fidelity and array fidelity can be varied independently.

## Related scientific architecture

Beaudoin, Hughes Clarke & Bartlett (2004) remains a relevant source for multi-sector MBES geometry, timing, steering, and surface sound-speed considerations:

https://journals.lib.unb.ca/index.php/ihr/article/view/20675
