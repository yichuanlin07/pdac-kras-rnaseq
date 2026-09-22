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
| KRAS P5 | SRR24828471 | MP2_K2v2 | 175 (collection 156) | 176 (collection 156) |
| KRAS P5_v2 | SRR24828472 | MP2_K2 | 129 | 130 |

Galaxy numbers apply only to the originating history. Inputs 129 and 130 completed FastQC with matching mate counts. Original input 127 and retry 150 are truncated and marked `DO_NOT_USE_TRUNCATED`; input 128 failed import. Separate R2 replacement 151 passed FastQC. The preferred matched SRR24828471 pair is now **175/176 in collection 156**, recovered together with SRA Toolkit. Retain old inputs for provenance, but exclude bad or redundant copies from analysis. Local label mappings come from the local inventory; ENA aliases alone do not establish byte identity.

## Cell lines and comparisons

ENA BioSample records were checked on 22 September 2026. `SC` denotes scramble siRNA control and `K2` denotes KRAS siRNA. R1 and R2 are mates, not replicates.

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

Compare control and KRAS treatment within each cell line. The M and P groups are different cell lines, not matched primary/metastatic samples from the same patients. Cell-line differences can confound a simple M-versus-P comparison. The two pilot inputs, Control M1 and KRAS P1, are also different cell lines and cannot isolate a treatment effect.

The [source paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC11301402/) describes eight cell lines as the biological replicates for each treatment in Figure 1. A downstream model should account for cell line as well as treatment. Resolve the extra MiaPaca-2 run before deciding which columns enter that model.

### The two MiaPaca-2 KRAS runs

- Local **KRAS P5**: SRR24828471, SRX20593397, [SAMN35622210](https://www.ebi.ac.uk/ena/browser/api/xml/SAMN35622210), alias `MP2_K2v2`, metadata `replicate=TRUE`.
- Local **KRAS P5_v2**: SRR24828472, SRX20593396, [SAMN35622209](https://www.ebi.ac.uk/ena/browser/api/xml/SAMN35622209), alias `MP2_K2`, metadata `replicate=FALSE`.

These are distinct public run, experiment and BioSample records. The local `v2` suffix is opposite to the public alias, so use accession numbers to avoid a swap. `replicate=TRUE` does not specify whether the repeat is biological, technical or a replacement experiment. Do not automatically merge, discard or count it as a ninth independent cell-line replicate. The library records state TruSeq, oligo-dT selection and paired-end sequencing, but do not settle strand specificity.

ENA sample XML can be inspected using `https://www.ebi.ac.uk/ena/browser/api/xml/` followed by the BioSample accession. Public run metadata are available from the [ENA study record](https://www.ebi.ac.uk/ena/browser/view/PRJNA980201).

## Expected checksums for newly imported files

These are ENA reference values, not completed Galaxy checksum validations.

| Filename | Expected bytes | ENA MD5 |
| --- | --- | --- |
| SRR24828471_1.fastq.gz | 2582199279 | 80a6ee296d0fffe29a6b335e79546778 |
| SRR24828471_2.fastq.gz | 2603110042 | f56e4529719292d8c8bd01af9b24b6b8 |
| SRR24828472_1.fastq.gz | 2930283917 | 1aaf3ff07a635d3cdf82754272c73233 |
| SRR24828472_2.fastq.gz | 3001011805 | 34cdbf3cd3a08a5fcb738b22f963dba7 |

Local recovery check: `KRAS_siRNA_P5_2.fastq.gz` has 2,603,110,042 bytes and MD5 `f56e4529719292d8c8bd01af9b24b6b8`, matching ENA. The local R1 is gzip-valid and contains 37,886,040 complete 150-base records with SRR24828471 headers. Its compressed MD5 differs from ENA. A streaming comparison of every read-header first token in local R1 and R2 returned an exact match (37,886,040 records in the same order); this confirms pair identifiers, not equality of R1 and R2 sequences. The local R1 uses longer SRA-style headers and repeated plus-line identifiers. A complete canonical ENA R1 was subsequently downloaded: its compressed MD5 matches the reference, and **all sequence and quality lines match the local R1 in order**. The compressed-file difference is representational, not a difference in the recovered read sequences or qualities.

Repair inputs 150/151 use the ENA URLs above. Input 150 again proved truncated (738 MB versus the expected approximately 2.58 GB), with an ignored `Bad file descriptor` error in the import log. The independent SRA Toolkit recovery succeeded: paired collection 156 contains 175 (forward) and 176 (reverse); log 159 reports 37,886,040 paired spots. FastQC 181/183 independently confirmed the full count, 150 bp, 51% GC and matching module flags for both reconstructed mates. The final 34-file MultiQC uses the verified local pair's reports 162/163, not failed, empty or duplicate validation outputs. Keep both reconstructed SRA mates together because their identifier format differs from the ENA export.
