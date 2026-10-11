"""Audit raw inputs, validate nine fits, and summarize effect stability without pooling P values."""
import sys, json, hashlib
from pathlib import Path
import numpy as np
import pandas as pd

root = Path(sys.argv[1]).resolve()
base = root / 'analysis/2026-10-11-post-meeting'
res = base / 'results'
sources = base / 'sources'
sources.mkdir(exist_ok=True)
read = lambda p: pd.read_csv(p, sep='\t', dtype={'ENTREZID':str})
save = lambda df, p: df.to_csv(p, sep='\t', index=False, na_rep='NA', float_format='%.15g')
src = root / 'analysis/2026-10-01/counts'
raw = read(src/'counts_raw.txt').set_index('ENTREZID')
meta = read(src/'sample_annotation.txt')
assert raw.shape == (28395,17) and raw.index.is_unique
assert list(raw.columns) == list(meta.sample_name)
assert np.isfinite(raw.values).all() and (raw.values>=0).all() and (raw.values==np.floor(raw.values)).all()
for _, row in meta.iterrows():
    t = read(src/'raw_counts'/f'{row.sample_name}.tabular')
    t.columns = ['ENTREZID','count']
    t.ENTREZID = t.ENTREZID.astype(str)
    t = t.set_index('ENTREZID')
    assert set(t.index) == set(raw.index)
    assert np.array_equal(raw[row.sample_name],t.loc[raw.index,'count'])
    assert raw[row.sample_name].sum() == row.assigned_counts
ena_path = root/'analysis/2026-10-04-week4/sources/ena_runs_2026-10-04.tsv'
ena = read(ena_path)
identity = meta.merge(ena,on='run_accession',validate='one_to_one')
assert (identity.ena_alias==identity.sample_alias).all()
save(identity, sources/'sample_ena_mapping.tsv')
save(identity[identity.cell_line.eq('MiaPaca-2')], sources/'p5_ena_mapping.tsv')
merged = read(res/'merged_counts.tsv').set_index('ENTREZID')
for (line,cond), rows in meta.groupby(['cell_line','condition']):
    assert np.array_equal(merged[f'{line}_{cond}'],raw[rows.sample_name].sum(axis=1))
coverage = read(res/'round_coverage.tsv')
lines = sorted(meta.cell_line.unique())
assert len(coverage)==9 and set(coverage.omitted_cell_line)-{'NONE'}==set(lines)
for _, row in coverage.iterrows():
    samples = read(res/row['round']/'samples.tsv')
    design = read(res/row['round']/'design.tsv').drop(columns='sample').values
    assert np.linalg.matrix_rank(design)==design.shape[1]==row.design_rank
    assert row.observations==len(samples) and row.residual_df==len(samples)-design.shape[1]
    assert (samples.groupby('cell_line').condition.apply(lambda x:set(x)=={'Control','Treatment'})).all()
    if row.omitted_cell_line!='NONE':
        assert row.omitted_cell_line not in set(samples.cell_line)
        assert len(samples)==14 and len(row.excluded_samples.split(';'))==2

full = {m:read(res/'full'/f'{m}_full.tsv').set_index('ENTREZID') for m in ['DESeq2','edgeR']}
cols = {'DESeq2':('log2FoldChange','padj'), 'edgeR':('logFC','FDR')}
loo = {m:{line:read(res/f'omit_{line}'/f'{m}_full.tsv').set_index('ENTREZID').reindex(full[m].index) for line in lines} for m in full}
gate = lambda d,m: d[cols[m][1]].lt(.05)&d[cols[m][0]].abs().gt(.5)
baseline_checks={}
for m in full:
    old=read(root/f'analysis/2026-10-04-week4/results/merge_p5/{m}_full.tsv').set_index('ENTREZID')
    checks={}
    for col in [cols[m][0],cols[m][1], 'pvalue' if m=='DESeq2' else 'PValue']:
        assert full[m].index.equals(old.index)
        a,b=full[m][col].to_numpy(),old[col].to_numpy()
        assert np.array_equal(np.isnan(a),np.isnan(b))
        checks[col]=float(np.nanmax(np.abs(a-b)))
        assert np.allclose(a,b,rtol=1e-10,atol=1e-12,equal_nan=True)
    baseline_checks[m]=checks
