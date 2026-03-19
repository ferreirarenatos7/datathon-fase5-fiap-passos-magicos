# p8_inde.py — Pergunta 8: Multidimensionalidade do INDE
# Salva resultados em output_p8.json
# encoding: utf-8

import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('../data/PEDE_PASSOS_DATASET_FIAP.csv', delimiter=';')

# H1/H2 — Correlacao de cada indicador com INDE por ano
indicadores_base = ['IAN', 'IDA', 'IEG', 'IAA', 'IPS', 'IPP', 'IPV']

print('H1/H2 — Correlacao dos indicadores com INDE por ano:')
print(f"{'Indicador':<8} {'2020':>8} {'2021':>8} {'2022':>8}")
print('-' * 36)

corr_inde = {}
for ind in indicadores_base:
    row = []
    for ano in [2020, 2021, 2022]:
        col_ind  = f'{ind}_{ano}'
        col_inde = f'INDE_{ano}'
        if col_ind in df.columns and col_inde in df.columns:
            tmp = df[[col_ind, col_inde]].apply(pd.to_numeric, errors='coerce').dropna()
            r = tmp[col_ind].corr(tmp[col_inde]) if len(tmp) > 10 else np.nan
        else:
            r = np.nan
        row.append(r)
    corr_inde[ind] = row
    vals = [f'{v:.3f}' if not np.isnan(v) else '  N/A' for v in row]
    print(f'{ind:<8} {vals[0]:>8} {vals[1]:>8} {vals[2]:>8}')

# H3 — Correlacao entre os proprios indicadores (2022)
cols_2022 = [f'{ind}_2022' for ind in indicadores_base if f'{ind}_2022' in df.columns]
cols_2022.append('INDE_2022')

df_corr = df[cols_2022].apply(pd.to_numeric, errors='coerce').dropna()
df_corr.columns = [c.replace('_2022', '') for c in df_corr.columns]

n_corr = len(df_corr)
print(f'\nH3 — Matriz de correlacao entre indicadores (2022, n={n_corr}):')
corr_matrix = df_corr.corr()
print(corr_matrix.round(2).to_string())

# H4 — INDE por Pedra
pedra_col   = 'PEDRA_2022'
inde_col    = 'INDE_2022'
pedra_order = ['Quartzo', 'Agata', 'Ametista', 'Topazio']
pedra_order_utf8 = ['Quartzo', '\u00c1gata', 'Ametista', 'Top\u00e1zio']

df_h4 = df[[pedra_col, inde_col]].copy()
df_h4[inde_col] = pd.to_numeric(df_h4[inde_col], errors='coerce')
df_h4 = df_h4.dropna()

print('\nH4 — INDE medio por Pedra (2022):')
inde_por_pedra = {}
for pedra in pedra_order_utf8:
    g = df_h4[df_h4[pedra_col] == pedra][inde_col]
    if len(g) > 0:
        inde_por_pedra[pedra] = {'media': round(g.mean(), 3), 'mediana': round(g.median(), 3), 'n': len(g)}
        print(f'  {pedra:<12}: media={g.mean():.3f}  mediana={g.median():.3f}  n={len(g)}')

# --- Graficos ---
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

# Heatmap
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
sns.heatmap(corr_matrix, ax=axes[0], annot=True, fmt='.2f', cmap='RdYlGn',
            vmin=-1, vmax=1, mask=mask, square=True, linewidths=0.5,
            annot_kws={'size': 8})
axes[0].set_title('H3 — Correlacao entre\nIndicadores (2022)')

# Correlacao com INDE por ano
x = np.arange(len(indicadores_base))
w = 0.25
cores_anos = ['#5bc0de', '#f0ad4e', '#5cb85c']
for j, (ano, cor) in enumerate(zip([2020, 2021, 2022], cores_anos)):
    vals = [corr_inde[ind][j] for ind in indicadores_base]
    vals_plot = [v if not np.isnan(v) else 0 for v in vals]
    axes[1].bar(x + j*w - w, vals_plot, w, label=str(ano), color=cor, alpha=0.85)
axes[1].set_xticks(x)
axes[1].set_xticklabels(indicadores_base, fontsize=9)
axes[1].axhline(0.5, color='gray', linestyle='--', linewidth=1)
axes[1].set_title('H1/H2 — Correlacao dos Indicadores\ncom INDE por Ano')
axes[1].set_ylabel('r de Pearson')
axes[1].set_ylim(0, 1.0)
axes[1].legend(fontsize=8)

# Boxplot INDE por Pedra
cores_pedra = {'Quartzo': '#d9534f', '\u00c1gata': '#f0ad4e',
               'Ametista': '#5bc0de', 'Top\u00e1zio': '#5cb85c'}
existentes_h4 = [p for p in pedra_order_utf8 if p in df_h4[pedra_col].unique()]
data_box = [df_h4[df_h4[pedra_col] == p][inde_col].values for p in existentes_h4]
bp = axes[2].boxplot(data_box, labels=existentes_h4, patch_artist=True)
for patch, pedra in zip(bp['boxes'], existentes_h4):
    patch.set_facecolor(cores_pedra.get(pedra, 'gray'))
    patch.set_alpha(0.7)
axes[2].set_title('H4 — Distribuicao do INDE\npor Pedra (2022)')
axes[2].set_ylabel('INDE')
axes[2].set_ylim(0, 10)

plt.suptitle('INDE — Multidimensionalidade, Correlacoes e Discriminacao por Pedra', fontsize=13)
plt.tight_layout()
plt.savefig('../figures/fig_p8_inde.png', dpi=100, bbox_inches='tight')
plt.close()
print('Figura salva: fig_p8_inde.png')

# --- Exportar resultados ---
# Serializar corr_inde (converte NaN para None para JSON)
corr_inde_serial = {
    ind: [None if np.isnan(v) else round(v, 4) for v in vals]
    for ind, vals in corr_inde.items()
}
# Correlacao entre indicadores (2022) como dict
corr_matrix_serial = {
    col: {row: (None if np.isnan(v) else round(v, 4))
          for row, v in corr_matrix[col].items()}
    for col in corr_matrix.columns
}

output = {
    'pergunta': 8,
    'titulo': 'Multidimensionalidade do INDE',
    'n_corr_2022': n_corr,
    'corr_indicadores_inde': corr_inde_serial,
    'corr_matrix_2022': corr_matrix_serial,
    'inde_por_pedra_2022': inde_por_pedra,
    'conclusoes': {
        'H1_maior_peso': 'IDA e IEG (maiores correlacoes com INDE nos tres anos)',
        'H2_estabilidade': 'Sim — ranking dos indicadores consistente em 2020, 2021 e 2022',
        'H3_redundancia': 'Parcial — IDA e IEG correlacionados entre si; IAN mais independente',
        'H4_discrimina_pedras': 'Sim — INDE medio aumenta monotonicamente de Quartzo para Topazio',
    }
}

with open('../outputs/output_p8.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
print('Resultado salvo: output_p8.json')
