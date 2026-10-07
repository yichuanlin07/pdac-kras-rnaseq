from pathlib import Path
import json, hashlib, re
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

ROOT = Path(__file__).resolve().parent / "plots"
ROOT.mkdir(exist_ok=True)
SOURCE = ROOT.parent / "counts"
FIG = ROOT / "figures"
DATA = ROOT / "data"
FIG.mkdir(exist_ok=True)
DATA.mkdir(exist_ok=True)
counts = pd.read_csv(SOURCE / "counts_raw.txt", sep="\t", index_col=0)
meta = pd.read_csv(SOURCE / "sample_annotation.txt", sep="\t")
assert list(counts.columns) == meta.sample_name.tolist()
qc = (
    pd.read_csv(SOURCE / "sources/summary_review.tsv", sep="\t")
    .set_index("sample")
    .loc[counts.columns]
)
x = counts.to_numpy(float)
totals = x.sum(0)
detected = (x > 0).sum(0)
assert np.array_equal(totals, qc.assigned.to_numpy())
labels = [
    ("C-" if r.condition == "Control" else "K-") + r.local_label.split(" ")[1]
    for r in meta.itertuples()
]
m1 = labels.index("K-M1")
normal = np.arange(17) != m1
palette = {"Control": "#356A91", "KRAS": "#B87333", "review": "#9D3035"}
barcolors = [palette[r.condition] for r in meta.itertuples()]
log = np.log2(x / totals * 1000000.0 + 1)
active = (x > 0).any(1)
corr = np.corrcoef(log[active].T)
variance = log.var(1, ddof=1)
top = np.argsort(-variance, kind="stable")[:500]
centered = log[top].T - log[top].T.mean(0)
u, s, vt = np.linalg.svd(centered, full_matrices=False)
scores = u[:, :2] * s[:2]
explained = s * s / (s * s).sum()
top10 = np.sort(x, axis=0)[-10:].sum(0) / totals * 100
metrics = meta.copy()
metrics["short_label"] = labels
metrics["genes_count_gt0"] = detected
metrics["top10_count_percent"] = top10
metrics.to_csv(DATA / "sample_metrics.tsv", sep="\t", index=False)
pd.DataFrame(corr, index=labels, columns=labels).to_csv(DATA / "pearson_logCPM.tsv", sep="\t")
pd.DataFrame(
    {"sample": meta.sample_name, "label": labels, "PC1": scores[:, 0], "PC2": scores[:, 1]}
).to_csv(DATA / "pca_scores.tsv", sep="\t", index=False)
pd.DataFrame({"ENTREZID": counts.index[top], "logCPM_variance": variance[top]}).to_csv(
    DATA / "pca_genes.tsv", sep="\t", index=False
)
facts = {
    "genes": len(counts),
    "samples": 17,
    "active_genes": int(active.sum()),
    "m1_detected": int(detected[m1]),
    "m1_top10_percent": float(top10[m1]),
    "pca_variance_explained": explained[:2].tolist(),
    "correlation_m1_range": [
        float(np.delete(corr[m1], m1).min()),
        float(np.delete(corr[m1], m1).max()),
    ],
    "m1_control_correlation": float(corr[m1, labels.index("C-M1")]),
    "m1_assigned": int(totals[m1]),
    "m1_assigned_percent": float(qc.assigned_percent.iloc[m1]),
    "m1_chimera_percent": float(qc.chimera_percent.iloc[m1]),
    "other_assigned_percent_range": [
        float(qc.assigned_percent[normal].min()),
        float(qc.assigned_percent[normal].max()),
    ],
    "other_detected_range": [int(detected[normal].min()), int(detected[normal].max())],
}
(DATA / "metrics.json").write_text(json.dumps(facts, indent=2) + "\n")
serif = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
if Path(serif).exists():
    font_manager.fontManager.addfont(serif)
plt.rcParams.update(
    {
        "font.family": "Liberation Serif",
        "font.size": 11,
        "axes.labelsize": 11,
        "axes.titlesize": 12,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "pdf.fonttype": 42,
        "svg.fonttype": "none",
        "figure.facecolor": "white",
        "axes.facecolor": "white",
    }
)


def save(fig, name):
    fig.savefig(FIG / (name + ".png"), dpi=240, bbox_inches="tight", facecolor="white")
    fig.savefig(FIG / (name + ".pdf"), bbox_inches="tight", facecolor="white")
    plt.close(fig)


def prep_bars(ax):
    ax.set_yticks(range(17), labels)
    ax.invert_yaxis()
    ax.set_axisbelow(True)
    ax.grid(axis="x", color="#dedede", linewidth=0.5)
    ax.axhline(7.5, color="#999999", linewidth=0.6)
    for i, t in enumerate(ax.get_yticklabels()):
        if i == m1:
            t.set_fontweight("bold")


fig, axes = plt.subplots(1, 2, figsize=(8, 5.4), gridspec_kw={"width_ratios": [1.1, 1]})
for ax in axes:
    prep_bars(ax)
