# PED-D16 Survey Planning Contract

Status: authoritative minimum scientific contract  
Experience: `PED-D16`  
Scope: vendor-neutral rectangular/reference-area survey-planning slice

## Purpose

PED-D16 teaches how a survey area and sonar swath geometry determine a simple set of planned survey lines and their first-order coverage consequence. This contract defines the minimum deterministic rules needed for learner-visible planned lines, predicted strip coverage, gaps/overlap, line count, total planned line length, and simple survey-time consequence.

It reuses canonical PED-D8 swath/footprint geometry and `docs/science/ped_d17_coverage_density_contract.md`. It does not define new sonar physics, detection behavior, uncertainty, IHO compliance scoring, route optimization, or vendor-specific planning logic.

## Reference area and frame

The minimum supported area is a convex rectangular horizontal survey area in a local planning frame `P` with coordinates `[x,y]` in metres.

- `+x`: local East-like horizontal axis;
- `+y`: local North-like horizontal axis;
- all planning geometry is 2-D horizontal;
- area vertices are Configured and ordered consistently around the rectangle;
- no geodetic curvature is modeled in this first slice.

The implementation may accept rectangle centre/width/height or four rectangle vertices, but must convert them to one explicit local-metre representation before planning.

A DTM may be displayed as contextual background, but first-slice line placement is based on the configured horizontal area and one canonical reference sonar swath width. Terrain-following and depth-varying swath adaptation are out of scope unless a later contract explicitly adds them.

## Planned line direction

The learner configures a line direction `alpha` in the planning frame, measured clockwise from `+y` (North-like), consistent with a navigation heading convention.

Define the unit vector along the planned line:

`u = [sin(alpha), cos(alpha)]`.

Define the unit normal pointing to the line's right/Starboard side:

`n = [cos(alpha), -sin(alpha)]`.

The sign of `n` is only used to order lines deterministically; line spacing and overlap use absolute distances.

Changing `alpha` rotates the family of parallel survey lines relative to the fixed survey rectangle. `alpha` and `alpha + 180 deg` represent the same geometric family with reversed traversal direction; line count/coverage must be invariant to that reversal.

## Canonical swath width

Let `W > 0` [m] be the canonical usable instantaneous swath width for the selected sonar/reference-depth configuration, derived upstream from PED-D8/D17 geometry.

PED-D16 must consume this authoritative width; React must not derive it from beam count, angle, or a frontend approximation.

The first slice assumes the same `W` for every planned line.

## Learner spacing mode

Exactly one spacing mode is active for a plan:

1. **Overlap mode** — learner configures fractional side overlap `q` with `0 <= q < 1`.
2. **Explicit-spacing mode** — learner configures desired line spacing `S_req > 0` [m].

### Overlap mode

The maximum permitted centreline spacing is

`S_req = W * (1 - q)`.

Examples:
- `q = 0` -> `S_req = W` (touching nominal strips);
- `q = 0.20` -> `S_req = 0.8 W`;
- increasing overlap decreases permitted spacing.

### Explicit-spacing mode

`S_req` is taken directly from the learner configuration.

If `S_req > W`, the plan is geometrically allowed but predicts internal line-to-line gaps. If `S_req = W`, adjacent idealized strips touch. If `S_req < W`, adjacent strips overlap.

Do not silently reinterpret an explicit gap-producing spacing as invalid; it is a legitimate pedagogical configuration whose consequence is `gapped` coverage.

## Across-area planning width

Project every rectangle vertex `r_i` onto the line-normal axis:

`c_i = r_i dot n`.

Define

`c_min = min(c_i)`  
`c_max = max(c_i)`  
`B = c_max - c_min`.

`B` is the rectangle's required cross-line span for the configured direction.

`B > 0` is required for a valid finite-area plan.

## Edge coverage and line placement

Each idealized survey line owns a cross-line coverage strip extending `W/2` to each side of its centreline.

The first and last line centres are anchored so the nominal swath reaches the projected area edges:

`c_first = c_min + W/2`  
`c_last  = c_max - W/2`.

### Area narrower than one swath

If `B <= W`, use exactly one line at

`c_1 = (c_min + c_max)/2`.

This line's nominal strip covers the entire projected cross-line span.

### Area wider than one swath

If `B > W`, define the usable centreline span

`D = B - W`.

Choose the minimum number of lines that does not exceed the requested maximum spacing:

`N = ceil(D / S_req) + 1`.

with `N >= 2`.

