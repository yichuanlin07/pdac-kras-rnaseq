# PDAC KRAS RNA-seq

RNA-seq analysis of control and KRAS siRNA samples from eight pancreatic cancer cell lines in [PRJNA980201](https://www.ebi.ac.uk/ena/browser/view/PRJNA980201).

[Week 6 pathway analysis](analysis/2026-10-30-week6/README.md) tests Hallmark and Reactome gene sets with CAMERA and over-representation analysis, including eleven paired models. The [English progress report](reports/Week6_2026-10-30/PDAC_KRAS_Week6_2026-10-30.pdf) presents the cell-cycle enrichment and primary CAMERA results.

[October 11 follow-up](analysis/2026-10-11-post-meeting/README.md) audits the FDR/effect-size screen and completes eight paired cell-line omission fits, with [English Methods](analysis/2026-10-11-post-meeting/Methods_en.md), [Chinese results](analysis/2026-10-11-post-meeting/Results_zh.md) and a [discussion report](reports/PDAC_KRAS_PostMeeting_2026-10-11.pdf).

[Week 4](analysis/2026-10-04-week4/README.md) compares DESeq2 and edgeR, checks the effect of P5 library handling and compares the results with Klomp et al. The main analysis combines the two P5 KRAS libraries. Their repeat type is not documented, so the analysis is exploratory.

[Source code](analysis/2026-10-04-week4/scripts/) · [Results](analysis/2026-10-04-week4/results/) · [Figures](analysis/2026-10-04-week4/figures/) · [Report PDF](reports/PDAC_KRAS_Week4_2026-10-06.pdf) · [Report DOCX](reports/PDAC_KRAS_Week4_2026-10-06.docx)

[Count preparation](analysis/2026-10-01/README.md) includes the corrected M1 inputs. [Quality checks](analysis/2026-09-22/README.md) and [Galaxy backups](galaxy_backup/README.md) record the read and alignment checks.
