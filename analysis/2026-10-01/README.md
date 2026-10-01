# M1 corrected counts and figures

All 17 runs are included. KRAS M1 was rebuilt from the verified ENA pair SRR24828469. The other 16 count columns are unchanged.

- `counts/prepare_data.R`: R source for joining counts, matching gene annotation and exporting tables. Uses base R.
- `counts/counts_raw.txt`: raw integer counts for 28,395 genes and 17 runs.
- `counts/count.txt`: the same counts with gene symbols.
- `counts/sample_annotation.txt`: sample names, cell lines and run accessions.
- `build_figures.py`: Python source for the four figures.
- `plots/PDAC_featureCounts_M1_corrected.pdf`: figures only.
- `counts/sources/m1_correction/`: input checksums, pairing checks and Galaxy dataset IDs.

Run from this directory:

```sh
Rscript counts/prepare_data.R
python3 -m pip install -r requirements.txt
python3 build_figures.py
```

The plots use log2(CPM + 1) for correlation and PCA. PCA uses the 500 genes with the highest variance. Exported count tables remain unnormalized integers. Liberation Serif gives the saved figure font; Matplotlib uses an available fallback if it is absent.

M1 has 37,657,740 assigned counts (68.94%), 18,871 detected genes, and 85.54% concordant unique alignment. The old result had 509 assigned counts because both inputs contained the same reads. The two P5 KRAS runs remain separate; their repeat type is unresolved.
