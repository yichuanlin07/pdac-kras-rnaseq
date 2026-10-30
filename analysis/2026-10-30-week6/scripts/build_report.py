from pathlib import Path
from copy import deepcopy
from datetime import datetime, timezone
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib
import json
import re
import sys
import pandas as pd
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph
from lxml import etree
ROOT = Path(__file__).resolve().parents[1]
OUT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT
REF = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else OUT / 'sources/report_template.docx'
if not REF.exists():
    REF = OUT / 'sources/report_template.docx'
QA = Path(sys.argv[3]).resolve() if len(sys.argv) > 3 else OUT / 'qa'
QA.mkdir(exist_ok=True, parents=True)
FINAL = OUT / 'PDAC_KRAS_Week6_2026-10-30.docx'
contract_path = QA / 'artifact.md'
if not contract_path.exists():
    contract_path = OUT / 'sources/template_contract.md'
contract = contract_path.read_text()
assert hashlib.sha256(REF.read_bytes()).hexdigest() in contract
d = Document(REF)
patterns = [deepcopy(p._p) for p in d.paragraphs]
table_pr = deepcopy(d.tables[0]._tbl.tblPr)
section = deepcopy(d._element.body.sectPr)
for child in list(d._element.body):
    if child.tag != qn('w:sectPr'):
        d._element.body.remove(child)
for key in list(d.part.rels):
    if d.part.rels[key].reltype.endswith('/image'):
        del d.part.rels[key]
M = json.loads((OUT / 'results/metrics.json').read_text())
compare = pd.read_csv(OUT / 'results/report_method_comparison.tsv', sep='\t').set_index('gene_set')
fit = pd.read_csv(OUT / 'results/fit_summary.tsv', sep='\t')

def set_font(run, size=10.5, bold=False):
    run.font.name = 'Times New Roman'
    run.font.size = Pt(size)
    run.bold = bold
    run.font.color.rgb = RGBColor(0, 0, 0)
    fonts = run._element.get_or_add_rPr().rFonts
    for key in ['ascii', 'hAnsi', 'eastAsia', 'cs']:
        fonts.set(qn('w:' + key), 'Times New Roman')
    return run

def para(text='', kind='body', page=False):
    idx = {'title': 0, 'week': 1, 'author': 2, 'heading': 3, 'body': 4, 'image': 16, 'label': 17, 'explain': 18, 'ref': 68, 'review': 75}[kind]
    e = deepcopy(patterns[idx])
    for ch in list(e):
        if ch.tag != qn('w:pPr'):
            e.remove(ch)
    d._element.body.insert(len(d._element.body) - 1, e)
    p = Paragraph(e, d._body)
    fmt = p.paragraph_format
    fmt.page_break_before = page
    fmt.line_spacing = 1.05
    fmt.widow_control = True
    contextual = e.get_or_add_pPr().find(qn('w:contextualSpacing'))
    if contextual is None:
        contextual = OxmlElement('w:contextualSpacing')
        e.get_or_add_pPr().append(contextual)
    contextual.set(qn('w:val'), '0')
    size = {'title': 20, 'week': 9.5, 'author': 9, 'heading': 14, 'body': 10.5, 'image': 10.5, 'label': 10, 'explain': 9, 'ref': 9, 'review': 10.5}[kind]
    if kind in ['heading', 'label']:
        fmt.keep_with_next = True
    elif kind == 'image':
        fmt.keep_with_next = True
    else:
        fmt.keep_with_next = False
    if kind == 'body':
        fmt.space_after = Pt(16)
    if kind == 'explain':
        fmt.space_after = Pt(18)
        if e.getprevious() is not None and e.getprevious().tag == qn('w:tbl'):
            fmt.space_before = Pt(8)
    if kind == 'ref':
        p.style = d.styles['Normal']
        fmt.left_indent = Inches(0.23)
        fmt.first_line_indent = Inches(-0.23)
        fmt.space_after = Pt(8)
        fmt.alignment = WD_ALIGN_PARAGRAPH.LEFT
        num = e.get_or_add_pPr().find(qn('w:numPr'))
        if num is not None:
            e.get_or_add_pPr().remove(num)
    for part in re.split('(<cite:[0-9,]+>)', text):
        if not part:
            continue
        if part.startswith('<cite:'):
            run = set_font(p.add_run(part[6:-1]), 8)
            run.font.superscript = True
        else:
            set_font(p.add_run(part), size, kind in ['title', 'week', 'heading', 'label'])
    return p

