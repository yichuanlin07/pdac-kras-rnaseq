from pathlib import Path
import csv
import hashlib
import json
import shutil
import subprocess
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT
REPO = Path(__file__).resolve().parents[3]
COUNTS = REPO / 'analysis/2026-10-01/counts'
PRIOR = REPO / 'analysis/2026-10-11-post-meeting'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def rows(path):
    with path.open() as f:
        return list(csv.DictReader(f, delimiter='\t'))

def main():
    src = OUT / 'sources'
    src.mkdir(parents=True, exist_ok=True)
    manifest = []
    for base, rel, name in [
        (COUNTS, 'counts_raw.txt', 'counts_raw.tsv'),
        (COUNTS, 'sample_annotation.txt', 'samples.tsv'),
        (COUNTS, 'annotate_geneID.txt', 'annotation.tsv'),
        (COUNTS, 'm1_correction_provenance.json', 'm1_correction_provenance.json'),
        (PRIOR, 'results/full/DESeq2_full.tsv', 'DESeq2_full.tsv'),
        (PRIOR, 'results/full/edgeR_full.tsv', 'edgeR_full.tsv'),
        (PRIOR, 'results/descriptive_joint_ge7of8.tsv', 'stable_ge7of8.tsv'),
        (PRIOR, 'results/full/filter.tsv', 'prior_filter.tsv'),
    ]:
        original = base / rel
        target = src / name
        if target.exists() and sha(target) != sha(original):
            raise ValueError(f'Existing snapshot differs: {target}')
        if not target.exists():
            shutil.copyfile(original, target)
        manifest.append({'role': name, 'original': str(original), 'snapshot': name,
                         'bytes': target.stat().st_size, 'sha256': sha(target)})
    matrix = rows(src / 'counts_raw.tsv')
    samples = rows(src / 'samples.tsv')
    assert len(matrix) == 28395 and len(samples) == 17
    assert len({r['ENTREZID'] for r in matrix}) == len(matrix)
    names = list(matrix[0])[1:]
    assert names == [r['sample_name'] for r in samples]
    assert len(set(names)) == 17
    source_checks = []
    for sample in samples:
        name = sample['sample_name']
        raw_path = COUNTS / 'raw_counts' / (name + '.tabular')
        raw = rows(raw_path)
        actual = {r[next(iter(r))]: int(r[name]) for r in raw}
        assert len(actual) == 28395
        assert all(int(r[name]) >= 0 and int(r[name]) == actual[r['ENTREZID']] for r in matrix)
        total = sum(int(r[name]) for r in matrix)
        assert total == int(sample['assigned_counts'])
        source_checks.append({'sample': name, 'run': sample['run_accession'],
                              'source': str(raw_path), 'sha256': sha(raw_path),
                              'assigned_counts': total, 'all_28395_values_match': True})
    assert sum(int(r['KRAS_siRNA_M1']) for r in matrix) == 37657740

    for name in ['h.all.v2026.2.Hs.entrez.gmt', 'c2.cp.reactome.v2026.2.Hs.entrez.gmt']:
        url = 'https://data.broadinstitute.org/gsea-msigdb/msigdb/release/2026.2.Hs/' + name
        target = src / name
        if not target.exists():
            with urllib.request.urlopen(url, timeout=60) as response:
                data = response.read()
            assert b'\t' in data and b'<html' not in data.lower()
            target.write_bytes(data)
        manifest.append({'role': 'gene_sets', 'url': url, 'snapshot': name,
                         'accessed': '2026-10-30', 'bytes': target.stat().st_size,
                         'sha256': sha(target), 'sets': len(target.read_text().splitlines())})
    commit = subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip()
    result = {'source_repository': str(REPO), 'source_commit': commit,
              'created_date': '2026-10-30', 'gene_rows': len(matrix), 'runs': len(samples),
              'corrected_M1_assigned': 37657740, 'snapshots': manifest,
              'original_count_table_checks': source_checks,
              'archive_warning': 'The 2026-09-30 archive contains the superseded 509-count M1 column. It was not used or changed.',
              'P5': 'Sum raw integer counts before filtering; repeat identity remains unresolved. Single-library sensitivity fits are required.'}
    (src / 'input_validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['source_commit','gene_rows','runs','corrected_M1_assigned']}))

if __name__ == '__main__':
    main()
