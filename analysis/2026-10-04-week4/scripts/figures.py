import sys, json, hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import scipy.stats as st
from scipy.cluster.hierarchy import linkage, leaves_list
from scipy.spatial.distance import squareform
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.colors import LinearSegmentedColormap

base = Path(sys.argv[1])
res = base / "results"
out = base / "figures"
out.mkdir(exist_ok=True)
if len(sys.argv) > 2:
    for p in Path(sys.argv[2]).glob("*.TTF"):
        font_manager.fontManager.addfont(str(p))
plt.rcParams.update(
    {
        "font.family": "Times New Roman",
        "font.size": 10,
        "axes.titlesize": 12,
        "axes.labelsize": 10,
        "legend.fontsize": 9,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "savefig.facecolor": "white",
    }
)
BLUE = "#2166AC"
RED = "#B2182B"
LAPIS = "#26619C"
GRAY = "#A6A6A6"
cmap = LinearSegmentedColormap.from_list("lapis", ["white", LAPIS])
read = lambda p: pd.read_csv(res / p, sep="\t")
de = read("merge_p5/DESeq2_full.tsv")
er = read("merge_p5/edgeR_full.tsv")
sc = read("scenario_summary.tsv")
sen = read("sensitivity_full.tsv")
cmp = read("merge_p5/method_comparison.tsv")
paper = read("paper_comparison_common_unique.tsv")
ps = read("paper_comparison_summary.tsv")


def save(fig, name):
    fig.savefig(out / (name + ".png"), dpi=220, bbox_inches="tight")
    fig.savefig(out / (name + ".pdf"), bbox_inches="tight")
    plt.close(fig)


def panel(ax, text):
    ax.set_title(text, loc="left", fontweight="bold", pad=10)


def num(x):
    return f"{x:,}"


short = {"MiaPaca-2": "MP2", "PANC-1": "PANC1"}


def lab(sample):
    cell, cond = sample.rsplit("_", 1)
    return short.get(cell, cell) + " " + ("K" if cond == "KRAS" else "C")


qc = []
fig, axs = plt.subplots(1, 2, figsize=(7.8, 3.4), layout="constrained")
for ax, method in zip(axs, ["DESeq2", "edgeR"]):
    p = read(f"merge_p5/{method}_PCA.tsv")
    v = read(f"merge_p5/{method}_PCA_variance.tsv").variance_fraction
    for cell, g in p.groupby("cell_line", sort=False):
        ax.plot(g.PC1, g.PC2, color="#C8C8C8", lw=0.6, zorder=1)
        for row in g.itertuples():
            ax.scatter(
                row.PC1,
                row.PC2,
                c=BLUE if row.condition == "Control" else RED,
                marker="o" if row.condition == "Control" else "^",
                s=35,
                zorder=2,
            )
        center = g[["PC1", "PC2"]].mean()
        offsets = {"Pa16C": (-15, 12), "Pa14C": (6, -12), "Pa02C": (-18, -13), "HPAC": (3, 9)}
        ax.annotate(
            short.get(cell, cell),
            center,
            xytext=offsets.get(cell, (3, 4)),
            textcoords="offset points",
            fontsize=8,
        )
    ax.set_xlabel(f"PC1 ({v.iloc[0]:.1%})")
    ax.set_ylabel(f"PC2 ({v.iloc[1]:.1%})")
    panel(ax, f"{method}: " + ("VST" if method == "DESeq2" else "TMM logCPM"))
    for cond, color, marker in [("Control", BLUE, "o"), ("KRAS siRNA", RED, "^")]:
        ax.scatter([], [], c=color, marker=marker, label=cond)
    ax.legend(frameon=False, loc="lower left", fontsize=8)
