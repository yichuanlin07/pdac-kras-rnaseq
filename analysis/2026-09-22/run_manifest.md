# Samples and sequencing runs

This list links the project's sample names to public sequencing records and Galaxy inputs. The European Nucleotide Archive (ENA) records were checked on 22 September 2026. Each run contains two paired files, R1 and R2.

## Run accessions

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
| KRAS P5 | SRR24828471 | MP2_K2v2 | 175 (collection 156) | 176 (collection 156) |
| KRAS P5_v2 | SRR24828472 | MP2_K2 | 129 | 130 |

Galaxy numbers identify datasets in the original history. The table retains the original input numbers where listed. Full alignment of Control P1 used replacement inputs 251/252; the read direction was checked, but file identity was not.

KRAS P5 uses the recovered pair **175/176 in collection 156**. Earlier R1 imports 127 and 150 were incomplete and are labelled `DO_NOT_USE_TRUNCATED`; R2 import 128 failed. R2 replacement 151 passed FastQC, but the final analysis uses the two files recovered together. KRAS P5_v2 inputs 129/130 also completed FastQC with matching read counts.

## Cell lines and comparisons

In the public sample names, `SC` means scramble siRNA control and `K2` means KRAS siRNA treatment.

| Local number | Cell line | ENA source classification | Control BioSample | KRAS BioSample |
| --- | --- | --- | --- | --- |
| M1 | Pa01C | Metastatic | SAMN35622213 | SAMN35622212 |
| M2 | Pa02C | Metastatic | SAMN35622215 | SAMN35622214 |
| M3 | Pa04C | Metastatic | SAMN35622217 | SAMN35622216 |
| P1 | Pa16C | Primary | SAMN35622221 | SAMN35622220 |
| P2 | PANC-1 | Primary | SAMN35622223 | SAMN35622222 |
| P3 | Pa14C | Primary | SAMN35622219 | SAMN35622218 |
| P4 | HPAC | Primary | SAMN35622208 | SAMN35622207 |
| P5 | MiaPaca-2 | Primary | SAMN35622211 | SAMN35622210 and SAMN35622209 |

Compare treatments within each cell line. The M and P groups come from different cell lines, rather than matched primary and metastatic samples from the same patients. Control M1 and KRAS P1, used for the pilots, are also different cell lines.

The [paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC11301402/) uses eight cell lines as biological replicates for each treatment in Figure 1. The expression analysis should account for both cell line and treatment. The extra MiaPaca-2 run needs to be resolved before choosing the final inputs.

### The two MiaPaca-2 KRAS runs

| Local name | Run | Experiment | BioSample | Public alias | Repeat field |
| --- | --- | --- | --- | --- | --- |
| KRAS P5 | SRR24828471 | SRX20593397 | [SAMN35622210](https://www.ebi.ac.uk/ena/browser/api/xml/SAMN35622210) | MP2_K2v2 | replicate=TRUE |
| KRAS P5_v2 | SRR24828472 | SRX20593396 | [SAMN35622209](https://www.ebi.ac.uk/ena/browser/api/xml/SAMN35622209) | MP2_K2 | replicate=FALSE |

The local `v2` label is attached to the opposite run from the public `v2` alias. Use the run accession to identify the files.

The repeat field does not say whether the second run is a biological repeat, technical repeat or replacement experiment. Both remain separate for now. The library records list TruSeq, oligo-dT selection and paired-end sequencing, but do not establish strand specificity.

## File checksums

These sizes and MD5 checksums come from ENA. They are reference values for the exported FASTQ files; Galaxy copies have not all been checked against them.

| Filename | Expected bytes | ENA MD5 |
| --- | --- | --- |
| SRR24828471_1.fastq.gz | 2582199279 | 80a6ee296d0fffe29a6b335e79546778 |
| SRR24828471_2.fastq.gz | 2603110042 | f56e4529719292d8c8bd01af9b24b6b8 |
| SRR24828472_1.fastq.gz | 2930283917 | 1aaf3ff07a635d3cdf82754272c73233 |
| SRR24828472_2.fastq.gz | 3001011805 | 34cdbf3cd3a08a5fcb738b22f963dba7 |

The local SRR24828471 R2 matches the ENA size and MD5. The local R1 has 37,886,040 complete records of 150 bases and passes gzip checks. All R1/R2 read identifiers match in order.

The local R1 has a different compressed MD5 because its headers and plus lines use a different format. A complete ENA R1 was downloaded and matched to the reference MD5. Every sequence and quality line in it matches the local R1 in order.

SRA Toolkit later recovered both mates into Galaxy collection 156. Log 159 records 37,886,040 paired spots. FastQC reports 181/183 confirm the read count, length and quality flags for both mates. Keep 175/176 together because their read identifiers use a different format from the ENA export.

Full checks are in [recovery_checks.json](recovery_checks.json). Public records are available from the [ENA study page](https://www.ebi.ac.uk/ena/browser/view/PRJNA980201).
