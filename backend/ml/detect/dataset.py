"""Generates a dataset YAML with absolute paths for ultralytics to consume.

`fasdd_cv.yaml` in this directory is kept with a relative `path:` purely as
human-readable documentation of the expected layout. Do NOT pass it to
ultralytics directly: empirically (tested against ultralytics 8.4.202), a
relative `path:` is resolved one directory level higher than the yaml
file's own location actually implies — confirmed by reproducing the
`FileNotFoundError` and walking `yaml_file.parents[...]` to find which
index it actually used. Rather than depend on resolution behavior that
differs across ultralytics versions, this writes a second yaml with
absolute `train`/`val`/`test` paths baked in, which has no relative path
to misinterpret.
"""

from pathlib import Path

import yaml

TEMPLATE_PATH = Path(__file__).parent / "fasdd_cv.yaml"
DATASET_DIR = Path(__file__).parent.parent.parent / "data" / "raw" / "fasdd_cv"
RESOLVED_PATH = Path(__file__).parent / ".fasdd_cv.resolved.yaml"


def resolved_data_yaml() -> Path:
    with open(TEMPLATE_PATH) as f:
        config = yaml.safe_load(f)

    for split in ("train", "val", "test"):
        config[split] = str(DATASET_DIR / config[split])
    config.pop("path", None)

    with open(RESOLVED_PATH, "w") as f:
        yaml.safe_dump(config, f)

    return RESOLVED_PATH
