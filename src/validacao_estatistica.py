# validacao_estatistica.py
# Validacao rigorosa da base e dos indicadores — 5 etapas
# Saida: output_validacao.json + figuras
# encoding: utf-8

import json
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

warnings.filterwarnings('ignore')

df = pd.read_csv('../data/PEDE_PASSOS_DATASET_FIAP.csv', delimiter=';')

ANOS       = [2020, 2021, 2022]
INDICADORES = ['IAN', 'IDA', 'IEG', 'IAA', 'IPS', 'IPP', 'IPV', 'INDE']
PEDRA_NIVEL = {'Quartzo': 0, '\u00c1gata': 1, 'Ametista': 2, 'Top\u00e1zio': 3}

resultados = {}

SEP = '=' * 70

# =========================================================================
# ETAPA 1 — Validacao da Base de Dados
# =========================================================================
print(SEP)
print('ETAPA 1 — VALIDACAO DA BASE DE DADOS')
print(SEP)

etapa1 = {}

# 1a. Dimensoes e cobertura por ano
print('\n[1a] Cobertura por ano (alunos com INDE nao nulo):')
cobertura = {}
for ano in ANOS:
    col = f'INDE_{ano}'
    n = int(df[col].notna().sum()) if col in df.columns else 0
    cobertura[ano] = n
    print(f'  {ano}: {n} alunos')
etapa1['cobertura_por_ano'] = cobertura

# 1b. Valores unicos por indicador (detectar discretizacao)
print('\n[1b] Valores unicos por indicador (todos os anos):')
valores_unicos = {}
for ind in INDICADORES:
    unicos_por_ano = {}
    for ano in ANOS:
        col = f'{ind}_{ano}'
        if col in df.columns:
            vals = pd.to_numeric(df[col], errors='coerce').dropna().unique()
            unicos_por_ano[ano] = sorted([round(float(v), 4) for v in vals])
    valores_unicos[ind] = unicos_por_ano
    n_max = max(len(v) for v in unicos_por_ano.values()) if unicos_por_ano else 0
    alerta = ' <-- DISCRETO' if n_max <= 5 else ''
    print(f'  {ind}: max {n_max} valores unicos{alerta}')
    if n_max <= 5:
        for ano, vals in unicos_por_ano.items():
            print(f'       {ano}: {vals}')
etapa1['valores_unicos'] = {
    ind: {str(ano): vals for ano, vals in anos.items()}
    for ind, anos in valores_unicos.items()
}

# 1c. NaN por indicador e ano
print('\n[1c] Percentual de NaN por indicador e ano:')
nan_pct = {}
header = f"{'Indicador':<8}" + ''.join(f'{ano:>10}' for ano in ANOS)
print(header)
print('-' * (8 + 10 * len(ANOS)))
for ind in INDICADORES:
    row_str = f'{ind:<8}'
    nan_pct[ind] = {}
    for ano in ANOS:
        col = f'{ind}_{ano}'
        if col in df.columns:
            pct = round(df[col].isna().mean() * 100, 1)
            nan_pct[ind][ano] = pct
            row_str += f'{pct:>9.1f}%'
        else:
            nan_pct[ind][ano] = None
            row_str += f'{"N/A":>10}'
    print(row_str)
etapa1['nan_pct'] = {ind: {str(ano): v for ano, v in anos.items()} for ind, anos in nan_pct.items()}

# 1d. NaN sistematico ou aleatorio? (correlacao entre missings)
print('\n[1d] NaN sistematico: alunos sem INDE_2020 tem mais NaN em outros anos?')
for ind in ['INDE', 'IDA', 'IEG']:
    col_ref = f'{ind}_2020'
    col_tgt = f'{ind}_2022'
    if col_ref in df.columns and col_tgt in df.columns:
        tem_2020 = df[col_ref].notna()
        n_com    = df[tem_2020][col_tgt].notna().sum()
        n_sem    = df[~tem_2020][col_tgt].notna().sum()
        tot_com  = tem_2020.sum()
        tot_sem  = (~tem_2020).sum()
        print(f'  {ind}: com dado em 2020 -> {n_com}/{tot_com} tem 2022 ({n_com/tot_com*100:.1f}%)')
        print(f'         sem dado em 2020 -> {n_sem}/{tot_sem} tem 2022 ({n_sem/tot_sem*100:.1f}% if tot_sem>0 else 0)')

