# Week 4: KRAS siRNA differential expression

The real 28,395-gene, 17-run matrix from [October 1](../2026-10-01/README.md) was analysed with DESeq2 and edgeR. Following the meeting tutorial, the exploratory main analysis sums SRR24828471 (public MP2_K2v2) and SRR24828472 (public MP2_K2) into one MiaPaca-2 KRAS observation. Two comparisons retain each library separately. This processing is complete; the remaining uncertainty is whether the original libraries represent technical or biological repeats, which the tutorial says the paper did not specify.

The October 6 report revisions clarify these choices and edit the English text for readability. Version 3 uses the requested title WEEK4 PROGRESS REPORT, keeps only the author's name beneath it, and increases paragraph gaps and table padding. Version 4 adds light horizontal guides to the DE-count and paired-expression plots. Numerical results are unchanged. Earlier reports and the published versions 1 and 2 source packages are retained.

At FDR < 0.05, DESeq2 identified 5,943 genes (2,912 down; 3,031 up) and edgeR identified 6,431 (2,923 down; 3,508 up). The overlap is 5,442, union 6,932 and Jaccard 0.785. Unshrunk log2FC estimates correlate at Pearson 0.884 and Spearman 0.910 across all 17,819 shared finite estimates. Positive log2FC means higher expression after KRAS siRNA.

| P5 handling | Retained genes | DESeq2 DE | edgeR DE | Shared DE |
| --- | ---: | ---: | ---: | ---: |
| Sum SRR24828471 + SRR24828472 (main) | 17,819 | 5,943 | 6,431 | 5,442 |
| Retain SRR24828472 only | 17,734 | 5,724 | 6,131 | 5,269 |
| Retain SRR24828471 only | 17,705 | 6,004 | 6,535 | 5,568 |

There are 5,084 genes with FDR < 0.05 and the same direction in both methods under all three choices. The fits share observations; they are sensitivity checks, not six independent confirmations. Main-versus-single-library DE-list Jaccard values range from 0.920 to 0.945. DPM3 loses edgeR significance when only SRR24828472 is used. EGR1 differs between methods. KRAS, DUSP6, SPRY4, MYC and CCND1 remain downward candidates; EMP2 remains upward. MYC decreases in seven of eight normalized sample pairs. Gene expression does not establish direct regulation or protein effects.

## Files

- [Full DESeq2 table](results/merge_p5/DESeq2_full.tsv) and [full edgeR table](results/merge_p5/edgeR_full.tsv): all 28,395 original genes, with low-count and independent-filter status retained.
- [Scenario summary](results/scenario_summary.tsv), [full sensitivity table](results/sensitivity_full.tsv), [sensitivity metrics](results/sensitivity_metrics.tsv), and [candidate review](results/candidate_review.tsv).
- [Method comparison](results/merge_p5/method_comparison.tsv), [paper benchmark](results/paper_comparison_summary.tsv), [conservative mapping exclusions](results/paper_excluded_mapping_rows.tsv), and [paper input audit](results/paper_input_audit.tsv).
- [Figures](figures): PCA, sample distances, adjusted-p volcanoes, DE counts, method agreement, P5 sensitivity, paper comparison, paired candidate counts, mean/SD and dispersion. Additional raw-run QC and MA/MD plots are provided. Each scenario also has a three-page native R dispersion diagnostic PDF.
- [Current English report](../../reports/PDAC_KRAS_Week4_2026-10-06_v4.docx) and [PDF](../../reports/PDAC_KRAS_Week4_2026-10-06_v4.pdf). [Version 1](../../reports/PDAC_KRAS_Week4_2026-10-04_v1.pdf), [version 2](../../reports/PDAC_KRAS_Week4_2026-10-06_v2.pdf) and [version 3](../../reports/PDAC_KRAS_Week4_2026-10-06_v3.pdf) are retained.
- [Version 4 document validation](sources/report_render_validation_2026-10-06_v4.json) records the chart-guide changes, unchanged scientific text and numerical results, and rendered layout checks. [Version 3 validation](sources/report_render_validation_2026-10-06_v3.json) and [version 2 validation](sources/report_render_validation_2026-10-06_v2.json) retain the preceding checks.
- [Input audit](sources/input_validation.json), [classroom file identities](sources/classroom_provenance.json), [independent numerical validation](results/independent_numerical_validation.json), [repeat-run verification](results/repeat_run_validation.json), and [dependency lockfile](renv.lock).

## Methods and departures from demonstration code

