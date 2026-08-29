# Sound speed at the transducer: scientific basis and model boundaries

Status: reference documentation for the HydroSIM acquisition model.

## Purpose

HydroSIM separates three quantities that must not be conflated:

1. **true local sound speed at the transducer** — part of the synthetic Truth model;
2. **measured sound speed at the transducer** — the observation produced by the local sound-speed sensor; and
3. **sound speed used by the sonar** — processing state selected from a sensor measurement, manual entry, profile interpolation, or a held previous value.

A real sonar does not know HydroSIM's Truth value. Truth is available only to the forward simulator and to diagnostics comparing simulated physical reality with processing results.

## Array steering and local sound speed

For a plane-wave steering component in a principal plane, the imposed tangential slowness is

\[
p_t = \frac{\sin\theta}{c}.
\]

For transmission, a delay law constructed for configured angle \(\theta_{cfg}\) using the sonar value \(c_{used}\) imposes

\[
p_t = \frac{\sin\theta_{cfg}}{c_{used}}.
\]

In the synthetic physical medium, whose local sound speed is \(c_{true}\), the resulting physical launch angle therefore satisfies

\[
\sin\theta_{phys}=c_{true}p_t
=\frac{c_{true}}{c_{used}}\sin\theta_{cfg}.
\]

Receive processing is the inverse interpretation problem. A physical arrival direction in the true medium produces spatial delay/slowness at the array; a beamformer using \(c_{used}\) maps that observed spatial delay to an estimated angle. HydroSIM therefore keeps TX physical steering and RX angle estimation as distinct operations rather than applying one generic post-detection angle correction.

The full 3-D reference model conserves both tangential components of slowness.

## Water-column profile and ray tracing

Sound speed at the transducer and the sound-speed profile have related but distinct roles. The local scalar at the array affects electronic beam steering/angle interpretation. The sound-speed field through the water column controls ray bending together with travel time and the initial ray state.

HydroSIM processing carries tangential slowness from the sonar angular observation into the configured processing profile. If the profile sound speed immediately below the ray-tracing start boundary is \(c_p\), then

\[
u_{x,p}=c_p p_x,\qquad u_{y,p}=c_p p_y,
\]

with the downward normal component obtained from unit-vector closure. The layered ray tracer then conserves the Snell ray parameter through horizontal layers.

No average sound speed is substituted for a layered profile in the layered reconstruction path.

## Explicit zero-thickness start boundary

HydroSIM now represents the transducer-depth value as an explicit `SoundSpeedProfileBoundary`, separate from the finite-thickness `LayeredSoundSpeedProfile`.

For detected direction \(\mathbf u_d\) at a boundary sound speed \(c_b\), the ray parameter is established from

\[
p_x=\frac{u_{x,d}}{c_b},\qquad
p_y=\frac{u_{y,d}}{c_b}.
\]

The first finite-thickness layer does not inherit \(c_b\). Instead, if that layer has sound speed \(c_1\), the direction just inside the layer follows

\[
u_{x,1}=c_1p_x,\qquad
u_{y,1}=c_1p_y.
\]

Thus a sensor value measured at the array face can establish the ray parameter without being numerically spread through an arbitrary depth interval. The layered propagation solver accepts this boundary explicitly for both depth-driven and travel-time-driven tracing.

This representation is a HydroSIM numerical/modeling choice motivated by the physical distinction between an array-face value and a water-column profile sample. It is not a claim that all manufacturers implement their internal ray tracing with an identical data structure.

## Narrow cancellation case

A perturbation of the transducer sound-speed measurement can cancel in a deliberately narrow HydroSIM reference case: stationary, monostatic, reciprocal propagation; aligned flat array; no roll/tilt; identical true and processing finite-thickness water-column profiles; and the same measured value used consistently for TX steering, RX angle mapping, and the zero-thickness processing boundary.

This is a **reference-model closure property**, not a general statement that sound-speed-at-transducer errors cancel in multibeam sounding solutions.

Kongsberg documentation for flat, horizontally mounted EM 120 transducers states that accuracy can be almost independent of variations in sound speed at transducer depth when roll and pitch are not excessive, and also states that sensor measurements are used in beam-pointing and ray-bending calculations. This supports the physical plausibility of a limited cancellation mechanism, but not a universal cancellation rule.

Beaudoin, Hughes Clarke, and Bartlett specifically analyze imperfect surface sound-speed information in multi-sector multibeam systems and identify operational complications including changing sector timing/boundaries and association of receive beams with transmit sectors. HydroSIM will therefore treat sector geometry and steering explicitly before generalizing the reference result.

## Controlled error-isolation matrix

HydroSIM provides a four-run reference matrix to separate two error classes without presupposing their signatures:

