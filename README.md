# PDAC KRAS RNA-seq analysis

This coursework project examines RNA sequencing (RNA-seq) data from pancreatic ductal adenocarcinoma (PDAC) cell lines treated with either control or KRAS-targeting small interfering RNA (siRNA). The aim is to compare gene expression between the two treatments within each cell line.

The repository contains analysis notes, result summaries and weekly reports. Quality checks and full-read alignments are complete. Gene counting and differential expression analysis are not yet reported.

## Start here

- [Week 2 report](reports/WK2YLINREP_2026-09-22_visual.pdf) — methods, figures and result tables.
- [Sample and run list](analysis/2026-09-22/run_manifest.md) — cell lines, public accessions and paired input files.
- [Full alignment results](analysis/2026-09-22/full_alignment/README.md) — alignment settings, results and the unresolved KRAS M1 issue.
- [Detailed analysis notes](analysis/2026-09-22/README.md) — quality checks, Galaxy jobs and file recovery.
- [中文说明](analysis/2026-09-22/interpretation_zh.md) — 质量检查、文件恢复和重复样本的说明。

## Data

The data come from [PRJNA980201](https://www.ebi.ac.uk/ena/browser/view/PRJNA980201), published with Klomp et al., *Defining the KRAS- and ERK-dependent transcriptome in KRAS-mutant cancers* ([Science, 2024](https://doi.org/10.1126/science.adk0775)).

There are **17 paired-end sequencing runs** across eight cell lines: eight control runs and nine KRAS siRNA runs. Each run has two FASTQ files, R1 and R2, giving 34 files in total.

M1–M3 label cell lines from metastatic sites; P1–P5 label cell lines from primary tumours. These are different cell lines, not matched primary and metastatic samples from the same patients.

MiaPaca-2 has two KRAS runs. Whether the extra run is a biological or technical repeat remains unclear, so the two runs are kept separate. Their local P5/P5_v2 labels differ from the public naming; use the [run accessions](analysis/2026-09-22/run_manifest.md#the-two-miapaca-2-kras-runs) to identify them.

## Progress

Based on the analysis records dated **22 September 2026**:

| Step | Status |
| --- | --- |
| Read quality | All 34 files reviewed with FastQC and included in MultiQC. Adapter and base/read-quality checks pass; composition and duplication flags remain. |
| Alignment | HISAT2 summaries are available for all 17 full runs against human hg38. Overall read alignment ranges from 95.79% to 97.72%. |
| KRAS M1 review | Unresolved. Only 0.0030% of pairs align concordantly to a unique location, despite 96.51% overall read alignment. Check the paired inputs and alignment settings before gene counting. |
| Gene counts and differential expression | Not yet reported. No treatment effect has been established. |

FastQC composition and duplication flags alone do not mean the reads are unusable. Likewise, a high overall alignment rate does not confirm correct pairing, as the KRAS M1 result shows.

## Analysis workflow

The analysis uses [Galaxy](https://galaxy-main.usegalaxy.org/):

1. Check sample identities and R1/R2 pairing.
2. Review read quality with FastQC and MultiQC.
3. Test alignment settings on a subset of reads and assess library strand specificity.
4. Align the full paired reads with HISAT2 against hg38.
5. Review alignment results before counting genes.

Strand checks support unstranded alignment for Control M1 and KRAS P1. The other runs used the same setting without individual confirmation. Pilot runs used the first 1,000,000 read pairs; their results are separate from the full alignments.

This is a coursework workflow, not an exact reproduction of the paper's processing pipeline. Tool versions and settings are recorded in the [analysis notes](analysis/2026-09-22/README.md) and [full alignment record](analysis/2026-09-22/full_alignment/README.md#parameters-and-strand-inference).

## Files and checks

`analysis/2026-09-22/` holds the notes, parameters, source alignment summaries and validation scripts. `reports/` holds the weekly PDFs and figures. Earlier reports are retained as snapshots of the work at those stages.

To check the saved summaries, run these commands from the repository root with Python 3:

```sh
python3 analysis/2026-09-22/validate_summaries.py
python3 analysis/2026-09-22/full_alignment/validate_full_alignment.py
```

These scripts check summary arithmetic and quality-check coverage. The second also regenerates `results.json`. They do not inspect the original reads or alignment files.

Raw FASTQ and BAM alignment files are kept outside Git, in Galaxy or separate data storage. Use the run list to locate inputs. Galaxy dataset numbers refer to the original history and are not public accession numbers.
