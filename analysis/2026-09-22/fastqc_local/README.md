# Local recovery quality checks

These two raw FastQC reports were computed from complete user-supplied SRR24828471 R1/R2 files on 22 September 2026. They were uploaded to Galaxy as **162 and 163** and combined with 32 existing Galaxy reports in **MultiQC 165**. They are not outputs of a Galaxy FastQC job. The separately restored Galaxy R2 report 153 is an independent check of the same mate and is excluded from the 34-file aggregate to avoid double counting.

FastQC 0.12.1 was downloaded from the [official Babraham download page](https://www.bioinformatics.babraham.ac.uk/projects/download.html). The archive SHA-256 is `5f4dba8780231a25a6b8e11ab2c238601920c9704caa5458d9de559575d58aa7`.

The executed command used the downloaded launcher, two concurrent files and 1,024 MB memory per file:

```bash
perl work/fastqc_0.12.1/FastQC/fastqc --threads 2 --memory 1024 \
  --outdir work/local_recovery_qc \
  /home/ylin/Downloads/Neo/KRAS_siRNA_P5_1.fastq.gz \
  /home/ylin/Downloads/Neo/KRAS_siRNA_P5_2.fastq.gz
```

No custom adapters, contaminants, limits or trimming were supplied. Both reports contain 37,886,040 reads, length 150 bp and 51% GC. Both have composition/duplication Fail and GC-distribution Warn; all other reported modules Pass. The local R2 matches the ENA compressed MD5. All local R1 sequence and quality lines match the complete canonical ENA R1, whose compressed MD5 was also verified. See `../recovery_checks.json` for the validation boundaries.

Report SHA-256:

- R1: `588252df5c659d64548e29edd7366334f350f29ece191394b6c7fc9104e0e225`
- R2: `76360671b93b6d150303425a39bebdd6a1f64b1938f3e5a0d5f76b03221cad45`

Only these small result files are committed. The raw FASTQ files, downloaded tool and large alignment files remain outside Git.
