# Daily Log

This file is the chronological record of nightly research runs.

## 2026-06-23 - Workspace Initialized

**Focus question:** How should persistent artificial gravity research be organized so future runs can make progress without losing failures or speculative threads?

**Sources reviewed:** None in this setup entry.

**What changed:** Created the research workspace structure and standing runbook.

**Reasoning:** A long-running speculative research effort needs explicit standards of evidence, hypothesis tracking, source notes, and a boundary map. Otherwise old failures will be rediscovered without learning from them.

**Failure or boundary found:** No physics conclusion yet. The main boundary at setup is epistemic: the project must encourage persistence without rewarding unsupported certainty.

**Hypothesis updates:** Initial register created.

**Next best step:** Start with a survey of established artificial gravity mechanisms and their limits, then use that map to identify less-explored adjacent mechanisms.

## 2026-06-24 - Laboratory Frame Dragging Scale

**Focus question:** Can ordinary laboratory-scale rotating masses create useful artificial gravity through gravitomagnetic or frame-dragging effects?

**Sources reviewed:** Ruggiero & Tartaglia, "Gravitomagnetic effects" (Nuovo Cimento B, 2002; arXiv:gr-qc/0207065); Everitt et al., "Gravity Probe B: Final Results of a Space Experiment to Test General Relativity" (Physical Review Letters, 2011; arXiv:1105.3456); Ruggiero & Astesiano, "A tale of analogies: gravitomagnetic effects, rotating sources, observers and all that" (Journal of Physics Communications, 2023; arXiv:2304.02167).

**What changed:** Added a quantitative boundary for H-002: gravitomagnetism is experimentally real and theoretically established in the weak-field limit, but ordinary engineered angular momentum is far too small to produce useful artificial gravity. For a deliberately aggressive flywheel estimate, `M = 10,000 kg`, `R = 1 m`, `omega = 1000 rad/s`, `I ~= 0.5MR^2`, and `J ~= 5e6 kg m^2/s`. At `r = 1 m`, the Lense-Thirring scale is only `Omega_LT ~= 2GJ/(c^2 r^3) ~= 7.4e-21 s^-1`. A velocity-dependent gravitomagnetic acceleration estimate `a_GM ~= 4vGJ/(c^2 r^3)` gives only `1.5e-17 m/s^2` even for a nearby test body moving at `v = 1000 m/s`, about `1.5e-18 g`.

**Reasoning:** Frame dragging couples to angular momentum, not merely to high RPM. The `G/c^2` suppression is severe. Gravity Probe B measured Earth's frame-dragging at tens of milliarcseconds per year, which is a major precision-GR success but also demonstrates the tiny scale even for a planetary source. Reaching `1g` at `r = 1 m` through the velocity-dependent weak-field term would require angular momentum on the order of `3.3e24 kg m^2/s` for a `1000 m/s` test body, roughly 18 orders of magnitude above the aggressive lab flywheel estimate.

**Failure or boundary found:** Ordinary rotating masses cannot provide practical artificial gravity through gravitomagnetic effects. The effect is established physics, but it is a precision-measurement phenomenon at human-accessible mass-energy densities. Any claim of useful lab-scale gravitomagnetic gravity must either invoke non-ordinary stress-energy, a non-GR coupling, or a systematic error; it cannot be explained by standard weak-field GR scaling alone.

**Hypothesis updates:** H-002 remains "strongly modeled" for engineered stress-energy in principle, but the ordinary-matter gravitomagnetic path is now marked as rejected for practical artificial gravity. Added H-006 to preserve the specific failed path.

**Next best step:** Quantify rotating-habitat artificial gravity comfort thresholds for `0.3g`, `0.5g`, and `1g`, including radius/RPM tradeoffs and Coriolis constraints, so the established baseline has the same numerical discipline as this rejected gravitomagnetic path.

## 2026-06-25 - Rotating Habitat Scale

**Focus question:** What radius and RPM combinations generate `0.3g`, `0.5g`, and `1g`, and where do Coriolis, gravity-gradient, and vestibular constraints begin to dominate the design?

