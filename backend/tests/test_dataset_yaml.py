"""Regression test for the relative-path resolution bug in dataset.py.

ultralytics resolves a dataset yaml's relative `path:` field one directory
level higher than the yaml file's own location would suggest (confirmed
empirically against ultralytics 8.4.202 — see dataset.py's docstring).
resolved_data_yaml() works around this by writing out absolute train/val/test
paths instead. This test pins that behavior so a future ultralytics upgrade
that changes (or fixes) the resolution logic doesn't silently break training.

Run: python3 -m unittest tests.test_dataset_yaml -v
"""

import unittest

from ml.detect.dataset import DATASET_DIR, resolved_data_yaml


class ResolvedDataYamlTests(unittest.TestCase):
    def test_splits_are_absolute_and_under_dataset_dir(self):
        import yaml

        path = resolved_data_yaml()
        self.addCleanup(path.unlink, missing_ok=True)

        with open(path) as f:
            config = yaml.safe_load(f)

        self.assertNotIn("path", config)
        for split in ("train", "val", "test"):
            self.assertTrue(config[split].startswith(str(DATASET_DIR)))

        self.assertEqual(config["nc"], 2)
        self.assertEqual(config["names"], {0: "fire", 1: "smoke"})


if __name__ == "__main__":
    unittest.main()