axes[0].barh(range(17), totals / 1000000.0, color=barcolors, height=0.66)
axes[0].set(xlim=(0, 48), xlabel="Assigned counts (millions)", title="A  Assigned count total")
for i, v in enumerate(totals):
    axes[0].text(v / 1000000.0 + 0.45, i, f"{v / 1000000.0:.1f}", va="center", fontsize=9)
rates = qc.assigned_percent.to_numpy()
axes[1].barh(range(17), rates, color=barcolors, height=0.66)
axes[1].set(xlim=(0, 100), xlabel="Assigned / all summary records (%)", title="B  Assignment rate")
for i, v in enumerate(rates):
    axes[1].text(v + 1, i, f"{v:.1f}%", va="center", fontsize=9)
fig.tight_layout(w_pad=2)
save(fig, "01_assignment")
fig, axes = plt.subplots(1, 2, figsize=(8, 5.4), gridspec_kw={"width_ratios": [1.05, 1]})
for ax in axes:
    prep_bars(ax)
axes[0].barh(range(17), detected, color=barcolors, height=0.66)
axes[0].set(xlim=(0, 23000), xlabel="Genes with raw count > 0", title="A  Detected genes")
for i, v in enumerate(detected):
    axes[0].text(v + 230, i, f"{v:,}", va="center", fontsize=8.5)
axes[1].barh(range(17), top10, color=barcolors, height=0.66)
axes[1].set(
    xlim=(0, max(12, top10.max() * 1.2)),
    xlabel="Share of assigned counts (%)",
    title="B  Top 10 genes by count",
)
for i, v in enumerate(top10):
    axes[1].text(v + 0.5, i, f"{v:.1f}%", va="center", fontsize=9)
fig.tight_layout(w_pad=2)
save(fig, "02_detection")
fig, ax = plt.subplots(figsize=(7.4, 6.4))
im = ax.imshow(corr, vmin=0, vmax=1, cmap="Blues", interpolation="nearest")
ax.set_xticks(range(17), labels, rotation=55, ha="right", fontsize=9)
ax.set_yticks(range(17), labels, fontsize=9)
ax.axhline(7.5, color="white", lw=1.2)
ax.axvline(7.5, color="white", lw=1.2)
for i in range(17):
    for j in range(17):
        ax.text(
            j,
            i,
            f"{corr[i, j]:.2f}",
            ha="center",
            va="center",
            fontsize=7.8,
            color="white" if corr[i, j] > 0.65 else "#222222",
        )
ax.get_xticklabels()[m1].set_fontweight("bold")
ax.get_yticklabels()[m1].set_fontweight("bold")
fig.colorbar(im, ax=ax, shrink=0.75, pad=0.035, label="Pearson r on log2(CPM + 1)")
fig.tight_layout()
save(fig, "03_correlation")
fig, ax = plt.subplots(figsize=(7.7, 5.1))
offsets = {
    0: (0, 18),
    1: (-42, -5),
    2: (-28, -14),
    3: (-27, -15),
    4: (-20, -17),
    5: (-25, 15),
    6: (8, -25),
    7: (-16, -19),
    8: (8, -4),
    9: (-44, 22),
    10: (8, 8),
    11: (8, 8),
    12: (8, 8),
    13: (10, 0),
    14: (8, 13),
    15: (-30, 13),
    16: (12, 0),
}
for i, row in enumerate(meta.itertuples()):
    ax.scatter(
        *scores[i],
        color=barcolors[i],
        marker="o" if row.condition == "Control" else "^",
        s=70 if i == m1 else 40,
        edgecolors="black",
        linewidths=0.4,
        zorder=3,
    )
    ax.annotate(
        labels[i],
        scores[i],
        xytext=offsets[i],
        textcoords="offset points",
        fontsize=9,
        arrowprops={"arrowstyle": "-", "lw": 0.45, "color": "#777777"},
        color=barcolors[i],
    )
for cond, marker in [("Control", "o"), ("KRAS", "^")]:
    ax.scatter([], [], color=palette[cond], marker=marker, s=40, label=cond)
ax.set(xlabel=f"PC1 ({explained[0] * 100:.2f}%)", ylabel=f"PC2 ({explained[1] * 100:.2f}%)")
ax.margins(0.2)
ax.grid(color="#dddddd", linewidth=0.5)
ax.set_axisbelow(True)
ax.legend(frameon=False, loc="lower left")
fig.tight_layout()
save(fig, "04_pca")
from pypdf import PdfWriter
import zipfile

pdf = ROOT / "PDAC_featureCounts_M1_corrected.pdf"
w = PdfWriter()
for name in ["01_assignment", "02_detection", "03_correlation", "04_pca"]:
    w.append(str(FIG / (name + ".pdf")))
with pdf.open("wb") as f:
    w.write(f)
with zipfile.ZipFile(
    ROOT.parent / "PDAC_featureCounts_M1_corrected.zip", "w", zipfile.ZIP_DEFLATED
) as z:
    z.write(pdf, pdf.name)
    for p in sorted(FIG.iterdir()):
        z.write(p, "figures/" + p.name)
print(pdf)
