# Week 4: KRAS siRNA differential expression

The [count matrix](../2026-10-01/counts/counts_raw.txt) has 28,395 genes and 17 runs from eight cell lines. DESeq2 and edgeR estimate KRAS siRNA versus control; positive log2FC means higher expression after KRAS siRNA.

The main analysis sums SRR24828471 and SRR24828472 into one MiaPaca-2 KRAS observation, following the October 3 tutorial. Separate fits retain each library in turn. Local P5 is SRR24828471, public **MP2_K2v2**; local P5_v2 is SRR24828472, public **MP2_K2**. The local v2 labels are reversed. ENA records confirm the aliases, accessions and distinct file MD5 values, but do not establish the repeat type. The merged analysis is exploratory. Both original libraries are retained in the input files.

## Results

At FDR < 0.05, DESeq2 detects 5,943 genes and edgeR detects 6,431. They share 5,442 genes, with a union of 6,932 and Jaccard 0.785. Unshrunk log2FC estimates correlate at Pearson 0.884 and Spearman 0.910 across 17,819 shared finite estimates.

| P5 handling | Retained genes | DESeq2 DE | edgeR DE | Shared DE |
| --- | ---: | ---: | ---: | ---: |
| Sum SRR24828471 + SRR24828472 | 17,819 | 5,943 | 6,431 | 5,442 |
| Retain SRR24828472 | 17,734 | 5,724 | 6,131 | 5,269 |
| Retain SRR24828471 | 17,705 | 6,004 | 6,535 | 5,568 |

In the main fit, DESeq2 finds 2,912 downregulated and 3,031 upregulated genes; edgeR finds 2,923 downregulated and 3,508 upregulated genes. Across both methods and all three P5 choices, 5,084 genes pass FDR < 0.05 with the same direction. These fits share samples and assess sensitivity to library handling.

KRAS, DUSP6, SPRY4, MYC and CCND1 decrease across the fits; EMP2 increases. MYC decreases in seven of eight normalized pairs. DPM3 loses edgeR significance when only SRR24828472 is used, and EGR1 differs between methods. Expression changes alone do not show direct regulation or protein effects.

## Methods

Each P5 choice leaves 16 observations, one control and one treatment per cell line. The design is `~condition + cell_line`, with Control as reference and `Treatment` for KRAS siRNA. It has nine full-rank columns and seven residual degrees of freedom. The model estimates a common treatment effect, without a treatment-by-cell-line interaction or within-line replication. Genes with counts >= 10 in at least two samples are retained separately in each fit. The primary DE lists use FDR < 0.05 without a log2FC cutoff and test a zero-effect null.

DESeq2 uses median-of-ratios size factors, negative-binomial dispersion fitting, Wald tests and independent filtering at `alpha=0.05`. Its full table also includes adjusted p values at the tutorial's default `alpha=0.1` and without independent filtering. Common-finite-p BH columns are in the method-comparison table. `apeglm` estimates are used in plots; tests and correlations use unshrunk log2FC. Posterior SD and Wald SE are separate columns.

edgeR uses TMM, `estimateDisp(robust=TRUE)`, `glmQLFit(robust=TRUE)` and `glmQLFTest` for `conditionTreatment`. Version 4.8.2 uses `legacy=FALSE` by default; the paper used version 3. BH adjustment covers the retained genes. Reversing the contrast in both methods negates log2FC and preserves raw p values.

DESeq2 QC uses VST with `blind=FALSE`; edgeR QC uses TMM logCPM with prior count 2, replacing the tutorial's undefined DESeq2 `vsd` object. PCA uses the 500 highest-variance genes, centred without scaling. Cell-line effects are not removed. Distances use all retained transformed genes and complete-linkage ordering. Volcanoes show adjusted p values with the FDR 0.05 line. Scatter plots crop extreme values for display; correlations use all shared finite estimates.

## Comparison with the paper

