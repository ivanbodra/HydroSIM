# Signal Explorer

Version: 0.1.0

## Purpose

`hydrosim.visualization.signal_explorer` is the first composition layer for the acoustic-signal block of the HydroSIM Didactic Explorer.

It does not introduce a new waveform model. It packages existing waveform and matched-filter reference calculations into a stable render-ready snapshot.

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
        -> future renderer / interactive UI
```

## Scientific boundary

The scientific calculations remain in `hydrosim.acquisition.waveform` and `hydrosim.acquisition.numerical_resolution`.

The Signal Explorer adapter must not:

- add noise or electronics implicitly;
- invent receiver bandwidth;
- infer calibrated source level or receive amplitude;
- add propagation or attenuation physics;
- redefine waveform sampling rules.

For that reason there is no Scientific Registry entry for this visualization adapter.

## Baseband representation

The first snapshot intentionally exposes the complex analytic/baseband representation used by the scientific waveform layer.

For a CW pulse this baseband signal is constant. That does **not** mean the physical acoustic pressure is constant in time; it means the carrier oscillation has been removed by the analytic/baseband representation.

A later didactic renderer may show a carrier-scale oscillation or an animated passband reconstruction, but that presentation must clearly distinguish itself from the baseband scientific representation and must not duplicate or replace the waveform model.

## Intended first interactive controls

The first Signal Explorer UI should remain small:

1. waveform type: CW or LFM;
2. center frequency;
3. pulse duration;
4. LFM bandwidth when applicable;
5. numerical sample rate as an advanced teaching control.

The immediate observable outputs should be waveform/baseband state and matched-filter response. Frequency-dependent propagation attenuation should be added only after a referenced absorption model is available in the Scientific Core.
