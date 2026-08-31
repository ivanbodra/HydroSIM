# Environmental sound-speed profile extension

Status: scientific specification for the first didactic environmental extension of a truncated sound-speed profile.

## Purpose

The Propagation Explorer should teach that sound speed in seawater is a derived environmental quantity rather than an independent profile parameter:

\[
c = c(T,S,P).
\]

This model also provides an explicit, scientifically interpretable way to continue a didactic profile below its maximum observed/configured depth without changing the strict finite-domain semantics of the generic layered ray tracer.

## Scientific distinction

A finite observed profile does not imply knowledge below its deepest observation. HydroSIM therefore does **not** silently extrapolate `LayeredSoundSpeedProfile` objects.

Profile support beyond the deepest supplied depth must be an explicit operation with an identified assumption and state category.

This is consistent with the NOAA/UNH HydrOffice Sound Speed Manager workflow, which treats profile extension as an explicit operation and can use climatological/model/reference-cast information rather than silently extending the final sample.

## First didactic environmental extension

Let `z_m` be the maximum supplied depth, with deepest temperature `T_m` and salinity `S_m`.

For the first reference model below that depth:

\[
T(z>z_m)=T_m,
\]

\[
S(z>z_m)=S_m,
\]

while hydrostatic pressure continues to vary with depth and latitude:

\[
P=P(z,\phi).
\]

Sound speed is then calculated from an established seawater formulation:

\[
c(z)=c[T_m,S_m,P(z,\phi)].
\]

The reference sound-speed formulation is Wong & Zhu (1995), which corrects the Chen & Millero (1977) seawater sound-speed formulation and is also implemented by the NOAA/UNH HydrOffice Sound Speed Manager.

The first implementation should use a recognized pressure/depth conversion consistent with TEOS-10/GSW where practical.

## Didactic control case

The Explorer should also support a deliberately simple constant-sound-speed continuation:

\[
c(z>z_m)=c(z_m).
\]

This is a control assumption, not the preferred environmental model. Comparing it with the environmental extension exposes the important teaching result that constant temperature and salinity do **not** imply constant sound speed because pressure continues to increase with depth.

## State semantics

The extension must preserve HydroSIM state categories:

- supplied temperature/salinity samples: `Observed` or `Configured`, according to lesson source;
- temperature/salinity below `z_m` under this model: `Estimated`;
- pressure calculated from depth and latitude: `Derived`;
- sound speed calculated from T/S/P: `Derived` from the environmental state;
- extended ray path and sounding reconstruction: `Derived`.

The extrapolated region must never be presented as measured/observed water-column data.

## Validity and limitations

This is a first-order didactic extrapolation. It does **not** claim that real deep-ocean temperature and salinity remain exactly constant below the last observation.

Its purpose is to:

1. preserve an explicit assumption below the observed domain;
2. demonstrate the pressure contribution to seawater sound speed;
3. provide a deterministic comparison with constant-c continuation; and
4. support ray-tracing lessons without hiding extrapolation inside the generic propagation solver.

For realistic operational or environmental reconstruction, a deeper cast, reference cast, climatology, or ocean model should be preferred. Future extensions may use WOA, RTOFS, or equivalent referenced environmental sources, but those are outside the first vertical slice.

## Architecture boundary

The generic layered propagation API remains strict: tracing outside a finite profile's explicit support is an error unless the caller has first constructed an explicitly extended profile.

The environmental extension belongs in a scientific helper/composition path used by the Propagation Explorer. It must not be embedded as implicit behavior of `LayeredSoundSpeedProfile` or the generic Snell solver.

## Expected tests

The implementation should test at least:

- continuity at `z_m`;
- increasing pressure with increasing depth for a fixed latitude;
- finite and physically plausible sound-speed values;
- deterministic behavior;
- divergence between constant-c and environmental extensions below `z_m`;
- preservation of strict finite-profile behavior in the generic ray tracer.

## References

Chen, C.-T., & Millero, F. J. (1977). *Speed of sound in seawater at high pressures*. Journal of the Acoustical Society of America, 62(5), 1129-1135.

Wong, G. S. K., & Zhu, S. (1995). *Speed of sound in seawater as a function of salinity, temperature, and pressure*. Journal of the Acoustical Society of America, 97(3), 1732-1736.

IOC, SCOR & IAPSO (2010). *The international thermodynamic equation of seawater – 2010: Calculation and use of thermodynamic properties*. Intergovernmental Oceanographic Commission, Manuals and Guides No. 56 (TEOS-10).

NOAA/UNH HydrOffice Sound Speed Manager, `hydroffice/hyo2_soundspeed`, including the oceanographic sound-speed and pressure/depth utilities and explicit profile-extension workflow.

## Coordination

Implementation handoff: Issue #34.

Didactic visualization handoff: Issue #35.
