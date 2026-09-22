# Galaxy analysis record

This folder records the Week 2 quality checks and reference alignment of the PDAC KRAS RNA sequencing data. Results are added only after the corresponding Galaxy job has finished and its output has been checked.

## Starting state

On 22 September 2026, the active Galaxy history contained 30 raw FASTQ files and 26 FastQC webpage reports. No HISAT2 output was present before this analysis. The account used about 119 GB of its 268.4 GB quota.

The local input set contains 34 compressed FASTQ files from 17 sequencing runs. Both mates of KRAS P5 and KRAS P5_v2 were absent from the active history. The P5_v2 label identifies a separate run; it is not yet established as an independent biological replicate.

## Jobs submitted

| Tool | Input history numbers | Output history numbers | Purpose |
| --- | --- | --- | --- |
| FastQC 0.12.1, Galaxy 0.74+galaxy1 | 112, 111, 110, 106 | 113–120 | Complete quality checks for KRAS P3 and P4 |
| HISAT2 2.2.3, Galaxy 2.2.3+galaxy0 | 13, 15 | 121 BAM, 122 summary | Control M1 pilot, unstranded, first 1,000,000 read pairs |
| HISAT2 2.2.3, Galaxy 2.2.3+galaxy0 | 13, 15 | 123 BAM, 124 summary | Same Control M1 pilot, Forward FR |
| HISAT2 2.2.3, Galaxy 2.2.3+galaxy0 | 13, 15 | 125 BAM, 126 summary | Same Control M1 pilot, Reverse RF |
| ENA URL import | SRR24828471 and SRR24828472 | 127–130 | Both mates of KRAS P5 and P5_v2, fastqsanger.gz |
| HISAT2 2.2.3, Galaxy 2.2.3+galaxy0 | 7, 8 | 131 BAM, 132 summary | KRAS P1 pilot, unstranded, first 1,000,000 read pairs |
| HISAT2 2.2.3, Galaxy 2.2.3+galaxy0 | 7, 8 | 133 BAM, 134 summary | Same KRAS P1 pilot, Forward FR |
| HISAT2 2.2.3, Galaxy 2.2.3+galaxy0 | 7, 8 | 135 BAM, 136 summary | Same KRAS P1 pilot, Reverse RF |
| FastQC 0.12.1, Galaxy 0.74+galaxy1 | 129, 128, 127, 130 | 139–146 | Both mates of the two imported runs |
| MultiQC 1.35, Galaxy 1.35+galaxy4 | 34 FastQC raw-data reports listed below | 147 plots collection, 148 webpage, 149 statistics | Complete raw-read QC summary with plot-data export |

HISAT2 uses the built-in `Human (Homo sapiens) (b38): hg38` reference, paired-end input, Phred+33 qualities, no end trimming, and default alignment and splice settings. The pilot saves a machine-readable alignment summary. It does not represent a full-run alignment result.

No existing Galaxy datasets were deleted.

## Verified results

All six HISAT2 jobs finished successfully. The summary percentages below were checked against the job's standard-error summary and strand parameters. Overall alignment counts individual reads; concordant unique alignment counts read pairs. Each job processed exactly 1,000,000 pairs.

| Input | Strand setting | Overall read alignment | Concordant unique pairs | Summary |
| --- | --- | --- | --- | --- |
| Control M1 (Pa01C) | Unstranded | 96.63% | 86.40% | 122 |
| Control M1 (Pa01C) | FR | 96.63% | 86.44% | 124 |
| Control M1 (Pa01C) | RF | 96.63% | 86.44% | 126 |
| KRAS P1 (Pa16C) | Unstranded | 96.40% | 87.43% | 132 |
| KRAS P1 (Pa16C) | FR | 96.40% | 87.43% | 134 |
| KRAS P1 (Pa16C) | RF | 96.40% | 87.43% | 136 |

Full integer counts and job IDs are in [hisat2_pilot_results.json](hisat2_pilot_results.json). A small difference between these two cell lines cannot be attributed to KRAS treatment. Identical FR/RF percentages do not identify the library's strand specificity.

FastQC now has **34 reviewed raw-file reports**, covering all 17 complete mate pairs. The final aggregate uses 32 Galaxy reports plus two local FastQC 0.12.1 reports from complete SRR24828471 files (uploaded as 162/163). KRAS P3 has 42,073,244 reads per mate; P4 has 40,452,536; SRR24828472 has 43,166,706; SRR24828471 has 37,886,040. All are 150 bases long. Composition and duplication Fail in every file. Both SRR24828471 mates additionally have a GC-distribution Warn; other listed modules Pass. See [fastqc_review.json](fastqc_review.json) for source IDs and coverage.

**MultiQC 165 completed successfully**, with 34/34 General Statistics rows, 32 GC Pass results and two GC Warn results. The displayed duplication range is **57.0%–67.3%**. Stats are in 166 and eight plot-data tables in collection 164. [multiqc_summary.json](multiqc_summary.json) preserves the displayed values, explicitly rounded. The job ID is `bbd44e69cb8906b5a3cfd869f45c6d15`.

## Error diagnosis and repair

