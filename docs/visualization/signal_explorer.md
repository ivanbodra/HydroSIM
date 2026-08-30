# Signal Explorer

Version: 0.2.0

## Purpose

`hydrosim.visualization.signal_explorer` is the first composition layer for the acoustic-signal block of the HydroSIM Didactic Explorer.

It does not introduce a new waveform model. It packages existing waveform and matched-filter reference calculations into a stable render-ready snapshot.

The first reference renderer is provided by `hydrosim.visualization.signal_explorer_plot`.

## Current scope

The snapshot supports the existing HydroSIM waveform definitions:

- finite-duration CW pulse;
- finite-duration linear-FM (LFM) pulse.

For one pulse and sample rate, it exposes:

- the continuous pulse definition;
- the discrete baseband sampling adequacy diagnostic;
- sample times;
- real and imaginary complex-baseband components;
- unwrapped baseband phase;
- normalized waveform autocorrelation / matched-filter response.

The causal chain is:

```text
CW or LFM definition
        -> sampling adequacy
        -> complex baseband realization
        -> matched-filter autocorrelation
        -> Signal Explorer snapshot
        -> reference renderer / future interactive UI
```

## First reference renderer

`plot_signal_explorer_comparison(first, second)` renders one CW snapshot and one LFM/chirp snapshot in three synchronized didactic panels:

1. transmitted waveform as the in-phase component of the scientific complex-baseband representation;
2. unwrapped baseband phase evolution;
3. normalized matched-filter/autocorrelation amplitude versus lag.

The renderer accepts the two snapshots in either order and uses each waveform's existing sample rate and duration. It selects only a readable time unit for display; it does not alter scientific values.

The first lesson therefore makes the main distinction visually explicit:

```text
finite CW
    -> constant complex-baseband phase
    -> broad autocorrelation response

LFM chirp
    -> evolving complex-baseband phase
    -> compressed matched-filter peak
```

The exact response remains dependent on the configured pulse duration, bandwidth, and discrete sample rate.

## Scientific boundary

The scientific calculations remain in `hydrosim.acquisition.waveform` and `hydrosim.acquisition.numerical_resolution`.

The Signal Explorer adapter and renderer must not:

- add noise or electronics implicitly;
- invent receiver bandwidth;
- infer calibrated source level or receive amplitude;
- add propagation or attenuation physics;
- redefine waveform sampling rules.

For that reason there is no Scientific Registry entry for this visualization adapter or renderer.

## Baseband representation

The first snapshot intentionally exposes the complex analytic/baseband representation used by the scientific waveform layer.

For a CW pulse this baseband signal is constant. That does **not** mean the physical acoustic pressure is constant in time; it means the carrier oscillation has been removed by the analytic/baseband representation.

The first renderer labels this representation explicitly. A later didactic renderer may show a carrier-scale oscillation or an animated passband reconstruction, but that presentation must clearly distinguish itself from the baseband scientific representation and must not duplicate or replace the waveform model.

## Intended first interactive controls

The first Signal Explorer UI should remain small:

1. waveform type: CW or LFM;
2. center frequency;
3. pulse duration;
4. LFM bandwidth when applicable;
5. numerical sample rate as an advanced teaching control.

The immediate observable outputs should be waveform/baseband state and matched-filter response. Frequency-dependent propagation attenuation should be added only after a referenced absorption model is available in the Scientific Core.
