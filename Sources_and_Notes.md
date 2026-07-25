# Sources And Notes

Add sources here with enough detail that future runs can judge quality quickly.

## Source Entry Template

```markdown
### Source title

- **Link:** ...
- **Type:** peer-reviewed paper / preprint / textbook / technical report / lecture notes / popular article / other
- **Quality:** high / medium / low / uncertain
- **Relevant claims:** ...
- **Useful equations or constraints:** ...
- **Impact on hypotheses:** ...
- **Follow-up:** ...
```

## Starter Source Targets

- Reviews of artificial gravity by rotation and human vestibular constraints.
- General relativity textbooks or lecture notes covering the equivalence principle, stress-energy tensor, weak-field limit, and frame dragging.
- Reviews of warp drives, energy conditions, and quantum inequalities.
- Experimental reports on gravitomagnetism, Lense-Thirring measurements, and equivalence principle tests.
- Analog gravity reviews in condensed matter, optics, fluids, and Bose-Einstein condensates.

### Ruggiero & Tartaglia - Gravitomagnetic effects

- **Link:** https://arxiv.org/abs/gr-qc/0207065
- **Type:** peer-reviewed review paper / arXiv preprint
- **Quality:** high for weak-field gravitomagnetism orientation; older but still useful as a compact review.
- **Relevant claims:** Reviews gravitoelectromagnetic formalisms, Lense-Thirring effects, clock effects, spin couplings, and proposed experimental/observational tests. The authors explicitly treat orders of magnitude as central to judging feasibility.
- **Useful equations or constraints:** For order-of-magnitude engineering checks, use the weak-field frame-dragging scale near angular momentum `J`: `Omega_LT ~ 2GJ/(c^2 r^3)` up to geometry-dependent factors. Velocity-dependent acceleration estimates inherit the same `GJ/(c^2 r^3)` suppression.
- **Impact on hypotheses:** Supports H-002 as real GR physics, but strongly disfavors ordinary lab rotating masses as an artificial-gravity mechanism.
- **Follow-up:** Compare the review's proposed experiments with modern precision limits and any claimed anomalous rotating-superconductor results.

### Everitt et al. - Gravity Probe B final results

- **Link:** https://arxiv.org/abs/1105.3456
- **Type:** peer-reviewed experimental paper
- **Quality:** high; direct space experiment testing geodetic and frame-dragging effects with cryogenic gyroscopes.
- **Relevant claims:** Reports a measured frame-dragging drift of `-37.2 +/- 7.2 mas/yr`, compared with the GR prediction of `-39.2 mas/yr`, and a geodetic drift of `-6601.8 +/- 18.3 mas/yr`, compared with `-6606.1 mas/yr`.
- **Useful equations or constraints:** The measured Earth frame-dragging magnitude gives a useful sanity check: even planetary angular momentum produces a tiny precession rate requiring a specialized satellite experiment.
- **Impact on hypotheses:** Confirms the phenomenon behind H-002 but reinforces the magnitude boundary for artificial-gravity engineering.
- **Follow-up:** Use Gravity Probe B and LAGEOS/LARES as benchmark scales when evaluating any proposed gravitomagnetic propulsion or inertia-control claim.

### Ruggiero & Astesiano - A tale of analogies: gravitomagnetic effects, rotating sources, observers and all that

- **Link:** https://arxiv.org/abs/2304.02167
- **Type:** invited topical review / arXiv preprint
- **Quality:** high for current conceptual framing; useful because it stresses that gravitomagnetic analogies depend on spacetime splitting and observer/measurement choices.
- **Relevant claims:** Reviews multiple paths to magnetic-like gravitational effects and surveys recent theoretical and experimental developments. It is especially useful for avoiding over-literal electromagnetic analogies.
- **Useful equations or constraints:** Treat gravitoelectromagnetism as a weak-field, slow-motion analogy rather than a new force-engineering toolkit equivalent to electromagnetism.
- **Impact on hypotheses:** Narrows H-002 and H-004: analogies are valuable for calculation and intuition, but they do not bypass stress-energy scaling.
- **Follow-up:** Extract a concise "GEM analogy caveats" note before reviewing more exotic rotating-source proposals.

### Clément, Bukley, and Paloski - Artificial gravity as a countermeasure for mitigating physiological deconditioning during long-duration space missions

- **Link:** https://www.frontiersin.org/journals/systems-neuroscience/articles/10.3389/fnsys.2015.00092/full
- **Type:** peer-reviewed review article
- **Quality:** high for human-spaceflight artificial-gravity orientation; strongest as a synthesis and source map rather than as a final design standard.
- **Relevant claims:** Artificial gravity by linear acceleration or steady rotation is an integrated countermeasure candidate for weightlessness-induced deconditioning, but rotating environments impose sensorimotor limits through Coriolis forces, cross-coupled angular accelerations, gravity gradients, and head/body motion. Older comfort-zone assumptions around `6 rpm` were based on limited data and may be conservative; progressive exposure and habituation studies suggest higher rates can be tolerated in some conditions.
- **Useful equations or constraints:** Rotating-habitat apparent gravity follows `a = omega^2 r`. The article gives the sanity-check example that `~4 rpm` at `~56 m` radius produces about `1g`. Coriolis acceleration for radial motion scales as `2 omega v`, independent of habitat radius for a fixed walking speed.
- **Impact on hypotheses:** Strengthens H-001 as the established artificial-gravity baseline, but makes B-004 quantitative: the main barrier is not unknown physics but the radius/RPM/human-adaptation trade.
- **Follow-up:** Review intermittent short-radius centrifuge evidence separately; the continuous-habitat table does not answer minimum effective artificial-gravity dose.

### Navarro & Sancho - A characterization of the electromagnetic stress-energy tensor

- **Link:** https://arxiv.org/abs/1101.2505
- **Type:** arXiv preprint / mathematical physics note
- **Quality:** medium-high as a compact mathematical source for EM stress-energy; not an engineering feasibility paper.
- **Relevant claims:** Characterizes the electromagnetic stress-energy tensor from geometric/dimensional reasoning in the presence of a 2-form. Useful here because it keeps the source term explicit: electromagnetic fields do contribute stress-energy, not just forces on charges.
- **Useful equations or constraints:** For engineering estimates in SI units, pair the standard EM energy density `u = (epsilon0 E^2 + B^2/mu0)/2` with `rho = u/c^2`; the gravitational field still scales through `G rho`.
- **Impact on hypotheses:** Supports H-002 in principle and H-007 as a magnitude-limited subcase: EM fields are real GR sources but weak for artificial gravity at accessible field strengths.
- **Follow-up:** Later compare with a GR textbook treatment of active gravitational mass, pressure, and stress so pressure/tension terms are handled correctly outside Newtonian estimates.

### Gibbons & Herdeiro - The Melvin Universe in Born-Infeld Theory and other Theories of Non-Linear Electrodynamics

- **Link:** https://arxiv.org/abs/hep-th/0101229
- **Type:** peer-reviewed theoretical paper / arXiv preprint
- **Quality:** high for exact-solution theory; low as direct engineering guidance.
- **Relevant claims:** Derives Melvin-universe-type solutions for gravity coupled to nonlinear electrodynamics, showing that electric, magnetic, and dyonic field configurations can participate in exact spacetime geometries.
- **Useful equations or constraints:** Exact Einstein-Maxwell or Einstein-nonlinear-electrodynamics solutions are existence proofs for field-sourced curvature, not evidence of practical field strengths.
- **Impact on hypotheses:** Strengthens the conceptual part of H-002 while reinforcing B-007/B-008: source accounting is real, but field energy requirements dominate feasibility.
- **Follow-up:** Use Melvin-type solutions as mathematical testbeds only after building the stress-energy scale table for ordinary mass, EM fields, Casimir energy, and plasma fields.

### Tsagas & Mavrogiannis - Melvin's magnetic universe, magnetic tension, and collapse

- **Link:** https://arxiv.org/abs/2011.08245
- **Type:** peer-reviewed theoretical paper / arXiv preprint
- **Quality:** high for conceptual GR/MHD nuance around magnetic tension; not an artificial-gravity proposal.
- **Relevant claims:** Re-examines Melvin's idealized magnetic universe and magnetic fields in relativistic collapse. The important lesson for this workspace is that magnetic tension and field-line elasticity affect self-gravity and collapse behavior; magnetic stress is not equivalent to a simple dust mass density.
- **Useful equations or constraints:** Use `u/c^2` only as a first-order magnitude screen. If a configuration survives that screen, the next pass must include pressure/tension terms in the full stress-energy tensor.
- **Impact on hypotheses:** Adds nuance to H-007: the EM path fails by many orders of magnitude for practical artificial gravity, but future theoretical work must not reduce EM stress-energy to scalar mass density too early.
- **Follow-up:** If high-energy plasma or magnetically dominated configurations are reviewed, track anisotropic stress separately from energy density.

### Hahn et al. - 45.5-tesla direct-current magnetic field generated with a high-temperature superconducting magnet

- **Link:** https://www.nature.com/articles/s41586-019-1293-1
- **Type:** peer-reviewed experimental engineering paper
- **Quality:** high for the state of high-field magnet engineering.
- **Relevant claims:** Reports a `45.5 T` direct-current field using a high-temperature superconducting coil inside a resistive background magnet. The paper is useful as an accessible benchmark for real engineered field strengths.
- **Useful equations or constraints:** At `B = 45.5 T`, `u = B^2/(2 mu0) ~= 8.2e8 J/m^3` and `rho = u/c^2 ~= 9.2e-9 kg/m^3`. This is enormous for materials engineering but negligible gravitationally.
- **Impact on hypotheses:** Helps quantify B-008 and reject ordinary EM field generation as a practical artificial-gravity path under known physics.
- **Follow-up:** Add a table comparing continuous, pulsed, destructive, magnetar, and Schwinger-scale fields if EM fields re-enter the active queue.

### Ford & Roman - Quantum Field Theory Constrains Traversable Wormhole Geometries

- **Link:** https://arxiv.org/abs/gr-qc/9510071
- **Type:** peer-reviewed theoretical paper / arXiv preprint
- **Quality:** high for early quantum-inequality constraints on exotic spacetime geometries; model-dependent but foundational.
- **Relevant claims:** Negative energy allowed by QFT is constrained by magnitude-duration bounds. When applied locally to static traversable wormholes, the allowed stress-energy distributions become Planck-scale or require extreme hierarchy between throat size and the thickness of the negative-energy band.
- **Useful equations or constraints:** Use Ford-Roman quantum inequalities as a warning that a local negative-energy density is not enough; the sampled duration, curvature radius, boundary distance, and compensating positive energy matter.
- **Impact on hypotheses:** Narrows H-003: negative energy remains a theoretical loophole, but macroscopic wormhole-like geometries are strongly disfavored under known QFT constraints.
- **Follow-up:** Compare these constraints with later averaged null energy condition and quantum focusing results.

### Ford & Roman - Restrictions on Negative Energy Density in Flat Spacetime

- **Link:** https://arxiv.org/abs/gr-qc/9607003
- **Type:** peer-reviewed theoretical paper / arXiv preprint
- **Quality:** high for quantum-inequality basics in flat spacetime.
- **Relevant claims:** Derives simpler quantum-inequality bounds for negative energy density seen by inertial observers, including scalar and electromagnetic fields. The constraint behaves like an uncertainty-principle limit on how negative and how long a sampled energy density can be.
- **Useful equations or constraints:** A representative four-dimensional massless scalar bound scales as `rho_sampled >= -O(hbar/(c^3 tau^4))`; shorter sampling times permit larger negative densities, but long-duration macroscopic negative energy is tightly limited.
- **Impact on hypotheses:** Supports B-009: quantum fields violate classical energy conditions locally but do not allow arbitrary macroscopic negative-energy reservoirs.
- **Follow-up:** Extract the exact sampling-function constants before using the bound in any future quantitative metric-design estimate.

### Pfenning & Ford - The unphysical nature of Warp Drive

- **Link:** https://arxiv.org/abs/gr-qc/9702026
- **Type:** peer-reviewed theoretical paper / arXiv preprint
- **Quality:** high as a constraint paper on Alcubierre-style warp metrics; not evidence that FTL is enabled.
- **Relevant claims:** Applies quantum-inequality restrictions to the negative energy required by the Alcubierre warp metric and finds bubble-wall thicknesses near a few hundred Planck lengths, with physically unattainable integrated energy requirements.
- **Useful equations or constraints:** Treat the result as a boundary for localized metric engineering: even mathematically allowed metrics may demand stress-energy distributions whose thickness, magnitude, and total energy are outside physical reach.
- **Impact on hypotheses:** Reinforces H-003 and B-005: warp metrics are useful stress-energy diagnostics but do not provide a current route to FTL or practical artificial gravity.
- **Follow-up:** Later compare with newer "positive energy" or subluminal warp metric variants to see whether they shift propulsion-relevant constraints without implying FTL.

### Fewster - Lectures on quantum energy inequalities

- **Link:** https://arxiv.org/abs/1208.5399
- **Type:** lecture notes / mathematical physics review
- **Quality:** high for modern conceptual grounding of quantum energy inequalities.
- **Relevant claims:** QFT violates classical energy conditions, but many theories satisfy quantum energy inequalities that act as remnants of the classical conditions. The notes give examples, derivation methods, and implications.
- **Useful equations or constraints:** Use QEIs as the general framework behind B-009 rather than relying on one special Ford-Roman sampling function.
- **Impact on hypotheses:** Keeps H-003 alive only in a constrained form: allowed negative energy must be evaluated with the relevant QFT, state, observer, sampling, geometry, and boundaries.
- **Follow-up:** Read alongside averaged null energy condition and quantum null energy condition papers before making any stronger statement about warp/wormhole impossibility.

### Jaffe - The Casimir Effect and the Quantum Vacuum

- **Link:** https://arxiv.org/abs/hep-th/0503158
- **Type:** peer-reviewed theoretical paper / arXiv preprint
- **Quality:** high as a conceptual warning about interpreting the Casimir effect; not a gravity-engineering paper.
- **Relevant claims:** Casimir forces can be computed without treating zero-point energy as a directly extractable substance; they can be understood as relativistic quantum forces between charges and currents.
- **Useful equations or constraints:** For artificial-gravity work, the sign and magnitude of renormalized stress-energy should be tracked, but the positive energy and mechanical stresses of the apparatus cannot be ignored.
- **Impact on hypotheses:** Weakens naive Casimir-vacuum engineering claims; supports H-008 as rejected for now.
- **Follow-up:** If Casimir cavities are revisited, include full apparatus mass-energy and stresses, not only the idealized field region.

### Carroll - Lecture Notes on General Relativity

- **Link:** https://arxiv.org/abs/gr-qc/9712019
- **Type:** graduate lecture notes / textbook-style review
- **Quality:** high for GR fundamentals and the weak-field/Newtonian limit; not an artificial-gravity engineering paper.
- **Relevant claims:** The Newtonian gravitational potential appears as the weak-field, slow-motion limit of general relativity, with ordinary mass-energy sourcing the familiar gravitational field. This justifies using `a = GM/r^2` as the first-order screen for nonrelativistic localized mass sources.
- **Useful equations or constraints:** For a compact source, `a = GM/r^2`, `M = ar^2/G`, and the radial tidal-gradient scale outside a spherical/point source is `|da/dr| = 2GM/r^3 = 2a/r`.
- **Impact on hypotheses:** Supports H-002 conceptually but rejects the ordinary-positive-mass subcase as practical engineering once the mass and gradient scales are computed.
- **Follow-up:** Use the weak-field tidal tensor explicitly in the next shaped-source calculation instead of only scalar acceleration.

### NIST/CODATA - Fundamental Physical Constants

- **Link:** https://physics.nist.gov/cuu/Constants/
- **Type:** standards reference
- **Quality:** high for constants.
- **Relevant claims:** Provides the numerical constants used in E-011: `G = 6.67430e-11 m^3 kg^-1 s^-2` and `c = 299792458 m/s`.
- **Useful equations or constraints:** Pair with `M = ar^2/G` and `E = Mc^2` for rest-energy equivalents.
- **Impact on hypotheses:** Provides the numerical basis for B-010/H-009 scale estimates.
- **Follow-up:** None; use as the standing constants reference for future scale checks.

### Ozel and Freire - Masses, Radii, and the Equation of State of Neutron Stars

- **Link:** https://arxiv.org/abs/1603.02698
- **Type:** peer-reviewed review paper / arXiv preprint
- **Quality:** high for compact-object mass/radius context; not an engineering source.
- **Relevant claims:** Neutron stars have solar-order masses compressed to radii of order `10 km`, which puts their mean densities near nuclear-density regimes. This provides context for how far ordinary spacecraft materials are from densities that could make compact positive-mass gravity sources.
- **Useful equations or constraints:** Mean density estimate `rho ~= 3M/(4 pi R^3)` for compact-object comparison; this is context only, not an engineering target.
- **Impact on hypotheses:** Reinforces H-009 rejection: compact positive-mass sources require density regimes associated with astrophysical objects, not controllable materials.
- **Follow-up:** If compact exotic objects ever enter the queue, separate "field source exists in astrophysics" from "safe, stable, containable engineered device."

### Gauss's Law For Gravity / Bouguer Plate Limit

- **Link:** https://en.wikipedia.org/wiki/Gauss%27s_law_for_gravity
- **Type:** mathematical physics reference / secondary source
- **Quality:** medium as a quick formula reference; the equations are standard Newtonian gravity and should be backed by a textbook in any publication-grade writeup.
- **Relevant claims:** Newtonian gravity obeys `nabla dot g = -4 pi G rho`. For an infinite flat plate of finite thickness, the field outside is perpendicular to the plate and has magnitude `2 pi G Sigma`, independent of distance.
- **Useful equations or constraints:** To create `1g` with the ideal infinite-sheet limit requires `Sigma = g/(2 pi G) ~= 2.34e10 kg/m^2`. For `0.01g`, the same limit still needs `~2.34e8 kg/m^2`.
- **Impact on hypotheses:** Supports B-011: the route to smooth positive-mass gravity is large extended mass, not compact localized engineering.
- **Follow-up:** Replace or supplement with a standard geophysics or classical mechanics text if this result becomes central.

### Tidal Tensor / Vacuum Hessian Constraint

- **Link:** https://en.wikipedia.org/wiki/Tidal_tensor
- **Type:** mathematical physics reference / secondary source
- **Quality:** medium as a quick orientation; use Carroll or a GR/Newtonian gravity text for formal citation.
- **Relevant claims:** In Newtonian gravity, differential acceleration is described by the Hessian of the potential. In vacuum the potential satisfies Laplace's equation, so the trace of the Hessian is zero.
- **Useful equations or constraints:** Outside a spherical source, the tidal tensor has the familiar radial/tangential structure proportional to `GM/r^3`; for source-free regions, derivative cancellation in one direction must be balanced by structure in other directions or higher derivatives.
- **Impact on hypotheses:** Clarifies why shaped-source cancellation can improve a point but not create arbitrary finite-volume uniform gravity without paying in source size or multipoles.
- **Follow-up:** Use this as the mathematical frame for E-013's constrained positive-mass optimization.

### Ring And Disk Axis Fields

- **Link:** https://en.wikipedia.org/wiki/Shell_theorem
- **Type:** mathematical derivation / secondary source
- **Quality:** medium; formulas are standard Newtonian integrals and are sufficient for first-pass screening.
- **Relevant claims:** The axial field of a ring follows from integrating point-mass contributions; disks can be built from rings.
- **Useful equations or constraints:** Ring on-axis acceleration: `g_z = GMz/(z^2+R^2)^(3/2)`. Its axial derivative vanishes at `R = sqrt(2) z`, a useful shaped-source example that cancels first-order axial tide at one point while leaving large higher-order variation. Uniform disk on-axis acceleration: `g_z = 2 pi G Sigma (1 - z/sqrt(z^2+R^2))`.
- **Impact on hypotheses:** Supports H-010/B-011: finite positive-mass geometries can reshape local derivatives but become massive and spatially large when forced to produce smooth useful acceleration.
- **Follow-up:** In E-013, compute full 3D field variation, not only the symmetry axis.

### Yurtsever, Marzban, and Meila - On the Gravitational Inverse Problem

- **Link:** https://arxiv.org/abs/1004.4939
- **Type:** arXiv preprint / mathematical physics and inverse-problem paper
- **Quality:** medium-high for inverse-problem framing; not an artificial-gravity engineering paper.
- **Relevant claims:** The forward map from mass density to gravitational potential or gravity-gradient data is straightforward, but the inverse problem is nonunique and constraint-dependent. This is useful context for E-013 because a source layout that fits a desired local field is not unique; the engineering question is the constrained positive-density, bounded-support, minimum-mass version.
- **Useful equations or constraints:** Treat the mass-to-field map as linear in source density for fixed source locations. Non-uniqueness means a numerical layout search needs explicit constraints: positive density, keep-out distance, target acceleration, allowed field variation, and mass objective.
- **Impact on hypotheses:** Supports H-011's framing: optimization may choose among many layouts, but non-uniqueness by itself does not bypass stress-energy magnitude.
- **Follow-up:** If E-013 is upgraded to a rigorous solver, formulate it as a nonnegative linear program over candidate mass cells and sample constraints on `g_x`, `g_y`, `g_z`, and field magnitude across the cabin volume.

### E-013 Finite-Disk Cabin Calculation

