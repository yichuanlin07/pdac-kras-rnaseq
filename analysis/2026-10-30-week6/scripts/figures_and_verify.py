from pathlib import Path
import json
import hashlib
import textwrap
import sys
import numpy as np
import pandas as pd
from scipy.stats import hypergeom
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.lines import Line2D

ROOT=Path(__file__).resolve().parents[1]
OUT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT
P=OUT/'results'; F=OUT/'figures'
F.mkdir(exist_ok=True)
BLUE='#2166AC'; RED='#B2182B'; LAPIS='#26619C'
plt.rcParams.update({'font.family':'serif','font.serif':['Times New Roman','DejaVu Serif'],
                     'font.size':9,'axes.titlesize':10,'axes.labelsize':9,
                     'savefig.facecolor':'white','pdf.fonttype':42,'ps.fonttype':42})
def read(name): return pd.read_csv(P/name,sep='\t')
def bh(p):
    p=np.asarray(p,float); order=np.argsort(p,kind='stable')
    q=np.minimum.accumulate((p[order]*len(p)/np.arange(1,len(p)+1))[::-1])[::-1]
    result=np.empty(len(p));result[order]=np.minimum(q,1);return result
def label(s):
    result=s.replace('HALLMARK_','').replace('REACTOME_','').replace('_',' ').capitalize()
    for old,new in [('E2f','E2F'),('G2m','G2M'),('Kras','KRAS'),('Myc','MYC'),('Dna','DNA'),('Tnfa','TNFA'),('nfkb','NF-kB'),('atr','ATR'),(' v1',' V1'),(' v2',' V2')]:
        result=result.replace(old,new)
    if s.startswith('HALLMARK_KRAS_SIGNALING_'): result=result.rsplit(' ',1)[0]+' '+s.rsplit('_',1)[1]
    return result
def save(fig,name):
    fig.savefig(F/(name+'.png'),dpi=300,bbox_inches='tight',pad_inches=.08)
    fig.savefig(F/(name+'.pdf'),bbox_inches='tight',pad_inches=.08)
    plt.close(fig)

cam=read('camera_all_fits.tsv'); ora=read('ora_all.tsv'); summary=read('fit_summary.tsv')
full=cam[cam.fit=='full'].set_index('gene_set')
fixed=read('camera_full_fixed_correlation_001.tsv').set_index('gene_set')
for name,x in cam.groupby('fit'):
    assert np.allclose(x.q_global,bh(x.PValue),rtol=1e-10,atol=1e-14)
    assert x.gene_set.is_unique and x.NGenes.between(15,500).all()
assert len(full)==1172 and (full.q_global>=.05).all()
for keys,x in ora.groupby(['list','background']):
    expected=hypergeom.sf(x.hits-1,x.universe,x.set_measured,x.selected)
    assert np.allclose(expected,x.PValue,rtol=1e-8,atol=1e-20)
    assert np.allclose(bh(x.PValue),x.q_global,rtol=1e-9,atol=1e-14)
    assert (x.hits<=np.minimum(x.selected,x.set_measured)).all()
prior=pd.read_csv(OUT/'sources/prior_filter.tsv',sep='\t',dtype={'ENTREZID':str})
current=read('gene_effects_full.tsv')
assert list(prior.loc[prior.prefilter_pass,'ENTREZID'])==list(current.ENTREZID.astype(str))
assert summary.observations.tolist()==[16]+[14]*8+[16]*2
assert summary['rank'].tolist()==[9]+[8]*8+[9]*2
assert summary.residual_df.tolist()==[7]+[6]*8+[7]*2
assert (summary.significant_global==0).all()
pooled=read('samples_full.tsv')
assert pooled.loc[pooled.sample_name=='KRAS_MiaPaca2_pooled','library_counts'].item()==68124190
direction=read('joint_2020_direction_audit.tsv')
assert len(direction)==2020 and direction.same_direction.all()

primary=ora[(ora['list']=='full_joint')&(ora.background=='eligible')].copy()
stable=ora[(ora['list']=='stable_ge7of8')&(ora.background=='eligible')]
sig=primary[primary.q_global<.05]
assert len(sig)==46
hall=sig[sig.collection=='Hallmark'].sort_values('q_global')
hall.to_csv(P/'report_hallmark_ora.tsv',sep='\t',index=False)