save(fig, "A1_PCA")
fig, axs = plt.subplots(1, 2, figsize=(7.8, 3.9), layout="constrained")
for ax, method in zip(axs, ["DESeq2", "edgeR"]):
    dm = read(f"merge_p5/{method}_sample_distance.tsv").set_index("ENTREZID")
    samples = list(dm.columns)
    values = dm.to_numpy()
    ix = leaves_list(linkage(squareform(values, checks=True), method="complete"))
    im = ax.imshow(values[np.ix_(ix, ix)], cmap=cmap, aspect="equal")
    labels = [lab(samples[i]) for i in ix]
    ax.set_xticks(range(16), labels, rotation=90, fontsize=7)
    ax.set_yticks(range(16), labels, fontsize=7)
    for tick, i in zip(ax.get_xticklabels(), ix):
        tick.set_color(RED if samples[i].endswith("_KRAS") else BLUE)
    for tick, i in zip(ax.get_yticklabels(), ix):
        tick.set_color(RED if samples[i].endswith("_KRAS") else BLUE)
    panel(ax, method + " Euclidean distance")
    fig.colorbar(im, ax=ax, shrink=0.7, label="Distance")
    pairs = []
    between = []
    for i in range(16):
        for j in range(i):
            same = samples[i].rsplit("_", 1)[0] == samples[j].rsplit("_", 1)[0]
            (pairs if same else between).append(values[i, j])
    qc.append(
        {
            "method": method,
            "median_within_cell_line_distance": float(np.median(pairs)),
            "median_between_cell_line_distance": float(np.median(between)),
        }
    )
save(fig, "A2_sample_distances")
fig, axs = plt.subplots(1, 2, figsize=(7.8, 3.7), layout="constrained")
selected = ["KRAS", "DUSP6", "SPRY4", "MYC", "CCND1", "EMP2"]
for ax, method, table, xcol, fdrcol in [
    (axs[0], "DESeq2", de, "log2FC_apeglm", "padj"),
    (axs[1], "edgeR", er, "logFC", "FDR"),
]:
    t = table[table[fdrcol].notna() & table[xcol].notna()]
    x = t[xcol].to_numpy()
    y = -np.log10(np.maximum(t[fdrcol].to_numpy(), 1e-300))
    sig = t[fdrcol].to_numpy() < 0.05
    ax.scatter(x[~sig], y[~sig], s=3, c=GRAY, alpha=0.45, rasterized=True)
    ax.scatter(x[sig], y[sig], s=4, c=np.where(x[sig] > 0, RED, BLUE), alpha=0.6, rasterized=True)
    ax.axhline(-np.log10(0.05), ls="--", c="black", lw=0.7)
    ax.axvline(0, c="black", lw=0.5)
    for sy in selected:
        row = t[t.SYMBOL == sy].iloc[0]
        offset = {"DUSP6": (-30, -10), "SPRY4": (-22, 6), "MYC": (5, -5)}.get(sy, (4, 3))
        ax.annotate(
            sy,
            (row[xcol], -np.log10(row[fdrcol])),
            xytext=offset,
            textcoords="offset points",
            fontsize=7,
            bbox=dict(facecolor="white", edgecolor="none", alpha=0.65, pad=0.3),
        )
    ax.set_xlabel("log2FC (apeglm)" if method == "DESeq2" else "log2FC (edgeR estimate)")
    ax.set_ylabel("-log10(adjusted p)")
    panel(ax, method)
save(fig, "B1_volcanoes")
fig, axs = plt.subplots(
    1, 2, figsize=(7.8, 3.15), layout="constrained", gridspec_kw={"width_ratios": [0.9, 1.1]}
)
r = sc.iloc[0]
ax = axs[0]
x = np.arange(2)
ax.bar(x - 0.17, [r.DESeq2_down, r.edgeR_down], 0.34, color=BLUE, label="Down")
ax.bar(x + 0.17, [r.DESeq2_up, r.edgeR_up], 0.34, color=RED, label="Up")
for pos, vals in [(x - 0.17, [r.DESeq2_down, r.edgeR_down]), (x + 0.17, [r.DESeq2_up, r.edgeR_up])]:
    for p, v in zip(pos, vals):
        ax.text(p, v + 45, num(int(v)), ha="center", fontsize=9)
