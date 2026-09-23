# Full HISAT2 alignment results

HISAT2 processed 727,731,715 read pairs from 17 sequencing runs against human hg38. This page summarizes the full-run results recorded on **22 September 2026**.

KRAS M1 stands out from the other runs: most reads align, but very few form the expected pairs. Its cause needs to be checked before this run is used for gene counting.

## Results

The percentages describe different parts of the alignment:

- **Overall alignment:** the percentage of individual reads that align, including reads aligned separately from their mate.
- **Concordant unique pairs:** the percentage of input pairs that align to one location with the expected orientation and spacing.
- **Discordant pairs:** the percentage of input pairs whose mates align uniquely but do not meet those pairing requirements.

| Run | Input pairs | Overall alignment | Concordant unique pairs | Discordant pairs |
| --- | ---: | ---: | ---: | ---: |
| Control M1 | 40,237,116 | 96.75% | 86.11% | 0.61% |
| Control M2 | 45,764,716 | 96.78% | 85.19% | 0.58% |
| Control M3 | 38,181,985 | 96.67% | 87.14% | 0.64% |
| Control P1 | 45,946,458 | 96.73% | 87.25% | 0.57% |
| Control P2 | 39,989,452 | 95.79% | 86.47% | 1.15% |
| Control P3 | 47,840,900 | 96.41% | 87.03% | 0.54% |
| Control P4 | 46,287,075 | 96.20% | 87.22% | 0.65% |
| Control P5 | 45,023,981 | 96.75% | 88.32% | 0.57% |
| **KRAS M1** | 45,292,678 | 96.51% | 0.0030% | 75.56% |
| KRAS M2 | 44,032,049 | 96.74% | 85.25% | 0.62% |
| KRAS M3 | 42,961,283 | 96.64% | 86.95% | 0.60% |
| KRAS P1 | 39,963,282 | 96.52% | 87.11% | 0.62% |
| KRAS P2 | 42,632,214 | 96.49% | 87.50% | 0.69% |
| KRAS P3 | 42,073,244 | 96.57% | 86.11% | 0.56% |
| KRAS P4 | 40,452,536 | 96.77% | 88.32% | 0.52% |
| KRAS P5 | 37,886,040 | 96.53% | 87.55% | 0.64% |
| KRAS P5_v2 | 43,166,706 | 97.72% | 88.09% | 0.32% |

KRAS M1 has only 1,371 concordant unique pairs out of 45,292,678 input pairs. Another 85,829 pairs align concordantly to multiple locations, while 34,222,895 pairs align discordantly. Its 96.51% overall alignment rate therefore does not show that pairing is correct.

The next checks are the R1/R2 identities, read order and paired-end settings. The Galaxy job completed with no read limit and default paired-end settings. The available summaries do not identify a cause; the difference in input compression is not enough to diagnose one.

Gene counts and differential expression results are not yet available. Treatment comparisons should use control and KRAS runs from the same cell line. The two MiaPaca-2 KRAS runs remain separate until their repeat type is clear; see the [sample and run list](../run_manifest.md).

## Parameters and strand inference

| Setting | Value |
| --- | --- |
| Galaxy HISAT2 version | 2.2.3+galaxy0 |
| Reference | Built-in human hg38 |
| Reads | Paired-end, Phred+33 quality scores |
| Strand setting | Unstranded |
| Read limit | None: skip 0, align-first-N 0 |
| End trimming | 0 bases from either end |
| Output | Machine-friendly summary and summary file enabled |
| Other settings | Defaults |

RSeQC Infer Experiment was used to check strand specificity on two pilot alignments. It sampled 200,000 reads with a minimum mapping quality of 30 and an hg38 BED12 annotation. The supplied results were:

| Pilot alignment | Undetermined | 1++,1--,2+-,2-+ | 1+-,1-+,2++,2-- |
| --- | ---: | ---: | ---: |
| Control M1 | 0.0637 | 0.4690 | 0.4673 |
| KRAS P1 | 0.0851 | 0.4580 | 0.4569 |

Both inputs have similar fractions in the two orientation groups, which supports unstranded alignment. The same setting was used for the other runs, although they were not tested individually. This strand check concerns transcript direction, rather than the orientation and spacing of paired reads.

## Files and sources

| File | Contents |
| --- | --- |
| [raw/](raw/) | 17 HISAT2 text summaries |
| [results.json](results.json) | Counts, calculated percentages, run accessions and source-file SHA-256 checksums |
| [validate_full_alignment.py](validate_full_alignment.py) | Script that checks the summaries and rebuilds `results.json` |

Fourteen text files were copied unchanged from the downloaded Galaxy mapping-summary collection 255, produced from input collection 253. The other three were transcribed from individual summaries:

| Run | Summary | Inputs | Source check |
| --- | --- | --- | --- |
| Control M1 | 195 | 13/15 | Checked against Galaxy job details on 22 September; alignment file 194 |
| KRAS P1 | 193 | 7/8 | Complete supplied summary, previously checked against Galaxy; alignment file 192 |
| KRAS P5 | Collection 285 | Collection 156, mates 175/176 | Complete supplied summary, previously checked against Galaxy; recovered run SRR24828471 |

Control P1 used replacement inputs 251/252 instead of 21/22. Their read direction was checked, but file identity was not. Run labels follow the [sample list](../run_manifest.md); labels alone cannot confirm that reads are paired in the correct order. Galaxy numbers refer to the original history.

Pilot datasets 121–136 are excluded from these full-run results. Earlier reports remain snapshots of previous work. Raw-read quality checks are in [fastqc_review.json](../fastqc_review.json) and [multiqc_summary.json](../multiqc_summary.json).

## Check the summaries

From the repository root, run:

```sh
python3 analysis/2026-09-22/full_alignment/validate_full_alignment.py
```

The script checks that counts add up, each unaligned pair accounts for two separately considered reads, and reported percentages agree with the counts. It then replaces `results.json` with the calculated results.

The script checks summary arithmetic only. Resolving KRAS M1 requires examining the reads and alignment files.
