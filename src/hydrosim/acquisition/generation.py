"""Generate acoustic acquisition events from dynamic vessel Truth."""

from __future__ import annotations

from math import floor

from hydrosim.timing import PingTiming, PoseTimeSeries, SimulationTime

from .models import AcquisitionPing, AcquisitionSequence, PingSchedule


def _trigger_seconds(schedule: PingSchedule) -> tuple[float, ...]:
    start = float(schedule.start_time.seconds)
    end = float(schedule.end_time.seconds)
    period = float(schedule.ping_period_seconds)

    if end == start:
        return (start,)

    count = floor((end - start) / period)
    values = [start + index * period for index in range(count + 1)]
    tolerance = 1e-12 * max(1.0, abs(start), abs(end), abs(period))
    if values and values[-1] > end + tolerance:
        values.pop()
    return tuple(values)


def generate_acquisition_sequence(
    poses: PoseTimeSeries,
    schedule: PingSchedule,
) -> AcquisitionSequence:
    """Create pings and sample Truth pose independently at Tx and Rx epochs.

    PoseTimeSeries deliberately rejects extrapolation. Therefore acquisition
    generation also fails explicitly when the motion stream does not support the
    complete Tx/Rx interval required by a scheduled ping.
    """

    pings: list[AcquisitionPing] = []
    for ping_index, trigger_seconds in enumerate(_trigger_seconds(schedule)):
        trigger = SimulationTime(seconds=trigger_seconds)
        tx = trigger.shifted(float(schedule.trigger_to_tx_seconds))
        rx_start = tx.shifted(float(schedule.receive_start_delay_seconds))
        rx_end = rx_start.shifted(float(schedule.receive_window_seconds))
        timing = PingTiming(
            trigger_time=trigger,
            tx_time=tx,
            rx_start_time=rx_start,
            rx_end_time=rx_end,
        )
        pings.append(
            AcquisitionPing(
                ping_index=ping_index,
                timing=timing,
                tx_pose=poses.pose_at(tx),
                rx_start_pose=poses.pose_at(rx_start),
                rx_end_pose=poses.pose_at(rx_end),
            )
        )

    return AcquisitionSequence(pings=tuple(pings))
