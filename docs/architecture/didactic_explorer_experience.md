# Didactic Explorer User Experience Contract

Version: 0.1.0

## Purpose

The HydroSIM Didactic Explorer should feel like an interactive scientific lesson, not a configuration form and not an imitation of a commercial sonar console.

The user experience is organized around the existing teaching contract:

```text
control -> physical phenomenon -> observable consequence
```

For every first-release lesson, the learner should be able to answer four questions without reading source code or external documentation:

1. What am I trying to understand?
2. Which parameter should I change?
3. Where should I look for the consequence?
4. What scientific representation am I looking at?

## Experience principles

### One learning question at a time

A page should start from a learning question rather than from a list of available parameters. Controls that do not help answer that question should not be exposed in the first-release view.

### Every active control must produce a visible consequence

A control should not be interactive merely because the Scientific Core accepts the parameter. If changing it does not alter an observable shown in the current lesson, it should be fixed, hidden, or explicitly deferred to another lesson.

This rule is especially important for the first Signal lesson. Its scientific plots use a complex analytic/baseband representation, so changing carrier center frequency does not visibly change the baseband CW waveform or normalized matched-filter response by itself. Until frequency is connected to a visible consequence such as wavelength/beam behavior or referenced frequency-dependent absorption, center frequency should remain context rather than an active teaching control.

### Immediate deterministic feedback

The learner should normally see the consequence while manipulating the control. The interface should favor direct manipulation, such as sliders paired with exact numeric entry, over an apply/run workflow for small deterministic lessons.

### Tell the learner where to look

The interface should include short observation guidance. It should not give away every conclusion, but it should direct attention to the relevant visual variable: peak width, phase evolution, ray curvature, footprint, sounding displacement, or another observable.

### Make fidelity visible

Each lesson must communicate what kind of representation is shown and what is not shown. Relevant labels include:

- conceptual geometry;
- controlled analytical/reference model;
- numerical scientific model;
- synthetic observation;
- derived sounding.

A scientific boundary note should prevent a visualization from implying greater fidelity than the underlying model supports.

### Preserve scientific state semantics

When a lesson introduces error, the interface should distinguish Truth, Observed, Configured, Estimated, and Derived states rather than blending them into a single display state.

### Progressive disclosure

The first screen should remain small. Advanced controls belong in later lessons or an advanced section only when their effect can be interpreted in the same causal chain.

## Application-level structure

The Didactic Explorer should expose the five connected learning blocks as one product:

```text
Signal -> Beam -> Propagation -> Vessel -> Motion
```

A block may be visible before it is implemented so the learner understands the product structure, but unfinished blocks must be clearly marked as planned and must not look operational.

The page structure should normally be:

```text
lesson title
learning question
scientific representation / fidelity note

controls / direct manipulation   |   main visualization
what to look for                 |   observable consequence
scientific boundary              |
```

## Signal lesson v0.1

The first integrated Signal lesson asks:

> How do pulse duration and LFM bandwidth change the transmitted baseband signal and its pulse-compression response?

Active controls:

- pulse duration;
- LFM bandwidth.

Fixed context:

- carrier center frequency: 300 kHz.

Observable panels:

- in-phase complex-baseband waveform;
- unwrapped baseband phase;
- normalized autocorrelation / matched-filter response.

The interface explicitly states that the baseband CW phase behavior does not represent constant physical acoustic pressure and that frequency-dependent absorption, electronics, noise, and a general wave-equation field solution are not yet represented in this lesson.

## Acceptance criteria for a first-release lesson

A lesson is ready for the application when all of the following are true:

- it has one explicit learning question;
- every exposed control changes a displayed observable;
- the displayed observable comes from the Scientific Core through a composition/snapshot boundary;
- the user receives immediate deterministic feedback for ordinary control changes;
- the representation/fidelity level is stated;
- important omissions are stated when they could otherwise be inferred incorrectly;
- the lesson can be reset to a meaningful default state;
- the vertical slice is covered by tests appropriate to its scientific and UI risk.

## Design implication

HydroSIM should optimize for scientific comprehension, not parameter density. The preferred first-release experience is therefore a small number of highly interpretable controls connected to strong visual consequences, with advanced system configuration introduced only as the learner moves toward the integrated Survey Simulator.
