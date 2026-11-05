"""Tests for ml/risk/preprocess.py.

Deliberately uses only unittest + csv/io (stdlib) so these checks run without
pandas/sklearn installed — the parsing/cleaning logic is the part most
likely to silently corrupt data, and it is independent of the ML stack.

Run: python3 -m unittest tests.test_preprocess -v
"""

import unittest
from pathlib import Path

from ml.risk.preprocess import _EXPECTED_COLUMNS, _fix_malformed_row, _parse_raw_rows

RAW_DATASET_PATH = (
    Path(__file__).parent.parent / "data" / "raw" / "Algerian_forest_fires_dataset_UPDATE.csv"
)

SYNTHETIC_CSV = """Bejaia Region Dataset
day,month,year,Temperature, RH, Ws,Rain ,FFMC,DMC,DC,ISI,BUI,FWI,Classes
01,06,2012,29,57,18,0,65.7,3.4,7.6,1.3,3.4,0.5,not fire
06,06,2012,31,67,14,0,82.6,5.8,22.2,3.1,7,2.5,fire

Sidi-Bel Abbes Region Dataset
day,month,year,Temperature, RH, Ws,Rain ,FFMC,DMC,DC,ISI,BUI,FWI,Classes
14,07,2012,37,37,18,0.2,88.9,12.9,14.6 9,12.5,10.4,fire
"""


class FixMalformedRowTests(unittest.TestCase):
    def test_leaves_well_formed_row_untouched(self):
        row = "01,06,2012,29,57,18,0,65.7,3.4,7.6,1.3,3.4,0.5,not fire"
        self.assertEqual(_fix_malformed_row(row), row)

    def test_splits_merged_dc_isi_token(self):
        malformed = "14,07,2012,37,37,18,0.2,88.9,12.9,14.6 9,12.5,10.4,fire"
        fixed = _fix_malformed_row(malformed)
        fields = fixed.split(",")
        self.assertEqual(len(fields), _EXPECTED_COLUMNS)
        self.assertEqual(fields[9], "14.6")  # DC
        self.assertEqual(fields[10], "9")  # ISI


class ParseRawRowsTests(unittest.TestCase):
    def test_parses_both_regions_and_fixes_malformed_row(self):
        rows = _parse_raw_rows(SYNTHETIC_CSV)

        self.assertEqual(len(rows), 3)
        self.assertEqual([r["region"] for r in rows], ["Bejaia", "Bejaia", "Sidi-Bel Abbes"])
        self.assertEqual([r["fire"] for r in rows], [0, 1, 1])

        fixed_row = rows[2]
        self.assertEqual(fixed_row["DC"], "14.6")
        self.assertEqual(fixed_row["ISI"], "9")
        self.assertEqual(fixed_row["Temperature"], "37")


class RealDatasetShapeTests(unittest.TestCase):
    """Integration check against the actual downloaded CSV.

    Skipped (not failed) when the file hasn't been fetched yet, so this
    suite still runs in a fresh checkout before scripts/download_risk_dataset.py
    has been run.
    """

    def setUp(self):
        if not RAW_DATASET_PATH.exists():
            self.skipTest(f"{RAW_DATASET_PATH} not present — run scripts/download_risk_dataset.py")

    def test_matches_documented_uci_counts(self):
        text = RAW_DATASET_PATH.read_text(encoding="utf-8", errors="replace")
        rows = _parse_raw_rows(text)

        self.assertEqual(len(rows), 244)
        regions = [r["region"] for r in rows]
        self.assertEqual(regions.count("Bejaia"), 122)
        self.assertEqual(regions.count("Sidi-Bel Abbes"), 122)

        labels = [r["fire"] for r in rows]
        self.assertEqual(sum(labels), 138)  # fire
        self.assertEqual(len(labels) - sum(labels), 106)  # not fire


if __name__ == "__main__":
    unittest.main()