def table(title, headers, rows, widths, numeric_cols=()):
    para(title, 'label')
    t = d.add_table(rows=1, cols=len(headers))
    old = t._tbl.tblPr
    t._tbl.replace(old, deepcopy(table_pr))
    t.autofit = False
    for col, w in zip(t.columns, widths):
        col.width = Inches(w)
    for i, h in enumerate(headers):
        t.rows[0].cells[i].text = h
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = str(v)
    for ri, row in enumerate(t.rows):
        trPr = row._tr.get_or_add_trPr()
        cannot = OxmlElement('w:cantSplit')
        trPr.append(cannot)
        if ri == 0:
            trPr.append(OxmlElement('w:tblHeader'))
        for ci, c in enumerate(row.cells):
            c.width = Inches(widths[ci])
            c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            pr = c._tc.get_or_add_tcPr()
            for tag in ['shd', 'tcMar', 'tcBorders']:
                old = pr.find(qn('w:' + tag))
                if old is not None:
                    pr.remove(old)
            sh = OxmlElement('w:shd')
            sh.set(qn('w:fill'), 'FFFFFF')
            pr.append(sh)
            mar = OxmlElement('w:tcMar')
            for side in ['top', 'left', 'bottom', 'right']:
                x = OxmlElement('w:' + side)
                x.set(qn('w:w'), '120')
                x.set(qn('w:type'), 'dxa')
                mar.append(x)
            pr.append(mar)
            borders = OxmlElement('w:tcBorders')
            for side in ['top', 'left', 'bottom', 'right']:
                x = OxmlElement('w:' + side)
                x.set(qn('w:val'), 'single')
                x.set(qn('w:sz'), '4')
                x.set(qn('w:color'), '000000')
                borders.append(x)
            pr.append(borders)
            for p in c.paragraphs:
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.05
                p.paragraph_format.keep_with_next = ri < len(t.rows) - 1
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT if ci in numeric_cols and ri else WD_ALIGN_PARAGRAPH.LEFT
                for r in p.runs:
                    set_font(r, 9, ri == 0)
    return t

def figure(name, title, explanation):
    p = para('', 'image')
    shape = p.add_run().add_picture(str(OUT / 'figures' / name), width=Inches(6.82))
    shape._inline.docPr.set('descr', title + '. ' + explanation)
    para(title, 'label')
    para(explanation, 'explain')

def sci(x):
    return f'{x:.2g}' if x < 0.001 else f'{x:.3f}'
para('KRAS suppression in pancreatic cancer cells', 'title')
para('WEEK6 PROGRESS REPORT', 'week')
para('Yichuan Lin', 'author')
para('1 Overview', 'heading')
para('Cell-cycle gene sets, led by E2F targets and the G2M checkpoint, were enriched among genes with lower expression after KRAS small interfering RNA (siRNA) treatment in eight pancreatic cancer cell lines from Klomp and colleagues. The primary CAMERA gene-set test returned a minimum adjusted P value (q) of 0.354.<cite:1,2>')
para('2 Work completed', 'heading')
para('The corrected count matrix contains 28,395 gene rows and matches all 17 source count tables. KRAS M1 has 37,657,740 assigned counts. The two MiaPaca-2 KRAS libraries were summed before filtering, giving 16 observations across eight paired cell lines.<cite:2>')
para('Hallmark and Reactome gene sets from the Molecular Signatures Database (MSigDB) 2026.2.Hs were matched to the count matrix by Entrez gene identifier.<cite:3> After trimmed mean of M-values (TMM) normalization, limma-trend models were fitted to log counts per million calculated with a prior count of two.<cite:4,5> The model was ~cell_line + condition, with Control as the reference. Filtering retained 17,819 genes with at least 10 counts in two observations. CAMERA compared each gene set with the remaining measured genes using its estimated residual gene correlation.<cite:6>')
para('The primary analysis tested 50 Hallmark and 1,122 Reactome sets containing 15-500 measured genes. Benjamini-Hochberg correction covered all 1,172 tests together. The minimum global q was 0.354, with zero sets at q < 0.05. Fixing the correlation at 0.01 yielded 272 sets at q < 0.05. Appendix C gives the correlation and degrees-of-freedom settings.<cite:2>')
para('The earlier DESeq2/edgeR joint list contains 2,020 genes: 745 decreases and 1,275 increases, with matching directions between methods. Over-representation analysis (ORA) used a background of 15,055 genes with adjusted P values in both methods. Across 2,266 tests, 46 set-direction combinations met q < 0.05: nine Hallmark and 37 Reactome. E2F targets and the G2M checkpoint had the strongest Hallmark enrichment among decreases.<cite:2>')
para('Sensitivity analyses comprised eight paired cell-line omissions and two single-library P5 models. The selected E2F, G2M and MYC sets retained their downward competitive direction across all 11 models. ORA of the 1,515-gene stability list also retained E2F and G2M enrichment.<cite:2>')
para('3 Next steps', 'heading')
para('Review the shared E2F and G2M contributor genes with the supervisor, confirm the preparation and replicate relationship of the two P5 libraries, and test these expression patterns in independent data.')
para('4 Summary', 'heading')
para('E2F targets and the G2M checkpoint are the priorities for follow-up. The next stage is to examine their shared contributor genes and test the expression pattern in independent data.')
para('Appendix A Samples and analysis design', 'heading', page=True)
meta = pd.read_csv(OUT / 'sources/samples.tsv', sep='\t')
rows = []
for line in sorted(meta.cell_line.unique()):
    m = meta[meta.cell_line == line]
    rows.append([line, '; '.join(m.loc[m.condition == 'Control', 'run_accession']), '; '.join(m.loc[m.condition == 'KRAS', 'run_accession'])])
