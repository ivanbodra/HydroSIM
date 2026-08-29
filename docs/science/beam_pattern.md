# One-Way Physical Beam Pattern

Version: 0.1.0

## Purpose

HydroSIM keeps the finite response of one acoustic element separate from the spatial interference produced by the array. The first normalized physical one-way beam pattern is therefore constructed explicitly as

\[
B(\mathbf u;\mathbf u_0)=E(\mathbf u)\,AF(\mathbf u;\mathbf u_0),
\]

where:

- \(E\) is the rectangular-element pressure factor;
- \(AF\) is the normalized narrowband array factor;
- \(\mathbf u\) is the evaluated field/source direction;
- \(\mathbf u_0\) is the steering direction.

This decomposition is a modeling assumption of the present ideal far-field array: all elements have identical dimensions and orientation, mutual coupling is absent, and the same element factor multiplies every channel.

## Complex field

The array factor retains its complex coherent sum. The rectangular element factor is a real signed pressure response. HydroSIM therefore preserves the sign of the element factor across aperture nulls before forming the complex one-way field:

\[
B_c = E_{signed}\,AF_c.
\]

The reported normalized amplitude and power are

\[
A_B=|B_c|,
\]

\[
P_B=A_B^2.
\]

These are normalized pattern quantities. They are not source level, receive sensitivity, transmission loss, target strength, or sonar-equation received level.

## Across-track convention

For an across-track angle \(\theta\), HydroSIM uses

\[
\mathbf u(\theta)=
\begin{bmatrix}
0\\
-\sin\theta\\
\cos\theta
\end{bmatrix},
\]

so positive angles point Port and negative angles point Starboard.

## Half-power beamwidth

An angular scan evaluates the physical one-way pattern on a deterministic angle grid. The sampled main peak is identified, then the first half-power crossings on either side are located and linearly interpolated between adjacent samples.

The threshold is local to the sampled peak:

\[
P_{HP}=\frac{1}{2}P_{peak}.
\]

If both crossings are contained in the requested angular interval,

\[
BW_{-3dB}=\theta_R-\theta_L.
\]

HydroSIM does not extrapolate a missing crossing beyond the requested scan.

## Element factor can suppress an array-factor lobe

Array factor and physical beam pattern are deliberately not synonyms. For example, a uniformly weighted two-element array with spacing

\[
d=\lambda
\]

has an array-factor grating lobe at endfire because the inter-element phase difference can again become an integer multiple of \(2\pi\).

If each rectangular element has transverse width

\[
b=\lambda,
\]

its first transverse element-factor null occurs at the same 90 degree direction. Therefore the array factor may equal unity while the physical beam pattern is zero:

\[
AF=1,\qquad E=0,\qquad B=0.
\]

This is an important didactic distinction: element directivity can attenuate or suppress lobes predicted by the spatial array factor alone.

## Current validation anchors

The initial regression tests include:

1. unity one-way response at boresight for uniform weights;
2. suppression of a \(d=\lambda\) array-factor grating lobe by a \(b=\lambda\) element null;
3. an eight-element uniform linear array with \(d=\lambda/2\), whose broadside one-way half-power beamwidth is approximately 12.8 degrees when the individual element is deliberately broad;
4. a steered scan whose sampled main peak follows the requested across-track steering angle.

## Current scope

Implemented:

- identical rectangular elements;
- far-field narrowband element factor;
- arbitrary regular 1D/2D element positions from `TransducerArray`;
- complex array weights;
- one-way element-factor × array-factor composition;
- deterministic across-track angular scans;
- sampled peak and interpolated half-power beamwidth.

Not yet implemented:

- automatic sidelobe classification;
- automatic null classification;
- grating-lobe classification across an arbitrary scan;
- transmit × receive two-way pattern;
- unequal element dimensions or orientations inside one array;
- mutual coupling;
- element-to-element calibration errors;
- near-field focusing;
- broadband beam patterns;
- calibrated electro-acoustic gain.

## Architectural consequence

The next physical composition is not a replacement for the current one-way pattern. A Mills-Cross or other MBES two-way angular response will combine explicit transmit and receive responses, conceptually

\[
B_{2way}(\mathbf u)=B_{Tx}(\mathbf u)\,B_{Rx}(\mathbf u),
\]

with the exact amplitude/power semantics kept explicit. Propagation and bottom interaction remain independent fidelity layers.
