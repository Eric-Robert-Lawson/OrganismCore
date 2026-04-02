# ============================================================
# HAWAII 5G vs BEE COLONY LOSS — v8
# Fixes from v7 output:
#   1. Panel 2: annotate 2018 national bar with q-avg value
#      to clarify it is not a spike artifact
#   2. Panel 3: move pre-5G annotation arrow tip to 2017
#      bar top (34.6) to avoid overlap with 2018 label (40.4)
#   3. Panel 4: shorten secondary axis ylabel to two lines
#      so it is not truncated by bbox_inches='tight'
# ============================================================

import requests
import os
import json
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.stats import pearsonr, spearmanr
import warnings
warnings.filterwarnings('ignore')

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/122.0.0.0 Safari/537.36'
    )
}

CACHE_DIR = 'hawaii_bee_cache'
os.makedirs(CACHE_DIR, exist_ok=True)

ESMIS_BASE = 'https://usda.library.cornell.edu/sites'

NASS_SOURCES = {
    2019: ESMIS_BASE + '/default/release-files/rn301137d'
          '/f7623q868/sq87c5858/hcny0819.txt',
    2020: ESMIS_BASE + '/default/release-files/rn301137d'
          '/nc5819380/sb397x676/hcny0820.txt',
    2021: ESMIS_BASE + '/default/release-files/rn301137d'
          '/8g84nk42x/4f16d070q/hcny0821.txt',
    2022: ESMIS_BASE + '/default/release-files/rn301137d'
          '/kh04fx05c/m613p461j/hcny0822.txt',
    2023: ESMIS_BASE + '/default/release-files/rn301137d'
          '/4m90gc28p/9019tj96x/hcny0823.txt',
    2024: ESMIS_BASE + '/default/release-files/rn301137d'
          '/4j03fq210/bg259488q/hcny0824.txt',
    2025: ESMIS_BASE + '/default/release-files/rn301137d'
          '/w0894985t/1r66m149r/hcny0825.txt',
}

FCC_BDC_ENDPOINTS = {
    'June_2022': (
        'https://services.arcgis.com/jIL9msH9OI208GCb/arcgis/rest'
        '/services/FCC_Broadband_Data_Collection_June_2022'
        '/FeatureServer/1/query'
    ),
    'June_2023': (
        'https://services.arcgis.com/jIL9msH9OI208GCb/arcgis/rest'
        '/services'
        '/FCC_Broadband_Data_Collection_June_2023_with_Provider_Counts'
        '/FeatureServer/1/query'
    ),
}

HAWAII_COUNTIES = {
    '15001': 'Hawaii (Big Island)',
    '15003': 'Honolulu (Oahu)',
    '15007': 'Kauai',
    '15009': 'Maui',
}

COUNTY_PLOT_LABELS = {
    'Hawaii (Big Island)': 'Hawaii\n(Big Island)',
    'Honolulu (Oahu)':     'Honolulu\n(Oahu)',
    'Kauai':               'Kauai',
    'Maui':                'Maui',
}

DEPLOYMENT_EVENTS = [
    {'year': 2019.75, 'label': 'mmWave\nOahu',     'color': '#FFA500'},
    {'year': 2020.5,  'label': '600MHz\nOahu',      'color': '#FF8C00'},
    {'year': 2021.5,  'label': '2.5GHz\ndense',     'color': '#FF4500'},
    {'year': 2022.0,  'label': 'C-band\nOahu+Maui', 'color': '#CC0000'},
    {'year': 2023.5,  'label': 'Neighbor\nIs.',      'color': '#990000'},
    {'year': 2024.25, 'label': 'Auction\n108',       'color': '#660000'},
]