ax.set_xticks(x, ["DESeq2", "edgeR"])
ax.set_ylim(0, 4200)
ax.set_ylabel("Genes (FDR < 0.05)")
ax.legend(frameon=False, ncol=2, loc="upper left")
panel(ax, "Treatment response")
ax.set_axisbelow(True)
ax.grid(axis="y", color="#D9D9D9", linewidth=0.5, alpha=0.75)
ax = axs[1]
both = (cmp.DESeq2_padj < 0.05) & (cmp.edgeR_FDR < 0.05)
ax.scatter(
    cmp.DESeq2_log2FC,
    cmp.edgeR_log2FC,
    c=np.where(both, LAPIS, GRAY),
    s=4,
    alpha=0.4,
    rasterized=True,
)
lim = 8
ax.plot([-lim, lim], [-lim, lim], c="black", lw=0.7)
ax.set(xlim=(-lim, lim), ylim=(-lim, lim), xlabel="DESeq2 log2FC (unshrunk)", ylabel="edgeR log2FC")
panel(ax, "Method agreement")
ax.text(
    0.04,
    0.96,
    f"r = {r.LFC_pearson:.3f}; n = {int(r.shared_finite_p):,}\nShared DE = {int(r.overlap):,}; J = {r.jaccard:.3f}",
    transform=ax.transAxes,
    va="top",
    fontsize=9,
    bbox=dict(facecolor="white", alpha=0.8, edgecolor="none"),
)
save(fig, "B2_counts_and_agreement")
sensitivity = []
fig, axs = plt.subplots(1, 2, figsize=(7.8, 3.0), layout="constrained")
for ax, method, key, lfc in [
    (axs[0], "DESeq2", "padj", "log2FoldChange"),
    (axs[1], "edgeR", "FDR", "logFC"),
]:
    a = de if method == "DESeq2" else er
    aset = set(a.loc[a[key] < 0.05, "ENTREZID"])
    for scname, color, label in [
        ("retain_SRR24828472", BLUE, "Retain 472 (public K2)"),
        ("retain_SRR24828471", RED, "Retain 471 (public K2v2)"),
    ]:
        b = read(f"{scname}/{method}_full.tsv")
        bset = set(b.loc[b[key] < 0.05, "ENTREZID"])
        valid = a[lfc].notna() & b[lfc].notna()
        ax.scatter(
            a.loc[valid, lfc],
            b.loc[valid, lfc],
            s=2,
            c=color,
            alpha=0.2,
            rasterized=True,
            label=label,
        )
        sensitivity.append(
            dict(
                method=method,
                scenario=scname,
                overlap=len(aset & bset),
                lost_from_merge=len(aset - bset),
                gained_over_merge=len(bset - aset),
                jaccard=len(aset & bset) / len(aset | bset),
                LFC_Pearson=float(st.pearsonr(a.loc[valid, lfc], b.loc[valid, lfc]).statistic),
                common_finite_LFC=int(valid.sum()),
            )
        )
    ax.plot([-6, 6], [-6, 6], c="black", lw=0.7)
    ax.set(xlim=(-6, 6), ylim=(-6, 6), xlabel="Merged P5 log2FC", ylabel="Single-library P5 log2FC")
    panel(ax, method)
    ax.legend(frameon=False, fontsize=8, markerscale=3)
save(fig, "C1_P5_sensitivity")
pd.DataFrame(sensitivity).to_csv(res / "sensitivity_metrics.tsv", sep="\t", index=False)
fig, axs = plt.subplots(1, 2, figsize=(7.8, 3.2), layout="constrained")
for ax, method, col in [
    (axs[0], "DESeq2", "local_DESeq2_logFC"),
    (axs[1], "edgeR", "local_edgeR_logFC"),
]:
    ax.scatter(paper[col], paper.paper_logFC, s=4, c=LAPIS, alpha=0.35, rasterized=True)
    ax.plot([-6, 6], [-6, 6], c="black", lw=0.7)
    r0 = ps[(ps.method == method) & (ps.absLFC_gt == 0.5)].iloc[0]
    ax.set(xlim=(-6, 6), ylim=(-6, 6), xlabel=f"Local {method} log2FC", ylabel="Paper edgeR log2FC")
    panel(ax, method + " vs paper")
    ax.text(
        0.04,
        0.96,
        f"r = {r0.LFC_Pearson:.3f}; n = {int(r0.common_genes):,}\nFDR < .05, |LFC| > .5: J = {r0.jaccard:.3f}",
        transform=ax.transAxes,
        va="top",
        fontsize=9,
        bbox=dict(facecolor="white", alpha=0.85, edgecolor="none"),
    )
