# PED-D9 Scientific Contract — Bottom Detection

Status: authoritative pedagogical-generation contract  
Experience: `PED-D9`  
Scope: minimum production learner vertical slice

## Learning question

PED-D9 teaches how an acoustic receive signal becomes a bottom timing/angle detection, while keeping the distinction between the received/matched-filter signal, the detection observation, and the later reconstructed sounding.

The first production slice is deliberately narrower than the full pedagogical plan. HydroSIM currently has an authoritative **reference amplitude detector** based on the strongest matched-filter magnitude. Phase detection, threshold/noise-driven false or missed detections, hybrid transition logic, detection windows, and High Density are not yet authoritative Core capabilities and must not be fabricated by the application or UI.

## Canonical Core ownership

- `src/hydrosim/acquisition/waveform.py` owns waveform/matched-filter correlation semantics.
- `src/hydrosim/acquisition/bottom_detection.py` owns `BottomDetection`, `BeamDetections`, and the reference amplitude detector.
- `docs/science/signal_waveform_contract.md` owns signal/matched-filter conventions.
- `docs/science/d8_observation_state_contract.md` owns the observation/reconstructed-sounding boundary.

The application/API may serialize these values but must not implement a second detector.

## First-slice governing algorithm

For a complex matched-filter correlation sequence `R[k]`, the reference detector selects

`k_peak = arg max_k |R[k]|`.

With reference length `N_ref` and sample rate `f_s`,

`lag_samples = k_peak - (N_ref - 1)`

`arrival_offset = lag_samples / f_s`

`TWTT = arrival_offset - tx_delay`.

The implementation rejects negative arrival lag and an arrival preceding the sector transmit epoch beyond the existing half-sample tolerance. A sub-half-sample negative numerical TWTT is clamped to zero by the canonical implementation.

These equations document existing Core behavior; they do not introduce a new detector.

## State semantics

### Configured

- sample rate `f_s` [Hz], positive;
- reference sample count `N_ref >= 1`;
- sector transmit delay `tx_delay` [s], non-negative;
- parent beam association and steering angle when supplied;
- the input correlation sequence used for the deterministic reference exercise.

A future learner-facing signal generator may expose physical echo/noise controls only through an authoritative signal/channel model; PED-D9 must not reinterpret arbitrary frontend values as physical noise or seabed scattering.

### Observed

`BottomDetection` is an **Observed measurement tuple**, not a Cartesian sounding. Its scientifically relevant fields include detection method, arrival/TWTT, beam association, detected/associated across-track angle, and normalized peak amplitude when available.

### Derived

Peak index, lag samples, and display conversions derived from the configured correlation and detector output are `Derived`. A Cartesian sounding reconstructed from a detection plus Configured platform/environment state is also `Derived` and belongs to the sounding-formation chain, not to the detector itself.

PED-D9 does not convert a detection into hidden `Truth` or an `Estimated` seabed position.

## Detection-method boundary

The only executable authoritative detection method for the first slice is:

- `amplitude_peak`: strongest matched-filter magnitude.

`phase_zero_crossing` exists as a data-model method label but there is no authoritative phase detector implementation in the current Core. It must therefore be presented as unavailable/deferred, not simulated with a frontend approximation.

Likewise, the current detector contains **no detection threshold, stochastic noise, sediment/backscatter law, false-alarm model, missed-detection model, detection window, hybrid amplitude/phase transition, or proprietary/vendor logic**. Those planned PED-D9 concepts require later scientific/Core capability before becoming functional learner controls.

## Multiple detections and High Density

The data architecture permits zero, one, or multiple `BottomDetection` objects per receive beam through `BeamDetections`; this is an architectural capability, not evidence that the present reference detector generates multiple detections. `detect_bottom_from_matched_filter()` returns exactly one strongest-peak detection for a valid input.

Therefore the first slice may teach the distinction `beam != sounding/detection count` conceptually and expose the container semantics, but it must not claim operational High Density or multiple-detection physics until a selection/generation model is implemented and scientifically specified.

## Angle and timing conventions

- across-track angle follows HydroSIM's canonical convention: zero is nominal downward; positive is Port; negative is Starboard;
- `tx_delay_seconds` is a physical/configured offset from the correlation reference epoch to sector transmission for this detector calculation;
- `twtt_seconds` is two-way acoustic travel time after removing that transmit delay;
- positive lag means the received echo occurs later than the reference.

Do not replace `TWTT` by geometric range using `c*TWTT/2` unless the active propagation model explicitly permits that approximation.

## Normalized amplitude boundary

`normalized_amplitude` is the magnitude of the selected correlation sample as supplied to the detector. It is not calibrated received level, source level, target strength/backscatter, SNR, detection probability, or absolute acoustic gain. The UI must not attach those meanings to it.

## Minimum learner cause → effect behavior

For the authoritative first slice:

1. moving the dominant matched-filter peak to a later non-negative lag increases the reported arrival offset and TWTT by the corresponding sample interval;
2. increasing `tx_delay` for a fixed arrival decreases recovered TWTT by the same amount until the invalid-before-transmit boundary is reached;
3. changing the strongest correlation magnitude location changes the selected detection location deterministically;
4. beam/angle association is preserved in the resulting observation and does not itself perform sounding reconstruction.

## Minimum scientific acceptance anchors

- a unique strongest peak at lag `L >= 0` returns `peak_lag_samples == L`;
- with `tx_delay = 0`, `TWTT = L / f_s`;
- with valid positive transmit delay, `TWTT = L/f_s - tx_delay` within floating precision;
- negative arrival lag is rejected;
- an arrival earlier than transmit by more than `0.5/f_s` is rejected;
- the returned method is `amplitude_peak`;
- supplied beam association and across-track angle are preserved;
- the detector does not emit a Cartesian sounding or classify its output as Truth;
- no API/UI path may advertise phase, threshold/noise, false/missed detection, hybrid, High Density, or multiple-detection generation as implemented unless corresponding authoritative Core capability is added.

## Validity / fidelity

This is a deterministic didactic/reference amplitude detector over an already-computed matched-filter correlation. It is suitable for teaching the signal-to-detection boundary and timing extraction. It is not a vendor bottom detector and does not model detection probability, acoustic scattering, electronics, stochastic noise, thresholding, phase-ramp estimation, footprint competition, or seabed-dependent bias.

## D5 relationship

PED-D5 remains a product-structure decision for Technical Lead. This contract does not create a second generic detectability model. Sonar-equation/SNR detectability concepts already belonging to PED-D3 should not be duplicated in PED-D9. PED-D9 owns the measurement-extraction boundary from processed receive signal to `BottomDetection`.

## References / traceability

This contract primarily binds existing HydroSIM authoritative behavior:

- `src/hydrosim/acquisition/bottom_detection.py`;
- `src/hydrosim/acquisition/waveform.py`;
- `docs/science/signal_waveform_contract.md`;
- `docs/science/d8_observation_state_contract.md`.

The strongest-matched-filter-peak rule is explicitly a HydroSIM reference/didactic detector, not a claim of universal MBES vendor practice. Higher-fidelity detection methods require their own recognized-source scientific contract before implementation.