# Mills Cross 2D Pattern Visualization

Version: 0.1.0

## Purpose

This visualization is a downstream didactic view of the scientific
`AngularPattern2DScan`. It does not recalculate acoustic propagation, steering,
array factors, element factors, or TX/RX frame transformations.

The three panels show the same angular grid and the same display scale:

1. TX — normalized one-way transmit response;
2. RX — normalized one-way receive response; and
3. TX × RX — normalized two-way response.

For the HydroSIM reference Mills Cross, the TX aperture is longitudinal and the RX
aperture is transverse. The expected visual signature is therefore a transmit
response narrow primarily in the along-track dimension, a receive response narrow
primarily in the across-track dimension, and a two-way response localized where the
two one-way responses overlap.

## Axes

The horizontal axis is across-track angle:

- positive: Port;
- negative: Starboard.

The vertical axis is along-track angle:

- positive: Forward;
- negative: Aft.

These signs are inherited from the scientific acquisition model and are not
redefined by the visualization layer.

## Display quantities

`prepare_mills_cross_pattern_panels(...)` supports three display scales:

- `db`: normalized power in dB, `10 log10(P)`;
- `power`: normalized linear power; and
- `amplitude`: normalized linear amplitude.

The default didactic view uses dB because it exposes main-lobe width, side lobes,
and relative suppression more clearly than a linear scale.

The default dB floor is -40 dB. Values below the selected floor are clipped only in
the plot-ready copy. The original `AngularPattern2DScan` is never modified.

## Rendering

`plot_mills_cross_pattern_panels(...)` uses Matplotlib from HydroSIM's optional
`visualization` dependency group. Matplotlib is imported only when the renderer is
called, keeping the scientific core and test environment independent of GUI or
plotting packages.

The renderer uses a common color scale for TX, RX, and two-way panels. This is
important didactically: independently autoscaling each panel could make weak and
strong responses appear visually equivalent.

## Scientific boundary

The figure is a normalized far-field narrowband angular-response visualization. It
is not a footprint on the seabed and does not yet include range, propagation loss,
bottom scattering, target strength, footprint integration, detection threshold,
waveform processing, or bathymetric reconstruction.