**Sources reviewed:** Clément, Bukley, and Paloski, "Artificial gravity as a countermeasure for mitigating physiological deconditioning during long-duration space missions" (Frontiers in Systems Neuroscience, 2015, https://www.frontiersin.org/journals/systems-neuroscience/articles/10.3389/fnsys.2015.00092/full). The review summarizes older rotating-room and centrifuge work, including Stone/Letko-style comfort-zone assumptions, Graybiel adaptation studies, Skylab rotating-chair observations, and short-radius centrifuge data.

**What changed:** Completed the first numerical baseline for H-001 and E-001. For rotational artificial gravity, `a = omega^2 r`, so required radius falls with the square of RPM. That makes low-RPM comfort expensive in structure size, while compact designs rapidly become human-factors experiments rather than ordinary habitat engineering.

| Target | 2 rpm radius | 4 rpm radius | 6 rpm radius | 10 rpm radius |
| --- | ---: | ---: | ---: | ---: |
| `0.3g` | `67.1 m` | `16.8 m` | `7.5 m` | `2.7 m` |
| `0.5g` | `111.8 m` | `27.9 m` | `12.4 m` | `4.5 m` |
| `1.0g` | `223.6 m` | `55.9 m` | `24.8 m` | `8.9 m` |

Additional scale checks: at `4 rpm`, a `1 m/s` radial walking motion produces Coriolis acceleration `2 omega v ~= 0.84 m/s^2`, or about `0.09g`; at `6 rpm`, the same motion gives `1.26 m/s^2`, or about `0.13g`. The apparent gravity difference over a `1.8 m` standing body is approximately `1.8/r`, so it is only `3.2%` for `1g` at `4 rpm` and `55.9 m`, but rises to `7.2%` for `1g` at `6 rpm` and `24.8 m`, and `20%` for `1g` at `10 rpm` and `8.9 m`.

**Reasoning:** The Clément/Bukley/Paloski review is useful because it separates the simple physics from the unresolved human data. It gives an example of `1g` at about `4 rpm` and `56 m`, matching the calculation above. It also reports that older comfort-zone estimates favored roughly `6 rpm` with radii from `12-24 m` for `0.3g-1g`, but those limits came from limited observations and may be conservative. Later adaptation results suggest humans can tolerate higher rotation rates under progressive exposure or habituation, but that does not automatically make high-RPM whole-habitat design prudent: head motion, radial motion, cross-coupled angular accelerations, and operational tasks remain the hard part.

**Failure or boundary found:** Rotation is not blocked by physics; it is blocked by coupled architecture and human-factors scaling. There is no "free" small rotating 1g habitat. Below roughly `30 m` radius, `1g` implies `~5.5 rpm` or more, with meaningful gravity gradients and Coriolis accelerations during ordinary movement. Very compact systems may still be useful as intermittent centrifuges or exercise countermeasures, but they should not be treated as equivalent to a continuously inhabited low-RPM habitat.

**Hypothesis updates:** H-001 remains the strongest near-term artificial-gravity path, but now has a numerical boundary: comfortable continuous rotation likely wants tens to hundreds of meters of radius depending on target gravity and acceptable RPM. B-004 was expanded with this scale table. E-001 is complete.

**Next best step:** Investigate whether intermittent short-radius centrifugation can provide enough physiological benefit to avoid full-time rotating habitats, and identify the minimum dose variables: gravity level, radius/RPM, session duration, frequency, exercise coupling, and motion restrictions.

## 2026-06-25 - Direction Update: Localized Field Generation

**Focus question:** How should the research queue change now that centrifuge-type gravity generation is sidelined in favor of localized field generation?

**Sources reviewed:** No new physics sources; this is a prioritization update based on user direction.

**What changed:** Rotation and centrifuge work remains preserved as the established baseline and benchmark boundary, but it is no longer the active next research path. `E-008` was parked. `E-009` was added as the next high-priority task: map localized artificial-gravity field generation under known physics.

**Reasoning:** Localized field generation is the more relevant target for inertial control, spacetime engineering, and speculative propulsion. The immediate rigor requirement is to keep the problem anchored in stress-energy accounting: under standard GR, real local gravity requires local stress-energy, so each candidate mechanism must state what source term it uses, how large it is, how localized it can be, and which precision tests or energy-condition constraints already bound it.

**Failure or boundary found:** No new failure was established in this update, but B-007 was added as the governing boundary: localized real gravitational fields require local stress-energy or new coupling. Claims that skip this accounting should be treated as weak signals or speculation until a source term and test path are explicit.

**Hypothesis updates:** H-001 is retained as a conventional benchmark but sidelined as the active focus. H-002 is promoted as the next active research route: engineered stress-energy, non-ordinary stress-energy, modified coupling, and localized field constraints.

**Next best step:** Start `E-009` by building a source-backed taxonomy of localized field-generation candidates: ordinary mass-energy concentration, electromagnetic stress-energy, negative energy/Casimir configurations, superconductors or condensed-matter anomaly claims, plasma/high-energy-density fields, modified-gravity couplings, and analog-gravity systems that are useful only as mathematics.

## 2026-06-26 - Electromagnetic Stress-Energy Scale

**Focus question:** Can localized electromagnetic field stress-energy generate a useful gravitational acceleration under known physics, or does the energy-density scale make it nonviable?

**Sources reviewed:** Navarro & Sancho, "A characterization of the electromagnetic stress-energy tensor" (arXiv:1101.2505, 2011); Gibbons & Herdeiro, "The Melvin Universe in Born-Infeld Theory and other Theories of Non-Linear Electrodynamics" (Classical and Quantum Gravity, 2001; arXiv:hep-th/0101229); Tsagas & Mavrogiannis, "Melvin's magnetic universe, the role of the magnetic tension and the implications for gravitational collapse" (Classical and Quantum Gravity, 2021; arXiv:2011.08245); Hahn et al., "45.5-tesla direct-current magnetic field generated with a high-temperature superconducting magnet" (Nature, 2019).

**What changed:** Added a hard scale boundary for ordinary electromagnetic localized field generation. Electromagnetic fields are legitimate stress-energy sources in GR, so this path is not conceptually forbidden. The problem is magnitude. A magnetic field has energy density `u = B^2/(2 mu0)` and equivalent mass density `rho = u/c^2`. A `45.5 T` continuous-field magnet corresponds to `u ~= 8.2e8 J/m^3` and `rho ~= 9.2e-9 kg/m^3`. Even a destructive or very short-pulse `1200 T` field would be only `u ~= 5.7e11 J/m^3` and `rho ~= 6.4e-6 kg/m^3`.

For a blunt spherical estimate, a `1 m` radius region would need `M = gr^2/G ~= 1.5e11 kg` at its surface to produce `1g`. That is `E ~= 1.3e28 J`, average `u ~= 3.2e27 J/m^3`, equivalent to `B ~= 8.9e10 T` if stored as magnetic field energy. By comparison, a `1 m` sphere filled with a `45.5 T` field has equivalent mass only `~3.8e-8 kg` and produces surface acceleration `~2.6e-18 m/s^2`, or `~2.6e-19 g`. A `1200 T` version still gives only `~1.8e-15 m/s^2`, or `~1.8e-16 g`.

**Reasoning:** The electromagnetic stress-energy tensor confirms that fields carry energy, momentum, pressure, and tension that enter the Einstein equations. Exact Einstein-Maxwell solutions such as Melvin-type magnetic universes are useful proof that magnetic/electric fields can shape spacetime in GR. They are not a practical engineering recipe for human-scale artificial gravity because the required field energies are astrophysical. The Melvin literature also warns against a naive "magnetic pressure just collapses gravitationally" picture: magnetic tension and field-line elasticity matter in relativistic collapse. That nuance is important for theory, but it does not rescue laboratory field generation from the `G/c^2` energy-density scale.

**Failure or boundary found:** Ordinary electromagnetic fields cannot create useful localized artificial gravity at laboratory or spacecraft scales unless accessible field strengths jump by roughly eight to nine orders of magnitude beyond magnetar-class `~1e10 T` fields or some nonstandard coupling is found. High-field magnet engineering may still be valuable for materials, plasma confinement, and analog experiments, but not because its direct GR field is large.

**Hypothesis updates:** Added H-007: ordinary electromagnetic stress-energy is a real but practically negligible localized-gravity source. H-002 remains viable only as a broad engineered-stress-energy umbrella; it must not treat "use strong EM fields" as a near-term field-generation route without new physics.

**Next best step:** Continue `E-009` by reviewing negative-energy/Casimir stress-energy and quantum-inequality limits, using the same scale discipline: local energy density, integrated energy, duration, and geometric control.

## 2026-06-28 - Casimir Negative-Energy Scale

**Focus question:** Can Casimir or other quantum negative-energy configurations generate a useful localized gravitational field, or do scale and quantum-inequality constraints make them nonviable under known physics?

**Sources reviewed:** Ford & Roman, "Quantum Field Theory Constrains Traversable Wormhole Geometries" (Physical Review D, 1996; arXiv:gr-qc/9510071); Ford & Roman, "Restrictions on Negative Energy Density in Flat Spacetime" (Physical Review D, 1997; arXiv:gr-qc/9607003); Pfenning & Ford, "The unphysical nature of Warp Drive" (Classical and Quantum Gravity, 1997; arXiv:gr-qc/9702026); Fewster, "Lectures on quantum energy inequalities" (2012; arXiv:1208.5399); Jaffe, "The Casimir Effect and the Quantum Vacuum" (Physical Review D, 2005; arXiv:hep-th/0503158).

**What changed:** Added a scale boundary for H-003 and E-010. The parallel-plate Casimir energy density magnitude is `|u| = pi^2 hbar c/(720 a^4)`. This rises rapidly as the separation `a` shrinks, but it remains gravitationally tiny at separations that can be treated as engineered structures. At `a = 1 um`, `|u| ~= 4.3e-4 J/m^3`, equivalent to `rho ~= 4.8e-21 kg/m^3`; at `a = 10 nm`, `|u| ~= 4.3e4 J/m^3`, `rho ~= 4.8e-13 kg/m^3`; at `a = 1 nm`, `|u| ~= 4.3e8 J/m^3`, `rho ~= 4.8e-9 kg/m^3`. Matching the crude `1 m` spherical `1g` energy-density scale from B-008, `u ~= 3.2e27 J/m^3`, would require `a ~= 1.9e-14 m`, smaller than nuclear dimensions and outside the regime of macroscopic plates, ordinary materials, or controllable device geometry.

**Reasoning:** Casimir configurations are important because QFT can violate classical pointwise energy conditions; the negative energy is not imaginary. But the useful engineering question is integrated stress-energy and controllability, not just the sign of the renormalized local energy density. Quantum inequalities restrict the magnitude-duration product of negative energy sampled along worldlines. Ford/Roman-style constraints applied to wormholes and Pfenning/Ford-style constraints applied to warp metrics both push macroscopic exotic geometries toward Planck-thin or physically unattainable stress distributions. Fewster's review reinforces the broader lesson: QFT relaxes classical energy conditions but replaces them with averaged remnants, not arbitrary macroscopic negative mass. Jaffe adds a source-quality warning: Casimir forces can be formulated as relativistic quantum forces between material charges/currents, so this route should not be oversold as direct extraction of unlimited vacuum energy.

**Failure or boundary found:** Negative-energy/Casimir stress is real but not a practical localized artificial-gravity source under known physics. It fails twice: accessible Casimir energy densities are far too small gravitationally, and attempts to concentrate negative energy enough for macroscopic metric engineering run into quantum-inequality, compensation, material, and geometry constraints. This does not prove all semiclassical gravity opportunities are closed, but it blocks the simple "stack Casimir cavities to make negative gravity" path.

**Hypothesis updates:** H-003 remains speculative but is narrowed: negative energy is a theoretical crack in classical energy conditions, not an engineering path unless a configuration can show macroscopic integrated negative stress-energy that survives quantum inequalities and includes the positive energy of boundaries/supports. Added H-008 to preserve the failed Casimir-local-gravity path.

**Next best step:** Continue E-009 with ordinary mass-energy concentration as a sanity baseline: how dense and how close would ordinary positive mass need to be to generate `0.01g`, `0.1g`, and `1g` gradients over `0.1-10 m`, and what tidal/structural hazards follow?

## 2026-06-30 - Ordinary Mass Local Gravity Scale

**Focus question:** How much ordinary positive mass-energy is needed to generate `0.01g`, `0.1g`, or `1g` at `0.1-10 m`, and do the mass, density, and tidal-gradient requirements leave any practical localized-field path under known physics?

**Sources reviewed:** Carroll, "Lecture Notes on General Relativity" (arXiv:gr-qc/9712019), for the Newtonian/weak-field limit; NIST/CODATA constants for `G` and `c`; Ozel and Freire, "Masses, Radii, and the Equation of State of Neutron Stars" (Annual Review of Astronomy and Astrophysics, 2016; arXiv:1603.02698), for compact-object density context.

**What changed:** Completed E-011 and added the ordinary-positive-mass boundary. In the weak-field limit, a compact source at distance `r` gives `a = GM/r^2`, so the required source mass is `M = ar^2/G`. Treating `r` as the source-surface distance for a blunt spherical benchmark gives:

| Target | `0.1 m` | `1 m` | `10 m` |
| --- | ---: | ---: | ---: |
| `0.01g` mass | `1.5e7 kg` | `1.5e9 kg` | `1.5e11 kg` |
| `0.1g` mass | `1.5e8 kg` | `1.5e10 kg` | `1.5e12 kg` |
| `1g` mass | `1.5e9 kg` | `1.5e11 kg` | `1.5e13 kg` |

The equivalent rest energies are also extreme: the `1 m`, `1g` case is `E = Mc^2 ~= 1.3e28 J`, matching the earlier EM-energy benchmark. Average densities for a sphere whose surface is at the field point remain far beyond ordinary material density: `1g` at `1 m` needs `rho_avg ~= 3.5e10 kg/m^3`; `0.01g` at `1 m` still needs `rho_avg ~= 3.5e8 kg/m^3`. A solid osmium-density sphere (`~2.26e4 kg/m^3`) would need a radius of about `1.55e4 m` for `0.01g`, `1.55e5 m` for `0.1g`, or `1.55e6 m` for `1g` at its surface.

**Reasoning:** This path is not conceptually speculative: ordinary mass is the cleanest established source of gravity. The failure is engineering scale and field shape. Bringing the source closer reduces total mass as `r^2`, but worsens tidal gradients as roughly `2a/r`. For the point/spherical benchmark, the acceleration gradient per meter is `2a/r`: at `1g`, that is `196 m/s^2 per m` at `0.1 m`, `19.6 m/s^2 per m` at `1 m`, and `1.96 m/s^2 per m` at `10 m`. Even a mild `0.01g` at `1 m` has a gradient of `0.196 m/s^2 per m`, about `0.02g` across a meter. A field strong enough and close enough to be useful becomes sharply nonuniform; a field distant enough to be smooth requires asteroid-scale mass.

**Failure or boundary found:** Ordinary positive mass can generate real localized gravity, but it is not a practical active artificial-gravity mechanism for spacecraft or labs under known physics. It fails by mass budget, density, structural support, tidal gradient, and hazard. The only way to get compact high acceleration from positive mass is to approach compact-object density regimes; those are not engineerable materials and would introduce containment, radiation, accretion, and catastrophic-failure issues long before becoming a usable cabin field.

**Blank space or new idea:** The remaining unclear space is not "more mass closer"; that boundary is closed. The useful blank space is shaped-source field quality: can any static or dynamic source geometry produce a locally flatter acceleration patch with less tidal gradient per unit peak acceleration, and what multipole/mass penalty does that impose? This is likely an optimization problem, not a loophole.

**Hypothesis updates:** H-002 is narrowed again: engineered stress-energy remains mathematically allowed, but ordinary positive mass-energy is now rejected as a practical localized field generator at human scale. Added H-009 to preserve this failed but important baseline.

**Next best step:** Run a shaped-source/multipole calculation: compare point mass, ring, slab/shell, and opposed-source geometries for local acceleration uniformity, mass required, and tidal tensor over a `1-2 m` human-scale volume.

## 2026-07-01 - Shaped Positive-Mass Field Quality

**Focus question:** Can shaped positive-mass geometries reduce tidal gradients over a `1-2 m` volume enough to matter, or does the mass penalty simply restate the ordinary source boundary?

**Sources reviewed:** Carroll's GR lecture notes for the Newtonian weak-field limit already used in E-011; Gauss-law/Newtonian gravity references for `div g = -4 pi G rho` and the infinite-sheet/Bouguer-plate limit; standard ring and disk axis-field formulas; multipole/Laplace-expansion references for the vacuum potential constraint.

**What changed:** Completed E-012 at first-pass scale. Static positive-mass shaping can improve local field uniformity, but it does not create an efficient localized artificial-gravity source. For a `1g` target at a cabin point `1 m` from the source reference:

| Geometry | Scale choice | Mass or surface density for `1g` | Local field-quality note |
| --- | ---: | ---: | --- |
| Point/sphere | `r = 1 m` | `1.47e11 kg` | Radial gradient `2g/m`; severe first-order tide. |
| Ring on axis | cabin point at `z = 1 m`, ring radius `R = sqrt(2) m` | `7.63e11 kg` | Axial first derivative is zero at the cabin point, but field falls to `0.77g` at `z = 0.5 m` and `0.89g` at `z = 1.5 m`; higher-order variation is large. |
| Finite disk | disk radius `R = 10 m`, cabin point `z = 1 m` from disk | `8.16e12 kg`, `Sigma ~= 2.60e10 kg/m^2` | About `55x` the point-mass budget; field changes by about `+5.5%/-5.4%` over `z = 1 +/- 0.5 m`. |
| Larger disk | disk radius `R = 20 m`, cabin point `z = 1 m` | `3.09e13 kg`, `Sigma ~= 2.46e10 kg/m^2` | About `210x` point-mass budget; axial variation over `+/-0.5 m` falls to about `+2.6%/-2.6%`. |
| Infinite sheet limit | ideal unbounded plane | `Sigma = g/(2 pi G) ~= 2.34e10 kg/m^2` | Distance-independent field outside the sheet, but requires unbounded mass; two equal parallel sheets cancel the field between them. |

**Reasoning:** In vacuum, the Newtonian potential is harmonic and the tidal tensor is the Hessian of the potential with zero trace. That means static source shaping can cancel selected derivatives at selected points, but cannot make an arbitrary finite positive-mass source behave like a perfectly uniform field over an extended region. The infinite sheet is the clean mathematical limit: it gives a constant external field, but the required surface density for `1g` is already `~2.34e10 kg/m^2`, and finite approximations require enormous area. The ring case is the useful cautionary example. Choosing `R = sqrt(2) z` nulls the axial derivative of `g_z = GMz/(z^2+R^2)^(3/2)`, so a naive single-gradient metric looks excellent. But over a meter-scale body, the higher-order shape is still large because the source is only meters away. Making a smoother field pushes the source farther/larger and raises total mass roughly with area.

**Failure or boundary found:** Positive-mass shaping can trade first-order tidal gradient for mass, size, and higher-order gradients, but it does not open a practical localized-field path under known physics. The best static geometries resemble a massive extended plate: smooth but astronomically heavy. Opposed positive-mass sources do not help in the simple equal-source case because they cancel acceleration where they improve symmetry; producing net acceleration plus low tide requires asymmetry or more elaborate multipoles, which reintroduce mass and higher-order variation.

**Blank space or new idea:** The remaining blank space is an optimization problem, not a loophole: given a keep-out surface around a `1-2 m` cabin, what is the minimum positive mass needed to produce a target acceleration while bounding all first- and second-order field errors? This could turn the qualitative "shaping penalty" into a rigorous lower-bound search.

**Hypothesis updates:** Added H-010 and B-011. H-009 remains rejected for practical localized artificial gravity, but now distinguishes compact-source failure from shaped-source field-quality tradeoffs.

**Next best step:** Run E-013: formulate a constrained positive-mass source optimization on a sphere, ring set, or planar array outside a keep-out volume, minimizing total mass for `0.01g` and `1g` while constraining acceleration variation across a `1-2 m` cabin.

## 2026-07-02 - Positive-Mass Cabin Optimization

**Focus question:** For a fixed keep-out volume around a `1-2 m` cabin, can a constrained positive-mass distribution produce `0.01g` or `1g` with tolerable full-volume field variation at less than asteroid-scale mass?

**Sources reviewed:** Carroll's GR lecture notes and the existing weak-field/Newtonian notes for the source-free potential and tidal tensor framing; the existing Gauss-law/Bouguer-plate and ring/disk axis-field notes from E-012; Yurtsever, Marzban, and Meila, "On the Gravitational Inverse Problem" (arXiv:1004.4939), for the non-uniqueness and constraint-dependence of gravitational inverse/source reconstruction.

**What changed:** Completed E-013 as a bounded calculation. The optimization target was narrowed to ordinary positive mass outside a cabin keep-out region, with no negative mass, active cancellation, or non-GR coupling. Two comparison families were useful:

| Model | Cabin half-size | Field tolerance | Representative constraint | Mass for `1g` | Mass for `0.01g` |
| --- | ---: | ---: | --- | ---: | ---: |
| Distant point mass | `1 m` | `~+/-10%` | keep `2h/d <= 0.1`, so `d ~= 20 m` | `5.9e13 kg` | `5.9e11 kg` |
| Distant point mass | `1 m` | `~+/-5%` | keep `2h/d <= 0.05`, so `d ~= 40 m` | `2.4e14 kg` | `2.4e12 kg` |
| Finite disk | `1 m` | `~+/-10%` | disk plane `2 m` behind center, `R ~= 11.5 m` | `1.2e13 kg` | `1.2e11 kg` |
| Finite disk | `1 m` | `~+/-5%` | disk plane `2 m` behind center, `R ~= 21.7 m` | `3.8e13 kg` | `3.8e11 kg` |
| Finite disk | `0.5 m` | `~+/-10%` | disk plane `1 m` behind center, `R ~= 5.8 m` | `2.9e12 kg` | `2.9e10 kg` |

The finite-disk calculation used `g_z = 2 pi G Sigma (1 - d/sqrt(d^2 + R^2))` at the cabin center and chose `R` so the first-order axial fractional variation over half-size `h` met the tolerance. A separate point-cell numerical check over the `3 x 3 x 3` cube samples found that the `2 m` cabin, `d = 2 m`, `R ~= 11.5 m` disk gives about `-9.8%` to `+10.3%` variation in field magnitude, with lateral components up to about `0.073g` at cube corners. Tightening to `+/-5%` requires `R ~= 21.7 m` and `3.8e13 kg` for `1g`.

**Reasoning:** Source-free cabin space is governed by a harmonic Newtonian potential, so the tidal tensor is traceless and derivative cancellation in one direction is not free. A constrained inverse-source problem with positive density can choose among many nonunique mass layouts, but non-uniqueness is not a rescue: all useful layouts still need enough integrated mass to create the central acceleration and enough source size or distance to suppress field variation. The disk is close to the best intuitive positive-mass family because it approaches the infinite-sheet limit, where the field is uniform; the price is surface density near `Sigma = g/(2 pi G) ~= 2.34e10 kg/m^2` for `1g` and large area. The point-mass comparison shows the opposite trade: moving the source away smooths the field, but mass grows as `d^2`.

**Failure or boundary found:** Constrained positive-mass optimization does not open a practical localized artificial-gravity route under known physics. Even the friendliest `0.01g`, `2 m` cabin, `+/-10%` finite-disk case is about `1e11 kg`; the `1g` version is about `1e13 kg`. These estimates ignore support structure, shielding, assembly, failure hazards, and the fact that the disk/plate itself would dominate the vehicle architecture.

**Blank space or new idea:** The positive-mass shape space is now blocked for practical cabin fields, but it leaves a useful design criterion for future speculative mechanisms: any non-rotational localized-field proposal should report the equivalent surface density or integrated stress-energy needed to beat the `~2e10 kg/m^2` infinite-sheet `1g` benchmark, plus the full 3D field variation over a cabin volume. The remaining open space is not better positive-mass geometry; it is source terms whose effective gravitational coupling, sign, or energy density differs from ordinary positive mass.

**Hypothesis updates:** H-010 is reinforced as rejected for practical localized gravity. Added H-011 to preserve the narrower failure of constrained positive-mass cabin optimization. Added B-012 as the new boundary. E-013 is complete.

**Next best step:** Run E-014: quantify high-energy-density radiation/plasma/source-term candidates, including laser cavities, radiation pressure, ICF-scale plasmas, antimatter/radiation storage, and whether any credible configuration beats the ordinary EM/positive-mass stress-energy scale without invoking new coupling.

## 2026-07-07 - Radiation And Plasma Source-Term Scale

**Focus question:** Can high-energy-density radiation, laser cavities, ICF-scale plasmas, pair plasma, or antimatter/radiation storage create gravitationally relevant localized stress-energy beyond the already-rejected ordinary EM and positive-mass benchmarks?

**Sources reviewed:** National Academies, *Fundamental Research in High Energy Density Science* (2023); Wurzel & Hsu, "Progress toward fusion energy breakeven and gain as measured against the Lawson criterion" (Physics of Plasmas, 2022; arXiv:2105.10954); DOE reporting on the 2022 NIF ignition shot; Sadler, Walsh, Zhou, and Li, "Role of self-generated magnetic fields in the inertial fusion ignition threshold" (Physics of Plasmas, 2022; arXiv:2203.08258); Ursescu, "Ultra-intense laser pulses and the High Power Laser System at Extreme Light Infrastructure - Nuclear Physics" (2021; arXiv:2105.05494); Ehlers, Ozsvath, Schucking, and Shang, "Pressure as a Source of Gravity" (2005; arXiv:gr-qc/0510041).

**What changed:** Completed E-014 as a scale screen. High-energy-density physics is genuinely extreme by laboratory standards, but its conventional threshold near `1e11 J/m^3` is still about `16.5` orders of magnitude below the crude `1 m` spherical `1g` benchmark, `u ~= 3.2e27 J/m^3`. A `1 m` sphere filled uniformly at `1e11 J/m^3` would have equivalent density `~1.1e-6 kg/m^3` and surface gravity only `~3.1e-16 m/s^2`.

Ultra-intense laser pulses improve the instantaneous energy-density number but not enough, and only for femtosecond/micron-scale volumes. An intensity `I = 1e23 W/cm^2 = 1e27 W/m^2` has traveling-wave energy density `u = I/c ~= 3.3e18 J/m^3`, about `9.0` orders below the `1g` meter-scale average. If, unrealistically, an entire `1 m` sphere were filled at that energy density, its surface acceleration would be only `~1.0e-8 m/s^2`; real pulses occupy tiny volumes for tiny durations, so their integrated gravitational field is much smaller.

The NIF/ICF comparison is a useful trap. A `3 MJ` fusion yield or laser pulse sounds enormous and can create astrophysically interesting plasma conditions, but its mass equivalent is only `E/c^2 ~= 3.3e-11 kg`. At `1 m`, that sources only `~2.2e-21 m/s^2`; even at `1 mm`, if all energy were concentrated as a compact source, the acceleration scale is only `~2.2e-15 m/s^2`. Concentrating `3 MJ` into a `50 um` hot spot gives a local energy density near `6e18 J/m^3`, but the total energy remains too small and the confinement time is far too short to act as useful artificial gravity.

**Reasoning:** Radiation, plasma thermal energy, magnetic fields, kinetic energy, antimatter annihilation products, and pair plasma all gravitate through stress-energy in standard GR. Pressure and anisotropic stress can change local source terms by order-unity factors; for an isotropic radiation fluid, the pressure contribution is not a path to a `10^9-10^16` multiplier. The dominant accounting remains total energy, volume, duration, and geometry. HED systems are excellent for testing materials, fusion burn physics, radiation transport, and plasma instabilities; they do not beat `G/c^2`.

**Failure or boundary found:** High-energy-density radiation/plasma source terms do not create a practical localized artificial-gravity route under known physics. They fail by the same invariant scale as ordinary EM stress-energy: accessible and even near-future laboratory energy densities are many orders too small when converted to gravitational source terms, and the highest peaks are pulsed, microscopic, destructive, and not shaped into a quasi-static cabin field. Antimatter does not change the conclusion; it is a compact energy-storage concept, not a new gravitational coupling. To get `1g` at `1 m` still requires total energy `~1.3e28 J`, regardless of whether that energy began as matter, antimatter, radiation, or plasma.

**Blank space or new idea:** The useful open space is no longer "more intense plasma." It is whether nonclassical radiation states, squeezed light, dynamical Casimir configurations, or engineered stress anisotropy can create a measurable stress-energy signature whose gravitational effect is detectable below the artificial-gravity threshold. That would be a precision-source experiment, not a human-scale gravity generator.

**Hypothesis updates:** Added H-012 and B-013: high-energy-density radiation/plasma source terms are real GR sources but rejected for practical localized artificial gravity under known coupling. H-002 remains the umbrella for source-term engineering, but it should no longer treat ICF, ultra-intense lasers, or antimatter/radiation storage as scale escapes without a new coupling or nonclassical stress-energy argument.

**Next best step:** Run E-015: review squeezed-light, dynamic Casimir, and nonclassical radiation stress-energy proposals, asking only whether they offer a clean precision-gravity source or stress-anisotropy test, not whether they can produce human-scale artificial gravity.

## 2026-07-08 - Nonclassical Radiation Stress-Energy

**Focus question:** Can squeezed light, dynamic Casimir radiation, or related nonclassical electromagnetic states produce a distinctive gravitationally relevant stress-energy signal worth a precision experiment, without claiming human-scale artificial gravity?

**Sources reviewed:** Ford and Roman, "Negative Energy in Superposition and Entangled States" (2007; arXiv:0705.3003); Wilson et al., "Observation of the Dynamical Casimir Effect in a Superconducting Circuit" (Nature 2011; arXiv:1105.4714); Ford and Roman, "Negative Energy Seen By Accelerated Observers" (Physical Review D 2013; arXiv:1302.2859); Fewster and Roman, "Null energy conditions in quantum field theory" (Physical Review D 2003; arXiv:gr-qc/0209036); Schnabel, "Squeezed states of light and their applications in laser interferometers" (Physics Reports 2017; arXiv:1611.03986); Maclay and Davis, "Testing a Quantum Inequality with a Meta-analysis of Data from Squeezed Light" (Foundations of Physics 2019; arXiv:1806.01269).

**Deepening work completed:** Reviewed more than three source types: QFT stress-energy calculations, a dynamic-Casimir experiment, squeezed-light metrology, and QI nuance papers. Ran a single-mode squeezed-state scale check over `10-30 dB` squeezing and over photon wavelengths from optical to gamma-ray scale. Compared the result against B-008 ordinary EM stress-energy, B-009 Casimir/QEI constraints, and B-013 classical radiation/plasma limits. Audited the hidden assumption that "negative normal-ordered energy density" can be treated as a freely accumulable negative mass density. Converted the failure into E-016, a precision-source/null-test design task.

**What changed:** E-015 is complete as a first-pass screen. Nonclassical radiation states are real and useful for quantum optics and precision measurement, but they do not change the artificial-gravity scale. In a one-mode traveling-wave model used by Ford and Roman, the normal-ordered energy density has the form `rho = (hbar omega / V) [n + R cos(...)]`, so a negative dip needs `R > n` and has minimum `rho_min = -(hbar omega / V)(R - n)`. For a single-mode squeezed vacuum, `n = sinh^2 r` and `R = sinh r cosh r`, so `R - n` approaches only `1/2` as squeezing grows. A `15 dB` squeezed vacuum has `r ~= 1.73`, `n ~= 7.4`, and `R - n ~= 0.48`: the local negative trough is at most about half a photon energy per mode volume, while the mean positive energy in the mode is several photons.

**Reasoning:** This is a useful distinction. Squeezed and superposed quantum states can create negative normal-ordered energy density relative to the vacuum, so H-003's theoretical crack is real. But the same calculation shows why it is not a macroscopic source term. At `lambda = 1064 nm`, even the deliberately optimistic scale `0.5 h nu / lambda^3` is only `~0.08 J/m^3`, about `4e28` times below the `1 m` spherical `1g` benchmark `u ~= 3.2e27 J/m^3`. At `lambda = 1 nm`, the same cubic-wavelength estimate rises to `~1e11 J/m^3`, comparable to HED science but still `~3e-17` of the `1g` benchmark. Matching the benchmark with a half-photon-per-cubic-wavelength estimate would require `lambda ~= 7.5e-14 m`, i.e. hard gamma-ray scale, before adding production, localization, bandwidth, compensation, apparatus energy, and QEI constraints. Dynamic Casimir radiation in the Wilson experiment is important because it produced real microwave photons and two-mode squeezing from a modulated superconducting boundary, but its `~11 GHz` photons carry only `~7.3e-24 J` each; the effect validates nonclassical field dynamics, not a large gravitational source.

**Failure or boundary found:** Nonclassical radiation does not rescue localized artificial gravity under known physics. Negative or subvacuum stress-energy features are oscillatory, state-dependent, bandwidth-limited, accompanied by positive energy, and constrained by quantum inequalities or related averaged conditions depending on observer and sampling. Accelerated-observer and null-averaging results are important cracks in naive energy-condition language, but Ford/Roman and Fewster/Roman both preserve the key engineering conclusion: they do not permit separable macroscopic negative-energy reservoirs for wormholes, warp metrics, or cabin-scale gravity fields.

**Blank space or new idea:** The remaining opportunity is a precision-source experiment, not a gravity generator. A deliberately modulated squeezed-light or dynamic-Casimir source might create a known, phase-tagged stress-energy expectation value or stress-correlation signal, allowing a null test of semiclassical source accounting, pressure/stress gravity, or detector response. The likely gravitational signal is far below present direct force sensitivity, so the next useful work is to calculate it honestly and compare it with torsion-balance, atom-interferometer, and optomechanical backgrounds before proposing hardware.

**Hypothesis updates:** Added H-013 and B-014: squeezed-light, dynamic-Casimir, and nonclassical radiation configurations are rejected as practical localized artificial-gravity sources under known coupling, but retained as possible precision-source or semiclassical-gravity testbeds. H-003 remains speculative and theory-relevant; H-002 is narrowed again to require full stress-energy accounting, not just a nonclassical label.

**Next best step:** Run E-016: design a quantitative precision-source/null experiment for modulated nonclassical electromagnetic stress-energy, estimating signal size, modulation frequency, detector class, shielding/confounders, and the exact hypothesis that a null or detection would update.

## 2026-07-09 - Modulated Nonclassical EM Null-Test Scale

**Focus question:** Could a modulated squeezed-light or dynamic-Casimir electromagnetic source produce a gravitational signal distinguishable from ordinary stored optical/rf power, and what would a rigorous null experiment actually test?

**Sources reviewed:** Ratzel, Wilkens, and Menzel, "Gravitational properties of light - The gravitational field of a laser pulse" (New Journal of Physics 2016; arXiv:1511.01023); Kuo and Ford, "Semiclassical Gravity Theory and Quantum Fluctuations" (Physical Review D 1993; arXiv:gr-qc/9304008); Panda et al., "Measuring gravity by holding atoms" (Nature 2024; arXiv:2310.01344); Ranjit et al., "Zeptonewton force sensing with nanospheres in an optical lattice" (Physical Review A 2016; arXiv:1603.02122); Lee et al., "New Test of the Gravitational 1/r^2 Law at Separations down to 52 um" (Physical Review Letters 2020; arXiv:2002.11761). Prior E-015 squeezed-light/DCE sources were reused for source-scale context.

**Deepening work completed:** Reviewed more than three detector/source-quality sources, including one that complicates the semiclassical-source picture by emphasizing stress-tensor fluctuations in negative-energy states. Ran a sensitivity check over modulated source energies from `1 J` to `1 MJ` and distances from `1 mm` to `1 m`. Built an independent detector-threshold bound by asking how much modulated energy would be needed to match a `6.2 nm/s^2` atom-interferometer acceleration. Compared against B-008, B-013, and B-014. Audited confounders: pump energy, apparatus mass motion, EM pickup, thermal expansion, radiation pressure, vibrations, shielding currents, and the distinction between stress-energy expectation value and fluctuations.

**What changed:** E-016 is complete as a feasibility screen. A modulated nonclassical EM source can be specified cleanly in principle, but its direct gravitational signal is far below current detector reach unless the experiment modulates enormous ordinary energy. Treating any source energy change `delta E` as a compact optimistic source gives

| `delta E` | `r = 1 mm` | `r = 0.1 m` | `r = 1 m` |
| ---: | ---: | ---: | ---: |
| `1 J` | `7.4e-22 m/s^2` | `7.4e-26 m/s^2` | `7.4e-28 m/s^2` |
| `1 kJ` | `7.4e-19 m/s^2` | `7.4e-23 m/s^2` | `7.4e-25 m/s^2` |
| `1 MJ` | `7.4e-16 m/s^2` | `7.4e-20 m/s^2` | `7.4e-22 m/s^2` |

The Panda atom-interferometer benchmark reports `6.2 nm/s^2` combined accuracy, so matching that acceleration by source energy alone would require about `8.3e12 J` at `1 mm`, `8.3e16 J` at `0.1 m`, or `8.3e18 J` at `1 m`. A levitated-nanosphere force benchmark sounds more sensitive in force units, but for a `~300 nm` silica sphere the `1 J`, `1 mm` gravitational force is only `~1.8e-37 N`, roughly `15-16` orders below a zeptonewton.

**Reasoning:** The cleanest experimental topology would modulate a squeezed-light or DCE state at a phase-tagged frequency while keeping classical pump power, cavity temperature, mirror motion, and electromagnetic leakage independently monitored. The nominal observable would be a detector response at the source modulation frequency and phase, compared with a classical coherent-state/control source with the same mean stored energy and apparatus state. Under standard semiclassical gravity, however, the gravitational channel couples to the full stress-energy expectation value plus whatever fluctuation/noise model is appropriate, not to the word "nonclassical." Kuo and Ford sharpen the boundary: negative-energy and squeezed-state regimes can have large stress-energy fluctuations, so a fixed classical metric sourced only by a smooth negative expectation value may be the wrong target observable. Ratzel et al. also warn that light-pulse gravity is tied to the complete emission/propagation/absorption stress-energy history, not just a stationary lump of optical energy.

**Failure or boundary found:** No near-term direct gravity experiment can isolate the gravitational field of modulated nonclassical EM stress-energy at the available source-energy scale. Any apparent detection would almost certainly first be a test of ordinary systematics unless it passes same-energy coherent-state controls, dummy heat loads, phase reversal, distance scaling, shielding variation, and source-off blind injections. A null result would not strongly constrain QFT negative energy or quantum inequalities; it would mostly confirm that `G delta E/(c^2 r^2)` is too small. A positive result at accessible energies would imply either a very large systematic error or a beyond-standard coupling, because standard coupling predicts a signal many orders below detector benchmarks.

**Blank space or new idea:** The useful experiment is not a direct gravity-source detection yet. The blank space is a source-accounting protocol: define the exact stress-energy expectation, variance, compensation, and apparatus-energy budget for a real squeezed/DCE source, then derive the gravitational observable that would be tested if detectors improved by many orders of magnitude. This could also clarify which semiclassical-gravity assumption is actually under test: smooth `<T_ab>` sourcing, stress-tensor noise, pressure/stress coupling, or detector response to nonclassical fields.

**Hypothesis updates:** Added H-014 and B-015. H-013 remains rejected for practical artificial gravity; its precision-test remnant is narrowed to "bookkeeping and null-protocol design" rather than a credible near-term gravitational detection. H-005 gains a concrete detector-benchmark path.

**Next best step:** Run E-017: build a complete stress-energy bookkeeping template for a real optical squeezed-light cavity or superconducting DCE source, including mean energy, negative/subvacuum component, stress-tensor variance, pump/boundary energy, heat loads, mechanical motion, and the control states needed before any gravity claim.

## 2026-07-10 - Closed Stress-Energy Ledger For Nonclassical EM Sources

**Focus question:** What complete stress-energy bookkeeping is required before a real squeezed-light cavity or superconducting dynamic-Casimir source could support any gravitational or semiclassical-source claim, and can nonclassical-state switching be isolated from ordinary apparatus energy?

**Sources reviewed:** Schönbeck, Thies, and Schnabel, "13 dB squeezed vacuum states at 1550 nm from 12 mW external pump power at 775 nm" (Optics Letters 2018); Wilson et al., "Observation of the Dynamical Casimir Effect in a Superconducting Circuit" (Nature 2011); Johansson et al., "The dynamical Casimir effect in superconducting microwave circuits" (Physical Review A 2010; arXiv:1007.1058); Hu and Verdaguer, "Stochastic Gravity: Theory and Applications" (Living Reviews in Relativity 2008; arXiv:0802.0658); Kuo and Ford 1993 and the E-015/E-016 sources for fluctuation and detector context.

**Deepening work completed:** Reviewed two real source architectures plus a stochastic-gravity framework, including Hu/Verdaguer's complication of a mean-field-only conclusion. Ran a squeezing/mode-rate sensitivity estimate from `1-1000 MHz`. Built an independent pump-per-modulation-cycle comparison over `1 Hz-1 MHz`. Compared against B-008, B-014, and B-015. Audited conservation, source/absorber history, losses, heat, mechanical recoil, electromagnetic leakage, and the distinction between mean field and connected correlations. Converted the remaining unclear space into E-018 with an explicit target observable.

**What changed:** E-017 is complete. The required artifact is a four-ledger source model:

| Ledger | Quantity to report | Why it cannot be omitted |
| --- | --- | --- |
| Mean field | Spatially resolved `<T_ab>`, spectrum, bandwidth, stored and emitted energy, momentum and pressure | Sources the leading semiclassical metric |
| Subvacuum term | Renormalization reference, negative region, sampling time/volume, compensating positive energy | Prevents treating a local negative trough as free negative mass |
| Fluctuations | Connected `<T_ab(x)T_cd(y)>`, smearing, phase and correlation spectrum | Defines any stochastic-gravity contrast beyond the mean |
| Apparatus | Pump/flux-line energy, cavity/crystal/SQUID/boundary energy, losses, heat, recoil, strain, shielding currents, source and absorber | Enforces conservation and exposes much larger ordinary backgrounds |

The minimum control matrix is: source-off; pump-on but detuned/no squeezing; coherent or thermal state matched in mean energy and spectrum; squeezing-phase reversal at fixed mean; dummy heat; dummy electromagnetic drive; distance/orientation changes; and blinded signal injection. Every state needs synchronized calorimetry, displacement/strain, field leakage, and phase-transfer measurements.

**Reasoning:** For ideal `13 dB` squeezed vacuum, `exp(-2r)=10^-1.3` gives `r ~= 1.50` and `n = sinh^2 r ~= 4.5`. At `1550 nm`, one photon carries `~1.28e-19 J`, so the mean excitation is `~5.8e-19 J` per mode and the one-mode negative trough is bounded near `~6.4e-20 J`. Even an illustrative `100 MHz` stream is only `~5.8e-11 W`, versus the demonstrated `12 mW` pump, a ratio `~4.8e-9`; the `1-1000 MHz` range remains `~4.8e-11` to `~4.8e-8`. At `1 kHz` switching, the pump supplies `12 uJ` per cycle, about `2e13` times one mode's mean excitation; over `1 Hz-1 MHz`, that comparison ranges from `~2e16` to `~2e10`. These are conservative scale comparisons, not claims about the paper's exact mode count or stored cavity energy.

The DCE ledger reaches the same conclusion independently. The superconducting experiment modulates a SQUID boundary near `11 GHz`; the emitted real photons and two-mode squeezing are powered by the external flux modulation. Therefore pump-line energy, Josephson/SQUID energy, emitted radiation, attenuation, heating, and electromagnetic reaction are part of the source. DCE does not supply a detached vacuum-energy reservoir.

**Failure or boundary found:** Nonclassicality cannot be toggled as though it were an additional conserved source term. Under standard semiclassical gravity, matched states with the same `<T_ab>` have the same leading mean-field prediction. If their fluctuations differ, the proposed observable must be derived from a smeared noise kernel or source-probe correlation; it is not a deterministic extra acceleration. Any experiment that changes pump power, heat, boundary drive, or mean stored energy while changing squeezing is dominated conceptually and practically by those ordinary terms.

**Blank space or new idea:** The mean-field route is blocked at accessible energy. The remaining blank space is **unclear**, not merely unengineered: can two states with matched mean `<T_ab>` but different connected stress correlations produce an operationally distinct probe-correlation spectrum after realistic spatial/temporal smearing? This asks a precise stochastic-gravity question without implying useful artificial gravity or FTL travel.

**Hypothesis updates:** Added H-015 and B-016. H-015 remains low-confidence because stochastic gravity identifies a formal noise-kernel channel, but no source/probe observable or credible sensitivity follows until smearing, bandwidth, geometry, and ordinary quantum back-action are specified.

**Next best step:** Run E-018: choose one idealized single-mode squeezed source and one simple probe, define a finite sampling function, calculate the connected stress-tensor noise kernel and predicted probe correlation spectrum for equal-mean coherent and squeezed states, and determine whether the proposed signature is distinct even in principle from electromagnetic quantum back-action.

## 2026-07-11 - Smeared Nonclassical Stress-Energy Noise Versus Back-Action

**Focus question:** For one idealized cavity mode and simple probe, do equal-mean coherent and squeezed states produce different smeared gravitational probe spectra, and is that difference operationally distinct from ordinary electromagnetic quantum back-action?

**Sources reviewed:** Hu and Verdaguer, "Stochastic Gravity: A Primer with Applications" (Classical and Quantum Gravity 2003; arXiv:gr-qc/0211090) and their 2008 Living Reviews update; Clark et al., "Observation of Strong Radiation Pressure Forces from Squeezed Light on a Mechanical Oscillator" (Nature Physics 2016; arXiv:1601.02689); Yap et al., "Broadband reduction of quantum radiation pressure noise via squeezed light injection" (2019; arXiv:1812.09804); prior Kuo/Ford, Schonbeck et al., and E-017 notes.

**Model and smearing:** Defined the spatially smeared source energy `E_f(t)=int d^3x f(x) T_00(x,t)` over one full cavity mode. Temporal sampling is slow compared with the optical period, so phase-sensitive terms at `2omega` average away; they would have to be restored for sub-cycle sampling. The source is stationary, the probe is outside the compact source at distance `r`, and `Omega r/c << 1`. A driven coherent state and squeezed vacuum share the same mode and mean photon occupation `N`. The remaining connected source variable is `delta E=hbar omega delta n`.

For the ideal states, `Var_coh(n)=N` and `Var_sq(n)=2N(N+1)`. Assuming the explicit cavity model `<delta n(t)delta n(0)>=Var(n) exp(-kappa|t|)`, the two-sided energy-noise spectrum is

`S_E(Omega)=2(hbar omega)^2 Var(n) kappa/(kappa^2+Omega^2)`.

In the optimistic compact, quasi-static gravitational approximation,

`S_a(Omega)=[G/(c^2 r^2)]^2 S_E(Omega)`.

This is a bounding model, not a full Einstein-Langevin solution: it omits tensor and angular factors, cavity-wall stress and recoil, pump and loss ports, and retarded conservation effects. Those omissions can change or cancel parts of the exterior spectrum; they cannot increase the absolute source energy enough to rescue detectability.

**Quantitative screen:** Using the E-017 scale `lambda=1550 nm`, `N=4.5`, an illustrative `kappa/2pi=100 MHz`, and the optimistic separation `r=1 mm`, the low-frequency acceleration amplitudes are `~1.14e-44 m/s^2/sqrt(Hz)` for the coherent state and `~3.78e-44 m/s^2/sqrt(Hz)` for squeezed vacuum. The squeezed/coherent PSD ratio is `2(N+1)=11` and the amplitude ratio is `sqrt(11)~=3.32`. The formal contrast is real in the model, but both spectra are roughly `35` orders below the `~nm/s^2` acceleration scale previously used as an atom-interferometer benchmark.

**Back-action comparison:** A reflecting probe inside the field experiences ordinary radiation-pressure fluctuations `delta F_EM~2 delta E/L`; its gravitational force is only `delta F_g~Gm delta E/(c^2r^2)`. Thus `delta F_g/delta F_EM~GmL/(2c^2r^2)`, about `3.7e-24` even for a generous `m=1 kg`, `L=1 cm`, `r=1 mm`. Clark et al. and Yap et al. experimentally establish that squeezed-field statistics do drive mechanical radiation-pressure spectra. Therefore a state-correlated mechanical signal is expected electromagnetically and is not a gravitational discriminator.

**Established physics:** Connected stress-tensor correlations are the source object in stochastic gravity; coherent and squeezed states can have different photon-number and stress correlations; squeezed radiation-pressure back-action is experimentally observed; standard gravitational coupling retains the `G/c^2` source suppression.

**Strongly modeled:** The Lorentzian spectrum follows from the stated stationary exponential cavity-correlation model. The compact Newtonian transfer is an optimistic low-frequency approximation, not a precision tensor solution.

**Speculative or unclear:** Whether a complete conserved cavity-plus-wall source retains this naive exterior monopole noise, or whether wall recoil and center-of-energy conservation redistribute it into higher multipoles and loss-port or retarded correlations. No artificial-gravity or FTL capability follows either way.

**Failure or boundary found:** A mathematically distinct nonclassical noise kernel is not an operationally isolated gravity signal. Direct EM back-action carries the same state tag at least `~23` orders more strongly in the generous comparison, while an externally shielded probe forces the calculation to include wall and support motion and the complete apparatus stress tensor. This rejects H-015 for now as a realizable isolation strategy without denying the formal stochastic-gravity distinction.

**Hypothesis and boundary updates:** Completed E-018, changed H-015 to rejected for now as an isolatable experiment, and added B-017. The result strengthens rather than evades B-015 and B-016.

**Next best step:** Run E-019: model a closed one-dimensional cavity plus movable walls and supports and a loss port, enforce total stress-energy and center-of-energy conservation, and calculate the exterior gravitational multipole and noise spectrum seen by a mechanically and electromagnetically isolated probe. The decisive question is whether internal photon-number noise survives as an exterior monopole source or only as much smaller redistributed multipole or retarded stress correlations.

## 2026-07-11 - E-019 Conserved Cavity Model, First Stage

**Focus question:** Before solving the complete tensor problem, what does explicit energy and center-of-energy conservation do to the optimistic exterior field from a cavity energy fluctuation?

**Artifact built:** Added `models/e019_conserved_cavity.py`, its model notes, and a standard-library verification suite. The model compares three one-dimensional weak-field source ledgers: a deliberately incomplete field-only source, a closed cavity that transfers energy from wall-localized reservoirs into the field, and an emitted pulse whose source support recoils by momentum conservation.

**What changed:** In the scalar `T00` model, the field-only estimate retains the compact-source acceleration `G deltaE/(c^2 r^2)`. Closing the perturbation-energy ledger sets the exterior monopole moment `I_0` to zero. Holding the center of energy fixed sets the dipole moment `I_1` to zero. The first surviving term is then

`delta a_x(r) = -(3G/c^2) I_2/r^4 + higher moments`.

For a symmetric cavity of length `L`, with `deltaE` moved from equal wall reservoirs into a central field mode, `I_2 = -deltaE L^2/4`, so the leading acceleration magnitude is `3G deltaE L^2/(4c^2 r^4)`. With `deltaE=1 J`, `L=0.01 m`, and `r=1 m`, the incomplete field-only estimate is `7.43e-28 m/s^2`, while the closed-ledger exact point model gives `5.57e-32 m/s^2`, a factor `7.5e-5` as large. A radial sweep converges to `r^-4.00000`.

The pulse scenario gives the same qualitative result. A right-moving pulse has position `ct` and momentum `deltaE/c`; the emitting support's first-order recoil displacement `-deltaE t/(Mc)` cancels the pulse's changing center-of-energy dipole. The first-order exterior perturbation again begins at a higher moment. The cancellation is independent of support mass because `M delta x` is fixed by momentum conservation.

**Established physics represented:** Weak-field energy sourcing, total-energy bookkeeping, center-of-energy conservation, photon momentum, source recoil, and the exterior point-source multipole expansion.

**Strongly modeled:** The signed point-energy distribution and first-order recoil derivative are a transparent conservation screen. They show that treating the fluctuating field alone creates a spurious exterior monopole and, for an emitted pulse, a spurious dipole.

**Still unclear:** This is not yet a divergence-free tensor source. It omits mirror pressure, support stress, momentum density, pump and absorber dynamics, retarded Green functions, gauge issues, and the exact stochastic noise kernel of the complete apparatus. A full solution could cancel or reshape the scalar quadrupole; it cannot restore a changing monopole for a closed, conserved system under standard GR.

**Sources checked:** Ratzel, Wilkens, and Menzel 2016 for emission/pulse/absorption structure in linearized gravity; Phillips and Hu 2000 for the stochastic-gravity noise-kernel source object; Gratus, Pinto, and Talaganis 2020 for the additional structure carried by a genuine stress-energy quadrupole.

**Next best step:** Upgrade the model from signed `T00` points to a conserved discretized `T^{mu nu}` for the field, mirrors, supports, pump, and absorber. Solve the retarded linearized Einstein equations and compare a gauge-invariant exterior tidal observable against the scalar quadrupole bound.

## 2026-07-11 - E-019 Divergence-Free Tensor And Retarded Tidal Model

**Focus question:** Does the scalar E-019 quadrupole survive when the source is promoted to a divergence-free `T^{mu nu}`, propagated retardedly, checked in harmonic gauge, and evaluated through a gauge-invariant tidal observable?

**Artifact built:** Added `models/e019_conserved_tensor.py` and a second verification suite. The source is a compact one-dimensional effective total-apparatus perturbation generated by a spatial superpotential `P(x)` with harmonic amplitudes `tau00=P''`, `tau0x=i(omega/c)P'`, and `tauxx=-(omega/c)^2 P`. These relations make both nontrivial components of `partial_mu T^{mu nu}=0` vanish by construction. The central positive `T00` region represents the field-energy perturbation, while the negative outer perturbation, energy flux, and longitudinal stress close the apparatus ledger.

**Retarded solution:** Propagated all tensor components with the 3+1 dimensional retarded kernel `exp(i k R)/R`, un-trace-reversed the metric, checked `partial_mu bar(h)^{mu nu}=0`, and calculated `R_0x0x`. Analytic first and second derivatives of the retarded kernel removed finite-difference ambiguity. The deliberately incomplete positive-`T00`-only comparison has a normalized `nu=0` harmonic-gauge residual of `1`; the conserved source converges from about `1.2e-5` at 501 cells to `3.0e-9` at 4001 cells, while its tidal result changes by less than `1e-5`.

**What changed:** A nonzero exterior tidal channel survives conservation. For `deltaE=1 J`, `L=1 cm`, `f=100 MHz`, and an axial probe at `1 m`, `|K_xx| ~= 2.04e-31 s^-2`, corresponding to `~2.04e-31 m/s^2` differential acceleration over a deliberately generous `1 m` baseline. The low-frequency limit matches the instantaneous `T00` tidal result. At `100 MHz`, energy flow, stress, and retardation raise the model result by a factor `~2.15` over that static benchmark; this is a tensor redistribution, not a restored monopole.

**Stress-budget finding:** Higher frequency is not a free enhancement. For this conserved family, `integral|Txx|/deltaE` is `~2.34e-9` at `1 MHz`, `~2.34e-5` at `100 MHz`, `~0.234` at `10 GHz`, and scales as `(omega L/c)^2`. Cases with enormous dynamic response also require enormous support-stress perturbations and cannot be interpreted without a much larger apparatus-energy baseline.

**Stochastic projection:** Because the deterministic transfer is nonzero and gauge-consistent, projected the E-018 exponential photon-number noise through it. For `1550 nm`, `N=4.5`, and `kappa/2pi=100 MHz`, the default `1 m` configuration gives one-sided relative-acceleration ASD `~3.13e-54 m/s^2/sqrt(Hz)` for a coherent state and `~1.04e-53 m/s^2/sqrt(Hz)` for squeezed vacuum. The amplitude ratio `sqrt(11) ~= 3.32` survives exactly. Moving the probe just outside the `1 cm` source, to `x=6 mm`, still gives only `~2.57e-46 m/s^2/sqrt(Hz)` over a `0.1 mm` baseline.

**Boundary found:** The blank space is resolved at bounded-model level. Conservation does not force every exterior fluctuation to zero; it removes the spurious changing monopole and dipole and leaves a formal higher-moment tidal channel. That channel is even less useful experimentally than the optimistic E-018 compact-source estimate. The formal stochastic-gravity distinction remains, but no localized artificial-gravity or practical precision-source path emerges.

**Remaining caveat:** The conserved source is an effective line tensor, not a microscopic finite-radius optical cavity with separately modeled mirrors, springs, pump, loss port, and absorber. Such a decomposition could redistribute multipoles or angular response. It would need an orders-of-magnitude enhancement to change the detectability conclusion and cannot restore a changing monopole for a closed system.

**Hypothesis and boundary updates:** E-019 is complete at bounded-model level; H-015 is reinforced as rejected for an isolatable experiment; B-018 added.

**Next best step:** Return the active localized-field queue to mechanism-level blank spaces such as modified-coupling candidates, anomalous claims with strong replication standards, or analog-gravity mathematical tools. Reopen the explicit apparatus tensor only if a concrete source architecture supplies a defensible stress/energy ledger that could change B-018 by many orders of magnitude.

## 2026-07-12 - Canonical Chameleon Body Screening Versus Cabin Loading

**Focus question:** Can an environmentally screened scalar field, using the canonical inverse-power chameleon as the concrete case, produce a body-scale, approximately universal localized acceleration inside a spacecraft-sized vacuum region while remaining compatible with laboratory fifth-force tests?

**Scope and epistemic status:** This run studied the passive, universally conformal, `n=1`, `Lambda=2.4 meV` chameleon benchmark. A chameleon field is hypothetical; it is not an established gravity generator. The calculation is a necessary-condition screen for a fifth force inside a matter-bounded cabin, not a theorem against every scalar potential, active boundary condition, or screened-gravity theory. It does not enable FTL travel or reactionless propulsion.

**Sources reviewed:** Khoury and Weltman's original effective-potential and thin-shell papers; Hui, Nicolis, and Stubbs on macroscopic equivalence-principle violation; Burrage et al. on chamber/source shape; Sabulsky et al., Yin et al., and Panda et al. on atom/force-sensor searches; the 2023 correction to Jaffe et al.; Fischer, Kading, and Pitschmann on updated screening-charge constraints; Upadhye, Hu, and Khoury on quantum stability; Wang, Hui, and Khoury on generalized-chameleon no-go results; and the 2026 Banks et al. long-baseline proposal and Feleppa et al. near-Earth bounds. The latter two are important complications: broader screened-scalar parameter spaces remain scientifically testable, while low-density space is not an unconstrained refuge.

**Artifact built:** Added `models/e020_chameleon_body_screening.py`, model notes, and a verification suite. The code evaluates the chamber-limited field, a body's thin-shell scalar charge, a smooth-gradient acceleration envelope, an independent spherical two-body envelope with non-overlap enforced, a counterfactual no-source-screening mass-equivalent, and the field requirements of a deliberately formal externally driven alternative.

**Canonical benchmark equations:** For

`V(phi) = Lambda^(4+n)/phi^n`

and conformal coupling `beta/M_Pl`, the optimistic size-limited chamber field is

`phi_bg ~= xi [n(n+1) Lambda^(4+n) L^2]^(1/(n+2))`,

with `xi=1` used as a favorable benchmark. A spherical body's scalar charge is bounded by

`q <= min[1, phi_bg/(2 beta M_Pl Phi_body)]`,

where `Phi_body=GM/(Rc^2)` and the positive interior field has been omitted. The body acceleration from a full chamber-scale excursion is therefore

`a_phi <= beta q c^2 phi_bg/(M_Pl L)`.

For two passive spheres in the same fixed background, the long-range expression

`a_phi = 2 beta^2 q_source q_target G M_source/r^2`

gives the independent benchmark envelope

`a_phi <= c^2 phi_bg^2 R_source/(2 M_Pl^2 Phi_target r^2)`.

The latter assumes canonical positive-field thin-shell behavior, a common fixed background, approximate spherical bodies, and an unsuppressed range factor. Finite range, the positive interior field, and published geometry coefficients below one reduce the result.

**Human-scale result:** For a `70 kg`, `0.3 m` homogeneous-sphere proxy and target `0.01g`:

| Chamber scale `L` | `phi_bg` | screening transition `beta` | passive body ceiling | `0.01g / ceiling` |
| ---: | ---: | ---: | ---: | ---: |
| `1 m` | `1.599 eV` | `1.895e-3` | `1.119e-13 m/s^2` | `8.77e11` |
| `10 m` | `7.423 eV` | `8.796e-3` | `2.410e-13 m/s^2` | `4.07e11` |
| `100 m` | `34.45 eV` | `4.083e-2` | `5.192e-13 m/s^2` | `1.89e11` |

In the screened, size-limited regime `a_max` grows only as `L^(1/3)`. Chamber size therefore cannot repair a roughly twelve-order gap; naive extrapolation would require a scale far beyond the regime where the chamber model is meaningful. At `beta=1`, even the deliberately favorable `xi=1` inversion needs `L ~= 1.21e4 m` merely to keep the human proxy unscreened. Published `xi<1` values push that scale upward.

**Source self-consistency:** Requiring the human proxy to remain unscreened in the `1 m` case limits `beta` to the optimistic `1.895e-3`, making a fully unscreened source-target scalar force only `2 beta^2 ~= 7.18e-6` of Newtonian attraction. Converting `0.01g` at `1 m` while pretending the source remains unscreened gives `2.05e14 kg`, but this is not a realizable lower bound: the source would screen long before reaching that mass. In a body-fitting non-overlapping example with `R_source=0.5 m` and center separation `0.8 m`, the source can remain unscreened at the target transition only up to `~117 kg`, and the pair acceleration is then `8.74e-14 m/s^2`, exactly the finite-geometry two-body ceiling. Increasing source mass does not escape the plateau.

**Universality failure:** At `beta=1` in the same optimistic `1 m` background, an atomic or `1 g`, `1 cm` proxy remains unscreened and receives `5.90e-11 m/s^2`; a `1 kg`, `0.1 m` proxy receives `2.61e-12 m/s^2`; the human proxy receives `1.12e-13 m/s^2`. Microscopic universality of the action therefore does not produce macroscopic universality: extended bodies screen according to compactness. A cabin field would load atoms, air, tools, organs, and the hull differently, unlike an ordinary GR gravitational field. The conformal fifth-force channel is also not automatically shared by light, so it is not equivalent to a universal GR field.

**Sensitivity checks:** Taking a `1 mm` rather than `1 m` gradient scale raises the local human force envelope only to `~1.12e-10 m/s^2`, still `8.8e8` below `0.01g` and no longer a uniform body-scale field. A source-shape gain of order three, as found in numerical chameleon studies, is similarly irrelevant to the gap. Positive inverse-power indices `n=2,4,10` produced lower chamber fields and lower ceilings in this fixed-`Lambda` normalization. These are robustness checks, not model-independent exclusions.

**Experimental boundary:** Panda et al. measured `33.3 +/- 6.2 nm/s^2`, consistent with the calculated Newtonian attraction, and report a geometry-specific `|a_anomaly| < 13 nm/s^2` at 95% confidence. Yin et al. report `F < 5.7e-17 N` and close an important coupling gap. Combined data are reported to exclude the natural parameter space of the basic `Lambda=2.4 meV` chameleon, not all screened scalars. The `13 nm/s^2` number is not a universal field ceiling and should not be applied directly to a screened human body. The corrected Jaffe result, not its original source-gravity value, must be used; updated neutron screening charges also erase several historical frontier claims.

**Established physics:** The laboratory null measurements; ordinary momentum conservation; and the fact that an internal scalar source and the cabin receive the equal-and-opposite reaction. An internal fifth-force generator could at most redistribute loading inside a craft; it cannot accelerate the closed craft reactionlessly.

**Strongly modeled conditional result:** If the canonical chameleon equations and passive screened-cabin assumptions are adopted, body screening creates a strength-versus-universality trade: weak coupling keeps a person unscreened but leaves the force weaker than gravity, while strong coupling screens the person and source so that acceleration saturates. This closes the specific passive canonical benchmark as a useful artificial-gravity route.

**Speculative crack, quantified rather than endorsed:** A wholly unscreened craft in a sufficiently large ambient field, or a separately specified actuator that maintains a much larger nonuniform scalar background, evades the passive chamber estimate algebraically. For an actively maintained, fully unscreened human proxy at `beta=1`, `0.01g` across `1 m` needs an optimistic field floor near `844 eV` plus a `2.657 GeV` excursion. The canonical gradient term alone is `~2.87e6 J/m^3`. Because the floor scales as `beta` while the excursion scales as `1/beta`, balancing them occurs near `beta ~= 1.77e3`, where both are `~1.50 MeV` and the gradient term is only `~0.91 J/m^3`. Thus ordinary energy-density scaling is not, by itself, a no-go theorem for a genuinely new strongly coupled field. The missing content is decisive: no experimentally allowed scalar actuator, screened-hull penetration solution, full potential/matter/backreaction calculation, quantum-valid EFT, or reaction architecture has been supplied. A high offset without a gradient produces no acceleration. This is a new-source assumption, not a chameleon device.

**Blank space or new idea:** A co-located "screening ladder" using atoms, microspheres, gram-scale bodies, and kilogram-scale bodies in the same modulated source field would test the predicted acceleration-versus-compactness curve rather than one absolute force. Varying chamber size and gas density would add a second signature. This would distinguish a screened fifth force from a universal gravity-like response, but it should target an allowed generalized model rather than the excluded basic benchmark.

**Hypothesis and boundary updates:** Added H-016 and B-019. Completed E-020. The passive canonical chameleon is rejected for useful cabin loading; generalized potentials, open-space boundary conditions, and active scalar sourcing remain separate questions.

**Next best step:** Run E-021 on a finite planar derivative-screened source. Galilean symmetry can preserve scalar charge-to-mass better than chameleon thin shells, and an exactly infinite plane makes the Galileon nonlinear terms vanish. The exact planar limit is singular and finite edges restore nonlinear behavior. Start from the optimistic free-scalar plane, `a_phi=4 pi G beta^2 Sigma`, which already requires `Sigma ~= 1.17e8/beta^2 kg/m^2` for `0.01g`; then include finite radius, cabin uniformity, Earth-background kinetic renormalization, current laboratory/LLR/astrophysical bounds, target response, and reaction. The decisive question is whether any finite, allowed configuration retains both the planar de-screening and approximately universal body response.

## 2026-07-13 - Finite Planar Cubic-Galileon Source

**Focus question:** Can a finite planar cubic-Galileon/Vainshtein source retain the exact infinite plane's de-screening and approximately universal response strongly enough to produce `0.01g` over a `2 m` cabin without astronomical surface density or conflict with present constraints?

**Scope and epistemic status:** This run studied the hypothetical canonically normalized cubic Galileon with universal conformal coupling `beta phi T/M_Pl`. The field has not been detected. The finite-disk calculation is a linear reference plus necessary-condition nonlinearity diagnostics, not a solved nonlinear device and not a theorem against every derivative-screened scalar. No FTL or reactionless propulsion follows.

**Sources reviewed:** Bloomfield, Burrage, and Davis on shape-dependent Vainshtein screening; Brax, Burrage, and Davis on plates in the Earth's Galileon background; Ogawa, Hiramatsu, and Kobayashi on nonlinear finite annular disks and local anti-screening; Hui and Nicolis on scalar charge universality; Hiramatsu et al. on the nonlinear two-body response; Burrage and Seery on the background-raised EFT cutoff; Andrews, Chu, and Trodden on the failure of finite-order Sun-Earth-Moon expansions; and Bartlett, Desmond, and Ferreira on LLR and galaxy/black-hole constraints.

**Deepening work completed:** Reviewed eight primary sources including the annular anti-screening counterexample; derived the exact-plane and finite linear-disk results in one normalization; swept cabin uniformity, target acceleration, and coupling; directly integrated the off-axis disk field over a `3 x 3 x 3` cabin sample; built independent edge-Hessian/Vainshtein and `mu`/thickness consistency identities; evaluated both an `H0^-1` cubic scale and the standard `150 Mpc` LLR crossover benchmark; calculated Earth-background dressing, local EFT cutoff, and direct plate/galaxy-bound cases; audited ordinary-body response, near-field two-body failure, momentum reaction, and the nonlinear PDE's ellipticity condition; and designed a dimensionless nonlinear follow-up.

**Artifact built:** Added `models/e021_galileon_planar_screen.py` and a verification suite. The model includes the exact linear disk axis field, direct off-axis thin-disk quadrature, a `3 x 3 x 3` cabin sampler, an axial-uniformity solver, Newtonian comparison, the spherical cubic Vainshtein radius, the finite-edge and density nonlinearity indices, and the radial Earth-background kinetic factor. It explicitly labels the finite linear field as a reference rather than a force upper bound because annular geometries can locally anti-screen.

**What changed:** The exact plane is a real algebraic crack, but the finite source is not a practical cabin-field route in the cubic benchmark. For the static equation

`nabla^2 phi + (c3/Lambda^3)[(nabla^2 phi)^2-(partial_i partial_j phi)^2] = beta rho/M_Pl`,

an exactly one-dimensional profile makes the nonlinear invariant vanish. A sheet of surface density `Sigma` therefore gives

`a_phi = 4 pi G (beta^2/Z) Sigma`,

where `Z=1` in a free background and `Z>1` is the local kinetic dressing. The same sheet's Newtonian field is `2 pi G Sigma`, so `a_phi/a_N = 2 beta^2/Z`.

For a finite linear disk, the on-axis factor is `f(z)=1-z/sqrt(z^2+R^2)`. Placing the cabin center `2 m` from the disk and spanning `z=1-3 m`, the smallest radius giving `+/-10%` axial variation is `R=11.723 m`. At `beta=1`, `Z=1`, and scalar target `0.01g`, the reference values are `Sigma=1.406e8 kg/m^2`, disk mass `6.069e10 kg`, and an unavoidable Newtonian contribution `0.005g`. This is already tens of billions of kilograms before supports. Relaxing axial uniformity to `+/-20%` still needs `2.22e10 kg`; tightening to `+/-5%` raises the mass to `1.93e11 kg`. Direct `3 x 3 x 3` sampling of the same linear disk gives field-magnitude ratios `0.9036-1.1012` and a maximum lateral component `0.0722` times the center field (`7.08e-3 m/s^2`, or `7.22e-4g`, for the scalar target). Raising the radius to about `11.85 m` brings all `27` sampled cabin points within `+/-10%` and changes the mass by only about `2%`; this is a sampled-cube diagnostic, not an analytic extremum proof, but it is adequate for the many-order feasibility boundary.

**Material/planarity gate:** At ordinary high material density, the required surface density cannot be packaged as a cabin-scale plate. Using `22590 kg/m^3` as an osmium-density benchmark gives thickness `h=6.22 km`, or `h/R~=531`, for the free reference. Enforcing even the loose thin-disk condition `h/R=0.01` with the same material requires `R=622 km` and `1.71e20 kg`. Conversely, the illustrative `0.10 m` plate requires `1.406e9 kg/m^3`, `~6.2e4` times osmium density. This is an engineering geometry boundary, not a fundamental density theorem, but it independently prevents a material finite disk from approximating the exact plane at the quoted cabin size.

**Finite-edge consistency result:** The free finite-disk field near its center has a Hessian scale that defines

`epsilon_edge = c3 beta Sigma/(2 Lambda^3 M_Pl R) = (r_V,disk / R)^3/4`.

This equality independently connects the local edge-curvature screen to the disk's global spherical Vainshtein diagnostic. `epsilon_edge << 1` is required to trust the linear finite disk; it is not a formula for the nonlinear force. With the round cosmological benchmark `Lambda=(M_Pl (hbar H0)^2)^(1/3)=1.758e-13 eV`, the `+/-10%`, `0.01g`, `beta=1` disk has `r_V=2.327e12 m` and `epsilon_edge=1.955e33`. Reaching `epsilon_edge=1` at fixed `beta` would require `Lambda~=0.022 eV`, changing the screening/EFT regime; keeping the cosmological `Lambda` and increasing `beta` while lowering `Sigma` would require the formal value `beta~=1.95e33`. Neither is a demonstrated, constraint-compatible device parameter choice. Even the standard published LLR crossover benchmark `r_c beta^(-3/2) >= 150 Mpc`, mapped at `beta=1` to `Lambda~=1.642e-12 eV`, leaves `epsilon_edge~=2.40e30`.

**Annular-density gate:** Ogawa et al. define `mu=beta rho_0/(Lambda^3 M_Pl)` and report that the center-hole enhancement becomes difficult to see above roughly `mu=10^3` in their source family. For a uniform disk of thickness `h`, the E-021 parameters obey the exact bridge `epsilon_edge=c3 mu h/(2R)`; for their thin spherical wedge this becomes approximately `c3 mu theta_0`. Their fiducial `mu=36.8`, `theta_0=0.05` therefore sits near `1.84`, while their `mu=3690` case sits near `184.5`. For the cosmological benchmark, the free target disk made `0.10 m` thick has `rho_0=1.406e9 kg/m^3`, `mu=4.58e35`, and reconstructs `epsilon_edge=1.955e33`, more than `32` orders above the paper-specific anti-screening regime. Even ordinary `1000 kg/m^3` material gives `mu~=3.26e29`. This does not prove that all annular geometries suppress at high `mu`, but it makes a literature-regime reproduction plus density continuation the first gate for E-023, not optional follow-up.

**Earth-background result:** Linearizing a locally radial plate perturbation about the exact spherical cubic background gives `Z=sqrt[1+(r_V/r)^3]`. At the Earth's surface the `H0^-1`, `beta=1` benchmark gives `r_V,Earth=1.074e17 m` (`3.48 pc`) and `Z_Earth=2.19e15`; the `150 Mpc` crossover benchmark still gives `Z_Earth=7.67e13`. Thus exact plate symmetry does not remove environmental screening. Formally holding the scalar target fixed under those factors would raise the linear-reference disk to `1.33e26 kg` (`22.2` Earth masses) or `4.65e24 kg` (`0.78` Earth masses), with Newtonian/scalar ratios `1.09e15` and `3.83e13`. These are reductios, not device estimates: they violate the small-perturbation approximation and make the disk's own nonlinear field dominant. A published Galileon-specific reinterpretation of older Eot-Wash plate data instead gives the conservative empirical dressed limit `beta_eff=beta/sqrt(Z)<0.05`. Saturating only that limit, the `+/-10%` disk needs `Sigma=5.62e10 kg/m^2` and `2.43e13 kg`; ordinary gravity is `200` times the scalar target. Newer short-range tests reach smaller separations, but no controlled finite-pattern cubic-Galileon recast was found, and Yukawa limits cannot simply be substituted into the nonlinear PDE.

**Space-environment check:** Removing the Earth does not generically set `Z=1`. In the isolated-Sun version of the same benchmark, `r_V,Sun=7.45e18 m` (`241 pc`), giving `Z_Sun=3.51e11` at `1 AU` and `3.51e8` at `100 AU`; literal fixed-target masses would be `2.13e22 kg` and `2.13e19 kg`. Real solar/galactic backgrounds are nonlinear and cannot be obtained by simply adding these one-source factors, so these are environmental scale checks rather than predictions. The free `Z=1` case remains useful as an optimistic void reference, and it already fails by source mass and its own finite-edge nonlinearity.

**EFT-control boundary:** The same cosmological normalization has a bare cubic cutoff wavelength `hbar c/Lambda=1.12e6 m`. The free `Z=1` meter-scale disk is therefore a formal classical reference, not a controlled prediction of the minimal EFT. A demonstrated kinetic background raises the local cutoff energy by roughly `sqrt(Z)`: the Earth estimates give dressed cutoff lengths `2.40 cm` for the `H0^-1` benchmark and `1.37 cm` for the `150 Mpc` benchmark. Smooth meter-scale profiles are conditionally controllable only in such a specified dressed background; physical edges and perforations must be smoothed above the applicable local cutoff, while a finer numerical mesh may be used only to resolve those already-smoothed features.

**Independent coupling benchmark:** Bartlett, Desmond, and Ferreira find `Delta G/G_N<0.16` at `1 sigma` for a representative large-Vainshtein-radius galaxy/black-hole-offset model. Only under the E-021 canonical mapping `Delta G/G_N=2 beta^2` does this give `beta<0.283`. Even that weaker, environment-dependent benchmark raises the free disk to `7.59e11 kg`; its ordinary gravity is `6.25` times the scalar target and its cosmological edge index is `6.91e33`. This is not a universal laboratory bound, but it independently shows that a constraint-compatible order-one unscreened coupling cannot be assumed.

**Fair total-loading comparison:** The masses above hold the *scalar contribution* at `0.01g`, deliberately asking whether the new channel can dominate ordinary positive mass. Counting Newtonian and scalar acceleration together, a pure Newtonian disk of this geometry needs `1.214e11 kg` for total `0.01g`; the free `beta=1` scalar reduces that to `4.046e10 kg`. The conditionally mapped galaxy limit gives `1.046e11 kg`, only a `13.8%` reduction from pure Newtonian, while the dressed plate limit gives `1.208e11 kg`, only a `0.50%` reduction. Thus the constraint-compatible total-field interpretation collapses back to the E-013 positive-mass boundary rather than opening a new route.

**Target response and reaction:** Galilean symmetry is a genuine improvement over E-020. For weakly self-gravitating stationary matter, the zero-momentum scalar charge satisfies `Q~=M`, and an exact constant gradient is protected by the Galilean shift. A human proxy therefore does not develop a chameleon-like thin-shell charge loss. The protection is conditional, however. At the cosmological scale the `70 kg` proxy's spherical `r_V` is `2.44e9 m`, vastly larger than the meter-scale field-curvature length. Hiramatsu et al. show that when source-target nonlinear regions overlap, the joint field can make the net force mass dependent even though microscopic coupling is universal. If their spherical fit were naively evaluated at the free disk's human/source mass ratio, the correction would be only `~2.4e-6`; that number is not transferable to a disk, but it shows target nonuniversality is a verification requirement rather than the decisive E-021 rejection. Translation invariance still conserves total matter-plus-field momentum: the plate, supports, and craft receive the reaction, so an internal source can create loading but cannot accelerate a closed craft's center of mass.

**Established physics:** The cited laboratory, lunar-ranging, and astrophysical null measurements; ordinary Newtonian gravity from the source plate; stress-energy/momentum conservation; and the mathematical consequences of the stated cubic field equation. These do not establish that a Galileon field exists.

**Strongly modeled conditional result:** If the cubic Galileon action, quasistatic approximation, universal coupling, and published background/constraint mappings are adopted, finite edges and ambient spherical backgrounds restore enormous nonlinear screening. The ideal plane is a singular symmetry limit rather than a smooth spacecraft-source approximation.

**Failure or boundary found:** A passive finite solid plate cannot presently turn Galileon planar de-screening into useful cabin gravity. In the weakly screened regime the source remains asteroid-scale and its ordinary gravity is unavoidable; in the cosmologically interesting strongly nonlinear regime, a finite `10 m` edge lies more than `30` orders beyond the linear-consistency index and the Earth background suppresses local response by another `~14-15` orders. Stronger coupling does not provide a controlled interpolation between those regimes.

**Blank space or new idea:** Ogawa et al. numerically found `|grad phi|` locally larger than the linear solution near a center hole in a thin, finite annular disk, even while most of the disk environment was screened. This is a genuine counterexample to treating Vainshtein nonlinearity as monotonic suppression. Reading their converged plots, the ratio `R=|grad phi|_nonlinear/|grad phi|_linear` peaks at only about `4-5` in the most favorable dilute/thin/small-hole cases and about `1.3` for `mu=3690`. More importantly, reflection and axial symmetry force the absolute vector field to vanish at the exact hole center; the large ratio is a localized off-center ridge, potentially aided by a small linear denominator, not a central uniform acceleration. The useful blank space is first whether a large *absolute* field survives density continuation, and only then whether controlled reflection-symmetry breaking or layered annuli can move it into a one-sided target volume without destroying the enhancement. Any candidate must retain acceptable gradients, source mass, ordinary gravity, and EFT control.

**Hypothesis updates:** Completed E-021; added H-017 and B-020. The passive finite solid-disk route is rejected for now, while localized annular anti-screening remains an unresolved geometry effect rather than an artificial-gravity claim.

**Next best step:** Run E-023 in two gates. First reproduce Ogawa et al.'s spherical-wedge annuli at `r_2/r_0=30`, `r_1/r_0={4,8,20}`, `theta_0={0.05,0.1,0.2}`, and `mu={36.8,369,3690}`, including their `200 x 100`/box convergence checks, `omega~0.01` under-relaxation, exact-center zero, `R~4-5` localized peak, and its geometry-specific loss above `mu~10^3`. Use `chi=c3 mu theta_0` as the continuation coordinate, but rank cases by absolute `|grad phi|` and usable-volume Hessian rather than `R` alone. Monitor the principal matrix `A_ij=delta_ij+2(c3/Lambda^3)[(nabla^2 phi)delta_ij-partial_i partial_j phi]`; reject branches that lose ellipticity or healthy kinetic signs even if the residual converges. Then translate survivors to smooth-edged cylindrical annuli, introduce controlled asymmetry only after symmetric replication passes, and continue through `epsilon_edge=c3 mu h/(2R)`. Report mass, ordinary gravity, reaction, and cutoff; require physical edge smoothing on scales at least as large as the conditional `~1-3 cm` Earth-dressed cutoff, and use finer meshes only to demonstrate numerical convergence of those resolved features. Include target masses only if the source field passes.

## 2026-07-14 - E-023 Annular Galileon Anti-Screening Replication

**Focus question:** Can the published cubic-Galileon force enhancement inside an annular wedge be independently reproduced on a residual-checked, elliptic branch, and does its absolute field profile reveal a usable localized-field opportunity rather than a ratio artifact?

**Sources reviewed:** Ogawa, Hiramatsu, and Kobayashi's primary paper; Ogawa's later thesis, which supplies the omitted mapped grid and corrects several figure labels; Hiramatsu et al.'s earlier nonlinear solver; White et al.'s residual-driven normal-branch method; Froese, Oberman, and Salvador's 2-Hessian methods; and Nicolis, Rattazzi, and Trincherini for the perturbation kinetic/principal matrix.

**Artifact built:** Added `models/e023_galileon_annulus.py`, research-only NumPy/SciPy requirements, documentation, and ten new tests. The solver implements the paper's dimensionless axisymmetric equation on the thesis grid `r=chi+0.2 chi^3/3`, the published `omega=0.01` lagged-source iteration, both disputed ray angles, exact-center zero, absolute force, algebraic/maximum/volume-weighted residuals, principal-matrix and time-kinetic signs, physical scaling, and reaction bookkeeping. Its default source uses exact overlap fractions in `r^3` and `sin(theta)`; a `cell_center` mode preserves the likely published Heaviside convention.

**Reproduction result:** The resolved effect reproduces, but its precise ratio does not. With the likely paper source convention, the nonlinear/linear force ratio at `r/r0=1` is `3.1198`, `3.3625`, and `3.3640` on proportional `100 x 50`, `200 x 100`, and `400 x 200` grids. Exact volume-fraction sources give `3.347` on `200 x 100`, `3.360` on strict `400 x 200`, and `3.315` on `400 x 400`. A `200 x 100` tolerance sweep gives `3.146`, `3.347`, and `3.378` at update stops `1e-7`, `1e-8`, and `1e-10`. The defensible statement is therefore a resolved enhancement of roughly `3.3`, not a precision peak. In contrast, exact-volume full-ray absolute-gradient peaks are `11.774`, `11.786`, and `11.788` on `200 x 100`, strict `400 x 200`, and `400 x 400`, only `0.12%` total spread. The anti-screened interval ends near `r/r0=5.6`. Thus the local enhancement is not solely a vanishing-denominator artifact, although the exact center remains zero.

**Numerical boundary:** The raw first-shell ratio is not a converged headline observable. It moves from `4.87` to `4.49` to `4.22` across the three paper-style grids and from `3.77` to `4.99` when only the `200 x 100` update tolerance changes from `1e-7` to `1e-10`. Even the resolved `r/r0=1` ratio changes several percent over the widest tolerance/angular sweep, contrary to treating the thesis's update-tolerance comparison as universal. At the paper's `1e-8` update stop, the `200 x 100` algebraic residual is still `4.34e-3`, its maximum residual is `2.49e-2`, and the innermost-cell spatial principal coefficient is `-0.0179`. A strict `400 x 200`, `1e-10` paper-source run reaches algebraic residual `1.47e-4` and minimum spatial coefficient `+0.0109`; the exact-volume run improves these to `1.06e-4` and `+0.0128`, with minimum time coefficient `1.0000089`. A `400 x 400` paper-stop run is also spatially positive (`+0.0129`) and preserves the absolute profile. The coarse negative sign therefore trends away under refinement; it is a stopping/discretization warning, not evidence that the continuum normal branch is unhealthy. With exact-volume sources and approximately fixed radial resolution, enlarging `rmax` from `80` to `160` changes the resolved ratio by `0.50%` and the absolute peak by `0.36%`; `rmax=40` is too close.

**Source and documentation audit:** Center-sampling represents `124.9%`, `93.72%`, and `93.79%` of the nominal source volume at `100 x 50`, `200 x 100`, and `400 x 200`; it even permits an empty thin source on some coarse grids. Exact overlap fractions remove this mass drift. The paper does not publish code or arrays and leaves origin/outer/mixed stencils and the linear solver incompletely specified. The arXiv caption labels its radial slice `theta=2pi/5`, while the later thesis uses the complementary `theta=pi/10`; both are now reported, with the thesis angle treated as the likely correction.

**Physical scale:** Conditional on the cosmological choice `M=Lambda=1.758e-13 eV`, `beta=1`, and `r0=1 m`, `mu=36.8` means density `1.13e-25 kg/m^3` and nominal source mass `6.26e-22 kg`. The full sampled-ray scalar acceleration peaks near `6.1e-35 m/s^2`; the local anti-screened region is of the same tiny order. A deliberately naive fixed-parameter rescaling to `0.01g` would need `r0~=1.62e33 m`, outer radius `~4.85e34 m`, and source mass `~2.64e78 kg`; those super-cosmological numbers invalidate the flat/static setup and are only a reductio. The field varies from exact zero at the center rather than providing a broad one-sided plateau, and an internal target's force is balanced by source/support reaction. This is a dimensionless nonlinear-geometry result, not an artificial-gravity or propulsion result.

**Established physics:** The numerical identities, source-volume integration, exact symmetry-center zero, and momentum reaction ledger. None establishes that a Galileon field exists.

**Strongly modeled conditional result:** Within the stated hypothetical cubic equation, a resolved annular enhancement near `r/r0~1` survives grid refinement and an independent source-volume treatment. Absolute force convergence is substantially better than the near-origin ratio maximum.

**Failure or boundary found:** The published update norm alone is not a sufficient residual or branch certificate, the raw center-adjacent peak is resolution sensitive, and the fiducial density/absolute field is cosmologically dilute and useless for loading. It is premature to perform the planned `~32`-order material-density continuation with only this Picard solver.

**Blank space or new idea:** The cubic equation can be shifted exactly into a 2-Hessian equation. That creates a genuinely independent numerical route whose admissibility condition is the same spatial-principal positivity test. A smoothed annulus solved by source-amplitude continuation in both formulations can separate a real geometry effect from discontinuous-interface and branch-selection artifacts.

**Hypothesis and boundary updates:** Added H-018 and B-021. E-023 stage one is complete; density continuation is gated on E-024 rather than assumed safe.

**Next best step:** Run E-024: implement a residual-driven, source-amplitude continuation solve for a smooth annular wedge and independently cross-check it with the shifted 2-Hessian formulation. Require agreement in resolved force, integrated flux, positive admissibility/principal signs, source-width convergence, and `rmax={40,80,160}` behavior before returning to `mu=369,3690` or material-density continuation.

## 2026-07-15 - Smooth Annular Galileon Continuation and the Shared-Stencil Trap

**Focus question:** Does the fiducial dilute annular cubic-Galileon anti-screening survive a positive, mass-preserving smooth source on the admissible normal branch, and does an exact shifted 2-Hessian solve provide enough independent validation to reopen density continuation?

**Scope and epistemic status:** This run tested one hypothetical static cubic-Galileon PDE. It did not test whether Galileon fields exist in nature, provide a useful absolute force, remain valid at material density, or admit a UV-complete causal theory. The exact center remains symmetry-forced to zero and the prior cosmological `r0=1 m` translation remains only `~6e-35 m/s^2`. No faster-than-light, inertial-control, or reactionless-propulsion claim follows.

**Sources reviewed:** Rechecked Ogawa, Hiramatsu, and Kobayashi's annular calculation and Ogawa's thesis; White et al.'s residual-driven normal-root method; Froese, Oberman, and Salvador's accurate and monotone 2-Hessian schemes; Dickson et al.'s pseudo-arclength conditioning analysis; and Nicolis, Rattazzi, and Trincherini's perturbation-kinetic diagnostics. The main methodological correction is that an exact algebraic shift evaluated with the same discrete Hessian is not an independent discretization.

**Algebra and acceptance gates:** Writing `H=D^2 phi`, the equation is `sigma1(H)+2 c3 sigma2(H)=S`. With `u=phi+|x|^2/(8 c3)` and `W=D^2u=H+I/(4 c3)`, it becomes

`sigma2(W)=3/(16 c3^2)+S/(2 c3)`.

The residuals obey the exact identity `R_G=2 c3 R_2`. The Galileon spatial-principal matrix is `A=2 c3 T1(W)`, so its three eigenvalues are `2 c3` times the pair sums of the shifted Hessian eigenvalues. For the positive source branch, pair-sum positivity is the 2-Hessian admissibility gate. The time coefficient is `K_t=1+2 c3 tr(H)`. A divergence current gives the shell test `integral J dot dA=integral S dV`; the shifted current gives a separately coded flux diagnostic.

**Artifact built:** Added `models/e024_galileon_continuation.py`, `models/e024_shifted_2hessian.py`, and `tests/test_e024_galileon_continuation.py`. The source uses positive quintic `C2` radial/angular transitions, cell averages integrated in the natural `r^3` and `sin(theta)` variables, and exact scalar-charge renormalization. The shifted solver has its own grid, derivatives, Jacobian-vector product, damped Newton-Krylov continuation, branch gates, and flux current; it deliberately does not import E-023. The validation driver also records the original Picard residual, White normal-root residual, formulation differences, transition-cell counts, shell flux, force rays, and explicit provisional/final gates.

**Deepening work completed:** After the first successful `40 x 20` solve, the run continued through fixed-width `80 x 40`, `120 x 60`, and `200 x 100` grids; a narrower smoothing-width stress test; `rmax=40,80,160` box checks; source-amplitude continuation from `lambda=0` to `1`; original/shifted residual identities; two independently coded shell currents; force-profile comparison; analytic-Jacobian finite differences; zero-source and manufactured-quadratic tests; and a primary-source audit of what would count as a genuinely independent 2-Hessian validation.

**Main numerical result:** The positive smooth source preserves the local anti-screened ridge on this grid family.

| Case | Intersected transition cells `(inner, outer, angular)` | minimum cells per transition width | ratio at `r/r0=1` | peak `|grad phi|` | max shell-flux error | global min spatial-principal value |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| broad smooth, `120 x 60` | `(19, 8, 4)` | `3.82` | `3.40718` | `11.73717` | `0.490%` | `0.00398` |
| broad smooth, `200 x 100` | `(31, 12, 7)` | `6.37` | `3.40669` | `11.75234` | `0.188%` | `0.00616` |
| narrower stress test, `200 x 100` | `(21, 8, 6)` | `5.09` | `3.37962` | `11.76834` | `0.229%` | `0.00643` |

The broad `120 x 60` to `200 x 100` change is about `0.014%` in the ratio and `0.13%` in the peak, but only the `200 x 100` broad run passes the six-cell gate. Narrowing the source shifts the ratio by `-0.80%` and the peak by `+0.14%`, but its angular transition spans only `5.09` cell widths, so it is a stress test rather than a passing width-convergence point. The enhancement is not removed by positive smoothing; this remains a same-grid-family result, not a continuum error theorem.

**Box check:** At deliberately coarse fixed angular resolution, `rmax=40` gives ratio `3.0457` and peak `10.9345`, so it is too close. `rmax=80` gives `3.4328` and `11.7121`; `rmax=160` gives `3.4581` and `11.7541`. The `80` to `160` residual drift is about `0.74%` in ratio and `0.36%` in peak. The finite-box sensitivity is smaller than the existence of the enhancement but remains part of the uncertainty ledger.

**Branch and formulation result:** Every accepted shifted-continuation stage retained positive spatial-principal, pair-sum, `sigma2`, and time-kinetic signs. The fine broad rerun ended with original-equation relative residual `1.21e-7`, global minimum spatial-principal value `0.00616`, and `K_t=1.00003`. The global minimum is in the first radial/equatorial cell at `(r,theta)=(0.0254,0.00785)`; excluding one boundary-cell layer gives `0.01282`. Original and shifted fields agree to about `2e-9` relatively, gradients to `2.6e-7`, and shell currents to roughly `1e-6`. This is strong evidence that the two codes selected the same admissible solution and that no obvious implementation-sign error drives the effect.

**Failure or boundary found:** The hoped-for “independent shifted formulation” is not the final independence certificate. If both paths construct the same discrete Hessian family, `R_G=2 c3 R_2` holds algebraically at the discrete level. Separate implementations and nonlinear solvers catch coding and branch-selection failures, but shared-stencil agreement cannot rule out a common discretization artifact. Location-aware diagnostics show that the smallest global principal value is in the first radial/equatorial cell and doubles when one boundary layer is excluded; it is therefore a boundary/stencil warning, not a physical near-degeneracy or condition estimate. In addition, the fine-grid original Picard run reaches a relative update near `1e-11` and tiny volume-weighted residual while retaining a conservative unweighted algebraic residual near `1.1e-3`; this directly preserves the failure of the published update norm as a standalone solution certificate.

**Established mathematics and computation:** The algebraic shift, residual scaling, principal-matrix/Newton-tensor identity, and divergence-current identity are exact for the stated PDE. Source mass, manufactured-solution behavior, Jacobian-vector product, branch signs, and grid/width/box/flux diagnostics are verified numerical properties of the checked implementation. None establishes a new physical field in nature.

**Strongly modeled conditional result:** Within the hypothetical cubic equation and tested centered-grid family, a positive mass-preserving smooth annulus retains a resolved local force enhancement near `3.4` on the admissible normal branch. The discontinuous source interface is therefore unlikely to be the sole cause of the E-023 effect.

**Speculation kept separate:** A verified continuum anti-screening geometry might motivate later density and controlled-asymmetry tests. It does not imply that the enhancement survives `~32` more orders in density, becomes broad or one-sided, couples universally to macroscopic targets, penetrates a hull, remains inside the EFT, or supplies net spacecraft momentum.

**Blank space or new idea:** The exact shift identifies a better falsification route than another same-grid refinement: solve the fixed smooth source with Froese-style monotone wide directional stencils, refining both physical and angular stencil resolution, or use a genuinely different Cartesian/cylindrical coordinate and boundary interpolation. Compare that field to a White normal-root solve, not merely to the algebraically equivalent centered residual. Manufactured nonlinear admissible solutions should be passed before the annulus is attempted. Pseudo-arclength may diagnose a simple fold but must never be used to continue past loss of ellipticity.

**Hypothesis and boundary updates:** Added H-019 and B-022. E-024 stage one is complete, but its final independent-discretization gate failed by construction rather than by a contradictory field result. H-018 remains very low confidence; density, asymmetry, target, and propulsion extensions remain blocked.

**Next best step:** Run E-025: implement a genuinely independent monotone wide-stencil 2-Hessian solver, or a comparably independent different-coordinate solver, for the fixed broad smooth `mu=36.8` source. Require manufactured-solution convergence, independent boundary interpolation, joint spatial/directional refinement, positive admissibility with a stable margin, shell-flux convergence, and agreement in absolute force and the `r/r0=1` ratio. Do not proceed to `mu=369`, `3690`, material density, or controlled asymmetry unless that gate passes.

## 2026-07-16 - Independent Wide-Directional 2-Hessian Gate

**Focus question:** Can a genuinely independent wide-directional discretization of the shifted 2-Hessian equation reproduce the fixed broad smooth `mu=36.8` annular cubic-Galileon force profile, shell flux, and positive admissibility margin without reusing E-024's centered discrete Hessian?

**Scope and epistemic status:** This run tests numerical independence for one hypothetical static cubic-Galileon PDE. It does not establish that Galileon fields exist, survive material density, produce useful absolute acceleration, control inertia, or enable FTL or reactionless propulsion. The prior `r0=1 m` cosmological translation remains only `~6e-35 m/s^2`; axisymmetry still forces the exact central vector force to zero.

**Sources reviewed:** Froese, Oberman, and Salvador's primary 2-Hessian paper; Froese's meshfree Hessian-eigenvalue scheme; Froese Hamfeldt and Lesniewski's three-dimensional boundary-augmented generalized differences; and Finlay and Oberman's higher-accuracy monotone directional interpolation. These establish the Cartesian monotone framework and its refinement conditions. They do not prove convergence of the cylindrical meridional-plus-azimuthal adaptation implemented here.

**Method:** For ordered directional curvatures `x<=y<=z`, the Froese monotone extension is `xy+xz+yz` when `x+y>=0` and `-x^2` otherwise. The latter branch rejects false-positive raw values such as `sigma2(-5,-5,1)=15` by returning `-25`. For an axisymmetric scalar, the continuum Hessian splits into a meridional `2 x 2` block and the azimuthal curvature `u_rho/rho`; its eigenframe therefore lies within the searched meridional orthogonal pairs plus the azimuthal direction. The code stores `phi`, adds the exact shift `1/(4c3)` to each directional curvature, and follows source amplitude with damped semismooth Newton-GMRES while enforcing positive pair-sum and time-kinetic diagnostics.

**Artifact built:** Added `models/e025_axisymmetric_wide_2hessian.py` and `tests/test_e025_axisymmetric_wide_2hessian.py`. The standalone path imports no E-023/E-024 grid, Hessian, residual, gradient, flux, source array, or solver. It uses a uniform nodal quarter-disk in `(rho,z)`, primitive integer wide directions, a separate outward-chord azimuthal curvature, exact circle intersections with positive unequal-distance weights, continuous piecewise source normalization, and an independent `4 pi rho d rho d z` nodal charge diagnostic.

**Manufactured and branch gates:** Thirteen focused tests pass. A nonconvex but 2-admissible quadratic is exact through a shortened curved-boundary stencil to `<2e-13`; a rotated nonconvex quadratic improves as directional radius grows; the nonlinear axisymmetric manufactured RMS error falls from `0.08565` to `0.03970` to `0.01541` as `h=0.25,0.125,0.0625` at fixed `m=3`; zero source returns exactly zero `phi`; and the small-source four-stage smoke solve reaches relative residuals `5.15e-9` in `L2` and `6.84e-9` in `Linf` with minimum pair sum `0.4940`, spatial principal `0.9880`, and time coefficient `1.00000017`.

**Directional failure reproduced:** The primary-source warning is visible in the new operator. At fixed `m=2`, manufactured interior RMS errors for `h=0.0625,0.03125,0.015625` are `1.637e-3`, `1.409e-3`, and `1.410e-3`: spatial refinement has reached a directional-error plateau. A coupled interior sequence `(h,m)=(0.125,2),(0.0625,3),(0.03125,4)` continues down through `3.030e-3`, `1.376e-3`, and `6.798e-4`. Boundary-inclusive errors on a comparable coupled sequence are not yet monotone, so the shortened circular boundary remains a separate convergence gate rather than a solved detail.

**Actual-source stress solves:** Two deliberately under-resolved `rmax=80`, `mu=36.8` solves reached the admissible normal root:

| `h,m` | Unknowns / bases | `dtheta` | Angular cells at radial half-height (`r=8`) | Charge error | Relative residual `L2 / Linf` | Minimum spatial / time | Solve time |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `1,1` | `5097 / 2` | `22.50 deg` | `0.8` | `-1.018%` | `6.44e-11 / 3.25e-10` | `0.02376 / 1.00033` | `4.9 s` |
| `0.5,2` | `20252 / 4` | `13.28 deg` | `1.6` | `-0.1024%` | `7.68e-10 / 5.59e-9` | `0.01804 / 1.00003` | `67.3 s` |

The minimum pair sum occurs at `(rho,z)=(5,0)` in the coarse checks, at the start of the smoothed inner support rather than the coordinate origin. Repeating at `rmax=40` changes the minimum spatial diagnostic by about `11%`, consistent with retaining E-024's warning that the smaller box is biased. These runs establish solver reach and a positive coarse branch only. With `0.8` and `1.6` cells across the narrowest half-height angular scale, neither may be used to quote the E-024 force ratio, absolute peak, flux, or continuum principal margin.

**Source and resource audit:** The continuous broad source normalization is `0.996984643909016`, giving nominal charge `204067.868812537`. Independent nodal cylindrical quadrature errors at `h=1,0.5,0.25,0.125` are `-1.018%`, `-0.1024%`, `-0.006813%`, and `-0.0004316%`; across the full `0.8 r0` angular scale at the radial window's half-height (`r=8`), the corresponding resolutions are `0.8,1.6,3.2,6.4` cells. At `rmax=80`, the quarter-disk unknown counts are `5097,20252,80731,322319`. Directional radii `m=1,2,3,4` reduce nearest-frame errors from `22.50` to `13.28` to `9.22` to `7.02 deg`, but the maximum physical stencil reach is still `1.414,1.118,0.901,0.625`, respectively. Thus the first six-cell source grid is not automatically asymptotic: its widest stencil still spans `~78%` of that `0.8` transition scale.

**Established mathematics versus internal adaptation:** The cited monotone 2-Hessian construction, pair-sum admissibility, and need for `h -> 0`, `dtheta -> 0`, and `h/dtheta -> 0` are established numerical analysis. The shifted ball problem has strictly positive right-hand side and smooth data in the admissible class. The restriction to axisymmetric meridional frames is exact in the continuum, but the discrete outward azimuthal chord, reflected axes, and shortened circular-boundary composition are internal. Manufactured convergence is necessary evidence for them, not a replacement for an applicable proof or the annulus observables.

**Failure or boundary found:** E-025 did not reproduce the annular force profile or flux tonight. The core lacks the independent linear/White normal-root comparison, ray-gradient reconstruction, shell-current integration, and location-aware continuum extrapolation. A fixed direction set demonstrably plateaus, the passing source-resolution level is `~3.22e5` unknowns before stencil and nonlinear costs, and boundary-inclusive coupled errors are not monotone yet. This is a preserved computational/validation boundary, not evidence for or against continuum anti-screening.

**Blank space or new idea:** Finlay and Oberman's barycentric directional interpolation improves the angular term from first to second order while retaining monotonicity, although its absolute error can be larger at modest grids. Combining that construction with Froese-style nonuniform point placement could concentrate `h<=0.125` around the `5<r<33`, `|theta|<0.1` source support and coarsen the empty exterior. A nearer-term accelerator is nested-grid prolongation plus matrix-free wide operators and a scalable Poisson preconditioner. Any adaptive route must still report positive weights, boundary resolution, shrinking stencil reach, source charge, and the same joint-refinement observables.

**Hypothesis and boundary updates:** H-019 remains `Medium-low`; the independent operator exists but the independent annulus result does not. Added B-023. Density, asymmetry, material, target, EFT, and propulsion extensions remain blocked.

**Next best step:** Continue E-025, first adding independent cylindrical linear/White residual, ray-gradient, shell-flux, and pair-minimum-location postprocessing plus nested-grid initialization. Run `(h,m)=(0.5,2)` and `(0.25,3)` with identical observables, then reach a six-cell level with either uniform `(0.125,4)` or a positive-weight locally refined scheme. Require decreasing `dtheta`, `h/dtheta`, and physical stencil reach; source-charge and outer-box convergence; stable positive pair sums; and agreement with E-024's absolute force profile and `r/r0=1` ratio. Stop on loss of admissibility. Do not begin `mu=369`, `3690`, material density, or controlled asymmetry unless the full gate passes.

## 2026-07-17 - E-025 Diagnostics and First Coupled Annulus Refinement

**Focus question:** Can the independent cylindrical wide-directional solver acquire the missing force, flux, White-root, and location diagnostics and produce a quantitatively comparable `(h,m)=(0.5,2) -> (0.25,3)` refinement point, rather than merely another converged nonlinear root?

**Scope and epistemic status:** This is numerical validation of one hypothetical static cubic-Galileon PDE. It does not show that a Galileon field exists in nature, survives material density, creates useful artificial gravity, controls inertia, or enables FTL or reactionless propulsion. The previously translated `r0=1 m` acceleration remains only `~6e-35 m/s^2`, and symmetry still forces the exact center vector force to zero.

**Sources and formula audit:** Rechecked White et al.'s normal attractive root, Froese, Oberman, and Salvador's monotone 2-Hessian scheme, Finlay and Oberman's angular-accuracy warning, and Trudinger and Wang's continuous admissible-cone/Hessian-measure framework. For `c3>0`, White's equation maps exactly to the current normalization with `k=1/c3` and `rho=S/c3`. The unsquared residual and the White residual are equivalent only on the selected normal branch, so the minimum radicand and `Delta phi+1/(2c3)` are now reported. The exact divergence current is

`J_rho = phi_rho + c3[(phi_zz+phi_rho/rho)phi_rho-phi_rhoz phi_z]`,

`J_z = phi_z + c3[(phi_rhorho+phi_rho/rho)phi_z-phi_rhoz phi_rho]`,

with `div J=S`. The spherical flux uses the latitude-from-equator measure `4 pi r^2 integral_0^(pi/2) cos(theta) J.n dtheta`. These identities are exact for the stated PDE; the numerical evaluation is not exact.

**Artifact and deepening work:** Extended `models/e025_axisymmetric_wide_2hessian.py` with a fixed-frame linear Poisson reference, separately evaluated bilinear/centered cylindrical derivatives, original-equation and White-root residuals, a `theta=pi/10` force ray, three spherical-current fluxes, pair-minimum locations, and a reproducible broad-annulus driver. The fixed-frame matrix diagnostic is explicitly labeled a cross-check because it reuses two E-025 operators; the interpolation/centered postprocessor does not reuse the wide directional matrices or active frames and excludes the outer derivative band. Added analytic quadratic tests for the centered Hessian, White residual, linear solve, and spherical-flux normalization, plus an exact assembled-versus-matrix-free Jacobian test. All `78` workspace tests pass.

The nonlinear Jacobian is now assembled from only the active frame once per Newton step. This preserves the root and Krylov counts while reducing the established coarse solve from `78.1 s` to `40.0 s`. A tempting raw nested-grid shortcut failed: bilinear prolongation of a full-source coarse field to a finer grid gave relative residual `1.723`, pair sum `-1.763`, spatial principal `-3.526`, and time coefficient `-3.493`. Raw prolongation is therefore rejected; any future predictor must be source-amplitude scaled and branch checked.

**Completed coarse diagnostic point:** The unchanged `12`-stage tolerances at `R=80`, `(h,m)=(0.5,2)` give `20252` unknowns, four bases, sampled-charge error `-0.102401%`, monotone residual `7.685e-10 / 5.590e-9` in relative `L2/Linf`, and positive minimum pair/spatial/time values `0.0090199 / 0.0180397 / 1.000026`. The pair minimum is at `(rho,z)=(5,0)`, at the smoothed inner support rather than the coordinate origin.

| Observable | E-024 broad reference | E-025 `(0.5,2)` | Interpretation |
| --- | ---: | ---: | --- |
| linear `|grad phi|` at `r=1` | `1.38687` | `1.37774` | `-0.66%`; source/domain normalization is already close |
| nonlinear `|grad phi|` at `r=1` | `4.72468` | `3.58496` | `-24.1%`; nonlinear profile is not resolved |
| ratio at `r=1` | `3.40669` | `2.60205` | `-23.6%`; not an independent confirmation |
| peak nonlinear `|grad phi|` | `11.75234` | `10.9761` | `-6.60%` |
| centered original residual, volume `L2` | not cross-normalized here | `2.9599%` | separate postprocessor still sees material discretization error |
| centered White-root residual, volume `L2` | `~1.98e-8` on E-024 | `0.6131%` | radicand stays positive; root not yet discretely matched |
| largest sampled-charge shell-flux error | `0.188%` | `4.500%` | fluxes remain under-converged |

The three E-025 fluxes are `195687.36`, `194982.85`, and `194684.89` at radii `42.4`, `51.8`, and `61.2`, or `-4.008%`, `-4.354%`, and `-4.500%` relative to the sampled charge. The centered White radicand has minimum `0.250048`, no negative nodes, and minimum normal-branch factor `0.500405`. These signs rule out an obvious wrong-root failure at this level, but they do not make the force or flux accurate.

**Fine refinement failure preserved:** The exact planned `(h,m)=(0.25,3)` run has `80731` unknowns, eight bases, sampled charge `204053.9659`, and charge error `-0.006813%`. It did not produce a full-source solution. At source amplitude `5/12`, Newton iteration `4`, GMRES exhausted the unchanged `40` restart-cycle cap after `4707` stage Krylov iterations. The current relative residual was `5.493e-6`, while the pair, spatial, and time margins remained positive at `0.0246525`, `0.0493051`, and `1.000004`. This is a solver-conditioning/cost boundary, not evidence that the admissible continuum branch ends. Tolerances and iteration caps were not relaxed to manufacture a result.

**Established versus conditional:** The divergence identity, the `c3>0` White-root mapping, the need for the restricted 2-admissible cone, and the requirement for coupled spatial/directional refinement are established mathematics for their stated settings. The axisymmetric curved-boundary stencil, the coarse force/flux values, and any extrapolation toward E-024 are internal computations. Froese's Cartesian proof does not automatically cover this reduction.

**Failure, boundary, and blank space:** E-025 now measures the right observables, but the first coupled refinement sequence is incomplete. The coarse point is far from E-024 and the fine point stops in the linear corrector before full source. The blank space is therefore **blocked computational validation**, specifically a scalable Jacobian-aware preconditioner and checkpointable continuation—not a physics opportunity. H-019 remains `Medium-low`; density, asymmetry, material, target, EFT, and propulsion continuations stay blocked.

**Next best step:** Add stage checkpoint/restart and benchmark a branch-preserving Jacobian-aware preconditioner (for example controlled incomplete factorization or multigrid for the active elliptic Jacobian) on the exact `(0.25,3)` case. Recover the full-source point without relaxing residual or admissibility gates, then compare the same force, centered/White residual, and three shell fluxes. Do not attempt `(0.125,4)` or any `mu`/asymmetry continuation until `(0.25,3)` closes and trends toward E-024.

## 2026-07-18 - Active-ILUT Recovery and the Full-Source Krylov Boundary

**Focus question:** Can a checkpointable, Jacobian-aware elliptic preconditioner recover E-025's exact `(h,m)=(0.25,3)` broad-annulus point without weakening the nonlinear residual, all-frame admissibility, time-kinetic, or fixed Krylov-cap gates?

**Scope and epistemic status:** This run investigated numerical reach for one hypothetical static cubic-Galileon PDE. It did not establish that a Galileon field exists, validate the independent annulus continuum limit, reach material density, create useful artificial gravity, control inertia, or enable FTL or reactionless propulsion. The prior conditional `r0=1 m` translation remains only `~6e-35 m/s^2`, and the exact symmetry center remains force-free.

**Sources reviewed and numerical logic:** Froese, Oberman, and Salvador establish that the 2-Hessian linearization is elliptic inside the `Gamma_2` admissible cone and becomes ill-conditioned as pair sums approach zero; positive pair sums therefore prevent an obvious branch loss but do not guarantee a cheap Krylov solve. Knoll and Keyes motivate physics/Jacobian-based preconditioning for Jacobian-free Newton-Krylov methods. Saad's ILUT supplies the controlled drop/fill incomplete-factorization family used here. Eisenstat and Walker require an inexact Newton correction to satisfy `||F+Js|| <= eta ||F||` with `eta<1`; this provides the decisive audit for any finite correction returned at the iteration cap. Sala and Tuminaro's Petrov-Galerkin smoothed aggregation and Manteuffel, Ruge, and Southworth's local approximate ideal restriction provide primary-source candidates for the next nonsymmetric multilevel comparison. These are numerical-analysis results, not evidence for the underlying speculative field.

**Artifact and verification work:** Extended `models/e025_axisymmetric_wide_2hessian.py` with atomic, pickle-free continuation checkpoints; strict grid, full discrete-operator/boundary, source-digest, schedule, tolerance, and iteration-cap validation; branch validation before any restart residual shortcut; active-Jacobian `spilu` rebuilt once per Newton step; and preconditioner setup/fill instrumentation. Checkpoints contain only accepted fields and reconstructible metadata, never rejected trials, Krylov bases, or factorization internals. Changing preconditioners is rejected after accepted work in an incomplete stage so accumulated counters cannot be mislabeled. Added tests for the zero-state Jacobian identity, active-ILU closure, completed and mid-stage checkpoint/resume equivalence, source and operator/boundary fingerprint rejection, preconditioner-provenance enforcement, and inadmissible restart rejection. The full workspace suite passes with `82` tests.

**Exact stalled-state preconditioner benchmark:** At the former `5/12` state the active Jacobian has about `4.59e5` nonzeros for `80731` unknowns. The fixed zero-state Poisson preconditioner exhausted all `2000` inner GMRES iterations. Rebuilding ILUT on the current active Jacobian gave:

| ILUT drop/fill | Inner iterations | Setup time | Factor nonzeros | Outcome of correction |
| --- | ---: | ---: | ---: | --- |
| `1e-2 / 5` | `861` | `0.425 s` | `1.36e6` | full step accepted |
| `1e-3 / 10` | `478` | `0.675 s` | `3.07e6` | full step accepted |
| `1e-4 / 20` | `316` | `1.184 s` | `6.90e6` | full step accepted |

Each ILUT correction reduced the nonlinear residual from `5.493e-6` to approximately `4.59e-8` while preserving pair/spatial/time minima near `0.02465 / 0.04930 / 1.000004`. The middle setting was retained as the cost/fill compromise. A direct sparse LU was not attempted because the symbolic/resource estimate was roughly `2.3 GB`; it is not a scalable validation route.

**Continuation result:** With the unchanged `12` amplitudes, nonlinear tolerance `1e-7`, GMRES tolerance `1e-8`, restart `50`, and cap of `40` restart cycles, active ILUT cleared the old wall and completed amplitudes `1/12` through `11/12`. Across those accepted stages it used `34081` GMRES inner iterations, `63` Newton loop iterations, `52` ILUT setups, `34.99 s` of factor setup, and at most `3110989` factor nonzeros. The accepted state is preserved at `models/checkpoints/e025_h025_m3_11of12.npz` with its SHA-256 and provenance documented beside it. The first full-source correction nevertheless exhausted the same `2000`-iteration cap at initial relative nonlinear residual `1/12=0.0833333`. Stronger `1e-4 / 20` ILUT and smaller source jumps to `23/24` and `15/16` also exhausted the cap. The `11/12` state remains admissible, with pair/spatial/time minima `0.0095666 / 0.0191332 / 0.9999972`; the stop is not demonstrated branch loss.

**Bounded `11/12` diagnostic only:** The accepted checkpoint has solver relative `L2/Linf` residuals `7.93e-9 / 7.21e-8`, centered original/White volume residuals `1.933% / 0.337%`, and shell-flux errors `-1.818% / -1.910% / -1.938%`. Its force ratio at `r/r0=1` is `3.24984`, peak absolute gradient is `10.4286`, and the anti-screened interval ends near `r/r0=5.5`. These are useful convergence diagnostics at `11/12` source only; they are not full-source E-025 observables and cannot be compared as a completed validation point.

**Rejected capped-direction heuristic:** The finite `2000`-iteration corrections were separately audited, not accepted into the solver. At full source their true linear residual ratios were `1.3565` for ILUT `1e-3 / 10` and `1.5409` for `1e-4 / 20`: both made `||F+Js||` larger than `||F||`, violating the basic `eta<1` inexact-Newton condition. Damping to `1/8` could lower the nonlinear residual by only `0.94-1.43%`; one trial collapsed the pair margin to `0.000368`. Passing the existing line search after heavy damping is therefore insufficient evidence that the capped vector is a valid Newton correction. Positive GMRES `info` remains a hard rejection.

**Established versus conditional:** The inexact-Newton residual test, ILUT algorithm, and nonsymmetric Krylov/multilevel method families are established numerical analysis. E-025's measured Jacobian asymmetry, exact iteration counts, and `11/12` observables are reproducible internal calculations for this discretization; whether a multilevel method will close it is an untested hypothesis. Ellipticity is necessary for the intended branch but does not imply mesh-independent conditioning, and no continuous-solution conclusion follows from solver failure.

**Failure, boundary, and blank space:** Active ILUT solved the previous local conditioning failure but did not close the full-source problem. The blank space is **blocked computational validation** with an **unengineered scalable nonsymmetric elliptic preconditioner**, not a new propulsion opportunity. The sharper boundary is that positive admissibility plus a successful local ILUT does not guarantee reach to the next continuation amplitude; nor may a capped vector whose true linear residual ratio exceeds one be relabeled as an inexact Newton step. H-019 remains `Medium-low`; all six-cell, density, asymmetry, target, EFT, and propulsion extensions remain blocked.

**Next computational hypothesis:** A nonsymmetric multilevel preconditioner tailored to the active elliptic operator—Petrov-Galerkin smoothed aggregation or local approximate ideal restriction, used with GMRES when fixed and FGMRES if the preconditioner varies—can reduce the true full-source linear residual below one at the preserved `11/12` checkpoint without relaxing any nonlinear or branch gate.

**Next best step:** Run E-026 from the saved `11/12` accepted state. First record row-sum, sign, asymmetry, and near-null-mode diagnostics for the exact active Jacobian; then benchmark one fixed Petrov-Galerkin or lAIR V-cycle against ILUT under the same `2000`-iteration cap. Require `||F+Js||/||F||<1` before any line search and full convergence to the unchanged `1e-7` nonlinear tolerance before quoting full-source force, centered/White residual, or shell flux. Do not increase source resolution or `mu` until the exact `(0.25,3)` full-source state closes.

## 2026-07-18 - Postselected Gravity Witness Retention

**Focus question:** What scientifically defensible opportunity, if any, should be retained from Saldanha, Marletto, and Vedral's proposal that a spatially superposed source mass can produce a postselected negative probe-momentum shift?

**Sources reviewed:** Saldanha, Marletto, and Vedral, arXiv:2602.12266v1; Ferrie and Combes on weak-value resource accounting; Yang on postselected metrology as information compression; Vicentini et al. and Di Pietra et al. on nanodiamond quantum-gravity feasibility; Aziz and Howl plus Gundhi, Infantino, and Bassi on the disputed scope of classical-gravity witnesses.

**Deepening work completed:** Re-derived the exact Gaussian successful-port probability and conditional momentum beyond the paper's first-order translation; checked complementary-port momentum conservation; recomputed both Eq. (11) benchmarks; coupled `g` to postselection probability and an ideal `5 sigma` sample count; converted source masses to ordinary-density radii; compared the corrected geometry with Casimir-Polder background scales; and separated the convex classical-mixture claim from broader model-dependent quantum-gravity interpretations.

**What changed:** Added H-020, B-025, and E-027. The retained opportunity is a finite-size, dual-port precision witness of coherent branch-dependent gravitational coupling. It is deliberately parked at medium priority behind the active E-026 numerical-validation task.

**Reasoning:** Each source branch gives an attractive impulse, but near-dark-port postselection subtracts two coherently translated probe amplitudes and can move the selected mean outside their classical convex hull. That sign is experimentally interesting. It does not reverse the unconditional interaction: retaining both ports restores the positive average `alpha^2 delta_A+beta^2 delta_B`, with opposite source/apparatus recoil. Weak-value amplification redistributes information into rare outcomes rather than multiplying force or fundamental information.

**Failure or boundary found:** The paper's explicit large-amplification example has bare postselection probability `1.8008e-7`, not `0.8e-3`, while its `~10^3` amplification is correct. Both feasibility examples use center distances smaller than the radii of ordinary-density sources of the stated masses. The heavy-probe shift is only `0.001978` momentum widths, requiring about `6.4e6` ideal accepted detections for `5 sigma` and roughly `3.2e11` preparations at the implied `g=100` rate. Corrected micron geometry introduces electromagnetic and Casimir-Polder backgrounds many orders above gravity. The effect therefore supplies no repulsive field, artificial gravity, inertial control, or propulsion.

**Blank space or new idea:** A sign-based dual-port convexity witness may still be valuable if a physically non-overlapping screened geometry exists. The unusually strong control is port closure: the anomalous selected port, complementary port, and unconditional momentum must all fit one joint likelihood. Calibrated dephasing, path blocking, phase scans, geometry reversal, and `M T/x^2` scaling can distinguish interference from selection bias and non-gravitational forces. A known electromagnetic or optical force should validate this ledger first.

**Hypothesis updates:** H-020 is `Low` confidence and limited to coherent branch-dependent interaction after gravitational provenance is established. B-025 permanently separates conditional anomalous momentum from a real repulsive gravity source. The active artificial-gravity boundaries and E-026 priority are unchanged.

**Next best step:** Keep the next scheduled run on E-026. When this retained precision-gravity branch is selected, run E-027 as an exact finite-body, screened-geometry, both-port likelihood and Fisher-information study before proposing hardware or strengthening the quantum-gravity interpretation.

## 2026-07-19 - E-026 Nonsymmetric AMG Closure and First Independent Full-Source Point

**Focus question:** Can a fixed nonsymmetric multilevel preconditioner close E-025's exact saved `(h,m)=(0.25,3)`, `11/12 -> 1` corrector under the unchanged `2000`-inner-iteration cap, true-residual test, nonlinear tolerance, and all-frame branch gates?

**Scope and epistemic status:** This run removed a numerical solver obstruction for one hypothetical static cubic-Galileon PDE. It did not establish that a Galileon field exists, prove the cylindrical discretization converges, reach material density, create useful artificial gravity, control inertia, or enable FTL or reactionless propulsion. The fiducial `r0=1 m` acceleration remains about `6e-35 m/s^2`, and the symmetric center force remains exactly zero.

**Sources reviewed:** Sala and Tuminaro's Petrov-Galerkin smoothed-aggregation paper; Manteuffel, Ruge, and Southworth's 2018 lAIR paper; the distinct 2019 Manteuffel, Münzenmaier, Ruge, and Southworth reduction/nAIR paper; PyAMG 5.3's official AIR, nonsymmetric-SA, strength, and fixed-preconditioner interfaces; SciPy 1.18's official GMRES residual and iteration semantics; and the prior Froese/Oberman/Salvador, Eisenstat/Walker, and E-025 operator basis. The source audit corrected two bibliographic conflations in `Sources_and_Notes.md`: Sala/Tuminaro is volume `31` (2008), pages `143-166`, and lAIR is the three-author volume `40` (2018) paper, not the four-author 2019 reduction paper.

**Deepening work completed:** Reconstructed and hash-checked the canonical checkpoint; characterized signs, row sums, diagonal dominance, asymmetry, sparsity symmetry, and smooth modes; benchmarked default lAIR against a separate nonsymmetric PG-SA hierarchy at the exact saved Jacobian; retained the unchanged SciPy GMRES cap and explicit unpreconditioned true-residual audit; completed the full target with both hierarchy families; compared their fields directly; ran independent force, centered/White, flux, and branch postprocessors; compared coarse/fine/E-024 convergence; added a reproducible model, five focused tests including the canonical campaign, a pickle-free full-source artifact, and a precisely gated next refinement task.

**Artifact built:** Added `models/e026_nonsymmetric_amg.py`, `tests/test_e026_nonsymmetric_amg.py`, PyAMG to the research requirements, and `models/checkpoints/e026_h025_m3_full_source_pgsa.npz`. The model never rewrites the canonical E-025 checkpoint. It verifies that checkpoint's SHA-256, reconstructs the exact operator/source digests through the v2 loader, sign-normalizes `J` to `A=-J`, requires the M-matrix-like sign pattern, freezes one V-cycle during each ordinary GMRES call, computes the true residual directly, rejects positive GMRES `info`, preserves the nonlinear decrease and wide-stencil pair/spatial/time gates, and writes a pickle-free result authenticating both field and report. PG-SA hierarchy setup uses recorded seed `260719` inside a saved/restored NumPy RNG context; effective hierarchy choices, candidates, implementation digest, and Python/NumPy/SciPy/PyAMG versions are recorded. A canonical integration test reruns the full campaign and requires exact field equality with the artifact.

**Exact matrix diagnosis:** The active Jacobian is `80731 x 80731` with `458371` nonzeros. Its Frobenius asymmetry is `||J-J^T||_F/||J||_F=0.139018`, so CG/SPD reasoning is invalid. For `A=-J`, all `80731` diagonals are positive, all `377640` off-diagonals are negative, `79522` rows have near-zero sums, and `1209` boundary-influenced rows are strictly diagonally dominant. The boundary-vanishing smooth mode is much slower under `J` than a random vector. This is an unusually clean M-matrix-like diffusion structure, although nonsymmetry and an indefinite symmetric part prevent promoting it to an SPD theorem.

**Saved-corrector sensitivity result:** With `restart=50`, `maxiter=40`, and `rtol=1e-8`, default lAIR returns `info=0` in `20` inner iterations and true residual ratio `2.609e-9`. Its speed is purchased with `11` levels and operator complexity `14.983`. Deterministically seeded nonsymmetric PG-SA uses separate left/right boundary-vanishing candidates, returns `info=0` in `45` iterations with true ratio `9.182e-9`, and needs only four levels with operator complexity `1.606`. PG-SA setup is about `0.22 s` versus `2.44 s` for lAIR on the saved matrix. Thus fewer Krylov iterations alone would have selected the more memory-expensive hierarchy.

The PG-SA near-null choice is not fragile. Writing `q=1-(r/R)^2`, normalized `(B,BH)=(q,q),(1,1),(q,1),(q,rho q)` use the same four-level hierarchy and converge in `45,57,54,44` iterations, all with `info=0` and true residual below `1e-8`. A cylindrical-volume-informed left candidate saves only one iteration; constant choices cost `20-30%` more. The retained `(q,q)` is the simplest boundary-compatible heuristic, not a tuned source of the result.

**Full-source closure:** PG-SA reaches the unchanged nonlinear `L2 < 1e-7` gate in three full, undamped Newton corrections:

| Step | Relative residual before -> after | GMRES inner iterations | True linear residual ratio |
| --- | ---: | ---: | ---: |
| 1 | `8.333e-2 -> 1.761e-3` | `45` | `9.182e-9` |
| 2 | `1.761e-3 -> 9.746e-6` | `44` | `1.884e-9` |
| 3 | `9.746e-6 -> 7.189e-8` | `46` | `2.870e-10` |

Final **wide-stencil all-frame gate** minima are `0.0088301 / 0.0176603 / 1.0000128`. Default lAIR independently closes in `20+20+20=60` inner iterations with the same three full steps. A fresh deterministic comparison gives lAIR/PG-SA relative `L2=1.67e-15` and maximum absolute difference `7.96e-13`; this is strong solver-independence evidence at the accepted discrete tolerance, not discretization independence.

**Independent branch cross-check failure preserved:** The separate fixed-frame diagnostic applied to the accepted field has minimum spatial-principal value `-0.0243895`; an independently reconstructed centered Hessian finds one negative node, `-0.0250979`, at `(rho,z)=(6.25,0.75)`, with eigenvalues `(-0.303537,-0.209012,1.857965)`. The input `11/12` field was already negative there (`-0.0135827` in the centered check), so AMG did not create the warning. This does mean that “positive branch signs” is defensible only for the solved wide-stencil operator. The positive White radicand/normal factor is a trace/root check, not a substitute for this spatial-principal check. Continuum admissibility is therefore unresolved and this node becomes a hard, location-aware E-028 convergence gate.

**First completed fine full-source observables:** At `(h,m)=(0.25,3)`, the force ratio at `r/r0=1` is `3.28303`, peak gradient is `11.0713`, centered original/White residuals are `1.963% / 0.328%`, and three shell-flux deficits are `1.857% / 1.953% / 1.986%`. The White radicand stays positive, with minimum normal-branch factor `0.500085`. Relative to coarse E-025, the ratio moves `2.60205 -> 3.28303`, peak `10.9761 -> 11.0713`, and worst flux deficit `4.50% -> 1.99%`, all toward E-024's `3.40669`, `11.75234`, and `0.188%`. The remaining differences are still material: about `-3.6%` in ratio, `-5.8%` in peak, and roughly an order of magnitude in flux error.

**Established versus conditional:** Fixed left-preconditioned GMRES semantics, explicit true-residual testing, nonsymmetric Petrov-Galerkin transfer, and lAIR are established numerical methods. The measured matrix structure, hierarchy costs, three-step closure, and force/flux values are reproducible internal results for this one grid. The published Cartesian monotone-scheme theorem still does not automatically cover the reflected-axis, curved-boundary cylindrical construction; AMG convergence does not prove nonlinear-PDE continuum convergence or physical realization.

**Failure or boundary found:** The former full-source wall was conditioning, not demonstrated termination of the **wide-stencil discrete** branch. The opposite overclaim is now the main danger: one converged full-source root does not establish mesh independence or continuum admissibility. The independent centered/fixed-frame spatial-principal check is negative at one node; the fine source has only about `3.2` cells across its narrow transition; the physical wide stencil is still long relative to that feature; centered residual remains near `2%`; and shell flux remains near `2%` low. Default lAIR's operator complexity near `15` also fails the intended scalability criterion despite excellent iteration count. H-019 therefore remains `Medium-low`; density, material, asymmetry, target, EFT, and propulsion work remains blocked.

**E-028 preflight and new failure:** Building the `R=80`, `(h,m)=(0.125,4)` model requires `322319` unknowns and `12` directional bases; sampled source charge is within `-4.316e-6` (`-0.0004316%`) of nominal. The build took `13.5 s`. Raw prolongation of the E-026 field is strongly inadmissible: pair/spatial/time minima are `-145.73 / -291.46 / -291.46`. Scaling that predictor by `11/12`, `3/4`, `1/2`, or `1/4` does not repair it; even the quarter field has `-36.06 / -72.12 / -72.12`. Its admissibility threshold is only `alpha~=0.00341926`, with the first failure at `(rho,z)=(78.125,15.5)` on the outer cutoff, so the barely admissible `0.34%` field is rejected as a useful warm start. No fine nonlinear solve or AMG hierarchy was attempted. This preserves a nested-grid predictor failure and rules out a casual “prolong and correct” start.

The native fine-grid Poisson reference is the constructive escape. It solved in `1.12 s`; its full-field admissibility threshold is `~0.09540`, so `(1/12) phi_linear` passes with pair/spatial/time `0.06323 / 0.12647 / 0.98999` and matches the existing first source target. A `1/24` linear start has larger margins `0.28162 / 0.56323 / 0.99499` if needed. Peak RSS was about `720 MiB` after the fine build, `1.02 GiB` during prolongation diagnostics, and `1.46 GiB` during the direct linear solve.

**Blank space or new idea:** The remaining solver blank space is now **joint refinement**, not a propulsion opportunity. E-028 should begin at source amplitude `1/12` from the verified native fine-grid predictor `(1/12) phi_linear`; use `1/24` stages only if the first correction cannot pass unchanged gates. A boundary-aware tapered coarse predictor is unnecessary unless the native start fails. The scientific test is whether the ratio, peak, centered residual, flux, the negative `(6.25,0.75)` cross-check, and all location-aware margins stabilize as `h`, directional resolution, physical stencil reach, source charge, and outer boundary are refined together.

**Hypothesis updates:** E-026 is complete as a saved-grid conditioning experiment. H-019 retains `Medium-low` confidence but its first independent full-source point is explicitly only wide-stencil-admissible; the failed centered/fixed-frame check prevents a continuum-admissibility claim. B-023/B-024 are updated, and B-026 records that multilevel solver closure is not a continuum certificate.

**Verification and provenance:** All `87` workspace tests pass, including an exact canonical E-026 campaign/artifact comparison; all model/test modules compile; dependency checks report no broken requirements; and the module CLI help smoke test passes. The regenerated format-v2 artifact has field SHA-256 `b5f0a48c9b5e84e7a6abc89239c797f0e082d0fbb6bc023913e3cf41d98042ed`, report SHA-256 `44c6913e509454c3ba2c19702137ee8b71f04ce7b6fb377638a690cab37a9acc`, and whole-file SHA-256 `0af7fa9b280b7803394aabb55939a17a6355105bdfead643a0e78d954cfcd6a2`. The canonical E-025 checkpoint remains unchanged.

**Next best step:** Run E-028 from `(1/12) phi_linear` on the native fine grid and the matching `1/12` source target, not raw coarse-field prolongation. Branch-check before any residual shortcut; fall back to a `1/24` predictor and 24-stage schedule only if the first correction cannot pass unchanged gates. Record hierarchy setup, operator and transfer storage, and peak memory. Preserve the same `1e-7`, `1e-8`, `2000`-inner-iteration, force, centered/White, flux, source-charge, all-frame, and minimum-location gates, and require the independent centered/fixed-frame value near `(6.25,0.75)` to become nonnegative or converge under refinement. Stop rather than reinterpret if it remains negative. Do not start `mu=369`, `3690`, material density, controlled asymmetry, or target backreaction. Only a consistent six-cell point should advance to the same-observable outer-box check.

## 2026-07-20 - E-028 Native Fine-Grid `1/12` Bootstrap

**Focus question:** Can the branch-safe native `(1/12) phi_linear` state on the `R=80`, `(h,m)=(0.125,4)` grid reach its matching nonlinear `1/12` source under strict residual, admissibility, memory, provenance, and checkpoint/restart gates?

**Why this narrow stage:** The prior run showed that raw E-026-field prolongation is unusable on the fine grid, while the native Poisson predictor is branch-safe. Advancing only to `1/12` isolates the first fine active-Jacobian and multilevel-solver test without spending the full campaign's memory/time budget or conflating a weak-source bootstrap with the requested full-source six-cell physics point.

**Source and method audit:** Re-read Froese, Oberman, and Salvador's monotone 2-Hessian framework, Finlay and Oberman's improved directional schemes, Froese Hamfeldt and Lesniewski's boundary-aware 3-D construction, Sala and Tuminaro's nonsymmetric PG-SA, Manteuffel, Ruge, and Southworth's lAIR analysis, Awanou's iterative `k`-Hessian work, and the official PyAMG complexity definitions. The established Cartesian convergence condition jointly sends `h -> 0`, `dtheta -> 0`, and `h/dtheta -> 0`; it is not automatically a theorem for this reflected-axis, curved-boundary cylindrical adaptation. Awanou makes a Poisson initialization scientifically reasonable in a different scheme, but direct branch tests remain mandatory here. PyAMG operator complexity is not a process-memory estimate, so E-028 records A/P/R bytes and peak RSS separately.

**Implementation:** Added `models/e028_fine_grid_campaign.py` and `tests/test_e028_fine_grid_campaign.py`. The campaign constructs the native fine Poisson reference once, stores it in a digest-checked pickle-free accepted-state checkpoint, branch-checks before any residual shortcut, freezes each PG-SA hierarchy inside GMRES, rebuilds between Newton corrections, and requires `info=0`, a directly evaluated true linear residual ratio below `1e-8`, no more than `2000` inner iterations, nonlinear decrease, and positive all-frame pair/spatial/time gates. It checkpoints only accepted states and records field/report/system/source fingerprints, runtime and source-module hashes, candidate/seed choices, A/P/R nonzeros and actual sparse bytes, peak RSS, all-frame locations, and separate fixed-frame/centered checks. Resume requires the same Python/library runtime provenance, and a saved fixed/centered conflict cannot cross into the next invocation. Final nonlinear acceptance is strictly below `1e-7`; the older `2 x tolerance` fallback is not inherited.

**Canonical fine-stage result:** The `322319`-unknown, 12-basis predictor begins with pair/spatial/time minima `0.0632326 / 0.126465 / 0.989990`. It is branch-safe but not already nonlinear-close: normalized initial defect is `0.567785`. Ten undamped Newton corrections and `370` summed GMRES inner iterations reach the matching `1/12` target with final relative nonlinear `L2=9.455e-12` and `Linf=3.058e-10`. Every corrector returns `info=0` and has direct true residual below `1e-8`. Final wide pair/spatial/time minima are `0.214399 / 0.428798 / 1.00000003`. The fixed-frame minimum is `0.428798` at `(rho,z)=(5.75,0)`, and the independently centered minimum is `0.429923` at the same location; neither has a nonpositive node.

**Source, observables, and partial-amplitude label:** Fine sampled-source charge error is `-4.3163e-6` (`-0.00043163%`). With source and charge denominators consistently scaled to `1/12`, the force ratio at `r/r0=1` is `1.050565`, the peak gradient is `1.516397` at the diagnostic-window endpoint `r=12`, centered original/White residuals are `0.7317% / 0.3245%`, and shell-flux deficits are `0.3284% / 0.2906% / 0.2584%`. These are weak-source diagnostics only. They cannot be compared as refinements of E-026's full-source `3.2830`, `11.0713`, or `1.86-1.99%`, and the positive `1/12` centered node does not resolve E-026's full-source negative node.

**Same-amplitude coarse control:** A fresh strict `R=80`, `(h,m)=(0.25,3)`, `1/12` control closes in eight Newton corrections and `189` GMRES iterations with nonlinear relative `L2=2.61e-12` and no fixed/centered conflict. Coarse-to-fine changes are `+0.861%` in force ratio, `+0.330%` in peak gradient, `-46.76% / -46.93%` in centered original/White residual, `-34.64%` in worst flux-deficit magnitude, and `-93.66%` in source-charge-error magnitude. This is encouraging same-amplitude bootstrap convergence. It is not the full-source refinement needed to judge H-019.

**AMG sensitivity, determinism, and memory:** The retained geometry-matched `(q,q)` PG-SA candidate uses `370` GMRES iterations. `(q,rho q)` uses `354`, while constant/constant uses `400`; all take ten Newton corrections and agree with the retained field to relative `L2` of order `1e-15`. A clean-process canonical replay is bitwise identical. Maximum operator complexity is `1.7524`, five levels, and maximum explicitly counted A/P/R CSR storage is about `72.6 MB`; peak process RSS is about `1.84 GiB`, so complexity/nonzeros alone would badly understate memory. The fine run costs about `3.29x` the same-amplitude coarse peak RSS and `95.8%` more GMRES work. lAIR was not retried because E-026's measured complexity `14.983` already exposed its diffusion-like coarse-fill risk and low-complexity PG-SA passed the stage.

**Resolution boundary preserved:** The nominal transition spans `6.4` cells, but `dtheta=0.122489`, `h/dtheta=1.0205`, and maximum primitive stencil reach is `0.625 r0`, still `78.125%` of the `0.8 r0` source-transition scale. This is not an asymptotic certificate. The successful stage validates a computational route and a partial-source discrete state; it does not establish the continuum branch, a full-source field, or physical realization.

**Outer-box failure mode found before spending the run:** The existing annulus diagnostic selects flux radii from the box dimensions. An `R=80` and `R=160` comparison would therefore sample different physical spheres, silently changing the observable. Any later box check must fix the physical flux radii and a common interior diagnostic window, while separately reporting global minima over each full box.

**Failure, boundary, and blank space:** No stage-`1/12` solver or branch failure occurred. The preserved failure is interpretive: weak-source positivity and partial-source force/flux cannot answer the full-source negative-node or continuum question. B-027 records this boundary. The remaining blank space is a checkpointed strict amplitude continuation, not artificial gravity or propulsion. H-019 stays `Medium-low`; no density, material, controlled-asymmetry, target, EFT, inertial-control, FTL, or reactionless-propulsion work is opened.

**Verification and provenance:** The full workspace suite passes `95` tests; all model and test modules compile. A fresh-process replay reproduces the canonical field bit for bit. Field SHA-256 is `65764586bd75368121cc616d28b5fdb0a6da4d05294da78b605bf44bba7ccce0`; final accepted checkpoint SHA-256 is `49de2d6b3dafb536ef60a9863d9fad7cf4d0a4df6d27a77166839f857fd4cdfa`; completed-stage artifact SHA-256 is `960076106dbf157fb80c696561cf5165c4c5c127b416f903c1ef2cdd1ebd649e`; and the recorded E-028 module SHA-256 is `e3e4029e8e83a08ee9d1df8068e325a1b9f954d4fd26232de12f6c46bb8eb95d`.

**Post-review repairs:** A read-only code audit found that a fixed/centered conflict saved at the end of a one-stage invocation could cross the next resume boundary. Resume now refuses to advance such a checkpoint, while still allowing the conflicting completed stage to be re-emitted for diagnosis. Resume also requires exact recorded runtime provenance so stage histories cannot silently mix Python/NumPy/SciPy/PyAMG versions. AIR default outputs now carry `_air`, not `_pgsa`, and the embedded hashes are described as integrity checks rather than tamper authentication. Focused regressions cover all three code paths.

**Next best step:** Resume the digest-checked `1/12` checkpoint at `2/12`, retaining one accepted stage at a time and the unchanged strict gates. Stop immediately on a wide, fixed-frame, or independently centered conflict and preserve the last accepted state. Do not interpret partial-stage observables as full-source refinement. Only after reaching a full-source fine state may the negative coarse node be judged; only if that gate passes should E-028 run the outer box with fixed physical flux spheres and a common interior window. Density/asymmetry work remains blocked.

## 2026-07-21 - E-028 Strict Fine-Grid `2/12` Continuation

**Focus question:** Can the integrity-checked native fine-grid `1/12` state advance to `2/12` on `R=80`, `(h,m)=(0.125,4)` without relaxing the nonlinear, direct-GMRES, iteration-cap, line-search, wide-stencil, completed-stage fixed/centered, provenance, or location safeguards?

**Sources reviewed:** Re-audited Froese, Oberman, and Salvador's monotone 2-Hessian admissible-cone and joint-refinement requirements; Finlay and Oberman's joint physical-reach/angular-error result; Awanou's local, scheme-specific `k`-Hessian iteration and Poisson-initialization precedent; Sala and Tuminaro's nonsymmetric Petrov-Galerkin smoothed aggregation; the official PyAMG nonsymmetric-SA implementation/documentation; SciPy's official GMRES semantics; and Mittelmann's predictor-corrector continuation precedent. The published convergence results remain Cartesian/scheme-specific and do not transfer automatically to this reflected-axis, shortened-boundary cylindrical construction.

**Deepening work completed:** (1) resumed exactly one accepted fine-grid source stage and checked its artifact/checkpoint digests; (2) ran a same-amplitude `(0.25,3)` control at `2/12` and a scratch coarse `3/12` forecast; (3) audited the full pointwise shifted `Gamma_2` conditions rather than pair sums alone; (4) repeated the canonical hierarchy and candidate-sensitivity checks; (5) tested full and damped secant predictors plus two scratch-only strict Newton paths toward `3/12`; (6) tracked the old `(6.25,0.75)` warning separately from the moving global minimum; and (7) specified a checkpoint-compatible next-stage/fallback decision tree.

**What changed:** The canonical resume closes `2/12` in nine accepted Newton corrections and `327` summed GMRES iterations. Eight steps are full and the fourth accepted correction uses a `0.25` line-search step. Final relative nonlinear `L2/Linf` residuals are `1.98284e-12 / 3.48351e-11`. Wide pair/spatial/time minima are `0.10327087 / 0.20654173 / 1.00000037`; fixed and independently centered minima are `0.20654173 / 0.20748251` at `(rho,z)=(5.375,0)`, with no nonpositive nodes or conflict. The field, report, artifact, and accepted checkpoint pass their loaders. Field SHA-256 is `3219171452d92fa1e6f027623a318e6aed11bfe9e463a7a6e55c262251270290`; report SHA-256 is `fe387583e8349617aaa8a860994e1a2e4244284a6e524cdfa5744ae85d425db0`; artifact SHA-256 is `2f6beaa5cfec35870816df07faa6ce1520b77e8b3ad17cd6b50e8b9a3bcb98f3`; accepted checkpoint SHA-256 is `8dd454c10583f0cfe4287d7938228b5e41023e4121320c2f2b6ab35aa55b9db3`; and the unchanged model-module SHA-256 is `e3e4029e8e83a08ee9d1df8068e325a1b9f954d4fd26232de12f6c46bb8eb95d`.

**Reasoning:** With denominators consistently normalized to the `2/12` source, the force ratio at `r/r0=1` is `1.165716`, peak gradient is `2.791581` at the diagnostic endpoint `r=12`, centered original/White residuals are `0.8553% / 0.2965%`, and the worst sampled-charge flux deficit is `-0.5962%`; relative sampled-source charge error remains `-0.000431633%`. The strict same-amplitude coarse `2/12` control closes in six Newton corrections and `150` GMRES iterations. Coarse-to-fine changes are `+0.995%` in force ratio, `+0.383%` in peak, `-44.53% / -46.73%` in centered original/White residuals, and `-38.43%` in worst flux-deficit magnitude. Global fixed/centered margins improve by `3.35% / 2.89%`, but the tracked old-warning location becomes `3.25%` less positive (`0.31772 -> 0.30740`). This is encouraging same-amplitude discretization evidence with a non-monotone local warning, not a continuum estimate; two coupled grids cannot supply a Richardson order because both `h` and angular coverage change and neither point is known asymptotic.

The admissible-cone audit sharpens the gate. For shifted eigenvalues `lambda_i`, `D sigma_2` has principal coefficients `lambda_j+lambda_k`, so positive pair sums establish ellipticity of the linearization, but they do not alone imply `sigma_2>0` away from an exact pointwise root. The accepted fine `2/12` field passes the stronger post-hoc check: minimum active monotone `sigma_2` is `0.18749999999`, while independent fixed/centered shifted minima are `0.15419055 / 0.15446866`; the maximum absolute active residual is only `1.065e-10`. This is evidence for the completed state, not yet a core-code gate. Changing the solver now would invalidate the module fingerprint, so explicit pointwise `sigma_2` should remain a manual hard stop until a deliberate checkpoint migration or post-campaign replay adds it to the schema.

Source continuation itself is mixed. From fine `1/12` to `2/12`, the global spatial margin falls by `51.8%`; centered original residual and worst flux-deficit magnitude worsen, while the White residual improves. A naïve full secant predictor `phi_3=2 phi_2-phi_1` fails decisively: wide pair/spatial are `-0.01508 / -0.03015`, fixed/centered have `31/30` nonpositive nodes, and minimum active `sigma_2=-5.34e-4`. A bounded scratch scan finds the residual-minimizing damped predictor near `lambda=0.82454`; requiring residual within `10%` of optimal plus fixed and active-`sigma_2` margins above `0.01` narrows the useful interval to `0.80038 <= lambda < 0.83286`. Conservative `lambda=0.8` lowers the target-`3/12` initial residual from `0.333333` to `0.025247`; one strict full Newton correction uses `59` GMRES iterations and reaches `0.005353` with fixed/centered `0.04733 / 0.04857`. These are scratch predictor-design results only.

The unchanged previous-state seed also remains viable in scratch: its first two strict `3/12` corrections are full, use `56+52` GMRES iterations, reduce residual `0.333333 -> 0.032072 -> 0.003013`, and end with positive wide spatial `0.11314`, fixed/centered `0.04283 / 0.04374`, and active `sigma_2=0.10588`. A separate coarse `3/12` control closes in five full Newton corrections and `132` GMRES iterations with fixed/centered `0.10556 / 0.10520`; its White residual improves but original residual and flux deficit worsen. Neither scratch path is a completed fine stage, but together they refute the simplistic affine claim that the branch must cross zero at `3/12`.

**Failure or boundary found:** The full secant extrapolation is outside both the recorded branch gates and the stronger shifted-`Gamma_2` condition, so it is rejected. The successful `2/12` state is still only a discrete partial-source root of a hypothetical scalar PDE. It does not resolve the coarse full-source negative node, prove spatial/directional/boundary convergence, justify an outer-box run, or change the approximately `6e-35 m/s^2` physical-scale boundary. PyAMG's actual configuration is best described as nonsymmetric smoothed aggregation with Petrov-Galerkin-type transfers; Sala-Tuminaro is precedent, not an exact implementation identity. Also, the resumed report's `1.616 GiB` peak RSS is invocation-local; campaign high-water remains about `1.84 GiB`, while explicit A/P/R storage remains about `72.6 MB`.

**Blank space or new idea:** The immediate blank space is controlled branch continuation, not artificial gravity or propulsion. Keep the canonical plain previous-state seed for the next accepted stage because it preserves the checkpoint/code fingerprint and already has a positive scratch path. If canonical `3/12` fails, preserve the `2/12` checkpoint and distinguish failure modes before migrating anything: a nonlinear/Krylov failure with positive margins motivates a separately fingerprinted `lambda=0.8` predictor experiment; a branch-margin failure motivates step bisection. A scratch `5/24` midpoint with half-secant `lambda=0.5` lowers its initial residual from `0.2` to `0.03639` while retaining fixed/centered about `0.0897 / 0.0902` and active `sigma_2=0.1026`. Either fallback requires a deliberate new schedule/checkpoint provenance path and may not reinterpret the current 12-stage checkpoint.

**Hypothesis updates:** H-019 remains `Medium-low`. E-028 now establishes strict fine-grid branch reach through `2/12`, reproducible solver robustness, and a useful same-amplitude control. It still lacks the full-source fine result, coupled asymptotic sequence, same-observable outer-box comparison, physical actuator, density continuation, target response, EFT ledger, and reaction accounting. No useful artificial-gravity, inertial-control, FTL, or reactionless-propulsion claim is opened.

**Verification and provenance:** All `95` workspace unit tests pass; the eight focused E-028 tests pass independently; `pip check` reports no broken requirements. An initial `pytest` attempt was unavailable because that package is not installed, so the repository's supported `unittest` suite was used. Python `3.14.6`, NumPy `2.5.1`, SciPy `1.18.0`, and PyAMG `5.3.0` match checkpoint provenance. Candidate `(q,q)`, `(q,rho q)`, and constant hierarchies close the same stage in `327 / 316 / 346` GMRES iterations and agree with the canonical field to relative `L2` of order `1e-15`; a clean canonical replay is bitwise identical.

**Next best step:** Verify checkpoint SHA `8dd454c10583f0cfe4287d7938228b5e41023e4121320c2f2b6ab35aa55b9db3` and unchanged module SHA, then resume exactly one canonical stage with `--stop-after-stage 3` and output `models/checkpoints/e028_h0125_m4_3of12_pgsa.npz`. Retain the plain `2/12` field seed, unchanged `1e-7` nonlinear and `1e-8` direct-GMRES/`2000`-inner gates, completed-stage fixed/centered hard stop, location ledger, source/resource audits, and manual active/fixed/centered shifted-`sigma_2` check. Compare any completed fine `3/12` observables against the preserved coarse `3/12` control. Do not change predictor or schedule unless the canonical attempt fails and a separately fingerprinted migration is explicitly undertaken.

## 2026-07-22 - E-028 Strict Fine-Grid `3/12` Continuation

**Focus question:** Can the integrity-checked native fine-grid `2/12` state advance exactly to `3/12` on `R=80`, `(h,m)=(0.125,4)` using the canonical plain previous-state seed without relaxing the nonlinear, direct-GMRES, `2000`-inner, line-search, wide-stencil, completed-stage fixed/centered, provenance, or location safeguards, while also passing manual active/fixed/centered shifted-`sigma_2` checks?

**Sources reviewed:** Re-audited Froese, Oberman, and Salvador's definition of the `Gamma_2` cone and the pair-sum coefficients of the `sigma_2` linearization; Finlay and Oberman's joint angular/physical-reach consistency requirement; Awanou's scheme-specific Poisson-initialization and local discrete-admissibility results; Sala and Tuminaro's nonsymmetric Petrov-Galerkin smoothed-aggregation precedent; the official PyAMG 5.3 nonsymmetric-SA implementation notes; SciPy 1.18's left-preconditioned GMRES convergence and callback semantics; and Mittelmann's continuation precedent. These are established numerical-analysis results under their stated hypotheses. They do not prove convergence of this reflected-axis, curved-boundary cylindrical adaptation, place the previous-state field in a Newton basin, or establish that the hypothetical cubic-Galileon model exists in nature.

**Deepening work completed:** (1) attempted the documented exact `2/12 -> 3/12` resume and preserved its provenance-gate failure; (2) rebuilt stages `1/12` and `2/12` from scratch under the current runtime, retained a separately named replay artifact, and verified its `2/12` field is bitwise identical to the prior accepted field; (3) resumed that new lineage exactly once from the plain `2/12` state and audited every nonlinear, Krylov, line-search, wide, fixed, centered, source, and resource record; (4) manually evaluated shifted `sigma_1`, shifted `sigma_2`, and pair sums on the active, fixed-coordinate, and independently centered Hessians because the driver does not enforce the full `Gamma_2` condition; (5) tracked `(rho,z)=(6.25,0.75)` separately from moving global minima; (6) reconstructed the coarse `(h,m)=(0.25,3)` `3/12` control and compared residuals over a common physical interior window; (7) varied the centered diagnostic's physical difference step on a common `r<=78.5` window; and (8) audited the exact first two scratch Newton corrections toward `4/12`, including the zero crossings along the first direction, without writing a checkpoint or artifact.

**Provenance failure and recovery:** The original checkpoint was created on `macOS-26.5.1-arm64-arm-64bit-Mach-O`; the current runtime reports `macOS-26.5.2-arm64-arm-64bit-Mach-O`. Python `3.14.6`, NumPy `2.5.1`, SciPy `1.18.0`, PyAMG `5.3.0`, the E-028 module, source, system, schedule, and AMG configuration otherwise match. The exact resume therefore stopped before solving with `ValueError: resume runtime provenance does not match`, and the original checkpoint remained unchanged at SHA-256 `8dd454c10583f0cfe4287d7938228b5e41023e4121320c2f2b6ab35aa55b9db3`. No comparison was bypassed or monkeypatched. A fresh current-runtime replay through `2/12` produced a field bit for bit identical to the prior field, with the same SHA-256 `3219171452d92fa1e6f027623a318e6aed11bfe9e463a7a6e55c262251270290`; its retained stage-2 artifact SHA-256 is `1cd31cc2c634c7f75bd56330c8c4f2da076fd3204bba5fd1831bb0d99c1abaa5`. Stage 3 was then accepted only on this separately fingerprinted lineage.

**What changed:** The current-runtime canonical replay closes `3/12=0.25` in seven full Newton corrections and `280` summed GMRES inner iterations. Every GMRES call returns `info=0`; the largest direct true-residual ratio is `9.1512e-9 < 1e-8`, the largest solve uses `56 < 2000` inner iterations, and every stored strict pass flag and Armijo/branch check passes. Final relative nonlinear `L2/Linf` residuals are `7.01069e-12 / 1.81747e-10`. Wide pair/spatial/time minima are `0.05654223 / 0.11308446 / 1.00000033`. Fixed and independently centered spatial minima are `0.11277736 / 0.11325609` at `(5.375,0.125)`, with zero nonpositive nodes and no conflict.

**Manual `Gamma_2` hard stop:** The active shifted eigenvalues have minimum `sigma_1=0.75000017`, minimum pair sum `0.05654223`, and minimum `sigma_2=0.18749999993` at `(14.75,9.5)` in basis `(1,0)`; all nonpositive counts are zero. The maximum active raw-`sigma_2` residual against the shifted right-hand side is `8.34e-10`, and the raw value agrees with the accepted monotone extension to `8.88e-16`. Independent fixed/centered shifted-`sigma_2` minima are `0.11611764 / 0.11613725` at `(5.625,0.5)`, again with zero nonpositive `sigma_1`, pair-sum, or `sigma_2` nodes. Thus the completed field lies in the tested discrete `Gamma_2` cones. This is a postprocessor result, not a theorem or a schema-enforced campaign gate.

**Partial-source observables and same-amplitude control:** At `3/12`, sampled charge is `51016.746997` versus nominal `51016.967203`, a relative error of `-4.31633e-6` (`-0.000431633%`). The force ratio at `r/r0=1` is `1.422741`; the maximum finite ratio is `1.439194`; and the maximum sampled nonlinear gradient is `3.919218` at the fixed-ray endpoint `r=12`, not a demonstrated global peak. The anti-screened ray interval is approximately `0.015625 <= r/r0 <= 6.40625`. Centered original/White volume residuals are `0.96917% / 0.27903%`, and the three sampled-charge flux deficits are `-0.74787% / -0.74159% / -0.72356%`.

The fresh coarse `3/12` control closes in five Newton corrections and `132` GMRES iterations. Fine versus coarse changes are `+0.447%` in the `r=1` ratio, `+0.382%` in endpoint gradient, `-40.99% / -45.91%` in common-window original/White volume residuals, and `-38.33%` in worst flux-deficit magnitude. Global fixed/centered spatial minima rise `6.84% / 7.66%`, and their global shifted-`sigma_2` minima rise `35.8% / 36.3%`. The old warning point is nonnegative on both grids, but its fixed/centered shifted-`sigma_2` falls `8.31% / 7.67%` on refinement; the fine values are `0.174109 / 0.173219` and spatial-principal values `0.231478 / 0.230306`. This mixed location behavior prevents a monotone-convergence or Richardson-order claim. Fine stage-3 GMRES cost also rises `112%`, so the branch is reachable but mesh-independent work is not established.

**Centered-diagnostic scale sensitivity:** On the shared `r<=78.5` window, the fine field remains positive at difference steps `0.125`, `0.25`, and `0.5`: centered shifted-`sigma_2` minima are `0.11614 / 0.12589 / 0.15801`, and spatial minima are `0.11326 / 0.11422 / 0.11650`. The warning-point `sigma_2` is `0.17322 / 0.16480 / 0.19989`, also positive throughout. Positivity is therefore not tied to the native `h=0.125` postprocessor. Quantitative trends are scale-sensitive: at matched physical step `0.25`, fine versus coarse warning-point `sigma_2` falls `12.15%`, whereas at step `0.5` it rises `4.77%`; common-window residual improvement also changes with the derivative step. The sign conclusion is robust over this bounded scan, but convergence percentages and minimum locations are diagnostic-scale dependent.

**Failure or boundary found:** The provenance gate worked as intended: an operating-system patch is enough to forbid silent mixed-runtime continuation. The scientifically relevant state was recovered only by a fresh, separately named replay. The new report authenticates the resumed input field but does not embed the pre-resume checkpoint container hash, so future runs must record that hash externally before mutation. More fundamentally, `3/12` is still only a discrete one-quarter-source root. It cannot decide the coarse full-source negative node, justify the outer-box run, establish continuum admissibility, or be compared as a refinement of E-026's full-source force profile. Invocation-local RSS is `1.604 GiB`; the current-runtime replay campaign high-water is `1.832 GiB`, the prior-runtime lineage reached `1.836 GiB`, and explicitly counted A/P/R arrays peak at `72.6 MB` decimal (`69.2 MiB`).

A scratch `4/12` audit exposes a solver-path boundary. The plain `3/12` field has target preflight residual `0.25`. Its exact first Newton correction passes strict GMRES in `56` inner iterations with direct ratio `5.60e-10`, and the full step passes Armijo plus every core wide gate, reducing residual to `0.01730`. Nevertheless, that off-root iterate has fixed/centered spatial minima `-0.03252 / -0.03210` and shifted-`sigma_2=-0.04482 / -0.04426` at two nodes near `(6.25,0.375)`. A second full correction returns them positive (`0.01674 / 0.01699` spatial and `0.02093 / 0.02126` shifted-`sigma_2`) while reducing residual to `0.001701`. Along the first direction, fixed shifted-`sigma_2` is the earliest zero at damping `alpha~=0.81237`; `alpha=0.8` barely passes, while the dyadic `alpha=0.5` retains fixed/centered spatial `0.05650 / 0.05643` and shifted-`sigma_2=0.06927 / 0.06917`. Froese-Oberman-Salvador's monotone extension and Newton Jacobian are deliberately defined outside `Gamma_2`; their theorem certifies scheme solutions, not every Newton iterate. Thus the transient does not reject a later completed root, but it forbids calling every accepted Newton state full-`Gamma_2` or physical and invalidates importing an admissible-neighborhood Newton proof.

**Blank space or new idea:** The useful blank space remains strict, replayable source continuation. The plain previous-state seed again closed without damping, so no predictor migration is warranted. The moving global minimum, derivative-scale sensitivity, and transient independent-cone exit show why global, fixed-location, completed-stage, and in-progress-state labels must remain distinct. The current in-progress report explicitly says the target has not converged and quotes no observables, but it does not record fixed/centered or shifted-`sigma_2`; an interrupted first `4/12` correction would therefore be resumable despite the known postprocessor conflict. The narrow solution is operational rather than a mid-lineage code change: keep stage 3 immutable, run stage 4 from a byte-identical working copy, never promote an in-progress field, and restart from the immutable stage-3 state after interruption. A future deliberate schema migration could add explicit per-iterate diagnostic status and input-container hashes. A stronger line search that rejects independent-cone exits would choose `0.5`, but that is an extra project safeguard, not a requirement of the cited monotone scheme, and would need its own replay/fingerprint.

**Hypothesis updates:** H-019 remains `Medium-low`. E-028 now establishes current-runtime, strict fine-grid branch reach through `3/12`, with positive manual active/fixed/centered `Gamma_2` checks and encouraging same-amplitude residual/flux trends. It still lacks the remaining nine source stages, a full-source fine state, another coupled refinement, a same-observable outer-box comparison, material-density continuation, controlled asymmetry, target response, EFT validity, and reaction accounting. The fiducial physical translation remains only about `6e-35 m/s^2`, the exact symmetric center remains force-free, and no useful artificial-gravity, inertial-control, FTL, or reactionless-propulsion claim is opened.

**Verification and artifact identity:** Both checkpoint and artifact loaders pass; their fields and reports are exactly equal. Field SHA-256 is `b2fcb751e8fb039d5031ddc9a5b6bd7245d13eae446d50663b652a5ba172d8ba`; report SHA-256 is `4d5d14daea28a0b07ab2ba72b5556ef293f2258822136c8ce2d5ed1d1774ae9f`; stage-3 artifact SHA-256 is `d44f43e9aa6f3e3542df570cd9999da7c6294858922dbad18af7df1798f64fef`; current accepted checkpoint SHA-256 is `368f569bd18cbcb0fdc443ce49703078b52953dd59155869334c10a2f3b8013c`; and the unchanged E-028 module SHA-256 is `e3e4029e8e83a08ee9d1df8068e325a1b9f954d4fd26232de12f6c46bb8eb95d`.

**Next best step:** Verify current checkpoint SHA `368f569bd18cbcb0fdc443ce49703078b52953dd59155869334c10a2f3b8013c`, current runtime provenance, and unchanged module SHA; leave `models/checkpoints/e028_h0125_m4_campaign_checkpoint_20260722.npz` immutable; and resume a verified byte-identical working copy exactly once through `4/12` with the plain accepted `3/12` field and a new date-stamped artifact. Treat any in-progress checkpoint as a computational search state only. If interrupted, preserve it for forensics but restart from another immutable stage-3 copy rather than blindly resuming the known transient conflict. Accept `4/12` only after strict nonlinear closure, loader equality, positive final wide/fixed/centered checks, and positive manual active/fixed/centered shifted-`sigma_2`; otherwise retain stage 3 and do not attempt stage 5. If runtime provenance drifts, replay into another lineage rather than bypassing the guard. Do not run the outer box, density, asymmetry, target, or propulsion extensions before full source passes.

## 2026-07-23 - E-028 Strict Fine-Grid `4/12` Continuation

**Focus question:** Can a verified byte-identical working copy of E-028's immutable current-runtime `3/12` checkpoint advance exactly once to a completed `4/12` endpoint under the unchanged nonlinear, direct-GMRES, iteration-cap, line-search, wide-stencil, provenance, source, and location gates, and does the completed endpoint re-enter positive independent fixed/centered and active/fixed/centered shifted-`Gamma_2` checks after the known transient off-cone first Newton iterate?

**Sources reviewed:** Re-audited Froese, Oberman, and Salvador's elliptic 2-Hessian cone, monotone extension, local Newton solver, and Cartesian convergence hypotheses; Finlay and Oberman's coupled physical-reach/angular-resolution analysis; Awanou's local smooth nondegenerate `k`-Hessian Newton result and scheme-specific Poisson-iteration precedent; Sala and Tuminaro's nonsymmetric Petrov-Galerkin smoothed-aggregation paper; and the official SciPy/PyAMG implementation semantics already recorded for E-028. The peer-reviewed Finlay-Oberman DOI `10.1137/18M1200269` is now recorded alongside the preprint. These sources support a final discrete-root audit but do not prove that every Newton iterate must stay in `Gamma_2`, that an endpoint recovery excludes a discrete branch jump, or that the cylindrical reflected-axis/curved-boundary adaptation satisfies the Cartesian convergence theorem.

**Deepening work completed:** (1) verified the immutable stage-3 checkpoint, model, runtime, and byte-identical working copy before solving; (2) advanced only the working copy from `3/12` to `4/12` and independently verified checkpoint/artifact loader equality and every stored nonlinear/Krylov gate; (3) rebuilt the full operator and manually audited active, fixed-coordinate, and independently centered shifted `sigma_1`, pair sums, and `sigma_2`, including the old `(6.25,0.75)` warning point, the transient `(6.25,0.375)` point, and centered difference steps `h`, `2h`, and `4h`; (4) reconstructed a fresh `(h,m)=(0.25,3)` `4/12` control and compared force, fixed-radius flux, common-window residual, source charge, branch margins, and Krylov work at the same amplitude; (5) independently replayed the fine stage with a deliberately cone-preserving first half step and hard active/fixed/centered `Gamma_2` checks after every later accepted iterate; and (6) audited the distinction between solver search states, accepted discrete roots, continuum branch identity, and physical realization.

**What changed:** The canonical current-runtime fine campaign reaches `4/12=1/3` source amplitude. Six full Newton corrections and `237` summed GMRES inner iterations close the stage with relative nonlinear `L2=6.80850e-9`; the relative `Linf` diagnostic is `1.63427e-7`. Every GMRES call returns `info=0`, the largest direct true-residual ratio is `8.44663e-9 < 1e-8`, the largest correction uses `56 < 2000` inner iterations, and every stored Armijo and wide-stencil gate passes. Final wide pair/spatial/time minima are `0.0355105 / 0.0710210 / 1.00000176`. Fixed and centered spatial minima are `0.0702601 / 0.0704617` at `(rho,z)=(5.375,0.25)`, with no nonpositive nodes or crosscheck conflict.

The stronger endpoint `Gamma_2` audit also passes. Active minima are `sigma_1=0.75000088`, pair sum `0.03551049`, and `sigma_2=0.18749900`; fixed minima are `0.75002107 / 0.03513004 / 0.08547619`; centered minima at the native difference step are `0.75001970 / 0.03523084 / 0.08535728`. Every active/fixed/centered nonpositive count is zero. Centered `sigma_2` remains positive at physical steps `0.125/0.25/0.5`, with minima `0.085357 / 0.096137 / 0.143379`. The active raw `sigma_2` agrees with the monotone extension to `8.88e-16`; its maximum absolute pointwise residual against the shifted source is `9.99e-7`. The old full-source warning location is positive at `4/12`: fixed/centered spatial `0.172158 / 0.170948` and shifted-`sigma_2=0.159439 / 0.158315`. The transient location is also positive at the endpoint: `0.120895 / 0.120187` and `0.176205 / 0.175171`.

**Reasoning:** Froese-Oberman-Salvador define the monotone extension and Newton derivative beyond the admissible cone, and their theorem concerns converged discrete solutions under stated Cartesian hypotheses, not every nonlinear iterate. Therefore the known first full correction's independent fixed/centered excursion does not by itself reject a final passing root. It also cannot be erased: the canonical path did not demonstrate that every independent reconstruction stayed in `Gamma_2`, and the literature supplies no uniqueness or no-branch-jump theorem for this adapted continuation.

The independent replay sharpens that ambiguity constructively. Replacing the first full correction by `alpha=0.5` leaves active/fixed/centered shifted `sigma_2=0.143383 / 0.069270 / 0.069172`, then six subsequent accepted corrections remain positive in all three `Gamma_2` audits. That cone-checked route reaches a field only `4.89e-12` away from the canonical endpoint in relative `L2` (`4.56e-8` maximum absolute difference), despite closing to a tighter residual `2.57e-12`. This is strong evidence that the endpoint is the same fixed-grid root and that the transient is solver-path dependent. It is not a proof of a unique continuum-admissible homotopy branch.

At `4/12`, the partial-source force ratio at `r/r0=1` is `1.809541`; the maximum finite sampled ratio is `1.894623`; and the maximum sampled nonlinear gradient is `4.940985` at the fixed diagnostic endpoint `r=12`, so it is not a resolved global peak. Centered original/White residuals at the native fine step are `1.03375% / 0.25724%`; sampled-charge flux deficits on the three fixed physical spheres are `-0.84453% / -0.85054% / -0.83862%`; sampled source-charge error remains `-4.31633e-6`.

The fresh same-amplitude coarse control closes in five Newton corrections and `136` GMRES iterations. Fine versus coarse changes are only `+0.0756%` in the `r=1` ratio and `+0.3673%` in the endpoint gradient, while the matched-`0.25`-step common-window original/White residuals fall `30.61% / 47.84%`, worst flux-deficit magnitude falls `37.97%`, fixed/centered spatial minima rise `4.72% / 6.65%`, and source-charge-error magnitude falls `93.66%`. Stage GMRES work rises `74.26%`. This is encouraging coupled same-amplitude evidence, but two grids with jointly changing spatial and angular resolution do not define an asymptotic order or mesh-independent cost.

**Failure or boundary found:** Stage 4 passes as a reproducible discrete partial-source endpoint, not as a continuum or physics result. The canonical first accepted search iterate conflicts with independent fixed/centered `Gamma_2`; the alternate cone-preserving route removes that path conflict without proving continuum branch uniqueness. Physical stencil reach remains `0.625 r0`, `h/dtheta=1.0205`, and the cylindrical boundary adaptation remains outside the cited Cartesian theorem. The field is only one-third of the fixed dilute source, the exact symmetric center remains force-free, and the fiducial `r0=1 m` physical acceleration remains about `6e-35 m/s^2`. Full source, another coupled refinement, fixed-observable outer-box stability, material-density continuation, asymmetry, target response, EFT validity, and reaction accounting all remain blocked. No artificial-gravity, inertial-control, FTL, or reactionless-propulsion claim follows.

**Blank space or new idea:** The immediate blank space is now a strict `4/12 -> 5/12` continuation with the same immutable-copy discipline and manual full-`Gamma_2` endpoint gate. The cone-preserving replay shows that an optional diagnostic-cone-safe path can test root identity without changing the canonical campaign: if a future full-step path again leaves the independent cone, compare its final field against a separately labeled half-step replay rather than treating either transient as physical. A later schema migration should store fixed/centered and shifted-`sigma_2` status for in-progress iterates and prevent a requested-final artifact from being mistaken for accepted before postprocessing, but changing the hashed driver mid-lineage would require a deliberate replay.

**Hypothesis updates:** H-019 remains `Medium-low`. E-028 now establishes strict native fine-grid branch reach through `4/12`, positive endpoint active/fixed/centered `Gamma_2`, sign stability across a bounded centered-scale scan, improving same-amplitude residual/flux/source diagnostics, and agreement with a cone-preserving path to within the accepted discrete tolerance. B-027 is extended to `4/12`; B-029 records that endpoint recovery and alternate-path agreement strengthen fixed-grid root evidence but do not certify a continuously admissible or unique continuum branch.

**Verification and artifact identity:** The immutable stage-3 checkpoint remained SHA-256 `368f569bd18cbcb0fdc443ce49703078b52953dd59155869334c10a2f3b8013c`. Its pre-run working copy matched byte for byte. The accepted stage-4 checkpoint SHA-256 is `8cd1abd9f43b9076d6fb884933d055c4746fb0c37e8fd6d596840b7353c13ec4`; artifact SHA-256 is `4ddd280ba9b4ada9ebdb1963d92904813047577e48c750134df36ff9c06f58c1`; field SHA-256 is `ec8fdb4f4050b11affb0194b4bb2eff68ab7e9ae3cf8371d54e3bf442bb7ae53`; report SHA-256 is `8b2c9ee855b2216862012434a16d87777d053bbd8cd0e11e8779d39ed3e4a4db`; and the E-028 module remains `e3e4029e8e83a08ee9d1df8068e325a1b9f954d4fd26232de12f6c46bb8eb95d`. The accepted checkpoint and artifact fields/reports are exactly equal under their integrity-checking loaders, and the saved linear field is finite. All eight focused E-028 tests and all `95` workspace tests pass; every model/test module compiles, and `pip check` reports no broken requirements. Invocation-local peak RSS is `1.621 GiB`; the current-runtime campaign high-water remains about `1.832 GiB`, and maximum explicit A/P/R storage remains `72,586,832` bytes.

**Next best step:** Verify accepted checkpoint SHA `8cd1abd9f43b9076d6fb884933d055c4746fb0c37e8fd6d596840b7353c13ec4`, exact runtime/code provenance, and byte-identical copy to a separately named stage-5 work file. Advance only that copy to `5/12`; after interruption restart from another accepted stage-4 copy. Treat the output as solver-completed pending loader identity, every strict nonlinear/Krylov/wide gate, final fixed/centered checks, and manual active/fixed/centered shifted `sigma_1`, pair-sum, and `sigma_2` acceptance with a bounded centered-step scan. If a full accepted correction leaves the independent cone, preserve it only as a search state and use a separately labeled half-step replay as a root-identity sensitivity check; do not silently change the canonical schedule. Compare any accepted `5/12` endpoint only against a fresh same-amplitude coarse control. Do not begin the outer-box, density, asymmetry, target, or propulsion extensions before full source passes.

## 2026-07-24 - E-028 Strict Fine-Grid `5/12` Continuation

**Focus question:** Can a verified byte-identical working copy of E-028's immutable current-runtime `4/12` checkpoint advance exactly once to a completed `5/12` endpoint under the unchanged provenance, nonlinear, direct-GMRES, iteration-cap, line-search, wide-stencil, and completed-stage fixed/centered gates; does the endpoint pass active/fixed/centered full shifted-`Gamma_2` checks over a bounded centered-step scan; and does a fresh same-amplitude coarse control support rather than contradict the fine result?

**Sources reviewed:** Re-audited Froese, Oberman, and Salvador's elliptic
2-Hessian cone, monotone extension, and Cartesian convergence hypotheses;
Finlay and Oberman's coupled physical-reach/angular-resolution error analysis;
Awanou's local, different-scheme `k`-Hessian result; and SciPy/PyAMG
implementation semantics. Added Hannes Uecker's open 2022 continuation and
bifurcation survey, DOI `10.1365/s13291-021-00241-5`, and Kearfott and Xing's
interval step-control paper, DOI `10.1137/0731048`. Also added Azimzadeh's
2019 weak-diagonal-dominance/M-matrix test, DOI `10.1090/mcom/3347`, for the
endpoint active-Jacobian audit. Uecker makes the missing
branch condition explicit: an invertible solution Jacobian is a sufficient
certificate for a locally unique solution graph only in some neighborhood.
Singularity removes that certificate and is necessary, but not sufficient,
for bifurcation; the survey's close patterned-PDE branches also illustrate
practical uncontrolled branch jumping near bifurcation points. Kearfott and
Xing provide one rigorous no-jump route: under their smooth
finite-dimensional assumptions, successful interval tests certify that the
corrector reaches the same curve and that the traversing curve segment is
unique in a constructed interval box. E-028 has no comparable inverse/IFT
bound, analytic uniqueness argument, or validated enclosure, so residual
closure, positive cones, and near-collinear increments remain evidence rather
than a no-branch-switch theorem.

**Deepening work completed:** (1) verified immutable stage-4 checkpoint SHA,
model/runtime provenance, collision-free output names, and a byte-identical
working copy before solving; (2) advanced only the working copy from `4/12`
to `5/12`, then independently verified checkpoint/artifact loader equality
and all stored nonlinear/Krylov/wide/fixed/centered gates; (3) reconstructed
active, fixed-coordinate, and independently centered shifted `sigma_1`, all
pair sums, and `sigma_2` at physical centered steps `h`, `2h`, and `4h`; (4)
replayed the canonical fine stage from immutable stage 4, captured all five
accepted Newton fields, and audited every endpoint and connecting update
segment; (5) rebuilt a fresh `(h,m)=(0.25,3)` control sequentially through
the same `5/12` amplitude and compared common-window residual, fixed-radius
flux, source charge, force, branch margins, and Krylov work; (6) measured
the weighted and unweighted cone-margin tails across stages 3, 4, and 5 rather than relying
only on a moving global minimum; and (7) computed discrete tangent/secant
sensitivities to test smooth fixed-grid continuation without promoting them
to uniqueness evidence.

**What changed:** The canonical current-runtime fine campaign now reaches
`5/12=0.4166667` source amplitude. Five full Newton corrections and `217`
summed GMRES inner iterations close the stage with relative nonlinear
`L2=4.82226e-8 < 1e-7`; relative `Linf=1.45898e-6` is retained as an
ungated diagnostic. Every GMRES call returns `info=0`, the maximum directly
recomputed true-residual ratio is `9.47315e-9 < 1e-8`, and the largest
correction uses `50 < 2000` inner iterations. Final wide pair/spatial/time
minima are `0.02505673 / 0.05011347 / 1.00000038`; final fixed/centered
spatial minima are `0.05011347 / 0.05024332`, with no nonpositive nodes or
conflict.

The full endpoint `Gamma_2` audit also passes. Active shifted minima are
`sigma_1=0.75000019`, pair `0.02505673`, and
`sigma_2=0.18748885`. Fixed minima are
`0.75003000 / 0.02505673 / 0.06204966`; centered native-step minima are
`0.75002774 / 0.02512166 / 0.06180786`. Every active/fixed/centered
nonpositive count is zero. On the common `r<=78.5` window, centered
`sigma_2` remains positive at physical difference steps
`0.125/0.25/0.5`, with minima
`0.06180786 / 0.07887984 / 0.13411076`. Active raw `sigma_2` agrees with
the monotone extension to `8.88e-16`; its maximum absolute pointwise
residual against the shifted source is `1.11518e-5`. These absolute
pointwise quantities are diagnostics, not substitutes for the unchanged
relative-`L2` acceptance gate.

**Accepted-path audit:** Unlike the stage-4 canonical path, all five stage-5
accepted full-step states pass the three tested active/fixed/centered
reconstructions. The smallest accepted-state or sampled-segment fixed pair
and `sigma_2` margins are `0.01260698 / 0.02988896`; centered values are
`0.01912254 / 0.05206855`. A fresh deterministic replay reproduces the saved
endpoint field bit for bit, with exactly five Newton corrections, `217`
GMRES iterations, and the same final residual. Fixed/centered Hessian maps
are affine in the piecewise-affine update path; endpoint checks, analytic
minima of the affine/quadratic `sigma_1`/`sigma_2` expressions, sampled pair
margins, and convexity of the `Gamma_2` Gårding cone support cone-positive
connecting segments. This is a replay of the chosen discrete solver path,
not an interval-certified uniqueness or no-jump result. The fixed
reconstruction shares wide-operator ingredients; only the centered
postprocessor is genuinely separate.

**Partial-source observables and same-amplitude control:** At `5/12`, the
force ratio at `r/r0=1` is `2.233660`; the maximum finite sampled ratio is
`2.466898`; and the maximum sampled nonlinear gradient is `5.881391` at the
fixed diagnostic endpoint `r=12`, not a demonstrated global peak. The
anti-screened sampled interval is approximately
`0.015625 <= r/r0 <= 6.203125`. Native-step centered original/White
residuals are `1.07590% / 0.24137%`; fixed-step values are
`1.03721% / 0.23899%`. Fixed-sphere sampled-charge flux deficits are
`-0.91107% / -0.92872% / -0.92223%`, and sampled source-charge error remains
`-4.31633e-6`.

The fresh coarse control reaches `5/12` in four Newton corrections and `123`
GMRES iterations. Fine versus coarse changes are `+0.619%` in the `r=1`
ratio and `+0.341%` in the sampled endpoint gradient. At matched physical
difference step `0.25` and common `r<=78.5`, fine original/White residuals
fall `29.79% / 47.50%`; worst fixed-sphere flux-deficit magnitude falls
`37.94%`; source-charge-error magnitude falls `93.66%`; and fixed/centered
spatial minima rise `2.16% / 1.78%`. Fine stage GMRES work rises `76.42%`.
The centered matched-step `sigma_2` margin rises `38.3%`, but this one
positive comparison does not define an error order. Two grids jointly change
physical spacing, direction set, and stencil geometry.

**Localized margin erosion:** The minimum remains positive but moves and
shrinks with amplitude. At the matched centered step `0.25`, stages
`3/12 -> 4/12 -> 5/12` give pair minima
`0.05711 -> 0.03590 -> 0.02525` and `sigma_2` minima
`0.12589 -> 0.09614 -> 0.07888`. The pair-margin `0.01%` weighted quantile
changes `0.11887 -> 0.09529 -> 0.08334`, while the common-window
axisymmetric nodal-quadrature weight fraction with pair margin below `0.05`
changes `0 -> 2.60e-5 -> 5.26e-5`; the sampled
`sigma_2<0.05` weighted fraction remains zero. At stage 5, `182` of `310365`
masked nodes (`5.864e-4` unweighted; `179` positive-weight nodes) lie below
the pair threshold. The denominator includes the large outer vacuum region,
and cylindrical weighting suppresses low-`rho` nodes. The erosion is
localized under this full-domain axisymmetric volume measure, but that does
not exclude a thin connected strip or a larger source-layer-relative tail.
Future stages must retain the global minimum, weighted tail, and node count;
any one alone would conceal useful information.

**Continuation interpretation:** Stage-3-to-4 and stage-4-to-5 tangent
equation mismatch proxies decrease from `0.06048` to `0.04821`; consecutive
weighted field increments have cosine `0.999903`; and the stage-4 secant
predictor misses the stage-5 field by `4.166%` of the stage-5 increment while
remaining wide-admissible. These support a smooth sampled fixed-grid path.
They do not establish Jacobian invertibility, exclude an undetected nearby
branch, or define a continuum homotopy. Uecker's local IFT boundary and
Kearfott-Xing's interval certificate make that distinction concrete.

A new endpoint active-Jacobian audit narrows but does not erase that gap.
For stages 4 and 5, the computed sign-normalized selected semismooth
Jacobians `A=-J` have positive diagonals, nonpositive off-diagonals, one
strongly connected graph component, weak diagonal dominance in all `322319`
rows to `1e-12` tolerance, and `3092 / 3069` strictly dominant rows. Their
Frobenius asymmetry ratios are `0.09217 / 0.09083`. This has the numerical
structure of Azimzadeh's irreducibly diagonally dominant nonsingular
M-matrix criterion and argues against singularity of the selected endpoint
linearizations. It is not an IFT certificate for E-028: four nodes have
exact or `<=1e-12` ties between active directional candidates at each
endpoint, so the min operator is semismooth there; not every generalized
Jacobian selection was audited; no inverse-norm or rounding enclosure was
computed; and no matrix condition was verified continuously between source
amplitudes.

**Failure, boundary, and blank space:** No stage-5 gate failed. The preserved
negative result is interpretive: strict residual closure, a cone-positive
Newton path, and smooth secant behavior still do not certify branch
uniqueness or continuum admissibility. The global cone margin is eroding and
increasingly localized, so the remaining seven source stages may still
terminate or expose a resolution conflict. The model remains a hypothetical
dilute scalar PDE with physical stencil reach `0.625 r0`,
`h/dtheta=1.0205`, no full-source fine solution, no outer-box comparison, no
material-density continuation, and no target/reaction/EFT closure. The exact
symmetric center remains force-free and the fiducial `r0=1 m` physical
translation remains about `6e-35 m/s^2`. No useful artificial gravity,
inertial control, FTL, or reactionless propulsion follows.

The narrow new opportunity is numerical, not propulsive: a cheap branch
health ledger can combine the tangent mismatch, increment cosine,
fixed-location values, global minima, and weighted/unweighted tails at every
accepted amplitude. A rigorous Kearfott-Xing-style interval no-jump
certificate is not implemented for E-028 and would require a smooth interval
extension plus scalable validated linear algebra; practicality at `322319`
unknowns is unestablished. A matrix-free
smallest-singular-value/inverse-norm diagnostic could be explored later, but
it would remain nonrigorous unless supplied with validated bounds.

**Hypothesis and boundary updates:** H-019 remains `Medium-low`. E-028 now
establishes strict current-runtime fine-grid reach through `5/12`, a
bitwise-replayed cone-positive canonical stage-5 path, positive endpoint
active/fixed/centered `Gamma_2`, bounded centered-scale sign stability, and
encouraging same-amplitude integrated diagnostics. B-027 is extended through
`5/12`; B-029 now records that even a cone-positive replay and smooth
tangent/secant ledger are not an IFT or interval branch certificate.

**Verification and artifact identity:** The immutable stage-4 source
checkpoint remained SHA-256
`8cd1abd9f43b9076d6fb884933d055c4746fb0c37e8fd6d596840b7353c13ec4`.
The accepted stage-5 checkpoint SHA-256 is
`4c2c10a53156c59b53abbc5963d9089f460c75e65b6cdc4fa1cb64d4f548977f`;
artifact SHA-256 is
`a72166c722c947dad9da93b505fa1335633adf23bd61c33a7dfa9968b6215c84`;
field SHA-256 is
`ab5b23f15f729cb0f72589c2287e1013f8f6b05a7dbe91ad6b1debffe272f5c7`;
report SHA-256 is
`7207528839fcdd909ed19467e6de349374c09ff2fcbd7a97e9780e568f2174c0`;
and the E-028 module remains
`e3e4029e8e83a08ee9d1df8068e325a1b9f954d4fd26232de12f6c46bb8eb95d`.
The immutable checkpoint and artifact loaders pass, their fields and reports
are exactly equal, and the saved linear field is finite. Campaign totals are
`37` Newton corrections and `1431` GMRES inner iterations through five
stages. Invocation-local peak RSS is `1.135 GiB`; the campaign high-water
remains about `1.832 GiB`, and maximum explicitly counted A/P/R storage
remains `72,586,832` bytes. The external `/usr/bin/time -l` wrapper returned
status 1 only after the successful model process because sandboxed
`kern.clockrate` access failed; the model output, artifact, and loader audits
are unaffected. All `95` built-in `unittest` tests pass in `8.824 s`; all
model/test modules compile; and `pip check` reports no broken requirements.
An attempted `pytest` invocation failed before discovery because `pytest` is
not installed in this research environment. That tooling miss is preserved
here and is not counted as a model/test failure.

**Next best step:** Verify accepted stage-5 checkpoint SHA
`4c2c10a53156c59b53abbc5963d9089f460c75e65b6cdc4fa1cb64d4f548977f`,
exact runtime/code provenance, and a byte-identical copy to a new stage-6
work file. Advance only that copy to `6/12`, exactly one canonical amplitude.
After interruption restart from another immutable stage-5 copy. Require
loader identity, unchanged nonlinear/Krylov/wide/fixed/centered gates,
manual active/fixed/centered full-`Gamma_2`, a bounded centered-step scan,
and an accepted-iterate/segment replay. Record both global minima and
weighted and unweighted margin tails, the tangent/secant ledger, tracked warning
locations, and a fresh coarse `6/12` same-amplitude control. Do not begin the
outer-box, density, asymmetry, target, or propulsion extensions before full
source passes.

## 2026-07-25 - E-028 Six-Twelfths Continuation Gate

**Focus question:** Can a collision-checked byte-identical work copy of
E-028's accepted current-runtime native fine-grid `5/12` checkpoint advance
exactly to `6/12` without relaxing any provenance, nonlinear, direct-GMRES,
iteration-cap, line-search, wide, fixed, centered, or full shifted-`Gamma_2`
gate; and do the accepted path, margin-tail, Jacobian-health, tangent/secant,
tracked-location, and fresh same-amplitude coarse diagnostics remain
consistent with a healthy sampled discrete continuation?

**Sources reviewed:** Re-read Froese, Oberman, and Salvador's elliptic
2-Hessian cone, monotone extension, and Cartesian convergence theorem
(`h -> 0`, angular fill distance `dtheta -> 0`, and `h/dtheta -> 0`);
Finlay and Oberman's coupled physical-reach/angular-error analysis; Awanou's
local discrete `k`-Hessian Newton result under a close seed and smooth
nondegenerate solution; Qi and Sun's semismooth-Newton theorem requiring
nonsingularity of every generalized Jacobian in the relevant neighborhood;
Azimzadeh's weakly chained diagonally dominant nonsingular M-matrix criterion;
and Kearfott and Xing's interval step control for proving that continuation
steps remain on one solution curve. These are high-quality sources for their
stated schemes and finite-dimensional theorems, but none directly certifies
E-028's reflected-axis cylindrical construction, its nearby generalized
Jacobians, or physical realization of the cubic-Galileon model.

**Provenance failure and recovery:** Exact resume from accepted stage 5
correctly stopped before solving because the saved implementation fingerprint
contained the former `requirements-research.txt` digest
`cd1df48db71c...`, while the committed file now hashes to
`b44e38d9b1076b4de3497d8d81a2dbfb2bf0405494ea129bfe3d3d6af0e46349`.
Python and the numerical-library versions were unchanged, but the exact guard
was not bypassed. A fresh current-provenance replay through `5/12` took
`164.61 s` and reproduced the accepted field bit for bit, with maximum absolute
difference zero and unchanged field SHA-256
`ab5b23f15f729cb0f72589c2287e1013f8f6b05a7dbe91ad6b1debffe272f5c7`.
Stage 6 was advanced only from that replay lineage.

**Deepening work completed:** The `6/12` corrector closed in five undamped
Newton steps and `254` GMRES inner iterations (`52 / 59 / 48 / 56 / 39`).
Every linear solve reported `info=0`; the largest independently recomputed
true-residual ratio was `9.1541e-9`, and the final nonlinear relative
`L2=5.4588e-8`. Wide pair/spatial/time minima are
`0.0192176 / 0.0384351 / 1.00000237`; native fixed/centered spatial minima are
`0.0330635 / 0.0327836`. Full active/fixed/native-centered shifted
`Gamma_2` minima `(sigma_1, pair, sigma_2)` are respectively
`(0.750001, 0.0192176, 0.187484)`,
`(0.750042, 0.0165318, 0.0425205)`, and
`(0.750039, 0.0163918, 0.0421584)`, with zero nonpositive counts. The centered
common-window `sigma_2` minimum remains positive at physical steps
`0.125 / 0.25 / 0.5`, namely
`0.0421584 / 0.0664598 / 0.127299`.

**Accepted-path and operator audit:** A fresh accepted-path replay is bitwise
identical at the endpoint. Every accepted state and nine samples on each
piecewise-affine connecting segment pass all three shifted-`Gamma_2`
reconstructions. The global sampled minima occur on the first correction:
active `(0.749547, 0.0174449, 0.122257)`, fixed
`(0.749542, 0.00225488, 0.00494198)`, and centered
`(0.749531, 0.00223272, 0.00488522)`. Endpoint tangent-equation mismatch falls
`0.06048 -> 0.04821 -> 0.04005` from stages 4 through 6; weighted successive
increment cosines are `0.999903` and `0.999935`, while new-increment secant
misses fall `0.04166 -> 0.03659`. Four exact endpoint active-frame ties occur
at axis nodes `z=7.75, 7.875, 8.0, 8.125`; enumerating all `16` selections
produces one bitwise-identical Jacobian. With sign normalized as `-J`, its
`322319` diagonal entries are positive, no off-diagonal is positive, all rows
are weakly diagonally dominant within rounding tolerance, `3047` are strict,
and the directed graph is one strong component. This removes the observed
tie-selection ambiguity at the endpoint only; it supplies neither a nearby
inverse bound nor an interval no-jump certificate.

**Low-tail geometry and same-amplitude control:** On the centered
common-window reconstruction at physical step `0.25`, pair minima erode
`0.057109 -> 0.035896 -> 0.025246 -> 0.019365` from stages 3 through 6.
At stage 6, `227/310365` nodes lie below `0.05`; their full-window
axisymmetric nodal-quadrature weight is only `6.535e-5`, but their
source-support-relative weight is `0.003139`. They form one connected thin
strip from `rho=0` to `6.25`, `z=0` to `0.75`, reaching the inner source
smoothing layer rather than isolated numerical speckles. A fresh strict
coarse `(h,m)=(0.25,3)` stage-6 control reproduces all prior stage counts and
closes in five Newton steps and `174` GMRES iterations. Fine-to-coarse changes
are `+1.728%` in the `r=1` ratio, `+0.321%` in the diagnostic-endpoint
gradient, `-29.185% / -47.148%` in matched original/White residual,
`-37.866%` in worst flux-deficit magnitude, and `-93.664%` in source-charge
error. The native margin trend is mixed, while the matched-step centered
spatial margin improves `0.0382235 -> 0.0387306`. Two grids are encouraging
but cannot establish asymptotic order.

**What changed:** E-028 now reaches exactly half source on a strict,
checkpointed fine-grid lineage. The stage-6 `r=1` force ratio is `2.604856`;
the maximum sampled gradient is `6.756110` at the diagnostic endpoint
`r=12`, not a proven global peak. Centered original/White residuals are
`1.10908% / 0.228795%`, fixed-window values are
`1.06821% / 0.226834%`, fixed-sphere flux deficits are
`-0.962787% / -0.990948% / -0.988775%`, and sampled source-charge error is
`-4.3163e-6`. The campaign now totals `42` Newton corrections and `1685`
GMRES iterations through six accepted stages.

**Failure or boundary found:** No strict stage-6 solver, endpoint-cone, or
sampled-path failure occurred. The important failure is interpretive: the
shrinking margin is spatially connected to the source-transition region, and
the first accepted correction approaches fixed/centered `sigma_2` near
`0.0049`. Full-domain weighting alone understates this source-relative
structure. The endpoint M-matrix pattern, smooth secants, and finite segment
sampling do not meet Qi-Sun's neighborhood hypothesis or Kearfott-Xing's
validated-continuation standard. Full source, a coupled asymptotic sequence,
outer-box stability, physical-density continuation, target response, EFT
validity, reaction accounting, useful artificial gravity, inertial control,
spacetime engineering, FTL, and propulsion therefore remain unresolved.

**Blank space or new idea:** Keep the global tail ledger, but add a
source-support-weighted connected-component ledger and track the minimum over
accepted corrections separately from the endpoint. Before promoting branch
health to branch certification, a future method project could combine
verified residual intervals with an interval inverse bound around each source
step. That is a numerical-analysis opportunity, not evidence for a device or
new physical mechanism.

**Hypothesis updates:** H-019 remains `Medium-low`. E-028 gains strong
fixed-grid evidence through half source, exact replay evidence, positive
sampled-path margins, an encouraging mixed two-grid comparison, and removal
of the observed endpoint tie ambiguity. B-027 is extended through `6/12`;
B-028 records that an implementation-fingerprint change required fresh replay;
and B-029 records the connected low-margin path and the still-open
neighborhood/inverse/interval boundary.

**Verification and artifact identity:** The accepted stage-6 checkpoint and
retained work snapshot are byte-identical at SHA-256
`ff82363833c84e416e020a8df56d6067b6b1f7612c41f30f6499d6b95690babb`.
The stage-6 artifact SHA-256 is
`64a0fca132dd6b068c543f102c74c3ffa09a545509d9f822857cc13e179c5476`;
field SHA-256 is
`cd806ff41c0a33d541cc5c1dba44a3c7ad693ddb6b81dda5eae2ac1db8757c3`;
report SHA-256 is
`fe2c11e1d2e7806b12836325eaaed565137b5495efbb25417f4c6545fd3a256c`;
and the unchanged module SHA-256 is
`e3e4029e8e83a08ee9d1df8068e325a1b9f954d4fd26232de12f6c46bb8eb95d`.
Invocation peak RSS was about `1.614 GiB`, with maximum explicitly counted
A/P/R storage `72,586,832` bytes. All `96` workspace unit tests pass; the
complete checkpoint SHA-256 manifest verifies, checkpoint/work/artifact
loaders agree exactly, every model/test module compiles, and `pip check`
reports no broken requirements.

**Next best step:** Keep accepted checkpoint SHA
`ff82363833c84e416e020a8df56d6067b6b1f7612c41f30f6499d6b95690babb`
immutable and advance only a fingerprint-matching work copy exactly to
`7/12`. Preserve every strict gate and repeat endpoint, accepted-path,
source-relative connected-tail, tracked-location, generalized-Jacobian-tie,
tangent/secant, and fresh coarse `7/12` checks. Stop if any frame becomes
nonpositive or if the low-margin strip broadens materially. Do not begin the
outer box, density, asymmetry, target, EFT, or propulsion extensions before a
strict full-source endpoint passes.

## 2026-07-26 - E-028 Seven-Twelfths Continuation Gate

**Focus question:** Can a collision-checked byte-identical work copy of
E-028's accepted native fine-grid `6/12` checkpoint advance exactly to
`7/12` without relaxing any provenance, nonlinear, direct-GMRES,
iteration-cap, line-search, wide, fixed, centered, or full shifted-`Gamma_2`
gate; and do the accepted path, source-relative connected low-margin tail,
tracked locations, generalized-Jacobian ties, tangent/secant ledger, and a
fresh same-amplitude coarse control remain consistent with a healthy sampled
discrete continuation?

**Sources reviewed:** Caffarelli, Nirenberg, and Spruck, "The Dirichlet
problem for nonlinear second-order elliptic equations, III" (*Acta
Mathematica* 155, 1985, DOI `10.1007/BF02392544`); Froese, Oberman, and
Salvador, "Numerical methods for the 2-Hessian elliptic partial differential
equation" (*IMA Journal of Numerical Analysis* 37, 2017, DOI
`10.1093/imanum/drw007`); Qi and Sun, "A nonsmooth version of Newton's
method" (*Mathematical Programming* 58, 1993, DOI
`10.1007/BF01581275`); Kearfott and Xing, "An interval step control for
continuation methods" (*SIAM Journal on Numerical Analysis* 31, 1994, DOI
`10.1137/0731048`); and Azimzadeh, "A fast and stable test to check if a
weakly diagonally dominant matrix is a nonsingular M-matrix" (*Mathematics
of Computation* 88, 2019, DOI `10.1090/mcom/3347`).