save(fig, "D1_paper_benchmark")
nc = read("merge_p5/DESeq2_normalized_counts.tsv").set_index("ENTREZID")
meta = read("merge_p5/samples.tsv")
gene_stats = []
fig, axs = plt.subplots(2, 3, figsize=(7.8, 4.2), layout="constrained")
cells = list(meta.cell_line.drop_duplicates())
palette = plt.cm.tab10(np.linspace(0, 1, 8))
for ax, sy in zip(axs.flat, selected):
    row = de[de.SYMBOL == sy].iloc[0]
    gene = int(row.ENTREZID)
    ys = np.log2(nc.loc[gene] + 1)
    downs = 0
    for j, cell in enumerate(cells):
        g = meta[meta.cell_line == cell]
        cs = g.loc[g.condition == "Control", "sample"].iloc[0]
        ks = g.loc[g.condition == "Treatment", "sample"].iloc[0]
        v = [ys[cs], ys[ks]]
        downs += v[1] < v[0]
        ax.plot([0, 1], v, color=palette[j], lw=0.8, alpha=0.8)
        ax.scatter([0, 1], v, c=[BLUE, RED], s=12, zorder=3)
    ax.set_xticks([0, 1], ["Control", "KRAS"])
    ax.set_ylabel("log2(normalized count + 1)", fontsize=8)
    panel(ax, sy)
    gene_stats.append(
        dict(ENTREZID=gene, SYMBOL=sy, paired_lines_down=downs, paired_lines_up=8 - downs)
    )
    ax.set_axisbelow(True)
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.5, alpha=0.75)
save(fig, "E1_candidate_paired_expression")
pd.DataFrame(gene_stats).to_csv(res / "candidate_pair_directions.tsv", sep="\t", index=False)
candidate = sen[sen.SYMBOL.isin(selected + ["EGR1", "DPM3", "TGFBR3", "WNT5A", "SFRP1"])].copy()
candidate.to_csv(res / "candidate_review.tsv", sep="\t", index=False)
fig, axs = plt.subplots(1, 3, figsize=(7.8, 2.65), layout="constrained")
for ax, file, title in [
    (axs[0], "DESeq2_log_normalized_mean_SD.tsv", "DESeq2 log2(count + 1)"),
    (axs[1], "DESeq2_mean_SD.tsv", "DESeq2 VST"),
    (axs[2], "edgeR_mean_SD.tsv", "edgeR logCPM"),
]:
    t = read("merge_p5/" + file)
    ax.hexbin(t["mean"], t.SD, gridsize=40, cmap=cmap, mincnt=1, linewidths=0)
    ax.set_xlabel("Mean transformed expression")
    ax.set_ylabel("Across-sample SD")
    panel(ax, title)
save(fig, "F1_mean_SD")
di = read("merge_p5/dispersion.tsv")
fig, axs = plt.subplots(1, 3, figsize=(7.8, 2.65), layout="constrained")
ax = axs[0]
valid = (di.baseMean > 0) & (di.DESeq2_dispersion > 0)
ax.scatter(
    di.loc[valid, "baseMean"],
    di.loc[valid, "DESeq2_dispersion"],
    s=2,
    c=LAPIS,
    alpha=0.3,
    rasterized=True,
)
t = di.loc[valid].sort_values("baseMean")
ax.plot(t.baseMean, t.DESeq2_dispersion_fit, c="black", lw=0.8)
ax.set(xscale="log", yscale="log", xlabel="Mean normalized count", ylabel="NB dispersion")
panel(ax, "DESeq2 final / trend")
ax = axs[1]
ax.scatter(
    di.edgeR_logCPM, np.sqrt(di.edgeR_NB_dispersion), s=2, c=LAPIS, alpha=0.3, rasterized=True
)
ax.set(xlabel="Average logCPM", ylabel="Biological CV")
panel(ax, "edgeR BCV")
ax = axs[2]
ax.scatter(di.edgeR_logCPM, di.edgeR_QL_variance, s=2, c=LAPIS, alpha=0.3, rasterized=True)
t = di.sort_values("edgeR_logCPM")
ax.plot(t.edgeR_logCPM, t.edgeR_QL_prior, c="black", lw=0.8)
ax.set(yscale="log", xlabel="Average logCPM", ylabel="QL posterior variance")
panel(ax, "edgeR QL / prior")
save(fig, "F2_dispersion_summary")
raw = read("raw17_samples.tsv")
fig, axs = plt.subplots(2, 1, figsize=(7.8, 4), layout="constrained")
colors = [BLUE if c == "Control" else RED for c in raw.condition]
labels = [
    short.get(r.cell_line, r.cell_line)
    + " "
    + (
        "C"
        if r.condition == "Control"
        else (
            "K/471"
            if r.run_accession == "SRR24828471"
            else "K/472" if r.run_accession == "SRR24828472" else "K"
        )
    )
    for r in raw.itertuples()
]
for ax, col, title in [
    (axs[0], "assigned_counts", "Assigned fragments (millions)"),
    (axs[1], "assigned_percent", "Assignment rate (%)"),
]:
    vals = raw[col] / (1000000.0 if col == "assigned_counts" else 1)
    ax.bar(np.arange(17), vals, color=colors)
    ax.set_xticks(np.arange(17), labels, rotation=45, ha="right", fontsize=8)
    ax.set_ylabel(title)
