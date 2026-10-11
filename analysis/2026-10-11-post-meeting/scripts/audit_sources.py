import sys,json,subprocess
from pathlib import Path
import pandas as pd
root=Path(sys.argv[1]).resolve();base=root/'analysis/2026-10-11-post-meeting';r=base/'results';s=base/'sources'
j=pd.read_csv(r/'full_joint_2020_stability.tsv',sep='\t')
j[~j.both_direction_stable_all8].to_csv(r/'full_joint_missing_rounds.tsv',sep='\t',index=False)
j[j.either_effect_drift_ge05].sort_values('DESeq2_LOO_max_abs_delta',ascending=False).to_csv(r/'full_joint_effect_drift_ge05.tsv',sep='\t',index=False)
rows=[]
for scenario in ['merge_p5','retain_SRR24828472','retain_SRR24828471']:
    old=root/f'analysis/2026-10-04-week4/results/{scenario}'
    d=pd.read_csv(old/'DESeq2_full.tsv',sep='\t',dtype={'ENTREZID':str}).set_index('ENTREZID')
    e=pd.read_csv(old/'edgeR_full.tsv',sep='\t',dtype={'ENTREZID':str}).set_index('ENTREZID')
    assert d.index.equals(e.index)
    dg=d.padj.lt(.05)&d.log2FoldChange.abs().gt(.5);eg=e.FDR.lt(.05)&e.logFC.abs().gt(.5)
    rows.append(dict(scenario=scenario,DESeq2_unshrunk_gate=int(dg.sum()),edgeR_reported_gate=int(eg.sum()),intersection=int((dg&eg).sum()),source='archived Week4 fits; recalculated screens, no new single-library fits'))
pd.DataFrame(rows).to_csv(r/'p5_choices_screening_audit.tsv',sep='\t',index=False)
code='suppressPackageStartupMessages(library(edgeR));stopifnot(packageVersion("edgeR")=="4.8.2");cat(deparse(edgeR:::glmLRT),sep="\\n");cat("\\nFIT\\n");cat(deparse(edgeR:::glmFit.default),sep="\\n")'
source=subprocess.check_output(['Rscript','-e',code],text=True)
assert 'prior.count = 0.125' in source and 'logFC <- glmfit$coefficients' in source and 'fit$unshrunk.coefficients <- fit$coefficients' in source
(s/'edgeR_installed_effect_source.txt').write_text(source)
(s/'effect_definitions.json').write_text(json.dumps({'DESeq2_primary':'results() log2FoldChange; before apeglm shrinkage','DESeq2_display_alternative':'lfcShrink(type=apeglm); posterior effect and posterior SD','edgeR_primary':'glmQLFTest() reported logFC from fitted coefficients; default prior.count=0.125','edgeR_evidence':'installed edgeR 4.8.2 glmFit.default and glmLRT; edgeR_installed_effect_source.txt','screen':'adjusted P<0.05 AND abs(primary effect)>0.5 after zero-effect testing'},indent=2))
print('Archived P5 screens, missing-round and amplitude-change tables, and installed effect definitions verified.')