**Deepening work completed:** Verified that the accepted stage-6 checkpoint,
its saved runtime, every implementation fingerprint, and the current
scientific Python environment match exactly. A collision-checked copy then
advanced to `7/12` in five full Newton corrections and `277` total GMRES
iterations. Every direct GMRES solve returned `info=0`, maximum true-residual
ratio was `9.0733e-9`, final nonlinear relative `L2/Linf` were
`1.86895e-8 / 6.04628e-7`, and all step lengths were one. The endpoint
passes the stored wide gates with pair/spatial/time minima
`0.0156637 / 0.0313274 / 1.00000258`, fixed/centered spatial minima
`0.0205178 / 0.0201393`, and no nonpositive nodes.

The independent endpoint reconstructions also pass. Active
`sigma_1/pair/sigma_2` minima are
`0.750001 / 0.0156637 / 0.187494`; fixed minima are
`0.750043 / 0.0102589 / 0.0276443`; and centered native-step minima are
`0.750040 / 0.0100696 / 0.0271270`. Centered common-window `sigma_2` stays
positive at physical steps `0.125/0.25/0.5`, with minima
`0.0271270 / 0.0533162 / 0.122429`. The endpoint field/report/linear-field
SHA-256 values are
`92b625491af99cea96bb5bacbdeb211f0ef04323d34103f9c84b0073bc2c990f`,
`7bf2cada15267c53c7934916d6f07291a358860a0538cf7dead24fa6db3ce997`,
and
`6fe081d1b9eb5a02e88e6c0e79531f6419aa35053f75c87090cf03be1f5bc606`.

