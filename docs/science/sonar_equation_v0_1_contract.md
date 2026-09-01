# Sonar Equation v0.1 Scientific Contract

Status: implementation-ready scientific contract for the first Didactic Explorer Sonar Equation / Acoustic Losses experience (D3).

## Teaching question

The first D3 experience answers one question:

> How do source level, propagation loss, seabed area backscatter, beam-pattern response and noise combine to determine received echo level and SNR?

It is not a calibrated manufacturer receiver model and does not yet model electronics, reverberation, detection probability, thresholding or bottom-type prediction.

## Reference active-sonar equation

For one seabed-area echo, HydroSIM v0.1 uses the level-domain decomposition

\[
RL = SL + G_{tx} - TL_{out} + BS - TL_{in} + G_{rx},
\]

where all additive terms are in dB and `RL` is the received echo level in dB re 1 µPa at the receiver.

The corresponding signal-to-noise ratio is

\[
SNR = RL - NL.
\]

For the reciprocal reference case with the same propagation model and path length on both legs,

\[
TL_{2w}=TL_{out}+TL_{in}=2TL_{1w},
\]

and therefore

\[
RL = SL + G_{tx} + BS + G_{rx} - TL_{2w}.
\]

The sign convention is explicit: source, backscatter and beam-pattern terms are added; propagation losses and noise reduce the resulting margin.

## Source level

`SL` is the acoustic source level referenced to 1 µPa at 1 m, in dB re 1 µPa @ 1 m.

For this first contract, `SL` is an explicit configured input. HydroSIM does not derive it from electrical transmit power, projector efficiency, cavitation limits or manufacturer settings.

`SL` is the boresight/reference source level for the selected transmit pattern. Off-axis transmit response is represented separately by `G_tx`.

## Beam-pattern level terms

`G_tx` and `G_rx` are **relative beam-pattern level corrections**, not classical directivity indices.

For a normalized pressure-amplitude beam response `|B|`,

\[
G_{rel}=20\log_{10}|B|.
\]

The normalized boresight value is 0 dB. Off-axis values are normally negative. This definition allows the existing HydroSIM normalized one-way TX/RX beam-pattern models to feed D3 without inventing an absolute array gain.

The v0.1 default is

\[
G_{tx}=G_{rx}=0\ \mathrm{dB},
\]

unless a traceable normalized beam-pattern value is supplied by the existing beam models.

Classical positive directivity index (`DI`) against isotropic noise is **not** part of this first D3 slice and must not be substituted silently for `G_rx`.

## Seabed area backscatter

D3 uses the existing `hydrosim.sonar_equation.backscatter.area_backscatter_term` result:

\[
BS=S_b+10\log_{10}(A/1\,\mathrm{m}^2).
\]

The implementation value to consume is:

`AreaBackscatterResult.backscatter_strength_db`.

`S_b` remains an explicit scattering-strength input. Frequency, grazing angle and sediment label must not be used to infer `S_b` in v0.1 unless a separately documented scattering model is introduced later.

## Transmission loss and range semantics

For each propagation leg, use the **acoustic path length** `r` along the propagation path, not Euclidean slant range unless the propagation model is homogeneous/straight and the two are equal.

The one-way spherical-spreading loss referenced to `r0 = 1 m` is

\[
TL_{spread}=20\log_{10}(r/r_0).
\]

The one-way absorption loss is

\[
TL_{abs}=\alpha\,r_{km},
\]

with `alpha` in dB/km and `r_km` the acoustic path length in km.

Thus

\[
TL_{1w}=TL_{spread}+TL_{abs}.
\]

The existing `src/hydrosim/acquisition/transmission_loss.py` implementation already follows this decomposition and should be reused.

If outbound and inbound paths differ, calculate them separately and add their dB losses. `2 * TL_1w` is valid only for the reciprocal equal-path reference case.

## Baseline frequency-dependent absorption model

For v0.1, select the simplified seawater absorption formula of **Ainslie & McColm (1998)**. It is sufficiently compact for a didactic frequency-loss experience while retaining explicit dependence on temperature, salinity, depth and pH.

With frequency `f` in kHz, temperature `T` in degrees Celsius, salinity `S` in practical salinity units / approximately ppt for this empirical formula, depth `D` in km, and absorption `alpha` in dB/km:

\[
f_1=0.78\sqrt{S/35}\,e^{T/26},
\]

\[
f_2=42e^{T/17},
\]

