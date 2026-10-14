"""Build consistent, high-resolution charts used by the report and slide deck."""
from pathlib import Path
import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

NAVY = '#102F3A'
TEAL = '#1B8A8F'
CORAL = '#F07861'
MUTED = '#637780'
GRID = '#D9E4E7'
PALE = '#F5F8F8'


def prepare_design_assets(root: Path, cv_results, report_dict, importance, audit):
    root = Path(root)
    assets = root / '.build_assets'
    assets.mkdir(exist_ok=True)
    results = root / 'results'
    out = {}
    plt.rcParams.update({
        'font.family': 'DejaVu Sans', 'font.size': 9,
        'axes.edgecolor': GRID, 'axes.labelcolor': MUTED,
        'xtick.color': MUTED, 'ytick.color': NAVY,
        'text.color': NAVY, 'figure.facecolor': 'white',
        'axes.facecolor': 'white', 'savefig.facecolor': 'white'
    })

    # Cross-validation comparison with fold standard deviation.
    cv = cv_results.copy().sort_values('cv_macro_f1_mean', ascending=True)
    labels = cv['model'].astype(str).tolist()
    means = cv['cv_macro_f1_mean'].astype(float).to_numpy()
    stds = cv['cv_macro_f1_std'].astype(float).to_numpy()
    fig, ax = plt.subplots(figsize=(7.5, 3.9), dpi=220)
    colors = [CORAL if 'Random Forest' == name else (TEAL if name == 'Random Forest + interactions' else '#A9B9BF') for name in labels]
    y = np.arange(len(labels))
    ax.barh(y, means, xerr=stds, height=0.62, color=colors, edgecolor='none', capsize=3,
            error_kw={'ecolor': NAVY, 'elinewidth': 0.8, 'capthick': 0.8})
    ax.set_yticks(y, labels)
    ax.set_xlim(0, max(0.82, float((means + stds).max() + .05)))
    ax.set_xlabel('Mean macro-F1 across 5 stratified folds (higher is better)', labelpad=9)
    ax.xaxis.grid(True, color=GRID, linewidth=0.7)
    ax.set_axisbelow(True)
    for spine in ['top', 'right', 'left']:
        ax.spines[spine].set_visible(False)
    ax.spines['bottom'].set_color(GRID)
    ax.tick_params(axis='y', length=0, pad=7)
    for yi, m, s in zip(y, means, stds):
        ax.text(min(m + s + .014, .80), yi, f'{m:.3f} +/- {s:.3f}', va='center', ha='left', fontsize=7.5, color=NAVY)
    fig.tight_layout(pad=1.4)
    path = assets / 'cv_comparison.png'; fig.savefig(path, dpi=220, bbox_inches='tight'); plt.close(fig); out['cv'] = path

    # Confusion matrix based only on saved observed test predictions.
    cm_path = results / 'confusion_matrix.csv'
    cm_df = pd.read_csv(cm_path, index_col=0)
    cm = cm_df.to_numpy(dtype=int)
    classes = ['1', '2', '3', '5']
    cmap = LinearSegmentedColormap.from_list('reef', ['#F4F8F8', '#8CC9C4', TEAL, NAVY])
    fig, ax = plt.subplots(figsize=(4.0, 3.4), dpi=220)
    im = ax.imshow(cm, cmap=cmap, vmin=0, vmax=cm.max())
    ax.set_xticks(range(4), classes); ax.set_yticks(range(4), classes)
    ax.set_xlabel('Predicted regime', labelpad=7); ax.set_ylabel('Actual regime', labelpad=7)
    ax.set_xticks(np.arange(-.5, 4, 1), minor=True); ax.set_yticks(np.arange(-.5, 4, 1), minor=True)
    ax.grid(which='minor', color='white', linestyle='-', linewidth=2)
    ax.tick_params(which='minor', bottom=False, left=False)
    threshold = cm.max() * .52
    for i in range(4):
        for j in range(4):
            ax.text(j, i, str(cm[i, j]), ha='center', va='center', fontsize=10,
                    color='white' if cm[i, j] >= threshold else NAVY, fontweight='bold' if i == j else 'normal')
    for spine in ax.spines.values(): spine.set_visible(False)
    fig.tight_layout(pad=1.1)
    path = assets / 'confusion_matrix.png'; fig.savefig(path, dpi=220, bbox_inches='tight'); plt.close(fig); out['cm'] = path

    # Class distribution chart.
    dist = pd.read_csv(results / 'class_distribution.csv')
    dist['regime'] = dist['regime'].astype(str)
    fig, ax = plt.subplots(figsize=(5.3, 2.8), dpi=220)
    colors = [TEAL, TEAL, TEAL, CORAL]
    bars = ax.bar(dist['regime'], dist['count'], color=colors, width=.56)
    ax.set_ylabel('Number of sites'); ax.set_xlabel('Observed regime label')
    ax.set_ylim(0, max(dist['count']) * 1.22)
    ax.yaxis.grid(True, color=GRID, linewidth=.7); ax.set_axisbelow(True)
    for spine in ['top', 'right', 'left']: ax.spines[spine].set_visible(False)
    ax.spines['bottom'].set_color(GRID); ax.tick_params(length=0)
    for bar, val in zip(bars, dist['count']): ax.text(bar.get_x()+bar.get_width()/2, val+3, str(int(val)), ha='center', va='bottom', fontsize=9, fontweight='bold')
    fig.tight_layout(pad=1.1)
    path = assets / 'class_distribution.png'; fig.savefig(path, dpi=220, bbox_inches='tight'); plt.close(fig); out['class_dist'] = path

    # Top-five permutation importance.
    imp = importance.copy().sort_values('permutation_importance_mean', ascending=True).tail(5)
    fig, ax = plt.subplots(figsize=(5.4, 3.1), dpi=220)
    vals = imp['permutation_importance_mean'].astype(float).to_numpy()
    names = imp['feature'].astype(str).tolist()
    cols = [CORAL if name in set(imp['feature'].astype(str).tail(3)) else TEAL for name in names]
    bars = ax.barh(np.arange(len(names)), vals, color=cols, height=.62)
    ax.set_yticks(np.arange(len(names)), names)
    ax.set_xlabel('Decrease in held-out macro-F1 when shuffled')
    ax.axvline(0, color=MUTED, linewidth=.7)
    ax.xaxis.grid(True, color=GRID, linewidth=.7); ax.set_axisbelow(True)
    for spine in ['top', 'right', 'left']: ax.spines[spine].set_visible(False)
    ax.spines['bottom'].set_color(GRID); ax.tick_params(axis='y', length=0, pad=5)
    for bar, val in zip(bars, vals):
        ax.text(val + (0.0006 if val >= 0 else -0.0006), bar.get_y()+bar.get_height()/2, f'{val:.3f}',
                va='center', ha='left' if val >= 0 else 'right', fontsize=7.5)
    fig.tight_layout(pad=1.1)
    path = assets / 'feature_importance.png'; fig.savefig(path, dpi=220, bbox_inches='tight'); plt.close(fig); out['importance'] = path
    return out
