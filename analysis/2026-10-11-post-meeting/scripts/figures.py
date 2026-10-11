import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

base=Path(sys.argv[1]); r=base/'results'; out=base/'figures';out.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':220})
colors={'DESeq2':'#176B9A','edgeR':'#C66B2C'}
def finish(fig,name):
    fig.savefig(out/f'{name}.png',bbox_inches='tight');fig.savefig(out/f'{name}.pdf',bbox_inches='tight');plt.close(fig)

fig,ax=plt.subplots(figsize=(8.2,3.3),layout='constrained')
labels=['DESeq2 model LFC','DESeq2 apeglm LFC','edgeR reported LFC','Joint: model + edgeR','Joint: apeglm + edgeR']
values=[2088,1702,2919,2020,1690]
ax.barh(labels[::-1],values[::-1],color=['#4A6572','#718691','#C66B2C','#7AA8C1','#176B9A'])
for i,v in enumerate(values[::-1]): ax.text(v+35,i,f'{v:,}',va='center')
ax.set_xlim(0,3300);ax.set_xlabel('Genes selected: adjusted P < 0.05 and |log2FC| > 0.5')
ax.set_title('Full fit: the effect definition changes the screened list',loc='left',fontweight='bold')
finish(fig,'F1_effect_definition_screening')

metrics=pd.read_csv(r/'effect_stability_by_round.tsv',sep='\t');metrics=metrics[metrics.scope.eq('full_joint_screen')]
order=['HPAC','MiaPaca-2','Pa01C','Pa02C','Pa04C','Pa14C','Pa16C','PANC-1']
fig,axes=plt.subplots(1,2,figsize=(9.1,3.8),layout='constrained');y=np.arange(8)
for m,off in [('DESeq2',-.12),('edgeR',.12)]:
    t=metrics[metrics.method.eq(m)].set_index('omitted_cell_line').loc[order]
    axes[0].plot(t.pearson,y+off,'o-',color=colors[m],label=m)
    axes[1].plot(t.p95_abs_delta,y+off,'o-',color=colors[m],label=m)
    axes[1].plot(t.median_abs_delta,y+off,'x',color=colors[m])
for ax in axes: ax.set_yticks(y,order);ax.invert_yaxis();ax.grid(axis='x',alpha=.25)
axes[0].set_xlim(.98,1.001);axes[0].set_xlabel('Pearson correlation with full-fit log2FC');axes[0].legend(loc='lower left',fontsize=9)
axes[1].set_xlim(0,.25);axes[1].set_xlabel('|LOO - full| log2FC: o = 95th percentile, x = median')
fig.suptitle('Omit one Control/Treatment pair: full-fit joint list (2,020 genes)',fontweight='bold')
finish(fig,'F2_effect_stability')

c=pd.read_csv(r/'candidate_stability.tsv',sep='\t').set_index('SYMBOL')
orderc=['KRAS','DUSP6','SPRY4','CCND1','EMP2','MYC','DPM3','EGR1','WNT5A','SFRP1','TGFBR3'];c=c.loc[orderc]
long=pd.read_csv(r/'candidate_loo_long.tsv',sep='\t')
fig,axes=plt.subplots(1,2,figsize=(9.1,4.6),sharex=True,sharey=True,layout='constrained');y=np.arange(len(c))
for ax,m in zip(axes,['DESeq2','edgeR']):
    ax.hlines(y,c[f'{m}_LOO_min_log2FC'],c[f'{m}_LOO_max_log2FC'],color=colors[m],lw=2)
    for i,symbol in enumerate(orderc):
        vals=long[long.SYMBOL.eq(symbol)&long.method.eq(m)].LOO_log2FC
        ax.scatter(vals,[i]*len(vals),s=15,color=colors[m],alpha=.5,zorder=3)
    ax.scatter(c[f'{m}_full_log2FC'],y,marker='D',color='black',s=24,zorder=4,label='Full fit')
    for v in [-.5,.5]: ax.axvline(v,color='#777777',ls='--',lw=.8)
    ax.axvline(0,color='#bbbbbb',lw=.8);ax.set_title(m);ax.grid(axis='y',alpha=.15);ax.set_xlim(-3.15,2.9)
    ax.set_xlabel('Treatment / Control log2FC');ax.set_yticks(y,orderc)
axes[0].invert_yaxis();axes[1].legend(loc='lower right',fontsize=8)
fig.suptitle('Candidate effects: full-fit diamonds and eight omission-fit estimates',fontweight='bold')
finish(fig,'F3_candidate_effects')

j=pd.read_csv(r/'full_joint_2020_stability.tsv',sep='\t');freq=j.simultaneous_joint_screen_rounds.value_counts().reindex(range(9),fill_value=0)
fig,ax=plt.subplots(figsize=(8.2,3.1),layout='constrained');ax.bar(freq.index,freq.values,color=['#94A6AF']*7+['#176B9A','#104B6A'])
for i,v in freq.items():ax.text(i,v+18,str(v),ha='center',fontsize=9)
ax.set_ylim(0,1460);ax.set_xticks(range(9));ax.set_xlabel('Rounds simultaneously passing adjusted P < 0.05 and |log2FC| > 0.5 in both methods')
ax.set_ylabel('Full-fit joint genes');ax.set_title('Screen stability: 1,515 genes pass in at least 7 of the same 8 rounds',loc='left',fontweight='bold')
finish(fig,'F4_joint_screen_stability')
