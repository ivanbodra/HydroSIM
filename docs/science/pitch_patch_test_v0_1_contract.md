# Pitch Patch Test v0.1 Scientific Contract

Status: implementation-ready scientific/sign contract for the minimum P2 Pitch Calibration experience.

## Purpose

The P2 experience teaches the standard hydrographic pitch patch-test principle:

> A residual pitch alignment error shifts reconstructed bottom geometry in the along-track direction; reciprocal passes over the same sloping seabed expose that error as a mismatch between the two profiles.

The learner estimates the pitch correction by bringing the reciprocal profiles into coincidence. Hidden simulation Truth is used only to validate the experiment; it is not the learner-facing estimator.

## Authoritative survey geometry

The v0.1 deterministic setup follows established NOAA multibeam calibration practice:

- one coincident survey line run twice in reciprocal directions;
- same vessel speed in both directions;
- a smooth along-track slope of approximately 10–20 degrees;
- slope crossed perpendicular to its depth contours;
- sufficient common coverage so both profiles represent the same physical seabed;
- navigation latency assumed already zero/corrected before estimating pitch;
- lever-arm, roll-alignment and yaw-alignment errors set to zero for this isolated lesson;
- no stochastic sensor noise in the reference case.

The minimum synthetic reference geometry is:

- local navigation frame: HydroSIM `N` (North-East-Down);
- first pass heading: 0 degrees;
- reciprocal pass heading: 180 degrees;
- vessel Truth roll/pitch: 0 degrees for the platform motion state;
- terrain: deterministic plane whose maximum gradient is along `X_N`;
- terrain slope: 15 degrees for the default lesson;
- reference depth: 50 m at the line origin;
- sounding observable: nadir or near-nadir beam only for the minimum P2 slice.

Using one near-nadir beam deliberately isolates the along-track pitch signature from the broader MBES swath geometry. A later patch-test experience may use full-swath matching without changing the sign contract below.

## HydroSIM pitch sign

HydroSIM already defines positive pitch as **bow up** in the Forward-Starboard-Down body frame.

Define:

- `theta_true`: physical transducer pitch alignment relative to the vessel/body frame;
- `theta_cfg`: pitch alignment currently configured in processing;
- `delta_theta_true = theta_true - theta_cfg`: correction that would make the configured alignment equal the physical alignment.

The P2 estimated correction is defined as

\[
\widehat{\Delta\theta}=\arg\min_{\Delta\theta} J(\Delta\theta),
\]

and the corrected/estimated alignment is

\[
\theta_{est}=\theta_{cfg}+\widehat{\Delta\theta}.
\]

Therefore the canonical sign rule is:

> A **positive estimated correction** means increase the configured HydroSIM pitch alignment in the positive (bow-up) direction.

In the deterministic closure case,

\[
\widehat{\Delta\theta}=\theta_{true}-\theta_{cfg}.
\]

Example: if `theta_true = +1.0 deg` and `theta_cfg = 0.0 deg`, the correct P2 estimate is `+1.0 deg`, and the corrected configuration becomes `+1.0 deg`.

This convention reports the **correction to apply to the configured alignment**, not the negative residual error. UI labels must preserve that wording.

## Learner-facing observable

For each reciprocal run, reconstruct the near-nadir sounding profile in the common navigation frame using the same candidate configured pitch correction.

Let the two reconstructed profiles be

\[
z_A(x;\Delta\theta),\qquad z_B(x;\Delta\theta),
\]

expressed over their common along-track navigation coordinate `x`.

The visible P2 residual is the disagreement between those reciprocal profiles over the same physical seabed. A pitch error appears primarily as an along-track displacement of the slope/feature; on a sloping bottom this also appears as a depth/profile mismatch at common horizontal positions.

The learner should see at least:

- pass A profile;
- reciprocal pass B profile;
- their mismatch before correction;
- the profiles approaching coincidence as the pitch correction is adjusted;
- the estimated pitch correction.

## Canonical estimator

For v0.1, use deterministic profile registration through the existing HydroSIM geometry rather than a vendor-specific closed-form patch-test formula.

For a candidate correction `Delta theta`, reconstruct both profiles with

\[
\theta_{candidate}=\theta_{cfg}+\Delta\theta.
\]

Interpolate both reconstructed profiles onto a common navigation-frame along-track grid over their overlap and evaluate