- **Link:** Internal calculation, 2026-07-02.
- **Type:** calculation / first-pass constrained optimization
- **Quality:** medium as an engineering screen; finite disk and point mass are comparison families, not a proof of global optimality.
- **Relevant claims:** For a `2 m` cabin, a finite disk in a plane `2 m` behind cabin center with `R ~= 11.5 m` gives about `+/-10%` full-cube field-magnitude variation and needs `~1.2e13 kg` for `1g`; the `0.01g` case scales linearly to `~1.2e11 kg`. Tightening to about `+/-5%` requires `R ~= 21.7 m` and `~3.8e13 kg` for `1g`.
- **Useful equations or constraints:** Disk axis field `g_z = 2 pi G Sigma (1 - d/sqrt(d^2 + R^2))`; first-order axial fractional slope `k = R^2 / ((d^2 + R^2)^(3/2) (1 - d/sqrt(d^2 + R^2)))`; distant point-source smoothing estimate `2h/d <= epsilon`.
- **Impact on hypotheses:** Adds B-012 and H-011; completes E-013; reinforces that positive-mass geometry is a boundary, not a practical route.
- **Follow-up:** Move to E-014 and compare high-energy-density radiation/plasma source terms against B-008, B-010, B-011, and B-012.

### National Academies - Fundamental Research in High Energy Density Science

- **Link:** https://nap.nationalacademies.org/catalog/26728/fundamental-research-in-high-energy-density-science
- **Type:** consensus study / technical report
- **Quality:** high for defining HED science priorities and laboratory regimes; not an artificial-gravity source.
- **Relevant claims:** High-energy-density science covers matter and radiation at extreme pressures and energy densities relevant to fusion, planetary interiors, stellar interiors, and weapons stewardship.
- **Useful equations or constraints:** Use the conventional HED scale `u ~ 1e11 J/m^3` as a laboratory-extreme benchmark. Gravitationally, this is only `rho = u/c^2 ~= 1.1e-6 kg/m^3`, and a `1 m` sphere at this density sources only `~3e-16 m/s^2` at its surface.
- **Impact on hypotheses:** Supports B-013: HED is extreme for plasma/material physics but still gravitationally tiny compared with the `~3e27 J/m^3` meter-scale `1g` benchmark.
- **Follow-up:** If any HED source is revisited, require both peak energy density and integrated energy over duration and volume.

### Wurzel & Hsu - Progress toward fusion energy breakeven and gain as measured against the Lawson criterion

- **Link:** https://arxiv.org/abs/2105.10954
- **Type:** peer-reviewed review / data compilation
- **Quality:** high for fusion comparison metrics and Lawson-criterion framing.
- **Relevant claims:** Fusion progress is usefully measured by density, confinement time, temperature, and gain, but those metrics address fusion energy viability rather than gravitational source strength.
- **Useful equations or constraints:** For artificial-gravity screening, translate any fusion energy or plasma stored energy through `m = E/c^2`; a megajoule-scale event has mass equivalent near `1e-11 kg`.
- **Impact on hypotheses:** Helps keep ICF and plasma performance claims in the right category: compelling fusion physics, not a gravitational-field shortcut.
- **Follow-up:** Use this source if a future run compares magnetic confinement and ICF energy content, but keep it separate from artificial-gravity viability.

### DOE - NIF fusion ignition announcement and reporting

- **Link:** https://www.energy.gov/articles/doe-national-laboratory-makes-history-achieving-fusion-ignition
- **Type:** official laboratory / DOE report
- **Quality:** high for reported shot energies; pair with peer-reviewed follow-up for detailed plasma parameters.
- **Relevant claims:** The December 5, 2022 NIF shot delivered about `2.05 MJ` to the target and produced about `3.15 MJ` of fusion output, reaching scientific ignition by the target-energy accounting.
- **Useful equations or constraints:** `3 MJ/c^2 ~= 3.3e-11 kg`; at `1 m` this corresponds to gravitational acceleration `~2.2e-21 m/s^2`. Even compressed into a `50 um`-scale region, the total energy is too small and too brief for useful artificial gravity.
- **Impact on hypotheses:** Reinforces H-012/B-013: ICF creates extraordinary transient HED states, but not a useful quasi-static source of gravity.
- **Follow-up:** Add peer-reviewed NIF ignition papers if E-015 needs detailed hotspot radius, burn duration, or pressure numbers.

### Sadler, Walsh, Zhou, and Li - Role of self-generated magnetic fields in the inertial fusion ignition threshold

- **Link:** https://arxiv.org/abs/2203.08258
- **Type:** peer-reviewed plasma-physics paper / arXiv preprint
- **Quality:** high for ICF magnetic-field modeling; indirect for artificial gravity.
- **Relevant claims:** Simulations predict self-generated magnetic fields exceeding `5 kT` in current NIF experiments; such fields can reduce electron heat loss and affect fusion yield.
- **Useful equations or constraints:** A `5 kT` magnetic field has `u_B = B^2/(2 mu0) ~= 1e13 J/m^3`, which is huge by laboratory standards but still about `14.5` orders below the `1 m` `1g` average energy-density benchmark.
- **Impact on hypotheses:** Strengthens the boundary against "plasma magnetic fields rescue EM gravity"; they matter for transport and ignition thresholds, not direct artificial gravity.
- **Follow-up:** If magnetized ICF is revisited, separate plasma confinement benefits from gravitational source claims.

### Ursescu - Ultra-intense laser pulses and the ELI-NP High Power Laser System

- **Link:** https://arxiv.org/abs/2105.05494
- **Type:** facility / high-intensity laser overview
- **Quality:** medium-high for ELI-NP capability orientation; use facility papers for exact delivered parameters.
- **Relevant claims:** ELI-NP's dual `10 PW` laser arms target extreme-field experiments with femtosecond pulses and micron-scale focusing.
- **Useful equations or constraints:** For an extreme intensity `I = 1e23 W/cm^2`, the traveling-wave energy density is `u = I/c ~= 3.3e18 J/m^3`, still about `9` orders below the `1 m` `1g` average; actual pulse volumes and durations make integrated gravitational effects much smaller.
- **Impact on hypotheses:** Supports H-012 rejection for ultra-intense laser pulses as direct gravity sources, while preserving them as possible tools for nonclassical radiation or strong-field QED experiments.
- **Follow-up:** Future work should ask whether squeezed or structured light changes stress correlations, not whether classical pulse intensity alone is enough.

### Ehlers, Ozsvath, Schucking, and Shang - Pressure as a Source of Gravity

- **Link:** https://arxiv.org/abs/gr-qc/0510041
- **Type:** theoretical GR paper / arXiv preprint
- **Quality:** medium-high for conceptual pressure-as-source discussion; use with a GR textbook before making strong claims.
- **Relevant claims:** In GR, pressure and stresses enter gravitational source terms; a naive scalar mass-density estimate can miss order-unity pressure contributions.
- **Useful equations or constraints:** For isotropic radiation, pressure is `p = u/3`, so pressure can change active-source estimates by factors of order unity, not by the many orders of magnitude needed for artificial gravity.
- **Impact on hypotheses:** Adds nuance to B-013: radiation/plasma stress must be tracked, but stress terms do not rescue the scale problem.
- **Follow-up:** If a future metric-source calculation survives the energy-density screen, compute the full stress-energy tensor rather than only `u/c^2`.

### E-014 Radiation and Plasma Source-Term Calculation

- **Link:** Internal calculation, 2026-07-07.
- **Type:** calculation / first-pass source-term screen
- **Quality:** medium as an engineering scale screen; not a full GR solution for radiation cavities or plasma devices.
- **Relevant claims:** HED, ultra-intense laser, ICF, pair-plasma, and antimatter/radiation-storage candidates do not beat the stress-energy scale under known coupling. A `1 m` `1g` source still needs `M ~= 1.47e11 kg` or `E ~= 1.32e28 J`.
- **Useful equations or constraints:** `u_HED ~ 1e11 J/m^3`; `u_laser = I/c`; `m = E/c^2`; `a = GE/(c^2 r^2)` for compact energy at distance `r`; surface field of uniform energy density sphere `a = 4 pi G (u/c^2) R / 3`.
- **Impact on hypotheses:** Adds H-012 and B-013; completes E-014; narrows H-002 by removing classical HED radiation/plasma as a scale escape.
- **Follow-up:** Move to E-015: nonclassical radiation stress-energy and precision-source experiments.

### Ford and Roman - Negative Energy in Superposition and Entangled States

- **Link:** https://arxiv.org/abs/0705.3003
- **Type:** peer-reviewed theoretical paper / arXiv preprint
- **Quality:** high for explicit QFT stress-energy examples; scalar-field model with quantum-optics analogies, not an engineering proposal.
- **Relevant claims:** Quantum field theory allows negative energy densities in states such as Casimir, squeezed, superposed, and entangled states, but known QI behavior restricts arbitrary separation of negative and positive energy. The paper calculates negative energy for states that have been or could be generated in quantum optics experiments.
- **Useful equations or constraints:** For a one-mode traveling wave, `rho = (hbar omega / V) [n + R cos(...)]`, so `rho_min = -(hbar omega / V)(R - n)` and negative energy requires `R > n`. For a single-mode squeezed vacuum, `n = sinh^2 r` and `R = sinh r cosh r`, so `R - n` tends to `1/2` at large `r`; increasing squeezing raises the mean positive photon number much faster than it raises the negative trough.
- **Impact on hypotheses:** Supports H-003 as a real theoretical crack in pointwise energy conditions, but adds H-013/B-014 rejecting squeezed radiation as a practical localized artificial-gravity source.
- **Follow-up:** If E-016 proceeds, use this one-mode expression only as a scale model; a real optical source needs bandwidth, beam geometry, losses, apparatus energy, and detector sampling.

### Wilson et al. - Observation of the Dynamical Casimir Effect in a Superconducting Circuit

- **Link:** https://arxiv.org/abs/1105.4714
- **Type:** peer-reviewed experimental paper / arXiv preprint
- **Quality:** high for dynamic-Casimir experimental status; indirect for gravitational sourcing.
- **Relevant claims:** A superconducting circuit with a SQUID-modulated boundary produced microwave photons attributed to the dynamical Casimir effect and observed two-mode squeezing, indicating the quantum character of the generated radiation.
- **Useful equations or constraints:** The experiment's modulation scale is around `11 GHz`; an `11 GHz` photon has energy `h nu ~= 7.3e-24 J`. Even unrealistically concentrating half a photon in `1e-12 m^3` is only `~4e-12 J/m^3`, before including the positive energy in the pump, circuit, and emitted photons.
- **Impact on hypotheses:** Strengthens the statement that nonclassical radiation phenomena are real laboratory physics, but supports B-014: they are precision-QFT effects, not large stress-energy sources for artificial gravity.
- **Follow-up:** Use DCE as a candidate modulated source in E-016 only if the calculation tracks pump leakage, electromagnetic shielding, vibration, thermal backgrounds, and the actual generated photon flux.

### Ford and Roman - Negative Energy Seen By Accelerated Observers

- **Link:** https://arxiv.org/abs/1302.2859
- **Type:** peer-reviewed theoretical paper / arXiv preprint
- **Quality:** high for observer-dependence nuance around negative energy; not a macroscopic-engineering loophole.
- **Relevant claims:** Accelerated observers moving through a single-mode squeezed electromagnetic vacuum can sample integrated negative energy in ways much weaker than inertial-worldline QI restrictions. The authors explicitly state this does not invalidate inertial-observer QIs or change constraints on macroscopic negative-energy applications such as traversable wormholes.
- **Useful equations or constraints:** Treat observer trajectory, sampling function, and detector motion as part of the stress-energy claim. Negative energy along accelerated worldlines is an operational signature, not a reservoir of negative mass.
- **Impact on hypotheses:** Adds nuance to H-003 and B-009; prevents overclaiming that every QI statement is universal, while preserving H-013/B-014's engineering rejection.
- **Follow-up:** If an experiment relies on accelerated detectors or oscillating mirrors, state whether it measures field stress-energy, detector response, radiation reaction, or a motion-induced sampling effect.

### Fewster and Roman - Null energy conditions in quantum field theory

- **Link:** https://arxiv.org/abs/gr-qc/0209036
- **Type:** peer-reviewed theoretical paper / arXiv preprint
- **Quality:** high for energy-condition nuance in QFT.
- **Relevant claims:** In four-dimensional Minkowski space, weighted null averages of the null-contracted stress tensor can be unbounded below for certain states, yet the averaged null energy condition is still satisfied in the construction, and timelike-worldline averages satisfy QI bounds in globally hyperbolic spacetimes.
- **Useful equations or constraints:** Avoid collapsing "no null QI of this form" into "macroscopic negative energy is free." The result is about the exact averaging path and state class.
- **Impact on hypotheses:** Supports careful wording in B-014: nonclassical states expose real cracks in classical energy-condition language, but not a known artificial-gravity route.
- **Follow-up:** Read QNEC/ANEC literature before returning to warp or wormhole metric source requirements.

### Schnabel - Squeezed states of light and their applications in laser interferometers

- **Link:** https://arxiv.org/abs/1611.03986
- **Type:** peer-reviewed review / arXiv preprint
- **Quality:** high for squeezed-light production and precision-measurement applications.
- **Relevant claims:** Squeezed light is a mature nonclassical resource for reducing quantum noise and improving interferometer sensitivity, including gravitational-wave detectors. Its value is measurement sensitivity, not added optical power or a large gravitational source term.
- **Useful equations or constraints:** Squeezing in dB maps to the squeeze parameter through variance reduction `e^(-2r)`. A `15 dB` squeezed vacuum has `r ~= 1.73`, mean photon number `sinh^2 r ~= 7.4`, and single-mode negative-trough coefficient `R - n ~= 0.48` in the Ford-Roman scale model.
- **Impact on hypotheses:** Supports E-015's distinction between "excellent precision metrology resource" and "gravitational source."
- **Follow-up:** For E-016, squeezed light may improve the detector or provide a modulated source, but those roles must not be confused.

### Maclay and Davis - Testing a Quantum Inequality with a Meta-analysis of Data from Squeezed Light

- **Link:** https://arxiv.org/abs/1806.01269
- **Type:** peer-reviewed analysis / arXiv preprint
- **Quality:** medium / uncertain for this workspace; useful as a provocative source-quality check, not as a settled refutation of QIs.
- **Relevant claims:** The authors compare a proposed squeezed-light QI with published homodyne squeezing data and report apparent violations for physically reasonable sampling functions.
- **Useful equations or constraints:** The paper is a reminder that experimental definitions of measured quadrature variance, normal ordering, sampling, detector bandwidth, and stress-energy expectation must be matched carefully before declaring a QI test.
- **Impact on hypotheses:** Does not rescue artificial-gravity claims. It raises a possible precision-test question for E-016: what observable would actually test semiclassical stress-energy constraints, rather than merely reanalyzing optical noise data?
- **Follow-up:** Treat as a motivation to design a cleaner null experiment; pair with Fewster/Ford/Roman theory before assigning high confidence.

### E-015 Nonclassical Radiation Stress-Energy Calculation

- **Link:** Internal calculation, 2026-07-08.
- **Type:** literature review + calculation / first-pass source-term screen
- **Quality:** medium as a scale boundary; not a full semiclassical gravity calculation for a real optical source.
- **Relevant claims:** Squeezed-light, superposition, and dynamic-Casimir states can produce negative or subvacuum stress-energy features relative to the vacuum, but not macroscopic separable negative energy. A `15 dB` single-mode squeezed vacuum gives `R - n ~= 0.48`; with an optimistic optical `1064 nm` cubic-wavelength mode volume, the negative trough scale is only `~0.08 J/m^3`, about `4e28` below the `1 m` `1g` benchmark.
- **Useful equations or constraints:** `r = dB/(20 log10 e)` for variance squeezing; `n = sinh^2 r`; `R - n = sinh r cosh r - sinh^2 r`; optimistic cubic-wavelength trough `u_neg ~ 0.5 h c / lambda^4`; matching `u ~= 3.2e27 J/m^3` by that toy estimate requires `lambda ~= 7.5e-14 m`.
- **Impact on hypotheses:** Adds H-013 and B-014; completes E-015; keeps nonclassical radiation as a precision-test candidate rather than a practical artificial-gravity mechanism.
- **Follow-up:** Run E-016: design a modulated nonclassical EM stress-energy null test with honest signal/background estimates.

### Panda et al. - Measuring gravity by holding atoms

- **Link:** https://arxiv.org/abs/2310.01344
- **Type:** peer-reviewed experimental paper / arXiv preprint
- **Quality:** high as a near-term precision-gravity detector benchmark; not a nonclassical-light source paper.
- **Relevant claims:** Atom interferometry with atoms held in an optical lattice measured the attraction of a miniature source mass and reported combined accuracy of `6.2 nm/s^2`, improving on similar free-fall measurements with stationary source masses.
- **Useful equations or constraints:** Use `~1e-9 to 1e-8 m/s^2` as an optimistic first benchmark for E-016 source-signal comparison, before considering integration time, modulation, source distance, and systematic backgrounds.
- **Impact on hypotheses:** Supports E-016 by anchoring "precision-source experiment" to actual gravitational detector scales. It also shows why nonclassical EM stress-energy is likely far below direct detection unless the source energy is many orders larger or the observable is not a simple Newtonian acceleration.
- **Follow-up:** Compare with torsion-balance and optomechanical force sensitivities before selecting the E-016 detector class.

### Ratzel, Wilkens, and Menzel - Gravitational properties of light

- **Link:** https://arxiv.org/abs/1511.01023
- **Type:** peer-reviewed theoretical paper / arXiv preprint
- **Quality:** high for linearized-gravity treatment of finite laser pulses; not a detector proposal for artificial gravity.
- **Relevant claims:** Studies the gravitational field of finite-lifetime laser pulses in linearized gravity and finds very small effects. The physical effects are tied to the emission and absorption history of the pulse, with source behavior propagating in shells at light speed.
- **Useful equations or constraints:** Treat laser or nonclassical-light sources as complete stress-energy histories, not stationary point masses unless that is an explicitly conservative bound. For first-pass magnitude, a compact energy modulation still obeys `a ~= G deltaE/(c^2 r^2)`.
- **Impact on hypotheses:** Supports B-015 by preventing the source model from hiding emission/absorption, momentum flow, or radiation-pressure bookkeeping behind a single "stored optical energy" number.
- **Follow-up:** If optical-source gravity is revisited, compare the compact-energy bound with the light-pulse linearized solution and include absorber/source recoil.

### Kuo and Ford - Semiclassical Gravity Theory and Quantum Fluctuations

- **Link:** https://arxiv.org/abs/gr-qc/9304008
- **Type:** peer-reviewed theoretical paper / arXiv preprint
- **Quality:** high for conceptual limits of semiclassical gravity in states with large stress-tensor fluctuations; older but directly relevant.
- **Relevant claims:** Semiclassical gravity with a classical metric sourced by `<T_ab>` is a good approximation only when stress-tensor fluctuations are small. The paper finds large energy-density fluctuations in cases with negative local energy density, including squeezed and Casimir-like states.
- **Useful equations or constraints:** Any proposed nonclassical-source gravity experiment must track not only `<T_ab>` but also stress-tensor variance/noise and the operational detector response. Negative expectation value does not automatically imply a smooth classical negative gravitational field.
- **Impact on hypotheses:** Narrows H-003, H-013, and H-014: nonclassical stress-energy remains theory-relevant, but a direct precision-source experiment must state which semiclassical assumption is being tested.
- **Follow-up:** E-017 should include a bookkeeping column for stress-tensor variance and whether the predicted observable is a mean field, stochastic metric fluctuation, or detector-noise correlation.

### Ranjit et al. - Zeptonewton force sensing with nanospheres in an optical lattice

- **Link:** https://arxiv.org/abs/1603.02122
- **Type:** peer-reviewed experimental paper / arXiv preprint
- **Quality:** high as an optomechanical force-sensor benchmark; indirect for gravitational source detection.
- **Relevant claims:** Demonstrates long measurement times and zeptonewton-scale force sensitivity with optically trapped silica nanospheres.
- **Useful equations or constraints:** Force sensitivity alone can mislead for gravity-source estimates because the test mass is tiny. A `~300 nm` silica sphere near a `1 J` equivalent source-energy modulation at `1 mm` feels only `~1.8e-37 N`, about `15-16` orders below a zeptonewton.
- **Impact on hypotheses:** Supports B-015: optomechanical sensors are excellent force probes, but current source-energy limits make nonclassical EM gravitational signals invisible by direct Newtonian force.
- **Follow-up:** Use optomechanics for systematics and force-calibration thinking, not as the default detector for EM stress-energy gravity until source energy or coupling assumptions change.

### Lee et al. - New test of the gravitational inverse-square law at separations down to 52 um

- **Link:** https://arxiv.org/abs/2002.11761
- **Type:** peer-reviewed experimental paper / arXiv preprint
- **Quality:** high as a short-range torsion-balance gravity benchmark; not a nonclassical-source test.
- **Relevant claims:** Uses a stationary torsion balance and rotating attractor to test Newtonian gravity at detector-attractor separations from `52 um` to `3.0 mm`, finding agreement with Newtonian gravity and constraining gravitational-strength Yukawa interactions below `38.6 um`.
- **Useful equations or constraints:** Rotating attractors, symmetry, and lock-in detection are the right experimental language for tiny gravity signals. However, those methods rely on macroscopic source masses, not joule-scale EM stress-energy.
- **Impact on hypotheses:** Supports H-005 and B-015 by suggesting the correct null-test architecture while reinforcing that modulated EM source energy is the bottleneck.
- **Follow-up:** E-017 should borrow the modulation/control discipline of torsion-balance experiments, but not assume their sensitivity transfers to microscopic stress-energy sources.