[Klomp et al., Science 2024](https://pmc.ncbi.nlm.nih.gov/articles/PMC11301402/) Data S1 uses the same contrast direction. Ambiguous Entrez mappings are excluded. The common subset has 14,200 genes with finite estimates in the paper and local results.

Local DESeq2 versus paper edgeR logFC has Pearson 0.905 and Spearman 0.923; local edgeR versus paper has Pearson 0.829 and Spearman 0.869. At FDR < 0.05 and |log2FC| > 0.5, DESeq2 shares 1,497 genes with the paper (Jaccard 0.704), and edgeR shares 1,510 (Jaccard 0.573). Directions agree for 1,497/1,497 and 1,509/1,510 shared genes, respectively. The effect-size cutoff selects genes after testing; it does not change the null hypothesis. Comparisons without that cutoff are also tabulated.

The paper used STAR/Gencode v30, Salmon/tximport, coding/non-Y/non-mitochondrial restrictions and at least 20 reads in two samples. This analysis uses HISAT2/RefSeq featureCounts and the tutorial's 10-count filter. The pipelines differ, and correlation alone cannot rank the methods. To rerun the comparison, obtain Data S1 from the article supplement or classroom attachment. Course originals are not included; their IDs and SHA256 values are in [classroom_provenance.json](sources/classroom_provenance.json).

## Files

- [DESeq2 full table](results/merge_p5/DESeq2_full.tsv) and [edgeR full table](results/merge_p5/edgeR_full.tsv): all 28,395 input genes, including filter status.
- [Scenario summary](results/scenario_summary.tsv), [P5 sensitivity](results/sensitivity_full.tsv), [sensitivity metrics](results/sensitivity_metrics.tsv) and [candidate review](results/candidate_review.tsv).
- [Method comparison](results/merge_p5/method_comparison.tsv), [paper comparison](results/paper_comparison_summary.tsv), [mapping exclusions](results/paper_excluded_mapping_rows.tsv) and [paper input checks](results/paper_input_audit.tsv).
- [Figures](figures): PCA, sample distances, volcanoes, DE counts, method agreement, P5 sensitivity, paper comparison, paired expression, mean/SD, dispersion, raw-run QC and MA/MD plots. Native R dispersion diagnostics are in each scenario's results folder.
- [Report DOCX](../../reports/PDAC_KRAS_Week4_2026-10-06_v4.docx) and [PDF](../../reports/PDAC_KRAS_Week4_2026-10-06_v4.pdf).
- [Input checks](sources/input_validation.json), [numerical checks](results/independent_numerical_validation.json), [repeat-run results](results/repeat_run_validation.json), [document checks](sources/report_render_validation_2026-10-06_v4.json) and [source review](sources/source_review_2026-10-06_v7.json).

## Run the analysis

Use R 4.5.2 and Python 3.12. [renv.lock](renv.lock) pins Bioconductor 3.22, DESeq2 1.50.2, edgeR 4.8.2, apeglm 1.32.0 and their dependencies. Source installation may need C/C++, Fortran, BLAS/LAPACK and zlib development files.

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

Use new output directories; the script refuses to overwrite results. Omit the CSV argument to run both methods and P5 sensitivity without the paper comparison. Counts, metadata and gene labels come from `analysis/2026-10-01/counts`. Entrez IDs are kept even when symbols are missing or Ensembl labels are multiple. The input-check script compares the matrix with all 17 run tables.

Two fresh R runs produced 81 identical TSV and method-JSON files. Separate Python checks reproduced the DE counts, overlaps, Jaccard values and correlations. PDF creation metadata and session text are excluded from byte comparisons. Versions and session information are in the results folder.

## Build figures and the report

Use an analysis directory containing the completed `results`. Set `FONT_DIR` to a folder with Times New Roman TTF files, then run:

```bash
python3 analysis/2026-10-04-week4/scripts/fontconfig.py "$FONT_DIR" /absolute/path/fontconfig.xml /absolute/path/font-cache
export FONTCONFIG_FILE=/absolute/path/fontconfig.xml
analysis/2026-10-04-week4/runtime/python/bin/python analysis/2026-10-04-week4/scripts/figures.py analysis/2026-10-04-week4 "$FONT_DIR"
analysis/2026-10-04-week4/runtime/python/bin/python analysis/2026-10-04-week4/scripts/report.py analysis/2026-10-04-week4 analysis/2026-10-04-week4/sources/report-template.docx /absolute/path/Week4.docx
libreoffice --headless --convert-to pdf --outdir /absolute/path/render /absolute/path/Week4.docx
analysis/2026-10-04-week4/runtime/python/bin/python analysis/2026-10-04-week4/scripts/finalize_pdf.py /absolute/path/render/Week4.pdf /absolute/path/Week4_final.pdf
```

The report builder reuses the included DOCX template. Inspect every PDF page for clipping, table breaks and figure labels. Fonts, installed libraries, FASTQ, BAM and recordings are not included in the package.

## Sources and next work

[DESeq2](https://doi.org/10.1186/s13059-014-0550-8), [edgeR v4](https://doi.org/10.1093/nar/gkaf018), [apeglm](https://doi.org/10.1093/bioinformatics/bty895) and [ENA PRJNA980201](https://www.ebi.ac.uk/ena/browser/view/PRJNA980201). Input commit: `462867100fa1628d716cb7722a574da5f90577df`.

The October 10 discussion covers method overlap, logFC correlation, tutorial plots and the paper comparison. The October 3 announcement did not set a primary effect-size cutoff or an exact submission time. Leave-one-cell-line-out analysis was deferred to the next session. Simulation files were not used in these real-data results.
