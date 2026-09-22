"""Check arithmetic and coverage in the manually verified Galaxy summaries."""
import json
from hashlib import sha256
from pathlib import Path

root = Path(__file__).resolve().parent
pilots = json.loads((root / 'hisat2_pilot_results.json').read_text())
for row in pilots['results']:
    n = pilots['pairs_per_job']
    assert sum(row[k] for k in ('concordant_1', 'concordant_gt1', 'discordant_1', 'remaining_pairs')) == n
    assert sum(row[k] for k in ('remaining_mate_0', 'remaining_mate_1', 'remaining_mate_gt1')) == 2 * row['remaining_pairs']
    assert round(100 * (1 - row['remaining_mate_0'] / (2 * n)), 2) == row['overall_percent']
    assert row['state'] == 'ok'
qc = json.loads((root / 'fastqc_review.json').read_text())
ids = qc['previously_reviewed_raw_report_ids'] + [r[k] for r in qc['additional_reviews'] for k in ('r1_raw_id', 'r2_raw_id')]
ids += [r['raw_id'] for r in qc.get('partial_run_reviews', [])]
assert len(ids) == len(set(ids)) == qc['completed_reviewed_files']
assert 138 not in ids
assert qc['completed_reviewed_files'] == 2 * qc['complete_pairs_reviewed'] + len(qc.get('partial_run_reviews', []))
multi = json.loads((root / 'multiqc_summary.json').read_text())
assert len(multi['rows']) == len({r[0] for r in multi['rows']}) == 34
assert [min(r[1] for r in multi['rows']), max(r[1] for r in multi['rows'])] == multi['duplication_percent_range']
assert multi['source_reports']['galaxy_computed'] + multi['source_reports']['local_fastqc_0_12_1'] == 34
assert sum(multi['gc_module'][k] for k in ('pass','warn','fail')) == 34
for mate, expected_sha in ((1, '588252df5c659d64548e29edd7366334f350f29ece191394b6c7fc9104e0e225'), (2, '76360671b93b6d150303425a39bebdd6a1f64b1938f3e5a0d5f76b03221cad45')):
    path = root / 'fastqc_local' / f'SRR24828471_R{mate}_local_fastqc_data.txt'
    assert sha256(path.read_bytes()).hexdigest() == expected_sha
    content = path.read_text()
    assert 'Total Sequences\t37886040\n' in content
    assert 'Sequence length\t150\n' in content
    assert '>>Per sequence GC content\twarn\n' in content
    assert len([line for line in content.splitlines() if line.startswith('>>') and line.endswith('\tfail')]) == 2
print(f"Validated {len(pilots['results'])} pilot summaries and {len(ids)} raw-read QC reports.")
print('Validated 34 unique MultiQC rows and both local report hashes/module results.')