**What changed:** The endpoint is retained only as a dated path-conflict
artifact and work checkpoint, not promoted into the accepted campaign
lineage. A deterministic canonical replay ends bitwise-identically and
repeats five Newton/`277` GMRES, but its first accepted full correction
leaves both independent reconstructed cones: fixed pair/`sigma_2` reach
`-0.00244344 / -0.00762639`, and centered values reach
`-0.00252146 / -0.00783733`. Active values remain positive. Later accepted
states recover all endpoint margins. Nine-point samples on the first
piecewise-affine segment reproduce the same negative minima.

A separate scratch sensitivity using `alpha=0.5` for the first correction
keeps the active/fixed/centered cones positive
(`0.016995 / 0.007405 / 0.007246` minimum pair sums after that half step),
then closes in four full corrections and `237` GMRES iterations. It reaches
the canonical endpoint to relative field `L2=7.49e-12` and maximum absolute
difference `7.02e-8`, with final relative residual `3.37e-9`. This supports
the same sampled fixed-grid root by a path-dependent corrector, but it does
not repair the predefined canonical path gate or prove uniqueness.

**Reasoning:** Continuous `Gamma_2` admissibility underlies ellipticity, but
the cited convergence theorem concerns a jointly refined Cartesian monotone
scheme, not this reflected cylindrical operator. Likewise, sampled
continuation is not the interval no-path-jump certificate described by
Kearfott and Xing. The four exact endpoint frame ties again generate
`2^4=16` selections, yet the tied frames have identical curvature triples
and gradients and every selection assembles the same matrix (SHA-256
`c724a0e2e02765550d3d45e6f5d5b3c3c893b8694695c10a5584c1664142120c`).
The sign-normalized matrix has positive diagonal, no positive off-diagonal,
all rows weakly diagonally dominant to numerical tolerance, and `3036`
strict rows. Its graph has a singleton weak component at `(rho,z)=(0,7.625)`
feeding the strict-containing `322318`-node component, so the numerical
WCDD path-to-strict condition holds even though irreducibility does not.
This is endpoint conditioning evidence only: no interval inequalities,
inverse bound, nearby-source enclosure, or continuum theorem follows.