# 1e. Consistencia do INDE: sera que e combinacao linear dos componentes?
print('\n[1e] Consistencia do INDE — R² da regressao INDE ~ IDA+IEG+IAN+IAA+IPS+IPP+IPV (2022):')
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

for ano in ANOS:
    feat_inde = [f'{ind}_{ano}' for ind in ['IDA', 'IEG', 'IAN', 'IAA', 'IPS', 'IPP', 'IPV']]
    tgt_inde  = f'INDE_{ano}'
    cols_ok   = [c for c in feat_inde if c in df.columns] + ([tgt_inde] if tgt_inde in df.columns else [])
    tmp = df[cols_ok].apply(pd.to_numeric, errors='coerce').dropna()
    if len(tmp) > 20 and tgt_inde in tmp.columns:
        X_ = tmp[[c for c in feat_inde if c in tmp.columns]]
        y_ = tmp[tgt_inde]
        lr = LinearRegression().fit(X_, y_)
        r2 = r2_score(y_, lr.predict(X_))
        coefs_inde = dict(zip(X_.columns, lr.coef_.round(4)))
        print(f'  {ano}: R²={r2:.4f}  intercept={lr.intercept_:.3f}')
        print(f'       Pesos: {coefs_inde}')
etapa1['inde_r2_por_ano'] = 'ver saida acima'

# 1f. Distribuicao de Pedras por ano
print('\n[1f] Distribuicao de Pedras por ano:')
pedra_dist = {}
for ano in ANOS:
    col = f'PEDRA_{ano}'
    if col in df.columns:
        dist = df[col].value_counts().to_dict()
        pedra_dist[ano] = {str(k): int(v) for k, v in dist.items()}
        print(f'  {ano}: {pedra_dist[ano]}')
etapa1['distribuicao_pedras'] = {str(k): v for k, v in pedra_dist.items()}

resultados['etapa1_base'] = etapa1

# =========================================================================
# ETAPA 2 — Analise Estatistica por Indicador
# =========================================================================
print(f'\n{SEP}')
print('ETAPA 2 — ANALISE ESTATISTICA POR INDICADOR')
print(SEP)

etapa2 = {}

for ind in INDICADORES:
    etapa2[ind] = {}
    print(f'\n--- {ind} ---')
    print(f"{'Ano':>5} {'n':>5} {'Media':>7} {'DP':>7} {'Min':>6} {'Q1':>6} {'Med':>6} {'Q3':>6} {'Max':>6} {'Skew':>7} {'Kurt':>7} {'Norm-p':>8}")
    print('-' * 90)
    for ano in ANOS:
        col = f'{ind}_{ano}'
        if col not in df.columns:
            continue
        s = pd.to_numeric(df[col], errors='coerce').dropna()
        if len(s) < 10:
            continue
        n    = len(s)
        mean = s.mean()
        std  = s.std()
        mn   = s.min()
        q1   = s.quantile(0.25)
        med  = s.median()
        q3   = s.quantile(0.75)
        mx   = s.max()
        skew = s.skew()
        kurt = s.kurtosis()

        # Teste de normalidade (Shapiro se n<=5000, KS se maior)
        if n <= 5000:
            _, p_norm = stats.shapiro(s.sample(min(n, 5000), random_state=42))
        else:
            _, p_norm = stats.kstest(s, 'norm', args=(mean, std))

        # Outliers pelo metodo IQR
        iqr   = q3 - q1
        lim_inf = q1 - 1.5 * iqr
        lim_sup = q3 + 1.5 * iqr
        n_out   = int(((s < lim_inf) | (s > lim_sup)).sum())

        etapa2[ind][ano] = {
            'n': n, 'mean': round(mean, 4), 'std': round(std, 4),
            'min': round(mn, 4), 'q1': round(q1, 4), 'median': round(med, 4),
            'q3': round(q3, 4), 'max': round(mx, 4),
            'skew': round(skew, 4), 'kurtosis': round(kurt, 4),
            'p_normalidade': round(float(p_norm), 6),
            'normal': bool(p_norm > 0.05),
            'n_outliers_iqr': n_out,
            'pct_outliers': round(n_out / n * 100, 1),
        }
        norm_flag = 'SIM' if p_norm > 0.05 else 'NAO'
        print(f'{ano:>5} {n:>5} {mean:>7.3f} {std:>7.3f} {mn:>6.2f} {q1:>6.2f} {med:>6.2f} {q3:>6.2f} {mx:>6.2f} {skew:>7.3f} {kurt:>7.3f} {p_norm:>8.4f} ({norm_flag}) out={n_out}')

