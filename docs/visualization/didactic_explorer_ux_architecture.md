# Didactic Explorer UX Architecture

Version: 0.1.0
Status: Design baseline

## 1. Purpose

The HydroSIM Didactic Explorer is an interactive scientific learning environment, not a parameter editor with plots.

Every learning experience should make a physical causal chain visible:

**control → physical phenomenon → observable consequence → interpretation**

The visualization is the primary teaching surface. Controls, numerical readouts, and explanatory text support the visualization rather than compete with it.

## 2. Primary users

### Student

The interface should help a student answer, in order:

1. What am I investigating?
2. What can I change?
3. What should I watch?
4. What changed?
5. Why did it change?
6. What kind of scientific representation am I seeing?

Progressive disclosure is preferred over exposing the full simulator configuration at once.

### Instructor

The interface must also work as a live classroom instrument. An instructor should be able to:

- establish a baseline quickly;
- isolate one physical phenomenon;
- change a parameter while explaining it;
- compare states;
- reset instantly;
- expose or hide explanatory material;
- retain legibility on a projector or large display.

Future interaction modes may include Guided Lesson, Free Exploration, and Instructor/Demonstration.

## 3. One laboratory, five perspectives

The Didactic Explorer uses five connected perspectives:

- Signal
- Beam
- Propagation
- Vessel
- Motion

These are not independent applications. They are pedagogical views of the same hydrographic sounding system.

Shared visual primitives, terminology, scientific-state encoding, controls, and interaction behavior should reinforce continuity between modules.

## 4. Standard learning-experience anatomy

A learning experience should normally contain the following layers.

### 4.1 Learning question

A short causal question that defines the experiment.

Example:

> How does array size affect beamwidth and seafloor footprint?

### 4.2 Essential controls

Expose only parameters that directly serve the current learning question.

Advanced or secondary parameters belong behind progressive disclosure.

### 4.3 Main visualization

The largest and strongest visual element on screen.

Changes should be visible immediately whenever computation permits.

### 4.4 What to look for

A short observation cue that directs attention to the relevant consequence without giving a long lecture.

### 4.5 Quantitative readouts

Important numerical values remain visible but subordinate to the phenomenon. Examples include wavelength, beamwidth, footprint, TWTT, and vertical error.

### 4.6 Scientific boundary

Each experience must state whether the representation is:

- Conceptual
- Analytical
- Numerical
- Simulation

Assumptions or major omissions should be accessible without dominating the main learning surface.

### 4.7 Reset and comparison

Reset must restore the exact baseline state.

Where pedagogically meaningful, the UI should support comparison such as baseline/current, before/after, or scientific states including Truth/Observed/Processed representations.

## 5. Proposed screen hierarchy

The default desktop hierarchy is:

1. global application bar;
2. module navigation;
3. learning-question strip;
4. contextual control rail;
5. dominant scientific visualization;
6. observation/readout rail or footer.

The interface should avoid large form blocks and excessive framing.

Controls should remain spatially close to the visualization they affect.

## 6. Scientific-state visual language

HydroSIM maintains distinct internal states:

- Truth
- Configured
- Observed
- Estimated
- Derived

The UI must preserve these distinctions consistently.

Color alone must never carry the full meaning. State encoding should be redundant through combinations of labels, line styles, markers, opacity, or other visual properties.

A future design-token layer should define canonical presentation rules for each state.

## 7. Scientific integrity

The UI must never imply physics that the Scientific Core does not calculate.

Animations are permitted only when their meaning is defensible.

Conceptual illustrations must be visibly identifiable as conceptual rather than quantitative simulation results.

The UI must not reimplement equations merely to obtain a convenient visual effect.

## 8. Localization

The application UI is bilingual from the beginning:

- English (`en`)
- Brazilian Portuguese (`pt-BR`)

English remains the canonical internal and fallback language.

User-facing strings are localization resources, not scientific identifiers.

Changing language must not alter simulation state, stored scenarios, scientific results, or reproducibility.

## 9. Accessibility and classroom readability

The design must account for:

- projector viewing distance;
- scalable typography;
- sufficient contrast;
- keyboard navigation and focus visibility;
- controls with adequate target sizes;
- scientific meaning that does not depend on color alone;
- reduced-motion preferences where animation is nonessential;
- graph titles, labels, axes, and annotations that remain readable in classroom use.

## 10. First vertical slice

The first UX reference implementation should be a complete Signal learning experience rather than a generic component library.

Recommended learning question:

**How does LFM bandwidth affect pulse compression?**

The slice should establish the reusable pattern for:

- learning question;
- essential controls;
- scientific boundary;
- main visualization;
- observation guidance;
- quantitative readouts;
- reset;
- EN/PT-BR switching.

Only after this vertical slice is validated should the same pattern be generalized across Beam, Propagation, Vessel, and Motion.

## 11. Design acceptance test

A proposed UI change should be rejected if it is visually attractive but does not improve at least one of the following:

- causal understanding;
- scientific interpretation;
- classroom demonstration;
- comparison of states;
- discoverability of the learning task;
- reduction of unnecessary cognitive load;
- accessibility;
- consistency across HydroSIM modules.
