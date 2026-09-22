# PDAC KRAS RNA sequencing analysis

This repository records a coursework analysis of RNA sequencing data from pancreatic ductal adenocarcinoma (PDAC) cells treated with control or KRAS-targeting small interfering RNA (siRNA). The current work checks read quality and prepares reference-genome alignments. It does not yet establish differential gene expression or treatment effects.

## Data

The project uses public sequencing data associated with [PRJNA980201](https://www.ebi.ac.uk/ena/browser/view/PRJNA980201) and Klomp et al., *Defining the KRAS- and ERK-dependent transcriptome in KRAS-mutant cancers* ([Science, 2024](https://doi.org/10.1126/science.adk0775)).

The local input inventory contains 17 paired-end sequencing runs, or 34 compressed FASTQ files:

- Control siRNA: M1–M3 and P1–P5, eight runs.
- KRAS siRNA: M1–M3, P1–P5 and P5_v2, nine runs.

Each run has an R1 and an R2 file. P5_v2 is a separate sequencing-run label; its biological-replicate status must be confirmed before any statistical comparison. M and P labels are retained as supplied and should not be assigned a biological meaning without checking the study metadata.

The [run manifest](analysis/2026-09-22/run_manifest.md) maps these local labels to public accessions and ENA sample aliases. In particular, local KRAS P5 maps to `SRR24828471` / `MP2_K2v2`, whereas local P5_v2 maps to `SRR24828472` / `MP2_K2`. Use the accession, not the suffix alone, to identify each run.

## Workflow

1. Check sample names, run accessions and R1/R2 pairing.
2. Run FastQC on both mates to assess quality, sequence composition, duplication and adapters.
3. Combine the FastQC outputs with MultiQC and check that every file is included.
4. Decide whether adapter or quality trimming is needed from the actual quality checks.
5. Use HISAT2 to align paired reads to the human hg38 reference. Compare strand settings in pilot runs before full-run alignment.
6. Save the alignment summaries, record the exact parameters, and update the weekly report.

Analyses run on [Galaxy](https://galaxy-main.usegalaxy.org/). This is a coursework workflow; it should not be described as an exact reproduction of the paper's processing pipeline.

## Current status

Analysis is in progress. At the start of the 22 September 2026 review, Galaxy contained 30 input files and 26 FastQC reports. Additional quality checks, missing-file imports and HISAT2 pilots have been submitted. Submission does not mean a job has finished. See the [dated analysis record](analysis/2026-09-22/README.md) for dataset numbers and settings.

Pilot alignments use the first 1,000,000 read pairs, not a random sample or the full sequencing run. Their mapping percentages must be labeled as pilot results. No gene-count matrix, differential-expression result or enrichment analysis is currently reported.

The [Week 2 interim report](reports/WK2YLINREP_2026-09-22_interim.pdf) contains the 26 previously checked FastQC reports and distinguishes them from pending work. The new MultiQC job uses 34 raw-read FastQC inputs; it must finish before its coverage and results can be confirmed.

## Repository contents

- `analysis/2026-09-22/`: analysis records, parameters and checked result summaries.
- `reports/`: dated progress reports; filenames marked `interim` are not final alignment reports.
- `.gitignore`: excludes raw reads, large alignment files and local secrets.

Raw FASTQ and BAM files are not stored in Git. Keep them in Galaxy or dedicated data storage, and use public accessions and manifests to locate inputs. Galaxy history numbers identify datasets within the originating history; they are not public accession numbers.

## Reproducing the analysis

Use the same paired inputs and reference build, and record the Galaxy tool versions and selected options. For a full alignment, remove the pilot read limit. Do not choose library orientation solely because one setting gives the highest mapping rate; check the library protocol or infer strand specificity from annotated alignments.

FastQC composition and duplication failures do not, by themselves, prove that RNA sequencing data are unusable. Unequal transcript abundance and library preparation can affect these checks. Do not remove duplicate RNA reads automatically.

## References

- [FastQC documentation](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/)
- [MultiQC documentation](https://docs.seqera.io/multiqc)
- [HISAT2 manual](https://daehwankimlab.github.io/hisat2/manual/)
- [Galaxy Training Network](https://training.galaxyproject.org/)
