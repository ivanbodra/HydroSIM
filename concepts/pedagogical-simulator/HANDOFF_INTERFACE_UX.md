# HydroSIM Pedagogical Simulator — Concept Handoff to Interface/UX

Status: **complete first-pass conceptual module**. This is a design sandbox handoff, not production UI and not scientific validation. Mock values, exaggerated motion, placeholder geometry, and illustrative visual responses are intentional where they help expose the interaction idea.

## Shared visual language

The learner should feel that HydroSIM is a virtual hydrographic laboratory rather than a configuration application. Each experience follows **INPUT → IMMEDIATE VISUAL RESPONSE → PHYSICAL INTUITION**. The phenomenon occupies most of the screen; controls are contextual and secondary. Shared devices include Baseline × Current ghost states, cause/effect strips, focus lenses, direct-manipulation intent, compact readouts, animated state transitions, and persistent links between upstream action and downstream visual consequence.

## 01 — Signal

**IDEA** — Turn the acoustic signal into a visible chain from transmission to returned echo and pulse-compression response.

**WHY** — Waveform concepts are difficult when shown only as equations or static plots. The learner should see CW/chirp, bandwidth, duration and compression as one evolving event.

**IMPORTANT INTERACTION** — Switch waveform and manipulate bandwidth/duration while transmit, receive and compressed response update together. Preserve a comparison state where useful.

**INPUTS expected** — waveform type; pulse duration; bandwidth; frequency range; repetition/timing controls; later optional matched-filter and spectrum controls.

**OUTPUTS visualized** — outgoing waveform; returned echo; time delay; spectrum/bandwidth cue; compressed peak; before/after pulse-width comparison.

Submodule concepts: **Waveform** uses CW × chirp switching; **Pulse** emphasizes envelope, duration and timing; **Spectrum** links waveform to frequency content; **Compression** uses ghost/reference response against current output.

## 02 — Beam

**IDEA** — Treat the beam as a volume of acoustic energy that becomes a visible illuminated region on the seabed.

**WHY** — Directivity, steering, beamwidth and sidelobes become intuitive when they are spatial rather than separate plots.

**IMPORTANT INTERACTION** — Manipulate steering, spread and sidelobe emphasis while the water-column beam volume and seabed footprint remain in one continuous scene.

**INPUTS expected** — steering; beamwidth; frequency/array-size concept controls; sidelobe emphasis; single/multibeam mode; later sector and dual-head presets.

**OUTPUTS visualized** — main lobe; sidelobes; beam axis; fan geometry; illuminated footprint; reference/nadir state; optional polar pattern inset.

Submodule concepts: **Beam Pattern** emphasizes main lobe/sidelobes; **Steering** foregrounds axis rotation; **Beamwidth** foregrounds angular spread; **Footprint** foregrounds the seabed response. Future extension can compare singlebeam, multibeam, multi-sector, dual-head and Mills-Cross layouts.

## 03 — Propagation

**IDEA** — Make the water column a manipulable medium through which the learner follows the same acoustic emission.

**WHY** — Environmental assumptions become easier to grasp when changes are seen as changes in a path rather than numbers in a table.

**IMPORTANT INTERACTION** — Shape an illustrative profile and environmental emphasis while multiple rays evolve through layers to the seabed; allow baseline/current profile comparison later.

**INPUTS expected** — sound-speed profile shape; range/depth scene controls; frequency emphasis; attenuation model selector later; seabed interaction presets.

**OUTPUTS visualized** — layered water column; profile lens; ray paths; range; illustrative energy/loss cue; seabed arrival region; return cue.

Submodule concepts: **Sound Speed** uses a draggable profile lens; **Refraction** turns the ray field into the main view; **Attenuation** adds an energy trail/readout; **Bottom Interaction** changes the contact/return visualization.

## 04 — Vessel & Sensors

**IDEA** — Present the vessel as a transparent connected instrument instead of a list of offsets.

**WHY** — Sensor geometry, lever arms and vertical references are highly spatial and should be read directly on the platform.

**IMPORTANT INTERACTION** — Select sensors and use an exploded/transparent view to trace relationships from GNSS and IMU through the vessel reference point to the acoustic head and water/reference levels.

