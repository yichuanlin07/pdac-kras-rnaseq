# Week 6 pathway analysis

Cell-cycle gene sets are enriched among genes with lower expression after KRAS siRNA treatment. E2F targets and the G2M checkpoint show the strongest Hallmark enrichment among downregulated genes in the joint list. The primary CAMERA analysis has a minimum global adjusted P value of 0.354; 46 ORA set-direction combinations meet q < 0.05.

The [English PDF](../../reports/Week6_2026-10-30/PDAC_KRAS_Week6_2026-10-30.pdf) and [editable English report](../../reports/Week6_2026-10-30/PDAC_KRAS_Week6_2026-10-30.docx) contain the findings, methods, figures and tables. The prose describes data, methods and results directly.

## Data and methods

The corrected matrix contains 28,395 gene rows across 17 source libraries. KRAS M1 has 37,657,740 assigned counts. Pooling the two MiaPaca-2 KRAS libraries gives 16 observations across eight paired cell lines; 17,819 genes pass filtering.

The primary model uses TMM normalization, logCPM with prior count 2, limma-trend and the paired design `~cell_line + condition`. CAMERA estimates residual gene correlation within each set. BH correction covers 50 Hallmark and 1,122 Reactome sets together. Sensitivity fits include eight paired cell-line omissions and two single-library P5 models. A separate calibration sensitivity fixes correlation at 0.01.

ORA uses the earlier 2,020-gene joint DESeq2/edgeR list, its 1,515-gene stability subset and the recorded eligible and retained backgrounds. Each list/background analysis jointly corrects both directions and both collections. Input snapshots and hashes are in [sources/input_validation.json](sources/input_validation.json). The input revision is `7e3fe15664597474008b63753dd9e4b20efec04a`.

## Reproduce the results

Use R 4.5.2, edgeR 4.8.2 and limma 3.66.0, with the Python versions in [requirements_figures.txt](scripts/requirements_figures.txt). Set `R_LIBS_USER` to an existing library containing the recorded R package versions. The package lock is in `sources/reference_renv.lock`.

From the repository root, choose a fresh output directory and run:

```bash
mkdir -p /tmp/pdac-week6-repeat
cp -a analysis/2026-10-30-week6/sources /tmp/pdac-week6-repeat/sources
Rscript analysis/2026-10-30-week6/scripts/analyze_pathways.R /tmp/pdac-week6-repeat
Rscript analysis/2026-10-30-week6/scripts/verify_contrast.R /tmp/pdac-week6-repeat
python3 analysis/2026-10-30-week6/scripts/figures_and_verify.py /tmp/pdac-week6-repeat
python3 analysis/2026-10-30-week6/scripts/build_report.py /tmp/pdac-week6-repeat /tmp/pdac-week6-repeat/sources/report_template.docx /tmp/pdac-week6-repeat/qa
```

`prepare_inputs.py` checks the source count tables against the matrix and prepares snapshots using repository-relative paths. Existing frozen snapshots support the commands above. `build_report.py` builds the English report using the retained template; PDF export uses a document renderer.

## Validation

The October 30 verification records Python compilation, R parsing, removal of source comments and docstrings, and equality of executable Python ASTs and parsed R expressions after comment removal. It also records a fresh eleven-model analysis, numerical table comparisons, independent hypergeometric and BH checks, and reversed-order/reversed-contrast CAMERA checks. Details are in `sources/code_validation.json`.

Complete tables are in `results/`, report tables in `tables/` and figures in `figures/`. The adjacent report directory holds the current English files. The local bilingual review copy is maintained in the research archive.
