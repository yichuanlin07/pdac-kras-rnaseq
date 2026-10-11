# KRAS follow-up: screening and eight cell-line omissions

Base commit: `e831fe0b0a642daa643ed5902d996b41cc7a6899`. Work is isolated on local branch `analysis/2026-10-11-post-meeting`. Earlier analyses are retained. No remote push was performed.

## Read first

- [Discussion report](../../reports/PDAC_KRAS_PostMeeting_2026-10-11.pdf): six visually checked pages, four new figures and the Methods draft.
- [中文结果重点](Results_zh.md): screening definitions, P5 mapping, eight rounds, candidates and limits.
- [English Methods draft](Methods_en.md): count-level methods actually executed.

The full-fit screen is adjusted P < 0.05 and absolute primary log2FC > 0.5. It selects 2,088 DESeq2 genes, 2,919 edgeR genes and a 2,020-gene intersection from 17,819 retained genes. DESeq2 uses its model effect before apeglm shrinkage; edgeR uses the reported logFC with default prior.count 0.125. Applying the cutoff to DESeq2 apeglm effects instead gives 1,702 genes and a 1,690-gene intersection. The cutoff is applied after testing the zero-effect null.

Each of eight omission fits removes one cell line's Control/Treatment pair. Refiltering and model fitting are repeated on 14 observations. All reduced designs have rank eight and six residual degrees of freedom. The full design has rank nine and seven residual degrees of freedom. A total of 2,017/2,020 reference genes have finite same-direction effects in every round in both methods. The other three are unavailable after low-count filtering in one round; available reference estimates do not reverse direction.

The descriptive joint >=7/8 list has **1,515 genes** and the 8/8 list has **1,291**. Both methods must pass in the **same** round. Full-fit joint selection, eight finite effects and direction agreement are also required. Separate >=7/8 passes per method yield 1,517 genes and are stored as a different flag. These sensitivity lists do not carry a new FDR guarantee or patient-outcome validation.

## Files and definitions

| File | Contents |
| --- | --- |
| `results/full/`, `results/omit_*/` | All 28,395 genes with filter/test status, model design, samples, normalization and method metadata |
| `results/round_summary.tsv`, `round_coverage.tsv` | Screen counts and explicit paired omissions, source runs, ranks and residual df |
| `results/screening_audit.tsv` | Full-universe thresholds and direction counts for DESeq2 model/apeglm and edgeR effects |
| `results/DESeq2_gene_stability.tsv`, `edgeR_gene_stability.tsv` | Each gene's full effects, availability, direction, thresholds, ranges and maximum changes |
| `results/joint_gene_stability.tsv` | Both methods, simultaneous joint pass counts and descriptive flags for all input genes |
| `results/full_joint_2020_stability.tsv` | Fixed full-fit intersection as the reference list |
| `results/descriptive_joint_ge7of8.tsv`, `descriptive_joint_all8.tsv` | The 1,515- and 1,291-gene discussion lists |
| `results/full_joint_effect_drift_ge05.tsv`, `full_joint_missing_rounds.tsv` | 52 genes flagged by amplitude change and three genes lacking one round's estimates |
| `results/effect_stability_by_round.tsv` | Correlations, direction, median/95th-percentile change by reference scope; `method_screen_Jaccard` always compares the full method screen with that omission's full method screen |
| `results/loo_long.tsv` | One gene/method/omission per row, including unavailable values; suitable for custom plots |
| `results/candidate_stability.tsv`, `candidate_loo_long.tsv` | Eleven historical candidates, both methods, all eight omissions |
| `results/p5_choices_screening_audit.tsv` | New threshold summaries of archived single-library fits; these models were not refitted |
| `sources/sample_ena_mapping.tsv`, `p5_ena_mapping.tsv` | All 17 run/sample/alias mappings and the P5 subset from the archived 2026-10-04 ENA snapshot |
| `sources/input_and_model_validation.json`, `repeat_run_validation.json` | Input, model, baseline and repeat-run checks |
| `sources/effect_definitions.json`, `edgeR_installed_effect_source.txt` | Effect definitions and the relevant installed edgeR source functions |
| `figures/` | Four new plots as PNG and vector PDF; candidate ranges are point-estimate ranges, not confidence intervals |

`screen_pass_rounds` combines FDR and effect cutoff; `FDR05_rounds` and `absLFC_gt05_rounds` are separate. `same_direction_rounds` counts finite nonzero effects agreeing with the full fit. `finite_effect_rounds` and `finite_adjusted_p_rounds` distinguish missing effects from filtered adjusted P values. Ranges/means use available estimates; descriptive lists require eight finite effects. No adjusted P values are averaged or pooled. Missing symbols do not change Entrez-based matching.

P5 raw integer counts are summed before filtering and normalization. Local P5 is SRR24828471 / MP2_K2v2 / SAMN35622210; local P5_v2 is SRR24828472 / MP2_K2 / SAMN35622209. The repeat identity and shared biological material remain unresolved. Distinct public records and FASTQ MD5 values cannot settle those questions.

## Reproduce

Use R 4.5.2 with the existing [Week 4 renv lock](../2026-10-04-week4/renv.lock): DESeq2 1.50.2, edgeR 4.8.2, apeglm 1.32.0. Install the Python versions listed in `requirements.txt`. Set `R_LIBS_USER` to an already restored library, and run from the repository root:

```bash
export TZ=Etc/UTC
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
Rscript analysis/2026-10-11-post-meeting/scripts/analyze_loo.R "$PWD" /absolute/path/new-results
Rscript analysis/2026-10-11-post-meeting/scripts/analyze_loo.R "$PWD" /absolute/path/repeat-results
```

The R script refuses to overwrite output. To reproduce the shipped summaries, place the first completed results in a fresh analysis copy at `analysis/2026-10-11-post-meeting/results`, then run:

```bash
python3 analysis/2026-10-11-post-meeting/scripts/summarize.py "$PWD"
python3 analysis/2026-10-11-post-meeting/scripts/audit_sources.py "$PWD"
python3 analysis/2026-10-11-post-meeting/scripts/verify_repeat.py analysis/2026-10-11-post-meeting/results /absolute/path/repeat-results
python3 analysis/2026-10-11-post-meeting/scripts/figures.py analysis/2026-10-11-post-meeting
python3 analysis/2026-10-11-post-meeting/scripts/report.py analysis/2026-10-11-post-meeting /absolute/path/discussion-report.pdf
```

The shipped full fit matches Week 4 effect estimates and raw/adjusted P values. Two complete nine-fit runs gave 68 byte-identical TSV and method-JSON files. Session text is excluded. Input count columns match all 17 source tables. Report layout and all figure labels were inspected after rendering all six pages.

Pathway enrichment and patient-outcome validation remain future work. The existing Week 4 paired-expression appendix was not regenerated. The English draft starts from corrected counts and does not claim new read processing or experiments.