resultados['etapa2_estatistica'] = etapa2

# =========================================================================
# ETAPA 3 — Correlacoes com Rigor (Pearson + Spearman + p-values)
# =========================================================================
print(f'\n{SEP}')
print('ETAPA 3 — CORRELACOES COM RIGOR')
print(SEP)

etapa3 = {}

# 3a. Correlacao de cada indicador com INDE — Pearson E Spearman com p-value
print('\n[3a] Correlacao com INDE (Pearson e Spearman) por ano:')
corr_com_inde = {}
for ind in ['IAN', 'IDA', 'IEG', 'IAA', 'IPS', 'IPP', 'IPV']:
    corr_com_inde[ind] = {}
    print(f'\n  {ind}:')
    print(f"  {'Ano':>5} {'Pearson-r':>11} {'p-val':>10} {'Spearman-r':>12} {'p-val':>10} {'Sig':>5}")
    print(f'  {"-"*55}')
    for ano in ANOS:
        col_ind  = f'{ind}_{ano}'
        col_inde = f'INDE_{ano}'
        if col_ind not in df.columns or col_inde not in df.columns:
            continue
        tmp = df[[col_ind, col_inde]].apply(pd.to_numeric, errors='coerce').dropna()
        if len(tmp) < 10:
            continue
        pr, pp = stats.pearsonr(tmp[col_ind], tmp[col_inde])
        sr, sp = stats.spearmanr(tmp[col_ind], tmp[col_inde])
        sig = '***' if min(pp, sp) < 0.001 else ('**' if min(pp, sp) < 0.01 else ('*' if min(pp, sp) < 0.05 else 'ns'))
        corr_com_inde[ind][ano] = {
            'pearson_r': round(pr, 4), 'pearson_p': round(float(pp), 6),
            'spearman_r': round(sr, 4), 'spearman_p': round(float(sp), 6),
            'significativo': sig,
        }
        print(f'  {ano:>5} {pr:>11.4f} {pp:>10.6f} {sr:>12.4f} {sp:>10.6f} {sig:>5}')
etapa3['corr_com_inde'] = corr_com_inde

# 3b. Correlacao entre indicadores (2022) — Spearman + p-value
print('\n[3b] Correlacao entre indicadores (Spearman, 2022):')
inds_2022 = [f'{ind}_2022' for ind in INDICADORES if f'{ind}_2022' in df.columns]
df_2022   = df[inds_2022].apply(pd.to_numeric, errors='coerce').dropna()
df_2022.columns = [c.replace('_2022', '') for c in df_2022.columns]

n_inds = len(df_2022.columns)
corr_matrix_sp = pd.DataFrame(index=df_2022.columns, columns=df_2022.columns, dtype=float)
pval_matrix_sp = pd.DataFrame(index=df_2022.columns, columns=df_2022.columns, dtype=float)

for c1 in df_2022.columns:
    for c2 in df_2022.columns:
        if c1 == c2:
            corr_matrix_sp.loc[c1, c2] = 1.0
            pval_matrix_sp.loc[c1, c2] = 0.0
        else:
            r, p = stats.spearmanr(df_2022[c1], df_2022[c2])
            corr_matrix_sp.loc[c1, c2] = round(r, 3)
            pval_matrix_sp.loc[c1, c2] = round(float(p), 6)

print(corr_matrix_sp.to_string())
print('\nPares com correlacao forte (|r|>0.6) e significativa (p<0.01):')
pares_fortes = []
for c1 in df_2022.columns:
    for c2 in df_2022.columns:
        if c1 >= c2:
            continue
        r = float(corr_matrix_sp.loc[c1, c2])
        p = float(pval_matrix_sp.loc[c1, c2])
        if abs(r) > 0.6 and p < 0.01:
            pares_fortes.append({'par': f'{c1}-{c2}', 'r': r, 'p': p})
            print(f'  {c1}-{c2}: r={r:.3f}  p={p:.6f}')

