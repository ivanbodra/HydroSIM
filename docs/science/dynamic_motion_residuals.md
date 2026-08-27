# Dynamic Motion Residuals in Multibeam Bathymetry

Version: 0.1.0  
Language: English (canonical)  
Status: Scientific working specification

## 1. Purpose

This document defines the initial HydroSIM scientific interpretation of dynamic multibeam integration residuals commonly described as **wobbles**.

HydroSIM does **not** treat `wobble` as a physical error source. A wobble is an observable spatial/temporal bathymetric signature produced by one or more underlying errors interacting with vessel motion, sonar geometry, timing, and/or the acoustic environment.

The canonical causal chain is:

```text
Error source
  -> input / integration error
  -> georeferencing or measurement effect
  -> sounding truth error
  -> spatial / temporal signature
  -> observed wobble
```

This distinction is normative because it allows the simulator to generate the signature from physical/configuration causes rather than imposing an arbitrary bathymetric ripple.

## 2. Scientific basis

The primary source for the initial signature taxonomy is Hughes Clarke (2003), *Dynamic Motion Residuals in Swath Sonar Data: Ironing out the Creases*. The paper emphasizes that conventional patch-test procedures examine only a subset of possible systematic integration biases and that additional biases may produce dynamic rather than static bathymetric signatures.

Hughes Clarke separates dynamic errors associated with periods in the ocean-wave spectrum — commonly called wobbles — from longer-period signatures associated with vessel accelerations such as turns, course changes, obstacle avoidance, and speed changes.

The Maingot (2019) work extends the problem from visual/correlation-based diagnosis toward model-based simultaneous estimation. Its publicly available abstract states that dynamic depth errors may result from offsets in orientation, space, sound speed, or time; that six common errors are simultaneously identified; and that individual sounding input-error relationships are considered over extended swath corridors. It also states that successful estimation requires significant vessel motion over a few tens of seconds and smooth or gently rolling bathymetry over the corresponding spatial extent.

Lurton (2003) is retained as a complementary reference for intrinsic acoustic time/angle measurement accuracy. HydroSIM keeps intrinsic acoustic measurement uncertainty scientifically distinct from integration-error residuals, although both may contribute to the final sounding uncertainty and error field.

Canonical bibliographic metadata is stored in `scientific_registry/references/bibliography.yaml`.

## 3. Shallow-water signature approximation

Hughes Clarke shows that signature classification is particularly useful when the ping transmit/receive cycle is short relative to the characteristic period of the driving vessel motion. Under this condition, the dynamic error changes little during a single ping and the instantaneous across-track profile can approximately represent one sample of the angular and/or positional error state.

As water depth increases and the reception cycle becomes comparable to the motion/error period, different beams within the same ping are affected at different times. A simple across-track slope then becomes a progressively poorer representation of one instantaneous error state.

Therefore HydroSIM must never assume that the shallow-water wobble taxonomy remains geometrically exact at arbitrary depth.

## 4. Signature classes

The initial HydroSIM registry preserves the four characteristic manifestation classes described by Hughes Clarke as observational labels, not physical models.

| Signature ID | Canonical interpretation |
| --- | --- |
| `hughes_clarke_type_I` | Approximately linear across-track tilt in the shallow-water approximation |
| `hughes_clarke_type_II` | Approximately in-phase vertical translation of the full swath |
| `hughes_clarke_type_III` | Nonlinear roll-coupled across-track tilt/curvature |
| `hughes_clarke_type_IV` | Approximately symmetric nonlinear across-track curvature |

The exact manifestation depends on depth, receive-cycle duration, swath geometry, motion spectrum, and the error source. These labels must therefore not be implemented as direct deformation generators.

## 5. Initial cause-to-signature matrix

