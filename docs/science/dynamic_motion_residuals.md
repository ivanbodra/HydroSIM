# Dynamic Motion Residuals in Multibeam Bathymetry

Version: 0.1.1  
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

The primary source for the initial signature taxonomy is Hughes Clarke (2003), *Dynamic Motion Residuals in Swath Sonar Data: Ironing out the Creases*. The paper explains that the conventional patch test addresses only a subset of possible systematic integration biases and that additional biases may produce dynamic rather than static bathymetric signatures.

Hughes Clarke separates errors varying at periods in the ocean-wave spectrum — commonly called wobbles — from a separate family driven by longer-period vessel accelerations such as turns, course changes, obstacle avoidance, and speed changes.

The paper explicitly examines seven common integration problems, labelled A-G. HydroSIM preserves these labels only as bibliographic locators; its canonical identifiers describe the physical/configuration cause instead.

The Maingot (2019) work extends the problem from visual/correlation-based diagnosis toward model-based simultaneous estimation. Its publicly available abstract states that dynamic depth errors may result from offsets in orientation, space, sound speed, or time; that six common errors are simultaneously identified; and that individual sounding input-error relationships are considered over extended swath corridors. It also states that successful estimation requires significant vessel motion over a few tens of seconds and smooth or gently rolling bathymetry over the corresponding spatial extent.

Lurton (2003) is retained as a complementary reference for intrinsic acoustic time/angle measurement accuracy. HydroSIM keeps intrinsic acoustic measurement uncertainty scientifically distinct from integration-error residuals, although both may contribute to the final sounding uncertainty and error field.

Canonical bibliographic metadata is stored in `scientific_registry/references/bibliography.yaml`.

## 3. Shallow-water signature approximation and depth dependence

Hughes Clarke shows that signature classification is particularly useful when the ping transmit/receive cycle is short relative to the characteristic period of the driving vessel motion. In that condition, the dynamic error changes little during a single ping and the instantaneous across-track profile can approximately represent one sample of the angular and/or positional error state.

This is not generally true in deep water. Hughes Clarke's Figure 5 shows the same latency-driven roll residual progressing from an approximately linear swath tilt in shallow water, through a nonlinear curved profile at intermediate depth, to a ripple migrating through the swath when the receive cycle becomes long relative to the motion/error period.

Therefore HydroSIM must never implement the Hughes Clarke Type-I to Type-IV taxonomy as a fixed bathymetric deformation independent of travel time and beam reception time.

Primary source mapping: Hughes Clarke (2003), printed pp. 8-10, Figures 2-5.

## 4. Hughes Clarke signature classes

The initial HydroSIM registry preserves four characteristic manifestation classes as observational labels, not physical models.

| Signature ID | Canonical interpretation |
| --- | --- |
| `hughes_clarke_type_I` | Approximately linear across-track angular tilt in the shallow-water approximation |
| `hughes_clarke_type_II` | Approximately in-phase vertical translation of the full swath |
| `hughes_clarke_type_III` | Nonlinear roll-coupled across-track tilt/curvature, with opposite phase on the two sides |
| `hughes_clarke_type_IV` | Approximately symmetric nonlinear curvature about nadir, with outer sides responding in phase |

The exact manifestation depends on depth, receive-cycle duration, swath geometry, motion spectrum, and the physical error source.

## 5. Hughes Clarke A-G source map

Hughes Clarke's seven illustrated cases are now mapped directly to HydroSIM concepts:

| Source case | Hughes Clarke description | HydroSIM canonical model | Main shallow-water signature |
| --- | --- | --- | --- |
| A | Motion scaling problems | `integration.motion_scale_error` | Type I for roll scaling; Type II component if heave is scaled |
| B | Time delays in motion sensor output | `integration.motion_latency_error` | Type I for roll latency; possible Type II heave component |
| C | Imperfect alignment of roll/pitch axes with sonar reference frame | `integration.motion_axes_yaw_misalignment` | Type I |
| D | X relative sensor-offset error | `integration.lever_arm_x_error` | Type II |
| E | Y relative sensor-offset error | `integration.lever_arm_y_error` | Type II |
| F | Vertical motion close to or in a sound-speed gradient | `environment.near_surface_sv_gradient_motion_coupling` | Type IV |
| G | Rolling with an imperfect surface sound speed | `integration.surface_sound_speed_error` | Type III |

