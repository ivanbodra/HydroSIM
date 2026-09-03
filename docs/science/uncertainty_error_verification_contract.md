# Uncertainty, Truth Error, and Verification Residual Contract

Version: 0.1.0  
Language: English (canonical)  
Status: Scientific contract

## 1. Purpose

This contract defines the minimum HydroSIM scientific architecture needed to keep three different quantities separate:

1. **a priori uncertainty** — uncertainty propagated from uncertain inputs and their covariance;
2. **simulation-truth error** — the difference between a reconstructed/derived result and hidden simulator Truth;
3. **a posteriori verification residual** — the discrepancy between two independently acquired or processed results used to assess agreement.

These concepts must never be represented by one generic `error` quantity.

The state invariant remains:

```text
Truth != Observed != Configured != Estimated != Derived
```

A value may be numerically equal to another state in a controlled case without becoming the same semantic state.

## 2. Normative terminology

### 2.1 A priori uncertainty

Uncertainty is a parameter describing the dispersion assigned to a quantity or result. A sensor specification, calibration uncertainty, installation-survey uncertainty, timing uncertainty, or environmental uncertainty is not itself an observed error.

HydroSIM uses **standard uncertainty** for uncertainty expressed as a standard deviation and **covariance** for joint second-order uncertainty. Expanded uncertainty must carry its coverage factor and/or stated coverage probability explicitly.

### 2.2 Simulation-truth error

For a Derived result `y_derived` and simulator Truth `y_truth`, expressed in the same frame, epoch, units, and quantity definition, the canonical truth-error vector is

```text
truth_error_vector = y_derived - y_truth
```

Therefore a positive component means that the Derived result is displaced in the positive direction of the declared frame relative to Truth.

This quantity is available only in simulation or other controlled cases where Truth is known. It is **Derived**, not Observed.

Preferred names:

- `truth_error_vector`
- `true_position_error` when the quantity is specifically position
- `truth_depth_error` for a scalar depth comparison when the sign convention is declared

Avoid an unqualified `error_vector` in new scientific APIs.

### 2.3 A posteriori verification residual

For two comparable results `y_a` and `y_b`, the ordered residual is

```text
verification_residual = y_a - y_b
```

The order (`a`, `b`) is part of the data definition and must not be lost.

A check/cross-line residual is an internal-consistency observation. It is **not automatically the true error** of either line. Common-mode systematic effects may be absent or strongly suppressed in the residual.

## 3. Coordinate and nomenclature requirements

HydroSIM must prefer **along-track** and **across-track** for vessel/sonar-relative horizontal geometry:

- along-track: approximately vessel `+X` / Forward;
- across-track: approximately `+Y` Starboard / `-Y` Port;
- vertical component follows the explicitly declared frame (for canonical local NED, `+Z` is Down).

Every uncertainty vector, covariance matrix, truth-error vector, and verification residual must declare enough metadata to identify:

- quantity/component ordering;
- units;
- reference frame;
- epoch or association when time-dependent;
- semantic state of the represented value.

A covariance matrix without an ordered component definition and frame is scientifically incomplete.

## 4. Versioned scientific data contracts

The following are **scientific schemas**, not a requirement for one particular Python class hierarchy. Software Engineering may implement them using dataclasses, typed dictionaries, pydantic models, or another stable representation without changing their semantics.

### 4.1 `UncertainInputSet` — scientific schema v0.1

Required semantics:

```text
schema_version: "0.1"
values: ordered vector x
component_ids: ordered identifiers matching x
units: unit per component
frame: frame identifier where applicable
covariance: Sigma_x
state: Observed | Configured | Estimated
```

Requirements:

- `Sigma_x` uses squared/cross-product units implied by the component ordering;
- diagonal terms are variances and must be non-negative;
- off-diagonal terms preserve covariance and must not be silently zeroed;
- the matrix must be symmetric to numerical tolerance and positive semidefinite within numerical tolerance;
- uncertainty contributors from different semantic states may coexist, but the state of each component must remain traceable.

Potential contributors include GNSS position, roll/pitch/heading/heave, installation/alignment, lever arms, TWTT/range, beam angle, sound speed, timing/latency, water level/vertical reduction, and bottom detection. This list is not a requirement to implement every contributor in v0.1.