### E-016 Modulated Nonclassical EM Null-Test Screen

- **Link:** Internal calculation, 2026-07-09.
- **Type:** experimental design + calculation / detector-scale screen
- **Quality:** medium as a bounding model; not a full optical-cavity or superconducting-circuit design.
- **Relevant claims:** Direct gravitational detection of modulated nonclassical EM stress-energy is not credible at current source energies. Even `1 MJ` modulated as an ideal compact source at `1 mm` gives only `~7.4e-16 m/s^2`; matching a `6.2 nm/s^2` atom-interferometer benchmark would require `~8.3e12 J` at `1 mm`.
- **Useful equations or constraints:** Compact-energy acceleration bound `a ~= G deltaE/(c^2 r^2)`; detector-threshold energy `deltaE ~= a c^2 r^2/G`; gravitational force on test mass `F ~= G deltaE m/(c^2 r^2)`.
- **Impact on hypotheses:** Adds H-014 and B-015; completes E-016; narrows nonclassical EM work to source bookkeeping, controls, and semiclassical-assumption tests rather than near-term gravity-source detection.
- **Follow-up:** Run E-017: build a source-accounting template for squeezed-light/DCE stress-energy, including mean, variance, apparatus compensation, and control states.

### Schönbeck, Thies, and Schnabel - 13 dB squeezed vacuum states at 1550 nm from 12 mW pump power

- **Link:** https://doi.org/10.1364/OL.43.000110
- **Type:** peer-reviewed optical experiment
- **Quality:** high for a concrete, efficient squeezed-vacuum source; it does not report a gravitational observable.
- **Relevant claims:** A doubly resonant PPKTP cavity produced `13 dB` squeezing at `1550 nm` from `12 mW` external pump power at `775 nm`.
- **Useful equations or constraints:** Interpreting `13 dB` ideally as `exp(-2r) = 10^-1.3` gives `r ~= 1.50`, `n = sinh^2 r ~= 4.5`, and mean excitation `n h c/lambda ~= 5.8e-19 J` per mode. The one-mode negative trough is bounded near half a photon, `~6.4e-20 J` at `1550 nm`. An illustrative `100 MHz` independent-mode rate would carry only `~5.8e-11 W`, about `4.8e-9` of the reported pump power.
- **Impact on hypotheses:** Supports B-016. The quantum state is experimentally meaningful, but pump, cavity, crystal, locking, loss, and heat terms dominate any total energy modulation and must be measured independently.
- **Follow-up:** Do not use the illustrative mode rate as a device claim; E-018 needs the measured bandwidth, mode functions, losses, and sampling function of a selected apparatus.

### Johansson et al. - The dynamical Casimir effect in superconducting microwave circuits

- **Link:** https://arxiv.org/abs/1007.1058
- **Type:** peer-reviewed theoretical circuit-QED paper / arXiv preprint
- **Quality:** high for the input-output and boundary-modulation model underlying superconducting DCE experiments.
- **Relevant claims:** DCE radiation is produced by rapidly modulating a SQUID boundary in an open waveguide or resonator; predicted observables include photon-flux density, output correlations, and quadrature squeezing. The resonator case is closely related to parametric downconversion.
- **Useful equations or constraints:** The source is an externally driven time-dependent boundary. A closed ledger must include the flux-pump line, SQUID/Josephson energy, emitted microwave photons, reflections, dissipation, and correlated output modes; the photons are not energy extracted without a pump.
- **Impact on hypotheses:** Reinforces B-016 and prevents treating the DCE label as a separable negative-energy reservoir.
- **Follow-up:** A real DCE ledger should use calibrated pump power at the chip, emitted spectral photon flux, line attenuation, device heating, and mechanical/electromagnetic reaction channels.

### Hu and Verdaguer - Stochastic Gravity: Theory and Applications

- **Link:** https://arxiv.org/abs/0802.0658
- **Type:** peer-reviewed review / arXiv preprint
- **Quality:** high for the distinction between semiclassical mean-field gravity and stress-tensor-fluctuation sourcing.
- **Relevant claims:** Semiclassical gravity uses `<T_ab>` in the semiclassical Einstein equation; stochastic gravity adds stress-tensor fluctuations through the noise kernel and Einstein-Langevin equation.
- **Useful equations or constraints:** An equal-mean coherent/squeezed comparison has no leading deterministic mean-field contrast merely because its variances differ. The candidate contrast is a connected, spatially and temporally smeared stress-tensor two-point function propagated into a probe correlation.
- **Impact on hypotheses:** Adds H-015. This keeps the fluctuation crack open but sharply defines what E-018 must calculate.
- **Follow-up:** Select a sampling function and probe response before discussing sensitivity; pointwise variance ratios alone are not an operational observable.

### E-017 Closed Stress-Energy Ledger And Control Matrix

- **Link:** Internal synthesis, 2026-07-10.
- **Type:** source accounting + falsification design
- **Quality:** medium as a general protocol; numerical examples are bounding comparisons, not a reconstructed apparatus dataset.
- **Relevant claims:** Every candidate source requires four coupled ledgers: `(1)` mean field stress-energy, `(2)` subvacuum/renormalized contribution, `(3)` connected stress-tensor correlations, and `(4)` classical apparatus energy-momentum and dissipation. A claim is not interpretable if any ledger is omitted.
- **Useful control matrix:** source-off; pump-on detuned/no squeezing; coherent or thermal state with matched mean energy and spectrum; phase reversal at fixed mean; dummy heat; dummy EM drive; distance/orientation scaling; blinded injections. Record total energy, momentum, temperature, displacement, magnetic/electric leakage, and phase for each state.
- **Impact on hypotheses:** Completes E-017, adds B-016 and H-015, and changes the next target from direct force detection to a smeared correlation calculation.
- **Follow-up:** Run E-018 on one idealized source/probe geometry.

### Hu and Verdaguer - Stochastic Gravity: A Primer with Applications

- **Link:** https://arxiv.org/abs/gr-qc/0211090
- **Type:** peer-reviewed theoretical review / arXiv preprint
- **Quality:** high for the Einstein-Langevin framework and definition of the stress-tensor noise kernel; not a laboratory source calculation.
- **Relevant claims:** Semiclassical gravity uses the expectation value of stress-energy, while stochastic gravity adds fluctuations through the connected stress-energy bi-tensor and an Einstein-Langevin equation. Metric two-point functions, rather than an added deterministic force, are the relevant output.
- **Useful equations or constraints:** For a smeared source observable `E_f(t)=int d^3x f(x) T_00(x,t)`, use the symmetrized connected correlator `N_E(t,t')=(1/2)<{delta E_f(t),delta E_f(t')}>`; propagate it through the retarded gravitational response before comparing with a probe spectrum.
- **Impact on hypotheses:** Supplies the formal channel retained in H-015 but does not imply experimental observability or useful artificial gravity.
- **Follow-up:** E-019 must use the total conserved apparatus stress tensor, not the field term alone.

### Clark et al. - Observation of Strong Radiation Pressure Forces from Squeezed Light

- **Link:** https://arxiv.org/abs/1601.02689
- **Type:** peer-reviewed experimental paper / arXiv preprint
- **Quality:** high for the operational back-action of squeezed microwave fields on a mechanical oscillator.
- **Relevant claims:** Squeezed-field amplitude fluctuations drive measurable nonclassical radiation-pressure noise; changing squeezing magnitude and phase changes the trade between imprecision and mechanical back-action.
- **Useful equations or constraints:** A mechanical probe coupled to the source field already measures its stress fluctuations electromagnetically. That response is not evidence of gravity and is the primary confounder for any source-probe correlation proposal.
- **Impact on hypotheses:** Strongly narrows H-015: the same state-dependent correlations proposed as a stochastic-gravity tag have an established, much larger ordinary optomechanical channel.
- **Follow-up:** Require shielding and geometry controls that remove direct field coupling without assuming away wall recoil or leakage.

### Yap et al. - Broadband Reduction of Quantum Radiation Pressure Noise via Squeezed Light Injection

- **Link:** https://arxiv.org/abs/1812.09804
- **Type:** peer-reviewed experimental paper / arXiv preprint
- **Quality:** high for squeezed-light manipulation of radiation-pressure noise in an optical cavity.
- **Relevant claims:** Amplitude-squeezed injection changed quantum radiation-pressure noise in a microresonator over roughly `10-50 kHz`, demonstrating that the relevant source statistics directly appear as ordinary mechanical back-action.
- **Useful equations or constraints:** State-dependent probe spectra require a full input-output and mechanical transfer model. A spectral difference alone cannot identify a gravitational channel.
- **Impact on hypotheses:** Reinforces B-017 and the need for a conserved apparatus-plus-probe calculation.
- **Follow-up:** Use measured optomechanical transfer functions as the ordinary-background template if an experimental architecture is ever specified.

### E-018 Single-Mode Smeared Noise-Kernel Screen

- **Link:** Internal calculation, 2026-07-11.
- **Type:** theory + calculation / optimistic bounding model
- **Quality:** medium as a transparent low-frequency screen; it is not a full electromagnetic stress-tensor or conserved cavity-wall calculation.
- **Model:** One cavity mode of angular frequency `omega`, linewidth `kappa`, spatially smeared over the full mode volume. A probe lies at `r` much larger than the source size, with `Omega r/c << 1`. Temporal sampling is slow compared with `1/omega`, suppressing phase-sensitive `2 omega` terms. A stationary driven coherent state and squeezed vacuum are matched at mean occupation `N`.
- **Useful equations or constraints:** `delta E = hbar omega delta n`; `Var_coh(n)=N`; `Var_sq(n)=2N(N+1)`. With the explicit exponential correlator assumption `<delta n(t)delta n(0)>=Var(n) exp(-kappa|t|)`, the two-sided spectrum is `S_E(Omega)=2(hbar omega)^2 Var(n) kappa/(kappa^2+Omega^2)`. The optimistic compact-source propagation is `S_a(Omega)=[G/(c^2 r^2)]^2 S_E(Omega)`. An optical-cycle-scale sampler would also retain `2 omega` anomalous terms; they vanish only in the stated slow-sampling limit.
- **Scale result:** For `lambda=1550 nm`, `N=4.5`, `kappa/2pi=100 MHz`, and `r=1 mm`, the zero-frequency acceleration amplitude is `~1.14e-44 m/s^2/sqrt(Hz)` for the coherent state and `~3.78e-44 m/s^2/sqrt(Hz)` for squeezed vacuum. The squeezed/coherent PSD ratio is `2(N+1)=11`, but multiplying an invisible signal by eleven does not make it measurable.
- **Back-action boundary:** For a perfectly reflecting probe sampling a cavity of length `L`, ordinary radiation-pressure force fluctuations scale like `delta F_EM ~ 2 delta E/L`, whereas the gravitational force on probe mass `m` scales like `delta F_g ~ G m delta E/(c^2 r^2)`. Their ratio is `G m L/(2c^2 r^2)`, only `~3.7e-24` even for the deliberately generous `m=1 kg`, `L=1 cm`, `r=1 mm` example. An external shielded probe avoids direct illumination but then cavity-wall recoil, support motion, losses, and total center-of-energy conservation must enter the source kernel.
- **Impact on hypotheses:** Completes E-018, adds B-017, and changes H-015 from unclear to rejected for now as an experimentally isolatable gravitational response. The formal difference between state noise kernels remains real within the idealized model.
- **Follow-up:** Run E-019 on the total conserved cavity-plus-wall stress tensor to determine whether the naive exterior monopole energy-noise spectrum survives redistribution into wall and support stresses.

### E-019 Conserved Tensor And Retarded Tidal Result

- **Link:** Internal model and calculation, 2026-07-11; see `models/e019_conserved_tensor.py`.
- **Type:** divergence-free stress-energy model + retarded linearized-gravity calculation
- **Quality:** medium-high as a verified bounded model; mathematically conserved and grid-converged, but still an effective one-dimensional total-apparatus source rather than a microscopic finite-radius cavity.
- **Layman summary:** Moving light energy around inside a sealed device does not create extra overall gravity. The walls, supports, and energy source react so that the apparent whole-device gravity change cancels. A tiny uneven gravity ripple remains because the energy distribution has shifted, and squeezed light changes the ripple's statistical pattern, but the result is far too small for foreseeable detection or artificial gravity. Driving the system faster merely transfers the burden into increasingly large structural stresses.
- **Conservation result:** The complete effective source uses `T00`, `T0x`, and `Txx` and satisfies `partial_mu T^{mu nu}=0`. The changing gravitational monopole and dipole vanish. A nonzero higher-moment tidal response `R_0x0x` survives and is harmonic-gauge consistent.
- **Useful scale:** For `deltaE=1 J`, `L=1 cm`, `f=100 MHz`, and a probe at `1 m`, the tidal-gradient amplitude is `~2.04e-31 s^-2`. Projecting the E-018 `1550 nm`, `N=4.5`, `kappa/2pi=100 MHz` noise model gives one-sided relative-acceleration ASD `~3.13e-54 m/s^2/sqrt(Hz)` for coherent light and `~1.04e-53 m/s^2/sqrt(Hz)` for squeezed vacuum over a `1 m` baseline. A close exterior probe at `x=6 mm` with a `0.1 mm` baseline still reaches only `~2.57e-46 m/s^2/sqrt(Hz)` for squeezed vacuum.
- **Stress boundary:** The integrated longitudinal stress grows as `(omega L/c)^2`; increasing frequency is therefore not a free gravitational amplifier. The model gives `integral|Txx|/deltaE ~= 2.34e-5` at `100 MHz` and `~0.234` at `10 GHz`.
- **Impact on hypotheses:** Completes E-019 at bounded-model level, reinforces H-015 as rejected for an isolatable experiment, and adds B-018. Conservation preserves a formal stochastic tidal channel but not a useful gravity source.
- **Follow-up:** Reopen only if a concrete mirror/pump/absorber architecture supplies a defensible complete stress-energy ledger capable of changing the conserved tidal transfer by many orders of magnitude.

### Khoury and Weltman - Chameleon Fields: Awaiting Surprises for Tests of Gravity in Space

- **Link:** https://arxiv.org/abs/astro-ph/0309300
- **Type:** primary theoretical paper; Physical Review Letters 93, 171104 (2004)
- **Quality:** high for the canonical effective-potential and thin-shell benchmark; the field is hypothetical and later experiments substantially narrow the model.
- **Relevant claims:** A conformally matter-coupled scalar can acquire a density-dependent effective mass. Dense extended bodies develop a thin shell, whereas sufficiently small bodies in a low-density environment can remain unscreened. Low-density space can therefore differ from a terrestrial chamber.
- **Useful equations:** `V_eff=V+rho exp(beta phi/M_Pl)`; `DeltaR/R=(phi_bg-phi_c)/(6 beta M_Pl Phi)`; the effective exterior scalar charge is approximately `q=min(1,3 DeltaR/R)`.
- **Impact on hypotheses:** Supplies the mechanism tested by E-020 and preserves the open-space caveat. It does not supply an artificial scalar source, a reactionless drive, or experimental evidence for the field.

### Hui, Nicolis, and Stubbs - Equivalence Principle Implications of Modified Gravity Models

- **Link:** https://arxiv.org/abs/0905.2966
- **Type:** primary theoretical paper; Physical Review D 80, 104002 (2009)
- **Quality:** high for the distinction between microscopic universal coupling and macroscopic screened-body response.
- **Relevant claims:** Chameleon screening can produce order-one equivalence-principle differences between extended objects even when the microscopic action couples universally. Scalar charge depends on gravitational potential/compactness, so large and small bodies need not fall alike.
- **Impact on hypotheses:** Directly blocks treating a chameleon fifth force as automatically equivalent to universal cabin gravity.

### Burrage et al. - The Shape Dependence of Chameleon Screening

- **Link:** https://arxiv.org/abs/1711.02065
- **Type:** primary numerical theory paper; JCAP 01 (2018) 056
- **Quality:** high for the studied axisymmetric chamber/source geometries; not a universal optimization theorem.
- **Relevant claims:** Non-spherical sources can be less screened, but the acceleration gain in the studied geometries is only about a factor of three. Chamber boundaries and source shape require nonlinear field solutions.
- **Impact on hypotheses:** Shape optimization cannot close E-020's eleven-to-twelve-order human-scale gap.

### Sabulsky et al. - Experiment to Detect Dark Energy Forces Using Atom Interferometry

- **Link:** https://arxiv.org/abs/1812.08244
- **Type:** primary experiment; Physical Review Letters 123, 061102 (2019)
- **Quality:** high for its apparatus and null result; constraints remain model- and geometry-dependent.
- **Relevant claims:** Rb atoms near a macroscopic source showed no appreciable non-Newtonian attraction. The analysis explicitly includes a body screening factor equivalent to the thin-shell charge used in E-020.
- **Impact on hypotheses:** Anchors the translation from field gradient to an object-dependent acceleration and reinforces the experimental null boundary.

### Yin et al. - Experiments with Levitated Force Sensor Challenge Theories of Dark Energy

- **Link:** https://arxiv.org/abs/2405.09791
- **Type:** primary experiment; Nature Physics 18, 1181-1185 (2022)
- **Quality:** high for the specified thin-film geometry and nonlinear model calculation.
- **Relevant claims:** A levitated sensor found no fifth force and set `F<5.7e-17 N` at 95% confidence. For `n=1`, `Lambda=2.4 meV`, it excludes `1.6e-3 < M/M_Pl < 0.12`, bridging an important atom/torsion gap; the authors report that combined data rule out the basic cosmologically viable chameleon dark-energy model.
- **Impact on hypotheses:** The canonical model used as E-020's favorable benchmark is already experimentally disfavored independently of its cabin-engineering failure.

### Panda et al. - Measuring Gravitational Attraction with a Lattice Atom Interferometer

- **Link:** https://arxiv.org/abs/2310.01344
- **Type:** primary experiment; Nature 631, 515-520 (2024)
- **Quality:** high; source-mass geometry and atomic systematics are measured and modeled.
- **Relevant claims:** The measured source attraction is `33.3 +/- 5.6_stat +/- 2.7_syst nm/s^2`, consistent with the `35.2 +/- 1.0 nm/s^2` Newtonian prediction. The reported anomaly is `-1.9 +/- 6.3 nm/s^2`, giving `|a_anomaly|<13 nm/s^2` at 95% confidence and closing the stated natural parameter space of the basic screened fifth-force model in combination with other experiments.
- **Caution:** This is a geometry-specific atomic bound, not a universal acceleration ceiling for macroscopic screened bodies.
- **Impact on hypotheses:** Reinforces H-016's experimental rejection while illustrating why atoms are useful screening probes.

### Jaffe et al. - 2023 Author Correction to Testing Sub-Gravitational Forces on Atoms

- **Link:** https://www.nature.com/articles/s41567-023-02255-5
- **Type:** primary author correction
- **Quality:** essential source-quality correction.
- **Relevant claims:** The tungsten source's Newtonian attraction was originally high by about a factor of two. The corrected values are `a_grav=33 +/- 3 nm/s^2`, `a_anomaly=41 +/- 24 nm/s^2`, and an attractive one-tailed `a_anomaly<81 nm/s^2` at 95% confidence. The corrected `n=1`, `Lambda=2.4 meV` bound is `M<1.7e-3 M_Pl`.
- **Impact on hypotheses:** Future constraint summaries must not reuse the original uncorrected anomaly or parameter bound.

### Fischer, Kading, and Pitschmann - Screened Scalar Fields in the Laboratory and the Solar System

- **Link:** https://arxiv.org/abs/2405.14638
- **Type:** peer-reviewed review and updated calculation; Universe 10, 297 (2024)
- **Quality:** high for current canonical screened-scalar constraint synthesis; individual model conclusions retain their assumptions.
- **Relevant claims:** Updated neutron screening-charge treatments sharply weaken or erase several historical neutron chameleon exclusions; for `Lambda=2.4 meV` and small positive `n`, qBOUNCE and neutron interferometry do not add useful constraints in the reviewed treatment.
- **Impact on hypotheses:** Prevents overstating obsolete neutron limits while leaving atom, force-sensor, torsion, and Casimir constraints intact.

### Upadhye, Hu, and Khoury - Quantum Stability of Chameleon Field Theories

- **Link:** https://arxiv.org/abs/1204.3906
- **Type:** primary EFT analysis; Physical Review Letters 109, 041301 (2012)
- **Quality:** high within the stated one-loop classical-control criterion.
- **Relevant claims:** For nearly gravitational coupling, keeping quantum corrections small gives `m_phi < 0.0073 (rho/10 g cm^-3)^(1/3) eV`, while fifth-force data already required `m_phi>0.0042 eV` at the time.
- **Impact on hypotheses:** Any active high-field chameleon proposal needs an explicit quantum-valid EFT check; classical profile engineering alone is insufficient.

### Wang, Hui, and Khoury - No-Go Theorems for Generalized Chameleon Field Theories

- **Link:** https://arxiv.org/abs/1208.4612
- **Type:** primary theoretical paper; Physical Review Letters 109, 241301 (2012)
- **Quality:** high under its generalized-chameleon assumptions.
- **Relevant claims:** The scalar's present cosmological Compton wavelength is bounded to roughly Mpc scales, and the conformal factor cannot provide self-acceleration over the last Hubble time. Chameleon-like explanations of cosmic acceleration still require dark energy rather than a free modified-gravity energy reservoir.
- **Impact on hypotheses:** Blocks interpreting the `Lambda` scale as an accessible propulsion or local-field power source.