The stage-4 through stage-7 tangent-mismatch proxies improve monotonically
`0.060480 -> 0.048207 -> 0.040049 -> 0.034506`. The stage-7 weighted
successive-increment cosine is `0.999953776`, and the secant miss divided by
the new increment is `0.0327969`. Active/fixed/centered checks at both
tracked locations `(6.25,0.375)` and `(6.25,0.75)` remain positive. These
support smooth sampled endpoint geometry only; they do not override the
negative canonical first correction, supply a no-jump theorem, or establish
continuum convergence.

The matched centered-step `0.25` tail supplies the second stop signal. From
stage 6 to stage 7, the pair minimum falls `0.0193653 -> 0.0157346`.
The `pair<0.05` set grows `227 -> 240` nodes while remaining one connected
source-layer strip; its full-window weight grows
`6.535e-5 -> 7.054e-5`, and its source-support weight remains about
`0.003139`. More importantly, the `pair<0.02` core broadens from `10` to
`74` nodes and its source-support weight grows
`0.000270 -> 0.000721`, a factor of `2.67`. The tail is still localized,
but the predeclared material-broadening stop condition is met.

A fresh coarse `(h,m)=(0.25,3)` `7/12` control closes in four Newton
corrections and `141` GMRES iterations. Fine versus coarse changes are
`+2.882%` in the `r=1` ratio, `+0.304%` in endpoint gradient,
`-28.32% / -46.37%` in matched original/White residuals,
`-37.75%` in worst flux-deficit magnitude, and `-93.66%` in source-charge
error magnitude. Fine stage GMRES rises `96.45%`, while native
fixed/centered spatial margins decline `34.19% / 35.54%`. Some integrated
diagnostics improve, but the local cone margin and work trend worsen; two
grids do not establish convergence.

