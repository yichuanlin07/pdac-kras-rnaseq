# PDAC KRAS RNA sequencing analysis

This repository records a coursework analysis of RNA sequencing data from pancreatic ductal adenocarcinoma (PDAC) cells treated with control or KRAS-targeting small interfering RNA (siRNA). The current work checks read quality and prepares reference-genome alignments. It does not yet establish differential gene expression or treatment effects.

## Data

The project uses public sequencing data associated with [PRJNA980201](https://www.ebi.ac.uk/ena/browser/view/PRJNA980201) and Klomp et al., *Defining the KRAS- and ERK-dependent transcriptome in KRAS-mutant cancers* ([Science, 2024](https://doi.org/10.1126/science.adk0775)).

The local input inventory contains 17 paired-end sequencing runs, or 34 compressed FASTQ files:

- Control siRNA: M1–M3 and P1–P5, eight runs.
- KRAS siRNA: M1–M3, P1–P5 and P5_v2, nine runs.

Each run has an R1 and an R2 file. ENA records confirm that M1–M3 are metastatic-source cell lines and P1–P5 are primary-source cell lines. These are different cell lines, not patient-matched primary/metastatic samples. Compare control and KRAS treatment within each cell line.

The extra MiaPaca-2 KRAS run has `replicate=TRUE` in ENA, but the record does not distinguish biological from technical repetition. Do not merge or discard it, or count it as a ninth independent cell-line replicate, without resolving the study design. See the manifest for all eight cell lines and BioSample accessions.

The [run manifest](analysis/2026-09-22/run_manifest.md) maps these local labels to public accessions and ENA sample aliases. In particular, local KRAS P5 maps to `SRR24828471` / `MP2_K2v2`, whereas local P5_v2 maps to `SRR24828472` / `MP2_K2`. Use the accession, not the suffix alone, to identify each run.

## Workflow

1. Check sample names, run accessions and R1/R2 pairing.
2. Run FastQC on both mates to assess quality, sequence composition, duplication and adapters.
3. Combine the FastQC outputs with MultiQC and check that every file is included.
4. Decide whether adapter or quality trimming is needed from the actual quality checks.
5. Use HISAT2 to align paired reads to human hg38. Check library strand specificity from the protocol or annotated alignments before full-run alignment; mapping-rate comparisons alone do not establish it.
6. Save the alignment summaries, record the exact parameters, and update the weekly report.

Analyses run on [Galaxy](https://galaxy-main.usegalaxy.org/). This is a coursework workflow; it should not be described as an exact reproduction of the paper's processing pipeline.

## Current status

Checked on 22 September 2026:

- **All 34 raw files reviewed:** 17 complete run pairs. The summary uses 32 Galaxy FastQC reports plus two local FastQC 0.12.1 reports for verified complete SRR24828471 files. All pass base/read quality, N content, length, overrepresented-sequence and adapter checks. All have base-composition and duplication Fail flags. Both SRR24828471 mates have a GC-distribution Warn. These module flags are not failed software jobs.
- **Six HISAT2 pilots completed:** Control M1 overall alignment 96.63%; KRAS P1 96.40%, for each of unstranded, FR and RF settings. These two inputs are different cell lines, so the difference is not evidence of a treatment effect.
- **Complete MultiQC finished:** dataset 165 contains exactly 34 file entries; duplication ranges from 57.0% to 67.3%. Statistics are in 166 and plot data in collection 164. This replaces paused summary 148.
- **Complete paired data recovered and verified on Galaxy:** SRA Toolkit recovered SRR24828471 into collection 156: **175 forward/R1 and 176 reverse/R2**. Log 159 records 37,886,040 spots and 75,772,080 reads written. Independent FastQC 181/183 confirms 37,886,040 reads per mate, 150 bp, 51% GC and the same module flags as the complete local files. Both truncated R1 imports are marked `DO_NOT_USE_TRUNCATED` and retained.

See the [dated analysis record](analysis/2026-09-22/README.md) for dataset numbers, repair status and checked results. All existing datasets are retained.

Pilot alignments use the first 1,000,000 read pairs, not a random sample or the full sequencing run. Their mapping percentages must be labeled as pilot results. No gene-count matrix, differential-expression result or enrichment analysis is currently reported.

The [updated Week 2 report](reports/WK2YLINREP_2026-09-22_checked.pdf) includes the complete QC summary, completed pilot alignments, sample-design limits and repair status. The older interim PDF is retained as a historical snapshot. A [Chinese explanation](analysis/2026-09-22/interpretation_zh.md) distinguishes QC flags, file damage and sample replication.

## Repository contents

- `analysis/2026-09-22/`: analysis records, parameters and checked result summaries.
- `reports/`: dated progress reports; filenames marked `interim` are not final alignment reports.
- `.gitignore`: excludes raw reads, large alignment files and local secrets.

Small result files include `hisat2_pilot_results.json`, `fastqc_review.json` and `validate_summaries.py`. Run `python3 analysis/2026-09-22/validate_summaries.py` to check pilot arithmetic and QC coverage. This validates the transcribed summaries, not the underlying reads.

Raw FASTQ and BAM files are not stored in Git. Keep them in Galaxy or dedicated data storage, and use public accessions and manifests to locate inputs. Galaxy history numbers identify datasets within the originating history; they are not public accession numbers.

## Reproducing the analysis

Use the same paired inputs and reference build, and record the Galaxy tool versions and selected options. For a full alignment, remove the pilot read limit. Do not choose library orientation solely because one setting gives the highest mapping rate; check the library protocol or infer strand specificity from annotated alignments.

FastQC composition and duplication failures do not, by themselves, prove that RNA sequencing data are unusable. Unequal transcript abundance and library preparation can affect these checks. Do not remove duplicate RNA reads automatically.

## References

- [FastQC documentation](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/)
- [MultiQC documentation](https://docs.seqera.io/multiqc)
- [HISAT2 manual](https://daehwankimlab.github.io/hisat2/manual/)
- [Galaxy Training Network](https://training.galaxyproject.org/)
