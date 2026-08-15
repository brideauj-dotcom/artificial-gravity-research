import json
import math
from pathlib import Path
import tempfile
import unittest

import models.e043_ehd_liquid_film_audit as e043


class E043EhdLiquidFilmAuditTests(unittest.TestCase):
    def test_novec_correlations_and_charge_relaxation_are_reproducible(self) -> None:
        properties = e043.novec_properties(15.0)
        self.assertTrue(
            math.isclose(properties["density_kg_m3"], 1503.92465, rel_tol=1e-12)
        )
        self.assertTrue(
            math.isclose(properties["relative_permittivity"], 7.0069, rel_tol=1e-12)
        )
        self.assertTrue(
            math.isclose(
                properties["conductivity_s_m"],
                1.35810680692499e-8,
                rel_tol=1e-12,
            )
        )
        self.assertTrue(
            math.isclose(
                properties["charge_relaxation_time_s"],
                0.004568056966039969,
                rel_tol=1e-10,
            )
        )

    def test_helpers_reject_invalid_physical_inputs(self) -> None:
        with self.assertRaises(ValueError):
            e043.novec_properties(62.0)
        with self.assertRaises(ValueError):
            e043.electric_field_v_m(1000.0, 0.0)
        with self.assertRaises(ValueError):
            e043.electric_field_v_m(-1.0, 1.0)
        with self.assertRaises(ValueError):
            e043.maxwell_energy_density_pa(-1.0, 1.0)
        with self.assertRaises(ValueError):
            e043.hydrostatic_pressure_pa(1000.0, -1.0)
        with self.assertRaises(ValueError):
            e043.electric_field_v_m(math.nan, 1.0)
        with self.assertRaises(ValueError):
            e043.electric_field_v_m(1.0, math.inf)
        with self.assertRaises(ValueError):
            e043.novec_properties(math.nan)

    def test_field_and_pressure_scales_use_published_geometry(self) -> None:
        audit = e043.field_and_pressure_audit()
        fields = audit["derived_fields"]
        scales = audit["same_unit_pressure_scales"]
        self.assertTrue(
            math.isclose(
                fields["ehd_gap_average_field_v_m"],
                5_905_511.811023622,
                rel_tol=1e-12,
            )
        )
        self.assertEqual(fields["dep_gap_average_field_v_m"], 1_250_000.0)
        self.assertTrue(
            math.isclose(
                scales[
                    "reconstructed_2mm_hydrostatic_from_15c_correlation_pa"
                ],
                29.507001633,
                rel_tol=1e-12,
            )
        )
        self.assertTrue(
            math.isclose(
                scales["pump_equivalent_acceleration_g_across_2mm_film"],
                1.6945130725882045,
                rel_tol=1e-12,
            )
        )
        self.assertTrue(
            math.isclose(
                scales["pump_pressure_to_ehd_gap_maxwell_ratio"],
                0.043763664274168,
                rel_tol=1e-12,
            )
        )

    def test_pressure_anchor_is_not_mislabeled_as_integrated_force(self) -> None:
        audit = e043.field_and_pressure_audit()
        limits = audit["provenance_limits"]
        self.assertFalse(limits["pump_pressure_measured_in_this_experiment"])
        self.assertFalse(
            limits["pump_reference_voltage_matches_data_guide_flights_1_and_3"]
        )
        self.assertFalse(limits["pump_flow_rate_reported"])
        self.assertFalse(limits["hydraulic_power_recoverable"])
        self.assertFalse(limits["comsol_field_or_mesh_released"])
        self.assertFalse(limits["integrated_total_electrode_force_recoverable"])
        self.assertIn("scale anchors", limits["warning"])
        self.assertFalse(audit["published_geometry"]["flight_heater_area_consistent"])
        self.assertIn("2.520 cm2", limits["geometry_warning"])

    def test_force_law_and_electrothermal_sensitivity_are_explicit(self) -> None:
        audit = e043.electromechanics_and_thermal_confounder_audit()
        definitions = audit["electroquasistatic_definitions"]
        self.assertIn("rho_free*E", definitions["korteweg_helmholtz_body_force"])
        self.assertIn("surface_integral", definitions["integrated_force_identity"])
        self.assertIn("never both", definitions["sharp_interface_rule"])
        self.assertFalse(audit["recoverability"]["volume_body_force_recoverable"])
        sensitivity = audit[
            "declared_15k_parallel_gradient_sensitivity_not_psi_measurement"
        ]
        self.assertTrue(
            math.isclose(
                sensitivity["dc_thermocharge_coulomb_pressure_scale_pa"],
                47.310841204496924,
                rel_tol=1e-12,
            )
        )
        self.assertIn("50 Pa", sensitivity["interpretation"])
        joule = audit["joule_heating_characteristic_not_volume_integral"]
        self.assertTrue(
            math.isclose(
                joule["uniform_1cm2_by_1p6mm_example_w"],
                0.0033952670173124752,
                rel_tol=1e-12,
            )
        )

    def test_bubble_dep_force_reproduces_reported_buoyancy_ratio(self) -> None:
        audit = e043.bubble_force_audit()
        scales = audit["reconstructed_scales"]
        self.assertTrue(
            math.isclose(
                scales[
                    "liquid_minus_vapor_density_inferred_from_reported_buoyancy_kg_m3"
                ],
                1465.0042162277155,
                rel_tol=1e-12,
            )
        )
        self.assertTrue(
            math.isclose(
                scales["dep_to_buoyancy_ratio"],
                9.136212624584719,
                rel_tol=1e-12,
            )
        )
        self.assertTrue(
            math.isclose(
                scales["displaced_liquid_mass_from_15c_correlation_kg"],
                6.299624842656802e-9,
                rel_tol=1e-12,
            )
        )
        self.assertTrue(
            math.isclose(
                scales["dep_force_per_displaced_liquid_mass_in_g"],
                8.899774343996196,
                rel_tol=1e-12,
            )
        )
        self.assertNotEqual(
            scales["dep_force_per_displaced_liquid_mass_in_g"],
            scales["dep_to_buoyancy_ratio"],
        )
        self.assertTrue(
            math.isclose(
                scales["implied_gradient_e_squared_v2_m3"],
                3.2982889267786145e15,
                rel_tol=1e-12,
            )
        )
        self.assertTrue(
            math.isclose(
                scales["maxwell_wagner_frequency_hz"],
                30.902061225114938,
                rel_tol=1e-12,
            )
        )

    def test_capillary_scale_is_preserved_as_a_confounder_not_a_detachment_model(self) -> None:
        audit = e043.bubble_force_audit()
        scales = audit["reconstructed_scales"]
        self.assertTrue(
            math.isclose(
                scales["capillary_circumference_force_scale_n"],
                8.545132017764094e-6,
                rel_tol=1e-12,
            )
        )
        self.assertTrue(
            math.isclose(
                scales["bubble_radius_to_dep_grate_feature_width"],
                0.1968503937007874,
                rel_tol=1e-12,
            )
        )
        self.assertTrue(
            math.isclose(
                scales["dep_to_capillary_circumference_scale"],
                0.0643641313974545,
                rel_tol=1e-12,
            )
        )
        self.assertTrue(
            math.isclose(
                scales[
                    "local_electric_capillary_number_epsilon_e2_a_over_gamma"
                ],
                12.04404411764706,
                rel_tol=1e-12,
            )
        )
        self.assertIn("contact-line capillarity", audit["interpretation"])

    def test_thermal_capacity_is_absolute_and_flight_dryout_is_not_chf(self) -> None:
        audit = e043.thermal_performance_audit()
        flight = audit["parabolic_flight"]
        ground = audit["terrestrial_updated_heater"]
        self.assertTrue(
            math.isclose(flight["reconstructed_absolute_baseline_capacity_w"], 12.375)
        )
        self.assertEqual(flight["reconstructed_absolute_dep_capacity_w"], 15.75)
        self.assertEqual(flight["reconstructed_incremental_capacity_w"], 3.375)
        self.assertFalse(flight["steady_state"])
        self.assertFalse(flight["true_chf_identified"])
        self.assertFalse(
            flight["journal_caption_and_data_guide_flight_voltage_consistent"]
        )
        self.assertEqual(flight["individual_condition_files"], 118)
        self.assertEqual(
            flight["reported_ehd_electrical_steady_state_time"],
            "several minutes; no exact duration reported",
        )
        self.assertEqual(
            flight["heater_area_sensitivity"]["data_guide_2p36_cm2_increment_w"],
            3.54,
        )
        self.assertIn("several-minute", flight["paper_caveat"])
        self.assertTrue(
            math.isclose(ground["reconstructed_incremental_capacity_w"], 5.87)
        )
        self.assertTrue(
            math.isclose(ground["relative_increase"], 0.6014344262295082)
        )

    def test_capacity_leverage_is_not_promoted_to_system_cop(self) -> None:
        audit = e043.thermal_performance_audit()["electrical_and_system_energy"]
        self.assertEqual(audit["flight_capacity_gain_per_reported_overall_max_hv_w"], 5.625)
        self.assertFalse(audit["published_summary_bounds_contradict"])
        self.assertFalse(audit["published_summary_scopes_identical"])
        self.assertIn("not coefficient of performance", audit["not_a_cop_warning"])
        missing = e043.reaction_and_energy_ledger()["missing_energy_terms"]
        self.assertIn("pump flow rate and hydraulic power delta_p times Q", missing)
        self.assertTrue(any("chiller" in item for item in missing))

    def test_real_gravity_field_energy_screen_fails_even_when_favorable(self) -> None:
        bound = e043.real_curvature_field_energy_screen()
        self.assertIn("not a rigorous", bound["assumption"])
        self.assertTrue(
            math.isclose(bound["electric_energy_density_j_m3"], 818.995, rel_tol=1e-12)
        )
        self.assertTrue(
            math.isclose(bound["mass_equivalent_kg"], 4.5930091237296776e-21)
        )
        self.assertTrue(
            math.isclose(
                bound["optimistic_acceleration_at_1cm_m_s2"],
                3.065512079450898e-27,
                rel_tol=1e-12,
            )
        )
        self.assertIn("fails", bound["decision"])

    def test_reaction_ledger_closes_internal_spacecraft_forces(self) -> None:
        ledger = e043.reaction_and_energy_ledger()
        self.assertIn("equal-and-opposite", ledger["electrical_source"])
        self.assertIn("flight rack", ledger["structure"])
        self.assertIn("cannot accelerate a closed vehicle", ledger["net_vehicle_implication"])

    def test_four_gates_keep_device_scale_separate_from_gravity(self) -> None:
        gates = e043.p023_gates()
        self.assertEqual(
            {key: gate["status"] for key, gate in gates.items()},
            {
                "1_source_coupling": "passed",
                "2_constraints_validity": "partial",
                "3_absolute_scale": "passed",
                "4_falsification": "partial",
            },
        )
        decision = e043.survival_rule_evaluation()
        self.assertTrue(decision["device_scale_force_anchor_recovered"])
        self.assertTrue(decision["device_scale_thermal_performance_recovered"])
        self.assertFalse(decision["useful_universal_acceleration"])
        self.assertTrue(decision["ordinary_em_field_energy_sources_real_curvature"])
        self.assertFalse(decision["useful_engineered_spacetime_curvature"])

    def test_claim_kill_matrix_preserves_positive_and_negative_results(self) -> None:
        matrix = {row["claim"]: row["supported"] for row in e043.claim_kill_matrix()}
        self.assertTrue(
            matrix[
                "the apparatus demonstrated electrically controlled thin-film boiling in transient microgravity"
            ]
        )
        self.assertFalse(
            matrix["the experiment measured a complete volume-force field or hydraulic efficiency"]
        )
        self.assertFalse(
            matrix[
                "PSI-9 generated detectable or useful real gravity, modified inertia, or reactionless propulsion"
            ]
        )

    def test_falsification_design_requires_momentum_and_energy_closure(self) -> None:
        design = e043.falsification_design()
        self.assertFalse(design["hardware_action_authorized"])
        self.assertIn("differential pump pressure", design["measurements"][0])
        self.assertIn("delta_p * Q", design["closure_equations"]["hydraulic_efficiency"])
        self.assertIn(
            "never include both",
            design["closure_equations"]["fluid_control_volume_momentum"],
        )
        self.assertIn(
            "all internal",
            design["closure_equations"]["sealed_cell_momentum"],
        )
        self.assertIn("one tenth", design["kill_rule"])

    def test_portfolio_is_diverse_and_only_p023_was_deepened(self) -> None:
        portfolio = e043.portfolio_refresh()
        self.assertEqual(
            [item["id"] for item in portfolio],
            ["P-023", "P-027", "P-028", "P-029", "P-030", "P-031"],
        )
        self.assertEqual(len({item["category"] for item in portfolio}), 6)
        self.assertEqual(
            [item["id"] for item in portfolio if item["disposition"].startswith("deepened")],
            ["P-023"],
        )
        self.assertEqual(
            portfolio[2]["disposition"],
            "candidate_next_product_constraint_and_noise_audit",
        )

    def test_no_heavy_compute_hardware_or_checkpoint_work_occurred(self) -> None:
        resources = e043.run_analysis()["resource_accounting"]
        self.assertTrue(all(value == 0 for value in resources.values()))

    def test_cli_writes_identical_deterministic_reports(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first_path = Path(directory) / "e043-first.json"
            second_path = Path(directory) / "e043-second.json"
            first_exit = e043.main(["--report-json", str(first_path)])
            second_exit = e043.main(["--report-json", str(second_path)])
            self.assertEqual(first_path.read_bytes(), second_path.read_bytes())
            report = json.loads(first_path.read_text(encoding="utf-8"))
        self.assertEqual(first_exit, 0)
        self.assertEqual(second_exit, 0)
        self.assertEqual(report["provenance"]["campaign"], "E-043")
        self.assertEqual(
            report["decision"]["status"],
            "retain_device_scale_thermal_analog_force_and_scaleup_partial",
        )
        self.assertFalse(
            report["decision"]["survived_as_useful_universal_or_curvature_gravity"]
        )
        self.assertTrue(
            report["decision"][
                "standard_gr_curvature_from_field_energy_exists_but_is_negligible"
            ]
        )


if __name__ == "__main__":
    unittest.main()
