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

HISAT2 uses the built-in `Human (Homo sapiens) (b38): hg38` reference, paired-end input, Phred+33 qualities, no end trimming, and default alignment and splice settings. The pilot saves a machine-readable alignment summary. It does not represent a full-run alignment result.

No existing Galaxy datasets were deleted.
