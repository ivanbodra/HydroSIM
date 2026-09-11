# D13 — Timing, Synchronization & Latency

Status: **Mapped**

**Decision:** `KEEP + REFINE + ADD CLOCK-SYNCHRONIZATION EXPERIENCE`  
**Current:** `web/pedagogical-explorer/src/TimingLab.tsx`  
**Scientific/API path:** `src/hydrosim/app/timing_api.py`  
**Historical implementation alias:** current Python classes still use `D14*`; pedagogical numbering in this directory is authoritative.

## Purpose
Teach why hydrographic observations must be associated with the **correct physical epoch**. The learner must distinguish the time when a quantity was measured from the later time when its data become available to the acquisition system, understand how update cadence and latency determine which observation can be used for a sonar event, and see how a timing mismatch becomes a spatial/geometric error when the platform is moving.

D13 must explicitly distinguish three concepts:

```text
SYNCHRONIZATION
  = clocks / timestamps refer to the intended common time basis

LATENCY
  = delay between measurement/sample epoch and data availability

SAMPLE AGE
  = TX/event epoch - epoch represented by the sample actually used
```

They are related but not interchangeable.

## Dominant discovery

```text
physical state at measurement epoch
  -> sample / timestamp
  -> transport + processing latency
  -> sample becomes available
  -> acquisition system associates an available sample with sonar event
  -> sample age / timing mismatch
  -> moving platform means wrong state is applied to the event
  -> spatial / angular sounding consequence
```

The core learning result is that **a sensor value can be numerically correct for its own measurement time and still be wrong for the sonar event if it is associated with the wrong time**.

## Inputs

### Primary — guided progression
1. **selected sensor stream** — position first, then attitude;
2. **sensor update rate** `f_update`;
3. **stream latency** `L`;
4. **vessel speed** for the position experiment;
5. **sonar event / association epoch**, initially TX time;
6. **stream start / first-sample epoch** so cadence can be made visible.

### Ping timing inputs
Introduce after the basic sample/availability distinction:
- trigger epoch;
- TX delay / TX epoch;
- RX start delay;
- receive-window duration.

These establish that trigger, transmit and receive are different events. For multisector cases, D9 may provide more than one TX epoch.

### Synchronization-specific inputs — required next scientific slice
The title includes synchronization, so the mature D13 must also support a validated clock model with at least:
- **clock/time offset** `Δt_clock` between one stream and the common time basis;
- synchronization mode / common reference such as ideal common time, 1PPS-disciplined or equivalent registered mode.

Advanced only when a Scientific-Core model exists:
- clock drift/skew;
- timestamp quantization;
- jitter / variable latency;
- interpolation/association policy;
- multiple TX-sector epochs from D9.

Do not expose these as decorative sliders before the Scientific Core defines their semantics.

## Outputs / visual response

### A. Event timeline
Use one fixed/shared time axis and show at minimum:
- trigger;
- TX;
- RX start;
- RX end;
- sensor sample epoch;
- sensor availability epoch.

The distinction between **sample time** and **available time** must be visually unmistakable.

### B. Periodic stream / cadence view
For each selected stream show:
- update rate `f_update`;
- nominal period `T_update = 1/f_update`;
- periodic sample ticks;
- each sample's availability shifted by its latency;
- the sample that is actually eligible at the selected sonar epoch.

The learner should be able to see why a higher update rate can reduce discretization/sample age while latency can still keep the newest sample unavailable.

### C. Causal association view
Show the active association rule explicitly. The current Scientific Core uses:

```text
latest sample with availability_time <= tx_time
```

For the retained sample show:
- measurement/sample epoch;
- availability epoch;
- selected sonar/TX epoch;
- sample age;
- whether any sample is causally available.

### D. Position timing consequence
For the controlled constant-speed position experiment, show:
- vessel/Truth position at the retained sample epoch;
- vessel/Truth position at TX;
- signed along-track difference on a fixed physical scale.

The current core-derived simplified consequence is equivalent to the constant-speed relationship

```text
Δx = v · (t_sample - t_TX)
```

but it must be labelled as a **position-state timing consequence**, not a complete sounding error.

### E. Attitude timing consequence
Initially show attitude **sample age only**. Do not convert milliseconds to metres without a registered angular-rate + beam/seafloor geometry model.

Recommended next slice: with D11 motion available, show Truth attitude at sample time versus Truth attitude at sonar epoch and the resulting angular difference, then let D14 own the full sounding displacement.

### F. Synchronization / clock view
Once `Δt_clock` is implemented, show two aligned time rulers:
- common/Truth time;
- sensor-reported time.

An offset should move timestamp labels/association without changing the physical event itself. This must visibly differ from latency, which moves **availability** rather than the original measurement epoch.

## Interaction sequence

