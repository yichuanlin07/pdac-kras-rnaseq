# Sequencing run manifest

Local labels are retained as supplied. Public aliases were checked through the [ENA study record](https://www.ebi.ac.uk/ena/browser/view/PRJNA980201) on 22 September 2026. All listed runs are paired-end RNA sequencing. R1 and R2 are two files from one run, not independent samples.

| Local label | Run accession | ENA sample alias | Galaxy R1 | Galaxy R2 |
| --- | --- | --- | --- | --- |
| Control M1 | SRR24828468 | Pa01_SC | 13 | 15 |
| Control M2 | SRR24828466 | Pa02_SC | 16 | 17 |
| Control M3 | SRR24828479 | Pa04_SC | 18 | 19 |
| Control P1 | SRR24828475 | Pa16_SC | 21 | 22 |
| Control P2 | SRR24828473 | Panc1_SC | 31 | 33 |
| Control P3 | SRR24828477 | Pa14_SC | 46 | 89 |
| Control P4 | SRR24828480 | HPAC_SC | 91 | 92 |
| Control P5 | SRR24828470 | MP2_SC | 90 | 93 |
| KRAS M1 | SRR24828469 | Pa01_K2 | 1 | 12 |
| KRAS M2 | SRR24828467 | Pa02_K2 | 11 | 10 |
| KRAS M3 | SRR24828465 | Pa04_K2 | 4 | 5 |
| KRAS P1 | SRR24828476 | Pa16_K2 | 7 | 8 |
| KRAS P2 | SRR24828474 | Panc1_K2 | 9 | 6 |
| KRAS P3 | SRR24828478 | Pa14_K2 | 106 | 110 |
| KRAS P4 | SRR24828481 | HPAC_K2 | 111 | 112 |
| KRAS P5 | SRR24828471 | MP2_K2v2 | 127 | 128 |
| KRAS P5_v2 | SRR24828472 | MP2_K2 | 129 | 130 |

Galaxy numbers apply only to the originating history. Inputs 127–130 were submitted for ENA import and are not confirmed complete. Local label mappings come from the local inventory; ENA aliases do not establish that an uploaded file is byte-identical. Do not treat the two MP2 KRAS runs as independent biological replicates without checking the experimental design.

## Expected checksums for newly imported files

These are ENA reference values, not completed Galaxy checksum validations.

| Filename | Expected bytes | ENA MD5 |
| --- | --- | --- |
| SRR24828471_1.fastq.gz | 2582199279 | 80a6ee296d0fffe29a6b335e79546778 |
| SRR24828471_2.fastq.gz | 2603110042 | f56e4529719292d8c8bd01af9b24b6b8 |
| SRR24828472_1.fastq.gz | 2930283917 | 1aaf3ff07a635d3cdf82754272c73233 |
| SRR24828472_2.fastq.gz | 3001011805 | 34cdbf3cd3a08a5fcb738b22f963dba7 |