etapa3['corr_spearman_2022'] = corr_matrix_sp.to_dict()
etapa3['pval_spearman_2022'] = pval_matrix_sp.to_dict()
etapa3['pares_fortes'] = pares_fortes

# 3c. IPP — investigar o salto de correlacao com INDE (2020 vs 2021)
print('\n[3c] IPP — investigar salto de correlacao 2020->2021:')
for ano in ANOS:
    col_ipp  = f'IPP_{ano}'
    col_inde = f'INDE_{ano}'
    if col_ipp in df.columns and col_inde in df.columns:
        s_ipp  = pd.to_numeric(df[col_ipp], errors='coerce')
        s_inde = pd.to_numeric(df[col_inde], errors='coerce')
        n_validos = s_ipp.notna() & s_inde.notna()
        vals_unicos_ipp = sorted(s_ipp.dropna().unique())
        print(f'  {ano}: n={n_validos.sum()}  |  valores IPP: {[round(v,2) for v in vals_unicos_ipp[:10]]}{"..." if len(vals_unicos_ipp)>10 else ""}')
        if len(vals_unicos_ipp) <= 5:
            print(f'       ALERTA: IPP_{ano} e discreto com {len(vals_unicos_ipp)} valores — Pearson pode ser enganoso')
etapa3['ipp_investigacao'] = 'ver saida acima'

# 3d. IPS_2020 — investigar coeficiente positivo no modelo
print('\n[3d] IPS_2020 — correlacao com defasagem (IAN_2022 < 10):')
if 'IPS_2020' in df.columns and 'IAN_2022' in df.columns:
    tmp_ips = df[['IPS_2020', 'IAN_2022']].apply(pd.to_numeric, errors='coerce').dropna()
    tmp_ips['DEFASAGEM'] = (tmp_ips['IAN_2022'] < 10).astype(int)
    r_pb, p_pb = stats.pointbiserialr(tmp_ips['DEFASAGEM'], tmp_ips['IPS_2020'])
    print(f'  Point-biserial r(IPS_2020, DEFASAGEM_2022) = {r_pb:.4f}  p={p_pb:.6f}')
    print(f'  Media IPS_2020 | Defasado={tmp_ips[tmp_ips["DEFASAGEM"]==1]["IPS_2020"].mean():.3f}  |  Adequado={tmp_ips[tmp_ips["DEFASAGEM"]==0]["IPS_2020"].mean():.3f}')
    etapa3['ips2020_investigacao'] = {
        'r_pointbiserial': round(r_pb, 4), 'p': round(float(p_pb), 6),
        'media_defasado': round(tmp_ips[tmp_ips['DEFASAGEM']==1]['IPS_2020'].mean(), 3),
        'media_adequado': round(tmp_ips[tmp_ips['DEFASAGEM']==0]['IPS_2020'].mean(), 3),
    }

resultados['etapa3_correlacoes'] = etapa3

# =========================================================================
# ETAPA 5 — Coerencia Interna
# =========================================================================
print(f'\n{SEP}')
print('ETAPA 5 — COERENCIA INTERNA')
print(SEP)

etapa5 = {}

# 5a. IDA+IEG dominam INDE (P8) — bate com importancia no modelo (P9)?
print('\n[5a] Consistencia P8 vs P9: IDA+IEG dominam INDE E o modelo?')
# Carrega feature importance do output_p9.json se existir
import os
if os.path.exists('output_p9.json'):
    with open('output_p9.json', encoding='utf-8') as f:
        p9_data = json.load(f)
    fi = p9_data.get('feature_importance_rf', {})
    print('  Top 5 features (RF):')
    for feat, imp in list(fi.items())[:5]:
        print(f'    {feat}: {imp:.4f}')
    ida_ieg_top = any('IDA' in k or 'IEG' in k for k in list(fi.keys())[:3])
    print(f'  IDA ou IEG no top 3? {"SIM" if ida_ieg_top else "NAO — INCONSISTENCIA"}')
    etapa5['p8_vs_p9_consistente'] = ida_ieg_top
else:
    print('  output_p9.json nao encontrado — rode p9_modelo.py primeiro')