- Input 127 (SRR24828471 R1) was marked `ok`, but FastQC 143/144 failed with `Ran out of data in the middle of a fastq entry. Your file is probably truncated.` A green import alone does not establish a complete file.
- Input 128 (R2) failed import. The import log contains `OSError: [Errno 9] Bad file descriptor`; downstream FastQC 141/142 paused.
- MultiQC 147–149 depends on those reports, so it paused too. It is not a completed 34-file summary.
- A local R2 recovery copy passed gzip and ENA MD5 checks. A browser upload was interrupted before completion and is not a verified replacement. We switched to separate server-side ENA URL imports: **150 R1 and 151 R2**. Original error datasets were not removed.
- Replacement FastQC: **154 webpage / 155 raw data for R1 failed again**. Input 150 is only 738 MB, and the import log again contains an ignored `Bad file descriptor`. **152 webpage / 153 raw data for R2 completed** with the expected 37,886,040 reads.
- Both complete local files passed FastQC. R1 and R2 header first tokens match in order. The R2 compressed MD5 matches ENA. A complete canonical ENA R1 was downloaded and its compressed MD5 verified; every sequence and quality line matches the local R1. Details and commands are in [recovery_checks.json](recovery_checks.json) and [fastqc_local/README.md](fastqc_local/README.md).
- An independent **fasterq-dump 3.1.1+galaxy1** recovery succeeded: paired collection **156**, R1 **175**, R2 **176**, log **159**. The log records **37,886,040 spots, 75,772,080 reads read and written**, and two FASTQ files. It uses split-3, biological reads only, no minimum-length filter and gzip output. Single-end collection 157 and other collection 158 are empty, as expected for this fully paired run. Keep both SRA mates together; do not mix its instrument-based identifiers with an ENA mate.
- Final Galaxy FastQC checks on 175/176 **completed and were reviewed**: collections **179 webpage / 180 raw**, with **181/182 for R1** and **183/184 for R2**. Both contain 37,886,040 reads, 150 bp and 51% GC. Both have composition/duplication Fail, GC Warn and all remaining listed modules Pass, matching the local reports. They are independent validation reports, not two extra samples in MultiQC 165. The local-copy R1 upload is an auxiliary backup, not an additional sample.
- Inputs 127 and 150 have been renamed with the `DO_NOT_USE_TRUNCATED` prefix and annotated. Their data are retained.

## Exclusions

An extra FastQC job was accidentally submitted for pilot BAM dataset 131. Its outputs are 137 and 138. They are retained but excluded from the raw-FASTQ summary. The correction submitted FastQC separately for raw input 130, producing outputs 145 and 146.

Old paused MultiQC input history numbers: `3, 48, 50, 54, 56, 58, 60, 62, 64, 66, 68, 70, 72, 74, 76, 78, 80, 82, 84, 86, 88, 97, 99, 101, 103, 105, 114, 116, 118, 120, 140, 142, 144, 146`. Exclude **142, 144 and 155** (failed/paused) and **138** (BAM QC). The attempted replacement selection 155/153 did not produce a new MultiQC job after 155 failed. Select verified replacement reports only once recovery is complete.

Final successful MultiQC input IDs: `3, 48, 50, 54, 56, 58, 60, 62, 64, 66, 68, 70, 72, 74, 76, 78, 80, 82, 84, 86, 88, 97, 99, 101, 103, 105, 114, 116, 118, 120, 140, 146, 162, 163`. Report 153 is an independent check of the same R2 represented by 163 and is excluded to avoid double counting. Empty FastQC collections 160/161 (submitted before SRA collection population) and 177/178 (mapped from that empty output) contain no results and are also excluded. No empty collection is counted as a successful quality check.

## What the FastQC flags mean

Base-composition Fail measures unequal A/T or G/C proportions at read positions, not base-call accuracy. Library preparation, including RNA-seq priming bias, can cause this pattern. It does not by itself justify cutting a fixed number of bases. The specific cause is not proven by a module label.

Sequence-duplication Fail measures repeated read sequences within a file. Highly expressed transcripts naturally produce repeated sequences; PCR amplification can also contribute. Raw FastQC cannot separate these causes. Do not remove duplicate RNA-seq reads automatically or confuse this flag with duplicate uploads or repeated experimental samples.

All 34 reviewed files pass the adapter and base/read-quality modules. This supports progressing to mapping for complete valid pairs, but it does not prove transcript-level accuracy or differential expression. The older MultiQC 108 duplication range of 57.0%–65.2% covers only its 22 entries; the complete 34-file result is 57.0%–67.3%.

The restored R2 GC plot shows a broad, approximately bell-shaped distribution with a high-GC shoulder rather than an isolated sharp secondary peak. Its cause is unresolved. FastQC Warn indicates deviation from the fitted distribution; it is not a species-contamination test. Compare the mate's result and alignment evidence before deciding whether further contamination checks are needed.

Sources: [FastQC base composition](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/Help/3%20Analysis%20Modules/4%20Per%20Base%20Sequence%20Content.html), [FastQC duplication](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/Help/3%20Analysis%20Modules/8%20Duplicate%20Sequences.html), [GC distribution](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/Help/3%20Analysis%20Modules/5%20Per%20Sequence%20GC%20Content.html), [study design and methods](https://pmc.ncbi.nlm.nih.gov/articles/PMC11301402/).

## Next checks

1. Use restored pair 175/176 for subsequent Galaxy analysis; its independent FastQC results match the complete local checks.
2. Use successful MultiQC 165, not paused MultiQC 148; its 34 distinct file entries have been checked.
3. Keep the completed pilot summaries separate from later full-run alignment results.
4. Confirm library strand specificity from protocol information or annotated alignments. Do not infer it from the largest mapping percentage alone.
5. Remove the pilot limit for full alignments after validating inputs and settings.
6. Use the checked report dated 22 September; retain the older interim report as a historical snapshot. Keep raw reads and BAM files outside Git.

Auxiliary local R1 upload **185** is excluded from the sample count and the final MultiQC inputs. The history displays 2.8 GB and a FASTQ preview, but this backup has not received a separate post-upload completeness check. Use the independently validated SRA pair **175/176** for subsequent work.
