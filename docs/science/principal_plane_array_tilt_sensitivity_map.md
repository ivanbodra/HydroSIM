# Principal-plane array-tilt sensitivity map

Status: analytical diagnostic for the controlled HydroSIM array-tilt experiment.

## Purpose

The single-curve tilt study showed that, for fixed beam angle and transducer sound-speed bias, the initial profile-frame Snell mismatch follows an exact reduced-model law. The next useful view is therefore a two-dimensional map over configured beam angle and transducer sensor bias.

This map is intentionally analytical. It does not ray-trace and it does not predict final sounding error directly. Its purpose is to identify where the controlled coordinate coupling is most sensitive before the full layered reconstruction is evaluated.

## Definition

Let

```text
theta = configured principal-plane beam angle
b = transducer sensor bias
c_true = true local sound speed
c_used = c_true + b
```

The physical TX angle in the array frame is

```text
theta_phys = asin((c_true / c_used) * sin(theta))
```

For array tilt `tau`, the exact reduced-model ray-parameter mismatch is

```text
Delta_p(tau) = K(theta, b) * sin(tau)
```

where

```text
K(theta, b) = cos(theta) / c_used
              - cos(theta_phys) / c_true
```

The mapped quantity is therefore

```text
K = d(Delta_p) / d(tau) at tau = 0
```

with unit `s/m/rad` in the explicit diagnostic naming used by the implementation.

## Interpretation

`K` is a local sensitivity coefficient for the profile-frame ray parameter. It is not a sounding uncertainty, an angular error, or a depth error.

Within the current reduced model:

- zero sound-speed bias gives `K = 0` for every propagating beam angle;
- `K(theta, b)` is even in beam angle, so port/starboard beams with equal absolute configured angle have the same coefficient when all other controlled quantities are identical;
- changing the sign of a small-to-moderate bias reverses the sign of the sensitivity in the tested reference regime;
- for the reference ranges exercised by the tests, the magnitude increases toward larger absolute beam angles.

The last two observations are retained as controlled-model behavior and should not be generalized beyond the propagating domain without inspecting the exact formula.

## Why this map is useful

The previous tilt sweep answers:

```text
How does one beam/bias pair respond as tilt changes?
```

The new map answers:

```text
Which beam/bias pairs are intrinsically most sensitive to the symmetry break near zero tilt?
```

Because the exact tilt dependence is `sin(tau)`, the coefficient can also reconstruct the analytical ray-parameter mismatch at any admissible tilt without another ray-tracing calculation:

```text
Delta_p(tau) = K * sin(tau)
```

This makes the map a useful pre-computation and validation surface for later numerical sounding-error studies.

## Validation

The implementation is checked against an independent direct evaluation of the closed-form equations. Additional limiting/symmetry tests require:

- zero bias -> zero coefficient;
- equal positive and negative beam angles -> equal coefficient;
- bias-sign reversal in the controlled reference case;
- deterministic angle-outer / bias-inner grid ordering;
- rejection of non-propagating steering states.

No layered propagation result is used to define the expected value of `K`.

## Scope and limitations

The map inherits all assumptions of the principal-plane array-tilt reference experiment: one principal plane, common TX/RX array orientation, stationary reciprocal propagation, and horizontal-profile coordinates. It characterizes the initial ray-parameter mismatch only.

A larger `|K|` means stronger initial sensitivity of `Delta_p` to small tilt. It does not by itself establish a larger final depth error, because the complete sounding response also depends on water-column structure, travel-time inversion, bottom geometry, depth, and later 3-D/multi-sector effects.