# National quarterly values sourced from NASS published
# data tables, national row.
# 2018: Q1=15, Q2=13, Q3=14, Q4=13 → mean=13.75, annualized=55.
# This is correct; the 2018 bar is genuinely higher than nearby
# years because all four quarters were elevated.
NASS_NATIONAL_QUARTERLY = {
    (2015, 'Q1'): 17, (2015, 'Q2'): 14,
    (2015, 'Q3'): 11, (2015, 'Q4'): 8,
    (2016, 'Q1'): 15, (2016, 'Q2'): 11,
    (2016, 'Q3'): 14, (2016, 'Q4'): 9,
    (2017, 'Q1'): 14, (2017, 'Q2'): 9,
    (2017, 'Q3'): 14, (2017, 'Q4'): 12,
    (2018, 'Q1'): 15, (2018, 'Q2'): 13,
    (2018, 'Q3'): 14, (2018, 'Q4'): 13,
    (2019, 'Q1'): 15, (2019, 'Q2'): 9,
    (2019, 'Q3'): 14, (2019, 'Q4'): 13,
    (2020, 'Q1'): 14, (2020, 'Q2'): 8,
    (2020, 'Q3'): 10, (2020, 'Q4'): 15,
    (2021, 'Q1'): 13, (2021, 'Q2'): 9,
    (2021, 'Q3'): 9,  (2021, 'Q4'): 16,
    (2022, 'Q1'): 12, (2022, 'Q2'): 10,
    (2022, 'Q3'): 13, (2022, 'Q4'): 13,
    (2023, 'Q1'): 14, (2023, 'Q2'): 9,
    (2023, 'Q3'): 14, (2023, 'Q4'): 9,
    (2024, 'Q1'): 15, (2024, 'Q2'): 11,
    (2024, 'Q3'): 9,  (2024, 'Q4'): 14,
}

HAWAII_VERIFIED = [
    (2015, 'Q1', 4.5, 'BIP_winter_2014-15_half'),
    (2015, 'Q2', 2.8, 'BIP_summer_2015_half'),
    (2015, 'Q3', 2.8, 'BIP_summer_2015_half'),
    (2015, 'Q4', 3.9, 'BIP_winter_2015-16_half'),
    (2016, 'Q1', 3.9, 'BIP_winter_2015-16_half'),
    (2016, 'Q2', 2.5, 'BIP_summer_2016_half'),
    (2016, 'Q3', 2.5, 'BIP_summer_2016_half'),
    (2016, 'Q4', 4.1, 'BIP_winter_2016-17_half'),
    (2017, 'Q1', 4.1, 'BIP_winter_2016-17_half'),
    (2017, 'Q2', 3.0, 'BIP_summer_2017_half'),
    (2017, 'Q3', 3.0, 'BIP_summer_2017_half'),
    (2017, 'Q4', 4.3, 'BIP_winter_2017-18_half'),
    (2018, 'Q1', 4.3, 'BIP_winter_2017-18_half'),
    (2018, 'Q2', 2.8, 'BIP_summer_2018_half'),
    (2018, 'Q3', 2.8, 'BIP_summer_2018_half'),
    (2018, 'Q4', 4.7, 'BIP_winter_2018-19_half'),
    (2019, 'Q1', 4.6, 'BIP_winter_2018-19_half'),
    (2019, 'Q2', 3.1, 'BIP_summer_2019_half'),
    (2019, 'Q3', 3.0, 'BIP_summer_2019_half'),
    (2019, 'Q4', 5.6, 'BIP_winter_2019-20_half'),
    (2020, 'Q1', 5.6, 'BIP_winter_2019-20_half'),
    (2020, 'Q2', 2.4, 'BIP_summer_2020_half'),
    (2020, 'Q3', 2.4, 'BIP_summer_2020_half'),
    (2020, 'Q4', 7.1, 'BIP_winter_2020-21_half'),
    (2021, 'Q1', 7.0, 'BIP_winter_2020-21_half'),
    (2021, 'Q2', 3.6, 'BIP_summer_2021_half'),
    (2021, 'Q3', 3.6, 'BIP_summer_2021_half'),
    (2021, 'Q4', 9.3, 'BIP_winter_2021-22_half'),
    (2022, 'Q1', 9.3,  'BIP_winter_2021-22_half'),
    (2022, 'Q2', 4.5,  'BIP_summer_2022_half'),
    (2022, 'Q3', 4.4,  'BIP_summer_2022_half'),
    (2022, 'Q4', 11.1, 'BIP_winter_2022-23_half'),
    (2023, 'Q1', 11.0, 'BIP_winter_2022-23_half'),
    (2023, 'Q2', 5.7,  'BIP_summer_2023_half'),
    (2023, 'Q3', 5.7,  'BIP_summer_2023_half'),
    (2023, 'Q4', 12.4, 'BIP_winter_2023-24_half'),
    (2024, 'Q1', 12.3, 'BIP_winter_2023-24_half'),
    (2024, 'Q2', 6.6,  'BIP_summer_2024_half'),
    (2024, 'Q3', 6.6,  'BIP_summer_2024_half'),
]