# 5b. Tese INDICADO_BOLSA: IEG e o principal diferenciador?
print('\n[5b] Tese mobilidade: IEG diferencia indicados mais que IDA?')
if os.path.exists('output_p11.json'):
    with open('output_p11.json', encoding='utf-8') as f:
        p11_data = json.load(f)
    ranking = p11_data.get('insight6_mobilidade', {}).get('ranking_diferenca', [])
    if ranking:
        print('  Ranking de diferenca (Indicado Sim - Nao):')
        for entry in ranking:
            print(f'    {entry["indicador"]}: {entry["dif"]:+.3f}')
        top1 = ranking[0]['indicador']
        ieg_pos = next((i for i, e in enumerate(ranking) if e['indicador'] == 'IEG'), None)
        ida_pos = next((i for i, e in enumerate(ranking) if e['indicador'] == 'IDA'), None)
        print(f'\n  IEG posicao: {ieg_pos+1 if ieg_pos is not None else "N/A"}')
        print(f'  IDA posicao: {ida_pos+1 if ida_pos is not None else "N/A"}')
        tese_ok = ieg_pos is not None and ida_pos is not None and ieg_pos <= ida_pos
        print(f'  Tese sustentada (IEG >= IDA)? {"SIM" if tese_ok else "NAO — REVISAR TESE"}')
        etapa5['tese_mobilidade_ieg_vs_ida'] = {
            'ieg_posicao': ieg_pos + 1 if ieg_pos is not None else None,
            'ida_posicao': ida_pos + 1 if ida_pos is not None else None,
            'tese_sustentada': bool(tese_ok),
        }
else:
    print('  output_p11.json nao encontrado — rode p11_insights.py primeiro')

# 5c. INDE discrimina Pedras? (teste estatistico formal — Kruskal-Wallis)
print('\n[5c] Kruskal-Wallis: INDE_2022 difere significativamente entre Pedras?')
pedra_col  = 'PEDRA_2022'
inde_col   = 'INDE_2022'
df_kw      = df[[pedra_col, inde_col]].copy()
df_kw[inde_col] = pd.to_numeric(df_kw[inde_col], errors='coerce')
df_kw      = df_kw.dropna()
grupos_kw  = [df_kw[df_kw[pedra_col] == p][inde_col].values
              for p in ['\u00c1gata', 'Quartzo', 'Ametista', 'Top\u00e1zio']
              if p in df_kw[pedra_col].unique()]
if len(grupos_kw) >= 2:
    H, p_kw = stats.kruskal(*grupos_kw)
    print(f'  H={H:.2f}  p={p_kw:.8f}  {"*** SIGNIFICATIVO" if p_kw < 0.001 else "nao significativo"}')
    etapa5['kruskal_wallis_inde_pedra'] = {'H': round(H, 4), 'p': round(float(p_kw), 8)}

# 5d. ANOS_PM: relacao com INDE e monotonica? (Spearman)
print('\n[5d] ANOS_PM x INDE_2022 — relacao monotonica?')
anos_pm_col = None
for col in df.columns:
    if 'ANOS' in col.upper() and 'PM' in col.upper():
        anos_pm_col = col
        break
if anos_pm_col and 'INDE_2022' in df.columns:
    tmp_pm = df[[anos_pm_col, 'INDE_2022']].apply(pd.to_numeric, errors='coerce').dropna()
    r_pm, p_pm = stats.spearmanr(tmp_pm[anos_pm_col], tmp_pm['INDE_2022'])
    print(f'  Spearman r={r_pm:.4f}  p={p_pm:.6f}  {"*** SIM" if p_pm < 0.001 else ""}')
    etapa5['anos_pm_spearman'] = {'r': round(r_pm, 4), 'p': round(float(p_pm), 6)}

# 5e. Origem escolar dos indicados — hipotese majoritariamente publica
print('\n[5e] Hipotese: indicados vem majoritariamente de escola publica?')
if os.path.exists('output_p11.json'):
    origem = p11_data.get('insight6_mobilidade', {}).get('origem_escolar_indicados', {})
    if origem:
        publica_pct = origem.get('P\u00fablica', {}).get('pct', 0)
        print(f'  % de indicados de escola publica: {publica_pct}%')
        print(f'  Hipotese sustentada (>50%)? {"SIM" if publica_pct > 50 else "NAO — REVISAR"}')
        etapa5['hipotese_escola_publica'] = {
            'pct_publica': publica_pct,
            'sustentada': bool(publica_pct > 50),
        }

