"""Create the formal weekly report by cloning the retained weekly template.
Usage: python report.py ANALYSIS_DIR TEMPLATE.docx OUTPUT.docx
Only body, figure relationships/media, content types and updateFields are changed.
"""
import sys,copy,re,json,zipfile,hashlib
from pathlib import Path
import pandas as pd
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph

base,template,target=map(Path,sys.argv[1:4]);target.parent.mkdir(parents=True,exist_ok=True)
res=base/'results';figs=base/'figures';read=lambda n:pd.read_csv(res/n,sep='\t')
sc=read('scenario_summary.tsv');ps=read('paper_comparison_summary.tsv');sen=read('sensitivity_full.tsv');pairs=read('candidate_pair_directions.tsv');validation=json.loads((res/'independent_numerical_validation.json').read_text())
doc=Document(template);patterns=[copy.deepcopy(p._p) for p in doc.paragraphs];body=doc._element.body
for child in list(body):
    if child.tag!=qn('w:sectPr'):body.remove(child)
def para(text='',pattern=4,cite=None):
    el=copy.deepcopy(patterns[pattern]);rp=None
    runs=el.findall(qn('w:r'))
    if runs:rp=copy.deepcopy(runs[0].find(qn('w:rPr')))
    for child in list(el):
        if child.tag!=qn('w:pPr'):el.remove(child)
    body.insert(len(body)-1,el);p=Paragraph(el,doc._body)
    r=p.add_run(text)
    if rp is not None:r._r.insert(0,rp)
    if cite:
        r=p.add_run(str(cite));r.font.name='Times New Roman';r.font.size=Pt(8);r.font.superscript=True
    return p
def heading(text,page=False):return para(text,15 if page else 3)
def cap(label,text,cite=None):
    para(label,17);para(text,18,cite)
def picture(name,width=6.72):
    p=para('',16);p.paragraph_format.keep_with_next=True
    p.add_run().add_picture(str(figs/(name+'.png')),width=Inches(width))
def table(headers,rows,widths=None):
    t=doc.add_table(rows=1,cols=len(headers));t.autofit=False
    if widths:
        for i,w in enumerate(widths):t.columns[i].width=Inches(w)
    for i,s in enumerate(headers):t.rows[0].cells[i].text=s
    for row in rows:
        cells=t.add_row().cells
        for i,s in enumerate(row):cells[i].text=str(s)
    for row in t.rows:
        pr=row._tr.get_or_add_trPr();pr.append(OxmlElement('w:cantSplit'))
        for i,c in enumerate(row.cells):
            if widths:c.width=Inches(widths[i])
            tcpr=c._tc.get_or_add_tcPr();shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'FFFFFF');tcpr.append(shade)
            for p in c.paragraphs:
                p.paragraph_format.space_before=Pt(0);p.paragraph_format.space_after=Pt(3);p.paragraph_format.line_spacing=1.05
                for r in p.runs:r.font.name='Times New Roman';r.font.size=Pt(9);r.font.color.rgb=RGBColor(0,0,0)
    for c in t.rows[0].cells:
        for r in c.paragraphs[0].runs:r.bold=True
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
    borders=OxmlElement('w:tblBorders')
    for edge in ['top','bottom','insideH','insideV','left','right']:
        e=OxmlElement('w:'+edge);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'4');e.set(qn('w:color'),'000000');borders.append(e)
    t._tbl.tblPr.append(borders)
    para('',18).paragraph_format.space_after=Pt(3)
    return t
def sci(x):return f'{x:.2g}'
num=lambda x:f'{int(x):,}'