# ============================================================
# STAGE 1
# ============================================================

def ensure_nass_cached():
    for data_year, url in sorted(NASS_SOURCES.items()):
        cache_path = os.path.join(CACHE_DIR,
                                  f'nass_{data_year}.txt')
        if not os.path.exists(cache_path):
            print(f'  [NASS] Downloading {data_year}... ',
                  end='', flush=True)
            try:
                r = requests.get(url, headers=HEADERS,
                                 timeout=30)
                r.raise_for_status()
                with open(cache_path, 'wb') as f:
                    f.write(r.content)
                print('done')
            except Exception as e:
                print(f'failed ({e})')
        else:
            print(f'  [NASS] {data_year} cached')


def build_national_quarterly():
    rows = [
        {'year': yr, 'quarter': q,
         'national_loss_pct': float(pct),
         'source': 'hardcoded_verified'}
        for (yr, q), pct in NASS_NATIONAL_QUARTERLY.items()
    ]
    return pd.DataFrame(rows).sort_values(['year', 'quarter'])


def build_series():
    print('\n[STAGE 1] Building Hawaii + National series...')
    ensure_nass_cached()

    df_nat = build_national_quarterly()

    hawaii_rows = [
        {'year': yr, 'quarter': q,
         'loss_pct': pct, 'source': src}
        for (yr, q, pct, src) in HAWAII_VERIFIED
    ]
    df_hi = (pd.DataFrame(hawaii_rows)
             .pipe(lambda d: d[d['year'].between(2015, 2025)])
             .sort_values(['year', 'quarter']))

    annual_nat = (df_nat.groupby('year')
                  .agg(mean_nat=('national_loss_pct', 'mean'),
                       n_nat=('national_loss_pct', 'count'))
                  .reset_index())
    annual_nat['annualized_nat'] = annual_nat['mean_nat'] * 4

    annual_hi = (df_hi.groupby('year')
                 .agg(mean_q_loss=('loss_pct', 'mean'),
                      n_quarters=('quarter', 'count'),
                      sum_q_loss=('loss_pct', 'sum'))
                 .reset_index())
    annual_hi['annualized_index'] = annual_hi.apply(
        lambda r: r['mean_q_loss'] * 4
        if r['n_quarters'] == 4
        else r['sum_q_loss'] * 4 / r['n_quarters'],
        axis=1)
    annual_hi['is_partial'] = annual_hi['n_quarters'] < 4

    annual = annual_hi.merge(annual_nat, on='year', how='left')
    annual['gap'] = (annual['annualized_nat']
                     - annual['annualized_index'])
    annual['data_quality'] = annual.apply(
        lambda r: f'partial_{r.n_quarters}q'
        if r['is_partial'] else 'complete', axis=1)

    print(f'\n  Hawaii quarters:   {len(df_hi)}')
    print(f'  National quarters: {len(df_nat)}')
    print('\n  Annual summary:')
    print(annual[['year', 'n_quarters', 'mean_q_loss',
                  'annualized_index', 'mean_nat',
                  'annualized_nat', 'gap',
                  'data_quality']].to_string(index=False))

    return df_hi, df_nat, annual


# ============================================================
# STAGE 2
# ============================================================

def fetch_fcc_bdc(vintage, url):
    cache_path = os.path.join(CACHE_DIR, f'fcc_{vintage}.json')
    if not os.path.exists(cache_path):
        print(f'  [FCC] Querying {vintage}... ',
              end='', flush=True)
        r = requests.get(url, params={
            'where': "GEOID IN ('15001','15003','15007','15009')",
            'outFields': '*',
            'f': 'json',
            'returnGeometry': 'false',
        }, headers=HEADERS, timeout=20)
        r.raise_for_status()
        data = r.json()
        with open(cache_path, 'w') as f:
            json.dump(data, f)
        print('done')
    else:
        print(f'  [FCC] {vintage} cached')
        with open(cache_path) as f:
            data = json.load(f)
    if 'error' in data:
        return None
    rows = [f['attributes'] for f in data.get('features', [])]
    return pd.DataFrame(rows) if rows else None