\[
J(\Delta\theta)=
\sqrt{
\frac{1}{N}
\sum_{i=1}^{N}
\left[z_A(x_i;\Delta\theta)-z_B(x_i;\Delta\theta)\right]^2
}.
\]

The estimated pitch correction is the candidate that minimizes `J`:

\[
\widehat{\Delta\theta}=\arg\min J(\Delta\theta).
\]

For the deterministic first slice, a bounded one-dimensional search or deterministic grid/refinement search is sufficient. This is an estimation operation over the existing physical geometry, not a new pitch-error propagation model.

The search interval should comfortably contain the hidden reference offset; `[-5 deg, +5 deg]` is suitable for the didactic default unless Software Engineering has a concrete numerical reason to use a narrower bound.

## Why a slope is required

On an ideal featureless flat plane, an along-track position shift cannot be identified from the bottom profile because the translated surface is unchanged. A slope or distinct feature converts the position shift into an observable reciprocal-profile mismatch.

This is why the reference scenario uses a 15-degree smooth slope and why the v0.1 P2 contract must not be implemented as a flat-bottom pitch test.

## Small-angle intuition (not the canonical estimator)

For a locally nadir-looking geometry at water depth `H` with a small residual pitch error `epsilon`, a single-pass along-track displacement has first-order scale

\[
|\delta x|\sim H\tan|\epsilon|\approx H|\epsilon|.
\]

Reciprocal passes expose opposite-sense shifts, so their relative displacement is of order `2 H tan(epsilon)` in the simplest symmetric geometry.

This relation is useful for teaching and sanity checks only. The estimator must use the HydroSIM geometric reconstruction and reciprocal-profile objective above so that sign and finite-angle behavior remain consistent with project conventions.

## State semantics

- `theta_true`: Truth;
- `theta_cfg`: Configured;
- reciprocal reconstructed soundings before calibration: Derived from Configured observations/geometry;
- `estimated_pitch_correction`: Estimated;
- `theta_est = theta_cfg + estimated_pitch_correction`: Estimated/Configured candidate depending on workflow stage;
- hidden comparison `theta_est - theta_true`: Derived validation diagnostic, not learner input.

## Required invariants and tests

1. **Zero residual closure:** if `theta_true == theta_cfg`, the estimator must return approximately 0 degrees and the reciprocal-profile objective must attain its minimum at zero correction.
2. **Sign closure:** if `theta_true > theta_cfg`, the estimated correction must be positive; if `theta_true < theta_cfg`, it must be negative.
3. **Magnitude closure:** for deterministic noiseless reference cases within the search domain, `theta_cfg + estimated_correction` must recover `theta_true` within the numerical tolerance justified by sampling/search resolution.
4. **Reciprocity:** swapping which reciprocal run is labelled A/B must not change the estimated correction.
5. **Minimum at correction:** applying the estimated correction must reduce the reciprocal-profile RMS mismatch relative to the uncorrected configuration.
6. **Flat-bottom non-identifiability:** a featureless flat plane must not be advertised as an identifiable P2 reference case; if tested, the implementation should expose the absence/weakness of the pitch observable rather than report a falsely precise solution.
7. **Isolation:** the reference scenario must keep latency, roll and yaw residuals at zero so the estimator is not solving a confounded calibration problem.

## First-slice boundaries

Out of scope for P2 v0.1:

- simultaneous estimation of latency and pitch;
- roll/yaw estimation;
- full-swath surface registration;
- stochastic noise and robust estimators;
- tide/water-level differences between reciprocal lines;
- lever-arm uncertainty;
- vendor-specific calibration-tool conventions;
- claiming that the recovered correction uniquely diagnoses the physical subsystem that caused an equivalent pitch residual.

## References

NOAA Ocean Exploration. *Multibeam Calibration: Conducting a Patch Test*. Pitch calibration guidance: reciprocal runs over the same line and a 10–20 degree slope; pitch offset produces reciprocal displacement of the slope.

NOAA Hydrographic Surveys Specifications and Deliverables (HSSD, 2022), multibeam calibration requirements: timing bias before pitch; pitch/timing lines as reciprocal passes over a 10–20 degree smooth slope perpendicular to depth contours.

R2Sonic. *The Patch Test*, Pitch Test section: reciprocal passes over the same sloping seabed and iterative pitch correction until the two profiles/surfaces reach a null/minimum.

HydroSIM conventions: `docs/conventions.md`.
HydroSIM reference scenario style: `src/hydrosim/scenarios/roll_offset.py`.
