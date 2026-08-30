# Layered SVP interface/contrast local-sensitivity convergence

## Status

Controlled numerical diagnostic. This study evaluates numerical stability of the existing local finite-difference sensitivity diagnostic. It is not an operational uncertainty model and does not establish an oceanographic law.

## Purpose

The local interface/contrast diagnostic estimates derivatives of the edge-minus-nadir swath-curvature metric around the Truth processing coordinate. Those derivatives depend on finite stencil steps. This convergence study repeats the same controlled experiment while progressively reducing both step sizes.

Let

```text
h = interface-depth finite-difference step [m]
k = sound-speed-contrast finite-difference step [m/s]
C = edge-minus-nadir vertical curvature [m]
```

Each requested coordinate `(h, k)` is evaluated with the existing centered 3 x 3 stencil. The refinement sequence must be ordered coarse to fine, with both `h` and `k` strictly decreasing.

## Quantities tracked

For every level the study retains the full local-sensitivity result, including

```text
dC/dz
dC/d(dc)
d2C/dz2
d2C/d(dc)2
d2C/(dz d(dc))
d(dc)/dz = -(dC/dz) / (dC/d(dc))
```

when the compensation denominator is numerically resolvable.

It also reports signed step-to-step changes, defined as

```text
Delta q_n = q_n - q_(n-1)
```

for the two first derivatives, the mixed derivative, and the compensation slope. The first level has no previous value and therefore stores `None` for these changes.

## Why no automatic pass/fail threshold

HydroSIM does not impose a universal tolerance for convergence. Appropriate tolerances depend on the intended experiment, water depth, profile morphology, beam fan, and numerical scale of the diagnostic. The study therefore exposes the refinement evidence rather than converting it into an unsupported universal quality flag.

## Why no formal observed order is asserted

Centered finite differences have familiar truncation properties for sufficiently smooth functions. The present response, however, is produced by a piecewise-constant layered propagation model with explicit interfaces and a full sounding reconstruction. HydroSIM therefore does not assume that a selected refinement sequence is already in a smooth asymptotic regime, nor does it infer a universal convergence order from a few levels.

## Controlled interpretation

If the derivatives and compensation slope change progressively less as `(h, k)` are reduced, that is numerical evidence that the selected local diagnostic is becoming step-stable for that experiment. Failure to stabilize can indicate that the stencil is still too coarse, that the response is strongly nonlinear over the sampled region, or that numerical precision/model discontinuities are becoming relevant.

The Truth-centered curvature should remain numerically closed at every level because the center coordinate is unchanged. This is a useful invariant, but it does not by itself demonstrate derivative convergence.

## State separation

Truth remains fixed: layered SVP, selected interface, flat bottom, ideal transducer sound-speed value, aligned pose. Configured state consists of the beam fan and the ordered finite-difference step pairs. Derived state consists of the local derivatives, compensation slope, interaction metric, and step-to-step changes.

## Limitations

This study does not provide TVU/THU, confidence intervals, stochastic uncertainty, global compensation curves, formal Richardson extrapolation, or guaranteed asymptotic convergence order. It applies only to the controlled horizontally layered, flat-bottom, principal-plane reference experiment implemented by the underlying diagnostics.