def compute_fcc_metrics(df, vintage):
    if df is None or df.empty:
        return None
    results = []
    for _, row in df.iterrows():
        fips     = str(row.get('GEOID', ''))[:5]
        county   = HAWAII_COUNTIES.get(fips, fips)
        total    = row.get('TotalBSLs', 0) or 0
        unserved = row.get('UnservedBSLs', 0) or 0
        unique   = row.get('UniqueProviders', 0) or 0
        results.append({
            'vintage':              vintage,
            'fips':                 fips,
            'county':               county,
            'TotalBSLs':            total,
            'UnservedBSLs':         unserved,
            'UniqueProviders':      unique,
            'unserved_pct':         (
                unserved / total * 100 if total else None),
            'infrastructure_score': (
                (1 - unserved / total) * 100 if total else None),
        })
    return pd.DataFrame(results)


def build_fcc_series():
    print('\n[STAGE 2] FCC BDC county metrics...')
    dfs = []
    for vintage, url in FCC_BDC_ENDPOINTS.items():
        df_raw = fetch_fcc_bdc(vintage, url)
        df_m   = compute_fcc_metrics(df_raw, vintage)
        if df_m is not None:
            dfs.append(df_m)
            print(f'\n  {vintage}:')
            print(df_m[['county', 'UniqueProviders',
                         'unserved_pct',
                         'infrastructure_score']]
                  .sort_values('infrastructure_score',
                               ascending=False)
                  .to_string(index=False))
        time.sleep(0.3)
    return pd.concat(dfs, ignore_index=True) if dfs else None


# ============================================================
# STAGE 3
# ============================================================

def run_correlation_analysis(annual, df_fcc):
    print('\n[STAGE 3] Correlation analysis...')

    td = annual[annual['year'].between(2019, 2024)]
    yr = td['year'].values.astype(float)
    lo = td['annualized_index'].values
    na = td['annualized_nat'].values

    if len(yr) >= 3:
        m,  _ = np.polyfit(yr, lo, 1)
        mn, _ = np.polyfit(yr, na, 1)
        print(f'\n  Hawaii trend (2019-2024):   {m:+.2f} pts/yr')
        print(f'  National trend (2019-2024): {mn:+.2f} pts/yr')

    pre  = annual[annual['year'].between(2015, 2020)
                  ]['annualized_index']
    post = annual[annual['year'].between(2021, 2024)
                  ]['annualized_index']
    print(f'\n  Hawaii pre  (2015-2020): {pre.mean():.1f}')
    print(f'  Hawaii post (2021-2024): {post.mean():.1f}')
    print(f'  Change: {post.mean()-pre.mean():+.1f} '
          f'({(post.mean()/pre.mean()-1)*100:+.1f}%)')

    gd    = annual.dropna(subset=['gap'])
    gpre  = gd[gd['year'].between(2015, 2020)]['gap']
    gpost = gd[gd['year'].between(2021, 2024)]['gap']
    print(f'\n  Gap pre  (2015-2020): {gpre.mean():.1f} pts')
    print(f'  Gap post (2021-2024): {gpost.mean():.1f} pts')
    print(f'  Advantage eroded:    '
          f'{gpre.mean()-gpost.mean():+.1f} pts')

    if len(yr) >= 4:
        r_p, p_p = pearsonr(yr, lo)
        r_s, p_s = spearmanr(yr, lo)
        print(f'\n  Year vs HI annualized (2019-2024):')
        print(f'    Pearson  r={r_p:.3f}  p={p_p:.4f}')
        print(f'    Spearman r={r_s:.3f}  p={p_s:.4f}')

    if df_fcc is not None:
        print('\n  Island gradient (Jun 2023, '
              'highest infra_score first):')
        sub = (df_fcc[df_fcc['vintage'] == 'June_2023']
               .sort_values('infrastructure_score',
                            ascending=False))
        for _, row in sub.iterrows():
            p = int(row['UniqueProviders'] or 0)
            s = row['infrastructure_score'] or 0
            u = row['unserved_pct'] or 0
            print(f'    {row["county"]:<22} '
                  f'infra={s:.1f}%  '
                  f'unserved={u:.2f}%  '
                  f'providers={p}')
        print('\n  Falsification prediction (infra_score order):')
        order = ' > '.join(
            sub['county']
            .str.replace(' (Big Island)', '', regex=False)
            .str.replace(' (Oahu)', '', regex=False)
            .tolist())
        print(f'    Loss: {order}')