| Case | Transducer sensor | Finite-thickness processing profile | Purpose |
| --- | --- | --- | --- |
| Reference | ideal | correct | numerical/scientific closure baseline |
| Transducer only | biased | correct | isolates array-face / zero-thickness-boundary perturbation |
| Profile only | ideal | perturbed | isolates water-column profile error |
| Combined | biased | perturbed | exposes interaction between both perturbations |

The matrix intentionally reports the resulting sounding error rather than encoding an assumption that each perturbation must produce a non-zero error. In the current narrow aligned reciprocal reference, the transducer-only case is expected to close, while a finite-thickness profile perturbation produces a controlled sounding error.

## Boundary value versus profile

Some Kongsberg systems/documentation describe the transducer sound-speed sensor value as being used both for beam steering and as the first value in the active sound-speed profile. That product behavior must not be confused with HydroSIM's internal numerical representation.

The current HydroSIM `LayeredSoundSpeedProfile` consists of finite-thickness constant-c layers. Replacing an entire first layer with a biased point sensor observation would incorrectly spread a local measurement perturbation through the layer thickness. The explicit zero-thickness boundary prevents that conflation while still allowing a product/workflow to use the measured transducer value as the ray-tracing start value.

## Source-to-model traceability

| HydroSIM statement/model choice | Primary or authoritative support | HydroSIM interpretation |
| --- | --- | --- |
| Local sound speed at the array affects beam steering/beam pointing | Kongsberg EM documentation; Nistad et al. (IHR) | Model `c_used` explicitly in TX/RX array processing. |
| Water-column sound-speed structure affects ray bending | Kongsberg EM documentation; Nistad et al. (IHR) | Keep profile/ray tracing separate from the local sensor observation. |
| Tangential slowness / Snell ray parameter is the invariant across horizontal sound-speed interfaces | standard geometrical-acoustics/Snell formulation; Nistad et al. (IHR) | Carry slowness, not the raw numerical beam angle, from array processing into layered propagation. |
| Multi-sector correction requires sector-specific information | Beaudoin, Hughes Clarke & Bartlett (2004) | Do not generalize a single aligned principal-plane closure to multi-sector MBES. |
| Limited cancellation can occur for flat/horizontal arrays | Kongsberg EM 120 Operator Manual | Preserve as a narrow reference diagnostic only. |
| Sensor value may be used as first profile value in some Kongsberg processing | Kongsberg EM 1002 Operator Manual | Represent the value as an explicit zero-thickness boundary instead of overwriting a finite-thickness layer. |

## References

### Peer-reviewed / hydrographic literature

Beaudoin, J. D., Hughes Clarke, J. E., & Bartlett, J. E. (2004). *Application of Surface Sound Speed Measurements in Post-processing for Multi-Sector Multibeam Echosounders*. International Hydrographic Review, 5(3), 17–32. https://journals.lib.unb.ca/index.php/ihr/article/view/20675

Nistad, J.-G., et al. *Improved Techniques to Resolve the Water Column Sound Speed Structure for Multibeam Ray Tracing*. International Hydrographic Review. https://ihr.iho.int/articles/improved-techniques-to-resolve-the-water-column-sound-speed-structure-for-multibeam-ray-tracing/

### Manufacturer documentation

Kongsberg Maritime. *EM 120 Operator Manual*, document 850-164112. Relevant discussion: sound speed at transducer depth, flat/horizontally mounted transducers, beam pointing, ray bending, and real-time sound-speed measurement. https://www.kongsberg.com/globalassets/kongsberg-maritime/km-products/product-documents/164112-em120-operator-manual.pdf

Kongsberg. *EM Series Multibeam Echo Sounders — Instruction Manual*, document 850-160692. Relevant discussion: application of sound speed at transducer depth and ray bending to beam data. Manufacturer documentation should be preferred over third-party manual mirrors when available.

Kongsberg. *EM 1002 Operator Manual*, document 850-160977. Relevant discussion: sound-speed profile, sound speed at transducer, use of a sensor close to the transducer face, and use of the sensor value in beam steering and as the first profile value. A manufacturer-hosted copy should be used when available; third-party mirrors are secondary access copies only.

## Documentation policy

Scientific equations or non-obvious physical assumptions introduced into this subsystem should be accompanied by:

- a citation to primary literature, standards, or authoritative manufacturer documentation;
- an explicit statement of whether the source supports the physical principle, a product-specific behavior, or HydroSIM's own modeling choice;
- assumptions and domain of validity;
- a test that exercises a limiting/closure case when feasible; and
- separation of scientific-model assumptions from numerical approximations.

When sources disagree or describe different generations/products, HydroSIM must retain the distinction rather than silently harmonizing them.