**INPUTS expected** — vessel/sensor layout; GNSS, IMU and transducer positions; lever-arm emphasis; waterline/draft/reference-level controls; later mounting-angle concepts.

**OUTPUTS visualized** — vessel cutaway; GNSS/IMU/transducer nodes; VRP/origin; lever-arm lines/vectors; waterline; transducer level; vertical reference stack.

Submodule concepts: **Vessel** foregrounds the platform; **Transducer**, **GNSS** and **IMU** isolate one device while preserving context; **Lever Arms** turns relationships into vectors; **Vertical References** overlays waterline and reference planes.

## 05 — Motion

**IDEA** — Let the learner move the vessel and observe the entire measurement scene react, with a ghost state always available.

**WHY** — Roll, pitch, yaw and heave are best learned as movements and consequences, not as four unrelated numeric fields.

**IMPORTANT INTERACTION** — Direct manipulation is the target language: drag/rotate the vessel around highlighted axes. The current prototype uses sliders as a stepping stone. Baseline vessel, beam field and sounding trail remain visible.

**INPUTS expected** — roll; pitch; yaw; heave; motion amplitude/speed for demonstrations; later time delay and calibration-error presets.

**OUTPUTS visualized** — baseline ghost vessel; current platform; motion axes; beam geometry; sounding trail; heave ruler; optional motion timeline and error amplification.

Submodule concepts: **Heave**, **Roll**, **Pitch** and **Yaw** each foreground one gesture; **Motion Viewer** combines them; **Sounding Impact** shifts attention downstream to swath/soundings.

## 06 — Integrated Lab

**IDEA** — Transition from lessons to one virtual hydrographic survey where vessel, signal, beam, propagation, motion and soundings coexist.

**WHY** — The educational endpoint is not memorizing six modules; it is understanding how the phenomena interact during a sounding operation.

**IMPORTANT INTERACTION** — Run/pause a survey and use a left-hand phenomenon rail as a **focus lens**. Selecting Signal, Beam, Propagation or Motion does not leave the scene; it changes visual emphasis inside the same experiment. Baseline can remain overlaid.

**INPUTS expected** — scenario/preset; vessel configuration; signal and beam settings; environmental/profile settings; motion/error settings; survey path/speed; comparison state.

**OUTPUTS visualized** — vessel; water surface; acoustic fan/rays; bottom; sounding cloud; active phenomenon focus; causal timeline from transmit to reconstruct; baseline/current state; compact experiment inspector.

Submodule concepts: **Survey Setup** prepares a scenario visually; **Realtime View** is the main integrated scene; **Sounding Generation** foregrounds the observation cloud; **Uncertainty** can become a contribution overlay; **Comparison** manages ghost/reference states; **Experiment Presets** packages curated learning stories.

## Scenario language

Recommended conceptual presets for UX exploration:

- **From CW to chirp** — preserve the same scene and progressively reveal spectrum/compression.
- **Narrow vs broad beam** — compare beam volume and footprint with a ghost reference.
- **Bending through the column** — alter the profile while a frozen baseline ray remains visible.
- **Where is the measurement made?** — exploded vessel with selectable GNSS/IMU/transducer/VRP chain.
- **Roll the vessel** — exaggerated direct manipulation with baseline ghost and sounding trail.
- **One ping, end to end** — integrated timeline: transmit → propagate → interact → receive → reconstruct.
- **Run a virtual survey** — integrated scene where focus shifts between Signal, Beam, Propagation and Motion without leaving the experiment.

## Navigation concept

The System Map remains a discovery surface, but every module has a clear **Enter laboratory** concept action. Submodules should normally change focus/state inside the module laboratory rather than open an unrelated page. The Integrated Lab is the convergence point and deliberately feels spatially larger and more operational than earlier lessons.

## First-pass milestone reached

The sandbox now contains executable first-pass concepts for all six modules, a connected system map, Baseline × Current language, scenario concepts, automated runtime screenshots, and this handoff package. Further work should be driven by Interface/UX selection and feedback rather than expanding the sandbox indiscriminately.

## Recommended adoption principle

Interface/UX should freely select, simplify, combine or reject these concepts. Preserve the interaction intent when useful, not the exact component structure, dimensions, colors, wording, values or placeholder geometry used in the sandbox.
