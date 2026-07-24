import hashlib
import json
import platform
import tempfile
import unittest
from pathlib import Path

import numpy as np
from scipy import sparse

from models.e026_nonsymmetric_amg import (
    AmgConfiguration,
    DEFAULT_OUTPUT_ARTIFACT,
    EXPECTED_INPUT_SHA256,
    build_fixed_hierarchy,
    load_campaign_artifact,
    matrix_diagnostics,
    run_exact_campaign,
    runtime_provenance,
    save_campaign_artifact,
    solve_linear_corrector,
)


class NonsymmetricAmgTests(unittest.TestCase):
    def test_matrix_diagnostics_identify_m_matrix_sign_pattern(self) -> None:
        jacobian = sparse.csr_matrix(
            [[-2.0, 1.0, 0.0], [0.5, -1.5, 1.0], [0.0, 0.25, -1.0]]
        )
        report = matrix_diagnostics(jacobian)
        self.assertEqual(report["jacobian_negative_diagonal_count"], 3)
        self.assertEqual(report["jacobian_positive_off_diagonal_count"], 4)
        self.assertEqual(report["sign_normalized_positive_diagonal_count"], 3)
        self.assertEqual(report["sign_normalized_negative_off_diagonal_count"], 4)
        self.assertGreater(report["frobenius_asymmetry_ratio"], 0.0)

    def test_fixed_pgsa_corrector_passes_true_residual_gate(self) -> None:
        size = 64
        positive = sparse.diags(
            [-0.8 * np.ones(size - 1), 2.0 * np.ones(size), -1.2 * np.ones(size - 1)],
            [-1, 0, 1],
            format="csr",
        )
        jacobian = -positive
        residual = np.linspace(0.2, 1.0, size)
        system = type(
            "System",
            (),
            {
                "rho": np.linspace(0.0, 3.5, size),
                "z": np.zeros(size),
                "grid": type("Grid", (), {"radial_max": 4.0})(),
            },
        )()
        configuration = AmgConfiguration(
            kind="pgsa", gmres_relative_tolerance=1.0e-9, max_coarse=8
        )
        caller_state = np.random.get_state()
        try:
            np.random.seed(2607)
            expected_state = np.random.get_state()
            correction, report = solve_linear_corrector(
                jacobian, residual, system, configuration
            )
            observed_caller_values = np.random.random(8)
            np.random.set_state(expected_state)
            expected_caller_values = np.random.random(8)
            repeated, repeated_report = solve_linear_corrector(
                jacobian, residual, system, configuration
            )
        finally:
            np.random.set_state(caller_state)
        self.assertTrue(np.all(np.isfinite(correction)))
        self.assertEqual(report["gmres_info"], 0)
        self.assertLess(report["true_linear_residual_ratio"], 1.0e-8)
        self.assertTrue(np.array_equal(observed_caller_values, expected_caller_values))
        self.assertTrue(np.array_equal(correction, repeated))
        self.assertEqual(
            report["true_linear_residual_ratio"],
            repeated_report["true_linear_residual_ratio"],
        )

    def test_air_hierarchy_action_is_fixed_and_finite(self) -> None:
        size = 48
        matrix = sparse.diags(
            [-np.ones(size - 1), 2.1 * np.ones(size), -np.ones(size - 1)],
            [-1, 0, 1],
            format="csr",
        )
        system = type(
            "System",
            (),
            {
                "rho": np.linspace(0.0, 1.0, size),
                "z": np.zeros(size),
                "grid": type("Grid", (), {"radial_max": 2.0})(),
            },
        )()
        hierarchy = build_fixed_hierarchy(
            matrix,
            system,
            AmgConfiguration(kind="air", max_coarse=8),
        )
        action = hierarchy.aspreconditioner(cycle="V")
        vector = np.linspace(-1.0, 1.0, size)
        first = action @ vector
        second = action @ vector
        self.assertTrue(np.all(np.isfinite(first)))
        self.assertTrue(np.allclose(first, second, rtol=0.0, atol=0.0))

    def test_campaign_artifact_roundtrip_rejects_digest_change(self) -> None:
        field = np.linspace(0.0, 1.0, 10)
        field_sha256 = hashlib.sha256(
            np.ascontiguousarray(field, dtype=np.float64).view(np.uint8)
        ).hexdigest()
        report = {
            "full_source": {"relative_residual_l2": 1.0e-8},
            "output_field_sha256": field_sha256,
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "campaign.npz"
            save_campaign_artifact(path, field, report)
            loaded, loaded_report = load_campaign_artifact(path)
            self.assertTrue(np.array_equal(loaded, field))
            self.assertEqual(loaded_report, report)
            with np.load(path, allow_pickle=False) as payload:
                changed = np.asarray(payload["field"], dtype=float)
                metadata = payload["metadata"].copy()
            changed_metadata = json.loads(str(metadata.item()))
            changed_metadata["report"]["full_source"][
                "relative_residual_l2"
            ] = 2.0e-8
            with path.open("wb") as handle:
                np.savez_compressed(
                    handle,
                    field=field,
                    metadata=np.array(json.dumps(changed_metadata, sort_keys=True)),
                )
            with self.assertRaisesRegex(ValueError, "report digest"):
                load_campaign_artifact(path)

            save_campaign_artifact(path, field, report)
            with np.load(path, allow_pickle=False) as payload:
                changed = np.asarray(payload["field"], dtype=float)
                metadata = payload["metadata"].copy()
            changed[0] += 1.0
            with path.open("wb") as handle:
                np.savez_compressed(handle, field=changed, metadata=metadata)
            with self.assertRaisesRegex(ValueError, "digest"):
                load_campaign_artifact(path)

    def test_canonical_campaign_matches_artifact_and_retains_spatial_warning(
        self,
    ) -> None:
        saved_field, saved_report = load_campaign_artifact(DEFAULT_OUTPUT_ARTIFACT)
        self.assertEqual(
            saved_report["input_checkpoint"]["sha256"], EXPECTED_INPUT_SHA256
        )
        try:
            field, report = run_exact_campaign(include_annulus_diagnostics=False)
        except ValueError as error:
            incompatible_operator = (
                "checkpoint system_digest does not match the requested solve"
                in str(error)
            )
            canonical_platform = (
                platform.system() == "Darwin" and platform.machine() == "arm64"
            )
            if incompatible_operator and not canonical_platform:
                self.skipTest(
                    "canonical checkpoint has an exact Darwin/arm64 discrete-"
                    f"operator fingerprint and was correctly rejected: {error}"
                )
            raise
        self.assertTrue(np.array_equal(field, saved_field))
        self.assertEqual(report["output_field_sha256"], saved_report["output_field_sha256"])
        self.assertEqual(
            report["input_checkpoint"]["sha256"], EXPECTED_INPUT_SHA256
        )
        self.assertEqual(report["runtime_provenance"], runtime_provenance())

        full_source = report["full_source"]
        self.assertLess(full_source["relative_residual_l2"], 1.0e-7)
        self.assertGreater(full_source["minimum_pair_sum"], 0.0)
        self.assertGreater(full_source["minimum_spatial_principal"], 0.0)
        self.assertGreater(full_source["minimum_time_kinetic"], 0.0)
        for row in full_source["history"]:
            self.assertEqual(row["linear"]["gmres_info"], 0)
            self.assertLess(row["linear"]["true_linear_residual_ratio"], 1.0e-8)

        warning = report["spatial_principal_crosschecks"]
        self.assertTrue(warning["wide_stencil_acceptance_gate"]["passes"])
        self.assertTrue(warning["crosscheck_conflicts_with_wide_gate"])
        for key in (
            "fixed_coordinate_crosscheck",
            "independent_centered_crosscheck",
        ):
            row = warning[key]
            self.assertEqual(row["nonpositive_node_count"], 1)
            self.assertLess(row["minimum_spatial_principal"], 0.0)
            self.assertEqual(row["minimum_rho"], 6.25)
            self.assertEqual(row["minimum_z"], 0.75)
        self.assertEqual(
            warning,
            saved_report["spatial_principal_crosschecks"],
        )


if __name__ == "__main__":
    unittest.main()