| Canonical error source | Cause domain | Principal driver | Expected across-track signature | Along-track manifestation | Signature class | Estimation role |
| --- | --- | --- | --- | --- | --- | --- |
| `integration.motion_scale_error` | orientation | roll / pitch amplitude | approximately linear tilt; small near nadir and increasing outward | follows driving motion cycle | Type I | estimated parameter |
| `integration.motion_latency_error` | timing | angular rate | approximately linear tilt in shallow water | periodic ribbing related to derivative/phase of motion | Type I | estimated parameter |
| `integration.motion_axes_yaw_misalignment` | orientation | roll-pitch cross-coupling | approximately linear motion-correlated tilt | follows coupled motion component | Type I | estimated parameter |
| `integration.lever_arm_x_error` | spatial integration | pitch | near-uniform full-swath vertical translation | primarily pitch-correlated | Type II | estimated parameter |
| `integration.lever_arm_y_error` | spatial integration | roll | near-uniform full-swath vertical translation | primarily roll-correlated | Type II | estimated parameter |
| `integration.surface_sound_speed_error` | surface sound speed | beam angle + roll | nonlinear roll-coupled tilt/curvature | roll-modulated | Type III | estimated parameter |
| `environment.near_surface_sv_gradient_motion_coupling` | surface sound speed | vertical motion + near-surface gradient | approximately symmetric outer-swath curvature | follows vertical motion | Type IV | confounding/external effect |
| `propagation.ssp_refraction_error` | water column | SSP mismatch + beam geometry | generally nonlinear; commonly stronger outward | depends on water-column variability | variable | confounding/external effect |

The machine-readable version is `scientific_registry/models/integration/dynamic_motion_residuals.yaml`.

## 6. Motion scale error

A scale mismatch means that the reported attitude amplitude differs systematically from the physical attitude amplitude. A HydroSIM representation may use

```text
attitude_observed = scale_factor * attitude_true
```

and therefore

```text
attitude_error = (scale_factor - 1) * attitude_true
```

The second relationship is a direct mathematical consequence of the first and is classified in the registry as `derived_from_source`, not as a verbatim published equation.

In the shallow-water roll-dominated case, Hughes Clarke describes the primary bathymetric manifestation as a residual across-track slope that correlates with roll phase and grows toward the outer swath. Scaling depends on the magnitude of the motion, not its period.

## 7. Motion latency

A timing offset causes the integration process to use a motion state corresponding to the wrong physical epoch. HydroSIM can express the exact conceptual relationship as

```text
attitude_error(t) = attitude_true(t - latency) - attitude_true(t)
```

For sufficiently small latency, first-order expansion gives

```text
attitude_error(t) ~= -attitude_rate(t) * latency
```

This approximation is classified as `derived_from_source`.

It provides an important didactic distinction:

- motion scale residuals approximately follow **attitude amplitude**;
- small-latency residuals approximately follow **attitude rate**.

For an ideal sinusoidal attitude signal, the scale-driven and latency-driven components are approximately in quadrature. In real vessel motion, multiple frequencies and correlated roll/pitch/heave prevent this from being a universally clean separation.

## 8. Motion-axis yaw misalignment

This error represents a rotation about the vertical axis between the motion sensor's roll/pitch axes and the vessel coordinate system, producing cross-talk between roll and pitch.

It must not be conflated with:

- vessel heading/yaw measurement error;
- sonar-to-body yaw alignment;
- heading patch-test bias.

HydroSIM therefore uses the explicit identifier `integration.motion_axes_yaw_misalignment`.

## 9. Lever-arm errors and induced heave

Incorrect horizontal separation between the motion reference and sonar reference can convert angular vessel motion into an erroneous vertical correction.

The principal shallow-water diagnostic relationships are:

- fore-aft (`X`) lever-arm error -> strongest coupling with pitch;
- transverse (`Y`) lever-arm error -> strongest coupling with roll.

The resulting signature may appear as a near-uniform rise/fall of the entire swath rather than an across-track angular tilt. This is the principal distinction between Type-II-like induced-heave signatures and Type-I angular signatures.

The implementation must derive this effect from rigid-body geometry. It must not create an artificial full-swath vertical offset waveform directly.

## 10. Surface sound speed error

Electronic beam steering depends on the sound speed used by the sonar. An incorrect surface sound speed therefore changes the realized beam-steering geometry.

When coupled with roll, Hughes Clarke describes a nonlinear across-track signature distinct from the approximately linear motion-scale signature. The curvature and differing behavior between inner and outer swath provide diagnostic information.

This is scientifically important because two different causes may share the same principal driver (`roll`) while producing different across-track shapes.

HydroSIM must therefore keep separate concepts for:

```text
cause
principal driver
signature class
observable diagnostic feature
```

## 11. Near-surface sound-speed gradient and vertical motion

If the transducer moves vertically through a near-surface sound-speed gradient, the sound speed physically present at the array varies with transducer depth:

```text
surface_sound_speed_at_array = c(z_transducer(t))
```