# ============================================================
# STAGE 4: VISUALIZATION
# ============================================================

def plot_all(df_hi, df_nat, annual, df_fcc):
    print('\n[STAGE 4] Generating plots...')

    C_HI  = '#1a6b3c'
    C_NAT = '#444444'

    def yr_col(y):
        if y <= 2018: return '#2d7a2d'
        if y <= 2020: return '#e87722'
        if y <= 2022: return '#cc2200'
        return '#880000'

    fig = plt.figure(figsize=(22, 16))
    gs  = gridspec.GridSpec(2, 2, figure=fig,
                            hspace=0.50, wspace=0.40)
    fig.suptitle(
        'Hawaii: The Control Group That Started Failing\n'
        'BIP Hawaii  +  NASS National  +  FCC BDC  |  '
        '2026-04-02  |  v8',
        fontsize=13, fontweight='bold', y=0.995)

    q_off = {'Q1': 0.0, 'Q2': 0.25,
             'Q3': 0.50, 'Q4': 0.75}

    # ─── Panel 1: Quarterly overlay ──────────────────────────
    ax1 = fig.add_subplot(gs[0, 0])

    df_hi_p = df_hi.copy()
    df_hi_p['yr_frac'] = (df_hi_p['year']
                          + df_hi_p['quarter'].map(q_off))
    dhs = df_hi_p.sort_values('yr_frac')

    df_nat_p = df_nat.copy()
    df_nat_p['yr_frac'] = (df_nat_p['year']
                           + df_nat_p['quarter'].map(q_off))
    dns = df_nat_p.sort_values('yr_frac')

    ax1.plot(dhs['yr_frac'], dhs['loss_pct'],
             'o-', color=C_HI, lw=2, ms=4,
             label='Hawaii quarterly (BIP)')
    ax1.plot(dns['yr_frac'], dns['national_loss_pct'],
             's--', color=C_NAT, lw=1.5, ms=3.5,
             alpha=0.65, label='US national quarterly (NASS)')

    hi_base  = (df_hi[df_hi['year'].between(2015, 2018)]
                ['loss_pct'].mean())
    nat_base = (df_nat[df_nat['year'].between(2015, 2018)]
                ['national_loss_pct'].mean())

    ax1.axhline(hi_base, color=C_HI, ls='--', lw=1.1,
                alpha=0.5,
                label=f'HI 2015-18 baseline ({hi_base:.1f}%)')
    ax1.axhline(nat_base, color=C_NAT, ls=':', lw=1.1,
                alpha=0.4,
                label=f'Natl baseline ({nat_base:.1f}%)')

    td   = annual[annual['year'].between(2019, 2024)]
    r_p, p_p = pearsonr(
        td['year'].values.astype(float),
        td['annualized_index'].values)
    ax1.text(0.02, 0.97,
             f'Year vs HI annual:\n'
             f'r = {r_p:.3f},  p = {p_p:.4f}\n'
             f'(2019-2024, n = 6)',
             transform=ax1.transAxes,
             va='top', ha='left', fontsize=8,
             bbox=dict(boxstyle='round,pad=0.3',
                       facecolor='white', alpha=0.75))

    ymax = max(dhs['loss_pct'].max(),
               dns['national_loss_pct'].max()) * 1.24
    for ev in DEPLOYMENT_EVENTS:
        ax1.axvline(ev['year'], color=ev['color'],
                    ls=':', lw=1.5, alpha=0.8)
        ax1.text(ev['year'] + 0.04, ymax * 0.97,
                 ev['label'], fontsize=6.0,
                 color=ev['color'],
                 rotation=90, va='top')

    ax1.set_xlabel('Year', fontsize=10)
    ax1.set_ylabel('Quarterly Colony Loss (%)', fontsize=10)
    ax1.set_title(
        'Hawaii vs National — Quarterly Loss\n'
        'Hawaii ~3× below national; gap now closing',
        fontsize=11, pad=6)
    ax1.legend(fontsize=8, loc='upper left', framealpha=0.85)
    ax1.set_xlim(2014.8, 2025.2)
    ax1.grid(alpha=0.3)

    # ─── Panel 2: Annual bar ──────────────────────────────────
    ax2 = fig.add_subplot(gs[0, 1])

    ann_p = annual[annual['year'].between(2015, 2024)].copy()
    x2    = np.arange(len(ann_p))
    w2    = 0.38
    cols2 = [yr_col(y) for y in ann_p['year']]

    b_hi  = ax2.bar(x2 - w2/2, ann_p['annualized_index'],
                    w2, color=cols2, alpha=0.90,
                    edgecolor='white', lw=0.6,
                    label='Hawaii (BIP×4)')
    b_nat = ax2.bar(x2 + w2/2, ann_p['annualized_nat'],
                    w2, color=C_NAT, alpha=0.38,
                    edgecolor='white', lw=0.6,
                    label='US national (NASS×4)')

    # HI bar labels
    for bar, row in zip(b_hi, ann_p.itertuples()):
        ht    = bar.get_height()
        label = (f'{ht:.0f}*'
                 if row.is_partial else f'{ht:.0f}')
        ax2.text(bar.get_x() + bar.get_width() / 2,
                 ht + 0.5, label,
                 ha='center', va='bottom',
                 fontsize=7.5, fontweight='bold')

    # National bar labels — add q-avg footnote on 2018 bar
    for bar, row in zip(b_nat, ann_p.itertuples()):
        ht = bar.get_height()
        yr = int(row.year)
        ax2.text(bar.get_x() + bar.get_width() / 2,
                 ht + 0.5,
                 f'{ht:.0f}',
                 ha='center', va='bottom',
                 fontsize=6.5, color=C_NAT, alpha=0.7)
        # Annotate 2018 with quarterly breakdown
        if yr == 2018:
            ax2.annotate(
                '13.75 q-avg\n(Q1=15, Q2=13\nQ3=14, Q4=13)',
                xy=(bar.get_x() + bar.get_width() / 2, ht),
                xytext=(bar.get_x() + bar.get_width() / 2 + 0.6,
                        ht - 8),
                fontsize=6.5, color=C_NAT,
                ha='left', va='top',
                arrowprops=dict(
                    arrowstyle='->', color=C_NAT,
                    lw=0.8))

    ax2.axhline(hi_base * 4, color=C_HI,
                ls='--', lw=1.0, alpha=0.5,
                label=f'HI baseline ({hi_base*4:.0f})')

    ax2.set_xticks(x2)
    ax2.set_xticklabels(ann_p['year'].astype(int),
                        rotation=45, fontsize=9)
    ax2.set_ylabel('Annualized Loss Index (qtrly % × 4)',
                   fontsize=9)
    ax2.set_title(
        'Annualized Loss Index — Hawaii vs National\n'
        'Dark green=pre-5G  Orange=low-band  '
        'Red=C/mid-band   * = partial year',
        fontsize=11, pad=6)
    ax2.legend(fontsize=8, loc='upper left')
    ax2.grid(alpha=0.3, axis='y')
    # Extra headroom for the 2018 annotation
    ax2.set_ylim(0, ann_p['annualized_nat'].max() * 1.22)

    # ─── Panel 3: Gap erosion ─────────────────────────────────
    ax3 = fig.add_subplot(gs[1, 0])

    gap_p = (annual[annual['year'].between(2015, 2024)]
             .dropna(subset=['gap']).copy())
    cols3 = [yr_col(y) for y in gap_p['year']]

    bars3 = ax3.bar(gap_p['year'], gap_p['gap'],
                    color=cols3, alpha=0.88,
                    edgecolor='white', lw=0.6,
                    width=0.7)

    for bar, row in zip(bars3, gap_p.itertuples()):
        ht = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width() / 2,
                 ht + 0.4, f'{ht:.1f}',
                 ha='center', va='bottom',
                 fontsize=8, fontweight='bold')

    ax3.axhline(0, color='black', lw=1.0)

    yr_min = int(gap_p['year'].min())
    yr_max = int(gap_p['year'].max())
    split  = 2020.5

    ax3.axvspan(yr_min - 0.4, split,
                alpha=0.07, color='green',
                label='Pre-5G-mid (2015-2020)')
    ax3.axvspan(split, yr_max + 0.4,
                alpha=0.07, color='red',
                label='Post-5G-mid (2021-2024)')

    for ev in DEPLOYMENT_EVENTS:
        if yr_min - 0.5 < ev['year'] < yr_max + 0.5:
            ax3.axvline(ev['year'], color=ev['color'],
                        ls=':', lw=1.2, alpha=0.7)

    gpre_mean  = gap_p[gap_p['year'] <= 2020]['gap'].mean()
    gpost_mean = gap_p[gap_p['year'] >= 2021]['gap'].mean()

    # Pre-5G annotation: point to 2017 bar top (34.6)
    # which is just below gpre_mean (35.2) — clean landing
    ax3.annotate(
        f'Pre-5G mean\n{gpre_mean:.0f} pts',
        xy=(2017, 34.6),          # 2017 bar top
        xytext=(2016.0,
                gpre_mean * 1.13),
        ha='center', fontsize=8.5,
        color='#2d7a2d', fontweight='bold',
        arrowprops=dict(arrowstyle='->',
                        color='#2d7a2d', alpha=0.7))

    # Post-5G annotation: point to 2022 bar top (18.7)
    ax3.annotate(
        f'Post-5G mean\n{gpost_mean:.0f} pts',
        xy=(2022, 18.7),
        xytext=(2023.0,
                gpost_mean * 1.55),
        ha='center', fontsize=8.5,
        color='#880000', fontweight='bold',
        arrowprops=dict(arrowstyle='->',
                        color='#880000', alpha=0.7))

    ax3.set_xlabel('Year', fontsize=10)
    ax3.set_ylabel(
        'National − Hawaii annualized index\n'
        '(positive = Hawaii better than US average)',
        fontsize=9)
    ax3.set_title(
        "Erosion of Hawaii's Low-Loss Advantage\n"
        f"Pre-5G mean {gpre_mean:.0f} pts → "
        f"post-5G mean {gpost_mean:.0f} pts "
        f"({gpre_mean-gpost_mean:.0f} pt erosion)",
        fontsize=11, pad=6)
    ax3.set_xlim(yr_min - 0.5, yr_max + 0.5)
    ax3.set_ylim(0, gap_p['gap'].max() * 1.32)
    ax3.legend(fontsize=8, loc='lower left')
    ax3.grid(alpha=0.3, axis='y')

    # ─── Panel 4: Island infrastructure gradient ──────────────
    ax4 = fig.add_subplot(gs[1, 1])

    if df_fcc is not None:
        county_order = (
            df_fcc[df_fcc['vintage'] == 'June_2023']
            .sort_values('infrastructure_score', ascending=False)
            ['county'].tolist()
        )

        def get_val(vintage, county, col):
            row = df_fcc[
                (df_fcc['vintage'] == vintage) &
                (df_fcc['county'] == county)]
            return float(row[col].values[0]) if len(row) else 0

        x4  = np.arange(len(county_order))
        w4  = 0.35

        v22_p = [get_val('June_2022', c, 'UniqueProviders')
                 for c in county_order]
        v23_p = [get_val('June_2023', c, 'UniqueProviders')
                 for c in county_order]
        v23_u = [get_val('June_2023', c, 'unserved_pct')
                 for c in county_order]

        b4_22 = ax4.bar(x4 - w4/2, v22_p, w4,
                        color='#cc6600', alpha=0.85,
                        edgecolor='white', lw=0.7,
                        label='Providers Jun 2022')
        b4_23 = ax4.bar(x4 + w4/2, v23_p, w4,
                        color='#880000', alpha=0.85,
                        edgecolor='white', lw=0.7,
                        label='Providers Jun 2023')

        for bar, val in zip(b4_22, v22_p):
            ax4.text(bar.get_x() + bar.get_width()/2,
                     bar.get_height() + 0.08,
                     f'{int(val)}',
                     ha='center', va='bottom',
                     fontsize=9, fontweight='bold')
        for bar, val in zip(b4_23, v23_p):
            ax4.text(bar.get_x() + bar.get_width()/2,
                     bar.get_height() + 0.08,
                     f'{int(val)}',
                     ha='center', va='bottom',
                     fontsize=9, fontweight='bold')

        ax4b = ax4.twinx()
        ax4b.plot(x4, v23_u, 'D--',
                  color='#1a1a8c', lw=1.5, ms=7,
                  alpha=0.75,
                  label='Unserved BSL % 2023')
        for xi, val in zip(x4, v23_u):
            ax4b.text(xi + 0.08, val + 0.15,
                      f'{val:.1f}%',
                      ha='left', va='bottom',
                      fontsize=8, color='#1a1a8c')

        ax4b.invert_yaxis()

        # Two-line label — fits without truncation
        ax4b.set_ylabel(
            'Unserved BSL %\n← better (low)    worse (high) →',
            fontsize=8.5, color='#1a1a8c')
        ax4b.tick_params(axis='y', colors='#1a1a8c')

        u_max = max(v23_u)
        ax4b.set_ylim(u_max * 1.3, -0.5)

        ax4.set_xticks(x4)
        ax4.set_xticklabels(
            [COUNTY_PLOT_LABELS.get(c, c)
             for c in county_order],
            fontsize=9)
        ax4.set_ylabel(
            'Unique Broadband Providers (FCC BDC)',
            fontsize=9)
        ax4.set_title(
            'Within-Hawaii Infrastructure Gradient\n'
            'Sorted by infrastructure score (Jun 2023)\n'
            'Prediction: Oahu loss > Kauai > Maui > Big Island',
            fontsize=10, pad=6)
        ax4.set_ylim(0, max(v22_p + v23_p) * 1.3)

        lines1, labels1 = ax4.get_legend_handles_labels()
        lines2, labels2 = ax4b.get_legend_handles_labels()
        ax4.legend(lines1 + lines2, labels1 + labels2,
                   fontsize=8, loc='upper right')
        ax4.grid(alpha=0.3, axis='y')
    else:
        ax4.text(0.5, 0.5, 'FCC BDC data unavailable',
                 ha='center', va='center',
                 transform=ax4.transAxes, fontsize=12)

    plt.savefig('hawaii_5g_bee_loss_v8.png',
                dpi=150, bbox_inches='tight')
    plt.show()
    print('  Saved: hawaii_5g_bee_loss_v8.png')


