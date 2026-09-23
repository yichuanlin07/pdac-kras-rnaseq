# Analysis notes — 22 September 2026

This folder records the Week 2 analysis in Galaxy: sample checks, recovery of missing files, read quality and alignment to human hg38.

The 22 September results include quality checks for all 34 FASTQ files and full alignment summaries for 17 runs in [full_alignment/](full_alignment/README.md), including the unresolved KRAS M1 pairing issue.

## Read quality

FastQC reviewed both files from each run. MultiQC 165 combines 32 Galaxy reports with two [local reports](fastqc_local/README.md) for the recovered SRR24828471 files.

| Check | Result |
| --- | --- |
| Files included | 34, covering 17 complete pairs |
| Base/read quality, N content, read length, overrepresented sequences and adapters | All pass |
| Base composition and sequence duplication | Fail in all files |
| GC distribution | Warn for both SRR24828471 mates; pass for the other 32 files |
| Duplication | 57.0%–67.3% |

Library preparation can affect base composition, while abundant transcripts and amplification can produce repeated sequences. The flags do not identify the cause, so they were not used alone to decide on trimming or duplicate removal. The GC warning also leaves the cause unresolved.

The complete results are in [fastqc_review.json](fastqc_review.json) and [multiqc_summary.json](multiqc_summary.json). Galaxy dataset 166 holds the MultiQC statistics, and collection 164 holds the plot data. The older MultiQC 108 covers only 22 files; MultiQC 148 paused after input failures.

## Pilot alignments

Six HISAT2 pilot jobs each used the first 1,000,000 read pairs. They tested three strand settings on Control M1 and KRAS P1.

| Input | Strand setting | Overall read alignment | Concordant unique pairs | Galaxy summary |
| --- | --- | ---: | ---: | --- |
| Control M1 | Unstranded | 96.63% | 86.40% | 122 |
| Control M1 | FR | 96.63% | 86.44% | 124 |
| Control M1 | RF | 96.63% | 86.44% | 126 |
| KRAS P1 | Unstranded | 96.40% | 87.43% | 132 |
| KRAS P1 | FR | 96.40% | 87.43% | 134 |
| KRAS P1 | RF | 96.40% | 87.43% | 136 |

FR and RF are the forward and reverse strand options. Their similar mapping rates do not identify strand specificity. Later RSeQC checks supported unstranded alignment for these two inputs; see the [full alignment settings](full_alignment/README.md#parameters-and-strand-inference).

Control M1 and KRAS P1 are different cell lines, so their alignment rates cannot isolate a treatment effect. Counts and job IDs are saved in [hisat2_pilot_results.json](hisat2_pilot_results.json); settings are in [pilot_parameters.json](pilot_parameters.json).

The pilots used HISAT2 2.2.3+galaxy0, the built-in hg38 reference, paired-end reads, Phred+33 quality scores, no end trimming and default alignment and splice settings.

## Recovering KRAS P5

Both KRAS P5 and P5_v2 were missing from the active history at the start. P5_v2 imported successfully. P5 (`SRR24828471`) needed several recovery attempts:

| Attempt | Outcome |
| --- | --- |
| First import, 127/128 | R1 was truncated; R2 failed. FastQC reported an incomplete FASTQ entry. |
| Second import, 150/151 | R1 was truncated again, at 738 MB rather than about 2.58 GB. R2 passed FastQC. |
| Local files | Both complete files passed the file checks and produced FastQC reports uploaded as 162/163. |
| SRA Toolkit recovery, collection 156 | Recovered both complete mates as 175/176. FastQC 181/183 confirmed the expected read counts and quality results. |

The failed imports logged `OSError: [Errno 9] Bad file descriptor`. Inputs 127 and 150 are labelled `DO_NOT_USE_TRUNCATED`. Use **175/176 together** for analysis: their identifier format differs from the ENA export.

SRA Toolkit 3.1.1+galaxy1 used split-3, biological reads only, no minimum-length filter and gzip output. Log 159 records 37,886,040 spots and 75,772,080 reads written. Both recovered mates contain 37,886,040 reads, 150 bases long, with 51% GC. Their FastQC flags match the local files.

The local R2 matches the ENA MD5 checksum. Every local R1 sequence and quality line matches the complete, checksum-verified ENA R1, and all local R1/R2 read identifiers match in order. Commands and checks are recorded in [recovery_checks.json](recovery_checks.json) and the [sample list](run_manifest.md).

## Galaxy records

The following dataset numbers belong to the Galaxy history used for this analysis.

| Work | Inputs | Outputs |
| --- | --- | --- |
| FastQC for KRAS P3/P4 | 112, 111, 110, 106 | 113–120 |
| Control M1 pilots | 13/15 | 121–126 |
| KRAS P1 pilots | 7/8 | 131–136 |
| Initial P5/P5_v2 imports | SRR24828471/472 | 127–130 |
| FastQC for those imports | 127–130 | 139–146 |
| Paused MultiQC | Initial report selection | 147–149 |
| Successful MultiQC | 32 Galaxy reports and local reports 162/163 | 164–166 |
| SRA recovery | SRR24828471 | Mates 175/176 in collection 156; log 159 |
| Recovery FastQC | 175/176 | Web reports 181/183; raw reports 182/184 |

FastQC used version 0.12.1 with Galaxy wrapper 0.74+galaxy1. MultiQC used 1.35+galaxy4. The successful MultiQC job ID is `bbd44e69cb8906b5a3cfd869f45c6d15`.

Its input reports were:

```text
3, 48, 50, 54, 56, 58, 60, 62, 64, 66, 68, 70, 72, 74, 76, 78,
80, 82, 84, 86, 88, 97, 99, 101, 103, 105, 114, 116, 118, 120,
140, 146, 162, 163
```

Failed or paused reports 142, 144 and 155 were excluded. Reports 137/138 came from an accidental FastQC run on a pilot BAM file. Report 153 and recovery reports 181–184 check mates already represented in MultiQC. Empty collections 160/161 and 177/178 were also excluded. Local R1 upload 185 is a backup without a separate completeness check.

At the end of this analysis, existing datasets remained in the history. The [sample list](run_manifest.md) identifies the inputs used for analysis, and the [full alignment record](full_alignment/README.md) covers the later runs.

## Check the saved summaries

From the repository root:

```sh
python3 analysis/2026-09-22/validate_summaries.py
```

This checks pilot arithmetic, coverage of the 34 files, MultiQC entries and the saved local report hashes. It does not inspect the original reads.

For help interpreting the quality flags, see the FastQC documentation on [base composition](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/Help/3%20Analysis%20Modules/4%20Per%20Base%20Sequence%20Content.html), [duplication](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/Help/3%20Analysis%20Modules/8%20Duplicate%20Sequences.html) and [GC distribution](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/Help/3%20Analysis%20Modules/5%20Per%20Sequence%20GC%20Content.html).
