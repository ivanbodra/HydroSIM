"""Didactic visualization of a 2D Mills-Cross angular response.

The scientific calculation is performed upstream by
``scan_mills_cross_two_way_pattern_2d``. This module only reshapes and renders
those results. It therefore must not change acoustic physics, steering, frame
conventions, or normalization.

The didactic three-panel view shows:

1. transmit one-way response;
2. receive one-way response; and
3. the two-way TX x RX response.

Across-track angle is the horizontal axis and along-track angle is the vertical
axis. Positive across-track is Port and positive along-track is Forward, exactly
as defined by the acquisition model.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import degrees
from typing import Literal

import numpy as np

from hydrosim.acquisition import AngularPattern2DScan

PatternScale = Literal["db", "power", "amplitude"]


@dataclass(frozen=True)
class MillsCrossPatternPanels:
    """Plot-ready TX, RX, and two-way matrices sharing one angular grid."""

    configuration_name: str
    across_track_angles_deg: np.ndarray
    along_track_angles_deg: np.ndarray
    transmit: np.ndarray
    receive: np.ndarray
    two_way: np.ndarray
    scale: PatternScale
    value_label: str
    minimum_value: float
    maximum_value: float


def _scale_power(power: np.ndarray, *, scale: PatternScale, floor_db: float) -> np.ndarray:
    if scale == "power":
        return power
    if scale == "amplitude":
        return np.sqrt(power)
    if scale != "db":
        raise ValueError("scale must be 'db', 'power', or 'amplitude'")
    if floor_db >= 0.0:
        raise ValueError("floor_db must be < 0")

    floor_power = 10.0 ** (floor_db / 10.0)
    return 10.0 * np.log10(np.maximum(power, floor_power))


def prepare_mills_cross_pattern_panels(
    scan: AngularPattern2DScan,
    *,
    scale: PatternScale = "db",
    floor_db: float = -40.0,
) -> MillsCrossPatternPanels:
    """Convert a 2D angular scan into three directly comparable matrices.

    The scan stores samples with along-track as the outer loop and across-track as
    the inner loop. The resulting matrices therefore have shape
    ``(n_along_track, n_across_track)``. TX and RX one-way power are recovered
    from their normalized amplitudes; the two-way power is already stored by the
    scientific scan.

    A common scale is used for all three panels. In dB mode the values represent
    normalized power, ``10 log10(P)``, clipped only for display at ``floor_db``.
    Clipping is a visualization operation and never modifies the scientific scan.
    """

    n_along = len(scan.along_track_angles_rad)
    n_across = len(scan.across_track_angles_rad)
    expected = n_along * n_across
    if len(scan.samples) != expected:
        raise ValueError(
            "scan sample count does not match the declared along/across angular grid"
        )

    tx_power = np.empty((n_along, n_across), dtype=float)
    rx_power = np.empty((n_along, n_across), dtype=float)
    two_way_power = np.empty((n_along, n_across), dtype=float)

    for index, sample in enumerate(scan.samples):
        i_along = index // n_across
        i_across = index % n_across
        tx_power[i_along, i_across] = float(sample.transmit_amplitude) ** 2
        rx_power[i_along, i_across] = float(sample.receive_amplitude) ** 2
        two_way_power[i_along, i_across] = float(sample.normalized_power)

    tx_values = _scale_power(tx_power, scale=scale, floor_db=floor_db)
    rx_values = _scale_power(rx_power, scale=scale, floor_db=floor_db)
    two_way_values = _scale_power(two_way_power, scale=scale, floor_db=floor_db)

    if scale == "db":
        label = "Normalized power (dB)"
        minimum = float(floor_db)
        maximum = 0.0
    elif scale == "power":
        label = "Normalized power"
        minimum = 0.0
        maximum = 1.0
    else:
        label = "Normalized amplitude"
        minimum = 0.0
        maximum = 1.0

    return MillsCrossPatternPanels(
        configuration_name=scan.configuration_name,
        across_track_angles_deg=np.array(
            [degrees(float(value)) for value in scan.across_track_angles_rad],
            dtype=float,
        ),
        along_track_angles_deg=np.array(
            [degrees(float(value)) for value in scan.along_track_angles_rad],
            dtype=float,
        ),
        transmit=tx_values,
        receive=rx_values,
        two_way=two_way_values,
        scale=scale,
        value_label=label,
        minimum_value=minimum,
        maximum_value=maximum,
    )


def plot_mills_cross_pattern_panels(
    scan: AngularPattern2DScan,
    *,
    scale: PatternScale = "db",
    floor_db: float = -40.0,
    cmap: str = "viridis",
    show_peak: bool = True,
):
    """Render the didactic TX / RX / two-way comparison with Matplotlib.

    Matplotlib is an optional HydroSIM visualization dependency and is imported
    only when this renderer is called. The returned ``(figure, axes)`` can be
    embedded by a future desktop or web UI without coupling the acoustic model to
    Matplotlib.
    """

    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:  # pragma: no cover - depends on optional environment
        raise ImportError(
            "Matplotlib is required for plot_mills_cross_pattern_panels; "
            "install HydroSIM with the 'visualization' extra"
        ) from exc

    panels = prepare_mills_cross_pattern_panels(scan, scale=scale, floor_db=floor_db)

    figure, axes = plt.subplots(1, 3, figsize=(13.5, 4.6), sharex=True, sharey=True)
    matrices = (panels.transmit, panels.receive, panels.two_way)
    titles = (
        "TX — transmit one-way",
        "RX — receive one-way",
        "TX × RX — two-way",
    )

    image = None
    for axis, matrix, title in zip(axes, matrices, titles, strict=True):
        image = axis.pcolormesh(
            panels.across_track_angles_deg,
            panels.along_track_angles_deg,
            matrix,
            shading="auto",
            cmap=cmap,
            vmin=panels.minimum_value,
            vmax=panels.maximum_value,
        )
        axis.set_title(title)
        axis.set_xlabel("Across-track angle (deg): +Port / -Starboard")
        axis.axhline(0.0, linewidth=0.6, alpha=0.5)
        axis.axvline(0.0, linewidth=0.6, alpha=0.5)

    axes[0].set_ylabel("Along-track angle (deg): +Forward / -Aft")

    if show_peak:
        axes[2].plot(
            degrees(float(scan.peak_across_track_angle_rad)),
            degrees(float(scan.peak_along_track_angle_rad)),
            marker="+",
            markersize=10,
            markeredgewidth=1.5,
        )

    figure.suptitle(
        f"Mills Cross angular response — {scan.configuration_name}\n"
        "Transmit × receive = two-way spatial selectivity"
    )
    if image is not None:
        figure.colorbar(image, ax=axes, label=panels.value_label, shrink=0.86)
    figure.subplots_adjust(left=0.07, right=0.91, bottom=0.18, top=0.80, wspace=0.12)
    return figure, axes