assert gate(full['DESeq2'],'DESeq2').sum()==2088
assert gate(full['edgeR'],'edgeR').sum()==2919
assert (gate(full['DESeq2'],'DESeq2') & gate(full['edgeR'],'edgeR')).sum()==2020
ds=full['DESeq2'].padj.lt(.05)&full['DESeq2'].log2FC_apeglm.abs().gt(.5)
assert ds.sum()==1702 and (ds&gate(full['edgeR'],'edgeR')).sum()==1690
screens=[]
for name,lfc,fdr in [('DESeq2_unshrunk',full['DESeq2'].log2FoldChange,full['DESeq2'].padj),('DESeq2_apeglm',full['DESeq2'].log2FC_apeglm,full['DESeq2'].padj),('edgeR',full['edgeR'].logFC,full['edgeR'].FDR)]:
    for cutoff in [0,.5]:
        g=fdr.lt(.05)&lfc.abs().gt(cutoff)
        screens.append(dict(method_effect=name,FDR_lt=.05,abs_log2FC_gt=cutoff,selected=int(g.sum()),down=int((g&lfc.lt(0)).sum()),up=int((g&lfc.gt(0)).sum())))
save(pd.DataFrame(screens),res/'screening_audit.tsv')

joint_base=gate(full['DESeq2'],'DESeq2')&gate(full['edgeR'],'edgeR')
metrics=[]; summaries={}; long=[]
for m in full:
    fc,pc=cols[m]; b=full[m]
    effects=pd.DataFrame({l:loo[m][l][fc] for l in lines})
    adjusted=pd.DataFrame({l:loo[m][l][pc] for l in lines})
    finite=np.isfinite(effects); same=effects.mul(np.sign(b[fc]),axis=0).gt(0)&finite
    gates=adjusted.lt(.05)&effects.abs().gt(.5)
    abs_gate=effects.abs().gt(.5)&finite
    delta=effects.sub(b[fc],axis=0).abs()
    s=b[['SYMBOL','GENENAME',fc,pc]].rename(columns={fc:'full_log2FC',pc:'full_adjusted_p'}).copy()
    s['full_screen_pass']=gate(b,m); s['full_joint_screen_pass']=joint_base
    s['finite_effect_rounds']=finite.sum(axis=1); s['finite_adjusted_p_rounds']=np.isfinite(adjusted).sum(axis=1)
    s['same_direction_rounds']=same.sum(axis=1); s['FDR05_rounds']=adjusted.lt(.05).sum(axis=1)
    s['absLFC_gt05_rounds']=abs_gate.sum(axis=1); s['screen_pass_rounds']=gates.sum(axis=1)
    s['LOO_min_log2FC']=effects.min(axis=1); s['LOO_max_log2FC']=effects.max(axis=1)
    s['LOO_mean_log2FC']=effects.mean(axis=1); s['LOO_median_log2FC']=effects.median(axis=1)
    s['LOO_min_abs_log2FC']=effects.abs().min(axis=1); s['LOO_max_abs_delta']=delta.max(axis=1)
    s['max_delta_omitted_cell_line']=delta.fillna(-1).idxmax(axis=1).where(finite.any(axis=1))
    s['LOO_max_abs_delta_over_full_abs']=s.LOO_max_abs_delta/s.full_log2FC.abs().replace(0,np.nan)
    s['direction_stable_all8']=s.finite_effect_rounds.eq(8)&s.same_direction_rounds.eq(8)
    s['descriptive_screen_ge7of8']=s.full_screen_pass&s.direction_stable_all8&s.screen_pass_rounds.ge(7)
    s['descriptive_screen_all8']=s.full_screen_pass&s.direction_stable_all8&s.screen_pass_rounds.eq(8)
    s['effect_drift_flag_ge05']=s.LOO_max_abs_delta.ge(.5)
    s.index.name='ENTREZID'; save(s.reset_index(),res/f'{m}_gene_stability.tsv'); summaries[m]=s
    for line in lines:
        d=loo[m][line]; f=d[fc]; p=d[pc]
        finite_pair=np.isfinite(b[fc])&np.isfinite(f)
        nonzero=finite_pair&b[fc].ne(0)&f.ne(0)
        base_gate=gate(b,m); new_gate=gate(d,m)
        for scope, mask in [('all_finite_effects',finite_pair),('full_method_screen',finite_pair&base_gate),('full_joint_screen',finite_pair&joint_base)]:
            x,y=b.loc[mask,fc],f[mask]; dif=(y-x).abs()
            sg=mask&nonzero
            metrics.append(dict(method=m,omitted_cell_line=line,scope=scope,n_baseline=int({'all_finite_effects':np.isfinite(b[fc]),'full_method_screen':base_gate,'full_joint_screen':joint_base}[scope].sum()),
              n_finite=int(mask.sum()),n_nonzero=int(sg.sum()),pearson=x.corr(y),spearman=x.corr(y,method='spearman'),
              direction_agreement=float((np.sign(b.loc[sg,fc])==np.sign(f[sg])).mean()),median_abs_delta=dif.median(),p95_abs_delta=dif.quantile(.95),
              reference_screen_retained=int((mask&base_gate&new_gate).sum()),method_screen_Jaccard=float((base_gate&new_gate).sum()/(base_gate|new_gate).sum())))
        q=pd.DataFrame({'ENTREZID':b.index,'SYMBOL':b.SYMBOL.values,'method':m,'omitted_cell_line':line,'full_log2FC':b[fc].values,
            'LOO_log2FC':f.values,'LOO_adjusted_p':p.values,'full_screen_pass':base_gate.values,'LOO_screen_pass':new_gate.values,
            'LOO_status':d.status.values,'abs_delta':(f-b[fc]).abs().values})
        long.append(q)