para('KRAS suppression in pancreatic cancer cells',0)
para('RNA-SEQ WEEKLY PROGRESS REPORT | WEEK 4',1)
para('Yichuan Lin | University of Ottawa, Faculty of Science | 2026-10-04 | Version 1',2)
heading('1 Overview')
para('This week completes differential expression analysis of the real PRJNA980201 counts from eight pancreatic cancer cell lines. The study examines the response to KRAS siRNA relative to control siRNA. The published study provides a biological reference for this reanalysis.',cite=1)
heading('2 Work completed')
para('The 28,395-gene matrix matched all 17 original run tables and the sample metadata. Counts were nonnegative integers, sample order was exact, and assigned-count totals agreed. Public metadata confirmed the reversed local P5 naming: SRR24828471 is MP2_K2v2; SRR24828472 is MP2_K2.',cite=6)
para('Both classroom methods were implemented with the design ~condition + cell_line, Control as reference, and a common filter of at least 10 counts in two samples. The tutorial-matched exploratory main analysis sums the two P5 KRAS libraries, producing 16 observations, a full-rank nine-column design and seven residual degrees of freedom. DESeq2 uses size-factor normalization and a Wald test; edgeR uses TMM normalization and robust quasi-likelihood fitting.',cite='2,3,5')
para('At FDR < 0.05, DESeq2 detected 5,943 genes and edgeR detected 6,431, with 5,442 shared genes (Jaccard 0.785). Unshrunk log2FC estimates correlated at Pearson r = 0.884 across 17,819 genes. Cell-line differences dominate the displayed PCA; a lack of separation by treatment on the first two components does not negate the paired model result. Figures and detailed comparisons are in Appendices A-D.')
para('P5 was also analysed with each library retained separately. There were 5,084 genes significant with the same direction in both methods under all three choices. These fits share the same data and assess sensitivity, rather than independent replication. Two fresh complete runs reproduced all numerical outputs exactly; reversed contrasts negated log2FC and retained p values.')
heading('3 Next steps')
para('Prepare to discuss method assumptions, PCA, overlapping genes and the paper benchmark on Saturday, October 10. Resolve the P5 repeat type before drawing confirmatory conclusions. Review genes near the FDR boundary and assess cell-line-specific responses when the experimental design is clarified. LOO remains a topic for the next discussion. Prepare a progress update for next week.',cite=5)
heading('4 Summary')
para('The common KRAS siRNA response is consistent across methods and broadly stable to the P5 choice, but individual gene lists change. KRAS, DUSP6, SPRY4, MYC and CCND1 are robust downward candidates; EMP2 is a robust upward candidate. These are expression associations, not proof of direct regulation, protein change or therapeutic relevance. The unresolved repeat identity and different upstream pipeline limit interpretation.')

heading('Appendix A Sample structure and transformed expression',True)
picture('A1_PCA')
cap('Figure A1  PCA of the main 16-sample analysis','PCA uses the 500 most variable genes after DESeq2 VST (blind = FALSE) or edgeR TMM logCPM (prior count 2). Genes are centred without scaling; cell-line effects have not been removed. Blue circles denote Control; red triangles denote KRAS siRNA. Lines connect matched conditions. PC1/PC2 explain 35.1%/21.7% for DESeq2 and 33.7%/20.6% for edgeR. PCA is descriptive and does not test treatment significance.')
picture('A2_sample_distances')
cap('Figure A2  Sample distances','Euclidean distances use all 17,819 prefiltered genes on each method’s transformed scale, with complete-linkage ordering. C = Control; K = KRAS siRNA; MP2 = MiaPaca-2. Median within-line versus between-line distances are 32.3 versus 118.3 for VST, and 81.7 versus 304.2 for logCPM. Distances are not comparable in absolute magnitude across the two transformations. Most matched conditions cluster closely; this supports including cell line in the model.')

heading('Appendix B Differential expression and method comparison',True)
picture('B1_volcanoes')
cap('Figure B1  Differential expression after KRAS siRNA','Adjusted p values determine colour: blue = downregulated; red = upregulated; grey = FDR >= 0.05. The horizontal line is FDR 0.05. Positive log2FC means higher expression after KRAS siRNA. DESeq2 displays apeglm-shrunken effect sizes, while its Wald p values remain unchanged; edgeR displays its reported logFC. The different vertical scales reflect different tests and should not be read as equivalent evidence strength. No effect-size gate defines the primary DE lists.',4)
picture('B2_counts_and_agreement')
cap('Figure B2  Gene counts and unshrunk effect-size agreement','DESeq2: 2,912 down and 3,031 up. edgeR: 2,923 down and 3,508 up. The intersection is 5,442 and union 6,932; Jaccard = intersection/union = 0.785. The scatter uses unshrunk DESeq2 estimates for a fair effect-size comparison; shared DE genes are lapis blue. Pearson r = 0.884 and Spearman rho = 0.910 across all 17,819 shared finite estimates. Display axes are cropped to +/-8; correlations include every shared estimate.')
para('Both methods model overdispersed counts, but differ in normalization, dispersion moderation and inference. DESeq2 independently filters at alpha = 0.05, removing 2,764 genes after the shared low-count filter and leaving 15,055 finite adjusted p values. edgeR tests all 17,819 retained genes. Recalculating BH on their common finite-p universe gives 5,797 DESeq2 and 6,431 edgeR genes. Native output remains the primary result; the supplementary comparison separates test-universe effects from method effects.',18)

