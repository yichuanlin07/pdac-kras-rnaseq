# FastQC results for SRR24828471

This folder contains the FastQC reports for the complete local R1 and R2 files of KRAS P5 (`SRR24828471`), checked on 22 September 2026.

## Results

Both files contain 37,886,040 reads of 150 bases, with 51% GC content. FastQC reports:

| Check | R1 and R2 |
| --- | --- |
| Base composition | Fail |
| Sequence duplication | Fail |
| GC distribution | Warn |
| All other reported modules | Pass |

The R2 file matches the European Nucleotide Archive (ENA) MD5 checksum. The local R1 has different file formatting, but every sequence and quality line matches the complete ENA R1. The ENA copy's MD5 was also checked. Details are in [recovery_checks.json](../recovery_checks.json).

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

SHA-256 checksums identify the tool archive and the two saved reports:

```text
FastQC archive  5f4dba8780231a25a6b8e11ab2c238601920c9704caa5458d9de559575d58aa7
R1 report       588252df5c659d64548e29edd7366334f350f29ece191394b6c7fc9104e0e225
R2 report       76360671b93b6d150303425a39bebdd6a1f64b1938f3e5a0d5f76b03221cad45
```