**Failure or boundary found:** The predeclared stage-7 acceptance gate fails
twice: the canonical first full correction becomes fixed/centered
`Gamma_2`-nonpositive, and the strict low-pair core broadens materially.
Therefore the accepted E-028 lineage remains at `6/12`, SHA-256
`ff82363833c84e416e020a8df56d6067b6b1f7612c41f30f6499d6b95690babb`.
The positive stage-7 endpoint is useful negative/path evidence, not an
accepted checkpoint and not evidence for a physical scalar field.

**Blank space or new idea:** The half-step sensitivity identifies a narrow
computational opportunity: migrate to a new fingerprinted campaign whose
line search explicitly enforces active, fixed, and centered full-`Gamma_2`
positivity and records those margins per accepted iterate. Retry only the
`6/12 -> 7/12` source interval with source-step bisection (starting at the
`13/24` midpoint), then demand compatible fine/coarse paths and a
predeclared tail cap. This would test whether the conflict is a corrector
artifact without rewriting the failed canonical history.

**Hypothesis updates:** H-019 remains `Medium-low`, but verified branch reach
does not advance beyond `6/12`. E-028 is blocked at its canonical stage-7
path/refinement gate. B-030 records the new endpoint-versus-path boundary,
and E-029 defines the diagnostic-cone-safe retry. The exact center remains
force-free, the cosmological `r0=1 m` translation remains only about
`6e-35 m/s^2`, and no artificial-gravity, inertial-control, spacetime-
engineering, reactionless-propulsion, or faster-than-light conclusion
follows.

