# Scientific Beam-Chain Review 1

Date: 2026-08-31
Status: completed scientific checkpoint
Scope: element factor -> array factor -> receive steering -> one-way beam pattern -> two-way beam pattern -> Mills Cross

## Purpose

This review evaluates whether the existing HydroSIM beam/array chain is scientifically coherent, whether the implemented equations are mutually consistent, and whether the current validation and reference traceability are sufficient to treat each stage as a mature reference model.

The review does **not** introduce new beam physics. It treats the existing implementation as scientific project heritage and checks its formulation, assumptions, validation strength, and traceability gaps.

## Reviewed implementation

- `src/hydrosim/acquisition/element_factor.py`
- `src/hydrosim/acquisition/array_factor.py`
- `src/hydrosim/acquisition/beamforming.py`
- `src/hydrosim/acquisition/beam_pattern.py`
- `src/hydrosim/acquisition/two_way_pattern.py`
- `src/hydrosim/geometry/mills_cross.py`

Related documentation and tests were also reviewed.

## Overall conclusion

The present beam-chain equations are internally coherent and physically interpretable within their declared fidelity domain.

No sign inconsistency was found between HydroSIM's receive-arrival timing convention and the array-factor residual-phase convention.

The main scientific weakness is **traceability maturity**, not the current mathematical formulation. Element factor, array factor, one-way beam pattern, two-way beam pattern, and Mills-Cross geometry are implemented and tested but are not yet represented by dedicated canonical entries in the Scientific Registry.

Therefore the immediate recommendation is **registry consolidation and source tightening**, not replacement of the current models.

## 1. Rectangular element factor

### Existing model

The current element is an ideal uniformly excited rectangular aperture/piston in the local XY plane with +Z normal.

For a unit direction `u` expressed in the element/array frame,

\[
E(\mathbf u)=
\operatorname{sinc}\left(\frac{k a}{2}u_x\right)
\operatorname{sinc}\left(\frac{k b}{2}u_y\right),
\]

where

\[
k=\frac{2\pi}{\lambda},\qquad \lambda=\frac{c}{f},
\]

and HydroSIM uses the unnormalized sinc convention

\[
\operatorname{sinc}(x)=\frac{\sin x}{x}.
\]

The code preserves the signed real pressure response across aperture nulls before later complex composition.

### Scientific assessment

This is a standard far-field rectangular-aperture directivity model. The separation of longitudinal and transverse aperture dimensions is physically appropriate for the present ideal model.

The current tests provide valid analytical implementation anchors:

- unity at boresight;
- first null for an aperture dimension equal to one wavelength at endfire in that principal plane;
- `2/pi` response for a half-wavelength aperture at 90 degrees;
- distinct longitudinal/transverse responses for unequal aperture dimensions.

### Validity domain

- far field;
- planar uniformly excited rectangular element;
- narrowband/monochromatic evaluation;
- identical orientation across elements when used in the current one-way beam composition;
- no baffle-edge complications beyond the ideal aperture model;
- no mutual coupling;
- no electro-mechanical element transfer function.

### Traceability assessment

**Status: scientifically plausible and analytically tested, registry incomplete.**

A dedicated Registry entry should be created after the source locator is tightened to a recognized acoustics/array reference. Suitable recognized sources located during this review include standard rectangular-piston/directivity treatments and modern sonar-array texts; the exact canonical source and equation locator should be selected before promoting the record to `reference_model`.

## 2. Narrowband array factor

### Existing model

For source direction `u`, steering direction `u0`, and element position `r_i`, HydroSIM uses

\[
\phi_i=k(\mathbf u-\mathbf u_0)\cdot\mathbf r_i.
\]

For complex weight `w_i`,

\[
A=\sum_i w_i e^{i\phi_i},
\]

with normalized magnitude

\[
AF=\frac{|A|}{\sum_i |w_i|}.
\]

### Sign-consistency check

HydroSIM receive steering defines the far-field physical arrival offset as