### 4.2 `PropagatedUncertainty` — scientific schema v0.1

Required semantics:

```text
schema_version: "0.1"
result_component_ids: ordered output identifiers
units: unit per output component
frame: output frame
covariance: Sigma_y
standard_uncertainty: sqrt(diag(Sigma_y))
method: "linearized_jacobian"
state: Derived
```

Optional expanded-uncertainty metadata may include:

```text
coverage_factor: k
coverage_probability: p
expanded_uncertainty: U
```

`k`, `p`, and the interpretation of `U` must be explicit. HydroSIM must not label `k * u` as a confidence interval unless the distributional assumptions needed for that interpretation are stated.

### 4.3 `TruthErrorVector` — scientific schema v0.1

Required semantics:

```text
schema_version: "0.1"
derived_value
truth_value
truth_error_vector = derived_value - truth_value
component_ids
units
frame
state: Derived
```

The two source values must represent the same physical quantity at compatible association/epoch and must be transformed to the same frame before subtraction.

### 4.4 `VerificationResidual` — scientific schema v0.1

Required semantics:

```text
schema_version: "0.1"
value_a
value_b
verification_residual = value_a - value_b
association_a
association_b
component_ids
units
frame
state: Derived
```

If uncertainty information is available, the residual covariance may also be stored as Derived metadata.

## 5. Linearized covariance propagation

For a measurement/reconstruction model

```text
y = f(x)
```

with input covariance `Sigma_x`, the first-order propagated covariance is

```text
Sigma_y ~= J Sigma_x J^T
```

where

```text
J_ij = partial f_i / partial x_j
```

evaluated at the stated nominal/configured point.

### 5.1 Canonical interface semantics

The scientific interface must accept:

- ordered nominal input vector `x`;
- ordered input covariance `Sigma_x`;
- either an explicit Jacobian `J` or a callable/model from which a Jacobian is obtained by an explicitly named method;
- ordered output-component definition.

It must return `Sigma_y` with output ordering and units/frame metadata.

The initial contract does **not** prescribe how every sonar/sensor Jacobian is calculated. Analytical, automatic-differentiation, and controlled numerical finite-difference Jacobians may coexist if their method and validity are explicit.

### 5.2 Validity boundary

The expression above is a local first-order approximation. It can be inadequate for strong nonlinearity, discontinuities, bounded/asymmetric distributions, multimodality, or large uncertainties relative to the model curvature.

When that limitation matters, HydroSIM must not silently present the linearized covariance as exact. A later Monte-Carlo/distribution-propagation path may be added without changing the semantic separation defined here.

## 6. Correlation is first-class

HydroSIM must not assume all uncertainty contributors are independent.

For scalar quantities `z1` and `z2`, with ordered difference

```text
Delta = z1 - z2
```

the variance is

```text
Var(Delta) = Var(z1) + Var(z2) - 2 Cov(z1, z2)
```

For vector quantities,

```text
r = y_a - y_b
```

and

```text
Sigma_r = Sigma_a + Sigma_b - Sigma_ab - Sigma_ba
```

where `Sigma_ab = Cov(y_a, y_b)` and `Sigma_ba = Sigma_ab^T` for real-valued quantities.

Shared GNSS corrections, water-level models, SVPs, calibration terms, timing sources, or other common processing inputs can generate correlation. A common-mode systematic error may therefore be poorly visible in cross-line residuals even when it materially affects both lines.

## 7. A posteriori check/cross-line model

The minimum HydroSIM model separates **pairing** from **residual interpretation**.

1. A pairing/intersection process identifies comparable results from line A and line B.
2. The compared values are transformed/reduced to a common physical quantity, frame, datum, and units.
3. The ordered residual `A - B` is computed.
4. If covariance information exists, residual covariance is computed with cross-covariance when known.
5. Statistics over many residuals are Derived diagnostics of agreement; they are not automatically estimates of absolute survey error.

Potential contributors to observed cross-line discrepancies include measurement noise, seabed roughness, different insonification/detection, navigation/motion, sound-speed effects, water-level reduction, and systematic effects. HydroSIM must not infer one physical cause from a residual without an explicit diagnostic/estimation model.

## 8. Compatibility strategy for existing generic error fields

Existing repository structures may contain fields named `error_vector` or similarly generic terms. They must not be reinterpreted silently.

