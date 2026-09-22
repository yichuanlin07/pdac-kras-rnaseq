# Full HISAT2 alignment review

Evidence cutoff: 22 September 2026. All 17 full-run summaries are present, with 727,731,715 input pairs and overall read alignment of 95.79%–97.72%. Completion does not mean every alignment is suitable for downstream analysis.

## Sources

- Fourteen files in `raw/` are byte-for-byte copies of the user's downloaded `HISAT2 on collection 253: Mapping summary` directory. Input collection 253 produced summary collection 255. Filenames identify its elements; `results.json` records SHA-256 hashes.
- `Control_siRNA_M1.txt` transcribes summary 195, checked against live Galaxy job details on 22 September. Inputs 13/15; BAM 194.
- `KRAS_siRNA_P1.txt` transcribes the complete user-supplied summary, previously checked against Galaxy summary 193. Inputs 7/8; BAM 192.
- `KRAS_siRNA_P5.txt` transcribes the complete user-supplied summary for input collection 156, previously checked against summary collection 285. Recovered mates 175/176 identify SRR24828471, not SRR24828472.
- Accession mappings follow `../run_manifest.md`. Labels do not prove correct read-by-read pairing. Control P1 in the batch uses replacement inputs 251/252 rather than original 21/22; direction was checked, byte identity was not.
- Historical pilot datasets 121–136 are excluded. Older reports remain historical snapshots.

Recreate `results.json` from the repository root:

```sh
python3 analysis/2026-09-22/full_alignment/validate_full_alignment.py
```

The parser verifies category sums, the two-mates relationship and all reported percentages. It does not validate BAM contents, read-header correspondence or biological suitability.

## Parameters and strand inference

HISAT2 2.2.3+galaxy0; built-in hg38; paired-end; unstranded; Phred+33; skip 0; align-first-N 0 (unlimited in this wrapper); trim both ends 0; machine-friendly summary and summary-file enabled; other settings default. KRAS M1's live details confirm state `ok`, exit code 0, no `-u`/`--upto` restriction and default paired-end settings. Different compression of its two inputs does not itself establish a pairing defect.

RSeQC Infer Experiment used hg38 BED12 annotation, 200,000 sampled reads and MAPQ 30. User-supplied results:

| Pilot BAM | Undetermined | 1++,1--,2+-,2-+ | 1+-,1-+,2++,2-- |
| --- | ---: | ---: | ---: |
| Control M1 | 0.0637 | 0.4690 | 0.4673 |
| KRAS P1 | 0.0851 | 0.4580 | 0.4569 |

Near-equal orientation fractions support unstranded libraries for these two inputs. Other runs used the same setting without individual confirmation. RNA strand specificity and mate geometry are different settings.

## KRAS M1 remains flagged

Summary 269 (batch element 7) contains 45,292,678 pairs: 1,371 concordantly unique (0.0030%, displayed as 0.00%), 85,829 concordant multi-mapping (0.19%), and 34,222,895 discordant (75.56%). Overall individual-read alignment is 96.51%.

The other 16 runs have 85.19%–88.32% concordant unique-pair alignment and 0.32%–1.15% discordant pairs. KRAS M1 is an outlier; its cause remains unresolved. Check mate identities/accessions, read-header order, accidental same-end inputs and pair geometry before quantification. Do not diagnose a specific cause from aggregate numbers alone. Retain current data and hold this run from downstream counting until resolved. This report task did not rerun or delete Galaxy jobs or inputs.

Overall alignment includes discordant pairs and separately aligned mates; it is not the fraction of properly paired reads. See the [HISAT2 manual](https://daehwankimlab.github.io/hisat2/manual/).

No gene-count matrix, differential-expression result or treatment effect is reported. Compare treatments within cell line. Keep both MiaPaca-2 KRAS accessions distinct until their repeat type is resolved. Raw-read QC remains documented in `../fastqc_review.json` and `../multiqc_summary.json`.