heading('Appendix C P5 sensitivity and limits',True)
para('Table C1  Differential expression under alternative P5 choices',17)
table(['P5 choice','Genes retained','DESeq2 DE','edgeR DE','Both methods'],[[{'merge_p5':'Sum both libraries','retain_SRR24828472':'Retain SRR24828472','retain_SRR24828471':'Retain SRR24828471'}[r.scenario],num(r.prefilter_pass),num(r.DESeq2_sig),num(r.edgeR_sig),num(r.overlap)] for r in sc.itertuples()],[2.1,1.2,1.1,1.1,1.2])
para('The two public runs have distinct sample accessions and FASTQ MD5 values. Their all-gene logCPM correlation is 0.993, but neither file identity nor correlation establishes technical or biological replication. Summing them is a tutorial assumption, not a resolved experimental fact. The alternative analyses preserve the original 17-run inputs.',18)
picture('C1_P5_sensitivity')
cap('Figure C1  Effect-size sensitivity to P5 handling','For merge versus retaining SRR24828472/SRR24828471, DESeq2 DE-list Jaccard values are 0.936/0.945; edgeR values are 0.932/0.920. Unshrunk log2FC correlations range from 0.992 to 0.996. Axes are cropped to +/-6; correlations use all finite paired estimates. Genes at the significance boundary can still change despite high global agreement.')
para('Table C2  Examples requiring cautious interpretation',17)
rows=[]
for sy in ['DPM3','EGR1','TGFBR3']:
    r=sen[sen.SYMBOL==sy].iloc[0];rows.append([sy,sci(r.merge_p5_DESeq2_padj),sci(r.merge_p5_edgeR_FDR),sci(r.retain_SRR24828472_edgeR_FDR),sci(r.retain_SRR24828471_edgeR_FDR)])
table(['Gene','DESeq2 FDR, sum','edgeR FDR, sum','edgeR FDR, 472','edgeR FDR, 471'],rows,[.8,1.5,1.5,1.5,1.4])
para('DPM3 loses edgeR significance when only SRR24828472 is used. EGR1 is significant in the main DESeq2 result but not edgeR; TGFBR3 is not significant in either main result. The additive model estimates a common treatment effect across lines and does not estimate a treatment-by-cell-line interaction. Eight paired cell lines do not establish within-line biological replication, and sensitivity to P5 cannot resolve that limitation.',18)

