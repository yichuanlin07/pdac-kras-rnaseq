"""Check HISAT2 summary counts and percentages, then rebuild results.json."""
from pathlib import Path
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
FIELDS = [
    ('total_pairs', r'Total pairs: (\d+)'),
    ('pair_unaligned', r'Aligned concordantly or discordantly 0 time: (\d+)'),
    ('concordant_unique', r'Aligned concordantly 1 time: (\d+)'),
    ('concordant_multiple', r'Aligned concordantly >1 times: (\d+)'),
    ('discordant_unique', r'Aligned discordantly 1 time: (\d+)'),
    ('unpaired_total', r'Total unpaired reads: (\d+)'),
    ('unpaired_unaligned', r'Aligned 0 time: (\d+)'),
    ('unpaired_unique', r'Aligned 1 time: (\d+)'),
    ('unpaired_multiple', r'Aligned >1 times: (\d+)'),
]
ACCESSIONS = {
    'Control M1':'SRR24828468', 'Control M2':'SRR24828466', 'Control M3':'SRR24828479',
    'Control P1':'SRR24828475', 'Control P2':'SRR24828473', 'Control P3':'SRR24828477',
    'Control P4':'SRR24828480', 'Control P5':'SRR24828470',
    'KRAS M1':'SRR24828469', 'KRAS M2':'SRR24828467', 'KRAS M3':'SRR24828465',
    'KRAS P1':'SRR24828476', 'KRAS P2':'SRR24828474', 'KRAS P3':'SRR24828478',
    'KRAS P4':'SRR24828481', 'KRAS P5':'SRR24828471', 'KRAS P5_v2':'SRR24828472',
}

def parse(path):
    text = path.read_text()
    row = {key:int(re.search(pattern, text).group(1)) for key,pattern in FIELDS}
    row['overall_alignment_pct'] = float(re.search(r'Overall alignment rate: ([\d.]+)%', text).group(1))
    n = row['total_pairs']
    assert n == sum(row[k] for k in ['pair_unaligned','concordant_unique','concordant_multiple','discordant_unique']), path
    assert row['unpaired_total'] == 2 * row['pair_unaligned'], path
    assert row['unpaired_total'] == sum(row[k] for k in ['unpaired_unaligned','unpaired_unique','unpaired_multiple']), path
    assert abs(100 * (1-row['unpaired_unaligned']/(2*n)) - row['overall_alignment_pct']) <= 0.0051, path
    for key, pattern in FIELDS[1:]:
        if key == 'unpaired_total':
            continue
        pct = float(re.search(pattern + r' \(([\d.]+)%\)', text).group(2))
        denominator = row['unpaired_total'] if key.startswith('unpaired_') else n
        assert abs(100*row[key]/denominator-pct) <= 0.0051, (path,key,pct)
    for key in ['concordant_unique','concordant_multiple','discordant_unique']:
        row[key+'_pct'] = 100*row[key]/n
    sample = path.stem.replace('_siRNA_', ' ')
    if sample == 'SRR24828472':
        sample = 'KRAS P5_v2'
    row.update(sample=sample, run_accession=ACCESSIONS[sample],
               source_file=str(path.relative_to(HERE)), sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
               pairing_review='flagged_unresolved' if sample=='KRAS M1' else 'no_comparable_summary_anomaly')
    return row

def build():
    rows = [parse(p) for p in sorted((HERE/'raw').glob('*.txt'))]
    assert len(rows)==17 and len({r['sample'] for r in rows})==17
    rows.sort(key=lambda r: list(ACCESSIONS).index(r['sample']))
    result = {
        'as_of':'2026-09-22', 'scope':'17 full sequencing runs. The earlier 1-million-pair pilots are excluded.',
        'metric_definitions':{
            'overall_alignment_pct':'100 * (1 - unaligned reads / (2 * input pairs)). Includes reads aligned separately from their mate.',
            'concordant_unique_pct':'100 * concordant unique pairs / input pairs',
            'discordant_unique_pct':'100 * discordant unique pairs / input pairs',
        },
        'total_pairs':sum(r['total_pairs'] for r in rows),
        'overall_alignment_pct_range':[min(r['overall_alignment_pct'] for r in rows), max(r['overall_alignment_pct'] for r in rows)],
        'flagged_samples':['KRAS M1'],
        'validation_limit':'These checks cover the text summaries. They do not inspect read names, pairing order or BAM files, or determine whether a run is suitable for gene counting.',
        'samples':rows,
    }
    (HERE/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='samples'},indent=2))
    return result

if __name__ == '__main__':
    build()