table('Table A1  Run accessions for the paired cell lines', ['Cell line', 'Control siRNA', 'KRAS siRNA'], rows, [1.15, 2.35, 3.32])
para('The MiaPaca-2 treatment observation combines the raw integer counts from SRR24828471 and SRR24828472, giving 68,124,190 assigned counts. Local P5 is SRR24828471 (public alias MP2_K2v2); local P5_v2 is SRR24828472 (MP2_K2).<cite:2>', 'explain')
table('Table A2  Model sizes and retained genes', ['Analysis', 'Observations', 'Cell lines', 'Retained genes', 'Residual df'], [['Full pooled model', '16', '8', '17,819', '7'], ['Eight omission models', '14 each', '7 each', f'{fit.iloc[1:9].genes.min():,}-{fit.iloc[1:9].genes.max():,}', '6 each'], ['P5 SRR24828471 only', '16', '8', '17,705', '7'], ['P5 SRR24828472 only', '16', '8', '17,734', '7']], [2.12, 1.15, 0.85, 1.55, 1.15], (1, 2, 3, 4))
para('Each omission removes both conditions of one cell line and repeats filtering, TMM normalization and limma-trend fitting. Residual df denotes residual degrees of freedom. The maximum effective library-size ratio across models is 2.21. The models estimate a common treatment effect after adjusting for cell line.<cite:2>', 'explain')
para('MSigDB 2026.2.Hs supplies 50 Hallmark and 1,867 Reactome sets; the Reactome snapshot uses release 97. Set size is measured after intersection with each analysis universe. Entrez identifiers determine gene matching and test eligibility, and gene symbols provide display labels.<cite:3>', 'explain')
para('Appendix B Enrichment of selected genes', 'heading', page=True)
figure('B1_hallmark_ora.png', 'Figure B1  Hallmark sets enriched in the joint gene list', 'The plot shows all nine Hallmark set-direction tests with global q < 0.05. Joint selection requires adjusted P < 0.05 and absolute log2 fold change > 0.5 in both gene-level methods; DESeq2 uses its unshrunk model effect. Dot size and adjacent numbers show the selected genes overlapping each set. Blue indicates decreases and red indicates increases after KRAS siRNA. The dashed line marks the expected overlap. ORA uses a hypergeometric test with a 15,055-gene background and jointly adjusts both directions and both collections.<cite:2>')
figure('B2_reactome_ora.png', 'Figure B2  Selected Reactome overlaps', 'The plot shows the six lowest-q downward and three lowest-q upward Reactome tests from the 37 significant set-direction combinations. Several Reactome terms share member genes.<cite:2>')
para('Appendix C Gene correlation and test assumptions', 'heading', page=True)
figure('C1_correlation_sensitivity.png', 'Figure C1  Comparison of enrichment tests', 'Eight selected Hallmark sets are compared using ORA in the primary CAMERA direction, CAMERA with estimated correlation, and CAMERA with correlation fixed at 0.01. Points to the right of the dashed line meet q < 0.05 in their respective test families. ORA uses a 15,055-gene background; CAMERA uses the 17,819 retained genes.<cite:2>')
rows = []
for term, short in [('HALLMARK_E2F_TARGETS', 'E2F targets'), ('HALLMARK_G2M_CHECKPOINT', 'G2M checkpoint'), ('HALLMARK_KRAS_SIGNALING_UP', 'KRAS signaling UP'), ('HALLMARK_KRAS_SIGNALING_DN', 'KRAS signaling DN'), ('HALLMARK_MYC_TARGETS_V1', 'MYC targets V1'), ('HALLMARK_INTERFERON_ALPHA_RESPONSE', 'Interferon alpha')]:
    r = compare.loc[term]
    rows.append([short, f'{r.CAMERA_rho:.3f}', sci(r.ORA_q), sci(r.CAMERA_q), sci(r.fixed_001_q)])