The October 3 DESeq2 and edgeR tutorials use `~condition + cell_line`, Control as reference and `Treatment` for KRAS siRNA. Counts >= 10 in at least two samples are retained separately within each P5 scenario. Each scenario has one observation per condition per cell line: 16 observations, nine full-rank design columns and seven residual degrees of freedom. No treatment-by-cell-line interaction or within-line replication is estimated. The zero-effect null is tested; the primary lists have no log2FC gate.

DESeq2 uses its median-of-ratios size factors, negative-binomial dispersion fitting and Wald testing. Independent filtering explicitly targets `alpha=0.05`, matching the reporting FDR. The tutorial's implicit default `alpha=0.1` produces 5,905 genes at FDR < 0.05 in the main fit; that adjusted-p column is retained. No-independent-filter and common-finite-p BH columns are also supplied. Main results have 10,576 low-count genes and 2,764 additionally independent-filtered genes; there are no missing retained-gene raw p values. `apeglm` shrinkage is used for visualization, while inference and method correlation use the unshrunk estimates. The posterior SD is distinct from the unshrunk Wald SE.

edgeR uses TMM, `estimateDisp(robust=TRUE)`, `glmQLFit(robust=TRUE)` and `glmQLFTest` for `conditionTreatment`. edgeR 4.8.2 uses its current QL implementation (`legacy=FALSE` default), which differs from the paper's v3 software. BH FDR is calculated over retained genes. Both methods' reversed contrasts are asserted to negate log2FC without changing raw p values.

The edgeR tutorial's sample-distance block refers to an undefined DESeq2 `vsd` object. Here it uses edgeR's own TMM logCPM, prior count 2. DESeq2 uses VST with `blind=FALSE`. PCA uses the 500 highest-variance genes, centred without scaling, and does not remove cell-line effects. Distances use all retained transformed genes, with complete-linkage ordering. Volcanoes plot adjusted p values directly, so the 0.05 line represents the stated FDR rather than a guessed common raw-p boundary. Scatter displays crop extreme values for readability; correlation calculations use all shared finite estimates.

Local P5 SRR24828471 is public **MP2_K2v2**, while local P5_v2 SRR24828472 is public **MP2_K2**. ENA aliases, sample accessions and MD5 values were checked on October 4. The tutorial alternate choice drops public MP2_K2v2, hence retains SRR24828472. A second sensitivity retains SRR24828471. Neither library is declared an independent biological replicate, and original data are preserved.

The October 3 announcement additionally requested overlapping DE genes, logFC correlation, all tutorial plots and comparison with the supplied paper Data S1 CSV, for discussion on October 10. It did not specify an exact submission time or a primary effect-size threshold. LOO was deferred; no LOO analysis or classroom submission is included.

## Paper benchmark