### Banks et al. - Searching for Screened Scalar Forces with Long-Baseline Atom Interferometers

- **Link:** https://arxiv.org/abs/2511.09750
- **Type:** peer-reviewed experimental proposal; Physical Review D 113, 084047 (2026)
- **Quality:** high for projected sensitivity and the modeled annular planar source; it is a proposal, not a detection.
- **Relevant claims:** A `10 m` atom interferometer with a source plate and `Q`-flip protocol could improve chameleon and symmetron bounds by about `1-1.5` orders. The scalar range in the chamber remains tied to the chamber scale, and broader screened-scalar parameter space remains worth testing.
- **Impact on hypotheses:** Complicates blanket rejection of all screened scalars while not reopening the excluded basic chameleon or the human-loading scale.

### Feleppa et al. - Bounds on Screened Dark Energy from Near-Earth Space-Based Measurements

- **Link:** https://arxiv.org/abs/2511.08448
- **Type:** primary theory/data reinterpretation; Physical Review Letters 136, 101002 (2026)
- **Quality:** high for the stated post-Newtonian screened-model mapping; prospective Sagnac sensitivity is not a completed measurement.
- **Relevant claims:** Gravity Probe B and LAGEOS-2 data constrain screened models in low-density near-Earth space. A future clock-based Sagnac test could exclude the chameleon parameter region considered by the authors.
- **Impact on hypotheses:** Preserves low-density space as physically distinct from a screened cabin but shows that it is already a precision-test regime, not an unconstrained engineering loophole.

### E-020 Canonical Chameleon Body-Screening Bound

- **Link:** Internal calculation, 2026-07-12; see `models/e020_chameleon_body_screening.py`.
- **Type:** analytic scaling model + verified numerical calculation
- **Quality:** medium-high as an optimistic necessary-condition screen; not a nonlinear finite-element chamber solution and not a bound on arbitrary active scalar sources.
- **Useful result:** For a `70 kg`, `0.3 m` proxy in a `1 m` passive chamber, the favorable `n=1`, `Lambda=2.4 meV`, `xi=1` model gives `phi_bg=1.599 eV` and a body-acceleration envelope `1.119e-13 m/s^2`, `8.77e11` below `0.01g`. A body-fitting non-overlapping spherical source calculation independently gives `8.74e-14 m/s^2` for `R_source=0.5 m`, `r=0.8 m`; at the joint screening transition that source can remain unscreened only up to `~117 kg`.
- **Formal crack:** An externally maintained unscreened field changes the problem. At `beta=1`, `0.01g` across `1 m` needs an optimistic `844 eV` unscreening floor and `2.657 GeV` excursion. No actuator, experimental allowance, hull solution, backreaction, reaction ledger, or EFT completion follows from those numbers.
- **Impact on hypotheses:** Completes E-020, adds H-016 and B-019, and redirects the active mechanism search to finite planar derivative screening in E-021.

### Hui and Nicolis - An Equivalence Principle for Scalar Forces

- **Link:** https://arxiv.org/abs/1009.2520
- **Type:** primary theoretical paper; Physical Review Letters 105, 231101 (2010)
- **Quality:** high for scalar charge-to-mass reasoning in Galilean-symmetric theories.
- **Relevant claims:** A universal scalar coupling is stable in the matter sector, and Galilean symmetry protects the scalar equivalence principle for ordinary weakly self-gravitating bodies more effectively than chameleon thin-shell screening.
- **Impact on hypotheses:** Motivates E-021 as a mechanism selected to address, rather than repeat, E-020's body-universality failure.

### Brax, Burrage, and Davis - Laboratory Tests of the Galileon

- **Link:** https://arxiv.org/abs/1106.1573
- **Type:** primary theoretical/laboratory-constraint paper; JCAP 09 (2011) 020
- **Quality:** high for the ideal plate/cavity solutions and contemporary constraints; finite cabin geometry needs a new calculation.
- **Relevant claims:** In exact planar symmetry the higher Galileon interactions reduce to total derivatives, so an ideal infinite plate can avoid the usual spherical Vainshtein suppression. The exact limit is fragile; real finite and nonparallel configurations require separate treatment.
- **Preliminary E-021 scale:** In the optimistic free-scalar plane, `a_phi=4 pi G beta^2 Sigma`, so even `0.01g` requires `Sigma ~= 1.17e8/beta^2 kg/m^2` before Earth-background renormalization, finite edges, current bounds, or support mass.
- **Impact on hypotheses:** Defines the next narrow crack to test rather than calling derivative screening a propulsion opportunity.

### Bloomfield, Burrage, and Davis - The Shape Dependence of Vainshtein Screening

- **Link:** https://arxiv.org/abs/1408.4759
- **Type:** primary analytic theory paper; Physical Review D 91, 083510 (2015)
- **Quality:** high for exact planar, cylindrical, and spherical symmetry classes; it is not a controlled approximation for a finite disk.
- **Relevant claims:** In the cubic Galileon, none of the derivative nonlinearities contribute to a static profile depending on only one spatial coordinate. Screening is absent for an exactly infinite plane, weaker for a cylinder, and strongest for a sphere. The unscreened scalar-to-Newtonian force ratio is `2 beta^2` in the paper's canonical normalization.
- **Useful equations:** For a plane with half-thickness `z0` and density `rho0`, `partial_z phi=beta rho0 z0/M_Pl` outside. For a sphere, `r_V=[2 beta M/(pi M_Pl Lambda^3)]^(1/3)` and the deep interior force is suppressed as `(r/r_V)^(3/2)` up to convention-dependent coefficients.
- **Impact on hypotheses:** Establishes that E-021's planar crack is real but symmetry-specific. It does not show that a finite plate approaches the plane smoothly when `r_V/R` is large.

### Ogawa, Hiramatsu, and Kobayashi - Anti-Screening of the Galileon Force Around a Disk Center Hole

- **Link:** https://arxiv.org/abs/1802.04969
- **Type:** primary numerical theory paper; Modern Physics Letters A 34, 1950013 (2019)
- **Quality:** high for the stated axisymmetric cubic PDE and convergence tests; the dimensionless annular sources were chosen for theory exploration, not a laboratory or spacecraft design.
- **Relevant claims:** A finite annular disk is screened in almost every modeled region, confirming that exact planar de-screening does not generally survive finite extent. Near the center hole, however, the nonlinear solution can exceed the corresponding linear force. This local anti-screening is stronger for thinner, less massive disks and smaller holes; the authors report no analytic explanation and describe the astrophysical relevance as unclear.
- **Density caveat:** Their dimensionless density parameter is `mu=beta rho_0/(Lambda^3 M_Pl)`. The fiducial runs use `mu=36.8`, with comparison runs at `369` and `3690`; enhancement becomes hard to see above roughly `mu=10^3` in this geometry. For `Lambda^3~=M_Pl H_0^2`, these are only `~10^1-10^3` times the cosmic mean-density scale, not material-source densities. The thin-wedge nonlinearity coordinate is approximately `chi=c3 mu theta_0`; the fiducial and high-density cases at `theta_0=0.05` are `chi~=1.84` and `184.5`.
- **Absolute-field caveat:** The published plots show approximate peak ratios `R~4-5` for favorable dilute/thin/small-hole cases and only `~1.3` for `mu=3690`. The exact hole center has zero vector field by reflection and axial symmetry, so `R>1` identifies an off-center ridge and does not itself establish useful absolute acceleration or a low-gradient target volume.
- **Numerical-method anchor:** The paper treats the nonlinear invariant as an iterated source, starts from the linear solution, and under-relaxes with `omega=O(0.01)` until `||phi_new-phi_old||/||phi_new||<1e-8`. Its fiducial grid is `200 x 100` with outer boundary `r_max/r_0=80`; box/grid checks preserve `R>1`, although the detailed peak is resolution-sensitive. E-023 reproduced the resolved effect and showed why residual/source-volume diagnostics must supplement that update stop.
- **Impact on hypotheses:** Prevents B-020 from claiming monotonic suppression or treating the linear disk as a strict upper bound. E-023/E-024 preserve the local dilute effect through source smoothing; E-025 now gates density continuation and any controlled-asymmetry attempt.

### Hiramatsu et al. - Equivalence Principle Violation in Vainshtein-Screened Two-Body Systems

- **Link:** https://arxiv.org/abs/1209.3364
- **Type:** primary numerical theory paper; Physical Review D 87, 063525 (2013)
- **Quality:** high for the studied DGP/cubic-like spherical two-body equation; its empirical mass-ratio fit is not a finite-disk formula.
- **Relevant claims:** When two bodies are separated by less than their individual Vainshtein radii, the smaller body cannot be treated as a passive test mass. Nonlinear interference nearly screens the external-field Laplacian at the small body and reduces the net force by a mass-dependent amount. In their limit, the correction scales approximately as `-0.56 (M_B/M_A)^0.6`; it changes the nominal Earth-Moon Galileon precession by about `4%`.
- **Momentum result:** Solving the joint nonlinear field restores the correct equal-and-opposite total force that naive superposition can violate. This reinforces that an internal Galileon source is not reactionless propulsion.
- **Impact on hypotheses:** Galilean charge universality does not by itself establish meter-scale universal cabin response; a finite source plus target must be solved jointly. Naively inserting the E-021 `70 kg`/`6.07e10 kg` mass ratio into the paper's spherical fit gives only a `~2.4e-6` correction, so this is a conditional validation gate, not evidence for a large occupant-dependent failure in the disk geometry.

### Burrage and Seery - Revisiting Fifth Forces in the Galileon Model

- **Link:** https://arxiv.org/abs/1005.1927
- **Type:** primary EFT/fifth-force theory paper; JCAP 08 (2010) 011
- **Quality:** high for background kinetic redressing in the stated Galileon EFT; ultraviolet conclusions remain completion-dependent.
- **Relevant claims:** Inside a spherical Vainshtein region, the fluctuation kinetic matrix becomes large. Canonical normalization raises the local strong-coupling scale by roughly `sqrt(Z)` in the cubic case. For DGP/cubic parameters at the Earth's surface, the resulting cutoff length is of order `1 cm`, so sub-millimeter patterned edges are not automatically within the minimal EFT's control. In the E-021 normalization, the `H0^-1` benchmark gives a bare length `1.12e6 m` and Earth-dressed length `2.40e-2 m`; the `150 Mpc` benchmark gives `1.37e-2 m`.
- **Impact on hypotheses:** The free `Z=1` meter-scale reference lies below the bare cutoff in length and is not a controlled minimal-EFT cabin prediction. Smooth meter-scale profiles can be discussed conditionally only after specifying a demonstrated dressed background; perforations, thin edges, and attempts to exploit E-023 must report the local cutoff rather than assume the classical PDE remains valid at every geometric feature.

### Andrews, Chu, and Trodden - Galileon Forces in the Solar System

- **Link:** https://arxiv.org/abs/1305.2194
- **Type:** primary analytic theory paper; Physical Review D 88, 084028 (2013)
- **Quality:** high as a caution on perturbative force calculations inside a dominant Vainshtein background.
- **Relevant claims:** For the Sun-Earth-Moon configuration, the nominal nonlinear expansion parameter becomes order unity; diagrams with arbitrarily many Galileon vertices enter at the same order. A finite-order one-Galileon exchange cannot rigorously map lunar ranging directly to `Lambda` without solving the nonlinear three-body problem.
- **Impact on hypotheses:** The often-quoted LLR crossover bound is useful as a published benchmark, not an exact model-independent theorem. E-021 therefore reports both the bound and its nonlinear caveat.

### Bartlett, Desmond, and Ferreira - Constraints on Galileons from Supermassive-Black-Hole Positions

- **Link:** https://arxiv.org/abs/2010.05811
- **Type:** primary observational analysis; Physical Review D 103, 023523 (2021)
- **Quality:** high for the stated galaxy sample, forward model, and assumptions; the large-scale reconstruction and hard screening filter are model-dependent.
- **Relevant claims:** Using 1,916 optical-center/active-nucleus offsets, the analysis finds `Delta G/G_N < 0.16` at `1 sigma` and `<0.36` at `2 sigma` for a representative `r_V=100 Mpc`, with applicability to crossover scales `r_c` of order `H0^-1` and above. The paper summarizes the LLR benchmark as `r_c alpha^(-3/2) >= 150 Mpc` and notes dependence on the Moon's assumed rotation vector.
- **Caution:** `Delta G/G_N`, `alpha`, the microscopic `beta`, and the locally dressed `beta/sqrt(Z)` are not interchangeable without fixing the action and background.
- **E-021 conditional mapping:** With `Delta G/G_N=2 beta^2`, the `1 sigma` limit maps to `beta<0.283`. The corresponding linear `0.01g` disk is `7.59e11 kg`, ordinary gravity is `6.25` times the scalar target, and `epsilon_edge=6.91e33`. This is a normalization-specific benchmark, not a direct bound on every local Galileon action.
- **Impact on hypotheses:** Strong coupling cannot be treated as a freely adjustable spacecraft parameter, but these astrophysical limits do not directly replace the finite nonlinear disk calculation.

### E-021 Finite Planar Cubic-Galileon Screen

- **Link:** Internal model and calculation, 2026-07-13; see `models/e021_galileon_planar_screen.py`.
- **Type:** analytic finite-disk reference + necessary-condition screening diagnostics + constraint synthesis
- **Quality:** medium-high as a verified scale screen; it does not solve the nonlinear finite-disk PDE and is not a force upper bound because local annular anti-screening is known.
- **Useful result:** A disk centered `2 m` behind a `2 m`-deep target volume needs `R=11.723 m` for `+/-10%` axial variation. In the free `beta=1` linear reference, scalar `0.01g` requires `Sigma=1.406e8 kg/m^2`, total mass `6.069e10 kg`, and produces `0.005g` of ordinary Newtonian acceleration. `+/-20%` and `+/-5%` cases require `2.22e10 kg` and `1.93e11 kg`, respectively. Direct `3 x 3 x 3` cube sampling gives magnitude ratios `0.9036-1.1012` and maximum lateral ratio `0.0722`; a radius near `11.85 m` brings all `27` sampled points within `+/-10%`, only a `~2%` mass correction. This is not a continuous-volume extremum proof.
- **Material geometry:** The free `Sigma` equals `6.22 km` of `22590 kg/m^3` osmium-density material, so the `11.7 m` source is not thin. Holding `h/R=0.01` requires `R=622 km` and `1.71e20 kg`; holding `h=0.10 m` requires `rho=1.406e9 kg/m^3`.
- **Edge diagnostic:** `epsilon_edge=c3 beta Sigma/(2 Lambda^3 M_Pl R)=(r_V/R)^3/4`. At `Lambda=1.758e-13 eV`, the reference disk has `epsilon_edge=1.955e33` and `r_V=2.327e12 m`. The `150 Mpc` LLR crossover benchmark still gives `epsilon_edge=2.40e30`.
- **Environment and constraints:** For the `H0^-1`, `beta=1` benchmark, `Z_Earth=2.19e15`. Applying it formally at fixed scalar target would require `1.33e26 kg`, with Newtonian/scalar ratio `1.09e15`; this invalidates the laboratory-perturbation premise and is used only as a reductio. The isolated-Sun check gives `r_V=241 pc`, `Z=3.51e11` at `1 AU`, and `3.51e8` at `100 AU`, so the free case is not recovered merely by leaving Earth. The conservative published dressed plate limit `beta_eff<0.05` gives the less model-specific floor `2.43e13 kg`, with Newtonian/scalar ratio `200`.
- **Astrophysical coupling case:** Conditionally mapping the galaxy-offset `Delta G/G_N<0.16` result gives `beta<0.283`, disk mass `7.59e11 kg`, Newtonian/scalar ratio `6.25`, and edge index `6.91e33`.
- **Total-field comparison:** Holding scalar acceleration alone at `0.01g` tests whether the Galileon channel is useful. If ordinary and scalar fields are instead summed to a total `0.01g`, the disk masses are `1.214e11 kg` for Newtonian gravity alone, `4.046e10 kg` for free `beta=1`, `1.046e11 kg` at the mapped galaxy limit, and `1.208e11 kg` at the dressed plate limit. The constrained cases provide only `13.8%` and `0.50%` mass reductions over ordinary gravity.
- **Annular-density diagnostic:** A uniform disk obeys `epsilon_edge=c3 mu h/(2R)`. If the free target disk is assigned a `0.10 m` thickness, `rho_0=1.406e9 kg/m^3` and `mu=4.58e35`, which reconstructs `epsilon_edge=1.955e33` and lies over `32` orders above the `mu~10^3` turnover reported for the published annular geometry. This is not a universal no-go theorem, but it is a mandatory continuation test before treating anti-screening as an engineering crack.
- **PDE acceptance condition:** Linearizing the static cubic operator about a candidate solution gives `A_ij=delta_ij+2(c3/Lambda^3)[(nabla^2 phi)delta_ij-partial_i partial_j phi]`. A continuation run must monitor its eigenvalues; residual convergence on a branch that loses ellipticity or has unhealthy fluctuation kinetic signs is not a usable solution.
- **Impact on hypotheses:** Completes E-021, adds H-017/B-020, rejects a passive finite solid disk for practical cabin loading, and sends the annular anti-screening caveat to E-023.

### Ogawa - Numerical Study of the Vainshtein Screening Mechanism in the Cubic Galileon Model

- **Link:** https://www.rikkyo.ne.jp/grp/itp/data/theses/2019_Ogawa.pdf
- **Type:** primary-author doctoral thesis (2019); expands the methods and figures behind arXiv:1802.04969.
- **Quality:** high for reconstructing the author's numerical setup, but it still does not publish solver code or raw arrays.
- **Reproduction-critical details:** Documents the radial map `r=chi+alpha chi^3/3` with `alpha=0.2`, cell-centred uniform `chi/theta` grids, and centred finite differences omitted from the paper. It reports less than `1%` force-ratio change between update tolerances `1e-7` and `1e-8` and provides corrected convergence-panel labels.
- **Correction:** The paper's radial-slice caption says `theta=2pi/5`; the thesis uses `theta=pi/10`. Because the coordinate is latitude from the equatorial plane, the thesis value is treated as the likely correction, while E-023 reports both.
- **Remaining ambiguity:** The thesis's printed `Delta chi=chi_max/(Nr-1)` conflicts with its cell-centre indexing; origin, outer ghost, mixed derivative, Heaviside-interface, and linear-solver conventions remain incomplete.
- **Impact on hypotheses:** Makes an independent faithful-grid replication possible but prevents claiming bitwise reproduction or treating detailed first-shell structure as author-validated data.

### White et al. - Robust Numerical Computation of the 3D Cubic-Galileon Field

- **Link:** https://arxiv.org/abs/2003.02648
- **Type:** primary numerical-method paper; Physical Review D 102, 024033 (2020).
- **Quality:** high for residual-driven cubic-Galileon numerics on the attractive normal branch; its solar-system geometries differ from E-023's annulus.
- **Relevant claims:** Uses gradient descent of an integrated nonlinear residual and explicitly selects the normal attractive branch. The method motivates treating a field-update norm as insufficient and recording residual, branch, and force diagnostics separately.
- **Impact on hypotheses:** Supports residual-driven normal-branch validation and E-025's comparison route. It does not validate the present annular solution by citation alone.

### Froese, Oberman, and Salvador - Numerical Methods for the 2-Hessian Equation

- **Link:** https://arxiv.org/abs/1502.04969
- **Type:** primary numerical-analysis paper (2016).
- **Quality:** high for elliptic 2-Hessian methods and admissibility; not written specifically for Galileon physics.
- **Relevant claims:** The fully nonlinear 2-Hessian equation is elliptic only on a restricted admissible class. The authors develop Newton-based monotone and higher-accuracy discretizations and test them on solutions of varied regularity.
- **Wide-stencil construction:** For primitive integer orthogonal frames, centered directional second differences are passed through a coordinatewise nondecreasing extension of `sigma_2` and minimized over the available frames. For ordered curvatures `x<=y<=z`, the extension is `xy+xz+yz` when `x+y>=0` and `-x^2` otherwise. This is why a raw positive `sigma_2` is not an admissibility certificate.
- **Convergence and boundary conditions:** The monotone truncation structure is `O(h^2+dtheta)`, and convergence requires the joint limits `h -> 0`, `dtheta -> 0`, and `h/dtheta -> 0`. Fixed-frame spatial refinement can plateau when angular error dominates. Some paper examples prescribe the exact solution in the strip where a full stencil does not fit; that is valid for manufactured tests but cannot certify an unknown annular solution.
- **E-024 bridge:** Algebraically shifting the dimensionless cubic equation by `u=phi+|x|^2/(8c3)` gives `sigma_2(D^2u)=3/(16c3^2)+S/(2c3)`. Its 2-admissibility pair-sum condition is exactly positivity of the Galileon spatial principal matrix for `c3>0`. This algebraic mapping is an internal derivation, not a claim made in the paper.
- **Impact on hypotheses:** Provides the genuinely independent monotone wide-stencil solver family and branch criterion now assigned to E-025. E-024's exact shift evaluated on the same grid family is an algebra and implementation check, not the final independent-discretization certificate.

### Froese - Meshfree Finite Difference Approximations for Functions of Hessian Eigenvalues

