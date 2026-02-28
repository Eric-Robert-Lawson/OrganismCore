import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# ============================================================
# GREENWOOD FUNCTION
# ============================================================

def greenwood_freq(x, A=165.4, a=2.1, k=0.88):
    return A * (10**(a * x) - k)

def greenwood_pos(f, A=165.4, a=2.1, k=0.88):
    """Normalized cochlear position (0=apex, 1=base) for frequency f."""
    return np.log10((f / A) + k) / a

COCHLEAR_MM = 35.0

# ============================================================
# ARCHIVE DATA — EXACT VALUES FROM OHSU TINNITUS ARCHIVE
# DATA SET 1, n=1514
# ============================================================

bin_labels = ['0–1900', '2000–3900', '4000–5900',
              '6000–7900', '8000–9900', '10000–16000']
bin_lo     = np.array([20,   2000,  4000,  6000,  8000,  10000], dtype=float)
bin_hi     = np.array([1900, 3900,  5900,  7900,  9900,  16000], dtype=float)
bin_n      = np.array([134,  244,   302,   285,   345,   204],   dtype=float)
n_total    = bin_n.sum()   # 1514.0

# Cochlear position of each bin boundary (mm from apex)
pos_lo_mm = np.array([greenwood_pos(f) * COCHLEAR_MM for f in bin_lo])
pos_hi_mm = np.array([greenwood_pos(f) * COCHLEAR_MM for f in bin_hi])
bin_width_mm = pos_hi_mm - pos_lo_mm

# ============================================================
# NULL MODEL: uniform on cochlear position axis
# ============================================================

# Renormalize so null_counts sums to EXACTLY n_total
# (avoids floating-point tolerance error in chisquare)
raw_null = bin_width_mm / bin_width_mm.sum()
null_counts = raw_null * n_total          # sums exactly to n_total
null_proportions = raw_null
obs_proportions  = bin_n / n_total

# ============================================================
# CHI-SQUARED TEST
# ============================================================

chi2, p_val = stats.chisquare(bin_n, f_exp=null_counts)

# ============================================================
# PRINT RESULTS
# ============================================================

print("=" * 68)
print("P4 ANALYSIS — TINNITUS PITCH vs COCHLEAR EIGENFUNCTION POSITIONS")
print("OHSU Tinnitus Archive, Data Set 1, n=1514")
print("=" * 68)
print()
print(f"{'Bin (Hz)':<16} {'mm_lo':>6} {'mm_hi':>6} {'width':>6} "
      f"{'obs_n':>6} {'obs_%':>6} {'null_%':>7} {'ratio':>7}")
print("-" * 68)
enrichment = obs_proportions / null_proportions
for i in range(len(bin_labels)):
    print(f"{bin_labels[i]:<16} "
          f"{pos_lo_mm[i]:>6.1f} {pos_hi_mm[i]:>6.1f} "
          f"{bin_width_mm[i]:>6.1f} "
          f"{int(bin_n[i]):>6d} {obs_proportions[i]*100:>6.1f}% "
          f"{null_proportions[i]*100:>7.1f}% "
          f"{enrichment[i]:>7.2f}x")
print("-" * 68)
print()
print(f"Chi-squared statistic : {chi2:.1f}")
print(f"p-value               : {p_val:.2e}")
print(f"Degrees of freedom    : {len(bin_n) - 1}")
print()
print(f"Reported mean pitch   : 5970 Hz  ± 3145 Hz")
pos_mean = greenwood_pos(5970) * COCHLEAR_MM
print(f"Greenwood position    : {pos_mean:.1f} mm from apex  "
      f"({pos_mean/COCHLEAR_MM*100:.0f}% of cochlear length)")
print()

zone_lo = greenwood_pos(4000) * COCHLEAR_MM
zone_hi = greenwood_pos(9900) * COCHLEAR_MM
pct_cochlea  = (zone_hi - zone_lo) / COCHLEAR_MM * 100
pct_tinnitus = (obs_proportions[2] + obs_proportions[3] +
                obs_proportions[4]) * 100
print(f"4–10 kHz zone         : {zone_lo:.1f}–{zone_hi:.1f} mm from apex "
      f"= {pct_cochlea:.0f}% of cochlear length")