1. **One event, one perfectly available sample.** Start with a position stream on an ideal common time basis, high enough update rate and zero latency. Sample epoch, availability epoch and TX association are easy to read.
2. **Update rate only.** Keep latency zero and reduce the position update rate. The retained sample becomes older in discrete steps even though it is available immediately. Show `Hz -> period -> sample age`.
3. **Latency only.** Restore the rate and increase latency. Samples keep their measurement epochs but become available later; the most recent physical observation may no longer be causally usable at TX.
4. **Rate versus latency.** Construct two configurations with similar sample age for different reasons. Ask the learner to identify whether the cause is coarse sampling or delayed availability.
5. **Move the platform.** Increase vessel speed while keeping the same timing mismatch. The sample age stays the same while the along-track position consequence grows. This is the clearest bridge from time error to spatial error.
6. **No sample available.** Move stream start/latency so no sample has reached the PU by TX. The system must report `unavailable`, not silently use a future observation.
7. **Attitude stream.** Compare high-rate attitude and lower-rate position streams. Show different cadence/latency/age but do not invent a metre consequence for attitude.
8. **Ping timing.** Reveal trigger, TX, RX start and RX end. Move TX delay and receive window to show that the selected association epoch is a defined sonar event, not just “the ping somewhere”.
9. **Multiple TX epochs.** Advanced: import two or more sector TX epochs from D9. The same sensor stream can have a different available/latest sample and age at each sector epoch. Preserve sector identity.
10. **Clock synchronization.** After the core supports clock offset, keep physical sample and latency fixed while changing only `Δt_clock`. Show the timestamp/association error separately from latency. Then restore common timing (e.g. ideal/1PPS-disciplined case).
11. **Diagnosis challenge.** Present one case dominated by low update rate, one by latency and one by clock offset. The learner identifies which timing mechanism caused the wrong state to be associated with the sonar event.

## Operational intuition / trade-offs

| Timing factor | What changes | What the learner should retain |
|---|---|---|
| Higher update rate | shorter nominal sample interval | usually reduces temporal discretization/age, but does not eliminate latency or clock error |
| Lower update rate | samples farther apart | the latest available state may be substantially older even with zero transport latency |
| Higher fixed latency | availability moves later while measurement epoch is unchanged | newest measurements may not be causally available when the sonar event occurs |
| Clock offset / poor synchronization | reported time differs from common event time | a physically correct observation can be associated with the wrong epoch even if it arrived quickly |
| Greater vessel speed | larger distance travelled during a given `Δt` | the same timing mismatch produces a larger position consequence |
| Faster attitude dynamics | larger orientation change during a given `Δt` | attitude timing sensitivity depends on angular motion and downstream beam geometry |
| 1PPS / common disciplined timing | aligns system clocks to a common reference in supported architectures | synchronization reduces clock-reference mismatch but does not by itself remove sensor/processing latency |
| Interpolation | can estimate state at the desired epoch when suitable bracketing observations exist | policy/model must be explicit; interpolation is not a substitute for good timestamps or valid samples |

Desired learner message: **hydrographic integration is a four-dimensional problem: every measurement needs the right value, place/orientation and time. Update rate determines when measurements exist, latency determines when they become available, and synchronization determines whether their timestamps refer to the same clock.**

## Scientific guardrails

- Keep **measurement epoch**, **timestamp**, **availability epoch**, **association epoch** and **sample age** as separate quantities.
- The current Scientific Core assumes one ideal scenario-relative time basis. It models periodic sample cadence, fixed stream latency and causal sample selection, but **does not yet model clock offset/drift or real synchronization error**. Do not claim that current controls demonstrate clock synchronization until this is added.
- Latency is not the same as clock offset. Increasing latency must not rewrite the physical sample epoch.
- Update rate is not latency. A 100 Hz stream can have large latency; a 10 Hz stream can have near-zero latency.
- Never use a sample whose availability epoch is after the selected sonar event in a causal real-time association unless the lesson is explicitly demonstrating post-processing with future/bracketing data.
- The current along-track consequence assumes constant vessel speed and concerns the **position state applied at TX**, not complete bathymetric sounding error.
- Do not convert attitude age directly to metres. Full geometric consequence requires angular rate/state, lever arms, beam direction, range and seafloor geometry; D11/D14 provide those ingredients.
- Preserve the exact TX epoch for each D9 sector when multisector timing is demonstrated.
- 1PPS, PTP, NTP, GNSS UTC and manufacturer timing architectures are examples of synchronization mechanisms, not interchangeable guarantees of identical performance.
- Avoid teaching network transport latency as universally deterministic; variable delay/jitter is a later fidelity feature unless explicitly modelled.
- Patch-test latency calibration can reveal an effective system timing offset, but D13 should teach the timing mechanism first; the Patch Test Module owns calibration workflow.
- Formal timing uncertainty propagation belongs to D17.