def oraplot(x,name):
    x=x.iloc[::-1].reset_index(drop=True)
    fig,ax=plt.subplots(figsize=(6.7,3.05 if len(x)<10 else 3.5))
    y=np.arange(len(x));colors=x.direction.map({'Down':BLUE,'Up':RED})
    for i,r in x.iterrows():
        ax.plot([1,r.fold_enrichment],[i,i],color='#D9D9D9',lw=1,zorder=1)
    ax.scatter(x.fold_enrichment,y,s=18+x.hits*2,c=colors,edgecolor='white',linewidth=.5,zorder=3)
    ax.set_yticks(y,[textwrap.fill(label(v),41) for v in x.gene_set],fontsize=8.5)
    ax.axvline(1,color='#777777',lw=.7,ls='--')
    ax.set_xlabel('Observed overlap / expected overlap')
    ax.set_xlim(.8,x.fold_enrichment.max()*1.17)
    for i,r in x.iterrows(): ax.text(r.fold_enrichment+.08,i,str(r.hits),va='center',fontsize=8)
    ax.spines[['top','right','left']].set_visible(False);ax.tick_params(axis='y',length=0)
    ax.legend(handles=[Line2D([],[],marker='o',linestyle='',color=BLUE,label='Lower after KRAS siRNA'),
                       Line2D([],[],marker='o',linestyle='',color=RED,label='Higher after KRAS siRNA')],
              loc='upper center',bbox_to_anchor=(.48,1.18),frameon=False,ncol=2,fontsize=8)
    fig.tight_layout(pad=.4);save(fig,name)
oraplot(hall,'B1_hallmark_ora')
react=pd.concat([sig[(sig.collection=='Reactome')&(sig.direction=='Down')].nsmallest(6,'q_global'),
                 sig[(sig.collection=='Reactome')&(sig.direction=='Up')].nsmallest(3,'q_global')]).sort_values('q_global')
react.to_csv(P/'report_reactome_ora.tsv',sep='\t',index=False)
oraplot(react,'B2_reactome_ora')

chosen=['HALLMARK_E2F_TARGETS','HALLMARK_G2M_CHECKPOINT','HALLMARK_KRAS_SIGNALING_UP',
        'HALLMARK_KRAS_SIGNALING_DN','HALLMARK_MYC_TARGETS_V1','HALLMARK_MYC_TARGETS_V2',
        'HALLMARK_INTERFERON_ALPHA_RESPONSE','HALLMARK_CHOLESTEROL_HOMEOSTASIS']
rows=[]
for term in chosen:
    c=full.loc[term];o=primary[(primary.gene_set==term)&(primary.direction==c.Direction)].iloc[0]
    st=stable[(stable.gene_set==term)&(stable.direction==c.Direction)].iloc[0]
    rows.append({'gene_set':term,'direction':c.Direction,'ORA_q':o.q_global,'ORA_hits':o.hits,
                 'CAMERA_q':c.q_global,'CAMERA_p':c.PValue,'CAMERA_rho':c.Correlation,
                 'fixed_001_q':fixed.loc[term,'q_global'],'stable_ORA_q':st.q_global,'stable_hits':st.hits})
compare=pd.DataFrame(rows);compare.to_csv(P/'report_method_comparison.tsv',sep='\t',index=False)
fig,ax=plt.subplots(figsize=(6.7,3.35))
yy=np.arange(len(compare))[::-1]
for column,offset,colour,marker,title in [
 ('ORA_q',.20,LAPIS,'o','Threshold-list ORA'),
 ('CAMERA_q',0,'black','s','CAMERA estimated correlation'),
 ('fixed_001_q',-.20,'#929292','D','CAMERA fixed correlation 0.01')]:
    ax.scatter(-np.log10(compare[column]),yy+offset,c=colour,s=24,marker=marker,label=title,zorder=3)
