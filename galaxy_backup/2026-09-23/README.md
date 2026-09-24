# Galaxy cleanup — 23 September 2026

History: **Datasets**, on [Main Galaxy](https://galaxy-main.usegalaxy.org/histories/view?id=bbd44e69cb8906b5123b15e2f796dd1c).

Cleanup is in progress. Files are removed only after their backups have been checked. Ordinary deletion can be reversed in Galaxy; permanent deletion has not been performed.

## File lists

- [Removed in this cleanup](00_manifests/deleted_this_cleanup.tsv)
- [Retained in Galaxy](00_manifests/retained.tsv)
- [Already deleted before this cleanup](00_manifests/previously_deleted.tsv)
- [Items still waiting for cleanup](00_manifests/pending.tsv)
- [All dataset records](00_manifests/all_datasets.tsv)
- [Checksums](00_manifests/SHA256SUMS.txt)

A Galaxy file can appear more than once in a history. The lists include both the history entry ID and the underlying physical dataset ID, so repeated entries are not counted as separate files when reporting storage.

## Where the backups are

| Folder | Contents |
| --- | --- |
| `00_manifests` | File lists, checksums and cleanup records |
| `01_raw` | FASTQ backups; local storage only |
| `02_fastqc` | Individual FastQC reports and early quality checks |
| `03_multiqc` | MultiQC reports, statistics and plots |
| `04_pilot_alignments` | Early test alignments and summaries; BAM files are local only |
| `05_retained_results` | Copies of alignment summaries, reference annotation and strand checks |
| `06_logs_and_other` | Recovery logs and other small outputs |

Full backups are under `/home/ylin/Documents/TRNTLabArchives/galaxy_backup/2026-09-23/`. Each inventory row gives the exact path. The raw data folder also contains separately checked local source files in `local_candidates`; those are identified as Galaxy backups only when their size and server checksum match.

Downloads were checked against Galaxy's byte count. When Galaxy supplied a SHA-256 checksum, it was checked too. The inventory states which checks were possible. A failed or paused job with zero output bytes has a metadata record, not a fabricated output file. Some entries deleted before this work could not be downloaded; their failures are listed separately.

## Retained Galaxy groups

Galaxy uses dataset collections for these groups:

| Group | Contents |
| --- | --- |
| `01_Aligned_BAM_17_runs` | All 17 full alignment BAM files |
| `02_Alignment_Summaries_17_runs` | Their 17 HISAT2 summaries |
| `03_Reference_and_Strand_Checks` | hg38 RefSeq annotation and two strand checks |
| `04_KRAS_M1_Raw_Pair_REVIEW` | Both original KRAS M1 read files |
| `05_QC_Reports_and_Recovery` | Final MultiQC report, statistics and recovery log |
| `06_QC_Plots` | Eight MultiQC plot tables |

The original result entries and input collections are hidden to keep the main view readable. Their links remain available through **Include hidden**. New collections reference the same physical datasets.

KRAS M1 needs further work: its summary reports only 1,371 concordant unique pairs out of 45,292,678 pairs. Its raw pair and BAM remain in Galaxy. The two KRAS P5 runs also remain separate. The [alignment report](../../analysis/2026-09-22/full_alignment/README.md) explains these limits.

## Restore a file

For an ordinary deleted entry, enable **Include deleted** in Galaxy and use **Undelete**. To restore a file from the local backup, find its path in the inventory, check its SHA-256 checksum, and upload it to Galaxy. Keep both mates of a paired read set together.

The full-history TGZ export was requested separately and was still being prepared during cleanup. It is not counted as a completed backup here.
