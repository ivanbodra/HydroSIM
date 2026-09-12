"""Selected D7 TX/RX directional response tied to canonical echosounder geometry."""

from __future__ import annotations

from pydantic import ConfigDict, Field

from hydrosim.acquisition.beamwidth_pattern import gaussian_beamwidth_pattern
from hydrosim.app.echosounder_api import (
    D8EchosounderRequest,
    D8EchosounderResponse,
    prepare_d8_echosounder_response,
)
from hydrosim.app.array_api import D6PatternSeries
from pydantic import BaseModel


class D7SelectedDirectionalRequest(D8EchosounderRequest):
    """D7 geometry plus the beamwidth-only selected-response controls."""

    model_config = ConfigDict(extra="forbid")

    transmit_across_track_beamwidth_deg: float = Field(default=2.0, gt=0.0, lt=179.0)
    selected_mbes_beam_index: int = Field(default=0, ge=0)
    response_sample_count: int = Field(default=361, ge=33, le=1441)


class D7DirectionalPatternSeries(BaseModel):
    model_config = ConfigDict(frozen=True)

    angle_deg: tuple[float, ...]
    normalized_amplitude: tuple[float, ...]
    normalized_power: tuple[float, ...]


class D7SelectedDirectionalResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    geometry: D8EchosounderResponse
    selected_mbes_beam_index: int
    selected_steering_angle_deg: float
    selected_endpoint_across_track_m: float
    tx_one_way: D7DirectionalPatternSeries
    rx_one_way: D7DirectionalPatternSeries
    two_way: D7DirectionalPatternSeries
    metadata: dict[str, str | float | int]


def _series(samples) -> D7DirectionalPatternSeries:
    return D7DirectionalPatternSeries(
        angle_deg=tuple(float(sample.angle_deg) for sample in samples),
        normalized_amplitude=tuple(float(sample.normalized_amplitude) for sample in samples),
        normalized_power=tuple(float(sample.normalized_power) for sample in samples),
    )


def _angle_grid(request: D7SelectedDirectionalRequest) -> tuple[float, ...]:
    start = float(request.minimum_angle_deg)
    stop = float(request.maximum_angle_deg)
    count = request.response_sample_count
    step = (stop - start) / float(count - 1)
    return tuple(start + index * step for index in range(count))


def prepare_d7_selected_directional_response(
    request: D7SelectedDirectionalRequest,
) -> D7SelectedDirectionalResponse:
    """Return geometry and render-ready beamwidth-defined TX/RX/two-way responses."""

    geometry_fields = set(D8EchosounderRequest.model_fields)
    geometry_request = D8EchosounderRequest.model_validate(
        {key: value for key, value in request.model_dump().items() if key in geometry_fields}
    )
    geometry = prepare_d8_echosounder_response(geometry_request)
    index = request.selected_mbes_beam_index
    if index >= len(geometry.mbes.beams):
        raise ValueError("selected_mbes_beam_index is outside the canonical MBES beam plan")
    selected = geometry.mbes.beams[index]
    steering = float(selected.steering_angle_deg)
    angles = _angle_grid(request)

    tx_samples = gaussian_beamwidth_pattern(
        angles_deg=angles,
        steering_angle_deg=0.0,
        half_power_beamwidth_deg=request.transmit_across_track_beamwidth_deg,
    )
    rx_samples = gaussian_beamwidth_pattern(
        angles_deg=angles,
        steering_angle_deg=steering,
        half_power_beamwidth_deg=request.receive_across_track_beamwidth_deg,
    )
    two_way = D7DirectionalPatternSeries(
        angle_deg=angles,
        normalized_amplitude=tuple(
            float(tx.normalized_amplitude * rx.normalized_amplitude)
            for tx, rx in zip(tx_samples, rx_samples, strict=True)
        ),
        normalized_power=tuple(
            float(tx.normalized_power * rx.normalized_power)
            for tx, rx in zip(tx_samples, rx_samples, strict=True)
        ),
    )

    return D7SelectedDirectionalResponse(
        geometry=geometry,
        selected_mbes_beam_index=index,
        selected_steering_angle_deg=steering,
        selected_endpoint_across_track_m=float(selected.endpoint_across_track_m),
        tx_one_way=_series(tx_samples),
        rx_one_way=_series(rx_samples),
        two_way=two_way,
        metadata={
            "pattern_source": "beamwidth_gaussian_proxy",
            "pattern_scope": "phenomenological main-lobe proxy; not a physical array pattern",
            "angle_frame": "sensor-frame across-track; zero +Z; positive Port (-Y)",
            "tx_steering_deg": 0.0,
            "rx_steering": "selected canonical MBES beam",
            "one_way_power_convention": "normalized power; 0.5 at steering +/- HPBW/2",
            "one_way_amplitude_convention": "nonnegative sqrt(normalized power)",
            "two_way_convention": "B_2w=B_tx*B_rx; P_2w=P_tx*P_rx",
            "state_semantics": "Configured beamwidths/selection; Derived directional responses",
        },
    )