- **Link:** https://arxiv.org/abs/1512.06287
- **Type:** primary numerical-analysis paper (2017).
- **Quality:** high for monotone generalized finite differences on point clouds; convergence still assumes consistency, stability, and a comparison principle for the PDE.
- **Relevant claims:** Positive-weight directional second derivatives can be built on nonuniform point clouds. Consistency requires `h/dtheta -> 0` and `dtheta -> 0`; the paper's optimal basic schedule has search radius `O(sqrt(h))`. Near a general boundary, the boundary sampling must be finer than the interior scale; otherwise an inconsistent boundary layer can remain.
- **Impact on hypotheses:** Supplies an adaptive fallback for E-025 if a uniform cylindrical grid cannot resolve both the annular transition and empty exterior economically. It does not validate the annulus without source-charge, residual, flux, force, boundary, and admissibility convergence.

### Froese Hamfeldt and Lesniewski - Convergent Finite Difference Methods for Fully Nonlinear Elliptic Equations in Three Dimensions

- **Link:** https://arxiv.org/abs/2103.09861
- **Type:** primary numerical-analysis paper (2021).
- **Quality:** high for Cartesian grids augmented by boundary points and monotone least-squares directional differences.
- **Relevant claims:** Their point-cloud hypotheses require boundary resolution `h_B/delta -> 0`, search radius `epsilon -> 0`, and `h/epsilon -> 0`. The implementation uses `delta=h/2`, `h_B=O(h^(5/4))`, and `epsilon=sqrt(h)` as one efficient three-dimensional schedule, plus multilevel orthogonal frames.
- **Impact on hypotheses:** Supports boundary-aware and locally refined alternatives for E-025. The current axisymmetric meridional-plus-azimuthal reduction remains an internal specialization, not a theorem quoted from this paper.

### Finlay and Oberman - Improved Accuracy of Monotone Finite Difference Schemes on Point Clouds and Regular Grids

- **Links:** https://arxiv.org/abs/1807.05150; peer-reviewed version https://doi.org/10.1137/18M1200269
- **Type:** primary numerical-analysis paper (2018).
- **Quality:** high for monotone directional-derivative interpolation; it is not specific to the 2-Hessian or Galileon equation.
- **Relevant claims:** Barycentric interpolation between simplices can preserve monotonicity while improving the angular error from first to second order: `O(R^2+dtheta^2)` on symmetric uniform grids and `O(R+dtheta^2)` on nonsymmetric point clouds. The authors also show that improved formal order need not mean lower absolute error at modest stencil radii.
- **Impact on hypotheses:** Offers a possible way to reduce E-025's directional-cost bottleneck. Composing it with the monotone 2-Hessian extension is an internal proposal and would require new manufactured, boundary, and annulus tests.

### Nicolis, Rattazzi, and Trincherini - The Galileon as a Local Modification of Gravity

- **Link:** https://arxiv.org/abs/0811.2197
- **Type:** foundational primary theoretical paper; Physical Review D 79, 064036 (2009).
- **Quality:** high for the Galileon action, symmetries, classical solutions, and perturbation kinetic structure; it does not validate a particular numerical annulus or establish that nature realizes the model.
- **Relevant claims:** Perturbations propagate in a background-dependent kinetic matrix, so the signs and eigenvalues of the linearized principal operator are physical branch diagnostics rather than optional solver metadata. Stability is more demanding than convergence of a static scalar profile.
- **Impact on hypotheses:** Supports E-023/E-024's spatial-principal and time-kinetic checks and E-025's requirement to remain on the admissible normal branch throughout any independent continuation.

### E-023 Annular Cubic-Galileon Replication

- **Link:** Internal model and calculation, 2026-07-14; see `models/e023_galileon_annulus.py`.
- **Type:** nonlinear PDE replication + source/discretization audit + conditional physical scaling.
- **Quality:** medium-high for establishing a resolved effect within the stated dimensionless PDE; incomplete until smooth-source flux checks and an independent normal-branch/2-Hessian solve agree.
- **Resolved result:** The corrected-ray ratio at `r/r0=1` remains roughly `3.3` across paper-style and exact-volume grids, but spans about `3.15-3.38` over the widest stopping/angular sweep. Exact source-volume fractions give absolute-gradient peaks `11.774`, `11.786`, and `11.788` on `200 x 100`, strict `400 x 200`, and `400 x 400`, only `0.12%` total drift. The absolute profile, not the precise ratio maximum, is the best-converged observable.
- **Numerical audit:** The raw first-shell peak varies materially with grid and update tolerance. The paper-style `200 x 100`, `1e-8` stop leaves algebraic residual `4.34e-3` and minimum spatial coefficient `-0.0179`; strict `400 x 200`, `1e-10` paper/exact-volume runs reach residuals `1.47e-4`/`1.06e-4` and minimum coefficients `+0.0109`/`+0.0128`. A `400 x 400` paper-stop field is also positive. The negative coarse minimum occurs in the first cell and trends positive, so it is not a demonstrated continuum instability. Exact-volume `rmax=80` and `160` results agree within `0.5%`, while `rmax=40` is measurably biased.
- **Source audit:** Center-mask source volume is `1.2493`, `0.9372`, and `0.9379` times nominal on the three grids. The default exact-overlap source integrates nominal mass exactly and preserves the resolved ratio, separating interface mass drift from the geometry effect.
- **Physical translation:** For `M=Lambda=1.758e-13 eV`, `beta=1`, and `r0=1 m`, density is `1.13e-25 kg/m^3`, nominal mass `6.26e-22 kg`, and the full sampled-ray scalar acceleration peak is only about `6e-35 m/s^2`. Naive fixed-parameter scaling to `0.01g` gives `r0~1.62e33 m` and mass `~2.64e78 kg`; the model is invalid on those scales, so this is a reductio rather than a device estimate. The exact center is zero; any target force has an equal-opposite source reaction.
- **Impact on hypotheses:** Adds H-018/B-021. It validates a local dimensionless anti-screening effect, not useful artificial gravity, material-density persistence, asymmetric field shaping, or propulsion.

### Dickson et al. - Condition Estimates for Pseudo-Arclength Continuation

- **Link:** https://arxiv.org/abs/math/0603716
- **Type:** primary numerical-analysis paper (2006).
- **Quality:** high for conditioning and Newton-GMRES behavior near regular points and simple folds; it is not specific to Galileon equations or ellipticity.
- **Relevant claims:** Natural-parameter continuation can encounter a singular field Jacobian at a simple fold, while pseudo-arclength augments the system so the path Jacobian remains nonsingular under the paper's regularity assumptions. This supports adaptive source-amplitude stepping and explains why a failing corrector need not, by itself, prove nonexistence.
- **Boundary for E-024/E-025:** Pseudo-arclength may follow a mathematical solution curve, but it cannot convert loss of the Galileon spatial-principal signs into a physically admissible branch. Ellipticity and kinetic-sign gates remain hard stops rather than continuation parameters.

### E-024 Smooth-Source and Shifted-2-Hessian Validation

- **Link:** Internal model and calculation, 2026-07-15; see `models/e024_galileon_continuation.py` and `models/e024_shifted_2hessian.py`.
- **Type:** smooth-source nonlinear PDE continuation + algebraic reformulation + flux/grid/width/box audit.
- **Quality:** medium-high for ruling out a simple discontinuous-interface artifact on the tested centered-grid family; incomplete as an independent continuum validation because the two formulations share the same coordinate/stencil family.
- **Source construction:** Uses positive quintic `C2` radial and angular transitions, integrates cell averages in `r^3` and `sin(theta)` variables, and renormalizes to the sharp wedge's scalar charge. On `200 x 100`, the broad profile spans at least `6.37` local cell widths and passes the six-cell gate. The narrower profile spans only `5.09` angular cell widths and is retained as a stress test, not a passing resolution case. Both preserve total source exactly by construction.
- **Resolved result:** The broad smooth source gives force ratio `3.4067` at `r/r0=1`, peak absolute gradient `11.7523`, and maximum shell-flux error `0.188%`; the narrower source gives `3.3796`, `11.7683`, and `0.229%`. The broad `120 x 60` to `200 x 100` ratio drift is `0.014%`, while `rmax=40` is biased and `80`/`160` are much closer. The enhancement therefore survives smoothing and ordinary numerical sensitivity checks.
- **Branch diagnostics:** The shifted source-amplitude solve remains on the positive normal branch through `lambda=1`; the fine broad rerun has global discrete minimum spatial-principal value `0.00616`, `K_t=1.00003`, positive local `sigma_2`, and original-equation residual `1.21e-7`. The minimum occurs in the first radial/equatorial cell at `(r,theta)=(0.0254,0.00785)`; excluding one boundary-cell layer raises the minimum to `0.01282`. This is a location-aware boundary/stencil warning, not a physical near-degeneracy or condition-number measurement.
- **Formulation audit:** The shifted 2-Hessian and original fields agree to parts in `1e9`, their gradients to a few parts in `1e7`, and their shell currents to about `1e-6`. These are strong implementation/branch cross-checks. They are not a genuinely independent discretization result: for one discrete Hessian, the shifted and original residuals are algebraically identical up to `2c3`.
- **Failure preserved:** On the fine grid, the under-relaxed original Picard solve reaches an update norm near `1e-11` and tiny volume-weighted residual but leaves a conservative unweighted algebraic residual near `1.1e-3`. The published update criterion alone is therefore rejected as a certificate. Density, material, asymmetry, and target continuation remain gated on E-025's monotone wide-stencil or different-coordinate solve.
- **Physical interpretation:** The exact center remains zero and the prior `r0=1 m` cosmological acceleration remains only `~6e-35 m/s^2`. This supports a conditional local nonlinear geometry effect, not useful artificial gravity, inertial control, FTL travel, or reactionless propulsion.

### E-025 Independent Axisymmetric Wide-Directional 2-Hessian Core

- **Link:** Internal model and calculation, 2026-07-16; see `models/e025_axisymmetric_wide_2hessian.py` and `tests/test_e025_axisymmetric_wide_2hessian.py`.
- **Type:** independent operator implementation + manufactured, branch, source-quadrature, and coarse actual-source checks.
- **Quality:** medium-high for verifying a separate numerical core; incomplete for the fixed annular field because the joint force/flux refinement campaign has not run.
- **Independent construction:** Uses a uniform cylindrical meridional quarter-disk, primitive orthogonal direction pairs, a separate azimuthal chord, positive unequal-distance circle intersections, the global monotone `sigma_2` extension, and continuous source normalization. It imports no E-023/E-024 discretization or source array.
- **Core result:** Thirteen focused tests and all workspace tests pass. The small-source smoke solve has relative residuals `5.15e-9`/`6.84e-9` in `L2`/`Linf`, minimum pair sum `0.4940`, and positive spatial/time diagnostics. The invalid curvatures `(-5,-5,1)` have raw `sigma_2=15` but monotone extension `-25`, preventing a false branch pass.
- **Directional sensitivity:** Fixed `m=2` manufactured interior errors plateau near `1.41e-3` under the last spatial refinement, whereas a coupled `(h,m)` sequence continues down to `6.80e-4`. Boundary-inclusive coupled errors are not yet monotone. This directly preserves the literature's fixed-stencil and boundary warnings.
- **Actual-source stress result:** Under-resolved `rmax=80` runs at `(h,m)=(1,1)` and `(0.5,2)` converge with positive minima and relative residuals below `6e-9`, but span only `0.8` and `1.6` cells across the full `0.8 r0` angular scale at the radial window's half-height (`r=8`). Their independent source-charge errors are `-1.018%` and `-0.1024%`. They establish solver reach, not the annular force or flux.
- **Resource boundary:** At `rmax=80`, `h=0.125` gives `322319` quarter-disk unknowns and `6.4` cells across that scale; `m=4` still reaches `0.625`, about `78%` of the `0.8` feature. A six-cell grid alone is therefore insufficient without further stencil-reach and observable convergence.
- **Failure preserved:** E-025 has not independently reproduced the `3.4067` ratio, `11.7523` peak, `0.188%` shell flux, or continuum admissibility margin. Linear/White comparison, ray force, shell flux, fine boundary behavior, and at least one six-cell joint-refinement level remain open. H-019 confidence is unchanged and all density/asymmetry/target extensions stay blocked.
- **Physical interpretation:** This remains numerics for an undetected hypothetical field. It supplies no useful artificial gravity, inertial control, FTL, or reactionless propulsion result.

### Trudinger and Wang - Hessian Measures II

- **Link:** https://arxiv.org/abs/math/9909199
- **Type:** primary mathematical-analysis paper; *Annals of Mathematics* 150 (1999), 579-604.
- **Quality:** high for the continuous `k`-convex/admissible structure and weak Hessian measures; it is not a numerical-convergence theorem for E-025's cylindrical stencil.
- **Relevant claims:** The `k`-Hessian equations live on a restricted admissible cone rather than on arbitrary symmetric Hessians. This is the continuous mathematical reason that a positive raw `sigma_2` value is not enough: the branch and pair-sum conditions must be retained.
- **Impact on hypotheses:** Reinforces E-025's hard admissibility gate. It does not transfer Froese's Cartesian discrete convergence result to the meridional-plus-azimuthal, reflected-axis, shortened-circle construction.

### E-025 Diagnostic Completion and First Coupled Refinement Attempt

- **Link:** Internal model and calculation, 2026-07-17; see `models/e025_axisymmetric_wide_2hessian.py` and `tests/test_e025_axisymmetric_wide_2hessian.py`.
- **Type:** independent force/residual/flux postprocessing + active-Jacobian performance repair + fixed-tolerance refinement attempt.
- **Quality:** medium for exposing the current convergence trajectory and solver boundary; not a continuum certificate because only the under-resolved coarse point completed.
- **Formula audit:** For `c3>0`, White et al.'s normal-root residual maps exactly with `k=1/c3` and `rho=S/c3`. The current `J_rho,J_z` obey `div J=S`; spherical flux restores both signs of `z` and the full azimuth with `4 pi r^2 integral cos(theta) J.n dtheta`. Minimum radicand and normal-branch factor are explicit gates. Trudinger and Wang support the continuous admissible-cone restriction, not the discrete cylindrical specialization.
- **Implementation result:** Added a fixed-frame linear Poisson cross-check, separately evaluated interpolated/centered cylindrical Hessian and White residual, force ray, spherical shell flux, pair-minimum locations, and broad-annulus driver. The assembled active Jacobian exactly matches the previous action and halves the measured coarse runtime from `78.1 s` to `40.0 s`; all `78` workspace tests pass.
- **Coarse quantitative result:** At `R=80`, `(h,m)=(0.5,2)`, the solver residual is `7.685e-10`, source-charge error `-0.102401%`, and pair/spatial/time minima are positive. The independent force ratio at `r=1` is `2.60205`, peak gradient `10.9761`, centered original/White volume residuals are `2.9599%`/`0.6131%`, and shell-flux errors are `-4.008%,-4.354%,-4.500%`. These remain materially away from E-024's `3.40669`, `11.75234`, and `0.188%` maximum flux error.
- **Fine failure preserved:** `(0.25,3)` improves sampled-charge error to `-0.006813%` but fails GMRES at amplitude `5/12`, Newton iteration `4`, with relative residual `5.493e-6` after `4707` stage Krylov iterations. Pair/spatial/time margins remain positive (`0.02465/0.04931/1.000004`), so the stop diagnoses conditioning rather than branch loss. No fine force or flux is quoted.
- **Impact on hypotheses:** H-019 confidence is unchanged. E-025's observable layer is complete enough for the next solve, but the independent annulus gate remains blocked on a checkpointable, Jacobian-aware fine-grid preconditioner. Density/asymmetry continuation remains out of scope.

### Knoll and Keyes - Jacobian-Free Newton-Krylov Methods: A Survey of Approaches and Applications

- **Link:** https://doi.org/10.1016/j.jcp.2003.08.010
- **Type:** primary numerical-methods review; *Journal of Computational Physics* 193 (2004), 357-397.
- **Quality:** high for Newton-Krylov algorithm structure and preconditioning principles; it does not analyze E-025's particular semismooth 2-Hessian operator.
- **Relevant claims:** Krylov performance is governed by preconditioning even when Jacobian-vector products are matrix free. A useful preconditioner may be an approximate or simplified Jacobian, but it must capture the stiff physics/operator structure well enough to make the linear correction tractable.
- **Impact on E-025:** Supports replacing the fixed zero-state coordinate-Laplacian inverse with a current-active-Jacobian approximation while leaving the exact active Jacobian, nonlinear residual, and branch-preserving line search unchanged.

### Saad - ILUT: A Dual Threshold Incomplete LU Factorization

- **Link:** https://doi.org/10.1002/nla.1680010405
- **Type:** primary numerical-methods paper; *Numerical Linear Algebra with Applications* 1 (1994), 387-402.
- **Quality:** high for the threshold-and-fill incomplete-factorization method; problem-specific robustness must be measured rather than inferred.
- **Relevant claims:** ILUT controls both numerical dropping and retained fill, providing a tunable sparse approximation to a nonsymmetric matrix factorization.
- **Impact on E-025:** Motivates the active-Jacobian `spilu` benchmark. The exact former stalled state improves from a capped `2000` GMRES iterations with the zero-state preconditioner to `478` with drop/fill `1e-3 / 10`; this is an internal benchmark, not a theorem or continuum result.

### Eisenstat and Walker - Choosing the Forcing Terms in an Inexact Newton Method

- **Link:** https://doi.org/10.1137/0917003
- **Type:** primary numerical-analysis paper; *SIAM Journal on Scientific Computing* 17 (1996), 16-32.
- **Quality:** high for inexact-Newton forcing terms and local convergence; E-025's semismooth active-set changes require separate care.
- **Relevant claims:** An inexact Newton correction must satisfy a controlled linear residual `||F+Js|| <= eta ||F||`, with a forcing parameter below one. Adaptive forcing can avoid oversolving early nonlinear iterations while retaining convergence conditions.
- **Impact on E-025:** Supplies the audit that rejects finite capped GMRES directions as usable Newton corrections: the tested full-source directions had true linear residual ratios `1.3565` and `1.5409`, even though heavy damping could make the nonlinear residual decrease slightly. E-025 therefore continues to reject positive GMRES `info`.

### Sala and Tuminaro - A New Petrov-Galerkin Smoothed Aggregation Preconditioner for Nonsymmetric Linear Systems

- **Link:** https://doi.org/10.1137/060659545
- **Type:** primary numerical-methods paper; *SIAM Journal on Scientific Computing* 31 (2008), 143-166.
- **Quality:** high for nonsymmetric smoothed aggregation; transfer to E-025's changing active operator is unproven.
- **Relevant claims:** Distinct restriction and prolongation operators can extend smoothed aggregation to nonsymmetric systems through a Petrov-Galerkin coarse operator.
- **Impact on E-025:** Provides one principled multilevel candidate for E-026. It must be benchmarked on the exact saved `11/12` active Jacobian and may not be treated as branch-preserving merely because it accelerates the linear solve.

### Manteuffel, Ruge, and Southworth - Nonsymmetric Algebraic Multigrid Based on Local Approximate Ideal Restriction

- **Link:** https://doi.org/10.1137/17M1144350
- **Open version:** https://arxiv.org/abs/1708.06065
- **Type:** primary numerical-methods paper; *SIAM Journal on Scientific Computing* 40 (2018), A4105-A4130.
- **Quality:** high for local approximate ideal restriction (`lAIR`) and nonsymmetric reduction-based AMG; no E-025-specific convergence guarantee follows.
- **Relevant claims:** Local approximation of ideal restriction can produce scalable reduction-based multigrid preconditioners for difficult nonsymmetric systems where classical symmetric assumptions are inappropriate.
- **Impact on E-025:** Supplies the second E-026 candidate. A fixed V-cycle can precondition GMRES; if the inner action changes across Krylov iterations, flexible GMRES is required and must be tested as a distinct solver configuration.

### Manteuffel, Münzenmaier, Ruge, and Southworth - Nonsymmetric Reduction-Based Algebraic Multigrid

- **Link:** https://doi.org/10.1137/18M1193761
- **Open version:** https://arxiv.org/abs/1704.05001
- **Type:** primary numerical-methods paper; *SIAM Journal on Scientific Computing* 41 (2019), S242-S268.
- **Quality:** high for the broader nonsymmetric reduction framework and `nAIR`; its near-triangular transport emphasis does not match E-026's bidirectional diffusion-like matrix.
- **Relevant claims:** Reduction-based AMG can be analyzed through separate error- and residual-propagation conditions, but the useful transfer and relaxation choices depend on matrix structure. The E-026 active Jacobian is not near triangular, so this paper is a boundary against selecting `nAIR` merely because the problem is nonsymmetric.

### PyAMG 5.3 - AIR and Nonsymmetric Smoothed-Aggregation Interfaces

- **Links:** https://pyamg.readthedocs.io/en/latest/generated/pyamg.classical.html and https://pyamg.readthedocs.io/en/latest/generated/pyamg.aggregation.html
- **Type:** official implementation documentation for the library used by E-026.
- **Quality:** authoritative for API behavior and default hierarchy construction, not a convergence guarantee for the annular operator.
- **Relevant claims:** `air_solver` accepts nonsymmetric CSR matrices and implements lAIR restriction; `smoothed_aggregation_solver(..., symmetry='nonsymmetric')` accepts separate right and left near-null candidates `B` and `BH`; `aspreconditioner(cycle='V')` exposes one fixed cycle as a SciPy `LinearOperator`. PyAMG's classical strength implementation states that its negative-edge convention is designed for M-matrices.
- **Impact on E-026:** Justifies sign-normalizing to `A=-J`, checking the positive-diagonal/nonpositive-off-diagonal pattern before hierarchy setup, freezing the V-cycle inside each GMRES call, and recording hierarchy complexity rather than inferring scalability from convergence alone.

