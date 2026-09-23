# PDAC KRAS RNA-seq analysis

This coursework project uses RNA sequencing (RNA-seq) to study pancreatic ductal adenocarcinoma (PDAC) cell lines. It compares control samples with samples treated with KRAS-targeting small interfering RNA (siRNA).

The data come from [PRJNA980201](https://www.ebi.ac.uk/ena/browser/view/PRJNA980201), published with Klomp et al., *Defining the KRAS- and ERK-dependent transcriptome in KRAS-mutant cancers* ([Science, 2024](https://doi.org/10.1126/science.adk0775)).

## Progress

The saved results cover work completed on 22 September 2026: quality checks for 34 FASTQ files and full HISAT2 alignments for 17 runs. Overall read alignment ranges from 95.79% to 97.72%.

KRAS M1 needs a pairing review: only 0.0030% of its read pairs align concordantly to a unique location. It needs further checks before gene counting. Gene counts and differential expression results are not yet available.

## Data and methods

The dataset contains eight cell lines, with eight control runs and nine KRAS runs. Each run has an R1 and an R2 file. M1–M3 refer to metastatic-source cell lines; P1–P5 refer to primary-source cell lines. Treatment comparisons use control and KRAS data from the same cell line.

MiaPaca-2 has an extra KRAS run whose repeat type is unclear. Both runs are kept separate. The [sample list](analysis/2026-09-22/run_manifest.md) maps local names to public accessions and explains the P5/P5_v2 naming.

The coursework workflow uses [Galaxy](https://galaxy-main.usegalaxy.org/), with FastQC for read quality, MultiQC for combined quality reports, and HISAT2 for alignment to human hg38. It differs from the paper's processing pipeline. Settings and results are recorded below.

## Reports and analysis

| File | Contents |
| --- | --- |
| [Week 2 report](reports/WK2YLINREP_2026-09-22_visual.pdf) | Methods, figures and result tables |
| [Analysis notes](analysis/2026-09-22/README.md) | Read quality, pilot alignments and file recovery |
| [Full alignment results](analysis/2026-09-22/full_alignment/README.md) | Results for all 17 runs, settings and the KRAS M1 issue |
| [Sample list](analysis/2026-09-22/run_manifest.md) | Cell lines, run accessions and input files |
| [中文说明](analysis/2026-09-22/interpretation_zh.md) | 分析进度、样本关系和结果说明 |

[galaxy_backup/](galaxy_backup/README.md) is reserved for Galaxy exports and dataset lists. No exports have been added yet.

The PDFs in `reports/` describe successive stages of the work. Their wording was revised on 23 September; each keeps its original data cutoff. Raw FASTQ and BAM alignment files are stored outside Git.

## Check the saved results

Run from the repository root with Python 3:

```sh
python3 analysis/2026-09-22/validate_summaries.py
python3 analysis/2026-09-22/full_alignment/validate_full_alignment.py
```

The scripts check summary arithmetic and quality-report coverage. The second rebuilds `results.json`. Neither checks the original reads or BAM files.