**Verification and artifact identity:** The retained stage-7 path-conflict
artifact SHA-256 is
`96ce02aca8198d23c1bb5c563bdf18b14c79ef4009dd03fd75fa2e77525c479b`;
the retained work-checkpoint SHA-256 is
`00fa8ce4cddece362e01b179f01f6ecfe8cc93cbc7b8eaa2e0eaeb520418e9c2`.
Their loaders agree exactly on the endpoint field and report. Neither name
or work suffix denotes acceptance.

**Next best step:** Implement E-029 as a fingerprinted, schema-compatible
diagnostic-cone-safe continuation branch. Preserve accepted stage 6 and this
failed stage-7 history; bisect `6/12 -> 7/12`, persist all three cone
diagnostics per accepted iterate, and require a positive fine/coarse sampled
path plus a non-broadening tail before reconsidering `7/12`. Do not advance
to `8/12` or start outer-box, density, asymmetry, target, EFT, or propulsion
work.

## 2026-07-27 - E-029 Diagnostic-Cone-Safe Continuation

**Focus question:** Can a new, fingerprinted continuation campaign advance
from immutable accepted E-028 stage `6/12` through the prescribed `13/24`
midpoint to `7/12` while keeping every accepted iterate and bounded segment
sample inside the active, fixed, and centered full shifted-`Gamma_2` cones on
both fine and fresh coarse grids, without broadening the predeclared
source-relative low-pair tails?

**Sources read:**

- L. Gårding, “An inequality for hyperbolic polynomials,” *Journal of
  Mathematics and Mechanics* **8** (1959), 957-965,
  DOI `10.1512/IUMJ.1959.8.58061`; and L. Caffarelli, L. Nirenberg, and
  J. Spruck, “The Dirichlet problem for nonlinear second-order elliptic
  equations, III,” *Acta Mathematica* **155** (1985), 261-301,
  DOI `10.1007/BF02392544`. These support the convex hyperbolicity cone and
  concavity setting, not a branch-uniqueness claim for this discretization.
- B. Froese, A. Oberman, and T. Salvador, “Numerical methods for the
  2-Hessian elliptic partial differential equation,” *IMA Journal of
  Numerical Analysis* **37** (2017), 2093-2122,
  DOI `10.1093/imanum/drw007`, arXiv:`1502.04969`; and G. Awanou,
  “Iterative methods for k-Hessian equations,” *Methods and Applications of
  Analysis* **25** (2018), 51-72,
  DOI `10.4310/MAA.2018.v25.n1.a3`, arXiv:`1406.5366`. Their convergence
  and local-iteration results require hypotheses not established for the
  reflected cylindrical min-of-frames campaign.
- J.-M. Mirebeau, “Discretization of the 3D Monge-Ampere operator, between
  wide stencils and power diagrams,” *ESAIM: M2AN* **49** (2015),
  1511-1523, DOI `10.1051/m2an/2015016`; C. den Heijer and
  W. Rheinboldt, “On steplength algorithms for a class of continuation
  methods,” *SIAM Journal on Numerical Analysis* **18** (1981), 925-948,
  DOI `10.1137/0718066`; and R. Kearfott and Z. Xing, “An interval step
  control for continuation methods,” *SIAM Journal on Numerical Analysis*
  **31** (1994), 892-914, DOI `10.1137/0731048`. Residual backtracking and
  corrector diagnostics motivate dyadic source-step subdivision, but a true
  no-jump result would require validated interval/rank hypotheses absent
  here.
- L. Qi and J. Sun, “A nonsmooth version of Newton's method,”
  *Mathematical Programming* **58** (1993), 353-367,
  DOI `10.1007/BF01581275`. Semismooth Newton convergence requires
  generalized-Jacobian regularity that was not proved for this active-frame
  operator.

**Deepening performed:** Added a separate E-029 campaign rather than altering
E-028. It validates the immutable stage-6 container, field, linear field,
report, system, source, runtime, dependencies, and implementation contents.
Historical absolute module paths are treated as non-semantic only after the
stored module bytes match exactly; the E-028 validator itself is unchanged.
The new line search preserves the strict nonlinear/Krylov/wide gates and
requires positive active, fixed, native-centered, and matched-centered
`sigma_1`, minimum pair sum, and `sigma_2` at each accepted endpoint plus
nine evenly spaced interior samples of every accepted Newton segment.

The endpoint tail audit uses the predeclared matched centered step `0.25`,
common window `rho<=78.5`, four-neighbor topology, and both raw/positive-
weight node counts and source-relative cylindrical weights. Grid-specific
caps were frozen from the immutable fine stage 6 and a freshly reconstructed
coarse stage 6 before testing `13/24`. Tails are endpoint acceptance gates,
not off-root Newton-state gates.

**What changed:** Fine `13/24` closes in four Newton corrections and `208`
GMRES inner iterations at relative residual `4.85255e-8`; coarse `13/24`
closes in three corrections and `106` GMRES at `1.17625e-8`. Every accepted
step is `1.0`, every direct linear residual is below `1e-8`, and all four
full-cone reconstructions plus every nine-point segment audit remain
positive. Fine endpoint active `sigma_1/pair/sigma_2` minima are
`0.7500013 / 0.0172407 / 0.1874845`; fixed values are
`0.7500410 / 0.00991990 / 0.0259839`; native-centered values are
`0.7500384 / 0.00974052 / 0.0255058`; and matched-centered values are
`0.7501307 / 0.0173536 / 0.0605420`.

The fine `pair<0.02` tail nevertheless grows from its frozen stage-6 cap of
`10` nodes, one component, and source-support weight `0.000270316` to `35`
nodes, one component, and `0.000512697`. Fine `pair<0.05` also grows
`227 -> 232` nodes even though its source-support weight remains
`0.003138624`. On the coarse grid, `pair<0.02` grows from `5` nodes, one
component, and `0.000414605` to `16` nodes, two components, and
`0.001586027`; its `pair<0.05` tail passes. Each grid therefore fails its
own frozen no-broadening cap already at the midpoint.

**Reasoning:** Dyadic source-step subdivision repairs the E-028 corrector-path
excursion at `13/24`, but it does not repair the independently declared
tail/refinement boundary. Convexity of a fixed reconstruction's
hyperbolicity cone helps interpret an exactly checked chord; it does not make
finite sampling an interval certificate, smooth the active-frame selection,
prove uniqueness, or transfer a Cartesian convergence theorem to this
cylindrical scheme. Path admissibility and source-layer margin erosion are
therefore separate gates.

A separately labeled scratch sensitivity continued the cone-safe split path
from `13/24` to `7/12`: all sampled cone paths stayed positive and the fine
endpoint matched the rejected E-028 stage-7 field to relative `L2=9.36e-12`.
The fine `pair<0.02` tail still reached `74` nodes and source-support weight
`0.000721390`; the coarse tail reached `30` nodes in two components and
weight `0.00173081`. This was not written as a campaign artifact and cannot
be accepted, but it shows that the tail failure is not cured by the repaired
corrector path.

**Failure or boundary found:** E-029 fails its predeclared tail gate on both
grids at `13/24`, before `7/12` and before the still-required endpoint
active-frame tie/WCDD audit. The campaign stops and leaves immutable accepted
lineage at E-028 stage `6/12`, checkpoint SHA-256
`ff82363833c84e416e020a8df56d6067b6b1f7612c41f30f6499d6b95690babb`.
The two retained E-029 files are explicitly `tail_conflict` artifacts, not
accepted checkpoints or evidence of a physical field.

**Blank space or new idea:** The remaining narrow numerical question is
whether the low-pair growth is mainly a brittle hard-threshold crossing or a
mesh-dependent precursor to genuine loss of admissibility. E-030 should use
the accepted stage-6 tangent equation to predict where the margin spectrum
crosses `0.05` and `0.02`, add a threshold-free weighted deficit diagnostic,
and verify only the dyadic amplitudes `49/96` and `25/48` on fine and coarse
grids. This is an unclear numerical regime, not an engineering or physics
crack.

**Hypothesis updates:** H-019 remains `Medium-low`; its accepted reach stays
at `6/12`. E-029 is complete as a negative path-versus-tail separation.
B-031 records that a cone-safe corrector path does not rescue a broadening
source-layer tail, and E-030 becomes the next bounded diagnostic. The exact
center remains force-free, the cosmological `r0=1 m` translation remains
about `6e-35 m/s^2`, and no artificial-gravity, inertial-control, spacetime-
engineering, reactionless-propulsion, or faster-than-light conclusion
follows.

**Verification and artifact identity:** The retained fine `13/24`
tail-conflict artifact has container SHA-256
`12459bdb21a8eefdd1a1ccfadf65b04556f533968d2f7b743eeb43ad27e7cf45`
and field SHA-256
`8cfefb872228b31139af1db64c31f582d1e82e9ccf9f35346ec28e0127891dd0`.
The retained coarse artifact has container SHA-256
`75242c78edadbf3f1e9194f82380b17ed4b7abcadc539ccc12025f25def36c9e`
and field SHA-256
`8681fd3614a54389d5fc58166077cd0090490c8480fa0d1872f9144173929329`.
Their embedded reports reproduce the final canonical run and loader-verified
field digests. The full repository suite passes `104/104`; every checkpoint
manifest digest verifies; `pip check` reports no broken requirements; and
`git diff --check` is clean.

**Next best step:** Run E-030 from immutable accepted stage 6: compute the
fine/coarse tangent-predicted low-pair margin-crossing spectrum, then verify
only `49/96` and `25/48` with the unchanged cone/path and tail bookkeeping.
Do not relax E-029, accept any state beyond `6/12`, revisit `7/12`, advance
to `8/12`, or begin outer-box, density, asymmetry, target, EFT, or propulsion
work.

## 2026-07-28 - E-030 Tangent-Predicted Margin Spectrum

**Focus question:** Starting from immutable accepted E-028 stage `6/12`, does
the early E-029 low-pair tail growth arise chiefly because grid samples cross
the hard `0.05` and `0.02` cutoffs, or does a threshold-free source-weighted
diagnostic still show a mesh-dependent precursor to loss of admissibility?
Predict with the exact stage-6 tangent and verify only `49/96` and `25/48` on
fine and fresh coarse grids without changing accepted lineage.

**Sources reviewed:**