## Dependencies / forward reuse

Consumes:
- D9 sector identity and multiple TX epochs;
- D10 sensor identities/reference geometry;
- D11 time-varying position/attitude/heave state;
- D12 stream identity, update cadence and timestamp-source semantics.

Passes forward:
- correctly associated position/attitude/environment states and sonar-event epochs to D14 Sounding Formation;
- timing-related planning/operational constraints to D15/D16;
- latency/synchronization uncertainty contributors to D17;
- effective latency intuition to the Patch Test Module without duplicating patch-test calibration pedagogy here.

## Current implementation delta

`TimingLab.tsx` and `timing_api.py` already contain a strong causal first slice:
- trigger, TX, RX-start and RX-end events;
- position and attitude stream selection;
- per-stream update rate and nominal period;
- per-stream fixed latency;
- sample epoch and availability epoch;
- causal rule `latest sample with availability_time <= tx_time`;
- sample age at TX;
- `unavailable` state when no causal sample exists;
- constant-speed position consequence in metres;
- attitude age explicitly **not** converted to metres.

Next-version changes:
- make `sample time -> availability time -> association to TX` the dominant first visual story;
- separate the current large control wall into progressive stages: cadence, latency, ping events, then advanced synchronization;
- draw periodic sample and availability ticks, not only one generic sample event;
- remove/de-emphasize the generic `timeline latency` control if it does not affect the per-stream association lesson or label it clearly as a separate demonstration quantity;
- keep fixed/shared timeline scales so changing latency/rate remains perceptible;
- add a Scientific-Core **clock-offset/common-time-basis model** before claiming a full synchronization lesson;
- add synchronized common-time vs sensor-time rulers after that model exists;
- later couple attitude sample age to D11 time-varying Truth attitude for angular consequence, without frontend-only motion physics;
- support D9 sector-specific TX epochs through the core/API when multisector association is added;
- preserve current causal no-future-sample rule and the explicit boundary that position timing consequence is not full sounding error.

## Recognized references

- **IHO S-5A Ed. 2.0.0 (Aug 2026), H6.1a — Hydrographic data acquisition / real-time acquisition and control**: integrated sensor acquisition, data-acquisition systems, time-tagging and communication-interface configuration establish the competence basis for synchronized hydrographic acquisition: <https://portal.iho.int/share/api/files/AAAAAAABALI/Standard%20S-5A%20Ed.2.0.0/S-5A_Ed2.0.0_05May26.pdf>
- **IHO S-5A Ed. 2.0.0, H4.2b — Survey data transfer**: explicitly includes latency, bandwidth and redundancy considerations in hydrographic data transfer: <https://portal.iho.int/share/api/files/AAAAAAABALI/Standard%20S-5A%20Ed.2.0.0/S-5A_Ed2.0.0_05May26.pdf>
- **IHO International Hydrographic Review (2025), “Survey systems verification and calibration in the hydrospatial domain”**, §4.7 Latency calibration — relates positional/acoustic synchronization, speed-dependent spatial discrepancy and PPS timing practice: <https://ihr.iho.int/articles/survey-systems-verification-and-calibration-in-the-hydrospatial-domain/>
- **NOAA Field Procedures Manual (2014), §4.2.4.2.2 Attitude** — identifies unaccounted acquisition-system latency as a source of vessel-motion artefacts and notes reprocessing for known latency: <https://www.nauticalcharts.noaa.gov/publications/docs/standards-and-requirements/fpm/2014-fpm-final.pdf>
- **Kongsberg EM 304 Installation Manual** — real-system evidence for PU 1PPS clock synchronization normally supplied by the positioning system: <https://www.kongsberg.com/globalassets/kongsberg-maritime/km-products/product-documents/427620_em304_installation_manual_en.pdf>
- **Kongsberg EM 2040 Installation documentation** — identifies external synchronization, 1PPS from GPS and external sensor interfaces; explicitly describes 1PPS as the preferred external-clock synchronization method for the system: <https://www.kongsberg.com/contentassets/098bb8dd6793498c8deb72431583958e/391932ad_em2040_slim_pu_installation.pdf>
- **Kongsberg Seapath 385** — hydrographic position/attitude/timing system example: all output data share timestamps stated to 0.001 s of actual measurement time; PTP/NTP are available for time-critical Ethernet applications: <https://www.kongsberg.com/what-we-do/ocean-space/inertial-solutions/seapath/seapath-385/>
- **Trimble Applanix POS MV** — hydrographic GNSS/INS example with position, attitude, heave and velocity data time-tagged to microsecond accuracy; used as real-system evidence for the importance of measurement-time tagging: <https://applanix.trimble.com/en/products/hardware/applanix-pos-mv>