print(f"Tinnitus in that zone : {pct_tinnitus:.1f}%")
print(f"Enrichment factor     : {pct_tinnitus/pct_cochlea:.1f}x over null")

# ============================================================
# PLOT
# ============================================================

fig, axes = plt.subplots(1, 3, figsize=(16, 6))

# --- Panel 1: Greenwood map with tinnitus zone ---
ax1 = axes[0]
x_norm  = np.linspace(0.02, 1.0, 2000)
f_curve = greenwood_freq(x_norm)
mask    = (f_curve >= 100) & (f_curve <= 20000)
ax1.semilogy(x_norm[mask] * COCHLEAR_MM, f_curve[mask],
             'k-', lw=2)
ax1.axhspan(4000, 9900, alpha=0.18, color='red',
            label='Peak tinnitus zone\n(61.5% of cases)')
ax1.axhline(5970, color='darkred', ls='--', lw=1.5,
            label='Mean pitch (5970 Hz)')
bin_mid_log = np.sqrt(bin_lo * bin_hi)
bin_mid_log[0] = 200   # geometric approx for 20–1900
pos_mid_mm = (pos_lo_mm + pos_hi_mm) / 2
for i in range(len(bin_labels)):
    ax1.scatter(pos_mid_mm[i], bin_mid_log[i],
                s=bin_n[i] / 5, color='steelblue',
                alpha=0.75, zorder=5)
ax1.set_xlabel('Distance from apex (mm)', fontsize=11)
ax1.set_ylabel('Characteristic frequency (Hz)', fontsize=11)
ax1.set_title('Greenwood Map\n(dot size ∝ patient count)', fontsize=11)
ax1.legend(fontsize=8)
ax1.grid(True, which='both', alpha=0.2)
ax1.set_xlim(0, 35)
ax1.set_ylim(100, 25000)

# --- Panel 2: Observed vs null ---
ax2 = axes[1]
x_pos = np.arange(len(bin_labels))
w = 0.35
ax2.bar(x_pos - w/2, obs_proportions  * 100, w,
        color='steelblue', alpha=0.85,
        label='Observed (Archive n=1514)')
ax2.bar(x_pos + w/2, null_proportions * 100, w,
        color='gray', alpha=0.6,
        label='Null: uniform on\ncochlear position axis')
ax2.set_xticks(x_pos)
ax2.set_xticklabels(bin_labels, rotation=35, ha='right', fontsize=8)
ax2.set_ylabel('% of patients', fontsize=11)
ax2.set_title(f'Observed vs Null Model\n'
              f'χ²={chi2:.0f},  p={p_val:.1e},  n={int(n_total)}',
              fontsize=11)
ax2.legend(fontsize=9)
ax2.grid(axis='y', alpha=0.3)

# --- Panel 3: Enrichment ratio ---
ax3 = axes[2]
colors = ['#d32f2f' if e > 1 else '#1565c0' for e in enrichment]
bars = ax3.bar(x_pos, enrichment, color=colors, alpha=0.85)
ax3.axhline(1.0, color='black', ls='--', lw=1.5,
            label='Null expectation (1.0×)')
for bar, val in zip(bars, enrichment):
    ax3.text(bar.get_x() + bar.get_width() / 2,
             bar.get_height() + 0.04,
             f'{val:.2f}×', ha='center', va='bottom', fontsize=9,
             fontweight='bold')
ax3.set_xticks(x_pos)
ax3.set_xticklabels(bin_labels, rotation=35, ha='right', fontsize=8)
ax3.set_ylabel('Enrichment over null\n(observed / expected)', fontsize=11)
ax3.set_title('Eigenfunction Enrichment\n'
              'Red = over-represented, Blue = under-represented',
              fontsize=11)
ax3.legend(fontsize=9)
ax3.grid(axis='y', alpha=0.3)
ax3.set_ylim(0, max(enrichment) * 1.35)

plt.suptitle(
    'P4: Tinnitus Pitch Distribution vs Cochlear Eigenfunction Positions\n'
    'OHSU Tinnitus Archive Data Set 1  (n=1514,  1981–1994)',
    fontsize=13, fontweight='bold', y=1.02
)
plt.tight_layout()
plt.savefig('p4_tinnitus_eigenfunction_analysis.png',
            dpi=150, bbox_inches='tight')
plt.show()
print("\nSaved: p4_tinnitus_eigenfunction_analysis.png")
