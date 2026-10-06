"""Build and audit the source snapshot without histories, course files or dependencies.
Usage: python package.py REPO_ROOT OUTPUT.zip
"""
import sys,hashlib,json,re,zipfile
from pathlib import Path
repo,target=map(Path,sys.argv[1:3]);analysis=repo/'analysis/2026-10-04-week4'
paths=list(analysis.rglob('*'))+list((repo/'analysis/2026-10-01/counts').rglob('*'))
paths+=[repo/'analysis/2026-10-01/README.md']
paths+=list((repo/'reports').glob('PDAC_KRAS_Week4_2026-10-0[46]_v[12]*'))
paths=[p for p in paths if p.is_file() and not any(x in p.parts for x in ['runtime','__pycache__','.git'])]
deny={'.mp4','.mov','.mkv','.fastq','.fq','.bam','.sam','.cram','.key','.pem','.TTF','.ttf','.Rmd'}
secret=re.compile(rb'(?:gh[pousr]_[A-Za-z0-9]{20,}|(?:AKIA|ASIA)[A-Z0-9]{16}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|[?&](?:X-Amz-Signature|sig)=[A-Za-z0-9%]{20,})')
entries={};records=[]
for p in sorted(set(paths)):
    assert p.suffix not in deny and not p.name.startswith('.env'),str(p)
    assert p.stat().st_size<50*1024**2,str(p)
    data=p.read_bytes();assert not secret.search(data),f'Potential secret in {p}'
    if p.suffix=='.docx':
        with zipfile.ZipFile(p) as z:
            for n in z.namelist():
                if n.endswith('.xml'):assert not secret.search(z.read(n)),f'Potential secret in {p}:{n}'
    name=str(p.relative_to(repo));entries[name]=data;records.append(dict(file=name,size=len(data),sha256=hashlib.sha256(data).hexdigest()))
entries['README.md']=b'# PDAC KRAS Week 4 source snapshot version 2\n\nStart with analysis/2026-10-04-week4/README.md. The current report is reports/PDAC_KRAS_Week4_2026-10-06_v2.pdf and its DOCX. Version 1 is retained for reference. This snapshot contains the real input counts and original run tables, analysis/report source, version locks, complete results and figures. The October 6 revision clarifies P5 handling and edits the report text; numerical results and figures are unchanged. See MANIFEST.json for file checksums. Private course originals, raw reads, recordings, credentials and installed runtimes are excluded. The paper benchmark needs an authorized Data S1 CSV, whose identity is recorded in classroom_provenance.json. Earlier repository history is not included.\n'
records.append(dict(file='README.md',size=len(entries['README.md']),sha256=hashlib.sha256(entries['README.md']).hexdigest()))
manifest=dict(input_commit='462867100fa1628d716cb7722a574da5f90577df',analysis_commit='6f34d7fe90474f61d3519574ecccfa22d4880e41',snapshot_date='2026-10-06',report_revision=2,file_count=len(entries),archive_entry_count=len(entries)+1,uncompressed_bytes=sum(map(len,entries.values())),secrets_scan_passed=True,private_course_originals_excluded=True,raw_reads_alignments_recordings_fonts_runtime_excluded=True,files=records)
entries['MANIFEST.json']=json.dumps(manifest,indent=2).encode()
target.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for name,data in sorted(entries.items()):
        zi=zipfile.ZipInfo(name,date_time=(2026,10,6,0,0,0));zi.compress_type=zipfile.ZIP_DEFLATED;z.writestr(zi,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
with zipfile.ZipFile(target) as z:
    assert z.testzip() is None
    for r in records:assert hashlib.sha256(z.read(r['file'])).hexdigest()==r['sha256']
result=dict(package=str(target),bytes=target.stat().st_size,sha256=hashlib.sha256(target.read_bytes()).hexdigest(),CRC_and_all_file_hashes_verified=True,source_file_count=len(entries),secrets_and_exclusions_passed=True)
print(json.dumps(result,indent=2))