Primary source mapping: Hughes Clarke (2003), printed pp. 10-15, Figures 6-10.

## 6. Motion scale error — case A

Hughes Clarke describes scale-factor problems in motion time series and notes that the error magnitude scales with the magnitude of the reported angle, most noticeably roll. In the shallow-water roll-dominated case, the resulting residual across-track slope correlates with roll phase and produces a linear tilt that is zero at nadir and increases toward the outer swath.

HydroSIM may represent this mechanism as:

```text
attitude_observed = scale_factor * attitude_true
attitude_error = (scale_factor - 1) * attitude_true
```

These expressions are `derived_from_source`; they are a compact HydroSIM formalization of the source-described scaling mechanism rather than verbatim equations from the paper.

Hughes Clarke also points out that if heave is scaled, each ping can be vertically displaced by the heave difference, producing an in-phase rise and fall of all beams — a Type-II component. Therefore case A is not restricted to one signature class if all motion components share the scale problem.

Source mapping: printed pp. 10-11; Figure 3 Type I; Figures 6A and 7A.

## 7. Motion latency — case B

Hughes Clarke explicitly formulates sinusoidal roll as a function of amplitude and period and differentiates it to show that sensitivity to timing error is governed by the rate of change of orientation:

```text
R(t) = A sin(2*pi*t/T)
dR/dt = (2*pi*A/T) cos(2*pi*t/T)
```

Consequently, for small latency HydroSIM can use the first-order relation:

```text
attitude_error(t) ~= -attitude_rate(t) * latency
```

The approximation itself is `derived_from_source`; the sinusoidal motion/rate relationship and the qualitative dependency on angular rate are directly supported by Hughes Clarke.

This establishes a particularly useful diagnostic distinction:

- scale residuals approximately follow motion **amplitude**;
- latency residuals approximately follow motion **rate**;
- at equal amplitude, shorter-period motion produces a larger latency signature.

For an ideal single-frequency sinusoid, scale- and latency-driven residual components are approximately in quadrature. Real vessel motion is multi-frequency and correlated across roll, pitch, and heave, so this is a didactic special case rather than a universal diagnostic rule.

Source mapping: printed pp. 11-12; Figure 2; Figure 3 Type I; Figures 6B and 7B.

## 8. Motion-axis yaw misalignment — case C

This error represents rotation about the vertical axis between the motion sensor's roll/pitch axes and the vessel coordinate system. Hughes Clarke explicitly gives the cross-coupling equations:

```text
sin(observed_roll)  = cos(E) sin(true_roll)  + sin(E) sin(true_pitch)
sin(observed_pitch) = cos(E) sin(true_pitch) - sin(E) sin(true_roll)
```

where `E` is the yaw misalignment angle.

The equations show two effects: attenuation of the same-axis signal by `cos(E)` and leakage from the other axis through `sin(E)`. For small `E`, the most sensitive diagnostic term is the cross-talk; approximately,

```text
roll_error  ~=  E * true_pitch
pitch_error ~= -E * true_roll
```

with radians implied in the first-order approximation.

This error must not be conflated with vessel heading error, sonar-to-body yaw alignment, or a conventional heading patch-test bias.

Source mapping: printed pp. 12-13; Figure 8; Figures 6C and 7C.

## 9. Lever-arm errors and induced heave — cases D and E

Hughes Clarke explicitly gives the induced-heave error associated with lever-arm errors `dX`, `dY`, `dZ` and vessel roll/pitch `r`, `p`:

```text
IH_error = -dX sin(p)
           + dY sin(r) cos(p)
           + dZ [1 - cos(r) cos(p)]
```

This equation is a `direct_source` relationship and must later be reconciled explicitly with HydroSIM's Forward-Starboard-Down frame and sign conventions before implementation.