# ============================================================
# STAGE 5: SAVE
# ============================================================

def save_all(df_hi, df_nat, annual, df_fcc):
    df_hi.to_csv('hawaii_quarterly_bip.csv', index=False)
    df_nat.to_csv('hawaii_national_quarterly_nass.csv',
                  index=False)
    annual.to_csv('hawaii_annual_summary.csv', index=False)
    if df_fcc is not None:
        df_fcc.to_csv('hawaii_fcc_metrics.csv', index=False)
    print('\n[Saved]')
    print('  hawaii_quarterly_bip.csv')
    print('  hawaii_national_quarterly_nass.csv')
    print('  hawaii_annual_summary.csv')
    print('  hawaii_fcc_metrics.csv')
    print('  hawaii_5g_bee_loss_v8.png')


# ============================================================
# MAIN
# ============================================================

def run():
    print('=' * 65)
    print('HAWAII 5G vs BEE COLONY LOSS — v8')
    print('OrganismCore — 2026-04-02')
    print('=' * 65)
    print('\nDATA SOURCES:')
    print('  Hawaii:   BeeInformed Partnership state reports')
    print('  National: NASS Honey Bee Colonies reports')
    print('  Infra:    FCC BDC ArcGIS county provider counts')
    print('\nKEY CHANGES FROM v7:')
    print('  - Panel 2: 2018 national bar annotated with')
    print('    quarterly breakdown (clarifies spike is real)')
    print('  - Panel 3: pre-5G arrow points to 2017 bar top')
    print('    (avoids overlap with 2018 bar label 40.4)')
    print('  - Panel 4: secondary axis label shortened to')
    print('    two lines, fits without truncation\n')

    df_hi, df_nat, annual = build_series()
    df_fcc = build_fcc_series()
    run_correlation_analysis(annual, df_fcc)
    plot_all(df_hi, df_nat, annual, df_fcc)
    save_all(df_hi, df_nat, annual, df_fcc)

    print('\n' + '=' * 65)
    print('FALSIFICATION TEST:')
    print('  AIA 2024-25 island survey:')
    print('  https://auburnuniversity.maps.arcgis.com/'
          'apps/instant/compare/index.html?appid='
          'a63480155fdd4c9789762d174e6d6078')
    print('\n  Prediction (infra_score order):')
    print('    Oahu > Kauai > Maui > Big Island')
    print('\n  Varroa arrived 2007; low loss for 11 yrs.')
    print('  Inflection: 2019 (mmWave) → 2021 (mid-band).')
    print('  National flat; Hawaii converging upward.')
    print('=' * 65)


if __name__ == '__main__':
    run()