Migration rule:

1. Determine the operands and sign convention of the existing field.
2. If it is exactly `Derived - Truth`, expose the new canonical semantic name `truth_error_vector`.
3. The legacy name may remain temporarily as a compatibility alias, but must be documented/deprecated and must return the same quantity/sign.
4. If the existing field is a comparison between non-Truth results, migrate it to an explicitly ordered residual name instead.
5. Do not map an uncertainty quantity to any `*_error*` field.

No serialized field should change sign as part of a rename without an explicit migration/version boundary.

## 9. Required analytical anchors

Implementation must include controlled tests independent of any full survey simulation.

### 9.1 Identity propagation

For `y = x`, `J = I`:

```text
Sigma_y = Sigma_x
```

### 9.2 Linear scalar propagation

For

```text
y = a x
```

with `Var(x) = sigma_x^2`:

```text
Var(y) = a^2 sigma_x^2
```

### 9.3 Correlated two-input propagation

For

```text
y = x1 + x2
J = [1, 1]
```

with covariance `Cov(x1,x2)=c12`:

```text
Var(y) = Var(x1) + Var(x2) + 2 c12
```

The test must demonstrate that retaining covariance changes the result relative to an independence assumption.

### 9.4 Correlated difference

For `Delta = z1-z2`:

```text
Var(Delta) = Var(z1) + Var(z2) - 2 Cov(z1,z2)
```

At equal variance `sigma^2` and perfect common-mode correlation (`Cov=sigma^2`), the idealized residual variance is zero even though each individual result remains uncertain. This is the canonical didactic anchor showing why agreement does not prove absolute accuracy.

### 9.5 Truth-error sign

For local NED positions

```text
truth   = [10, 20, 30] m
derived = [11, 18, 33] m
```

HydroSIM must return

```text
truth_error_vector = [+1, -2, +3] m
```

### 9.6 Residual order

If

```text
z_a = 12.0 m
z_b = 11.5 m
```

then an `A - B` residual is

```text
+0.5 m
```

and reversing the associations must return `-0.5 m`.

## 10. API/state separation invariants

The following are normative:

- uncertainty covariance is not a truth-error vector;
- truth error is not an observation available to a real survey workflow;
- a verification residual is not automatically truth error;
- standard uncertainty is not a realized error;
- an a posteriori residual must retain operand order/association;
- covariance and residuals must retain frame, component order, and units;
- a hidden injected systematic offset and the standard uncertainty assigned to the corresponding parameter are independent concepts;
- UI text and APIs must not use `error` as an umbrella label for all three families.

## 11. Didactic objective

A later learner-facing experience may place the three families side by side for the same synthetic survey:

```text
A priori expected uncertainty
    -> what dispersion the model predicts from stated uncertain inputs

Hidden simulation-truth error
    -> what error actually occurred in this controlled simulation

A posteriori verification residual
    -> what an independent comparison can observe
```

The key lesson is that these quantities can disagree for scientifically valid reasons, especially when systematic/common-mode errors exist.

## 12. References

- JCGM 100:2008, *Evaluation of measurement data — Guide to the expression of uncertainty in measurement (GUM)*. BIPM/JCGM. The GUM provides the established uncertainty/covariance and first-order propagation framework used here.
- JCGM 101:2008, *Supplement 1 to the GUM — Propagation of distributions using a Monte Carlo method*. Retained as a future higher-fidelity alternative when linearization is inadequate.
- IHO S-44 Edition 6.2.0 (October 2024), *IHO Standards for Hydrographic Surveys*. Retained as the current hydrographic standards context for survey uncertainty and quality requirements.
- Hughes Clarke (2003), *Dynamic Motion Residuals in Swath Sonar Data: Ironing out the Creases*. Retained for the distinction between physical/integration causes and observable bathymetric residual signatures.

## 13. Scope boundary

This contract defines semantics and the minimum propagation/residual mathematics. It does not yet require:

- a complete TPU budget for every HydroSIM sensor;
- one hard-coded vendor uncertainty model;
- Monte-Carlo propagation;
- a specific cross-line matching algorithm;
- automatic diagnosis of residual causes;
- compliance certification against a particular IHO survey order.

Those are separate capabilities and must be introduced only when required by an active product slice.