save(fig, "extra_raw17_count_QC")
fig, axs = plt.subplots(1, 2, figsize=(7.8, 3.1), layout="constrained")
ax = axs[0]
valid = de.padj.notna()
ax.scatter(
    np.log10(de.loc[valid, "baseMean"] + 1),
    de.loc[valid, "log2FC_apeglm"],
    c=np.where(de.loc[valid, "padj"] < 0.05, RED, GRAY),
    s=3,
    alpha=0.4,
    rasterized=True,
)
ax.axhline(0, c="black", lw=0.6)
ax.set(xlabel="log10(baseMean + 1)", ylabel="apeglm log2FC")
panel(ax, "DESeq2 MA")
ax = axs[1]
ax.scatter(
    er.logCPM, er.logFC, c=np.where(er.FDR < 0.05, RED, GRAY), s=3, alpha=0.4, rasterized=True
)
ax.axhline(0, c="black", lw=0.6)
ax.set(xlabel="Average logCPM", ylabel="log2FC")
panel(ax, "edgeR MD")
save(fig, "extra_MA_MD")
checks = []
for _, r in sc.iterrows():
    a = read(r.scenario + "/DESeq2_full.tsv")
    b = read(r.scenario + "/edgeR_full.tsv")
    aset = set(a.loc[a.padj < 0.05, "ENTREZID"])
    bset = set(b.loc[b.FDR < 0.05, "ENTREZID"])
    assert len(a) == len(b) == 28395 and a.ENTREZID.is_unique and b.ENTREZID.is_unique
    assert (
        len(aset) == r.DESeq2_sig
        and len(bset) == r.edgeR_sig
        and (len(aset & bset) == r.overlap)
        and (len(aset | bset) == r.union)
    )
    assert r.DESeq2_up + r.DESeq2_down == r.DESeq2_sig and r.edgeR_up + r.edgeR_down == r.edgeR_sig
    assert np.isclose(len(aset & bset) / len(aset | bset), r.jaccard)
    x = read(r.scenario + "/method_comparison.tsv")
    assert np.isclose(st.pearsonr(x.DESeq2_log2FC, x.edgeR_log2FC).statistic, r.LFC_pearson)
    checks.append(
        dict(
            scenario=r.scenario,
            genes=len(a),
            low_count=int((a.status == "low_count_prefilter").sum()),
            independent_filtered=int((a.status == "independent_filtered").sum()),
            DESeq2_unavailable_p=int(a.loc[a.prefilter_pass, "pvalue"].isna().sum()),
            count_intersection_union_Jaccard_correlation_verified=True,
        )
    )
robust = int((sen.significant_all_six & sen.same_direction_all_six).sum())
for row in ps.itertuples():
    x = paper.local_edgeR_logFC if row.method == "edgeR" else paper.local_DESeq2_logFC
    f = paper.local_edgeR_FDR if row.method == "edgeR" else paper.local_DESeq2_padj
    l = set(paper.loc[(f < 0.05) & (abs(x) > row.absLFC_gt), "ENTREZID"])
    p = set(
        paper.loc[(paper.paper_FDR < 0.05) & (abs(paper.paper_logFC) > row.absLFC_gt), "ENTREZID"]
    )
    assert (
        len(l & p) == row.overlap
        and np.isclose(len(l & p) / len(l | p), row.jaccard)
        and (len(l) == row.local_sig)
        and (len(p) == row.paper_sig)
    )
audit = dict(
    scenarios=checks,
    robust_same_direction_all_six=robust,
    QC_distances=qc,
    paper_common_unique_genes=len(paper),
    paper_Jaccard_denominators_verified=True,
    correlations_use_all_shared_finite_estimates=True,
    scientific_scope="Exploratory common treatment effect; six fits share data and are not independent replication.",
)
(res / "independent_numerical_validation.json").write_text(json.dumps(audit, indent=2))
print(json.dumps(audit, indent=2))