### SciPy Sparse ILU and GMRES Interfaces

- **Links:** https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.linalg.spilu.html and https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.linalg.gmres.html
- **Type:** official library documentation for the implementation used in E-025.
- **Quality:** authoritative for API behavior, not for problem-specific mathematical convergence.
- **Relevant claims:** `spilu` exposes drop tolerance, fill factor, and SuperLU ordering controls. With `callback_type='pr_norm'`, SciPy GMRES reports inner iterations while `maxiter` counts restart cycles; convergence is tested against the unpreconditioned residual norm.
- **Impact on E-025:** Fixes the interpretation of `restart=50,maxiter=40` as at most `2000` inner iterations per correction and makes the recorded setup/fill provenance reproducible.

### E-025 Active-ILUT Recovery and Full-Source Boundary

- **Link:** Internal model and calculation, 2026-07-18; see `models/e025_axisymmetric_wide_2hessian.py`, `tests/test_e025_axisymmetric_wide_2hessian.py`, `models/checkpoints/README.md`, and `Daily_Log.md`.
- **Type:** checkpoint/restart implementation + exact stalled-state preconditioner benchmark + fixed-cap continuation and capped-direction audit.
- **Quality:** medium-high for the reproducible numerical boundary at this grid and source schedule; incomplete as an independent continuum result because the exact full-source point still does not converge.
- **Implementation result:** Atomic checkpoints preserve only accepted fields and validated metadata. They fingerprint the full discrete operator including boundary offsets as well as the grid and source, and reject preconditioner changes after accepted work in an incomplete stage. The solver rejects an inadmissible restart before the residual shortcut, rebuilds `spilu` on the exact active Jacobian once per Newton step, and records setup count/time/factor fill. Completed and interrupted mid-stage resumes are tested; all `82` workspace tests pass.
- **Former-wall result:** At the old `5/12` state, active ILUT `1e-3 / 10` closes the correction in `478` inner iterations and reduces nonlinear residual from `5.493e-6` to `~4.59e-8` without eroding the positive pair/spatial/time margins.
- **Continuation result:** The unchanged campaign reaches accepted amplitude `11/12`, then fails the first full-source correction at the same `2000`-iteration cap. Stronger ILUT and intermediate `23/24` and `15/16` targets also cap. The accepted `11/12` state remains admissible, so this is not demonstrated loss of ellipticity.
- **Failure preserved:** Full-source capped directions have true linear residual ratios above one. Their small nonlinear decrease after heavy damping is rejected as insufficient under the inexact-Newton criterion. No full-source force, residual, or flux is quoted, H-019 confidence remains `Medium-low`, and density/asymmetry continuation remains blocked.
- **Blank space:** The next test is a nonsymmetric multilevel preconditioner—Petrov-Galerkin smoothed aggregation or lAIR—against the saved `11/12` active Jacobian, with the true linear residual ratio and all existing nonlinear/admissibility gates retained.

### E-026 Nonsymmetric AMG Closure of the Exact Full-Source Point

- **Link:** Internal model and calculation, 2026-07-19; see `models/e026_nonsymmetric_amg.py`, `tests/test_e026_nonsymmetric_amg.py`, and `models/checkpoints/e026_h025_m3_full_source_pgsa.npz`.
- **Type:** exact saved-Jacobian characterization + two-family fixed-AMG benchmark + branch-gated nonlinear completion + independent observable audit.
- **Quality:** medium-high for closing the exact `(h,m)=(0.25,3)` solver gate reproducibly; still incomplete as a continuum validation because this source transition has only about `3.2` cells and no same-observable six-cell or outer-box point exists.
- **Matrix result:** The canonical checkpoint SHA-256 is unchanged. Its active Jacobian is `80731 x 80731` with `458371` nonzeros and Frobenius asymmetry `||J-J^T||/||J||=0.139018`. For `A=-J`, every diagonal is positive, every off-diagonal is negative, `79522` rows have near-zero sums, and `1209` boundary-influenced rows are strictly diagonally dominant. This supports an M-matrix-like diffusion interpretation, not SPD treatment; the symmetric part is not positive definite.
- **Saved-corrector benchmark:** Under the unchanged GMRES `restart=50`, `maxiter=40`, and `rtol=1e-8`, default lAIR converges in `20` inner iterations with true residual ratio `2.609e-9`, but its operator complexity is `14.983` and setup is about `2.44 s`. Deterministically seeded nonsymmetric PG-SA with the boundary-vanishing candidate `1-(r/R)^2` converges in `45` iterations with true ratio `9.182e-9`, operator complexity `1.606`, and setup about `0.22 s`. Both have `info=0`; neither relies on a capped vector.
- **Left/right-candidate sensitivity:** Let `q=1-(r/R)^2`. L2-normalized `(B,BH)=(q,q),(1,1),(q,1),(q,rho q)` all build the same four-level, `736000`-nonzero hierarchy and converge with `info=0` in `45,57,54,44` iterations, respectively; true residual ratios remain below `1e-8`. The volume-weighted left candidate saves only one iteration, while constants cost `20-30%` more. The retained `(q,q)` choice is therefore a simple geometry-matched heuristic, not a delicately tuned necessity.
- **Full-source result:** Rebuilding one fixed PG-SA hierarchy per Newton step closes the target in three undamped accepted corrections. Relative nonlinear `L2` residual falls `8.333e-2 -> 1.761e-3 -> 9.746e-6 -> 7.189e-8`; GMRES uses `45+44+46=135` inner iterations; all true linear ratios are below `1e-8`; final **wide-stencil all-frame** pair/spatial/time minima are `0.0088301 / 0.0176603 / 1.0000128`. Default lAIR independently reaches the same tolerance in `20+20+20=60` iterations, and a fresh deterministic comparison agrees with PG-SA to relative `L2=1.67e-15`, but its hierarchy remains about `9.3x` more complex.
- **Reproducibility boundary repaired:** PG-SA setup initially consumed unrecorded global NumPy randomness. The retained campaign now isolates seed `260719`, restores caller RNG state, records effective hierarchy/candidate/runtime/code provenance, authenticates the report as well as the field, and passes an exact canonical rerun test. This repairs computational reproducibility; it does not strengthen the physics.
- **Independent admissibility warning:** The artifact's separate fixed-frame cross-check has minimum spatial-principal value `-0.0243895`; an independent centered reconstruction finds one negative node, `-0.0250979`, at `(rho,z)=(6.25,0.75)`. The `11/12` input was already negative there, so this is not an AMG regression, but it prevents promoting the positive wide-stencil gates or White radicand to continuum-admissibility evidence.
- **Independent observables:** The full-source fine point gives force ratio `3.28303` at `r/r0=1`, peak gradient `11.0713`, centered original/White residuals `1.963% / 0.328%`, and shell-flux deficits `1.857-1.986%`. It moves from the coarse E-025 point (`2.60205`, `10.9761`, `4.01-4.50%`) toward E-024 (`3.40669`, `11.75234`, `0.188%`) but remains materially different. This is the first completed independent refinement point, not an independent continuum confirmation.
- **Fine-grid preflight boundary and start:** The `(0.125,4)` six-cell model has `322319` unknowns, `12` bases, and `-0.0004316%` sampled-charge error. Raw E-026-field prolongation is inadmissible (`-145.73 / -291.46 / -291.46` pair/spatial/time), remains so through `1/4`, and becomes barely admissible only below `alpha~=0.00341926` because of the outer cutoff at `(78.125,15.5)`; reject it as a warm start. The native fine-grid Poisson reference solves in `1.12 s`, and `(1/12) phi_linear` passes with `0.06323 / 0.12647 / 0.98999`, matching the first source target. Peak RSS was about `1.46 GiB` during that direct linear solve. E-028 should use this `1/12` start, with `1/24` (`0.28162 / 0.56323 / 0.99499`) as fallback. No fine nonlinear solve or AMG hierarchy was attempted.
- **Boundary and impact:** E-026 is complete as a discrete conditioning result. H-019 gains evidence but remains `Medium-low` until a six-cell coupled point makes the negative centered/fixed-frame node nonnegative or demonstrably convergent and an outer-box comparison stabilizes the same observables. Density, material, asymmetry, target, EFT, artificial-gravity, and propulsion extensions remain blocked.

### Saldanha, Marletto, and Vedral - Repulsive Gravitational Force as a Witness of the Quantum Nature of Gravity

- **Link:** https://arxiv.org/abs/2602.12266
- **Type:** primary theoretical preprint; arXiv v1, submitted 2026-02-12.
- **Quality:** medium for the conditional-interference mechanism; low for current experimental feasibility because the four-page treatment omits finite source size, a total-trial sensitivity budget, and quantitative background/decoherence controls, and contains a material postselection-probability inconsistency.
- **Mechanism:** A source mass is prepared in `alpha|A>+beta|B>`. Its two locations give a probe attractive impulses `delta_j=G M m T/x_j^2>0`. Postselection near a dark source port leaves `psi_ps(p) proportional to beta psi(p-delta_B)-alpha psi(p-delta_A)`, whose weak-limit displacement `delta_eff=(beta delta_B-alpha delta_A)/(beta-alpha)` can be negative through destructive interference.
- **Exact Gaussian audit:** With probe momentum standard deviation `sigma_p`, branch overlap is `S=exp[-(delta_A-delta_B)^2/(8 sigma_p^2)]`. The exact successful-port probability is `P_-=[1-2 alpha beta S]/2`, and the exact conditional mean is `[beta^2 delta_B+alpha^2 delta_A-alpha beta(delta_A+delta_B)S]/[1-2 alpha beta S]`. The simple translated-packet interpretation additionally requires the amplified displacement, not merely each bare impulse, to remain small relative to `sigma_p`.
- **Conservation boundary:** If the complementary port is retained, `P_-<p>_-+P_+<p>_+=alpha^2 delta_A+beta^2 delta_B>0`. The selected anomaly therefore creates no negative source field, net momentum, or propulsion opportunity.
- **Arithmetic audit:** The paper's stated `beta=1/sqrt(2)+0.0003` and `alpha=sqrt(1-beta^2)` give `P_ps=(beta-alpha)^2/2=1.8008e-7`, not the printed `0.8e-3`. Its approximately `-1059.9 delta_A` shift for `delta_A=10 delta_B` is consistent, so the amplification and stated probability cannot both describe that parameter set. The corrected rate is one success per about `5.6e6` preparations before other losses.
- **Impact on hypotheses:** Added H-020 as a low-confidence precision witness and B-025 as the durable boundary. This does not reopen any useful artificial-gravity, inertial-control, FTL, or reactionless-propulsion path.

### Postselected Metrology Resource Boundary - Ferrie and Combes; Yang

- **Links:** https://doi.org/10.1103/PhysRevLett.112.040406 and https://doi.org/10.1103/PhysRevLett.132.250802
- **Type:** primary peer-reviewed quantum-metrology papers.
- **Quality:** high for resource-normalized weak-value/postselection interpretation; neither paper analyzes this gravitational apparatus specifically.
- **Relevant claims:** Near an orthogonal postselection, signal gain scales approximately as `g` while successful-event probability falls approximately as `g^-2`; discarded trials prevent unbounded shot-noise or Fisher-information gain. Postselection can nevertheless act as useful information compression when the final detector is noisy, saturated, or expensive.
- **Impact on E-027:** Optimize likelihood or Fisher information per prepared source-probe cycle, including both ports and detector constraints, rather than maximizing `g`. The retained proposal must state the technical-noise regime that makes postselection useful.

### Nanodiamond Geometry and Background Context - Vicentini et al.; Di Pietra et al.

- **Links:** https://arxiv.org/abs/2405.21029 and https://arxiv.org/abs/2410.19601
- **Type:** primary nanodiamond quantum-gravity feasibility proposals.
- **Quality:** medium as platform studies; proposed rather than demonstrated, but useful for finite-size, Casimir-Polder, vacuum, temperature, and coherence scales.
- **Finite-size audit:** At diamond density, the postselected-gravity paper's `2e-8 kg` source has radius about `111 micrometers`, exceeding its `50 micrometers` center distance. Its `1e-14 kg` source has radius about `0.879 micrometers`, exceeding its `0.4 micrometers` center distance. Even the densest ordinary condensed matter cannot fit either point-source mass inside the assumed radius.
- **Background alarm:** Reinterpreting the second `0.4 micrometers` as a surface gap gives center distance about `1.288 micrometers` and lowers the nominal selected signal from `0.001978` to about `1.91e-4` momentum widths. A retarded dielectric-dipole estimate at that corrected distance places the Casimir-Polder force roughly `1e12` above gravity and is only an alarm estimate because the close geometry violates the far-separation dipole approximation. Related platform studies move toward roughly `200 micrometers`, cryogenic operation, extraordinary vacuum, and shielding; at `200 micrometers`, the paper's second Eq. (11) signal falls to about `7.9e-9` widths.
- **Impact on E-027:** Enforce physical radii and surface gaps before optimizing. Include grounded-screen geometry, charge/dipole budgets, sphere-screen forces, trap gradients, collisions, thermal decoherence, phase stability, and repetition rate.

### Classical-Gravity Witness Scope - Aziz and Howl; Gundhi, Infantino, and Bassi

- **Links:** https://doi.org/10.1038/s41586-025-09595-7 and https://arxiv.org/abs/2604.19696
- **Type:** peer-reviewed theoretical challenge and current technical rebuttal concerning whether classical gravity coupled to quantum matter can generate entanglement.
- **Quality:** high relevance but unsettled interpretation. The 2025 claim and 2026 rebuttal disagree about whether the retained transition amplitudes permit classical-gravity-generated matter entanglement.
- **Impact on H-020:** A negative conditional momentum would cleanly exclude an incoherent convex mixture of noninvasive branchwise-attractive kicks after selection-bias controls. Inferring quantized spacetime or gravitons additionally requires locality, mediator, matter-model, and channel-closure assumptions. E-027 should compare explicit models rather than label every classical alternative excluded.

### Internal Postselected-Gravity Feasibility Audit

- **Link:** Internal derivation and calculation, 2026-07-18; retained as E-027, H-020, and B-025.
- **Type:** exact Gaussian audit + finite-size estimate + ideal sample-count bound + opportunity design.
- **Quality:** high for the algebra and elementary geometry under stated assumptions; conditional for Casimir-Polder and apparatus feasibility until a full finite-body screened model is built.
- **Signal and trial scale:** The paper's heavy-probe benchmark gives `|delta_eff|/Delta p=0.001978`, velocity shift `2.09e-10 m/s`, and conditional acceleration `4.17e-10 m/s^2` over `0.5 s`. An independent Gaussian mean measurement needs approximately `(5/0.001978)^2=6.4e6` accepted detections for `5 sigma`. If `delta_A/delta_B=10`, `g=100` implies `P_ps` near `2.0e-5`, or about `3.2e11` ideal preparations before inefficiency and systematics.
- **Best retained opportunity:** Measure both output ports and the full probe likelihood; deliberately remove source coherence; block each path; scan postselection phase; reverse geometry; and test `M`, `T`, and `x^-2` scaling. First reproduce the same port-complete interference ledger with a calibrated electromagnetic or optical force. Only a non-overlapping, screened parameter region that survives this accounting merits a gravity experiment.

### Awanou - Iterative Methods for k-Hessian Equations

- **Links:** https://doi.org/10.4310/MAA.2018.v25.n1.a3 and https://arxiv.org/abs/1406.5366
- **Type:** primary peer-reviewed numerical-analysis paper plus author preprint.
- **Quality:** high for iterative solution of discrete `k`-Hessian equations under the paper's hypotheses; indirect for E-028 because its schemes, domains, boundary handling, and initialization argument are not the cylindrical wide-directional construction used here.
- **Relevant claim:** Poisson-type initializations and iteration within a discrete admissible class are principled tools in another `k`-Hessian framework. This supports testing the native fine-grid Poisson field as a continuation seed, but it is not a convergence or branch-preservation theorem for E-028.
- **Impact on E-028:** The native `(1/12) phi_linear` predictor is treated as a tested computational construction. Its positivity is checked directly before any residual shortcut; no theorem is imported across discretizations.

### PyAMG Multilevel Complexity Definitions and E-028 Memory Accounting

- **Link:** https://pyamg.readthedocs.io/en/latest/generated/pyamg.multilevel.html
- **Type:** official implementation documentation for the multilevel library used by E-028.
- **Quality:** high for PyAMG's reported complexity definitions; it is not a process-memory model.
- **Relevant claim:** Operator complexity is the sum of nonzeros in the level operators divided by fine-operator nonzeros. It does not include prolongation/restriction storage, setup temporaries, retained `keep=True` objects, Krylov vectors, Python/SciPy overhead, or the model's other arrays.
- **Impact on E-028:** Report A/P/R nonzeros and actual CSR-array bytes separately and treat process peak RSS as the authoritative resource envelope. The `1/12` campaign reaches operator complexity `1.7524` and at most about `72.6 MB` of explicitly counted A/P/R sparse arrays, yet peak RSS is about `1.84 GiB`.

### E-028 Native Fine-Grid `1/12` Bootstrap and Resource Audit

- **Link:** Internal model and calculation, 2026-07-20; see `models/e028_fine_grid_campaign.py`, `tests/test_e028_fine_grid_campaign.py`, `models/checkpoints/e028_h0125_m4_campaign_checkpoint.npz`, and `models/checkpoints/e028_h0125_m4_1of12_pgsa.npz`.
- **Type:** digest-checked nonlinear-PDE calculation, same-amplitude control, deterministic replay, and source-backed numerical-method audit.
- **Quality:** high for exact replay and stated discrete solver/resource results in the recorded environment; conditional for continuum interpretation because the stage is only `1/12` source, the cylindrical scheme is an internal adaptation of published Cartesian methods, `h/dtheta` is not small, physical stencil reach is still large, and no outer-box or full-source fine point has been run.
- **Strict solve result:** On `R=80`, `(h,m)=(0.125,4)`, `322319` unknowns, the verified native `(1/12) phi_linear` predictor has wide pair/spatial/time minima `0.06323 / 0.12647 / 0.98999` but a normalized nonlinear defect `0.5678`. Ten undamped Newton corrections and `370` GMRES inner iterations reach the matching `1/12` target with nonlinear relative `L2=9.455e-12`. Every corrector returns `info=0`, uses fewer than `2000` inner iterations, and has a directly evaluated true residual ratio below `1e-8`. Final wide minima are `0.21440 / 0.42880 / 1.00000003`; fixed and independently centered spatial minima are `0.42880` and `0.42992`, with no nonpositive nodes.
- **Partial-source observables:** The explicitly `1/12`-normalized force ratio at `r/r0=1` is `1.05057`; peak gradient is `1.51640` at the diagnostic-window endpoint `r=12`; centered original/White residuals are `0.7317% / 0.3245%`; and sampled-partial-charge flux deficits are `0.328% / 0.291% / 0.258%`. These are not comparable as refinements of E-026's full-source ratio, peak, or flux. In particular, the positive weak-source centered check does not resolve E-026's full-source negative node.
- **Same-amplitude control:** A strict `(h,m)=(0.25,3)`, `1/12` control closes in `8` Newton corrections and `189` GMRES iterations. Moving to the fine grid lowers centered original/White residuals by about `46.8% / 46.9%`, lowers the worst flux-deficit magnitude by `34.6%`, and lowers source-charge-error magnitude by `93.7%`; the force ratio changes by `+0.86%` and peak by `+0.33%`. Peak memory rises by about `3.29x` and GMRES work by `95.8%`. This is bootstrap convergence evidence, not a full-source continuum point.
- **Hierarchy sensitivity and replay:** Geometry-matched `(q,q)`, `(q,rho q)`, and constant candidates all close in the same ten Newton steps, using `370`, `354`, and `400` GMRES iterations; their fields agree to relative `L2` of order `1e-15`. A fresh-process canonical replay is bitwise identical. lAIR was not attempted on the fine grid because E-026 already measured operator complexity `14.983`, consistent with published warnings that reduction hierarchies can fill for diffusion-like problems; the lower-complexity PG-SA path already passed every current stage gate.
- **Resolution and resource boundary:** `dtheta=0.12249`, `h/dtheta=1.0205`, maximum primitive reach is `0.625 r0`, and reach/source-transition scale is `0.78125`. Peak RSS is about `1.84 GiB`; maximum PG-SA operator complexity is `1.7524`, with about `72.6 MB` maximum explicit A/P/R sparse storage. Checkpoint resume retains the full linear field and avoids repeating the direct solve.
- **Outer-box trap:** Existing annulus diagnostics choose flux spheres relative to the box. `R=80` and `R=160` would therefore measure different radii. A valid later box comparison must use fixed physical spheres and a common interior diagnostic window while separately retaining whole-box minima.
- **Impact on hypotheses:** H-019 remains `Medium-low`. E-028 stage `1/12` is complete as a solver/bootstrap result, B-027 forbids promoting it to a full-source refinement, and the next strict target is `2/12`. Density, material, asymmetry, target, EFT, artificial-gravity, inertial-control, FTL, and propulsion extensions remain blocked.

### E-028 `2/12` Method and Source Audit