[Klomp et al., Science 2024](https://pmc.ncbi.nlm.nih.gov/articles/PMC11301402/) Data S1 reports KRAS versus nonspecific siRNA, matching the contrast direction. Its CSV has 14,799 Ensembl rows: 224 have missing/nonnumeric Entrez IDs and 38 rows map ambiguously to numeric Entrez IDs. Excluding every ambiguous mapping, without selecting a favourable row, leaves 14,537 unique numeric Entrez IDs. The joint finite-estimate universe has 14,200 genes.

Across that universe, local DESeq2 versus paper edgeR logFC has Pearson 0.905/Spearman 0.923; local edgeR versus paper has Pearson 0.829/Spearman 0.869. At FDR < 0.05 and |log2FC| > 0.5, DESeq2 and paper share 1,497 genes (union 2,127; Jaccard 0.704), while edgeR and paper share 1,510 (union 2,637; Jaccard 0.573). Same-direction overlap is 1,497/1,497 and 1,509/1,510 respectively. Native FDR < 0.05 comparisons without the effect gate are also tabulated. Paper-wide thresholding selects 1,728 original rows; the common unique-ID subset has 1,690. These are different denominators. The effect-size gate is a post hoc selection rule, not a threshold-null hypothesis test.

The paper used STAR/Gencode v30, Salmon/tximport, coding/non-Y/non-mitochondrial restrictions, and at least 20 reads in two samples. The local input uses HISAT2/RefSeq featureCounts and the tutorial's 10-count filter. This is a benchmark rather than exact reproduction, and higher correlation does not identify a superior method. The classroom CSV and Rmd files are local references only and are excluded from this repository/package. File IDs, sizes and SHA256 values record their identity. Obtain Data S1 from the authorized classroom attachment or the article's public supplement to rerun the benchmark.

## Reproduce

Use R 4.5.2 and Python 3.12. The `renv.lock` pins Bioconductor 3.22, DESeq2 1.50.2, edgeR 4.8.2 and apeglm 1.32.0, including dependencies. A C/C++ compiler, Fortran, BLAS/LAPACK and zlib development files may be required for source installation. Use an isolated library; no system or permission changes are part of this workflow.

From the repository root:

```bash
cd analysis/2026-10-04-week4
Rscript scripts/restore.R "$PWD/runtime/R-library"
cd ../..
export R_LIBS_USER="$PWD/analysis/2026-10-04-week4/runtime/R-library"
export TZ=Etc/UTC
python3 -m venv analysis/2026-10-04-week4/runtime/python
analysis/2026-10-04-week4/runtime/python/bin/pip install -r analysis/2026-10-04-week4/requirements.txt
python3 analysis/2026-10-04-week4/scripts/audit_inputs.py "$PWD"
Rscript analysis/2026-10-04-week4/scripts/analyze.R "$PWD" /absolute/path/new-results /absolute/path/science.adk0775_data_s1.csv
Rscript analysis/2026-10-04-week4/scripts/analyze.R "$PWD" /absolute/path/repeat-results /absolute/path/science.adk0775_data_s1.csv
python3 analysis/2026-10-04-week4/scripts/verify_repeat.py /absolute/path/new-results /absolute/path/repeat-results
```

The output directory must be new; the script refuses to overwrite existing results. Omit the final CSV argument to run both real-data methods and P5 sensitivity without the paper benchmark. Input counts, metadata and gene labels are loaded from `analysis/2026-10-01/counts`. Gene IDs remain Entrez; missing symbols or multi-Ensembl labels do not cause gene removal or duplication. `audit_inputs.py` validates all 17 underlying run tables and hashes the inputs.

To remake the published figures/report, use the analysis directory with `results` containing the verified run. Set `FONT_DIR` to an authorized local directory containing Times New Roman TTF files. Fonts are not distributed. A process-specific fontconfig file with this directory enables the native R Cairo PDFs without changing system fonts.

```bash
python3 analysis/2026-10-04-week4/scripts/fontconfig.py "$FONT_DIR" /absolute/path/fontconfig.xml /absolute/path/font-cache
export FONTCONFIG_FILE=/absolute/path/fontconfig.xml
analysis/2026-10-04-week4/runtime/python/bin/python analysis/2026-10-04-week4/scripts/figures.py analysis/2026-10-04-week4 "$FONT_DIR"
analysis/2026-10-04-week4/runtime/python/bin/python analysis/2026-10-04-week4/scripts/report.py analysis/2026-10-04-week4 analysis/2026-10-04-week4/sources/report-template.docx /absolute/path/Week4.docx
libreoffice --headless --convert-to pdf --outdir /absolute/path/render /absolute/path/Week4.docx
analysis/2026-10-04-week4/runtime/python/bin/python analysis/2026-10-04-week4/scripts/finalize_pdf.py /absolute/path/render/Week4.pdf /absolute/path/Week4_final.pdf
```

Render DOCX to PDF using LibreOffice or the Codex document renderer and inspect every page before delivery. The report builder preserves template styles, numbering, theme, footer and section geometry byte-for-byte; it updates the report text, figures and current document metadata. Version 2 adds the immutable analysis reference and numbers citations by first appearance. Version 3 widens body paragraph gaps to 16 pt and appendix gaps to 18 pt, adds 6 pt cell padding on every side, keeps the short tables together, and starts References on a separate page. Version 4 adds light horizontal guides beneath the DE-count bars and candidate-expression data; existing FDR and diagonal reference lines are retained. Type sizes and line spacing follow the template. Remove automatically exported PDF outlines to retain the template's plain-heading format. The included template is the author's retained report template, not a classroom tutorial. The report has nine composite figures and four tables, with Times New Roman, true superscript citations, white tables and the requested blue/red/lapis palette.

## Verification and sources

Two fresh final R runs reproduced **81 TSV/method-JSON outputs byte-for-byte**. An independent Python calculation checked counts, intersections, unions, Jaccard denominators and correlations for every scenario and benchmark rule. Both reversed-contrast assertions passed. PDF metadata are excluded from byte comparisons. Primary package sources are official Bioconductor/CRAN; Python packages are from PyPI. Full session information and version inventories are retained. FASTQ, BAM, recordings, credentials, installed libraries and original private course attachments are excluded.

Method references: [DESeq2](https://doi.org/10.1186/s13059-014-0550-8), [edgeR v4](https://doi.org/10.1093/nar/gkaf018), [apeglm](https://doi.org/10.1093/bioinformatics/bty895). Input reference: [ENA PRJNA980201](https://www.ebi.ac.uk/ena/browser/view/PRJNA980201). Current input commit: `462867100fa1628d716cb7722a574da5f90577df`. Classroom files were read at their current October 3 version, with IDs and hashes in `sources/classroom_provenance.json`; simulation files were never used as real-data results.
