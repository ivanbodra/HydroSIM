# Two-Way Beam Pattern

Version: 0.2.0

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

The narrowband far-field two-way reference response is

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

## Explicit array orientation

Each `TransducerArray.orientation` defines the fixed array-to-sensor rotation

\[
R_{SA}=R_z(\psi)R_y(\theta)R_x(\phi),
\]

where a vector represented in array frame \(A\) is represented in the containing
sensor frame \(S\) by

\[
\mathbf u_S=R_{SA}\mathbf u_A.
\]

Because a direction vector has no translation term, the inverse component
transformation is simply

\[
\mathbf u_A=R_{SA}^{T}\mathbf u_S.
\]

Therefore one physical direction in the common sensor frame is expressed
independently in TX and RX frames as

\[
\mathbf u_{A,Tx}=R_{SA,Tx}^{T}\mathbf u_S,
\]

\[
\mathbf u_{A,Rx}=R_{SA,Rx}^{T}\mathbf u_S.
\]

The steering directions follow exactly the same transformation rule.

This is now implemented explicitly by the sensor-frame two-way API. The lower-level
API remains available when TX- and RX-local direction components are already known.

## Why the frames remain independent

A physical direction is common to TX and RX, but its numerical coordinates generally
differ when the apertures have different installation rotations. HydroSIM therefore
does not copy one local vector into both beam-pattern calculations.

This distinction is important even before introducing Mills Cross. It supports

- co-aligned TX/RX apertures;
- arbitrary fixed angular offsets;
- orthogonal apertures;
- dual-head arrangements; and
- future sector-specific aperture geometries.

The acoustic response model remains independent of the installation architecture.

## Mills Cross as a configuration

A classic MBES Mills-Cross arrangement can be represented by separate TX and RX
apertures whose principal dimensions are approximately orthogonal. For example, a
90-degree relative yaw about the common sensor +Z axis can rotate one linear
aperture's principal axis relative to the other while preserving their common
broadside normal.

Each aperture still retains its own

- element dimensions;
- element positions and spacing;
- fixed installation orientation;
- complex weights;
- steering direction; and
- one-way beam pattern.

The final directional response is obtained only after the common physical direction
has been transformed into both local frames and the independent one-way responses
have been evaluated and multiplied.

Other sonar configurations use the same composition without being described as
Mills Cross.

## Current implementation boundary

The explicit bridge currently begins from a common **sensor-frame direction**. A
later integration layer may obtain that direction from vessel/body or navigation
coordinates using the existing HydroSIM installation and vessel-attitude transforms.
That later composition should preserve the same chain:

\[
N \rightarrow B/S \rightarrow A_{Tx}, A_{Rx}.
\]

The array response layer itself should not acquire vessel-motion responsibilities.

## Current assumptions

The implementation assumes

- narrowband operation;
- common acoustic frequency for TX and RX;
- common sound speed;
- far-field one-way patterns;
- normalized responses;
- fixed array installation orientation inside the sensor frame;
- no propagation loss;
- no bottom scattering or target strength;
- no receive detection threshold;
- no waveform envelope or matched filtering; and
- no near-field focusing.

These limitations are explicit so later fidelity layers can be added without
silently changing the reference model.