- **Links:** Froese, Oberman, and Salvador, https://arxiv.org/abs/1502.04969; Finlay and Oberman, https://arxiv.org/abs/1807.05150 and https://doi.org/10.1137/18M1200269; Awanou, https://arxiv.org/abs/1406.5366; Sala and Tuminaro, https://doi.org/10.1137/060659545; PyAMG nonsymmetric smoothed aggregation, https://pyamg.readthedocs.io/en/latest/generated/pyamg.aggregation.html; SciPy GMRES, https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.linalg.gmres.html; Mittelmann continuation, https://doi.org/10.1137/0723068.
- **Type:** primary numerical-analysis papers plus official implementation documentation.
- **Quality:** high for the stated Cartesian schemes, continuation concepts, and library semantics; indirect for E-028's axisymmetric/reflected/curved-boundary discretization and no evidence that the cubic-Galileon model is physically realized.
- **Admissible-cone correction:** For shifted Hessian eigenvalues `lambda_i`, `sigma_2=lambda_1 lambda_2+lambda_1 lambda_3+lambda_2 lambda_3` and the principal coefficients of its linearization are the three pair sums. Positive pair sums are therefore the right ellipticity test, but they do not alone imply `sigma_2>0` away from an exact pointwise root. The full `Gamma_2` check needs `sigma_1>0` and `sigma_2>0`; positive pair sums supply the former, while the latter should be recorded explicitly. E-028's accepted `2/12` field passes post hoc with active/fixed/centered shifted-`sigma_2` minima `0.187500 / 0.154191 / 0.154469`. This should become an explicit gate only through a checkpoint-compatible migration or replay, not an in-place code change.
- **Convergence boundary:** Froese-Oberman-Salvador require `h -> 0`, `dtheta -> 0`, and `h/dtheta -> 0` for their monotone Cartesian framework. Finlay-Oberman show error depends jointly on angular resolution and physical neighbor reach. E-028 moves in the right direction but still has `h/dtheta=1.0205` and reach `0.625 r0`, or `78.1%` of the source-transition scale. The theorem does not automatically cover the present cylindrical composition, and local-uniform field convergence would not by itself certify derivative observables such as peak force or flux.
- **Initializer and continuation boundary:** Awanou provides useful Poisson-iteration precedent under different hypotheses; Mittelmann provides general predictor-corrector precedent. Neither proves that E-028's native Poisson field, previous-stage field, or damped secant lies in the Newton basin. Direct residual and branch checks remain decisive.
- **Linear-solver semantics:** SciPy uses left preconditioning, minimizes the preconditioned residual, but tests final convergence against `b-Ax`; with `callback_type='pr_norm'`, `restart=50,maxiter=40` means at most `2000` inner iterations. E-028's direct recomputation of the true residual is therefore correctly interpreted. Each V-cycle is fixed within a GMRES call; a varying preconditioner would require a flexible Krylov method.
- **Naming correction:** Sala-Tuminaro's specific PG-SA algorithm includes restriction smoothing and local damping. PyAMG's `symmetry='nonsymmetric'` path builds distinct left/right candidates and a restriction from `A^H`, so “PyAMG nonsymmetric SA with Petrov-Galerkin-type transfers” is accurate. It is not literally the Sala-Tuminaro algorithm. The historical/internal `pgsa` configuration and artifact token are retained to preserve campaign fingerprints.

### E-028 Native Fine-Grid `2/12` Continuation and Predictor Audit

- **Link:** Internal calculation, 2026-07-21; see `models/e028_fine_grid_campaign.py`, `models/checkpoints/e028_h0125_m4_campaign_checkpoint.npz`, and `models/checkpoints/e028_h0125_m4_2of12_pgsa.npz`.
- **Type:** integrity-checked nonlinear-PDE continuation, same-amplitude controls, deterministic replay, admissibility audit, and scratch predictor sensitivity.
- **Quality:** high for the exact discrete state and stated runtime; conditional for any continuum interpretation, and inapplicable as evidence for a physical artificial-gravity field.
- **Strict stage result:** Starting from accepted `1/12`, the fine `2/12` target closes in nine Newton corrections and `327` GMRES iterations. Eight steps are full; one is damped to `0.25`. Final relative nonlinear `L2/Linf` are `1.98284e-12 / 3.48351e-11`; wide pair/spatial/time are `0.10327087 / 0.20654173 / 1.00000037`; fixed/centered are `0.20654173 / 0.20748251`, with no nonpositive nodes. Field SHA is `3219171452d92fa1e6f027623a318e6aed11bfe9e463a7a6e55c262251270290`; artifact SHA is `2f6beaa5cfec35870816df07faa6ce1520b77e8b3ad17cd6b50e8b9a3bcb98f3`; checkpoint SHA is `8dd454c10583f0cfe4287d7938228b5e41023e4121320c2f2b6ab35aa55b9db3`.
- **Partial-source observables:** Ratio at `r/r0=1` is `1.165716`; peak is `2.791581`; centered original/White residuals are `0.8553% / 0.2965%`; worst partial-charge flux deficit is `-0.5962%`. These are `2/12` observables and may not refine E-026's full-source values.
- **Same-amplitude control:** Coarse `(0.25,3)`, `2/12` closes in six Newton and `150` GMRES iterations. Fine refinement changes ratio/peak by only `+0.995% / +0.383%`, lowers centered original/White residuals `44.53% / 46.73%`, and lowers worst flux-deficit magnitude `38.43%`. Yet the tracked `(6.25,0.75)` centered value declines `3.25%`; convergence is not uniformly monotone by location. A scratch coarse `3/12` control also passes but has mixed residual/flux trends, furnishing a comparison point rather than a fine-grid prediction.
- **Predictor failure and bounded crack:** The full secant `2 phi_2-phi_1` fails wide, fixed, centered, and active-`sigma_2` checks. Damping has a narrow useful region: `lambda*=0.82454` minimizes the initial `3/12` residual, while imposing residual within `10%` of optimum plus fixed and active-`sigma_2` margins above `0.01` gives `0.80038 <= lambda < 0.83286`. At conservative `lambda=0.8`, one strict correction reaches residual `0.005353` with positive checks. A half-secant at midpoint `5/24` retains much wider margins and residual `0.03639`. These are fallback designs only; they do not modify or supersede the canonical plain-seed campaign.
- **Resource and implementation boundary:** Stage-2's process reports `1.616 GiB`, but that is invocation-local; campaign high-water remains the stage-1 value near `1.84 GiB`. Explicit retained A/P/R sparse arrays remain about `72.6 MB`. Source charge and memory are recorded audits, not threshold-enforced solver gates. Unkeyed SHA-256 fields provide integrity/reproducibility checks, not tamper authentication.
- **Interpretation ladder:** Linear GMRES convergence establishes one correction; Newton convergence establishes one fixed discrete root; source continuation establishes reach along that discrete branch; coupled grid/direction/box stabilization is needed for continuum evidence; outer-box stabilization is a further test; and none of these establishes that nature realizes the model or that it can create useful artificial gravity. H-019 therefore remains `Medium-low`, and the next canonical target is only `3/12`.

### E-028 `3/12` Runtime-Replay, Admissible-Cone, and Same-Amplitude Audit

- **Links:** Froese, Oberman, and Salvador, https://arxiv.org/abs/1502.04969 and https://doi.org/10.1093/imanum/drw007; Finlay and Oberman, https://arxiv.org/abs/1807.05150 and https://doi.org/10.1137/18M1200269; Awanou, https://arxiv.org/abs/1406.5366; Sala and Tuminaro, https://doi.org/10.1137/060659545; PyAMG nonsymmetric smoothed aggregation, https://pyamg.readthedocs.io/en/latest/generated/pyamg.aggregation.html; SciPy GMRES, https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.linalg.gmres.html; Mittelmann continuation, https://doi.org/10.1137/0723068.
- **Type:** primary numerical-analysis papers, official implementation documentation, and an integrity-checked internal nonlinear-PDE replay/calculation dated 2026-07-22.
- **Quality and transfer boundary:** High for the papers' stated Cartesian schemes, the `Gamma_2` definition, and SciPy/PyAMG implementation semantics; high for the exact saved discrete arrays and reports; indirect for E-028's cylindrical reflected-axis/curved-boundary construction; no evidence that nature realizes this cubic-Galileon field. Froese-Oberman-Salvador require positive `sigma_1` and `sigma_2` for `Gamma_2`, while their Proposition 2.6 couples positive pair sums with `sigma_2>0`; pair sums are the principal coefficients of the linearization, not a substitute for the nonlinear cone test. Their convergence theorem does not automatically certify E-028 or derivative observables. Finlay-Oberman likewise motivates joint angular and physical-reach refinement, but its stencil parameter is analogous rather than identical to E-028's primitive reach.
- **Continuation and initializer boundary:** Awanou supplies empirical/scheme-specific Poisson-initialization precedent and local results under smooth nondegenerate admissible solutions with a sufficiently close seed; it also records a degenerate three-dimensional failure. Mittelmann supplies historical predictor-corrector precedent. Neither proves that E-028's Poisson or previous-state seed lies in the Newton basin. The completed branch and residual checks remain the evidence.
- **AMG/GMRES implementation boundary:** Sala-Tuminaro uses restriction smoothing and local damping. PyAMG 5.3's nonsymmetric-SA path instead constructs distinct left/right candidates, derives restriction through an `A^H`-smoothed transfer, and uses a Petrov-Galerkin coarse operator; E-028's global Jacobi choice is not Sala-Tuminaro's local damping. The retained wording is therefore “PyAMG nonsymmetric SA with Petrov-Galerkin-type transfers,” with Sala-Tuminaro as precedent rather than identity. SciPy's GMRES uses left preconditioning, reports `pr_norm` at inner iterations, and still tests convergence with the unpreconditioned `b-Ax`; `restart=50,maxiter=40` permits at most `2000` inner iterations. E-028's independent direct-residual audit is correctly stricter than relying on callback history.
- **Provenance failure preserved:** Direct resume from `models/checkpoints/e028_h0125_m4_campaign_checkpoint.npz` stopped before solving because its saved platform was `macOS-26.5.1-arm64-arm-64bit-Mach-O` while the current platform was `macOS-26.5.2-arm64-arm-64bit-Mach-O`. Python and all numerical package versions matched. The original checkpoint remained unchanged at SHA-256 `8dd454c10583f0cfe4287d7938228b5e41023e4121320c2f2b6ab35aa55b9db3`; the comparison was not bypassed. A fresh current-runtime replay through `2/12` produced a bitwise-identical field with SHA-256 `3219171452d92fa1e6f027623a318e6aed11bfe9e463a7a6e55c262251270290`; the retained replay artifact SHA-256 is `1cd31cc2c634c7f75bd56330c8c4f2da076fd3204bba5fd1831bb0d99c1abaa5`. This separates runtime drift from numerical drift before continuing.
- **Strict stage result:** The separately fingerprinted current-runtime lineage closes `3/12` from the plain accepted `2/12` field in seven full Newton corrections and `280` GMRES inner iterations. Maximum direct true-residual ratio is `9.1512e-9`, maximum per-correction inner count is `56`, all `info` values are zero, and final nonlinear relative `L2/Linf` are `7.01069e-12 / 1.81747e-10`. Wide pair/spatial/time are `0.05654223 / 0.11308446 / 1.00000033`; fixed/centered spatial minima are `0.11277736 / 0.11325609` at `(5.375,0.125)`, with no nonpositive nodes or conflict.
- **Full discrete `Gamma_2` audit:** Active shifted minima are `sigma_1=0.75000017`, pair sum `0.05654223`, and `sigma_2=0.18749999993`; fixed/centered shifted-`sigma_2` minima are `0.11611764 / 0.11613725`, all with zero nonpositive nodes. The active raw-`sigma_2` residual against the shifted right-hand side is at most `8.34e-10`, and raw `sigma_2` agrees with the active monotone extension to `8.88e-16`. The old warning point `(6.25,0.75)` remains positive: fixed/centered spatial-principal `0.231478 / 0.230306` and shifted-`sigma_2=0.174109 / 0.173219`. These are post-hoc discrete checks, not an implementation-enforced gate or continuum proof.
- **Partial-source observables:** At amplitude `0.25`, ratio at `r/r0=1` is `1.422741`; maximum finite ratio is `1.439194`; maximum sampled nonlinear gradient is `3.919218` at the fixed-ray endpoint `r=12`; centered original/White volume residuals are `0.96917% / 0.27903%`; and sampled-charge flux deficits are `-0.74787% / -0.74159% / -0.72356%`. Sampled versus nominal charge differs by `-4.31633e-6`. These are one-quarter-source observables, not refinements of the full-source E-026 values.
- **Same-amplitude control and nonuniform trend:** A fresh coarse `(0.25,3)` `3/12` control closes in five Newton corrections and `132` GMRES iterations. On the fine grid, ratio and endpoint gradient rise only `0.447% / 0.382%`; common-physical-window original/White residuals fall `40.99% / 45.91%`; worst flux-deficit magnitude falls `38.33%`; global fixed/centered spatial minima rise `6.84% / 7.66%`; and global shifted-`sigma_2` minima rise `35.8% / 36.3%`. Yet shifted-`sigma_2` at the old warning point falls `8.31% / 7.67%`, and stage-3 GMRES work rises `112%`. Two coupled grids therefore support branch reach and improving integrated diagnostics, not uniform monotone convergence, an asymptotic order, or mesh-independent work.
- **Centered-difference sensitivity:** A common `r<=78.5` audit with fine physical difference steps `0.125`, `0.25`, and `0.5` keeps centered shifted-`sigma_2` positive at `0.11614 / 0.12589 / 0.15801` and spatial-principal positive at `0.11326 / 0.11422 / 0.11650`. The warning-point `sigma_2` is `0.17322 / 0.16480 / 0.19989`. Positivity is therefore robust over this bounded postprocessor-scale scan. Quantitative refinement trends are not: at matched physical step `0.25`, fine versus coarse warning-point `sigma_2` falls `12.15%`, while at step `0.5` it rises `4.77%`; residual trends also vary with step. Do not treat a single centered difference step as an independent continuum certificate.
- **Newton-iterate scope and stage-4 scratch warning:** Froese-Oberman-Salvador Proposition 2.6 algebraically characterizes `Gamma_2` through pair-sum and `sigma_2` conditions for curvature triples; nonnegative right-hand side supplies the `sigma_2` condition only at an exact discrete root. Their Section 3.4 monotone extension is deliberately defined on all curvature triples, their Newton Jacobian includes the outside-cone branch, and their convergence theorem concerns solutions of the discrete scheme rather than every nonlinear iterate. A scratch `4/12` first correction therefore remains a valid core wide-Newton step even though its independent postprocessors leave `Gamma_2`: full damping reduces residual `0.25 -> 0.01730`, with wide spatial/time `0.05110 / 0.99863`, but fixed/centered spatial become `-0.03252 / -0.03210` and shifted-`sigma_2=-0.04482 / -0.04426` near `(6.25,0.375)`. The second full correction returns those checks positive while residual reaches `0.001701`. This transient does not prove the root branch crossed the cone and does not reject a final passing root; it does forbid treating every accepted Newton iterate as an admissible physical/root state or importing Awanou's different-scheme admissible-neighborhood theorem.
- **Damping and checkpoint consequence:** Along the exact first `4/12` direction, fixed shifted-`sigma_2` is the earliest independent zero at `alpha~=0.812368`; centered shifted-`sigma_2`, fixed spatial, and centered spatial cross at approximately `0.813667`, `0.817634`, and `0.818990`. `alpha=0.8` passes with little margin; the dyadic `alpha=0.5` has fixed/centered spatial `0.05650 / 0.05643` and shifted-`sigma_2=0.06927 / 0.06917`. The present line search correctly accepts `alpha=1` under its defined Armijo plus wide gates, then stores an explicitly incomplete checkpoint before any independent postprocessing. That is computationally coherent but operationally delicate. Preserve the accepted stage-3 checkpoint immutably, run stage 4 from a byte-identical working copy, never quote an in-progress state, and restart from stage 3 after interruption. A per-iterate independent-cone line search would be a separately fingerprinted extra safeguard, not a cited-theorem requirement.
- **Artifacts and resource scope:** Current-runtime stage-3 field/report/artifact/checkpoint SHA-256 values are `b2fcb751e8fb039d5031ddc9a5b6bd7245d13eae446d50663b652a5ba172d8ba`, `4d5d14daea28a0b07ab2ba72b5556ef293f2258822136c8ce2d5ed1d1774ae9f`, `d44f43e9aa6f3e3542df570cd9999da7c6294858922dbad18af7df1798f64fef`, and `368f569bd18cbcb0fdc443ce49703078b52953dd59155869334c10a2f3b8013c`. The report's `1.604 GiB` RSS is invocation-local; the current replay campaign high-water is `1.832 GiB`, the prior runtime lineage reached `1.836 GiB`, and explicitly counted A/P/R storage peaks at `72.6 MB` decimal. Artifact existence alone is not acceptance: the driver can write a requested-final-stage artifact before a later invocation would enforce a fixed/centered conflict, and shifted-`sigma_2` remains manual.
- **Impact on hypotheses:** H-019 remains `Medium-low`. E-028 reaches a clean discrete `3/12`, but full source, another coupled refinement, fixed-observable outer-box stability, density/asymmetry, target response, EFT, and reaction accounting remain blocked. The exact center is force-free, the fiducial physical acceleration remains about `6e-35 m/s^2`, and no artificial-gravity, inertial-control, FTL, or propulsion conclusion follows.

### E-028 `4/12` Endpoint, Same-Amplitude, and Cone-Preserving-Path Audit

- **Links:** Froese, Oberman, and Salvador, https://arxiv.org/abs/1502.04969 and https://doi.org/10.1093/imanum/drw007; Finlay and Oberman, https://arxiv.org/abs/1807.05150 and https://doi.org/10.1137/18M1200269; Awanou, https://arxiv.org/abs/1406.5366; Sala and Tuminaro, https://doi.org/10.1137/060659545; internal calculation and artifacts dated 2026-07-23.
- **Type:** primary numerical-analysis source audit plus integrity-checked nonlinear continuation, full discrete-cone postprocessing, same-amplitude grid control, and alternate solver-path sensitivity.
- **Quality and scope:** High for the exact saved arrays, residuals, hashes, and fixed-grid comparisons; high for the cited sources under their stated assumptions; indirect for the cylindrical reflected-axis/curved-boundary discretization; no evidence that nature realizes the cubic-Galileon model.
- **Source conclusion on the transient:** The literature does not require every Newton iterate of the extended monotone operator to remain in `Gamma_2`, so the known fixed/centered excursion on the first full correction does not by itself reject a final passing root. The wide operator itself stays within its recorded pair-sum gate. Conversely, no cited result proves that endpoint recovery excludes a discrete branch jump, supplies uniqueness for this adapted continuation, or transfers the Cartesian convergence theorem to E-028. Awanou's local result assumes a sufficiently close seed and a smooth nondegenerate uniformly elliptic neighborhood; Sala-Tuminaro addresses linear preconditioning, not nonlinear branch selection.
- **Strict canonical result:** A byte-identical copy of accepted stage 3 reaches `4/12` in six full Newton corrections and `237` GMRES inner iterations. Maximum direct true-residual ratio is `8.4466e-9`, maximum per-correction inner count is `56`, every `info` is zero, and final nonlinear relative `L2/Linf` are `6.8085e-9 / 1.6343e-7`. Wide pair/spatial/time are `0.0355105 / 0.0710210 / 1.00000176`; fixed/centered spatial minima are `0.0702601 / 0.0704617`, with no nonpositive nodes or conflict.
- **Full endpoint `Gamma_2` audit:** Active shifted minima are `sigma_1=0.75000088`, pair `0.03551049`, and `sigma_2=0.18749900`. Fixed minima are `0.75002107 / 0.03513004 / 0.08547619`; centered native-step minima are `0.75001970 / 0.03523084 / 0.08535728`. Every nonpositive count is zero. Centered `sigma_2` stays positive at difference steps `0.125/0.25/0.5`, with minima `0.085357 / 0.096137 / 0.143379`. Active raw `sigma_2` agrees with the monotone extension to `8.88e-16`; the maximum absolute pointwise shifted-source residual is `9.99e-7`.
- **Tracked locations:** At `(6.25,0.75)`, fixed/centered spatial and shifted-`sigma_2` are `0.172158 / 0.170948` and `0.159439 / 0.158315`. At the transient `(6.25,0.375)` location, they are `0.120895 / 0.120187` and `0.176205 / 0.175171`. Both are positive at the completed endpoint.
- **Partial-source observables:** At one-third source, ratio at `r/r0=1` is `1.809541`; maximum finite sampled ratio is `1.894623`; maximum sampled nonlinear gradient is `4.940985` at the fixed-ray endpoint `r=12`; native-step centered original/White residuals are `1.03375% / 0.25724%`; and fixed-sphere sampled-charge flux deficits are `-0.84453% / -0.85054% / -0.83862%`. The endpoint location on the ray must not be relabeled a resolved global peak.
- **Same-amplitude control:** A fresh coarse `(h,m)=(0.25,3)` `4/12` control closes in five Newton and `136` GMRES iterations. Fine versus coarse changes are `+0.0756%` in ratio, `+0.3673%` in endpoint gradient, `-30.61% / -47.84%` in matched-`0.25`-step common-window original/White residuals, `-37.97%` in worst fixed-sphere flux-deficit magnitude, `+4.72% / +6.65%` in fixed/centered spatial minima, and `-93.66%` in source-charge-error magnitude. Fine stage GMRES work rises `74.26%`. The integrated trends improve, but two coupled grids cannot establish an asymptotic order or mesh-independent work.
- **Cone-preserving path sensitivity:** Replacing the first full correction by `alpha=0.5` leaves active/fixed/centered shifted `sigma_2=0.143383 / 0.069270 / 0.069172`. Six later accepted corrections were manually hard-stopped on active/fixed/centered `sigma_1`, pair, and `sigma_2`; all remained positive. This route reaches the canonical endpoint to relative field `L2=4.89e-12` and maximum absolute difference `4.56e-8`, while closing to a tighter residual `2.57e-12`. That strongly supports one fixed-grid root and identifies the full-step excursion as solver-path dependent; it does not prove a unique continuum-admissible homotopy branch.
- **Artifacts and resources:** Accepted checkpoint, artifact, field, and report SHA-256 values are `8cd1abd9f43b9076d6fb884933d055c4746fb0c37e8fd6d596840b7353c13ec4`, `4ddd280ba9b4ada9ebdb1963d92904813047577e48c750134df36ff9c06f58c1`, `ec8fdb4f4050b11affb0194b4bb2eff68ab7e9ae3cf8371d54e3bf442bb7ae53`, and `8b2c9ee855b2216862012434a16d87777d053bbd8cd0e11e8779d39ed3e4a4db`. Invocation-local peak RSS is `1.621 GiB`; campaign high-water remains about `1.832 GiB`; maximum explicit A/P/R storage is `72,586,832` bytes.
- **Impact on hypotheses:** H-019 remains `Medium-low`. E-028 reaches a reproducible one-third-source discrete endpoint with improving same-amplitude diagnostics and a cone-preserving same-root sensitivity. Full source, another coupled refinement, fixed-observable outer-box stability, density/asymmetry, target response, EFT, reaction accounting, useful gravity, inertial control, FTL, and propulsion remain blocked.

