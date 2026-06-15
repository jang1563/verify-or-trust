#!/usr/bin/env python3
"""Validate the public Verify-or-Trust release surface."""
from __future__ import annotations

import csv
import json
import math
import pathlib
import re
import subprocess
import sys
import tempfile
from collections.abc import Iterable


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from verify_or_trust.panels import PanelConfig, build_panels, write_panels  # noqa: E402


STRICT_JSON_FILES = [
    "artifact_manifest.json",
    "schemas/artifact_manifest.schema.json",
    "schemas/substrate_row.schema.json",
    "schemas/panel.schema.json",
    "schemas/episode.schema.json",
]

SUBSTRATE = "data/substrates/gears_norman.csv"
REQUIRED_SUBSTRATE_COLUMNS = [
    "perturbation",
    "gene",
    "fm_log2FC",
    "fm_call",
    "real_label",
    "regime",
    "raw_log2FC",
    "raw_se",
    "raw_q",
    "n_trt",
    "n_cntrl",
]

TEXT_SUFFIXES = {
    ".cff",
    ".csv",
    ".json",
    ".md",
    ".py",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}

FORBIDDEN_PATH_RE = re.compile(
    "|".join([r"(^|/)_private/", r"(^|/)runs/", r"\.slurm$", r"\.sbatch$"]),
    re.IGNORECASE,
)


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def reject_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON constant {value!r}")


def run_git(args: list[str]) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True)


def tracked_files() -> list[str]:
    return [line for line in run_git(["ls-files"]).splitlines() if line]


def load_strict_json(rel: str):
    return json.loads((ROOT / rel).read_text(), parse_constant=reject_constant)


def iter_manifest_paths(obj) -> Iterable[str]:
    if isinstance(obj, dict):
        path = obj.get("path")
        if isinstance(path, str):
            yield path
        for value in obj.values():
            yield from iter_manifest_paths(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from iter_manifest_paths(item)


def public_terms() -> list[str]:
    join = "".join
    return [
        join(["job ", "application"]),
        join(["faculty ", "application"]),
        join(["cover ", "letter"]),
        join(["res", "ume"]),
        join(["inter", "view"]),
        join(["private ", "GitHub"]),
        join(["private ", "HF"]),
        join(["private ", "dataset"]),
        join(["flip ", "public"]),
        join(["at the user's ", "request"]),
        join(["at your ", "request"]),
    ]


def check_strict_json_files() -> None:
    for rel in STRICT_JSON_FILES:
        if not (ROOT / rel).exists():
            fail(f"missing JSON file: {rel}")
        load_strict_json(rel)
    print("strict JSON files OK")


def check_manifest() -> None:
    manifest = load_strict_json("artifact_manifest.json")
    missing = []
    for rel in iter_manifest_paths(manifest):
        if rel.startswith(("http://", "https://")):
            continue
        if not (ROOT / rel).exists():
            missing.append(rel)
    if missing:
        fail("manifest points to missing local paths: " + ", ".join(sorted(set(missing))))
    print("manifest paths OK")


def check_tracked_paths(paths: list[str]) -> None:
    offenders = [p for p in paths if FORBIDDEN_PATH_RE.search(p)]
    if offenders:
        fail("forbidden tracked paths: " + ", ".join(offenders))
    print("tracked file set OK")


def check_public_text(paths: list[str]) -> None:
    terms = public_terms()
    offenders = []
    for rel in paths:
        path = ROOT / rel
        if path.suffix not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        hits = [term for term in terms if term.lower() in text]
        if hits:
            offenders.append(f"{rel}: {', '.join(hits)}")
    if offenders:
        fail("public text guard failed: " + "; ".join(offenders))
    print("public text OK")


def as_finite_float(value: str, *, optional: bool = False) -> float | None:
    if value == "":
        if optional:
            return None
        raise ValueError("blank value")
    x = float(value)
    if not math.isfinite(x):
        raise ValueError("non-finite value")
    return x


def check_substrate_csv() -> None:
    path = ROOT / SUBSTRATE
    with path.open(newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames != REQUIRED_SUBSTRATE_COLUMNS:
            fail(f"unexpected substrate columns: {reader.fieldnames}")
        rows = list(reader)

    problems = []
    for rownum, row in enumerate(rows, start=2):
        if row["fm_call"] not in {"effect", "no_effect"}:
            problems.append(f"{rownum}: bad fm_call")
        if row["real_label"] not in {"POSITIVE", "TESTED_NEGATIVE"}:
            problems.append(f"{rownum}: bad real_label")
        for col in ["fm_log2FC"]:
            try:
                as_finite_float(row[col], optional=True)
            except ValueError as e:
                problems.append(f"{rownum}: {col} {e}")
        for col in ["raw_log2FC", "raw_se", "raw_q"]:
            try:
                as_finite_float(row[col])
            except ValueError as e:
                problems.append(f"{rownum}: {col} {e}")
        for col in ["n_trt", "n_cntrl"]:
            try:
                if int(row[col]) < 0:
                    raise ValueError("negative count")
            except ValueError as e:
                problems.append(f"{rownum}: {col} {e}")

    if problems:
        fail("substrate schema failed: " + "; ".join(problems[:20]))
    if len(rows) != 4008:
        fail(f"unexpected substrate row count: {len(rows)}")
    print("substrate CSV OK")


def assert_json_safe(value, where: str = "root") -> None:
    if isinstance(value, float) and not math.isfinite(value):
        fail(f"non-finite JSON number at {where}")
    if isinstance(value, dict):
        for key, item in value.items():
            assert_json_safe(item, f"{where}.{key}")
    elif isinstance(value, list):
        for idx, item in enumerate(value):
            assert_json_safe(item, f"{where}[{idx}]")


def check_generated_panels() -> None:
    panels = build_panels(str(ROOT / SUBSTRATE), PanelConfig(seed=13))
    if len(panels) != 107:
        fail(f"unexpected generated panel count: {len(panels)}")

    with tempfile.TemporaryDirectory() as tmp:
        out = pathlib.Path(tmp) / "panels.jsonl"
        write_panels(panels, str(out))
        text = out.read_text()
        if any(token in text for token in ["NaN", "Infinity", "-Infinity"]):
            fail("generated panels contain a non-standard JSON constant")
        for line_num, line in enumerate(text.splitlines(), start=1):
            rec = json.loads(line, parse_constant=reject_constant)
            assert_json_safe(rec, f"line {line_num}")
    print("generated panels JSONL OK")


def main() -> int:
    paths = tracked_files()
    check_strict_json_files()
    check_manifest()
    check_tracked_paths(paths)
    check_public_text(paths)
    check_substrate_csv()
    check_generated_panels()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