table('Table C1  Correlation estimates and adjusted P values', ['Gene set', 'Estimated correlation', 'ORA q', 'CAMERA q', 'Fixed 0.01 q'], rows, [1.7, 1.22, 1.3, 1.3, 1.3], (1, 2, 3, 4))
para('Primary CAMERA estimates residual correlation within each set, sets a minimum variance inflation factor of one, and uses seven residual degrees of freedom in the full model. The fixed-correlation sensitivity uses correlation 0.01 and 17,817 test degrees of freedom in the installed implementation.<cite:2,6>', 'explain')
para('Correcting the 50 Hallmark tests separately gave a minimum q of 0.368.<cite:2>', 'explain')
para('Appendix D Sensitivity and biological context', 'heading', page=True)
figure('D1_direction_sensitivity.png', 'Figure D1  Competitive direction across eleven models', 'D and U indicate downward and upward CAMERA directions relative to the other measured genes. Column 1 is the full pooled model; columns 2-9 each omit the named cell line; the last two columns retain SRR24828471 or SRR24828472 alone for P5 KRAS. All nine displayed sets are available in every model. Across the 11 primary fits, zero sets met global q < 0.05.<cite:2>')
rows = []
for term, short in [('HALLMARK_E2F_TARGETS', 'E2F targets down'), ('HALLMARK_G2M_CHECKPOINT', 'G2M checkpoint down'), ('HALLMARK_KRAS_SIGNALING_UP', 'KRAS signaling UP down'), ('HALLMARK_KRAS_SIGNALING_DN', 'KRAS signaling DN up')]:
    r = compare.loc[term]
    rows.append([short, int(r.ORA_hits), sci(r.ORA_q), int(r.stable_hits), sci(r.stable_ORA_q)])
table('Table D1  ORA using the descriptive stability list', ['Gene set and direction', 'Full-list overlap', 'Full-list q', 'Stable-list overlap', 'Stable-list q'], rows, [2.02, 1.2, 1.2, 1.2, 1.2], (1, 2, 3, 4))
para('The stability list contains 538 decreases and 977 increases. Inclusion requires joint selection in the full fit, finite effects with the same direction in all eight omissions, and selection by both differential-expression methods in at least seven omission rounds. ORA uses the same 15,055-gene background. Repeating ORA with all 17,819 retained genes as the background also retains E2F and G2M enrichment.<cite:2>', 'explain')
para("The cell-cycle enrichment is consistent with the published study's findings on KRAS-ERK regulation of proliferation.<cite:1> The Hallmark names KRAS signaling UP and KRAS signaling DN identify the reference signatures; their observed directions here are down and up, respectively.<cite:2>", 'explain')
para('Pathway analyses used R 4.5.2, edgeR 4.8.2 and limma 3.66.0. ORA used the existing DESeq2 and edgeR result tables.<cite:2>', 'explain')
para('References', 'heading', page=True)
refs = ['Klomp JA, Klomp JE, Stalnecker CA, Bryant KL, Edwards AC, Drizyte-Miller K, et al. Defining the KRAS- and ERK-dependent transcriptome in KRAS-mutant cancers. Science. 2024 Jun 7;384(6700):eadk0775. doi:10.1126/science.adk0775.', 'Lin Y. PDAC KRAS RNA-seq Week 6 pathway analysis [dataset]. 2026 Oct 30. Input source revision 7e3fe15664597474008b63753dd9e4b20efec04a. Analysis archive: Week6_2026-10-30 (sources/input_validation.json; results/).', 'Molecular Signatures Database. Human Hallmark and Reactome gene sets, version 2026.2.Hs [Internet]. 2026 Oct [cited 2026 Oct 30]. Available from: https://data.broadinstitute.org/gsea-msigdb/msigdb/release/2026.2.Hs/ . Release notes: https://docs.gsea-msigdb.org/MSigDB/Release_Notes/MSigDB_2026.2.Hs/ .', 'Robinson MD, Oshlack A. A scaling normalization method for differential expression analysis of RNA-seq data. Genome Biol. 2010 Mar 2;11(3):R25. doi:10.1186/gb-2010-11-3-r25.', 'Ritchie ME, Phipson B, Wu D, Hu Y, Law CW, Shi W, et al. limma powers differential expression analyses for RNA-sequencing and microarray studies. Nucleic Acids Res. 2015 Apr 20;43(7):e47. doi:10.1093/nar/gkv007.', 'Wu D, Smyth GK. Camera: a competitive gene set test accounting for inter-gene correlation. Nucleic Acids Res. 2012 Sep;40(17):e133. doi:10.1093/nar/gks461.']
for i, text in enumerate(refs, 1):
    para(f'{i}. {text}', 'ref')