\[
\Delta t_i=-\frac{\mathbf u\cdot\mathbf r_i}{c}.
\]

The compensation delay for steering toward `u0` is

\[
\tau_i=\frac{\mathbf u_0\cdot\mathbf r_i}{c}.
\]

Under the declared analytic-signal convention

\[
s(t)=e^{i2\pi f t},
\]

the combined residual phase is

\[
-2\pi f\Delta t_i-2\pi f\tau_i
=k(\mathbf u-\mathbf u_0)\cdot\mathbf r_i.
\]

Therefore the `beamforming.py` timing law and `array_factor.py` spatial-phase law are mutually consistent.

### Validation strength

The two-element tests are strong **independent analytical** anchors for the numerical summation itself:

- `d=lambda/2`, source +30 deg, broadside steering -> normalized amplitude `sqrt(2)/2`, power 0.5;
- source +30 deg, steering -30 deg -> ideal cancellation;
- `d=lambda`, broadside steering, endfire direction -> coherent grating-lobe recurrence.

These checks do not depend on the HydroSIM numerical routine to generate their expected values.

### Validity domain

- far-field plane-wave model;
- narrowband monochromatic phase;
- deterministic element positions;
- ideal prescribed complex weights;
- no mutual coupling;
- no channel calibration mismatch;
- no near-field focusing;
- no finite-bandwidth spatial response.

### Traceability assessment

**Status: mathematically strong, analytically validated, registry incomplete.**

The model is mature enough for a dedicated Scientific Registry entry once its canonical array-theory reference is added with a precise equation/section locator.

## 3. Receive steering geometry

The current steering model

\[
\Delta t_i=-\frac{\mathbf u\cdot\mathbf r_i}{c}
\]

has already been reviewed in `docs/reviews/physics_architecture_review_1.md` and is retained.

Its role must remain distinct from the array factor:

- steering geometry predicts inter-element time offsets;
- array factor evaluates coherent narrowband spatial response;
- waveform-domain beamforming and detection are separate fidelity layers.

**Status: retained existing reference geometry; no new formulation recommended.**

## 4. One-way physical beam pattern

### Existing model

HydroSIM composes element and array responses as

\[
B_{1w}(\mathbf u;\mathbf u_0)=E(\mathbf u)AF(\mathbf u;\mathbf u_0).
\]

The signed real element response multiplies the complex array field before amplitude and power are derived.

### Scientific assessment

This is a sound decomposition for the present ideal identical-element far-field array model.

An important strength is that HydroSIM does not equate array factor with physical beam pattern. The current tests explicitly demonstrate that an element-factor null can suppress a spatial grating lobe predicted by the array factor alone.

### Limitations

The model is not a calibrated transmit or receive sensitivity model and currently excludes:

- absolute gain/source level;
- element-to-element transfer-function differences;
- mutual coupling;
- broadband integration;
- near-field effects;
- propagation loss;
- bottom scattering;
- electronic noise.

### Documentation note

`docs/science/beam_pattern.md` contains an historical "next stage" statement saying that transmit x receive two-way composition is not yet implemented. That statement is stale because `two_way_pattern.py` and `docs/science/two_way_beam_pattern.md` now implement/document that stage.

This is documentation drift, not a scientific-model defect.

**Status: implemented and coherent; Registry entry missing; one explanatory document requires synchronization.**

## 5. Two-way TX x RX beam pattern

### Existing model

HydroSIM treats TX and RX apertures independently and evaluates their normalized one-way complex responses toward the same physical field direction.

The reference two-way field is

\[
B_{2w}(\mathbf u)=B_{Tx}(\mathbf u)B_{Rx}(\mathbf u),
\]

with

\[
A_{2w}=|B_{2w}|,
\qquad
P_{2w}=|B_{2w}|^2.
\]

The common physical direction is transformed independently into TX and RX array-local frames.

### Scientific assessment

