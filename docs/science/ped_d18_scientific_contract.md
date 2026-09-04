# PED-D18 Scientific Contract — Uncertainty / TPU

Status: authoritative pedagogical-generation contract  
Experience: `PED-D18`  
Scope: minimum learner-facing scalar-input slice

## Learning question

PED-D18 teaches that uncertainty assigned to different physical inputs propagates differently into sounding-position uncertainty, and that the effect depends on the sounding geometry. It reuses the canonical uncertainty semantics and covariance propagation in `docs/science/uncertainty_error_verification_contract.md` and `src/hydrosim/integration/uncertainty.py`.

This first slice is a controlled analytical teaching model, not a complete hydrographic TPU implementation and not an IHO-order compliance calculator.

## State semantics

Learner-entered nominal scenario quantities and standard uncertainties are `Configured`. The input covariance, Jacobian, propagated covariance, component standard uncertainties, THU/TVU summaries and contribution curves are `Derived`. Standard uncertainty is not realized error and must not be labelled as such.

## Controlled geometry

Use a local right-handed sounding frame with components `(along, across, down)` [m], where `down` is positive downward. The nominal beam lies in the across/down plane at across-track angle `beta` measured from downward vertical, with HydroSIM sign convention: positive angle Port, negative Starboard.

For nominal slant range `r`:

```text
along = 0
across = -r sin(beta)
down = r cos(beta)
```

The minus sign maps positive-Port beam angle to negative body/sensor `Y` because canonical `+Y` is Starboard.

The minimum pedagogical scenario may hold nominal `r`, `beta`, sound speed `c`, TWTT `t_w`, and vessel along-track speed `v` as scenario parameters rather than counting them as uncertainty atoms.

## Seven learner uncertainty controls

The canonical scalar controls are one-sigma standard uncertainties, all non-negative:

1. `u_position_horizontal` [m] — isotropic horizontal platform-position standard uncertainty; contributes equally and independently to along/across position components in this minimum slice.
2. `u_attitude_roll` [rad] — roll standard uncertainty. Roll is selected as the first-slice attitude representative because a beam in the across/down plane has a direct analytical across/vertical sensitivity. This is not a claim that pitch/heading uncertainty is negligible in a complete TPU.
3. `u_range` [m] — standard uncertainty of slant range after detection/ranging.
4. `u_sound_speed` [m/s] — standard uncertainty of the effective sound speed used in the homogeneous range conversion for this controlled case.
5. `u_offset_across` [m] — standard uncertainty of the relevant installation/lever-arm component in the across direction.
6. `u_timing` [s] — standard uncertainty of position-to-ping timing association; converted to along-track position sensitivity through nominal vessel speed `v`.
7. `u_water_level` [m] — standard uncertainty of the vertical reduction/water-level contribution; acts on the down component in this local model. Sign is immaterial to its variance contribution but the underlying coordinate convention remains `+down`.

These seven controls are independent in the first production slice. The resulting diagonal input covariance is therefore an explicit didactic assumption, not a general HydroSIM rule. The generic canonical uncertainty API continues to preserve arbitrary covariance/correlation.

## Analytical first-order mapping

Let the ordered uncertain input vector be

```text
q = [p_h_along, p_h_across, roll, range, sound_speed, offset_across, timing, water_level]
```

The single learner `u_position_horizontal` control populates two independent equal-variance components `p_h_along` and `p_h_across`; therefore seven controls generate eight covariance components internally.

At the nominal scenario, use output

```text
y = [along, across, down]
```

and the following local sensitivities:

```text
position along:   d y / d p_h_along  = [1, 0, 0]
position across:  d y / d p_h_across = [0, 1, 0]

range:            d y / d r          = [0, -sin(beta), cos(beta)]

roll:             d y / d roll       = [0, -down, across]
                  = [0, -r cos(beta), -r sin(beta)]

offset across:    d y / d offset     = [0, 1, 0]

timing:           d y / d dt         = [v, 0, 0]

water level:      d y / d h          = [0, 0, 1]
```

