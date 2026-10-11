import sys,json,hashlib
from pathlib import Path
a,b=map(Path,sys.argv[1:3]);checks=[]
names=['merged_counts.tsv','merged_samples.tsv','round_summary.tsv','round_coverage.tsv','package_versions.tsv']
rounds=['full']+sorted(p.name for p in a.glob('omit_*') if p.is_dir())
for name in names:
    assert (a/name).read_bytes()==(b/name).read_bytes(),name
    checks.append(name)
for rnd in rounds:
    for p in sorted((a/rnd).iterdir()):
        if p.suffix in ['.tsv','.json']:
            relative=p.relative_to(a)
            assert p.read_bytes()==(b/relative).read_bytes(),str(relative)
            checks.append(str(relative))
assert len(rounds)==9
report={'nine_fits_rerun':True,'identical_files':len(checks),'all_compared_files_byte_identical':True,
 'excluded':['sessionInfo.txt (runtime text)'], 'files':checks}
(a.parent/'sources/repeat_run_validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='files'},indent=2))
