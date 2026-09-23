# FastQC results for SRR24828471

FastQC 0.12.1 checked the complete local KRAS P5 (`SRR24828471`) files on 22 September 2026. The two text reports are saved here.

## Results

R1 and R2 each contain 37,886,040 reads, all 150 bases long, with 51% GC content. Their FastQC results are the same:

| Check | R1 and R2 |
| --- | --- |
| Base composition | Fail |
| Sequence duplication | Fail |
| GC distribution | Warn |
| All other reported modules | Pass |

The R2 MD5 matches the European Nucleotide Archive (ENA) reference. R1 uses different header formatting; its sequences and quality scores match the complete ENA R1 in order. The ENA copy also matches its reference MD5. See [recovery_checks.json](../recovery_checks.json).

These reports were uploaded to Galaxy as datasets 162/163. MultiQC 165 combines them with 32 Galaxy reports to cover all 34 input files. The separate Galaxy R2 report 153 checks the same mate and was excluded to avoid counting it twice.

## Command

FastQC 0.12.1 came from the [Babraham download page](https://www.bioinformatics.babraham.ac.uk/projects/download.html). The command below uses the paths from the original local run, with two files processed at once and 1,024 MB of memory per file.

```bash
perl work/fastqc_0.12.1/FastQC/fastqc --threads 2 --memory 1024 \
  --outdir work/local_recovery_qc \
  /home/ylin/Downloads/Neo/KRAS_siRNA_P5_1.fastq.gz \
  /home/ylin/Downloads/Neo/KRAS_siRNA_P5_2.fastq.gz
```

The run used default adapter, contaminant and limit settings, with no trimming. The raw reads and downloaded tool are stored outside this repository.

## File checksums

Use these SHA-256 checksums to identify the downloaded archive and saved reports:

```text
FastQC archive  5f4dba8780231a25a6b8e11ab2c238601920c9704caa5458d9de559575d58aa7
R1 report       588252df5c659d64548e29edd7366334f350f29ece191394b6c7fc9104e0e225
R2 report       76360671b93b6d150303425a39bebdd6a1f64b1938f3e5a0d5f76b03221cad45
```