- Froese, Oberman, and Salvador, *IMA Journal of Numerical Analysis* **37**
  (2017), 209-236, DOI `10.1093/imanum/drw007`, for the positive pair-sum
  characterization of the three-dimensional `Gamma_2` branch and the need
  for coupled spatial/directional refinement.
- Barles and Souganidis, *Asymptotic Analysis* **4** (1991), 271-283,
  DOI `10.3233/ASY-1991-4305`, for the monotone/stable/consistent plus
  comparison-principle convergence framework that this cylindrical
  two-grid diagnostic does not establish.
- Cohen-Steiner, Edelsbrunner, and Harer, *Discrete & Computational
  Geometry* **37** (2007), 103-120,
  DOI `10.1007/s00454-006-1276-5`, for stability of sublevel persistence on
  one common space under a sup-norm perturbation. This complicates any claim
  based on raw component counts from different grids.

**Deepening work completed:** (1) reviewed three primary numerical/topological
sources, including a theorem that narrows what topology can mean here; (2)
derived and solved the exact active stage-6 tangent equation on both grids;
(3) scanned tangent-predicted crossings throughout `1/2 <= a <= 13/24` but
ran nonlinear roots only at the two predeclared amplitudes; (4) compared the
local tangent bound with four full nonlinear solves under unchanged E-029
gates; (5) separated E-029-compatible source-support-volume weighting from
literal source-charge weighting `w*S`; (6) retained four-neighbor topology
and the frozen tail ledger; and (7) designed a common-space persistence test
precisely enough for the next run.

**What changed:** Added `models/e030_margin_spectrum.py` and nine focused unit
tests. The module validates the accepted stage-6 container, field, linear
field, report, source/operator, runtime, AMG configuration, and historical
module bytes through E-029's existing loader. It reconstructs coarse stage 6
freshly and writes no field artifact.

For

```text
F(phi,a) = M(phi) - 3/(16 c_3^2) - a S/(2 c_3),
```

the tangent obeys `J_6 dphi/da = S/(2c_3)`. The strict helper solves
`(-J)x=rhs`, so E-030 supplies `rhs=-S/(2c_3)` and separately audits
`J_6 dphi/da-S/(2c_3)`. Fine/coarse tangents take `56/42` GMRES iterations
with direct residual ratios `6.385e-9 / 6.265e-10`.

The prescribed nonlinear roots all close without relaxing a gate:

| Grid and amplitude | Newton / GMRES | Relative nonlinear `L2` |
| --- | ---: | ---: |
| Fine `49/96` | `3 / 156` | `2.52e-10` |
| Fine `25/48` | `3 / 155` | `1.88e-10` |
| Coarse `49/96` | `3 / 108` | `2.19e-12` |
| Coarse `25/48` | `2 / 79` | `4.52e-9` |

Every endpoint and accepted Newton state passes the active, fixed,
native-centered, and matched-centered full-`Gamma_2` checks plus wide and
direct-Krylov gates. Nine stored points on each accepted correction segment
pass all four full-`Gamma_2` cone checks; the wide and Krylov gates are
endpoint/accepted-state diagnostics rather than interior-sample claims.

**Threshold result:** The tangent predicts the hard counts unusually well.
For fine `pair<0.02`, predicted/observed totals are `14/14` at `49/96` and
`22/20` at `25/48`; coarse is exactly `7/7` and `11/11`. Fine
`pair<0.05` is `228/228` and `231/231`; coarse is `66/66` and `67/66`.
The raw count growth is therefore consistent with grid samples crossing
fixed thresholds smoothly; the sampled evidence does not indicate a jump.

**Threshold-free and topology result:** That explanation is not a rescue.
Fine `pair<0.02` changes `10 -> 14 -> 20` nodes and stays one connected
component. Its source-support-volume tail weight is unchanged at
`0.000270316` through `49/96`, showing that the first four new fine nodes are
cutoff-sensitive but outside source support, then rises to `0.000340976` at
`25/48`. Coarse changes `5 -> 7 -> 11`, creates a second source-supported
component already at `49/96`, and grows
`0.000414605 -> 0.000730494 -> 0.001296462`.

Source-support-volume mean positive deficits at `49/96` and `25/48` are fine
`9.794e-5 / 1.904e-4` and coarse `1.433e-4 / 2.809e-4`, making coarse
`1.46-1.48x` larger. Source-charge means are much smaller: fine
`1.041e-6 / 1.969e-6`, coarse `1.686e-6 / 3.294e-6`. Only about
`0.28-0.34%` of sampled source charge sits where the pair margin decreases,
so the erosion is concentrated in the low-density smoothing layer. The
charge-weighted coarse/fine discrepancy remains `1.62-1.67x`, however, and
the split topology remains.

**Reasoning:** Hard-threshold node counts are brittle, and the tangent shows
that E-029's apparent jump overlays a smooth local trend. The smooth trend is
still resolution dependent in magnitude and component structure. The two
weightings answer different questions: support-volume weighting is sensitive
to the physical extent of the smoothing layer, while `w*S` measures how much
sampled source strength occupies it. Neither may be silently substituted for
the other. Two grids and positive sampled paths cannot decide whether the
detached lobe converges, disappears, or is a derivative-reconstruction
artifact.

**Failure or boundary found:** E-030 is a mixed/negative diagnostic. It
finds the raw count jump consistent with smooth threshold crossings rather
than evidence of a sudden branch event, but it does not clear the
tail/refinement boundary. Both grids fail a frozen tail cap by `49/96`;
coarse/fine normalized deficits and topology disagree.
No E-030 field was saved, accepted, or added to the checkpoint manifest.
Accepted lineage remains E-028 stage `6/12`, SHA
`ff82363833c84e416e020a8df56d6067b6b1f7612c41f30f6499d6b95690babb`.

**Blank space or new idea:** The unresolved numerical question is now a
common-space stability problem. E-031 should restrict the fine matched
pair-margin field to exactly coincident coarse nodes in the source-layer
window, put both scalar fields on one four-neighbor complex, and compare
their zero-dimensional sublevel persistence with their common-node sup-norm
difference `epsilon`. A feature of lifetime `p` costs `p/2` to match to the
diagonal, so a detached component with `p <= 2 epsilon` remains unresolved
under the Cohen-Steiner stability bound. Keep source-support-volume and
source-charge deficit spectra separate.

**Hypothesis updates:** H-019 remains `Medium-low`; B-032 records that
tangent-predictable cutoff counts do not erase mesh-dependent erosion. E-030
is complete and E-031 is the next bounded experiment. The symmetric center
remains force-free, the fiducial cosmological translation remains only about
`6e-35 m/s^2`, and nothing here supports useful artificial gravity, inertial
control, spacetime engineering, reactionless propulsion, or faster-than-light
travel.

**Verification and provenance:** Final transient report SHA-256
`428f093858c3c326e1470bb8ea6a95eef095259192a54f1ffb777fee5c71448b`;
E-030 module SHA-256
`d2d96f1cc0d2366fe8408e26df99c79f5bcbb58adc8c897170203352ecf01baf`.
The report records peak RSS `1.573 GiB` and `87.14 s` for the final canonical
run. All `113` workspace unit tests, module compilation, checkpoint-manifest
integrity, dependency, LFS, and diff checks pass.

**Next best step:** Run E-031 only at `49/96` and `25/48`: compare the fine
and coarse matched pair-margin fields on identical physical nodes and one
four-neighbor complex using common-node sup norm and zero-dimensional
sublevel persistence/merge trees, requiring feature lifetime greater than
twice the sup discrepancy before calling it stable. Do not accept beyond
`6/12`, advance to
`13/24` or `7/12`, or begin outer-box, density, asymmetry, target, EFT, or
propulsion work.

## 2026-07-29 - E-031 Common-Space Persistence Screen

**Focus question:** At only the unaccepted `49/96` and `25/48` diagnostics,
does E-030's detached coarse `pair<0.02` component have finite
zero-dimensional persistence lifetime greater than twice the fine/coarse
pair-margin sup discrepancy after both fields are placed on exactly the same
physical node graph?

**Sources reviewed:**

- Edelsbrunner, Letscher, and Zomorodian, *Discrete & Computational Geometry*
  **28** (2002), 511-533, DOI `10.1007/s00454-002-2885-2`, for filtered
  complexes, persistence, and feature lifetime.
- Cohen-Steiner, Edelsbrunner, and Harer, *Discrete & Computational
  Geometry* **37** (2007), 103-120,
  DOI `10.1007/s00454-006-1276-5`, for the common-space bottleneck bound
  `d_B <= ||f-g||_infinity`.
- Chazal, Cohen-Steiner, Glisse, Guibas, and Oudot, *SoCG 2009*, 237-246,
  DOI `10.1145/1542362.1542407`, as complicating evidence that different-space
  comparisons require explicit algebraic proximity rather than raw component
  counts.
- Barles and Souganidis 1991; Crandall, Ishii, and Lions 1992; and Froese,
  Oberman, and Salvador 2017 for the separate viscosity/discretization
  boundary. The correct Froese-Oberman-Salvador page range is
  `2093-2122`; the prior E-030 log's `209-236` was a bibliographic typo and
  is corrected explicitly here without rewriting that historical entry.

**Deepening work completed:** (1) reviewed four primary source families,
including different-space and derivative-convergence complications; (2)
predeclared ordinary-H0 lower-star and strict `p>2 epsilon` conventions;
(3) reconstructed only the two E-030 endpoints under unchanged gates;
(4) mapped every coarse node to the exact `2i,2j` fine lattice node with no
interpolation between grids; (5) ran persistence on the full connected common
window and a positive-source induced sensitivity; (6) audited essential
classes, crop-boundary contact, birth/death levels, dying-branch bounding
boxes, and nearby fine intervals; (7) recomputed source-support-volume and
source-charge deficits with one common quadrature; and (8) designed E-032 to
attack the dominant scalar discrepancy rather than advancing the branch.

**What changed:** Added `models/e031_common_space_persistence.py` and nine
focused tests. Equal-valued vertices and edges enter at one filtration level;
ordinary-H0 finite intervals use `[birth,death)`, essential deaths are
recorded as null, and deterministic ties can create only zero-lifetime
representatives. Persistence and `epsilon` are unweighted. Volume and
`w*S` source-charge spectra remain separate.

The primary common graph has `77,735` vertices, `154,840` four-neighbor
edges, and one terminal component. The connected positive-source sensitivity
has `907` vertices and `1,688` edges. Fine source values equal coarse source
values bit for bit on mapped nodes.

| Amplitude | `epsilon` | `2 epsilon` | coarse birth | coarse death | lifetime `p` | `p/(2 epsilon)` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `49/96` | `0.119040574` | `0.238081148` | `0.019760745` | `0.024382798` | `0.004622053` | `0.019414` |
| `25/48` | `0.120302377` | `0.240604753` | `0.019320319` | `0.023836178` | `0.004515859` | `0.018769` |

The detached dying branch contains three nodes over
`rho=5.75-6.25`, `z=0.5`. One node lies below `0.02` at `49/96`; two do at
`25/48`. The branch does not touch the full-window crop boundary. It does
touch the positive-source mask boundary, so that induced graph is a
conditional sensitivity rather than the theorem-level decision surface.

The fine full-graph diagram contains a nearby bar at the same birth coordinate
with birth/death `0.024265289/0.030417719` and
`0.023845922/0.029937659`; its `L-infinity` diagram distance from the coarse
bar is `0.00603492/0.00610148`. It is born above `0.02`, so it does not make
a second fine component at the display threshold. This is a useful
threshold-crossing clue, not a proven spatial matching.

With one common coarse quadrature, fine/coarse mean positive deficits are:

| Measure | `49/96` fine / coarse / ratio | `25/48` fine / coarse / ratio |
| --- | ---: | ---: |
| Source-support volume | `9.654e-5 / 1.433e-4 / 1.484` | `1.874e-4 / 2.809e-4 / 1.499` |
| Source charge `w*S` | `1.066e-6 / 1.686e-6 / 1.582` | `2.065e-6 / 3.294e-6 / 1.595` |

**Reasoning:** On one finite graph with linear edge interpolation, the vertex
sup difference is the graph-function sup norm, so persistence stability gives
an `epsilon`-matching. A finite bar of lifetime `p` is `p/2` from the
diagonal. The coarse lobe's lifetime is only `1.94%/1.88%` of
`2 epsilon`, so the theorem permits it to disappear into the diagonal by a
wide margin. This does not show that the lobe is numerical noise; it shows
that the observed two-grid discrepancy is far too large to certify it.

The full-window and source-mask birth/death values agree, which removes one
obvious crop-death ambiguity. The systematic common-quadrature deficit ratios
remain, however. The sup discrepancy is localized at
`(rho,z)=(8.75,0.75)`, where fine/coarse pair margins are
`0.258418/0.139377` and `0.259653/0.139350`. That scale is the next
diagnostic target.

**Failure or boundary found:** E-031 does not validate the detached coarse
lobe as common-space persistence-stable, native-fine, or continuum topology.
It also does not disprove the feature. Persistence guarantees concern some
off-diagonal counterpart, not spatial identity; restricting the fine field
discards between-node information; and no theorem here gives convergence of
a Hessian-derived diagnostic. Accepted lineage remains immutable E-028 stage
`6/12`, checkpoint SHA
`ff82363833c84e416e020a8df56d6067b6b1f7612c41f30f6499d6b95690babb`.

**Blank space or new idea:** The unresolved space is now component-level
rather than topological. E-032 should keep the same transient endpoints and
node map, decompose the `~0.12` discrepancy into radial, mixed, axial, and
azimuthal matched-Hessian terms, and repeat only predeclared common physical
difference steps at the sup-error hotspot and lobe basin. This can distinguish
post-processing/reconstruction sensitivity from a broader field discrepancy.
It remains a numerical diagnostic, not an engineering opportunity.

**Hypothesis updates:** H-019 remains `Medium-low`. E-031 is complete as an
unresolved stability screen; B-033 records the new boundary; E-032 becomes
the next bounded experiment. Living-map pointers that still described E-029
or E-030 as future work were advanced explicitly. The exact center remains
force-free, the cosmological `r0=1 m` translation remains about
`6e-35 m/s^2`, and no artificial-gravity, inertial-control,
spacetime-engineering, reactionless-propulsion, or faster-than-light
conclusion follows.

**Verification and provenance:** Fine endpoints reproduce
`3/156` and `3/155` Newton/GMRES with relative residuals
`2.52e-10/1.88e-10`; coarse reproduces `3/108` and `2/79` with
`2.19e-12/4.52e-9`. All endpoints and accepted Newton states pass the
unchanged nonlinear, direct-Krylov, wide, and four full-`Gamma_2` gates;
every frozen tail gate remains failed. The transient canonical report SHA-256
is `f208acb17bb6c2243a8fae6364e84e12e2d1beb12e5b00ac8e7bea2a30b58278`;
the E-031 module SHA-256 is
`0017917e7152427d97474e6f4c30a1f39d41466ce5f670080145aa63d01326bc`.
The report records `85.82 s` elapsed and `1.572 GiB` peak RSS. All `122`
workspace tests pass, all model/test modules compile, dependencies are
consistent, and every checkpoint matches `SHA256SUMS`. No field, checkpoint,
or manifest entry was written.

**Next best step:** Run E-032 only at transient `49/96` and `25/48` from
immutable stage 6. On identical nodes, decompose the matched pair-margin
discrepancy into radial, mixed, axial, azimuthal, eigenvalue, and physical
difference-step contributions at `(8.75,0.75)` and the
`rho=5.75-6.25, z=0.5` lobe basin. Do not save an endpoint, advance to
`13/24` or `7/12`, or begin outer-box, density, asymmetry, target, EFT, or
propulsion work.

## 2026-07-30 - E-032 Matched-Hessian Discrepancy Decomposition

**Focus question:** At only the transient `49/96` and `25/48` endpoints,
which radial, mixed, axial, azimuthal, eigenvalue, or physical
reconstruction-step contribution dominates E-031's approximately `0.12`
fine/coarse common-node pair-margin discrepancy at `(rho,z)=(8.75,0.75)`
and in the `rho=5.75-6.25`, `z=0.5` detached-lobe basin?

**Sources reviewed:** NIST DLMF section 3.4 and Prentice 2011 on centered
finite-difference error and step selection; Hoffman and Wielandt 1953, Ky Fan
1949, Overton and Womersley 1992, Magnus 1985, Lewis 1996, and Davis and Kahan
1970 on symmetric eigenvalue sums, perturbation bounds, differentiability,
and gap dependence; Barles and Souganidis 1991, Crandall, Ishii, and Lions
1992, and Froese, Oberman, and Salvador 2017 on the separate
potential-versus-derivative convergence boundary. Official Oxford metadata
also shows that the Froese-Oberman-Salvador article is pages `209-236`, not
`2093-2122`; the E-031 historical entry's attempted correction was itself
wrong, and this entry corrects that mistake explicitly rather than rewriting
history.

**Deepening work completed:** (1) replayed E-031 under its exact provenance
before adding the new diagnostic; (2) reviewed more than three primary or
authoritative numerical-analysis sources, including nonsmooth/gap and
step-size complications; (3) derived the exact axisymmetric identity
`pair=trace(H)-lambda_max(H)+2 shift`; (4) added an order-neutral
four-component Shapley ledger with all coalition-marginal envelopes and exact
closure; (5) checked Weyl and Hoffman-Wielandt perturbation bounds; (6)
recomputed only the two frozen transient endpoints and separated their grid
gap from the stage-6 baseline gap; (7) repeated the four fixed ROI nodes at
mesh-compatible physical steps `0.25` and `0.5`; (8) retained common-volume,
source-charge, eigenbranch, and lobe-node sign diagnostics; and (9) designed
E-033 to localize the remaining scale dependence without advancing or saving
the branch.

**What changed:** Added `models/e032_hessian_discrepancy.py` and focused
tests. The campaign validates immutable E-028 stage 6, reproduces fine
`49/96` and `25/48` in `3/156` and `3/155` Newton/GMRES and coarse in
`3/108` and `2/79`, then evaluates no new amplitude. All unchanged solver,
Krylov, wide, and four full-`Gamma_2` gates pass; every frozen tail gate
remains failed.

At the E-031 hotspot, signed differences and exact Shapley attributions are:

| Amplitude | Step | Fine minus coarse `pair` | Radial | Mixed | Axial | Azimuthal |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `49/96` | `0.25` | `0.119041` | `0.02350` | `0.01354` | `0.08039` | `0.00161` |
| `49/96` | `0.50` | `0.034289` | `0.02091` | `-0.00103` | `0.01290` | `0.00151` |
| `25/48` | `0.25` | `0.120302` | `0.02384` | `0.01338` | `0.08150` | `0.00159` |
| `25/48` | `0.50` | `0.034688` | `0.02146` | `-0.00112` | `0.01286` | `0.00149` |

At step `0.25`, axial is order-robust: its smallest coalition marginal is
`0.07777/0.07885`, larger than every competing maximum. The exact spectral
identity shows large cancellation rather than an eigenvalue switch:
`Delta trace=0.47083/0.47999` and
`-Delta lambda_max=-0.35178/-0.35969`. Every audited fine/coarse pair branch
remains lower-meridional plus azimuthal. The smallest transient-endpoint
top-eigenvalue gap is `1.2719`; including the stage-6 ROI baselines, the
minimum is `1.2637`.

At step `0.5`, however, the hotspot discrepancy falls by
`71.20%/71.17%` and radial becomes order-robustly dominant. Most of the
canonical hotspot mismatch also predates the transient continuation:
stage 6 already has `Delta pair=0.117658` at step `0.25`; progression to
`49/96` and `25/48` adds only `0.001383` and `0.002645`. This separates a
grid/reconstruction gap from the later source-amplitude response.

The lobe basin is heterogeneous. At step `0.25`, its three nodewise
differences are `0.00725, 0.00450, 0.01839` at `49/96` and
`0.00758, 0.00453, 0.01735` at `25/48`. At step `0.5`, the first node changes
sign and every fine/coarse lobe pair exceeds `0.046`; the `pair<0.02`
three-node basin therefore leaves the sublevel set under that smoother
reconstruction. E-032 did not search the full step-`0.5` common field for a
displaced component. This is a scale sensitivity, not evidence that the
feature is noise or absent.

**Reasoning:** The pair margin is the sum of the two smallest shifted
eigenvalues. For the axisymmetric Hessian it equals
`trace(H)-lambda_max(H)+2 shift`, so the spectral cancellation can be
checked exactly. Weyl gives `|Delta pair| <= 2||Delta H||_2`, and
Hoffman-Wielandt supplies the ordered-eigenvalue Frobenius check; every
reported point passes both. Shapley averaging over all `24` component
replacement orders then supplies one explicit, symmetric attribution
convention without pretending that a nonlinear eigenvalue function has a
unique causal component budget.

The physical-step comparison is more decisive than the canonical component
ranking. Both `0.25` and `0.5` land on lattice nodes of both grids, yet they
produce different dominant components and a `~71%` discrepancy change. A
smaller `0.125` step was rejected from the primary comparison because it is
half a coarse cell: bilinear interpolation would multiply pure coarse
second differences by `H/delta=2` while treating mixed and first derivatives
differently.

**Failure or boundary found:** E-032 explains the declared E-031
`0.25`-step discrepancy but does not identify a reconstruction-independent
cause. Axial curvature dominates that one postprocessor; radial dominates at
`0.5`, one lobe node changes sign, and all three frozen lobe-basin nodes leave
the cutoff. The full step-`0.5` field was not searched for a displaced
component. Uniform convergence of a potential would not imply convergence of
this recovered Hessian, and only two grids exist. Accepted lineage therefore
remains immutable E-028 stage `6/12`, checkpoint SHA
`ff82363833c84e416e020a8df56d6067b6b1f7612c41f30f6499d6b95690babb`.

**Blank space or new idea:** The remaining blank space is numerical and
testable: is the `0.25` axial excess produced by a one-cell-scale curvature
mode in the exact common-node potential difference, or by a spatially
coherent feature that survives a declared local recovery scale? E-033 should
hold the same endpoints fixed, express every Hessian-component difference as
an exact stencil applied to `e=phi_fine-phi_coarse` on common nodes, compare
nested `0.25/0.5` axial stencils and one predeclared local quadratic-recovery
window, and map signed cancellation across the hotspot and lobe strip. This
can test whether the behavior is more consistent with a one-cell artifact or
a coherent error field and inform whether to park the branch. It still cannot
establish continuum Hessian convergence; that would require a justified
recovery analysis and a refined nonlinear-grid sequence.

**Hypothesis updates:** H-019 remains `Medium-low` and accepted branch reach
remains `6/12`. E-032 is complete as a negative/mixed
reconstruction-sensitivity result; B-034 records the new boundary and E-033
becomes the next bounded diagnostic. No physical field, artificial gravity,
inertial control, spacetime engineering, reactionless propulsion, or
faster-than-light conclusion follows.

**Verification and provenance:** The transient E-032 report SHA-256 is
`c167d3db04f4798b8dedce79745a5bc8a570a02a1a0325aab7b3d6f30d342b36`;
the campaign module SHA-256 before documentation-only edits is
`5772d892b652ba03878b50162f2e8391c284c174eda7f4999310a057f941a7b7`.
The report records `80.70 s` elapsed and `1.570 GiB` peak RSS. No field,
checkpoint, retained work snapshot, or manifest entry was written. All `130`
workspace tests pass, every model/test module compiles, `pip check` reports no
broken requirements, every tracked checkpoint matches `SHA256SUMS`, Git LFS
integrity passes, and the final diff has no whitespace errors.

**Next best step:** Run E-033 only at the same transient `49/96` and
`25/48` endpoints from immutable stage 6. On the fixed common lattice,
decompose the fine-minus-coarse potential error into exact nested
`0.25/0.5` component stencils and one predeclared local quadratic recovery at
the hotspot and lobe strip. Stop after assessing whether the axial excess is
more consistent with a one-cell-scale or spatially coherent error. Do not save
endpoints, relax any tail gate, advance amplitude, or begin outer-box, density,
asymmetry, target, EFT, or propulsion work.

## 2026-07-31 - E-033 Common-Node Potential-Error Stencils

**Focus question:** At only the same transient `49/96` and `25/48`
endpoints, is E-032's reconstruction-scale change more consistent with
one-cell-scale content in the exact common-node potential error or with a
spatially coherent error that survives one predeclared local quadratic
recovery at the frozen hotspot and three-node lobe basin?

**Sources reviewed:** Savitzky and Golay 1964 on local least-squares
differentiation; Warming and Hyett 1974 and Lele 1992 on modified-equation
and modified-wavenumber diagnostics; Zhang and Naga 2005 and Guo, Zhang, and
Zhao 2017 on polynomial-preserving recovery under stated mesh hypotheses;
Picasso et al. 2011 and Kamenski and Huang 2014 on local quadratic Hessian
recovery, topology dependence, and the possibility of a nonconvergent
recovered Hessian. These support a manufactured polynomial gate and an
auditable fixed recovery, not a superconvergence claim for these nonlinear
finite-difference fields.

**Deepening work completed:** (1) froze the window, weights, basis, endpoints,
and two centered steps before the replay; (2) mapped all four `5 x 5`
patches by integer coarse indices and the exact `2:1` fine map, producing
`100` references to `60` unique common nodes and using no interpolation;
(3) recorded all `25` fine, coarse, and error values per patch; (4) expressed
radial, mixed, axial, and azimuthal fine-minus-coarse component gaps as exact
linear stencils of `e=phi_fine-phi_coarse`; (5) exposed the exact nested
`0.25-minus-0.5` detail stencils, including the negative fourth-difference
identity for pure curvatures; (6) applied one unweighted total-degree-two
least-squares recovery over the same `+/-0.5` support, recording rank,
condition, weights, and residuals; (7) validated all degree-two monomials
and a general quadratic to roundoff; and (8) retained smooth-quartic,
long-wave, and Nyquist controls that show why scale disagreement does not
identify its own cause.

**What changed:** Added `models/e033_potential_error_stencils.py` and focused
tests. The campaign validates immutable E-028 stage 6, reconstructs fresh
coarse stage 6, and recomputes only `49/96` and `25/48`. Fine roots reproduce
`3/156` and `3/155` Newton/GMRES and coarse roots reproduce `3/108` and
`2/79`. All inherited nonlinear, direct-Krylov, wide, and four
full-`Gamma_2` gates pass; every frozen tail gate remains failed.

At the E-031 hotspot, the fine-minus-coarse component gaps are:

| Amplitude | Recovery | Radial | Mixed | Axial | Azimuthal |
| --- | --- | ---: | ---: | ---: | ---: |
| `49/96` | centered `0.25` | `0.028904` | `-0.017571` | `0.440309` | `0.001612` |
| `49/96` | centered `0.5` | `0.022047` | `0.002340` | `0.251346` | `0.001510` |
| `49/96` | quadratic | `0.007631` | `-0.001174` | `0.215699` | `0.001884` |
| `25/48` | centered `0.25` | `0.029280` | `-0.017399` | `0.449122` | `0.001592` |
| `25/48` | centered `0.5` | `0.022607` | `0.002568` | `0.255821` | `0.001486` |
| `25/48` | quadratic | `0.007857` | `-0.000942` | `0.219232` | `0.001869` |

The quadratic error-component vector is nearer in Frobenius norm to the
`0.5` centered vector at every one of the `8` endpoint/ROI cases. At the
hotspot its axial value is about `6.3x` closer to `0.5` than to `0.25`, and
the fit residual RMS is `4.80%/4.83%` of the local error range. Across the
three lobe nodes, axial values fall from `0.400-0.663` at `0.25` to
`0.212-0.287` at `0.5` and `0.178-0.218` under the quadratic recovery.
The fit also returns a nonzero axial coefficient at every lobe node. Lobe fit
residual RMS is `10.99-11.80%` of range and maximum residual is
`19.10-20.44%`, so it is not a clean local quadratic.

**Reasoning:** Differentiation is linear, so every component gap must equal
the declared stencil applied to the exact common-node potential error; all
closures pass within `2e-11`. The pair margin is nonlinear in Hessian
eigenvalues, however. Re-eigenvaluating the separately recovered fine and
coarse Hessians makes the quadratic pair discrepancy closer to the `0.5`
pair at only the two hotspot cases, not at the six lobe cases. That is not a
contradiction: radial, mixed, axial, and azimuthal changes undergo spectral
cancellation. It prevents the component-localization result from becoming a
recovery-independent lobe statement.

The quadratic fit itself shares the larger stencil's `+/-0.5` outer support.
Its proximity to the `0.5` result is therefore not an independent convergence
point. More strongly, the smooth quartic, long-wave, and Nyquist controls all
put the quadratic component vector nearer the `0.5` vector despite encoding
mutually different mechanisms; the quartic even has a zero analytic Hessian
at its center. The observed nearest-scale ordering is therefore
non-identifying.

**Failure or boundary found:** E-033 exactly localizes the nested
`0.25-minus-0.5` component detail and finds a nonzero axial coefficient under
the one fixed quadratic recovery, but the controls prevent either quantity
from being classified as a one-cell cause or a coherent continuum component.
It does not prove an interpolation artifact—no interpolation was used in the
patches—nor certify a continuum Hessian, classify the lobe as noise, or
recover a stable pair-margin feature. The overlapping lobe windows are
correlated, the two amplitudes are not independent samples, solver error is
not enclosed as a Hessian interval, and only two grids exist. Accepted
lineage remains immutable E-028 stage `6/12`, checkpoint SHA
`ff82363833c84e416e020a8df56d6067b6b1f7612c41f30f6499d6b95690babb`.

**Blank space or new idea:** Before another expensive nonlinear replay,
E-034 should qualify the postprocessors themselves. Compute the exact 2D
Fourier/modified-wavenumber symbols of the `0.25`, `0.5`, and fixed
25-node quadratic component stencils, including the local
`phi_r/rho` factor; map their resolvable and null bands; and show the
non-unique smooth/grid-scale mode mixtures compatible with E-033's recorded
component ratios. This is an analytic/manufactured calculation only. A later
nonlinear refinement would require a preregistered three-grid recovery
sequence, not another recovery window chosen after seeing these endpoints.

**Hypothesis updates:** H-019 remains `Medium-low`, but its status now records
E-033's mixed error-first localization. B-035 records that exact stencil
closure and polynomial recovery do not supply derivative convergence. E-033
is complete; E-034 becomes the next bounded calculation. The exact center
remains force-free, the cosmological `r0=1 m` translation remains about
`6e-35 m/s^2`, and no physical field, artificial gravity, inertial control,
spacetime engineering, reactionless propulsion, or faster-than-light
conclusion follows.

**Verification and provenance:** The final transient report SHA-256 is
`032b19f33f61d0b7892c4c7c902d721f5e0795bffdc1748c236c9a6de53febfe`;
the E-033 module SHA-256 before documentation-only edits is
`ff12ad13b6bc807b0b5c814ea2ea1a932941f7da1eff8ac26223a8aca02d840e`.
The report records `81.66 s` elapsed and `1.535 GiB` peak RSS. No field,
checkpoint, retained work
snapshot, or manifest entry was written. All `141` workspace tests pass;
every model/test module compiles; `pip check` reports no broken requirements;
all tracked checkpoints match `SHA256SUMS`; Git LFS integrity passes; and the
final diff has no whitespace errors.

**Next best step:** Run E-034 as a no-PDE-solve transfer-function
qualification of exactly the three frozen E-033 postprocessors. Derive and
test their component symbols against smooth polynomial, long-wave, and
Nyquist modes, and predeclare what a future three-grid recovery study would
have to show. Do not replay or save transient endpoints, relax a tail gate,
advance amplitude, or begin outer-box, density, asymmetry, target, EFT, or
propulsion work.
