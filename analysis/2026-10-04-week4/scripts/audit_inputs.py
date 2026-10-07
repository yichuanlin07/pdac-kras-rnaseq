import csv, json, hashlib, pathlib, sys

root = pathlib.Path(
    sys.argv[1] if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parents[3]
)
src = root / "analysis/2026-10-01/counts"
out = root / "analysis/2026-10-04-week4/sources"
read = lambda p: list(csv.DictReader(open(p), delimiter="\t"))
meta = read(src / "sample_annotation.txt")
c = read(src / "counts_raw.txt")
ids = [r["ENTREZID"] for r in c]
cols = list(c[0])[1:]
assert len(c) == 28395 and len(cols) == 17 and (len(set(ids)) == len(ids))
assert cols == [m["sample_name"] for m in meta]
for m in meta:
    vals = [int(r[m["sample_name"]]) for r in c]
    assert min(vals) >= 0
    assert sum(vals) == int(m["assigned_counts"])
    raw = read(src / "raw_counts" / f"{m['sample_name']}.tabular")
    tab = {r[list(r)[0]]: int(r[list(r)[1]]) for r in raw}
    assert set(tab) == set(ids)
    assert all((v == tab[k] for k, v in zip(ids, vals)))
ena = read(out / "ena_runs_2026-10-04.tsv")
er = {r["run_accession"]: r for r in ena}
for m in meta:
    assert er[m["run_accession"]]["sample_alias"] == m["ena_alias"], (m, er[m["run_accession"]])
p5 = [
    {**m, **er[m["run_accession"]]}
    for m in meta
    if m["cell_line"] == "MiaPaca-2" and m["condition"] == "KRAS"
]
manifest = {
    "input_commit": "462867100fa1628d716cb7722a574da5f90577df",
    "gene_rows": len(c),
    "runs": len(cols),
    "all_integer_nonnegative": True,
    "metadata_columns_exact_match": True,
    "raw_run_tables_exact_match": True,
    "assigned_sums_exact_match": True,
    "ena_sample_alias_exact_match": True,
    "p5_public_identity": p5,
    "p5_repeat_type": "unresolved; no independence assumption",
    "sha256": {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in [
            src / "counts_raw.txt",
            src / "sample_annotation.txt",
            src / "annotate_geneID.txt",
            out / "ena_runs_2026-10-04.tsv",
        ]
    },
}
(out / "input_validation.json").write_text(json.dumps(manifest, indent=2))
print(json.dumps(manifest, indent=2))