heading('Appendix D Benchmark against the original paper',True)
picture('D1_paper_benchmark')
cap('Figure D1  Local estimates versus paper edgeR estimates','The supplied Data S1 CSV contains 14,799 Ensembl rows. Conservative mapping excludes 224 missing/nonnumeric Entrez IDs and 38 rows with ambiguous numeric-ID mappings, yielding 14,537 unique numeric Entrez IDs. Of these, 14,200 have finite estimates in both local methods. All correlations use this common universe, not a significance-selected subset. Axes are cropped to +/-6. Data S1 compares KRAS to nonspecific siRNA, matching the local contrast direction.',1)
para('Table D1  DE-list agreement on the 14,200-gene common universe',17)
rows=[]
for r in ps.itertuples():rows.append([r.method,'FDR < .05'+(' + |LFC| > .5' if r.absLFC_gt else ''),num(r.local_sig),num(r.paper_sig),num(r.overlap),f'{r.jaccard:.3f}'])
table(['Local method','Selection rule','Local DE','Paper DE','Overlap','Jaccard'],rows,[1.05,2.05,.9,.9,.9,.85])
para('For the |log2FC| > 0.5 comparison, 1,497/1,497 DESeq2 shared genes and 1,509/1,510 edgeR shared genes have the same direction as the paper. Without this effect-size gate, the corresponding agreement is 4,499/4,500 and 4,355/4,357. Paper-wide FDR < 0.05 plus |log2FC| > 0.5 selects 1,728 original rows; after conservative mapping and the common-universe restriction, 1,690 remain. These denominators answer different questions.',18)
para('The paper used STAR, Gencode v30, Salmon and tximport, whereas the local matrix comes from HISAT2 and RefSeq featureCounts. It also restricted gene biotypes/chromosomes and used at least 20 reads in two samples; the classroom workflow uses 10 counts in two samples. The paper used edgeR v3, while this analysis uses edgeR v4. These differences make this a benchmark, not an exact pipeline reproduction. A higher correlation for DESeq2 does not establish that it is the better method.',18,1)
para('Scientific review: the study connects acute KRAS suppression with ERK-linked transcription and cell-cycle programming. The local downward DUSP6/SPRY4 and MYC/CCND1 associations are consistent with that context. A pooled expression change alone cannot establish a direct KRAS target, a protein effect, or a dependency. Follow-up should examine line-level responses and experimental replication before making mechanistic claims.',18,1)

heading('Appendix E Candidate genes for discussion',True)
picture('E1_candidate_paired_expression')
cap('Figure E1  Candidate expression in matched cell lines','DESeq2-normalized counts are shown as log2(count + 1). Each line connects one cell line; blue points are Control and red points are KRAS siRNA. These paired observations show heterogeneity without fitting separate line-specific treatment effects. MYC decreases in seven of eight lines despite a negative common model effect; EMP2 increases in all eight. P5 uses the main summed-library assumption.')
para('Table E1  Main estimates and robustness',17)
rows=[]
for sy in ['KRAS','DUSP6','SPRY4','MYC','CCND1','EMP2']:
    r=sen[sen.SYMBOL==sy].iloc[0];p=pairs[pairs.SYMBOL==sy].iloc[0];rows.append([sy,f'{r.merge_p5_DESeq2_log2FC:.2f}',f'{r.merge_p5_edgeR_log2FC:.2f}',sci(r.merge_p5_DESeq2_padj),sci(r.merge_p5_edgeR_FDR),f'{p.paired_lines_down}/8 down' if sy!='EMP2' else '8/8 up'])
table(['Gene','DESeq2 LFC','edgeR LFC','DESeq2 FDR','edgeR FDR','Paired direction'],rows,[.85,1.1,1.1,1.2,1.2,1.2])
para('All six selected genes have FDR < 0.05 and the same direction in both methods under all three P5 choices. They were selected for the KRAS/ERK and cell-cycle discussion, together with one strong upward example; this is not an unbiased enrichment analysis. KRAS provides a knockdown check; DUSP6 and SPRY4 are established KRAS-ERK readouts in the source study. MYC and CCND1 provide cell-cycle context. EMP2 is an upward expression candidate; this analysis does not establish its mechanism.',18,1)
para('Candidate status is provisional. Full tables retain every input gene, including filtered genes and unavailable adjusted p values. Small FDR values do not imply large effects, and post hoc effect-size filtering is not a test of a nonzero effect-size threshold. No enrichment or causal interpretation was added to this week’s results.',18)
para('Software: R 4.5.2; DESeq2 1.50.2; edgeR 4.8.2; apeglm 1.32.0. Package versions and the dependency lockfile accompany the reproducible source package.',18)

