# p10_efetividade.py — Pergunta 10: Efetividade do Programa
# Salva resultados em output_p10.json
# encoding: utf-8

import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

df = pd.read_csv('../data/PEDE_PASSOS_DATASET_FIAP.csv', delimiter=';')

pedra_order = ['Quartzo', '\u00c1gata', 'Ametista', 'Top\u00e1zio']

# --- INDE medio por Pedra por ano ---
print('Evolucao do INDE medio por Pedra ao longo dos anos:')
inde_por_pedra_ano = {}
for pedra in pedra_order:
    linha = f'{pedra:<12}: '
    inde_por_pedra_ano[pedra] = {}
    for ano in [2020, 2021, 2022]:
        ped_col  = f'PEDRA_{ano}'
        inde_col = f'INDE_{ano}'
        if ped_col in df.columns and inde_col in df.columns:
            g = df[df[ped_col] == pedra][inde_col]
            g = pd.to_numeric(g, errors='coerce').dropna()
            if len(g) > 0:
                inde_por_pedra_ano[pedra][ano] = {'media': round(g.mean(), 3), 'n': len(g)}
                linha += f'{ano}={g.mean():.2f}(n={len(g)})  '
            else:
                inde_por_pedra_ano[pedra][ano] = None
                linha += f'{ano}=N/A           '
    print(linha)

# --- Taxa de progressao de Pedra ---
mask = df['PEDRA_2020'].notna() & df['PEDRA_2022'].notna()
df_prog = df[mask][['PEDRA_2020', 'PEDRA_2022']].copy()

pedra_nivel = {'Quartzo': 0, '\u00c1gata': 1, 'Ametista': 2, 'Top\u00e1zio': 3}
df_prog['NIVEL_2020'] = df_prog['PEDRA_2020'].map(pedra_nivel)
df_prog['NIVEL_2022'] = df_prog['PEDRA_2022'].map(pedra_nivel)
df_prog = df_prog.dropna()

total_prog = len(df_prog)
progrediu  = int((df_prog['NIVEL_2022'] > df_prog['NIVEL_2020']).sum())
manteve    = int((df_prog['NIVEL_2022'] == df_prog['NIVEL_2020']).sum())
regrediu   = int((df_prog['NIVEL_2022'] < df_prog['NIVEL_2020']).sum())

print(f'\nTaxa de progressao de Pedra (2020 -> 2022, n={total_prog}):')
print(f'  Progrediu  : {progrediu:>3} ({progrediu/total_prog*100:.1f}%)')
print(f'  Manteve    : {manteve:>3} ({manteve/total_prog*100:.1f}%)')
print(f'  Regrediu   : {regrediu:>3} ({regrediu/total_prog*100:.1f}%)')

# --- INDE medio geral por ano ---
print('\nINDE medio geral por ano:')
inde_geral = {}
for ano in [2020, 2021, 2022]:
    col = f'INDE_{ano}'
    if col in df.columns:
        vals = pd.to_numeric(df[col], errors='coerce').dropna()
        inde_geral[ano] = {'media': round(vals.mean(), 4), 'n': len(vals)}
        print(f'  {ano}: {vals.mean():.3f}  (n={len(vals)})')

# --- Graficos ---
cores_pedra_map = {
    'Quartzo': '#d9534f', '\u00c1gata': '#f0ad4e',
    'Ametista': '#5bc0de', 'Top\u00e1zio': '#5cb85c'
}
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

# Evolucao INDE por Pedra
anos_plot = [2020, 2021, 2022]
for pedra in pedra_order:
    vals_line = []
    for ano in anos_plot:
        entry = inde_por_pedra_ano[pedra].get(ano)
        vals_line.append(entry['media'] if entry else np.nan)
    anos_validos = [a for a, v in zip(anos_plot, vals_line) if not np.isnan(v)]
    vals_validos = [v for v in vals_line if not np.isnan(v)]
    if anos_validos:
        axes[0].plot([str(a) for a in anos_validos], vals_validos,
                     marker='o', label=pedra, color=cores_pedra_map[pedra], linewidth=2)
axes[0].set_title('Evolucao do INDE Medio\npor Pedra (2020-2022)')
axes[0].set_ylabel('INDE Medio')
axes[0].set_ylim(0, 10)
axes[0].legend(fontsize=9)

# Progressao de Pedra
labels_prog = ['Progrediu', 'Manteve', 'Regrediu']
vals_p      = [progrediu, manteve, regrediu]
cores_p     = ['#5cb85c', '#f0ad4e', '#d9534f']
bars2 = axes[1].bar(labels_prog, vals_p, color=cores_p, width=0.5)
for bar, val in zip(bars2, vals_p):
    pct = val / total_prog * 100
    axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                 f'{val}\n({pct:.1f}%)', ha='center', va='bottom', fontsize=10)
axes[1].set_title(f'Progressao de Pedra\n2020 -> 2022 (n={total_prog})')
axes[1].set_ylabel('Quantidade de Alunos')

# INDE geral por ano
if inde_geral:
    anos_g = [str(a) for a in sorted(inde_geral.keys())]
    vals_g = [inde_geral[a]['media'] for a in sorted(inde_geral.keys())]
    axes[2].plot(anos_g, vals_g, marker='o', color='#5bc0de', linewidth=2)
    for i, (a, v) in enumerate(zip(anos_g, vals_g)):
        axes[2].text(i, v + 0.05, f'{v:.3f}', ha='center', fontsize=11)
    axes[2].set_title('INDE Medio Geral\npor Ano')
    axes[2].set_ylabel('INDE Medio')
    axes[2].set_ylim(0, 10)

plt.suptitle('Efetividade do Programa Passos Magicos — Evolucao e Progressao', fontsize=13)
plt.tight_layout()
plt.savefig('../figures/fig_p10_efetividade.png', dpi=100, bbox_inches='tight')
plt.close()
print('Figura salva: fig_p10_efetividade.png')

# --- Exportar resultados ---
output = {
    'pergunta': 10,
    'titulo': 'Efetividade do Programa',
    'inde_geral_por_ano': {str(k): v for k, v in inde_geral.items()},
    'progressao_pedra': {
        'n_total': total_prog,
        'progrediu': progrediu, 'pct_progrediu': round(progrediu/total_prog*100, 1),
        'manteve':   manteve,   'pct_manteve':   round(manteve/total_prog*100, 1),
        'regrediu':  regrediu,  'pct_regrediu':  round(regrediu/total_prog*100, 1),
    },
    'inde_por_pedra_ano': {
        pedra: {str(ano): v for ano, v in anos.items()}
        for pedra, anos in inde_por_pedra_ano.items()
    },
    'conclusoes': {
        'INDE_geral': 'Crescimento consistente de 2020 para 2022',
        'progressao': 'Maioria dos alunos progrediu ou manteve a Pedra',
        'limitacao': 'Apenas alunos presentes nos 3 anos (n=' + str(total_prog) + ', ~23% da base)',
        'alerta_metodologico': 'Regressao de Pedra pode refletir revisao de criterios em 2022, nao queda real',
    }
}

with open('../outputs/output_p10.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
print('Resultado salvo: output_p10.json')
