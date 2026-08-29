# Two-Way Beam Pattern

Version: 0.1.0

## Purpose

HydroSIM models transmit and receive apertures as independent physical systems.
Mills Cross is therefore represented as one possible installation/array geometry,
not as a defining property of MBES and not as a universal sonar architecture.

## Reference composition

Let the normalized complex one-way transmit and receive field responses toward the
same physical direction be

\[
B_{Tx}(\mathbf u),\qquad B_{Rx}(\mathbf u).
\]

The first narrowband far-field two-way reference response is

\[
B_{2w}(\mathbf u)=B_{Tx}(\mathbf u)B_{Rx}(\mathbf u).
\]

The normalized two-way amplitude is

\[
A_{2w}=|B_{2w}|,
\]

and normalized two-way power is

\[
P_{2w}=|B_{2w}|^2.
\]

These are normalized directional responses. They are not source level, receive
sensitivity, target strength, propagation loss, or a complete sonar-equation term.

## Independent local frames

A physical direction is common to TX and RX, but its coordinate representation can
differ because the apertures can have different installation rotations. HydroSIM
therefore accepts

- the physical direction expressed in the TX-array frame; and
- the same physical direction expressed in the RX-array frame.

Frame transformation remains a geometry/integration responsibility. The acoustic
composition layer does not assume that the two array frames are aligned or
orthogonal.

This separation is what permits a Mills-Cross installation without hard-coding
Mills Cross into the generic response model.

## Mills Cross as a configuration

A classic MBES Mills-Cross arrangement can be represented by separate TX and RX
apertures whose principal dimensions are approximately orthogonal. Each aperture
retains its own

- element dimensions;
- element positions and spacing;
- complex weights;
- steering direction; and
- one-way beam pattern.

The final directional response is obtained only after the two independent one-way
responses are evaluated toward the same physical direction and multiplied.

Other sonar configurations can use the same composition without being described as
Mills Cross.

## Current assumptions

The first implementation assumes

- narrowband operation;
- common acoustic frequency for TX and RX;
- common sound speed;
- far-field one-way patterns;
- normalized responses;
- no propagation loss;
- no bottom scattering or target strength;
- no receive detection threshold;
- no waveform envelope or matched filtering; and
- no near-field focusing.

These limitations are explicit so later fidelity layers can be added without
silently changing the reference model.