ax.set_yticks(yy,[label(v) for v in compare.gene_set],fontsize=8.5)
ax.axvline(-np.log10(.05),color='#777',ls='--',lw=.8)
ax.text(-np.log10(.05)+.15,len(compare)-.35,'q = 0.05',fontsize=8,va='top')
ax.set_xlabel('-log10 adjusted P value')
ax.set_xlim(-.15,float(-np.log10(compare[['ORA_q','CAMERA_q','fixed_001_q']]).min().min())*1.08)
ax.spines[['top','right','left']].set_visible(False);ax.tick_params(axis='y',length=0)
ax.legend(frameon=False,loc='lower right',fontsize=8)
fig.tight_layout(pad=.6);save(fig,'C1_correlation_sensitivity')

fits=summary.fit.tolist();selected=chosen+['REACTOME_CELL_CYCLE_CHECKPOINTS']
matrix=cam.pivot(index='gene_set',columns='fit',values='Direction').loc[selected,fits]
assert matrix.isin(['Down','Up']).all().all(), 'Missing or invalid CAMERA direction in heatmap'
values=np.where(matrix.to_numpy()=='Down',0.,1.)
fig,ax=plt.subplots(figsize=(6.7,3.2))
ax.imshow(values,cmap=ListedColormap([BLUE,RED]),vmin=0,vmax=1,aspect='auto')
for i in range(values.shape[0]):
 for j in range(values.shape[1]):ax.text(j,i,'D' if values[i,j]==0 else 'U',ha='center',va='center',color='white',fontsize=8)
ax.set_yticks(range(len(selected)),[label(t) for t in selected],fontsize=8)
names=['Full']+[s.replace('omit_','') for s in fits[1:9]]+['P5 471','P5 472']
ax.set_xticks(range(len(fits)),names,rotation=65,ha='right',fontsize=8)
ax.tick_params(length=0);ax.spines[:].set_visible(False)
ax.set_xlabel('Columns 2-9 omit both conditions of the named cell line',labelpad=8)
fig.tight_layout(pad=.7);save(fig,'D1_direction_sensitivity')


de=pd.read_csv(OUT/'sources/DESeq2_full.tsv',sep='\t',dtype={'ENTREZID':str}).set_index('ENTREZID')
er=pd.read_csv(OUT/'sources/edgeR_full.tsv',sep='\t',dtype={'ENTREZID':str}).set_index('ENTREZID')
contrib=[]
for _,r in primary[(primary.gene_set.isin(chosen))&(primary.hits>0)].iterrows():
 for gene in r.hits_entrez.split(';'):
  contrib.append({'gene_set':r.gene_set,'direction':r.direction,'ENTREZID':gene,
                  'SYMBOL':de.loc[gene,'SYMBOL'],'DESeq2_log2FC':de.loc[gene,'log2FoldChange'],
                  'DESeq2_padj':de.loc[gene,'padj'],'edgeR_logFC':er.loc[gene,'logFC'],'edgeR_FDR':er.loc[gene,'FDR']})
pd.DataFrame(contrib).to_csv(P/'selected_pathway_contributors.tsv',sep='\t',index=False)
metrics={'input_gene_rows':28395,'input_runs':17,'full_observations':16,'retained_genes':17819,
         'camera_sets':1172,'Hallmark_sets':50,'Reactome_sets':1122,'primary_CAMERA_significant':0,
         'primary_CAMERA_min_global_q':float(full.q_global.min()),'primary_Hallmark_min_collection_q':float(full[full.collection=='Hallmark'].q_collection.min()),
         'camera_models':11,'ORA_background':15055,'ORA_joint_up':1275,'ORA_joint_down':745,
         'ORA_tests':len(primary),'ORA_significant_set_direction_tests':46,
         'ORA_Hallmark_significant':9,'ORA_Reactome_significant':37,
         'stable_list_genes':1515,'stable_ORA_significant':int((stable.q_global<.05).sum()),
         'fixed_correlation_significant':int((fixed.q_global<.05).sum()),
         'source_and_model_checks_passed':True,'independent_hypergeometric_and_BH_checks_passed':True,
         'software':{'numpy':np.__version__,'pandas':pd.__version__,'matplotlib':matplotlib.__version__}}
(OUT/'results/metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
print(json.dumps(metrics,indent=2))