resultados['etapa5_coerencia'] = etapa5

# =========================================================================
# FIGURAS
# =========================================================================
print(f'\n{SEP}')
print('GERANDO FIGURAS...')
print(SEP)

# Figura 1: Boxplots de todos os indicadores por ano
fig1, axes1 = plt.subplots(2, 4, figsize=(20, 10))
axes1 = axes1.flatten()
for i, ind in enumerate(INDICADORES):
    dados = []
    labels = []
    for ano in ANOS:
        col = f'{ind}_{ano}'
        if col in df.columns:
            s = pd.to_numeric(df[col], errors='coerce').dropna()
            if len(s) > 0:
                dados.append(s.values)
                labels.append(str(ano))
    if dados:
        bp = axes1[i].boxplot(dados, labels=labels, patch_artist=True)
        cores_box = ['#5bc0de', '#f0ad4e', '#5cb85c']
        for patch, cor in zip(bp['boxes'], cores_box):
            patch.set_facecolor(cor)
            patch.set_alpha(0.7)
    axes1[i].set_title(f'{ind}')
    axes1[i].set_ylim(0, 11)
    axes1[i].set_ylabel('Valor')

plt.suptitle('Distribuicao dos Indicadores por Ano (2020-2021-2022)', fontsize=14)
plt.tight_layout()
plt.savefig('../figures/fig_val_distribuicoes.png', dpi=100, bbox_inches='tight')
plt.close()
print('Figura salva: fig_val_distribuicoes.png')

# Figura 2: Heatmap Spearman com p-values (2022)
fig2, axes2 = plt.subplots(1, 2, figsize=(18, 7))

corr_sp_num = corr_matrix_sp.astype(float)
mask_tri    = np.triu(np.ones_like(corr_sp_num, dtype=bool))

sns.heatmap(corr_sp_num, ax=axes2[0], annot=True, fmt='.2f',
            cmap='RdYlGn', vmin=-1, vmax=1, mask=mask_tri,
            square=True, linewidths=0.5, annot_kws={'size': 8})
axes2[0].set_title('Correlacao Spearman (2022)\n(triangulo inferior)')

# Heatmap de significancia
pval_sp_num = pval_matrix_sp.astype(float)
sig_matrix  = (pval_sp_num < 0.05).astype(float) * corr_sp_num.abs()
sns.heatmap(sig_matrix, ax=axes2[1], annot=True, fmt='.2f',
            cmap='YlOrRd', vmin=0, vmax=1, mask=mask_tri,
            square=True, linewidths=0.5, annot_kws={'size': 8})
axes2[1].set_title('Magnitude das correlacoes significativas\n(p<0.05, triangulo inferior)')

plt.suptitle('Correlacoes Spearman com Significancia Estatistica (2022)', fontsize=13)
plt.tight_layout()
plt.savefig('../figures/fig_val_correlacoes.png', dpi=100, bbox_inches='tight')
plt.close()
print('Figura salva: fig_val_correlacoes.png')

# Figura 3: NaN por indicador e ano
nan_df = pd.DataFrame(nan_pct).T
nan_df.columns = nan_df.columns.astype(str)
nan_df = nan_df.apply(pd.to_numeric, errors='coerce')

fig3, ax3 = plt.subplots(figsize=(12, 5))
nan_df.T.plot(kind='bar', ax=ax3, color=['#5bc0de', '#f0ad4e', '#5cb85c'], alpha=0.85)
ax3.set_title('Percentual de NaN por Indicador e Ano')
ax3.set_ylabel('% NaN')
ax3.set_xlabel('Indicador')
ax3.legend(title='Indicador', bbox_to_anchor=(1.01, 1), loc='upper left')
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig('../figures/fig_val_nan.png', dpi=100, bbox_inches='tight')
plt.close()
print('Figura salva: fig_val_nan.png')

# =========================================================================
# EXPORTAR RESULTADOS
# =========================================================================
with open('../outputs/output_validacao.json', 'w', encoding='utf-8') as f:
    json.dump(resultados, f, ensure_ascii=False, indent=2, default=str)
print('\nResultado salvo: output_validacao.json')
print('\n=== CONCLUIDO ===')
print('Proximo passo: revisar output_validacao.json e rodar p9_modelo_v2.py (etapa 4)')
