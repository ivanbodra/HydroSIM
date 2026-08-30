# Principal-plane array tilt sounding-error map

Status: controlled numerical diagnostic linked to the analytical principal-plane array-tilt sensitivity model.

## Purpose

The analytical sensitivity map identifies the local Snell ray-parameter sensitivity to array tilt as a function of configured beam angle and transducer sound-speed bias. This diagnostic connects that analytical quantity to the final calculated-minus-Truth sounding response in the existing layered reference experiment.

No new acoustic propagation law is introduced. The numerical response is obtained by reusing the established Truth-versus-processing experiment with identical finite-thickness Truth and processing profiles.

## Coordinates

The map samples three explicit coordinates:

- configured array-frame across-track angle `theta_cfg`;
- transducer sound-speed sensor bias `b`;
- principal-plane array tilt `tau`.

The local true sound speed is `c_true` and the sonar-used sound speed is

```text
c_used = c_true + b
```

The physical TX angle in array coordinates is

```text
theta_phys = asin((c_true / c_used) * sin(theta_cfg))
```

## Analytical anchor

The zero-tilt sensitivity coefficient is

```text
K = cos(theta_cfg) / c_used - cos(theta_phys) / c_true
```

For the reduced principal-plane model, the exact signed ray-parameter mismatch at tilt `tau` is

```text
Delta_p_analytical = K * sin(tau)
```

The numerical experiment independently reconstructs the two profile-frame ray parameters from the Truth launch angle and processing receive angle:

```text
p_truth = sin(theta_phys_profile) / c_true
p_processing = sin(theta_est_profile) / c_used
Delta_p_numerical = p_processing - p_truth
```

The map records the residual

```text
r_p = Delta_p_numerical - Delta_p_analytical
```

This residual is a consistency diagnostic between the closed-form coordinate model and the numerical reference-experiment state construction. It is not an uncertainty estimate.

## Sounding response

For each angle-bias-tilt point, the map records:

- analytical sensitivity `K`;
- analytical `Delta_p`;
- numerical `Delta_p`;
- analytical-versus-numerical residual;
- across-track sounding error `dy`;
- vertical sounding error `dz`;
- total sounding-error norm.

The sounding error is calculated minus Truth in the documented HydroSIM NED-like frame, where `Y` is starboard and `Z` is down.

The analytical ray-parameter mismatch has a known odd symmetry in tilt. No corresponding odd or even symmetry is imposed on `dy`, `dz`, or the total sounding-error norm. Refraction, TWTT inversion, layer transitions, bottom intersection, and coordinate geometry can make the final sounding response nonlinear.

## Controlled interpretation

Two exact closure cases remain useful checks:

1. `tau = 0`: the narrow aligned transducer-value cancellation is recovered;
2. `b = 0`: the sonar-used sound speed equals Truth, so the array-tilt coordinate alone introduces no sound-speed error.

When both `tau` and `b` are non-zero, the map quantifies how the initial analytical ray-parameter mismatch propagates into horizontal and vertical sounding error for the chosen controlled geometry.

The result must not be interpreted as a general MBES error law. Magnitudes depend on the selected profile, water depth, beam angle, tilt, and other assumptions of the reference experiment.

## Validation

Validation uses independent closed-form expressions for `theta_phys`, `K`, and `Delta_p`. The tests require the numerical ray-parameter mismatch reconstructed from experiment states to match the closed form to floating-point precision.

The tests also preserve zero-tilt and zero-bias sounding closure, resolve non-zero across-track and total errors when both perturbations are present, and deliberately avoid imposing a final sounding-error symmetry that has not been derived.

## Scope and limitations

The diagnostic remains limited to stationary reciprocal propagation, one principal plane, one common TX/RX array orientation, horizontal layered sound-speed structure, aligned platform pose, and flat-bottom geometry. It does not yet include independent 3-D TX/RX installation rotations, vessel attitude dynamics, multi-sector timing, sector association, uncertainty propagation, or operational accuracy specifications.