The separation of TX and RX local coordinate representations is correct and important. Copying one array-local direction into another rotated aperture would be physically wrong.

The current test suite verifies:

- unity for fully matched normalized TX and RX responses;
- product behavior of independent one-way amplitudes;
- independent local-frame direction representations;
- orientation round-trip consistency;
- correct component changes for orthogonal TX/RX apertures;
- equivalence between the sensor-frame bridge and explicit manual local transforms.

Most of these tests are **implementation consistency / analytical composition** tests. They are strong for architecture and coordinate handling but are not external experimental validation of a real transducer.

### Validity domain

- far field;
- narrowband;
- common acoustic frequency;
- common sound speed for the pattern evaluation;
- normalized responses;
- fixed array installation orientation;
- no propagation/scattering/noise/detection in the pattern layer.

**Status: scientifically coherent reference composition; Registry entry missing.**

## 6. Mills-Cross configuration

### Existing model

HydroSIM correctly treats Mills Cross as a **specific transducer-installation geometry**, not as a universal definition of MBES.

The reference configuration requires strictly linear TX and RX apertures whose principal axes are orthogonal in a common sensor frame.

### External support

Recognized hydroacoustic literature supports the common Mills-Cross interpretation as orthogonal transmit and receive line arrays whose intersecting directional responses create narrow two-way beams. A particularly useful traceable source is:

- Demer, D. A., Berger, L., Bernasconi, M., et al. (2015), *Calibration of acoustic instruments*, ICES Cooperative Research Report No. 326, DOI `10.17895/ices.pub.5494`.

That report explicitly describes the common Mills-Cross hydrographic MBES arrangement using a line-array transmit fan and an orthogonal receive array forming multiple beams.

Recent peer-reviewed sonar literature also continues to describe modern systems as two uniform linear transducer arrays arranged in a Mills Cross, while distinguishing the physical transducer arrays from the beams formed by coherent interference.

### Scientific assessment

The current generic HydroSIM representation is appropriate for the didactic/reference level because it does not encode a vendor-specific head geometry.

The orthogonality constraint should remain a property of `MillsCrossConfiguration`, while generic two-way beam composition remains usable for non-Mills-Cross configurations.

**Status: scientifically supported; dedicated Registry entry recommended.**

## Scientific maturity classification

| Model | Implementation | Analytical tests | External reference traceability | Registry | Current assessment |
|---|---|---|---|---|---|
| Rectangular element factor | yes | good | needs canonical locator | no | partially consolidated |
| Narrowband array factor | yes | strong | needs canonical locator | no | partially consolidated |
| Receive steering law | yes | strong | previously reviewed | no dedicated beamforming entry | consolidated formulation |
| One-way beam pattern | yes | good | indirect/needs canonical locator | no | partially consolidated |
| Two-way TX x RX pattern | yes | good | conceptually supported | no | partially consolidated |
| Mills-Cross geometry | yes | good geometry tests | strong recognized support | no | ready for registry formalization |

## Recommendations

1. **Do not replace the current equations.** No scientific reason for replacement was found in this review.
2. Add dedicated Scientific Registry records for the existing beam-chain models before expanding beam physics.
3. Add at least one recognized canonical array/acoustics reference with precise source locators for rectangular element directivity and array factor.
4. Add the ICES CRR 326 Mills-Cross reference to `scientific_registry/references/bibliography.yaml`.
5. Synchronize the historical "not yet implemented" text in `docs/science/beam_pattern.md` with the existing two-way implementation.
6. Classify current validation honestly: analytical anchors validate equations/numerics; they do not constitute experimental transducer validation.
7. Do not introduce mutual coupling, near-field focusing, broadband beam-pattern integration, or calibrated electro-acoustic gain until a concrete fidelity requirement calls for them.

## Gate decision

The existing beam-chain implementation is scientifically suitable to retain as the HydroSIM reference foundation.

The gate for additional beam physics is therefore **registry and reference consolidation**, not mathematical redesign.
