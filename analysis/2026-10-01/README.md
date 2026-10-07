# Corrected counts and figures

This folder contains all 17 runs, with KRAS M1 corrected to 37,657,740 assigned counts (68.94%); the other 16 columns are unchanged and both P5 KRAS runs remain separate.
Run `Rscript counts/prepare_data.R` here to rebuild the raw count tables, then install `requirements.txt` and run `python3 build_figures.py` to recreate the [four figures](plots/PDAC_featureCounts_M1_corrected.pdf).
Correlation and PCA use log2(CPM + 1), with the 500 highest-variance genes used for PCA; the exported count tables remain unnormalized integers.
Source code, count tables and checks are in [counts](counts/); figures are in [plots](plots/).
