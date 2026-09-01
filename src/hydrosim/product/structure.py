"""Canonical product structure tied to existing HydroSIM scientific capabilities.

This module is intentionally presentation-agnostic. It defines product modules,
submodules, user-facing objects/items, and their scientific/application bindings.
It does not invent missing science: when a capability is not yet available, the
item remains present with an explicit ``required_capability`` and no binding.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScientificBinding:
    """Reference to an existing HydroSIM implementation used by a product item."""

    path: str
    purpose: str


@dataclass(frozen=True)
class ProductItem:
    """Smallest countable product object/interaction/output."""

    id: str
    name: str
    bindings: tuple[ScientificBinding, ...] = ()
    required_capability: str | None = None
    optional: bool = False


@dataclass(frozen=True)
class ProductSubmodule:
    """Meaningful functional area composed of product items."""

    id: str
    name: str
    items: tuple[ProductItem, ...]


@dataclass(frozen=True)
class ProductModule:
    """Top-level HydroSIM product module."""

    id: str
    name: str
    submodules: tuple[ProductSubmodule, ...]


def _b(path: str, purpose: str) -> ScientificBinding:
    return ScientificBinding(path=path, purpose=purpose)


def _i(
    id_: str,
    name: str,
    *bindings: ScientificBinding,
    required: str | None = None,
    optional: bool = False,
) -> ProductItem:
    return ProductItem(id=id_, name=name, bindings=tuple(bindings), required_capability=required, optional=optional)


DIDACTIC_EXPLORER = ProductModule(
    id="didactic-explorer",
    name="Didactic Explorer",
    submodules=(
        ProductSubmodule(
            id="signal",
            name="Signal",
            items=(
                _i("cw-waveform", "CW waveform", _b("hydrosim.visualization.signal_explorer", "signal state")),
                _i("lfm-waveform", "LFM/chirp waveform", _b("hydrosim.visualization.signal_explorer", "LFM signal state")),
                _i("pulse-duration", "Pulse duration", _b("hydrosim.visualization.signal_explorer.SignalExplorerControls", "configured duration")),
                _i("bandwidth", "LFM bandwidth", _b("hydrosim.visualization.signal_explorer.SignalExplorerControls", "configured bandwidth")),
                _i("phase-evolution", "Phase evolution", _b("hydrosim.visualization.signal_explorer", "derived phase")),
                _i("matched-filter", "Matched-filter/autocorrelation response", _b("hydrosim.visualization.signal_explorer", "pulse-compression response")),
                _i("baseline-current", "Baseline × Current comparison", _b("hydrosim.app.signal_compare", "pedagogical comparison state")),
                _i("quantitative-readout", "T/B/TB/1-B quantitative state", _b("hydrosim.visualization.signal_explorer", "derived signal quantities")),
                _i("frequency-wavelength", "Frequency/wavelength consequence", required="canonical carrier-frequency/wavelength lesson adapter"),
                _i("reset", "Reset state"),
            ),
        ),
        ProductSubmodule(
            id="beam-pattern",
            name="Beam Pattern",
            items=(
                _i("frequency", "Frequency", _b("hydrosim.visualization.beam_explorer.BeamExplorerControls", "configured acoustic frequency")),
                _i("wavelength", "Wavelength", _b("hydrosim.visualization.beam_explorer", "derived wavelength")),
                _i("element-count", "Element count / aperture", _b("hydrosim.visualization.beam_explorer.BeamExplorerControls", "array aperture input")),
                _i("element-spacing", "Element spacing", _b("hydrosim.acquisition.array_factor", "array sampling geometry")),
                _i("tx-rx-pattern", "TX/RX beam pattern", _b("hydrosim.acquisition.beam_pattern", "beam pattern"), _b("hydrosim.geometry.mills_cross", "TX/RX geometry")),
                _i("beamwidth", "-3 dB beamwidth", _b("hydrosim.visualization.beam_explorer", "beamwidth output")),
                _i("side-lobes", "Side-lobe response", _b("hydrosim.acquisition.array_factor", "array sidelobes")),
                _i("footprint", "Seafloor footprint", _b("hydrosim.acquisition.footprint", "beam-limited footprint")),
                _i("beam-steering", "Beam steering", _b("hydrosim.acquisition.beamforming", "steered response")),
                _i("weighting", "Array weighting/shading", required="user-facing weighting adapter", optional=True),
                _i("reset", "Reset state"),
            ),
        ),
        ProductSubmodule(
            id="sonar-equation",
            name="Sonar Equation / Acoustic Losses",
            items=(
                _i("source-level", "Source level", required="source-level model/adapter"),
                _i("spreading-loss", "Spreading loss", required="transmission-loss spreading model"),
                _i("absorption", "Absorption", required="referenced absorption model"),
                _i("frequency", "Frequency", required="acoustic-loss control adapter"),
                _i("range", "Range", required="acoustic-loss control adapter"),
                _i("transmission-loss", "Transmission loss", required="transmission-loss model"),
                _i("backscatter", "Target strength / backscatter", _b("hydrosim.sonar_equation.backscatter", "backscatter terms")),
                _i("noise", "Noise level", required="noise model"),
                _i("directivity", "Directivity / array gain", _b("hydrosim.acquisition.beam_pattern", "array directivity")),
                _i("received-level", "Received level / SNR / detection margin", required="integrated sonar-equation adapter"),
                _i("contribution-breakdown", "Equation contribution breakdown", required="integrated sonar-equation adapter"),
                _i("reset", "Reset state"),
            ),
        ),
        ProductSubmodule(
            id="sound-velocity-refraction",
            name="Sound Velocity & Refraction",
            items=(
                _i("truth-svp", "Truth SVP", _b("hydrosim.visualization.layered_svp_explorer", "truth profile")),
                _i("processing-svp", "Processing SVP", _b("hydrosim.visualization.propagation_explorer", "processing profile")),
                _i("ray-tracing", "Ray tracing", _b("hydrosim.acquisition.layered_propagation", "piecewise-layer ray propagation")),
                _i("refraction", "Snell/refraction consequence", _b("hydrosim.acquisition.layered_propagation", "refraction geometry")),
                _i("truth-intersection", "Truth bottom intersection", _b("hydrosim.visualization.layered_svp_explorer", "truth sounding")),
                _i("reconstructed-sounding", "Reconstructed sounding", _b("hydrosim.visualization.propagation_explorer", "processing reconstruction")),
                _i("truth-processing", "Truth × Processing comparison", _b("hydrosim.visualization.propagation_explorer", "error isolation")),
                _i("temperature-salinity-pressure", "Temperature / salinity / pressure inputs", required="environmental sound-speed model", optional=True),
                _i("profile-extension", "Explicit profile extension mode", required="SVP extension policy adapter", optional=True),
                _i("reset", "Reset state"),
            ),
        ),
        ProductSubmodule(
            id="vessel-sensors-vertical-references",
            name="Vessel / Sensors / Vertical References",
            items=(
                _i("vrp", "Vessel reference point", _b("hydrosim.app.vessel_vertical_reference", "VRP-centered geometry")),
                _i("gnss", "GNSS antenna", _b("hydrosim.app.vessel_vertical_reference", "GNSS lever arm")),
                _i("imu", "IMU/MRU", _b("hydrosim.app.vessel_vertical_reference", "IMU lever arm")),
                _i("transducer", "Transducer", _b("hydrosim.app.vessel_vertical_reference", "transducer lever arm")),
                _i("lever-arms", "X/Y/Z lever arms", _b("hydrosim.geometry.transforms", "rigid-body lever-arm transform")),
                _i("waterline", "Configured waterline", _b("hydrosim.app.vessel_vertical_reference", "waterline relative to VRP")),
                _i("transducer-depth", "Transducer immersion", _b("hydrosim.app.vessel_vertical_reference", "depth below waterline")),
                _i("water-level", "Hydrographic water level", _b("hydrosim.app.vessel_vertical_reference", "datum-referenced water level kept separate")),
                _i("static-draft", "Static draft", required="explicit static-draft adapter"),
                _i("vertical-datum-link", "Vertical datum relation", required="validated datum-to-vessel relation", optional=True),
                _i("reset", "Reset state"),
            ),
        ),
        ProductSubmodule(
            id="motion",
            name="Motion",
            items=(
                _i("roll", "Roll", _b("hydrosim.app.motion_lesson.MotionLessonControls", "configured roll")),
                _i("pitch", "Pitch", _b("hydrosim.app.motion_lesson.MotionLessonControls", "configured pitch")),
                _i("yaw", "Yaw deviation", _b("hydrosim.app.motion_lesson.MotionLessonControls", "configured yaw deviation")),
                _i("heave", "Heave", _b("hydrosim.app.motion_lesson.MotionLessonControls", "hydrographic heave positive Up")),
                _i("vessel-pose", "Vessel pose consequence", _b("hydrosim.motion.models.VesselMotionModel", "pose generation")),
                _i("transducer-position", "Transducer position consequence", _b("hydrosim.app.motion_lesson.MotionLessonSnapshot", "lever-arm consequence")),
                _i("beam-direction", "Beam orientation consequence", _b("hydrosim.app.motion_lesson.MotionLessonSnapshot", "beam direction in navigation frame")),
                _i("combined-motion", "Combined motion state", _b("hydrosim.motion.models.VesselMotionModel", "combined deterministic motion")),
                _i("latency", "Latency/time delay", _b("hydrosim.timing", "simulation timing"), required="motion-to-observation latency adapter"),
                _i("compensation", "Compensation on/off comparison", required="motion compensation processing adapter", optional=True),
                _i("reset", "Reset state"),
            ),
        ),
        ProductSubmodule(
            id="sonar-systems-geometry",
            name="Sonar Systems & Geometry",
            items=(
                _i("sbes", "SBES representation", required="SBES system geometry adapter"),
                _i("mbes", "MBES representation", _b("hydrosim.geometry.beams", "beam geometry")),
                _i("mills-cross", "Mills Cross TX/RX geometry", _b("hydrosim.geometry.mills_cross", "orthogonal TX/RX geometry")),
                _i("beam-fan", "Beam fan / swath", _b("hydrosim.geometry.beams", "beam directions")),
                _i("beam-spacing", "Beam count / spacing", _b("hydrosim.acquisition.beam_spacing", "beam spacing")),
                _i("multisector", "Multisector transmission", required="multisector system adapter"),
                _i("dual-head", "Dual-head geometry", required="dual-head system adapter"),
                _i("steering", "Steering/orientation context", _b("hydrosim.acquisition.beamforming", "beam steering")),
                _i("reset", "Reset state"),
            ),
        ),
        ProductSubmodule(
            id="sounding-formation",
            name="Sounding Formation / Detection Chain",
            items=(
                _i("transmit", "Transmit event", _b("hydrosim.acquisition.generation", "acquisition generation")),
                _i("propagation", "Pulse propagation", _b("hydrosim.acquisition.layered_propagation", "propagation")),
                _i("seabed-interaction", "Seabed interaction", _b("hydrosim.sonar_equation.backscatter", "backscatter")),
                _i("receive", "Receive event", _b("hydrosim.acquisition.element_signals", "received element signals")),
                _i("bottom-detection", "Bottom detection", _b("hydrosim.acquisition.bottom_detection", "detection")),
                _i("twtt-range", "TWTT / range formation", _b("hydrosim.acquisition", "range/acquisition state")),
                _i("beam-angle", "Beam-angle association", _b("hydrosim.geometry.beams", "beam direction")),
                _i("pose-association", "Position/attitude association", _b("hydrosim.motion.models", "vessel pose"), _b("hydrosim.timing", "time association")),
                _i("reconstruction", "Sounding reconstruction", _b("hydrosim.geometry.soundings", "sounding geometry")),
                _i("truth-observed", "Truth × Observed sounding", required="integrated acquisition observation state"),
                _i("reset", "Reset state"),
            ),
        ),
    ),
)


PATCH_TEST = ProductModule(
    id="patch-test",
    name="Patch Test",
    submodules=tuple(
        ProductSubmodule(id=id_, name=name, items=items)
        for id_, name, items in (
            (
                "roll-calibration",
                "Roll Calibration",
                (
                    _i("scenario", "Reciprocal-line scenario", _b("hydrosim.scenarios.roll_offset", "roll-offset scenario")),
                    _i("hidden-bias", "Hidden/configurable roll bias", _b("hydrosim.scenarios.roll_offset", "roll offset")),
                    _i("swath-output", "Swath discrepancy output", _b("hydrosim.geometry.soundings", "sounding geometry")),
                    _i("adjustment", "Roll adjustment"),
                    _i("estimated", "Estimated roll"),
                    _i("truth-estimated", "Truth × Estimated comparison"),
                    _i("run-reset-check", "Run / reset / check solution"),
                ),
            ),
            ("pitch-calibration", "Pitch Calibration", (_i("scenario", "Pitch calibration scenario", required="pitch patch-test scenario"), _i("bias", "Pitch bias"), _i("displacement", "Along-track displacement"), _i("estimate", "Estimated pitch"), _i("truth-estimated", "Truth × Estimated comparison"), _i("run-reset-check", "Run / reset / check solution"))),
            ("yaw-calibration", "Yaw Calibration", (_i("scenario", "Yaw calibration scenario", required="yaw patch-test scenario"), _i("bias", "Yaw bias"), _i("displacement", "Horizontal consequence"), _i("estimate", "Estimated yaw"), _i("truth-estimated", "Truth × Estimated comparison"), _i("run-reset-check", "Run / reset / check solution"))),
            ("latency-calibration", "Latency Calibration", (_i("scenario", "Latency calibration scenario", required="latency patch-test scenario"), _i("speed", "Vessel speed", _b("hydrosim.motion.models.StraightLineTrajectory", "trajectory speed")), _i("bias", "Latency bias", _b("hydrosim.timing", "time model")), _i("displacement", "Along-track displacement"), _i("estimate", "Estimated latency"), _i("truth-estimated", "Truth × Estimated comparison"), _i("run-reset-check", "Run / reset / check solution"))),
            ("integrated-exercise", "Integrated Patch Test Exercise", (_i("setup", "Vessel/sensor setup", _b("hydrosim.geometry", "vessel/sensor geometry")), _i("line-plan", "Calibration-line plan", required="survey-line planner"), _i("acquisition", "Acquisition sequence", _b("hydrosim.acquisition", "acquisition core")), _i("biases", "Selectable/hidden biases"), _i("solutions", "Individual calibration solutions"), _i("corrected", "Combined corrected result"), _i("before-after", "Before/after comparison"), _i("new-scenario", "Reset/new scenario"), _i("report", "Final result/report"))),
        )
    ),
)


SURVEY_SIMULATOR = ProductModule(
    id="survey-simulator",
    name="Survey Simulator",
    submodules=(
        ProductSubmodule("vessel-configuration", "Vessel Configuration", (_i("vrp", "VRP", _b("hydrosim.geometry.models", "reference geometry")), _i("gnss-imu", "GNSS / IMU installation", _b("hydrosim.geometry.transforms", "lever arms")), _i("sonar-installation", "Sonar/transducer installation", _b("hydrosim.geometry", "rigid-body geometry")), _i("waterline-draft", "Waterline / draft", _b("hydrosim.app.vessel_vertical_reference", "vertical references")), _i("save-load-reset", "Save / load / reset configuration", required="scenario persistence"))),
        ProductSubmodule("sonar-configuration", "Sonar Configuration", (_i("system-type", "SBES/MBES selection", required="sonar system configuration model"), _i("frequency", "Frequency", _b("hydrosim.acquisition", "acoustic acquisition")), _i("pulse", "Pulse type/duration/bandwidth", _b("hydrosim.visualization.signal_explorer", "signal controls")), _i("beam-geometry", "Beam geometry", _b("hydrosim.geometry.beams", "beam geometry")), _i("steering-sectors", "Steering/sectors", _b("hydrosim.acquisition.beamforming", "steering"), required="sector configuration adapter"), _i("ping-rate", "Ping rate", _b("hydrosim.timing", "timing")), _i("range-swath", "Range/swath limits", required="survey acquisition configuration"), _i("summary-reset", "Configuration summary/reset"))),
        ProductSubmodule("environment-seabed", "Environment & Seabed", (_i("bathymetry", "Bathymetric surface", _b("hydrosim.geometry.terrain", "seafloor geometry")), _i("svp", "Sound-speed profile", _b("hydrosim.acquisition.layered_propagation", "propagation environment")), _i("water-level", "Water level", _b("hydrosim.app.vessel_vertical_reference", "hydrographic water level")), _i("acoustic-seabed", "Acoustic seabed properties", _b("hydrosim.sonar_equation.backscatter", "backscatter")), _i("presets-load-reset", "Presets/load/reset", required="environment scenario persistence"))),
        ProductSubmodule("survey-planning", "Survey Planning", (_i("area", "Survey area", required="survey area model"), _i("lines", "Survey lines", required="survey-line planner"), _i("spacing-heading", "Line spacing/heading", required="survey-line planner"), _i("speed", "Vessel speed", _b("hydrosim.motion.models.StraightLineTrajectory", "trajectory")), _i("trajectory", "Planned trajectory", _b("hydrosim.motion.models", "trajectory")), _i("coverage", "Predicted swath/coverage", _b("hydrosim.geometry.beams", "beam geometry"), required="coverage planner"))),
        ProductSubmodule("survey-execution", "Survey Execution / Acquisition", (_i("controls", "Start/pause/stop/step/reset", _b("hydrosim.timing", "simulation time")), _i("trajectory", "Vessel trajectory", _b("hydrosim.motion.models", "vessel motion")), _i("motion", "Motion state", _b("hydrosim.motion", "motion")), _i("ping", "Ping emission", _b("hydrosim.acquisition.generation", "acquisition generation")), _i("swath", "Swath/sounding accumulation", _b("hydrosim.geometry.soundings", "soundings")), _i("progress-time", "Line/coverage/time progress", required="survey execution controller"))),
        ProductSubmodule("sensors-errors", "Sensors & Error Injection", (_i("gnss", "GNSS observations/errors", required="GNSS observation model"), _i("attitude", "Attitude observations/errors", _b("hydrosim.motion", "truth attitude"), required="attitude observation error model"), _i("heave-heading", "Heave/heading observations", _b("hydrosim.motion", "truth motion"), required="sensor observation adapter"), _i("latency", "Latency", _b("hydrosim.timing", "timing")), _i("lever-arm-bias", "Lever-arm biases", _b("hydrosim.geometry.transforms", "lever arms")), _i("water-level-error", "Water-level error", required="water-level observation error model"), _i("sv-error", "Sound-speed error", _b("hydrosim.visualization.propagation_explorer", "processing SVP mismatch")), _i("truth-observed", "Truth × Observed views", required="observation-state integration"))),
        ProductSubmodule("synthetic-observations", "Synthetic Observations", (_i("timestamp", "Timestamp", _b("hydrosim.timing", "time")), _i("twtt-range", "TWTT/range", _b("hydrosim.acquisition", "acquisition observations")), _i("beam-angle", "Beam angle", _b("hydrosim.geometry.beams", "beam geometry")), _i("position-attitude", "Position/attitude/heave/heading", _b("hydrosim.motion", "truth pose")), _i("sound-speed", "Sound speed", _b("hydrosim.acquisition.layered_propagation", "sound speed")), _i("water-level", "Water level", _b("hydrosim.app.vessel_vertical_reference", "water level")), _i("identifiers", "Ping/beam identifiers", required="observation record schema"), _i("truth-observed", "Truth/Observed state", required="observation record schema"), _i("inspection", "Table/time-series inspection", required="observation inspection adapter"))),
        ProductSubmodule("processing-reconstruction", "Processing & Reconstruction", (_i("positioning", "Apply positioning", required="processing pipeline"), _i("attitude-heave", "Apply attitude/heave", _b("hydrosim.geometry.transforms", "rigid-body transforms")), _i("lever-arms", "Apply lever arms", _b("hydrosim.geometry.transforms", "lever-arm correction")), _i("latency", "Apply latency", _b("hydrosim.timing", "timing"), required="processing latency correction"), _i("ray-tracing", "Sound-speed correction/ray tracing", _b("hydrosim.acquisition.layered_propagation", "ray tracing")), _i("water-level", "Vertical/water-level correction", required="vertical processing adapter"), _i("georeferencing", "Georeferencing", _b("hydrosim.geometry.soundings", "sounding geometry")), _i("reconstruction", "Sounding reconstruction", _b("hydrosim.geometry.soundings", "reconstruction")), _i("run-reset-inspect", "Run/reset/intermediate inspection", required="processing controller"))),
        ProductSubmodule("qc-analysis", "QC & Analysis", (_i("plan-swath", "Plan/swath view", required="QC presentation adapter"), _i("cross-section", "Cross-section", required="QC section adapter"), _i("sounding-view", "Sounding view", _b("hydrosim.geometry.soundings", "soundings")), _i("surface", "Bathymetric surface", _b("hydrosim.geometry.terrain", "terrain")), _i("difference", "Difference/error surface", required="QC difference computation"), _i("coverage", "Coverage", required="coverage analysis"), _i("statistics", "Statistics", required="QC statistics"), _i("uncertainty", "Uncertainty/quality outputs", required="uncertainty model", optional=True), _i("truth-processed", "Truth × Processed comparison", required="integrated truth/processed analysis"))),
        ProductSubmodule("export-scenarios", "Export & Scenario Management", (_i("save-load", "Save/load scenario", required="scenario persistence"), _i("duplicate-reset", "Duplicate/reset scenario", required="scenario persistence"), _i("export-observations", "Export synthetic observations", required="observation exporter"), _i("export-soundings", "Export processed soundings", required="sounding exporter"), _i("metadata", "Metadata/configuration export", required="metadata exporter"), _i("hydrographic-formats", "Hydrographic/raw-like formats", required="format-specific exporters", optional=True), _i("validation", "Export status/validation", required="export validation"))),
    ),
)


HYDROSIM_PRODUCT: tuple[ProductModule, ...] = (
    DIDACTIC_EXPLORER,
    PATCH_TEST,
    SURVEY_SIMULATOR,
)


def find_submodule(submodule_id: str) -> ProductSubmodule:
    """Return one canonical submodule by identifier."""

    for module in HYDROSIM_PRODUCT:
        for submodule in module.submodules:
            if submodule.id == submodule_id:
                return submodule
    raise KeyError(submodule_id)