para('Review: ____________________    Date: ____________________', 'review')
d.core_properties.title = 'KRAS suppression in pancreatic cancer cells Week 6 progress report'
d.core_properties.author = 'Yichuan Lin'
d.core_properties.subject = 'Hallmark and Reactome pathway analysis with sensitivity checks'
d.core_properties.created = datetime(2026, 10, 30, 22, 0, tzinfo=timezone.utc)
d.core_properties.modified = datetime(2026, 10, 30, 22, 0, tzinfo=timezone.utc)
tmp = QA / 'report-working.docx'
d.save(tmp)
editable = {'word/document.xml', 'word/_rels/document.xml.rels', '[Content_Types].xml', 'docProps/core.xml', 'word/settings.xml'}
with ZipFile(REF) as base, ZipFile(tmp) as edited, ZipFile(FINAL, 'w', ZIP_DEFLATED) as final:
    names = set(base.namelist()) | set(edited.namelist())
    for name in sorted(names):
        if name.startswith('word/media/') and name not in edited.namelist():
            continue
        if name in base.namelist() and name not in editable and (not name.startswith('word/media/')):
            data = base.read(name)
        else:
            data = edited.read(name) if name in edited.namelist() else base.read(name)
        if name == 'word/settings.xml':
            tree = etree.fromstring(data)
            field = tree.find(qn('w:updateFields'))
            if field is None:
                field = OxmlElement('w:updateFields')
                tree.append(field)
            field.set(qn('w:val'), 'true')
            data = etree.tostring(tree, xml_declaration=True, encoding='UTF-8', standalone=True)
        final.writestr(name, data)
preserved = []
with ZipFile(REF) as base, ZipFile(FINAL) as final:
    for name in base.namelist():
        if name not in editable and (not name.startswith('word/media/')):
            assert base.read(name) == final.read(name), name
            preserved.append(name)
    tree = etree.fromstring(final.read('word/document.xml'))
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    assert not tree.xpath('//w:bookmarkStart|//w:hyperlink[@w:anchor]', namespaces=ns)
    assert not any(('TOC' in t for t in tree.xpath('//w:instrText/text()', namespaces=ns)))
assert etree.tostring(Document(FINAL)._element.body.sectPr, method='c14n', exclusive=True) == etree.tostring(section, method='c14n', exclusive=True)
(QA / 'package-fidelity.json').write_text(json.dumps({'preserve_only_parts_identical': preserved, 'section_geometry_identical': True, 'reference_sha256': hashlib.sha256(REF.read_bytes()).hexdigest(), 'new_figures': len(d.inline_shapes), 'tables': len(d.tables)}, indent=2) + '\n')
(OUT / 'sources/references.json').write_text(json.dumps({'references': refs, 'citation_sequence': [1, 2, 3, 4, 5, 6], 'accessed': '2026-10-30'}, indent=2) + '\n')
print(FINAL)
