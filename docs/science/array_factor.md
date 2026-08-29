# Narrowband Array Factor

Version: 0.1.0
Status: implemented reference model

## Purpose

HydroSIM keeps the directivity of one physical element separate from the spatial
interference produced by multiple elements. The present model implements the
second quantity: the one-way far-field narrowband **array factor**.

The intended decomposition is

\[
B(\mathbf u)=E(\mathbf u)\,AF(\mathbf u),
\]

where `E` is the element factor and `AF` is the array factor. This separation is
important because element dimensions and array spacing produce different physical
effects and should remain independently configurable.

## Direction convention

Both the source direction \(\mathbf u\) and steering direction \(\mathbf u_0\) are
unit vectors expressed in the array-local frame and point **from the array centre
toward the acoustic source / field direction**.

This preserves the convention already used by HydroSIM receive steering:

- zero across-track angle: array-local +Z normal;
- positive across-track: Port (-Y);
- negative across-track: Starboard (+Y).

## Residual spatial phase

For element position \(\mathbf r_i\), frequency \(f\), sound speed \(c\), wavelength
\(\lambda=c/f\), and wavenumber

\[
k=\frac{2\pi}{\lambda},
\]

the residual phase after steering is

\[
\phi_i=k(\mathbf u-\mathbf u_0)\cdot\mathbf r_i.
\]

This follows directly from the existing HydroSIM timing convention. A source
direction gives the far-field arrival offset

\[
\Delta t_i=-\frac{\mathbf u\cdot\mathbf r_i}{c},
\]

and steering toward \(\mathbf u_0\) applies compensation delay

\[
\tau_i=\frac{\mathbf u_0\cdot\mathbf r_i}{c}.
\]

Under the complex-signal convention \(s(t)=e^{i2\pi ft}\), their combined phase is
therefore

\[
-2\pi f\Delta t_i-2\pi f\tau_i
= k(\mathbf u-\mathbf u_0)\cdot\mathbf r_i.
\]

## Complex weights and normalization

For complex element weight \(w_i\), HydroSIM computes

\[
A=\sum_i w_i e^{i\phi_i}.
\]

The normalized one-way magnitude is

\[
AF=\frac{|A|}{\sum_i |w_i|},
\]

and normalized power is

\[
P_{AF}=AF^2.
\]

This normalization guarantees that perfectly phase-aligned contributions reach
unity independently of the overall weight scale. It is a normalized voltage /
pressure-like response, not absolute acoustic gain or received level.

Uniform weights \(w_i=1\) are used by default. Complex weights are already accepted
so later shading, calibration, or deliberate phase weighting can be represented
without changing the array-factor equation.

## Analytical anchors

The implementation includes closed-form tests independent of the numerical code.
For a two-element array with spacing

\[
d=\frac{\lambda}{2},
\]

broadside steering and a source at +30 degrees give an inter-element residual phase
of magnitude

\[
\Delta\phi=\frac{2\pi d}{\lambda}\sin 30^\circ=\frac{\pi}{2}.
\]

The normalized magnitude of two equal elements is therefore

\[
AF=\left|\cos\frac{\Delta\phi}{2}\right|
=\frac{\sqrt 2}{2},
\]

with normalized power 0.5.

For a +30 degree source steered to -30 degrees, the residual inter-element phase is
\(\pi\), so the two equal elements cancel ideally.

For broadside steering with \(d=\lambda\), a source at +90 degrees produces a
\(2\pi\) inter-element phase difference and therefore adds coherently again. This is
the first explicit HydroSIM demonstration of a **grating lobe / spatial alias**.

## Scope and limitations

The current array factor assumes:

- far-field plane-wave geometry;
- one monochromatic frequency;
- deterministic element positions;
- ideal complex weights;
- no mutual coupling;
- no channel noise or calibration mismatch;
- no finite-bandwidth effects;
- no near-field focusing;
- no element directivity inside the array-factor calculation.

Element directivity remains in `element_factor.py`. The next physical beam-pattern
layer should combine the two explicitly rather than folding element directivity into
this model.

## Next stage

The immediate next relationship is

\[
B_{one-way}(\mathbf u)=E(\mathbf u)\,AF(\mathbf u).
\]

After separate TX and RX patterns exist, HydroSIM can form the two-way response
without confusing a geometric pencil ray with a physical finite-aperture beam:

\[
B_{two-way}(\mathbf u)=B_{Tx}(\mathbf u)\,B_{Rx}(\mathbf u).
\]