heading('Appendix F Transformation and dispersion diagnostics',True)
picture('F1_mean_SD',6.4)
cap('Figure F1  Mean and standard deviation after transformation','Across-sample SD is plotted against mean transformed expression for log2 normalized counts, VST and TMM logCPM. The plots describe the relationship between abundance and variability; biological cell-line differences remain in the SD. VST and logCPM are used for descriptive distances and PCA, while count models are used for differential-expression testing.')
picture('F2_dispersion_summary',6.4)
cap('Figure F2  Dispersion estimates','DESeq2 final negative-binomial dispersions and the fitted trend, edgeR biological coefficient of variation (square root of NB dispersion), and edgeR moderated QL posterior variance with its prior trend. These estimates describe excess count variation and its moderation; they do not verify replicate independence. The separate three-page R diagnostic PDF contains the native plotting functions for inspection.',cite='2,3')
doc.paragraphs[-1].paragraph_format.space_after=Pt(6)
heading('References')
references=[
'Klomp JA, Klomp JE, Stalnecker CA, Bryant KL, Edwards AC, Drizyte-Miller K, et al. Defining the KRAS- and ERK-dependent transcriptome in KRAS-mutant cancers. Science. 2024;384(6700):eadk0775. doi:10.1126/science.adk0775. Data S1.',
'Love MI, Huber W, Anders S. Moderated estimation of fold change and dispersion for RNA-seq data with DESeq2. Genome Biol. 2014;15(12):550. doi:10.1186/s13059-014-0550-8.',
'Chen Y, Chen L, Lun ATL, Baldoni PL, Smyth GK. edgeR v4: powerful differential analysis of sequencing data with expanded functionality and improved support for small counts and larger datasets. Nucleic Acids Res. 2025;53(2):gkaf018. doi:10.1093/nar/gkaf018.',
'Zhu A, Ibrahim JG, Love MI. Heavy-tailed prior distributions for sequence count data: removing the noise and preserving large differences. Bioinformatics. 2019;35(12):2084-92. doi:10.1093/bioinformatics/bty895.',
'Adrian. DESeq2 Tutorial KRAS; edgeR Tutorial KRAS; weekly tasks announcement. Biomedical DryLab [private course materials]. 2026 Oct 3. Accessed 2026 Oct 4.',
'European Nucleotide Archive. PRJNA980201 run metadata [Internet]. Accessed 2026 Oct 4. Available from: https://www.ebi.ac.uk/ena/browser/view/PRJNA980201.'
]
for ref in references:para(ref,34)
para('Review: ____________________    Date: ____________________',37)

# Preserve all reference package parts except the explicitly editable components.
settings=doc.settings.element
for e in settings.findall(qn('w:updateFields')):settings.remove(e)
update=OxmlElement('w:updateFields');update.set(qn('w:val'),'true');settings.append(update)
temp=target.with_suffix('.build.docx');doc.save(temp)
editable={'word/document.xml','word/_rels/document.xml.rels','[Content_Types].xml','word/settings.xml'}
with zipfile.ZipFile(template) as old,zipfile.ZipFile(temp) as new,zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as final:
    oldnames=set(old.namelist());newnames=set(new.namelist())
    for name in old.namelist():final.writestr(name,new.read(name) if name in editable else old.read(name))
    for name in new.namelist():
        if name not in oldnames:final.writestr(name,new.read(name))
with zipfile.ZipFile(template) as old,zipfile.ZipFile(target) as final:
    same=[n for n in old.namelist() if n not in editable]
    assert all(old.read(n)==final.read(n) for n in same)
    from lxml import etree
    a=etree.fromstring(old.read('word/document.xml'));b=etree.fromstring(final.read('word/document.xml'))
    assert etree.tostring(a.find('.//'+qn('w:sectPr')))==etree.tostring(b.find('.//'+qn('w:sectPr')))
    text=final.read('word/document.xml').decode();assert 'TOC' not in text and 'bookmarkStart' not in text
temp.unlink()
qa=dict(template_sha256=hashlib.sha256(template.read_bytes()).hexdigest(),preserved_opaque_parts=len(same),all_preserved_byte_for_byte=True,section_geometry_exact=True,body_font='Times New Roman',true_superscript_citations=True,figures=len(doc.inline_shapes),tables=len(doc.tables),body_sections=['1 Overview','2 Work completed','3 Next steps','4 Summary'],source_results='2026-10-04-week4')
(target.parent/(target.stem+'_structure_validation.json')).write_text(json.dumps(qa,indent=2));print(target)