\[
\alpha =
0.106e^{(pH-8)/0.56}\frac{f_1f^2}{f_1^2+f^2}
+0.52\left(1+\frac{T}{43}\right)\frac{S}{35}e^{-D/6}\frac{f_2f^2}{f_2^2+f^2}
+0.00049e^{-(T/27+D/17)}f^2.
\]

The three terms represent boric-acid relaxation, magnesium-sulfate relaxation and pure-water/viscous contribution.

### Baseline environmental defaults

For the first interactive lesson, when the environmental controls are not exposed, use explicit configured defaults:

- temperature: 10 °C;
- salinity: 35;
- pH: 8.0;
- representative depth for absorption coefficient: 0 km for the simplest frequency-comparison baseline.

These are didactic defaults, not inferred observations.

### Validity boundary

Ainslie & McColm is an empirical seawater absorption approximation. The commonly stated environmental validity checks include approximately `-6 < T < 35 °C`, `7.7 < pH < 8.3`, `5 < S < 50`, and `0 < D < 7 km` under the reference conditions stated by the formulation. HydroSIM must validate inputs against the implemented model documentation and must not present values outside the documented domain as equally supported.

The D3 first slice need not expose all environmental variables as controls. Frequency is the principal didactic control; environmental quantities may remain configured context.

## Noise level

`NL` is the **band-integrated equivalent receiver noise level** in dB re 1 µPa for the same effective processing bandwidth represented by the echo level.

It is an explicit configured input in v0.1.

Do not accept a noise spectral density in dB re 1 µPa²/Hz as though it were already `NL`; spectral density requires bandwidth integration before use in this equation.

The first slice does not split ambient, self-noise and electronics noise.

## SNR and detection boundary

The first D3 output is

\[
SNR=RL-NL.
\]

No detection threshold, probability of detection, false-alarm probability or detection index is defined in v0.1. Therefore the UI should not label SNR as a probability or binary detection result.

A future documented detector may define a detection margin such as `SNR - threshold`; that is outside this contract.

## Required contribution breakdown

The D3 adapter should expose at least:

- `source_level_db_re_1upa_at_1m`;
- `tx_relative_beam_gain_db`;
- `outbound_spreading_loss_db`;
- `outbound_absorption_loss_db`;
- `outbound_total_loss_db`;
- `backscatter_strength_db` (existing area-integrated `BS` result);
- `inbound_spreading_loss_db`;
- `inbound_absorption_loss_db`;
- `inbound_total_loss_db`;
- `rx_relative_beam_gain_db`;
- `received_level_db_re_1upa`;
- `noise_level_db_re_1upa`;
- `snr_db`.

For a reciprocal case it may additionally expose `two_way_transmission_loss_db`.

## First-slice boundaries

Explicitly out of scope for D3 v0.1:

- prediction of `S_b` from sediment class;
- reverberation;
- calibrated transducer sensitivity / TVR / receive-voltage chain;
- electronics and quantization;
- classical array directivity index unless separately derived and documented;
- stochastic noise realization;
- frequency-dependent bottom scattering;
- uncertainty propagation;
- detection probability and threshold models;
- multipath and non-reciprocal propagation.

## Implementation invariants

1. Increasing either one-way path length with all other inputs fixed must not increase `RL`.
2. Increasing absorption coefficient with range fixed must reduce `RL`.
3. In the reciprocal reference case, `TL_2w = 2 * TL_1w` within numerical tolerance.
4. With normalized boresight beam responses, `G_tx = G_rx = 0 dB`.
5. A lower normalized beam amplitude must not increase `G_rel`.
6. `SNR = RL - NL` exactly in the level-domain model.
7. The D3 adapter must consume `AreaBackscatterResult.backscatter_strength_db`; it must not rederive or reinterpret sediment type.

## References

Ainslie, M. A., & McColm, J. G. (1998). *A simplified formula for viscous and chemical absorption in sea water*. Journal of the Acoustical Society of America, 103(3), 1671–1672. DOI: 10.1121/1.421258.

Francois, R. E., & Garrison, G. R. (1982). *Sound absorption based on ocean measurements*. Journal of the Acoustical Society of America. The Ainslie–McColm simplification is based on the established relaxation-process treatment represented by this work.

Waite, A. D. (2002). *Sonar for Practising Engineers*, 3rd ed. Wiley. General level-domain active-sonar equation and source/propagation terminology.

HydroSIM implementation sources:
- `src/hydrosim/acquisition/transmission_loss.py`
- `src/hydrosim/sonar_equation/backscatter.py`
