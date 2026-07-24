import unittest
import tempfile
from pathlib import Path

import numpy as np

import models.e025_axisymmetric_wide_2hessian as e025

from models.e025_axisymmetric_wide_2hessian import (
    AxisymmetricGrid,
    build_system,
    solve_linear_reference,
)
from models.e026_nonsymmetric_amg import (
    AmgConfiguration,
    configuration_provenance,
    runtime_provenance,
)
from models.e028_fine_grid_campaign import (
    _default_output_artifact,
    _require_resume_crosscheck_clear,
    _sha256_array,
    _validate_resume_report,
    implementation_provenance,
    load_campaign_checkpoint,
    peak_rss_bytes,
    save_campaign_checkpoint,
    scaled_source_metadata,
    solve_one_stage,
)


class FineGridCampaignTests(unittest.TestCase):
    @staticmethod
    def _small_problem():
        system = build_system(AxisymmetricGrid(4.0, 0.5, 2))
        source = 0.02 * np.exp(-((system.rho - 1.8) / 0.7) ** 4) * np.exp(
            -(system.z / 0.65) ** 4
        )
        linear = solve_linear_reference(system, source)
        configuration = AmgConfiguration(
            kind="pgsa",
            gmres_relative_tolerance=1.0e-9,
            max_coarse=8,
        )
        return system, source, linear, configuration

    def test_scaled_source_metadata_preserves_charge_error(self) -> None:
        metadata = {
            "continuous_normalization": 1.2,
            "nominal_volume": 10.0,
            "nominal_charge": 20.0,
            "sampled_charge": 19.5,
            "sampled_charge_relative_error": -0.025,
            "minimum_source": 0.0,
            "maximum_source": 3.0,
        }
        scaled = scaled_source_metadata(metadata, 0.25)
        self.assertEqual(scaled["nominal_charge"], 5.0)
        self.assertEqual(scaled["sampled_charge"], 4.875)
        self.assertEqual(scaled["sampled_charge_relative_error"], -0.025)
        self.assertEqual(scaled["full_source_amplitude"], 0.25)

    def test_small_native_linear_stage_closes_with_strict_pgsa_gate(self) -> None:
        system, source, linear, configuration = self._small_problem()
        field, stage = solve_one_stage(
            system,
            source,
            0.5 * linear,
            0.5,
            configuration,
        )
        self.assertTrue(np.all(np.isfinite(field)))
        nonlinear = stage["nonlinear"]
        self.assertLess(nonlinear["relative_residual_l2"], 1.0e-7)
        self.assertGreater(nonlinear["minimum_pair_sum"], 0.0)
        self.assertGreater(nonlinear["minimum_spatial_principal"], 0.0)
        self.assertGreater(nonlinear["minimum_time_kinetic"], 0.0)
        for row in nonlinear["history"]:
            self.assertEqual(row["linear"]["gmres_info"], 0)
            self.assertLess(row["linear"]["true_linear_residual_ratio"], 1.0e-8)

    def test_interrupted_stage_resumes_exactly_from_accepted_step(self) -> None:
        system, source, linear, configuration = self._small_problem()
        uninterrupted, _ = solve_one_stage(
            system, source, 0.5 * linear, 0.5, configuration
        )
        captured = {}

        class StopAfterAcceptedStep(RuntimeError):
            pass

        def interrupt(field, history):
            if len(history) == 1:
                captured["field"] = field.copy()
                captured["history"] = list(history)
                raise StopAfterAcceptedStep

        with self.assertRaises(StopAfterAcceptedStep):
            solve_one_stage(
                system,
                source,
                0.5 * linear,
                0.5,
                configuration,
                accepted_step_callback=interrupt,
            )
        resumed, resumed_stage = solve_one_stage(
            system,
            source,
            captured["field"],
            0.5,
            configuration,
            prior_history=captured["history"],
        )
        self.assertTrue(np.array_equal(resumed, uninterrupted))
        self.assertEqual(len(resumed_stage["nonlinear"]["history"]), 4)

    def test_checkpoint_integrity_checks_field_linear_field_and_report(self) -> None:
        field = np.linspace(0.0, 1.0, 12)
        linear = np.linspace(1.0, 2.0, 12)
        report = {"output_field_sha256": _sha256_array(field), "campaign": {}}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "checkpoint.npz"
            save_campaign_checkpoint(path, field, linear, report)
            loaded_field, loaded_linear, loaded_report = load_campaign_checkpoint(
                path
            )
            self.assertTrue(np.array_equal(loaded_field, field))
            self.assertTrue(np.array_equal(loaded_linear, linear))
            self.assertEqual(loaded_report, report)
            with np.load(path, allow_pickle=False) as payload:
                saved_field = payload["field"].copy()
                changed_linear = payload["full_linear_field"].copy()
                metadata = payload["metadata"].copy()
            changed_linear[0] += 1.0
            with path.open("wb") as handle:
                np.savez_compressed(
                    handle,
                    field=saved_field,
                    full_linear_field=changed_linear,
                    metadata=metadata,
                )
            with self.assertRaisesRegex(ValueError, "linear-field digest"):
                load_campaign_checkpoint(path)

    def test_saved_crosscheck_conflict_blocks_next_resumed_stage(self) -> None:
        report = {
            "spatial_principal_crosschecks": {
                "crosscheck_conflicts_with_wide_gate": True
            }
        }
        _require_resume_crosscheck_clear(report, 3, 3)
        with self.assertRaisesRegex(RuntimeError, "hard stop"):
            _require_resume_crosscheck_clear(report, 3, 4)

    def test_air_default_output_cannot_alias_pgsa_artifact(self) -> None:
        pgsa = _default_output_artifact(1, "pgsa")
        air = _default_output_artifact(1, "air")
        self.assertNotEqual(pgsa, air)
        self.assertTrue(pgsa.name.endswith("_pgsa.npz"))
        self.assertTrue(air.name.endswith("_air.npz"))

    def test_resume_rejects_mixed_runtime_provenance(self) -> None:
        system, source, _, configuration = self._small_problem()
        prior_runtime = runtime_provenance()
        prior_runtime["python"] = "different-runtime"
        report = {
            "operator_and_source": {
                "system_digest": e025._system_digest(system),
                "full_source_digest": e025._source_digest(source),
            },
            "implementation_provenance": implementation_provenance(),
            "runtime_provenance": prior_runtime,
            "configuration": {
                "amg": configuration_provenance(configuration)
            },
            "campaign": {"completed_stage": 0, "stages": []},
        }
        with self.assertRaisesRegex(ValueError, "runtime provenance"):
            _validate_resume_report(report, system, source, configuration)

    def test_peak_rss_is_positive(self) -> None:
        self.assertGreater(peak_rss_bytes(), 0)


if __name__ == "__main__":
    unittest.main()