### Continuation Branch Identity: Local IFT, Practical Jumping, and Interval Certification

- **Links:** Hannes Uecker, *Continuation and Bifurcation in Nonlinear
  PDEs--Algorithms, Applications, and Experiments*,
  https://doi.org/10.1365/s13291-021-00241-5; R. Baker Kearfott and Zhaoyun
  Xing, *An Interval Step Control for Continuation Methods*,
  https://doi.org/10.1137/0731048.
- **Type:** open peer-reviewed continuation survey and primary
  interval-numerics paper.
- **Quality:** high for their stated finite-dimensional/PDE-discretization
  continuation claims; indirect for E-028 because its semismooth wide
  operator, cylindrical construction, and `322319`-unknown implementation
  are not interval enclosed.
- **Relevant claim:** Uecker states the standard local boundary precisely.
  If `G_u` is invertible at a solution, the implicit function theorem gives a
  sufficient certificate for a locally unique solution graph within some
  neighborhood. Singular `G_u` removes that certificate and is necessary,
  but not sufficient, for bifurcation. The survey's patterned-PDE examples
  document uncontrolled branch jumping as a practical problem for nearby
  branches, especially near bifurcation points. Kearfott and Xing provide one
  stronger “same curve” route: under their smooth finite-dimensional
  assumptions, successful interval tests verify corrector convergence to the
  same curve and uniqueness of the traversing curve segment in a constructed
  interval box.
- **Impact on E-028:** Small residuals, positive endpoint/path cones,
  near-collinear stage increments, and a close secant predictor are useful
  fixed-grid evidence, but none supplies an inverse bound, identifies an IFT
  neighborhood, or rigorously encloses a unique continuation segment. E-028
  must therefore say “smooth sampled fixed-grid continuation” rather than
  “proved same branch.” A matrix-free spectral/inverse-norm diagnostic could
  be a future warning indicator. A comparable validated enclosure or an
  independent analytic uniqueness argument would be needed for a rigorous
  no-jump claim.

### E-028 `5/12` Endpoint, Accepted-Path, Margin-Tail, and Same-Amplitude Audit

- **Links:** Froese, Oberman, and Salvador,
  https://arxiv.org/abs/1502.04969 and
  https://doi.org/10.1093/imanum/drw007; Finlay and Oberman,
  https://arxiv.org/abs/1807.05150 and
  https://doi.org/10.1137/18M1200269; Uecker,
  https://doi.org/10.1365/s13291-021-00241-5; Kearfott and Xing,
  https://doi.org/10.1137/0731048; Parsiad Azimzadeh,
  https://doi.org/10.1090/mcom/3347 and
  https://arxiv.org/abs/1701.06951; internal calculation and artifacts dated
  2026-07-24.
- **Type:** primary/high-quality numerical-analysis audit plus an
  integrity-checked nonlinear continuation, accepted-iterate replay,
  independent full-cone reconstruction, distributional margin check, and
  fresh same-amplitude grid control.
- **Strict canonical result:** A byte-identical copy of accepted stage 4
  reaches `5/12` in five full Newton corrections and `217` GMRES inner
  iterations. Maximum direct true-residual ratio is `9.47315e-9`, maximum
  per-correction inner count is `50`, all `info` values are zero, and final
  nonlinear relative `L2/Linf` are `4.82226e-8 / 1.45898e-6`. Wide
  pair/spatial/time are
  `0.02505673 / 0.05011347 / 1.00000038`; fixed/centered spatial minima are
  `0.05011347 / 0.05024332`, with no conflict.
- **Endpoint full-`Gamma_2` audit:** Active shifted
  `sigma_1/pair/sigma_2` minima are
  `0.75000019 / 0.02505673 / 0.18748885`. Fixed minima are
  `0.75003000 / 0.02505673 / 0.06204966`; centered native-step minima are
  `0.75002774 / 0.02512166 / 0.06180786`. Every nonpositive count is zero.
  Centered `sigma_2` stays positive at physical steps `0.125/0.25/0.5`,
  with minima `0.06180786 / 0.07887984 / 0.13411076`. Active raw
  `sigma_2` agrees with the monotone extension to `8.88e-16`; maximum
  pointwise shifted-source residual is `1.11518e-5`.
- **Accepted-path replay:** A fresh deterministic canonical replay ends at a
  field bitwise identical to
  the retained field and repeats exactly five Newton and `217` GMRES
  iterations. All accepted states pass the three tested
  active/fixed/centered full-cone reconstructions. The smallest accepted-state
  or sampled-segment fixed pair/`sigma_2` are
  `0.01260698 / 0.02988896`; centered values are
  `0.01912254 / 0.05206855`. Analytic segment `sigma_1`/`sigma_2` minima,
  sampled pair margins, and Gårding-cone convexity support positive
  piecewise-affine connecting segments. The fixed reconstruction shares
  wide-operator ingredients; the centered postprocessor is separate. This
  removes the stage-4-style path conflict for this one step; it is not an
  interval uniqueness certificate.
- **Partial-source observables:** At `5/12`, ratio at `r/r0=1` is
  `2.233660`; maximum finite ratio is `2.466898`; maximum sampled nonlinear
  gradient is `5.881391` at the fixed ray endpoint `r=12`; native centered
  original/White residuals are `1.07590% / 0.24137%`; and fixed-sphere
  sampled-charge flux deficits are
  `-0.91107% / -0.92872% / -0.92223%`. Sampled source-charge error is
  `-4.31633e-6`. The endpoint gradient is not a resolved global peak.
- **Same-amplitude control:** A fresh coarse `(h,m)=(0.25,3)` stage-5
  control closes in four Newton and `123` GMRES iterations. Fine versus
  coarse changes are `+0.619%` in ratio, `+0.341%` in endpoint gradient,
  `-29.79% / -47.50%` in matched-step common-window original/White
  residuals, `-37.94%` in worst flux-deficit magnitude, `-93.66%` in
  source-charge-error magnitude, and `+2.16% / +1.78%` in fixed/centered
  spatial margins. Fine stage GMRES rises `76.42%`. These are encouraging
  two-grid comparisons, not asymptotic orders.
- **Margin-tail result:** At matched centered step `0.25`, stages
  `3/12,4/12,5/12` have pair minima
  `0.05711,0.03590,0.02525`, pair `0.01%` weighted quantiles
  `0.11887,0.09529,0.08334`, and common-window axisymmetric
  nodal-quadrature weight fractions below pair margin `0.05` of
  `0,2.60e-5,5.26e-5`. At stage 5, `182/310365` masked nodes
  (`5.864e-4` unweighted; `179` positive-weight nodes) lie below the pair
  threshold. The corresponding `sigma_2` minima are
  `0.12589,0.09614,0.07888`, with zero sampled weighted fraction below
  `0.05` at stage 5. The full-window denominator is dominated by outer
  vacuum, and cylindrical weights suppress low-`rho` nodes. Cone-margin
  erosion is localized under that measure, but a thin connected strip or a
  larger source-layer-relative tail is not excluded; report minima, weighted
  tails, and node counts.
- **Continuation sensitivity:** Stage-3-to-4 and stage-4-to-5 tangent
  mismatch proxies are `0.06048 / 0.04821`; consecutive weighted increment
  cosine is `0.999903`; and a stage-4 secant predictor remains
  wide-admissible but misses stage 5 by `4.166%` of the final increment.
  This supports a smooth sampled discrete path without proving `G_u`
  invertible or excluding nearby branches.
- **Selected endpoint Jacobian:** Azimzadeh's peer-reviewed criterion makes
  the active-matrix sign/graph audit interpretable. At stages 4 and 5,
  computed `A=-J` has positive diagonal, nonpositive off-diagonals, one
  strongly connected graph component, all `322319` rows weakly diagonally
  dominant to `1e-12`, and `3092 / 3069` strict rows; Frobenius asymmetry is
  `0.09217 / 0.09083`. Thus each selected endpoint matrix has the numerical
  pattern of an irreducibly diagonally dominant nonsingular M-matrix. This
  does not complete the IFT hypothesis: four nodes at each endpoint have
  active-candidate gaps `<=1e-12` (including exact ties), so the min operator
  is semismooth there; other generalized-Jacobian selections, inverse norms,
  rounding validation, and the intervening source interval were not
  certified.
- **Artifacts and resources:** Accepted checkpoint, artifact, field, and
  report SHA-256 values are
  `4c2c10a53156c59b53abbc5963d9089f460c75e65b6cdc4fa1cb64d4f548977f`,
  `a72166c722c947dad9da93b505fa1335633adf23bd61c33a7dfa9968b6215c84`,
  `ab5b23f15f729cb0f72589c2287e1013f8f6b05a7dbe91ad6b1debffe272f5c7`,
  and
  `7207528839fcdd909ed19467e6de349374c09ff2fcbd7a97e9780e568f2174c0`.
  Invocation-local peak RSS is `1.135 GiB`; campaign high-water remains
  about `1.832 GiB`; maximum explicit A/P/R storage remains `72,586,832`
  bytes.
- **Impact on hypotheses:** H-019 remains `Medium-low`. E-028 reaches a
  reproducible five-twelfths-source discrete endpoint with a cone-positive
  replayed accepted path and improving integrated same-amplitude diagnostics.
  The remaining seven source stages, another coupled refinement, fixed-box
  comparison, density/asymmetry, target response, EFT validity, reaction
  accounting, useful gravity, inertial control, FTL, and propulsion remain
  blocked.

### E-028 `6/12` Endpoint, Connected-Tail, Tie-Vertex, and Same-Amplitude Audit

- **Links:** Froese, Oberman, and Salvador,
  https://arxiv.org/abs/1502.04969 and
  https://doi.org/10.1093/imanum/drw007; Finlay and Oberman,
  https://arxiv.org/abs/1807.05150 and
  https://doi.org/10.1137/18M1200269; Awanou,
  https://arxiv.org/abs/1406.5366 and
  https://doi.org/10.4310/MAA.2018.v25.n1.a3; Qi and Sun,
  https://doi.org/10.1007/BF01581275; Azimzadeh,
  https://arxiv.org/abs/1701.06951 and
  https://doi.org/10.1090/mcom/3347; Kearfott and Xing,
  https://doi.org/10.1137/0731048; internal calculation and artifacts dated
  2026-07-25.
- **Type and transfer boundary:** Primary/high-quality numerical-analysis
  sources plus an integrity-checked nonlinear continuation, deterministic
  accepted-path replay, independent full-cone reconstruction, connected-tail
  audit, exhaustive observed tie-vertex enumeration, and fresh
  same-amplitude grid control. Froese-Oberman-Salvador's continuum result
  couples `h`, angular resolution, and stencil reach within its Cartesian
  monotone framework; Finlay-Oberman likewise makes spatial and angular
  refinement inseparable. Neither theorem automatically transfers to
  E-028's cylindrical reflected-axis/curved-boundary construction. Awanou's
  local uniqueness result assumes a smooth nondegenerate solution, a
  sufficiently close seed, and sufficiently small `h`. Qi-Sun require
  nonsingularity of every generalized Jacobian for their local semismooth
  Newton conclusion, while Kearfott-Xing obtain a no-jump certificate only
  through a successful interval enclosure. The calculations below satisfy
  none of those full hypotheses and provide no evidence that nature realizes
  the cubic-Galileon model.
- **Provenance failure and fresh replay:** Strict resume from accepted stage 5
  stopped before solving because the saved `requirements-research.txt`
  fingerprint was
  `cd1df48db71c...`, whereas the committed file fingerprint is
  `b44e38d9b107...`; numerical package versions and the runtime otherwise
  matched. The guard was not bypassed and the accepted checkpoint remained
  immutable. A fresh current-provenance replay through `5/12` took
  `164.61 s` and produced a field bitwise identical to accepted stage 5
  (maximum absolute difference zero; field SHA-256
  `ab5b23f15f729cb0f72589c2287e1013f8f6b05a7dbe91ad6b1debffe272f5c7`).
  The retained replay artifact SHA-256 is
  `b3adf0714c96815ece3782232dafa5b623e6fc7dcdfeaae4239e1f52267f2ab4`.
  This establishes numerical continuity across a provenance change without
  weakening the recorded loader policy.
- **Strict stage result:** The current-provenance lineage advances from the
  replayed stage 5 field to `6/12` in five full Newton corrections and
  `254` GMRES inner iterations (`52,59,48,56,39`). Every step length is one,
  every `info` is zero, maximum direct true-residual ratio is
  `9.15407e-9`, and final nonlinear relative `L2/Linf` are
  `5.45884e-8 / 1.78440e-6`. Wide pair/spatial/time minima are
  `0.01921756 / 0.03843512 / 1.00000237`; fixed/centered spatial minima are
  `0.03306351 / 0.03278356` at `(6.0,0.5)`, with zero nonpositive counts.
  The campaign totals through stage 6 are `42` Newton corrections and
  `1685` GMRES inner iterations.
- **Endpoint full-`Gamma_2` audit:** Active shifted
  `sigma_1/pair/sigma_2` minima are
  `0.75000118 / 0.01921756 / 0.18748363`. Fixed minima are
  `0.75004236 / 0.01653175 / 0.04252053`; centered native-step minima are
  `0.75003875 / 0.01639178 / 0.04215838`. All three reconstructions have
  zero nonpositive counts. Centered common-window `sigma_2` remains positive
  at physical steps `0.125/0.25/0.5`, with minima
  `0.04215838 / 0.06645977 / 0.12729943`. Active raw `sigma_2` agrees with
  the monotone extension to `1.78e-15`; maximum pointwise shifted-source
  residual is `1.63670e-5`. The tracked points `(6.25,0.75)` and
  `(6.25,0.375)` remain positive in active, fixed, and centered
  reconstructions; these are finite-grid postprocessors, not interval
  bounds.
- **Accepted-path replay:** A deterministic replay ends at a field bitwise
  identical to the retained endpoint and exactly repeats five Newton and
  `254` GMRES iterations. All accepted states and nine sampled points on
  every piecewise-affine correction segment remain positive in the tested
  active/fixed/centered `Gamma_2` reconstructions. The smallest sampled
  `sigma_1/pair/sigma_2` values occur on the first correction:
  `0.74954661 / 0.01744492 / 0.12225661` active,
  `0.74954222 / 0.00225488 / 0.00494198` fixed, and
  `0.74953072 / 0.00223272 / 0.00488522` centered. The endpoint later
  recovers margin. This is a close but positive sampled solver path, not a
  rounded interval certificate or proof that no branch jump occurred.
- **Connected margin tail:** At matched centered step `0.25` on the common
  `r<=78.5` window, stages `3/12,4/12,5/12,6/12` have pair minima
  `0.05711,0.03590,0.02525,0.01937` and pair `0.01%` weighted quantiles
  `0.11887,0.09529,0.08334,0.07520`. At stage 6, `227/310365` nodes lie
  below pair margin `0.05` (`223` with positive quadrature weight):
  the full-window weighted fraction is `6.535e-5`, but the
  source-support-relative and source-transition-relative fractions are
  `0.003139 / 0.003339`. Those nodes form one connected component from
  `rho=0` to `6.25` and `z=0` to `0.75`, reaching the inner source
  smoothing layer. Threshold scans find `10` nodes below `0.02`, `118`
  below `0.03`, `177` below `0.04`, and `263` below `0.06`; the matched
  centered `sigma_2` minimum is `0.06646`, with only five nodes below
  `0.08`. The tail is therefore geometrically thin but connected and more
  prominent relative to the source layer than the outer-vacuum-dominated
  full-window denominator suggests.
- **Continuation and generalized-Jacobian audit:** Tangent-equation mismatch
  proxies decrease `0.06048 -> 0.04821 -> 0.04005` over stages 4--6;
  consecutive weighted increment cosines are
  `0.999903 / 0.999935`, while secant misses at stages 5 and 6 are
  `4.166% / 3.659%` of the new increments. This supports a smooth sampled
  fixed-grid path only. At stage 6, four exact active-frame ties occur on
  the axis at `z=7.75,7.875,8.0,8.125` between frames 8 and 11. Exhausting
  all `2^4=16` selections yields one bitwise-identical matrix (SHA-256
  `68710ffa7e9c26d961c7401e070bee8962d587bd7dd42c48cbfe8e251ea89211`).
  For sign-normalized `A=-J`, all `322319` diagonal entries are positive,
  no off-diagonal is positive, the graph has one strongly connected
  component, all rows are weakly diagonally dominant to tolerance, and
  `3047` rows are strict; Frobenius asymmetry is `0.09127`. Azimzadeh's
  criterion supports nonsingularity of this observed endpoint matrix
  pattern. It does not supply an inverse norm, rounding enclosure, all
  nearby-source generalized Jacobians, or a continuum uniqueness result,
  so the Qi-Sun and no-jump hypotheses remain incomplete.
- **Partial-source observables:** At one-half source, ratio at `r/r0=1` is
  `2.604856`; maximum finite sampled ratio is `3.022631`; and maximum
  sampled nonlinear gradient is `6.756110` at the diagnostic ray endpoint
  `r=12`, not a resolved global peak. Native-step centered original/White
  residuals are `1.10908% / 0.22880%`; fixed-sphere sampled-charge flux
  deficits are `-0.96279% / -0.99095% / -0.98878%`; sampled source-charge
  error is `-4.31633e-6`.
- **Same-amplitude control:** A fresh coarse `(h,m)=(0.25,3)` `6/12`
  control closes in five full Newton corrections and `174` GMRES iterations
  after exactly reproducing all earlier coarse stage counts. Fine versus
  coarse changes are `+1.728%` in ratio, `+0.321%` in endpoint gradient,
  `-29.19% / -47.15%` in matched-step common-window original/White
  residuals, `-37.87%` in worst flux-deficit magnitude, and `-93.66%` in
  source-charge-error magnitude, while stage GMRES work rises `45.98%`.
  Wide pair/spatial margins rise `0.878%`, but native fixed/centered spatial
  and `sigma_2` minima decline; at matched physical step `0.25`, the
  centered spatial margin rises only `1.327%` and fine centered
  `sigma_2=0.06646` versus coarse `0.04704`. These are mixed, encouraging
  two-grid trends, not an asymptotic convergence order.
- **Artifacts and resources:** Accepted checkpoint and byte-identical
  retained work-snapshot SHA-256 are
  `ff82363833c84e416e020a8df56d6067b6b1f7612c41f30f6499d6b95690babb`.
  Stage-6 artifact, field, and report SHA-256 values are
  `64a0fca132dd6b068c543f102c74c3ffa09a545509d9f822857cc13e179c5476`,
  `cd806ff41c0a33d541cc5c1dba44a3c7ad693ddb6b81dda5eae2ac1db8757c3e`,
  and
  `fe2c11e1d2e7806b12836325eaaed565137b5495efbb25417f4c6545fd3a256c`.
  Peak RSS is `1.614 GiB`; maximum explicitly counted A/P/R storage remains
  `72,586,832` bytes.
- **Impact on hypotheses:** H-019 remains `Medium-low`. E-028 now reaches a
  reproducible half-source discrete endpoint with a strictly replayed
  positive sampled correction path, improving integrated same-amplitude
  diagnostics, and no selection ambiguity at the four observed endpoint
  ties. Margin erosion is nevertheless a connected source-layer feature,
  and neither endpoint matrix structure nor two grids supplies continuum
  admissibility, uniqueness, or a no-jump theorem. The remaining six source
  stages, another coupled refinement, fixed-box comparison,
  density/asymmetry, target response, EFT validity, reaction accounting,
  useful gravity, inertial control, FTL, and propulsion remain blocked.