save(pd.DataFrame(metrics),res/'effect_stability_by_round.tsv')
save(pd.concat(long,ignore_index=True),res/'loo_long.tsv')
joint=summaries['DESeq2'][['SYMBOL','GENENAME']].copy()
for m,s in summaries.items():
    for col in s.columns:
        if col not in ['SYMBOL','GENENAME']: joint[f'{m}_{col}']=s[col]
joint['full_joint_screen_pass']=joint_base
joint['both_direction_stable_all8']=summaries['DESeq2'].direction_stable_all8&summaries['edgeR'].direction_stable_all8
joint['both_descriptive_ge7of8']=summaries['DESeq2'].descriptive_screen_ge7of8&summaries['edgeR'].descriptive_screen_ge7of8
joint['both_descriptive_all8']=summaries['DESeq2'].descriptive_screen_all8&summaries['edgeR'].descriptive_screen_all8
joint_gates=pd.DataFrame({line:gate(loo['DESeq2'][line],'DESeq2')&gate(loo['edgeR'][line],'edgeR') for line in lines})
joint['simultaneous_joint_screen_rounds']=joint_gates.sum(axis=1)
joint['joint_descriptive_ge7of8']=joint_base&joint.both_direction_stable_all8&joint.simultaneous_joint_screen_rounds.ge(7)
joint['joint_descriptive_all8']=joint_base&joint.both_direction_stable_all8&joint.simultaneous_joint_screen_rounds.eq(8)
joint['either_effect_drift_ge05']=summaries['DESeq2'].effect_drift_flag_ge05|summaries['edgeR'].effect_drift_flag_ge05
joint.index.name='ENTREZID'; save(joint.reset_index(),res/'joint_gene_stability.tsv')
save(joint[joint.full_joint_screen_pass].reset_index(),res/'full_joint_2020_stability.tsv')
save(joint[joint.joint_descriptive_ge7of8].reset_index(),res/'descriptive_joint_ge7of8.tsv')
save(joint[joint.joint_descriptive_all8].reset_index(),res/'descriptive_joint_all8.tsv')
candidate=read(root/'analysis/2026-10-04-week4/results/candidate_review.tsv').ENTREZID.tolist()
save(joint.reindex(candidate).reset_index(),res/'candidate_stability.tsv')
save(pd.concat(long).query('ENTREZID in @candidate'),res/'candidate_loo_long.tsv')
totals={m:{k:int(s[k].sum()) for k in ['full_screen_pass','direction_stable_all8','descriptive_screen_ge7of8','descriptive_screen_all8']} for m,s in summaries.items()}
jb=joint[joint.full_joint_screen_pass]
totals['full_joint_2020']={'baseline':len(jb),'both_direction_all8':int(jb.both_direction_stable_all8.sum()),
 'both_ge7of8':int(jb.both_descriptive_ge7of8.sum()),'both_all8':int(jb.both_descriptive_all8.sum()),
 'simultaneous_joint_ge7of8':int(jb.joint_descriptive_ge7of8.sum()),'simultaneous_joint_all8':int(jb.joint_descriptive_all8.sum()),
 'either_effect_drift_ge05':int(jb.either_effect_drift_ge05.sum())}
(res/'stability_totals.json').write_text(json.dumps(totals,indent=2))
manifest={'gene_rows':28395,'raw_runs':17,'merged_observations':16,'LOO_rounds':8,'all_integer_nonnegative':True,
 'raw_run_tables_match':True,'assigned_counts_match':True,'ENA_saved_snapshot_matches':True,'ENA_snapshot_date':'2026-10-04',
 'P5_raw_integer_sum_exact':True,'all_designs_full_rank':True,'each_omission_removes_Control_Treatment_pair':True,
 'baseline_week4_numerical_match':baseline_checks,'expected_screen_counts_verified':True,
 'nonconverged_DESeq2_by_round':dict(zip(read(res/'round_summary.tsv')['round'],read(res/'round_summary.tsv').DESeq2_beta_nonconverged)),
 'sha256':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [src/'counts_raw.txt',src/'sample_annotation.txt',src/'annotate_geneID.txt',ena_path]}}
(sources/'input_and_model_validation.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(totals,indent=2))
