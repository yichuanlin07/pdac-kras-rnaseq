import sys, json, hashlib
from pathlib import Path

primary, repeat = map(Path, sys.argv[1:3])
records = []
for f in sorted(repeat.rglob("*")):
    if f.suffix in (".tsv", ".json") and f.name not in (
        "repeat_run_validation.json",
        "independent_numerical_validation.json",
    ):
        rel = f.relative_to(repeat)
        a = (primary / rel).read_bytes()
        b = f.read_bytes()
        assert a == b, f"Output mismatch: {rel}"
        records.append(dict(file=str(rel), sha256=hashlib.sha256(a).hexdigest()))
assert len(records) >= 81
result = dict(
    independent_fresh_R_runs=2,
    seed=20261004,
    byte_identical_numeric_TSV_and_method_JSON_count=len(records),
    all_passed=True,
    files=records,
    excluded_from_byte_comparison="PDF creation metadata and sessionInfo; rendered figures inspected separately",
)
(primary / "repeat_run_validation.json").write_text(json.dumps(result, indent=2))
print("Byte-identical outputs:", len(records))