This equation is a HydroSIM abstraction of the source-supported physical mechanism and is classified as `derived_from_source`.

The expected signature is approximately symmetric across the swath, with little effect near nadir and larger effects toward the outer beams. This is an important example of an error signature that emerges from **coupling between environmental state and platform motion** rather than from a single sensor parameter.

## 12. Water-column SSP mismatch

An incorrect sound-speed profile used for ray tracing can produce nonlinear across-track depth errors, commonly increasing toward outer beams. Unlike the simpler surface sound-speed steering effect, no single universal linear formula is appropriate because the error depends on the full propagation geometry and sound-speed structure.

For this reason `propagation.ssp_refraction_error` is registered in this v0.1 specification as `not_yet_formulated`. A future propagation model must supply the governing ray equations, assumptions, and validation cases.

## 13. Observability

HydroSIM distinguishes **error existence** from **error observability**.

A hidden Truth parameter may be non-zero while the acquisition conditions provide insufficient excitation to estimate it reliably. Maingot (2019) explicitly reports that successful estimation requires significant vessel motion over periods of a few tens of seconds and smooth or gently rolling bathymetry along the equivalent spatial extent.

Accordingly, model metadata may include:

```yaml
observability:
  required_excitation: []
  preferred_geometry: []
  poor_conditions: []
  confounded_by: []
```

This is particularly important for Module 2 calibration exercises. HydroSIM should not manufacture an obvious signature merely because an instructor configured a non-zero hidden error.

## 14. RISC parameterization status

The accessible Maingot (2019) abstract explicitly states that six common motion-driven errors are simultaneously identified and that the underlying offsets occur in orientation, space, sound speed, or time.

For HydroSIM v0.1, the working six-parameter reconstruction is:

```text
motion scale
motion latency
motion-axis yaw misalignment
X lever-arm error
Y lever-arm error
surface sound-speed error
```

This enumeration is currently marked `strongly_supported_reconstruction`, not `direct_source`, because the publicly accessible abstract does not enumerate the six parameters. It must be promoted to `direct_source` only after verification against the full thesis equations, a primary-source parameter table, or an equivalent authoritative Maingot/RISC publication.

This provenance distinction is intentional and normative.

## 15. Evidence and traceability policy

Each scientific relationship should identify an evidence level:

- `direct_source`: explicitly supported by a cited source;
- `derived_from_source`: mathematical consequence or approximation derived by HydroSIM from a source-supported relationship;
- `strongly_supported_reconstruction`: synthesis strongly supported by the literature but awaiting exact primary-source verification;
- `hypothesis`: retained for investigation and not suitable as a canonical implementation claim.

Where possible, `source_mapping` should identify the specific section, equation, figure, page, table, or other locator in the primary source.

The desired traceability chain is:

```text
Reference
  -> scientific claim/model
  -> equation or algorithm
  -> implementation
  -> validation case
```

and must also be navigable in reverse from implementation to scientific source.

## 16. Relationship to uncertainty architecture

The following concepts remain distinct:

```text
sensitivity
!= a priori uncertainty
!= simulation-truth error
!= observed residual signature
```

A Jacobian may describe the sensitivity of a sounding to an input parameter. Sensor/model covariance propagated through that sensitivity describes a priori uncertainty. A hidden difference between Truth and Configured state produces actual simulation-truth error. Vessel motion and survey geometry can transform that error into an observable dynamic signature.

The wobble model therefore complements, but does not replace, the HydroSIM a priori uncertainty framework.

## 17. Implementation rule

No production scientific implementation should expose a generic parameter such as:

```text
wobble_amplitude
```

as a substitute for a physical/configuration cause.

Didactic visualization may measure or display apparent wobble amplitude as a **Derived** quantity, but the simulated bathymetry must arise from the configured/hidden physical model and the acquisition geometry.

## 18. Next verification tasks

The following items remain intentionally open after v0.1:

1. verify the exact six-parameter RISC/Maingot vector against full primary-source equations;
2. map the Hughes Clarke mechanisms to exact page/equation/figure locators where available;
3. formalize rigid-body lever-arm induced-heave equations under HydroSIM frame/sign conventions;
4. formulate surface-sound-speed beam-steering equations under the HydroSIM `TxSector` / `RxBeam` model;
5. connect each error model to sounding-level Jacobians for the a priori uncertainty architecture;
6. create literature-derived and analytical golden-value tests before implementing the complete wobble estimator.
