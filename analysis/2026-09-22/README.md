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

## Pending results and exclusions

At the latest check on 22 September, the new outputs were still unavailable. HISAT2 pilots and the missing-file imports had not returned usable results. No mapping rate or full-run alignment is claimed. MultiQC also depends on the pending FastQC jobs.

An extra FastQC job was accidentally submitted for pilot BAM dataset 131. Its outputs are 137 and 138. They are retained but excluded from the raw-FASTQ summary. The correction submitted FastQC separately for raw input 130, producing outputs 145 and 146.

MultiQC input history numbers: `3, 48, 50, 54, 56, 58, 60, 62, 64, 66, 68, 70, 72, 74, 76, 78, 80, 82, 84, 86, 88, 97, 99, 101, 103, 105, 114, 116, 118, 120, 140, 142, 144, 146`. These are 34 distinct raw-data reports. Output 138 is not included.

## Next checks

1. Check whether the imports and quality checks finish successfully. Inspect errors before retrying any job.
2. Confirm MultiQC contains 34 distinct file entries with the expected R1/R2 names.
3. Read the six pilot alignment summaries and record paired-read denominators and strand options.
4. Confirm library strand specificity from protocol information or annotated alignments. Do not infer it from the largest mapping percentage alone.
5. Remove the pilot limit for full alignments after validating inputs and settings.
6. Replace the interim report only after checking the new results. Keep raw reads and BAM files outside Git.