For the controlled homogeneous sound-speed/range relation

```text
r = c t_w / 2
```

the sound-speed sensitivity is

```text
d r / d c = t_w / 2

d y / d c = (t_w / 2) [0, -sin(beta), cos(beta)]
```

This `c*t_w/2` relation is valid only for this explicitly homogeneous pedagogical scenario; it must not replace the canonical propagation/range semantics elsewhere in HydroSIM.

The Python scientific/application layer constructs `Sigma_q`, the analytical Jacobian `J`, then delegates propagation to the canonical relation

```text
Sigma_y ~= J Sigma_q J^T
```

through `propagate_uncertainty()`. React must never construct variances, covariance matrices, or Jacobians.

## Learner-visible outputs

Minimum authoritative outputs are:

- component standard uncertainties `u_along`, `u_across`, `u_down` [m];
- propagated 3x3 covariance in the declared local frame;
- `THU = sqrt(u_along^2 + u_across^2)` [m] as the radial horizontal standard-uncertainty summary for this pedagogical slice;
- `TVU = u_down` [m] as the vertical standard uncertainty in this pedagogical slice;
- optional `TPU_3D = sqrt(u_along^2 + u_across^2 + u_down^2)` [m], only if explicitly labelled **3-D combined standard uncertainty**. Do not present this scalar as an IHO-defined compliance statistic or as a universal industry definition of `TPU`;
- across-track/beam-angle variation obtained by reevaluating the same analytical Jacobian over configured `beta`, not by inventing a display-only curve;
- per-input variance contributions may be shown when computed in Python from the same Jacobian and diagonal first-slice covariance.

If expanded uncertainty is displayed, its coverage factor `k` must be explicit. A default `k=2` may be offered only as `expanded uncertainty, k=2`; it must not be labelled a 95% confidence interval without distributional assumptions.

## Expected analytical anchors

1. With every input uncertainty zero, propagated covariance and all component standard uncertainties are zero.
2. At nadir (`beta=0`), range and sound-speed uncertainty contribute vertically but not across-track; roll uncertainty contributes across-track with magnitude sensitivity `r`.
3. At nadir, timing uncertainty contributes along-track as `u_along = |v| u_timing` when it is the only non-zero contributor.
4. At nadir, `u_offset_across` contributes one-for-one to `u_across`.
5. Increasing `|beta|` redistributes range/sound-speed contributions between across and vertical components according to sine/cosine geometry.
6. Port/Starboard reversal changes signed Jacobian terms where appropriate but does not change variances for a single independent symmetric scalar contributor.
7. Doubling one isolated standard uncertainty doubles its isolated output standard-uncertainty contribution and quadruples its variance contribution.

## Validity and fidelity boundary

The first slice assumes a homogeneous medium for the explicit sound-speed sensitivity, one beam in the across/down plane, local first-order linearization, small roll uncertainty, scalar independent contributors, constant nominal along-track vessel speed for timing sensitivity, and no covariance between the seven learner controls.

It does not constitute a full MBES TPU budget. It excludes pitch/heading coupling, full 3-D attitude covariance, beam-angle uncertainty, detection uncertainty, refraction/SVP covariance, dynamic heave models, datum transformation uncertainty, correlated navigation/environmental terms, nonlinear/Monte-Carlo propagation, and vendor-specific uncertainty models. These may be added only through later explicit scientific contracts.

## Traceability

This contract specializes, but does not replace:

- `docs/science/uncertainty_error_verification_contract.md`;
- `src/hydrosim/integration/uncertainty.py`.

Scientific basis remains JCGM 100:2008 (GUM) for first-order covariance propagation and IHO S-44 Edition 6.2.0 for hydrographic uncertainty context. The controlled geometry follows HydroSIM canonical body/local conventions and the existing separation `Truth != Observed != Configured != Estimated != Derived`.