The source identifies the dominant dynamic couplings:

- X lever-arm error -> pitch-correlated induced heave;
- Y lever-arm error -> predominantly roll-correlated induced heave;
- Z lever-arm contribution is generally much smaller for modest roll/pitch.

When the receive cycle is short relative to the motion period, this error is nearly common to every beam in the swath and appears as an in-phase rise/fall of the complete swath: Type II.

Source mapping: printed pp. 13-14; induced-heave equation; Figure 3 Type II; Figures 6D-E and 7D-E.

## 10. Near-surface sound-speed gradient and vertical motion — case F

Hughes Clarke gives the erroneous beam-steering relation for a sound-speed mismatch as:

```text
theta_error = asin[(V_error / V_correct) sin(theta_correct)]
```

where the paper's `theta_error` denotes the erroneous steered angle rather than a simple angle difference. The notation must therefore be normalized carefully when implemented in HydroSIM.

When the transducer oscillates vertically through a strong near-surface sound-speed gradient, the sonar-relative water-column structure changes dynamically with vertical transducer motion. Hughes Clarke describes a refraction artefact symmetric about nadir: both sides curl upward or downward together, while near-nadir beams show little movement. This is the Type-IV signature.

HydroSIM may abstract the environmental coupling as:

```text
surface_sound_speed_at_array = c(z_transducer(t))
```

which is classified as `derived_from_source`.

Source mapping: printed pp. 14-15; Figure 9; Figure 3 Type IV; Figures 6F and 7F.

## 11. Rolling with imperfect surface sound speed — case G

Hughes Clarke considers the more common case where surface sound speed is simply wrong and the receive array is no longer level because of roll or mounting angle. The paper gives a rolled-array steering relationship of the form:

```text
theta_error = asin[(V_error / V_correct) sin(theta_correct - phi)]
```

and shows that the resulting Snell constant is not preserved.

The resulting angular error depends on roll magnitude and sign and on desired steering angle. Because steering error grows with obliquity, the final swath tilts nonlinearly from side to side. The two sides are out of phase, producing Hughes Clarke Type III.

This case is easily confused with roll scaling because both correlate with roll. Hughes Clarke proposes comparing inner-swath and outer-swath slopes: they should be similar for simple roll scaling but differ when the profile is curved by steering/refraction error.

Source mapping: printed p. 15; Figure 10; Figure 3 Type III; Figures 6G and 7G.

## 12. Water-column SSP mismatch

An incorrect sound-speed profile used for ray tracing can produce nonlinear across-track depth errors, commonly increasing toward outer beams. Hughes Clarke explicitly lists adequate knowledge of the water-column sound-speed profile as an assumption of basic alignment and distinguishes conventional refraction bias from the surface-steering mechanisms discussed in cases F and G.

No single universal linear formula is appropriate because the error depends on the full propagation geometry and sound-speed structure. `propagation.ssp_refraction_error` therefore remains `not_yet_formulated` in this specification. A future propagation model must supply governing ray equations, assumptions, and validation cases.

## 13. Diagnostic observables from Hughes Clarke

The source's diagnostic approach motivates several Derived observables that HydroSIM can expose without treating them as physical causes:

```text
high_pass_filtered_full_swath_across_track_slope
high_pass_filtered_inner_swath_across_track_slope
high_pass_filtered_port_slope
high_pass_filtered_starboard_slope
high_pass_filtered_swath_averaged_depth
roll
roll_rate
pitch
pitch_rate
vertical_motion_at_sonar
```

Hughes Clarke distinguishes two broad observable families: outer swath edges rising/falling (Types I, III, IV) and the complete swath rising/falling (Type II). Cross-plots between filtered bathymetric observables and driving motion quantities are then used to diagnose likely causes.

A key identifiability warning from the paper is preserved: different physical causes can produce similar signatures. In particular, Type III surface-sound-speed/roll effects may resemble Type-I roll scaling, while heave scaling can be difficult to separate from X/Y lever-arm induced-heave effects.

## 14. Observability and Maingot/RISC

