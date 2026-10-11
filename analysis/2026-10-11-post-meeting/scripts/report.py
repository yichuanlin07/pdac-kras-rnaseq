"""Build the English discussion report from verified analysis outputs."""
import sys,json,re
from pathlib import Path
import pandas as pd
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Image,PageBreak
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.utils import ImageReader
from xml.sax.saxutils import escape

base=Path(sys.argv[1]);out=Path(sys.argv[2]);out.parent.mkdir(parents=True,exist_ok=True)
r=base/'results';s=base/'sources'
validation=json.loads((s/'repeat_run_validation.json').read_text()); assert validation['all_compared_files_byte_identical']
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodySmall',fontName='Helvetica',fontSize=9.5,leading=13.2,spaceAfter=7,textColor=colors.HexColor('#243B49')))
styles.add(ParagraphStyle(name='CaptionSmall',fontName='Helvetica',fontSize=8.2,leading=11,spaceAfter=8,textColor=colors.HexColor('#52606D')))
styles.add(ParagraphStyle(name='CellSmall',fontName='Helvetica',fontSize=8.2,leading=10.5))
styles['Title'].fontName='Helvetica-Bold';styles['Title'].fontSize=21;styles['Title'].leading=25;styles['Title'].alignment=TA_LEFT
styles['Heading1'].fontSize=16;styles['Heading1'].leading=20;styles['Heading1'].textColor=colors.HexColor('#155E82');styles['Heading1'].spaceAfter=11
styles['Heading2'].fontSize=11;styles['Heading2'].leading=15;styles['Heading2'].spaceAfter=6
story=[]
def p(text,sty='BodySmall'):story.append(Paragraph(text,styles[sty]))
def h(text):p(text,'Heading1')
def sub(text):p(text,'Heading2')
def table(rows,widths):
    cells=[[Paragraph(escape(str(c)),styles['CellSmall']) for c in row] for row in rows]
    t=Table(cells,colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E8F1F5')),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),('LINEBELOW',(0,0),(-1,0),.6,colors.HexColor('#9FB3C0')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F7F9FA')])]))
    story.append(t);story.append(Spacer(1,9))
def fig(name,width=520):
    path=base/'figures'/f'{name}.png';w,hh=ImageReader(str(path)).getSize();story.append(Image(str(path),width=width,height=width*hh/w));story.append(Spacer(1,6))
def page():story.append(PageBreak())

p('KRAS RNA-seq: screening and<br/>cell-line omission analysis','Title')
p('October 11, 2026 | Follow-up to the October 10 group meeting','CaptionSmall')
h('1. Main findings')
p('Adding the post-test effect cutoff reduces the full-fit joint list from <b>5,442 to 2,020 genes</b>. Across eight paired cell-line omissions, <b>1,515</b> of these genes pass the joint screen in at least seven of the same eight rounds; <b>1,291</b> pass in every round. These are descriptive stability lists for discussion and subsequent external evaluation.')
fig('F1_effect_definition_screening')
p('Figure 1. All counts refer to the full retained universe of 17,819 genes. The screen is adjusted P &lt; 0.05 and |log2FC| &gt; 0.5. DESeq2 model LFC is before apeglm shrinkage. edgeR uses its reported LFC with the default prior count 0.125. The 14,200-gene paper-comparison subset is not used here.','CaptionSmall')
table([['Definition','DESeq2','edgeR','Intersection'],['FDR < 0.05 only','5,943','6,431','5,442'],['FDR + primary effect cutoff','2,088','2,919','2,020'],['FDR + DESeq2 apeglm cutoff','1,702','2,919','1,690']],[275,80,80,85])
p('<b>Direction:</b> 2,017/2,020 genes have finite effects with the full-fit direction in all eight rounds in both methods. Three genes are filtered out in one round. No direction reversal occurs among available estimates in this reference list.')
p('<b>Examples:</b> KRAS, DUSP6, SPRY4, CCND1 and EMP2 pass in all rounds in both methods. MYC remains significant and negative in every round but crosses the 0.5 effect boundary twice.')

page();h('2. Sample handling and model audit')
p('The input has 28,395 genes and 17 runs. MiaPaca-2 KRAS libraries are summed gene by gene as raw integers before filtering and normalization, yielding 16 analysis observations. The pooled Treatment observation has 68,124,190 assigned counts; the Control observation is retained separately.')
table([['Local label','Run accession','BioSample','Public alias'],['Control P5','SRR24828470','SAMN35622211','MP2_SC'],['KRAS P5','SRR24828471','SAMN35622210','MP2_K2v2'],['KRAS P5_v2','SRR24828472','SAMN35622209','MP2_K2']],[95,135,145,145])
p('The local v2 label is reversed relative to the public alias. The archived ENA snapshot (2026-10-04) confirms distinct BioSample records and FASTQ MD5 values. It does not establish technical or biological repeat identity or shared biological material. Pooling remains an explicit exploratory assumption; the two libraries are not counted as independent replicates.')
table([['Audit item','Full fit','Each omission fit'],['Observations / cell lines','16 / 8','14 / 7'],['Model','~ condition + cell_line','~ condition + cell_line'],['Design rank / residual df','9 / 7','8 / 6'],['Low-count rule','>=10 counts in >=2 observations','Same rule, recalculated'],['Condition direction','KRAS siRNA / Control','KRAS siRNA / Control']],[190,165,165])
p('Each omission removes both conditions of one cell line. Omitting MiaPaca-2 removes its Control and its pooled Treatment, including both source KRAS libraries. Normalization and dispersions are refitted for each reduced dataset. The additive model estimates a common cell-line-adjusted treatment effect without an interaction; within-cell-line replication is unavailable.')
sub('Primary effect and test are separate')
p('DESeq2 uses Wald tests and its model log2FoldChange before apeglm shrinkage for the main screen. apeglm posterior effects and posterior SD are saved separately. edgeR uses TMM and robust quasi-likelihood fitting (v4, legacy = FALSE); its reported logFC is moderated by prior.count = 0.125. Both tests use a zero-effect null. The 0.5 cutoff is applied after testing.')
sub('Archived single-library checks')
table([['P5 choice','DESeq2 screen','edgeR screen','Intersection'],['Sum two libraries','2,088','2,919','2,020'],['Retain SRR24828472','2,094','2,827','2,008'],['Retain SRR24828471','2,086','2,855','1,991']],[275,80,80,85])
p('These screens were recalculated from the archived Week 4 fits. Single-library models were not refitted in this work.','CaptionSmall')

page();h('3. Effect stability across eight omissions')
fig('F2_effect_stability')
p('Figure 2. Effect comparisons use the full-fit joint list, with finite values in each round (2,020, except 2,018 after omitting PANC-1 and 2,019 after omitting Pa02C). Point estimates are compared with the full fit; these values are not confidence intervals.','CaptionSmall')
p('DESeq2 Pearson correlations are 0.9944-0.9975 and edgeR correlations are 0.9918-0.9978. The 95th percentiles of absolute log2FC change are 0.1306-0.1915 and 0.1082-0.2226, respectively. Omitting MiaPaca-2 gives the lowest correlations and largest 95th-percentile changes in both methods, while overall agreement remains high.')
fig('F4_joint_screen_stability')
p('Figure 3. Joint passes require both methods to pass in the same round. The main descriptive list also requires full-fit selection, eight finite effects and direction agreement in each method. Separate >=7/8 passes per method would give 1,517 genes because the failed rounds can differ; the simultaneous definition gives 1,515.','CaptionSmall')
p('GSTM2 and CDK15 lack estimates after omitting PANC-1; DDX3Y lacks estimates after omitting Pa02C. All three fail that round\'s low-count filter. Missing estimates are recorded explicitly. A total of 52 reference genes have a maximum effect change >=0.5 log2 units in at least one method and are exported for inspection; this flag does not establish single-line causation.')

page();h('4. Candidate results for discussion')
fig('F3_candidate_effects')
p('Figure 4. Diamonds show full-fit estimates; dots and horizontal ranges show the eight omission estimates. Dashed lines mark +/-0.5. Ranges are minimum-to-maximum point estimates, not confidence intervals.','CaptionSmall')
c=pd.read_csv(r/'candidate_stability.tsv',sep='\t').set_index('SYMBOL')
rows=[['Gene','DESeq2 full LFC','edgeR full LFC','Screen rounds D / E','Interpretation']]
notes={'KRAS':'Persistent decrease','DUSP6':'Persistent decrease','SPRY4':'Persistent decrease','CCND1':'Persistent decrease','EMP2':'Persistent increase','MYC':'Effect boundary sensitivity','DPM3':'Small effect despite FDR','EGR1':'Statistical evidence differs','WNT5A':'Method-sensitive evidence','SFRP1':'Direction changes','TGFBR3':'Below the effect cutoff'}
for gene in ['KRAS','DUSP6','SPRY4','CCND1','EMP2','MYC','DPM3','EGR1','WNT5A','SFRP1','TGFBR3']:
 row=c.loc[gene];rows.append([gene,f'{row.DESeq2_full_log2FC:.3f}',f'{row.edgeR_full_log2FC:.3f}',f'{int(row.DESeq2_screen_pass_rounds)}/8 ; {int(row.edgeR_screen_pass_rounds)}/8',notes[gene]])
table(rows,[60,90,90,105,175])
p('MYC remains FDR-significant and negative in all rounds; omitting HPAC or Pa16C moves its absolute effect below 0.5. DPM3 remains significant but never exceeds 0.5. EGR1 retains negative effects greater than 0.5 in magnitude but passes FDR in 4/8 DESeq2 and 1/8 edgeR fits. These are different forms of sensitivity, not interchangeable evidence of a dominant cell line.','CaptionSmall')

methods=(base/'Methods_en.md').read_text().splitlines()
chunks={};key=None
for line in methods:
 if line.startswith('## '):key=line[3:];chunks[key]=[]
 elif key and line.strip():chunks[key].append(line.strip())
def method_section(key):
 sub(key)
 for line in chunks[key]:
  text=escape(line);text=re.sub(r'`([^`]+)`',r'<font name="Courier">\1</font>',text);p(text)
page();h('5. Manuscript Methods draft')
for key in ['Count data and sample structure','MiaPaca-2 library handling','Differential expression']:method_section(key)
page();h('6. Methods: omission analysis and verification')
method_section('Leave-one-cell-line-out analysis')
sub('Completed verification')
p('Raw counts were checked against all 17 source tables, assigned totals, metadata order and the saved ENA alias mapping. The pooled counts match exact gene-level sums. All nine designs are full rank; reverse contrasts negate effects and preserve raw P values; no DESeq2 coefficient fit failed to converge. The full fit matches the archived Week 4 effect estimates and P values to numerical tolerance. Two fresh nine-fit runs produced 68 byte-identical TSV and method-JSON files.')
sub('Limits and next discussion')
p('The descriptive 7/8 and 8/8 lists have not been evaluated for patient-outcome prediction. No new guarantee of false-discovery control follows from counting correlated omission passes. P5 repeat identity remains unresolved. Effect changes do not establish direct regulation, protein changes or a validated clinical signature. The existing Week 4 paired-expression appendix is retained; it was not regenerated.')
p('The next meeting can discuss the omission definition, candidate effects and the joint list. The October 10 meeting suggested Lin draft Methods and other group members draft Results, with roles open to group adjustment. The manuscript draft was requested within two weeks of that meeting; no exact delivery time or fixed word limit was assigned. Pathway enrichment remains deferred.')
sub('Deliverables and references')
p('The dated analysis directory contains code, full tables for nine fits, gene and candidate stability tables, screening audits, four figures, Methods_en.md and Results_zh.md. Input files and history remain in the independent local repository branch. No remote push or publication was performed.')
p('Source records: corrected project counts (analysis/2026-10-01/counts); archived Week 4 results and ENA snapshot; local October 10 meeting summary. Statistical software: DESeq2 (doi:10.1186/s13059-014-0550-8), edgeR v4 (doi:10.1093/nar/gkaf018), apeglm (doi:10.1093/bioinformatics/bty895). These references identify the software; the Methods describe the operations actually executed here.','CaptionSmall')
def footer(canvas,doc):
 canvas.saveState();canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#52606D'));canvas.drawString(46,26,'KRAS group discussion | October 11, 2026');canvas.drawRightString(566,26,str(doc.page));canvas.restoreState()
doc=SimpleDocTemplate(str(out),pagesize=(612,792),leftMargin=46,rightMargin=46,topMargin=40,bottomMargin=43,title='KRAS RNA-seq screening and cell-line omission analysis',author='')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(out)
