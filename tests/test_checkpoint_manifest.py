import hashlib
import unittest
from pathlib import Path


CHECKPOINT_DIR = Path(__file__).resolve().parents[1] / "models" / "checkpoints"
MANIFEST = CHECKPOINT_DIR / "SHA256SUMS"


class CheckpointManifestTests(unittest.TestCase):
    def test_manifest_covers_and_verifies_every_checkpoint(self) -> None:
        expected: dict[str, str] = {}
        for line in MANIFEST.read_text(encoding="utf-8").splitlines():
            digest, filename = line.split(maxsplit=1)
            self.assertRegex(digest, r"^[0-9a-f]{64}$")
            self.assertNotIn(filename, expected)
            expected[filename] = digest

        present = {path.name for path in CHECKPOINT_DIR.glob("*.npz")}
        self.assertEqual(present, set(expected))

        for filename, expected_digest in sorted(expected.items()):
            payload = (CHECKPOINT_DIR / filename).read_bytes()
            actual_digest = hashlib.sha256(payload).hexdigest()
            self.assertEqual(actual_digest, expected_digest, filename)


if __name__ == "__main__":
    unittest.main()