HydroSIM distinguishes **error existence** from **error observability**.

Maingot (2019) explicitly reports that successful estimation requires significant vessel motion over periods of a few tens of seconds and smooth or gently rolling bathymetry along the equivalent spatial extent. The method considers each sounding's input-error relationship over extended sections of a swath corridor, addresses multiple errors simultaneously, better accounts for along-track sounding distribution, and is not restricted to shallow-water geometry.

Accordingly, scientific model metadata may include:

```yaml
observability:
  required_excitation: []
  preferred_geometry: []
  poor_conditions: []
  confounded_by: []
```

A hidden Truth parameter may be non-zero but effectively unobservable in a particular motion state or acquisition geometry. HydroSIM must not manufacture a visible wobble merely because the hidden error is non-zero.

## 15. RISC parameterization status

The accessible Maingot (2019) abstract explicitly states that six common motion-driven errors are simultaneously identified and that the underlying offsets occur in orientation, space, sound speed, or time.

For HydroSIM v0.1.1, the working six-parameter reconstruction remains:

```text
motion scale
motion latency
motion-axis yaw misalignment
X lever-arm error
Y lever-arm error
surface sound-speed error
```

This enumeration remains `strongly_supported_reconstruction`, not `direct_source`, because the accessible abstract does not enumerate the six parameters. It must be promoted only after verification against the full thesis equations, a primary-source parameter table, or an equivalent authoritative Maingot/RISC publication.

The fact that Hughes Clarke's seven A-G cases map naturally onto these six candidate fitted parameters plus the external/environmental near-surface-gradient case strengthens the reconstruction but does not by itself prove the exact RISC vector.

## 16. Evidence and traceability policy

Each scientific relationship identifies an evidence level:

- `direct_source`: explicitly supported by the cited source;
- `derived_from_source`: mathematical consequence or approximation derived by HydroSIM from a source-supported relationship;
- `strongly_supported_reconstruction`: synthesis strongly supported by the literature but awaiting exact primary-source verification;
- `hypothesis`: retained for investigation and not suitable as a canonical implementation claim.

Where possible, `source_mapping` identifies the specific source case, printed page, equation, figure, table, or other locator.

The desired traceability chain is:

```text
Reference
  -> scientific claim/model
  -> equation or algorithm
  -> implementation
  -> validation case
```

and must also be navigable in reverse from implementation to scientific source.

## 17. Relationship to uncertainty architecture

The following concepts remain distinct:

```text
sensitivity
!= a priori uncertainty
!= simulation-truth error
!= observed residual signature
```

A Jacobian may describe the sensitivity of a sounding to an input parameter. Sensor/model covariance propagated through that sensitivity describes a priori uncertainty. A hidden difference between Truth and Configured state produces actual simulation-truth error. Vessel motion and survey geometry can transform that error into an observable dynamic signature.

The wobble model therefore complements, but does not replace, the HydroSIM a priori uncertainty framework.

## 18. Implementation rule

No production scientific implementation should expose a generic parameter such as:

```text
wobble_amplitude
```

as a substitute for a physical/configuration cause.

Didactic visualization may measure or display apparent wobble amplitude as a **Derived** quantity, but simulated bathymetry must arise from the configured/hidden physical model and acquisition geometry.

## 19. Next verification tasks

The following items remain intentionally open after v0.1.1:

1. verify the exact six-parameter RISC/Maingot vector against full primary-source equations;
2. reconcile the Hughes Clarke induced-heave equation with HydroSIM's exact frame/sign/rotation conventions and create analytical tests;
3. normalize Hughes Clarke's sound-speed steering notation into explicit `desired_angle`, `realized_angle`, and `angle_error` quantities;
4. formulate the surface-sound-speed steering mechanism within the HydroSIM `TxSector` / `RxBeam` architecture;
5. formulate full water-column SSP/refraction effects using a documented ray model;
6. connect each error model to sounding-level Jacobians for the a priori uncertainty architecture;
7. create literature-derived and analytical golden-value tests before implementing a complete dynamic-residual estimator.