Place the `N` line centres uniformly between the two edge anchors:

`c_j = c_first + j * S_actual`,  j = 0 ... N-1

where

`S_actual = D / (N - 1)`.

Therefore

`S_actual <= S_req`.

This rule is intentional: the requested overlap or explicit spacing acts as a maximum allowed centreline spacing, while the edge anchors guarantee nominal coverage at both projected rectangle edges. The final plan may therefore contain slightly more overlap than requested when `D` is not an integer multiple of `S_req`.

The API must expose both `requested_spacing_m` and `actual_spacing_m` so the learner can see this consequence.

## Finite planned line geometry

For each centre offset `c_j`, define the infinite planned line

`p(t) = n * c_j + u * t`.

Clip this line against the configured rectangle. The intersection, when valid, is a finite line segment with endpoints `p_start_j` and `p_end_j`.

The segment length is

`L_j = ||p_end_j - p_start_j||` [m].

Only non-zero finite intersections are valid survey lines.

The exact clipping algorithm is an implementation choice (for example, analytic line-rectangle intersection or a standard convex clipping method), but the resulting finite segment must be geometrically equivalent.

### Alternating traversal direction

For display/executable-order purposes, consecutive line segments may alternate direction (lawnmower ordering):

- line 0: one endpoint -> opposite endpoint;
- line 1: reversed;
- etc.

This alternation is a route-ordering convenience only. It must not change line geometry, count, length, swath coverage, or scientific state.

No turn arcs or turn distances are added in the minimum slice.

## Line count and total planned length

The planned line count is

`N_lines = number of valid clipped line segments`.

For the supported rectangle and valid offsets above, this should equal `N`.

Total planned survey-line length is

`L_total = sum_j L_j` [m].

This is the length of on-line acquisition segments only. It excludes turns, run-ins/run-outs, cross-lines, transit to/from the survey area, and safety margins.

## Predicted strip coverage

For each planned line, construct its idealized cross-line strip of half-width `W/2` around the finite centreline segment, then clip that strip to the survey rectangle.

The union of all clipped strips is the predicted nominal survey coverage for the first slice.

The implementation may return render-ready polygons or an equivalent clipped strip representation, provided the frontend does not have to recreate the geometry scientifically.

### Adjacent-line overlap/gap consequence

For adjacent line centres separated by `S_actual`:

- if `S_actual < W`: overlap width `O = W - S_actual`;
- if `S_actual = W` within numerical tolerance: strips touch, `O = 0`, no internal gap;
- if `S_actual > W`: gap width `G = S_actual - W`.

Because the default edge-placement rule forces `S_actual <= S_req`, overlap-mode plans with valid `0 <= q < 1` necessarily have `S_actual <= W` and therefore no internal cross-line gap in the idealized constant-swath model.

Explicit-spacing mode may intentionally produce gaps when `S_req > W`; however, when edge anchoring requires additional lines, `S_actual` may become less than `S_req`. The predicted classification must always use `S_actual`, not the learner's requested value alone.

### Coverage classification

At minimum expose:

- `continuous`: no internal uncovered region between adjacent nominal strips inside the rectangle;
- `overlapping`: continuous and `S_actual < W` for at least one adjacent pair;
- `touching`: continuous and all adjacent pairs touch within tolerance (`S_actual ~= W`);
- `gapped`: at least one internal gap exists because an adjacent effective centre spacing exceeds `W`.

For the uniform first-slice plan, all adjacent spacings are equal when `N > 1`, so one classification is sufficient for the family.

The physical area outside the configured rectangle is irrelevant; strips may extend beyond it before clipping and must not count toward in-area coverage.

## Relation to D17

PED-D17 defines instantaneous footprint/coverage and sounding-density consequences. PED-D16 uses the canonical swath/footprint support as a planning-width input across multiple survey lines.

Important boundary:

- D17 High Density or multiple detections can change sounding density inside a swath;
- they do not, by themselves, change `W` for PED-D16;
- therefore they do not justify wider line spacing unless a separate canonical sonar geometry actually increases usable swath width.

PED-D16 line planning must never derive line spacing from sounding count alone.

## Vessel speed and survey time

Let vessel survey speed be `v > 0` [m/s].

The minimum idealized on-line survey time is

`t_on_line = L_total / v` [s].

This is a Derived lower-bound/reference acquisition time for the planned line segments only.

It excludes:

- turns;
- acceleration/deceleration;
- run-in/run-out stabilization distance;
- cross-lines;
- transits;
- weather/current effects;
- operational delays.

If `v <= 0` or non-finite, line geometry remains valid but survey-time output is unavailable/invalid.

Do not invent turn-time or vendor maneuver models in this slice.

## Configured / Derived semantics

### Configured

- rectangular survey area;
- reference depth/scenario used upstream to obtain canonical swath;
- sonar/configuration selection;
- canonical usable swath width `W` as a consumed configured/scenario quantity;
- line direction `alpha`;
- spacing mode;
- requested overlap `q` or requested spacing `S_req`;
- vessel survey speed.

### Derived

- planning axes `u`, `n`;
- projected cross-line span `B`;
- requested spacing from overlap mode;
- actual spacing `S_actual`;
- planned line offsets and clipped endpoints;
- line count;
- individual and total line lengths;
- clipped predicted coverage strips/union;
- overlap/gap widths and classification;
- idealized on-line survey time.

No new Truth, Observed, or Estimated state is created by the reference planner.

## Invalid and unsupported states

Return explicit invalid/unavailable status rather than fabricated output when:

- area is not a valid finite rectangle for the minimum slice;
- area dimensions or projected span are non-positive/non-finite;
- canonical swath width `W <= 0` or non-finite;
- overlap mode has `q < 0` or `q >= 1`;
- explicit spacing has `S_req <= 0` or non-finite;
- line direction is non-finite;
- clipping does not yield a finite non-zero segment where one is expected;
- required geometry is not expressed in a common declared local-metre frame.

Unsupported rather than silently approximated:

- arbitrary concave/non-rectangular polygons in the first slice;
- terrain-following/adaptive spacing;
- depth-varying swath along a line;
- slope-dependent usable-swath optimization;
- geodetic great-circle planning;
- current/wind compensation;
- turn optimization;
- safety offsets/exclusion zones;
- IHO order/compliance scoring;
- probabilistic coverage or detection assurance;
- uncertainty/TPU-based spacing rules;
- vendor-specific planning constraints.

## Minimum acceptance anchors

1. **Single-line case:** `B <= W` -> exactly one centred line.
2. **No-overlap anchor:** `B=300 m`, `W=100 m`, `q=0` -> `D=200 m`, `N=3`, `S_actual=100 m`, touching/continuous.
3. **20% overlap anchor:** `B=300 m`, `W=100 m`, `q=0.20` -> `S_req=80 m`, `N=ceil(200/80)+1=4`, `S_actual=66.666... m`; predicted overlap is about `33.333 m`, i.e. at least the requested 20% overlap because edge anchoring tightens spacing.
4. **Spacing monotonicity:** decreasing `S_req` cannot decrease line count for fixed area/direction/swath.
5. **Swath monotonicity:** increasing `W` at fixed area/direction/overlap cannot require more lines.
6. **Direction reversal:** `alpha` and `alpha+180 deg` produce the same geometric line family, line count, total length and coverage classification.
7. **Edge coverage:** first/last nominal strips reach `c_min` and `c_max` exactly under the reference rule when `B>W`.
8. **Length closure:** `L_total` equals the sum of Euclidean clipped segment lengths.
9. **Time anchor:** `L_total=2000 m`, `v=4 m/s` -> `t_on_line=500 s`.
10. **No turn invention:** changing traversal alternation does not change `L_total` or predicted on-line time.
11. **High Density boundary:** enabling High Density alone does not change line spacing or line count unless upstream canonical usable swath width changes for another reason.
12. **Explicit gap case:** a plan whose effective adjacent spacing is `120 m` with `W=100 m` reports `20 m` nominal internal gap; it must not be called invalid merely because it is gapped.

## Implementation boundary

Scientific/Core geometry or the PED-D16 application model owns:

- planning-frame projection;
- requested-to-actual spacing conversion;
- line-count rule;
- edge anchors;
- line clipping;
- line lengths;
- nominal strip coverage geometry;
- overlap/gap classification;
- on-line survey-time calculation.

The API should serialize render-ready line segments, spacing, count/length, coverage/gap state and validity.

React may visualize and label these outputs in EN/PT-BR but must not reimplement the line-placement equations, clipping, overlap/gap science, or time calculation.

## Reused authority

- canonical PED-D8 beam/swath/finite-footprint geometry;
- `docs/science/ped_d17_coverage_density_contract.md`;
- `docs/conventions.md` for units, frames and state semantics.
