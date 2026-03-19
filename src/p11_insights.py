# p11_insights.py — Pergunta 11: Insights e Criatividade
# Salva resultados em output_p11.json
# encoding: utf-8

import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

df = pd.read_csv('../data/PEDE_PASSOS_DATASET_FIAP.csv', delimiter=';')

resultados = {}

# -----------------------------------------------------------------------
# Insight 1 — Impacto do tempo no programa (ANOS_PM) no desempenho
# -----------------------------------------------------------------------
anos_pm_col = None
for col in df.columns:
    if 'ANOS' in col.upper() and 'PM' in col.upper():
        anos_pm_col = col
        break

insight1 = {}
if anos_pm_col:
    df_anos = df[[anos_pm_col, 'INDE_2022', 'IDA_2022']].copy()
    for col in [anos_pm_col, 'INDE_2022', 'IDA_2022']:
        df_anos[col] = pd.to_numeric(df_anos[col], errors='coerce')
    df_anos = df_anos.dropna()
    print('Insight 1 — INDE e IDA por tempo no programa (ANOS_PM):')
    for anos_val in sorted(df_anos[anos_pm_col].unique()):
        g = df_anos[df_anos[anos_pm_col] == anos_val]
        entry = {'inde_medio': round(g['INDE_2022'].mean(), 3),
                 'ida_medio':  round(g['IDA_2022'].mean(), 3),
                 'n': len(g)}
        insight1[int(anos_val)] = entry
        print(f'  {int(anos_val)} ano(s): INDE={entry["inde_medio"]:.3f}  IDA={entry["ida_medio"]:.3f}  n={entry["n"]}')
else:
    print('Coluna ANOS_PM nao encontrada.')
resultados['insight1_anos_pm'] = insight1

# -----------------------------------------------------------------------
# Insight 2 — Perfil de alunos bolsistas vs nao bolsistas
# -----------------------------------------------------------------------
bolsa_col = None
for col in df.columns:
    if 'BOLSA' in col.upper() or 'BOLSISTA' in col.upper():
        bolsa_col = col
        break

insight2 = {}
if bolsa_col:
    df_bolsa = df[[bolsa_col, 'INDE_2022', 'IDA_2022']].copy()
    for col in ['INDE_2022', 'IDA_2022']:
        df_bolsa[col] = pd.to_numeric(df_bolsa[col], errors='coerce')
    df_bolsa = df_bolsa.dropna()
    print('\nInsight 2 — INDE e IDA por status de bolsa:')
    for grupo in df_bolsa[bolsa_col].unique():
        g = df_bolsa[df_bolsa[bolsa_col] == grupo]
        entry = {'inde_medio': round(g['INDE_2022'].mean(), 3),
                 'ida_medio':  round(g['IDA_2022'].mean(), 3),
                 'n': len(g)}
        insight2[str(grupo)] = entry
        print(f'  {grupo}: INDE={entry["inde_medio"]:.3f}  IDA={entry["ida_medio"]:.3f}  n={entry["n"]}')
resultados['insight2_bolsistas'] = insight2

# -----------------------------------------------------------------------
# Insight 3 — Taxa de retencao por coorte
# -----------------------------------------------------------------------
s20 = df['INDE_2020'].notna()
s21 = df['INDE_2021'].notna()
s22 = df['INDE_2022'].notna()

n_2020_only = int((s20 & ~s21 & ~s22).sum())
n_2021_only = int((~s20 & s21 & ~s22).sum())
n_2022_only = int((~s20 & ~s21 & s22).sum())
n_20_21     = int((s20 & s21 & ~s22).sum())
n_20_22     = int((s20 & ~s21 & s22).sum())
n_21_22     = int((~s20 & s21 & s22).sum())
n_todos     = int((s20 & s21 & s22).sum())
total_alunos = len(df)

retencao = round(n_todos / (n_2020_only + n_20_21 + n_20_22 + n_todos) * 100, 1)

print(f'\nInsight 3 — Retencao por coorte:')
print(f'  Apenas 2020: {n_2020_only}  |  Apenas 2021: {n_2021_only}  |  Apenas 2022: {n_2022_only}')
print(f'  2020+2021: {n_20_21}  |  2020+2022: {n_20_22}  |  2021+2022: {n_21_22}')
print(f'  Todos 3 anos: {n_todos}')
print(f'  Retencao 2020->2022: {retencao}%')

resultados['insight3_coorte'] = {
    'n_2020_only': n_2020_only, 'n_2021_only': n_2021_only, 'n_2022_only': n_2022_only,
    'n_20_21': n_20_21, 'n_20_22': n_20_22, 'n_21_22': n_21_22,
    'n_todos_3_anos': n_todos, 'total': total_alunos,
    'pct_todos_3_anos': round(n_todos / total_alunos * 100, 1),
    'retencao_2020_2022_pct': retencao,
}

# -----------------------------------------------------------------------
# Insight 4 — Variacao dos indicadores 2020 vs 2022
# -----------------------------------------------------------------------
print('\nInsight 4 — Variacao dos indicadores 2020 vs 2022:')
print(f"{'Indicador':<8} {'2020':>8} {'2022':>8} {'Dif':>8}")
print('-' * 36)

insight4 = {}
for ind in ['IAN', 'IDA', 'IEG', 'IAA', 'IPS', 'IPP', 'IPV', 'INDE']:
    c20 = f'{ind}_2020'
    c22 = f'{ind}_2022'
    if c20 in df.columns and c22 in df.columns:
        m20 = round(pd.to_numeric(df[c20], errors='coerce').mean(), 4)
        m22 = round(pd.to_numeric(df[c22], errors='coerce').mean(), 4)
        insight4[ind] = {'media_2020': m20, 'media_2022': m22, 'dif': round(m22 - m20, 4)}
        print(f'{ind:<8} {m20:>8.3f} {m22:>8.3f} {m22-m20:>+8.3f}')
resultados['insight4_variacao_indicadores'] = insight4

# -----------------------------------------------------------------------
# Insight 5 — Instituicao de Ensino como fator contextual
# -----------------------------------------------------------------------
inst_col = 'INSTITUICAO_ENSINO_ALUNO_2020'
mapa_tipo = {
    'Escola P\u00fablica'      : 'P\u00fablica',
    'Escola Jo\u00e3o Paulo II' : 'Comunit\u00e1ria',
    'Rede Decis\u00e3o/Uni\u00e3o': 'Comunit\u00e1ria',
    'Einstein'                  : 'Parceira Privada',
    'FIAP'                      : 'Parceira Privada',
    'UNISA'                     : 'Parceira Privada',
    'Est\u00e1cio'              : 'Parceira Privada',
}

df_inst = df.copy()
df_inst['TIPO_INST'] = df_inst[inst_col].map(mapa_tipo)
df_inst = df_inst[df_inst['TIPO_INST'].notna()]

tipos_ordem = ['P\u00fablica', 'Comunit\u00e1ria', 'Parceira Privada']
indicadores_inst = ['IAN', 'IDA', 'IEG', 'IAA', 'IPS', 'IPP', 'IPV', 'INDE']

insight5 = {}
print('\nInsight 5 — Indicadores por tipo de instituicao:')
for tipo in tipos_ordem:
    g = df_inst[df_inst['TIPO_INST'] == tipo]
    insight5[tipo] = {'n': len(g), 'indicadores': {}}
    print(f'  {tipo} (n={len(g)}):')
    for ind in indicadores_inst:
        c22 = f'{ind}_2022'
        if c22 in df_inst.columns:
            v = round(pd.to_numeric(g[c22], errors='coerce').mean(), 3)
            insight5[tipo]['indicadores'][ind] = float(v) if not np.isnan(v) else None
    print('    2022: ' + '  '.join([
        f'{ind}={insight5[tipo]["indicadores"].get(ind, "N/A")}'
        for ind in indicadores_inst
    ]))

# Progressao por tipo
pedra_nivel_inst = {'Quartzo': 0, '\u00c1gata': 1, 'Ametista': 2, 'Top\u00e1zio': 3}
df_prog_inst = df_inst[df_inst['PEDRA_2020'].notna() & df_inst['PEDRA_2022'].notna()].copy()
df_prog_inst['NIVEL_2020'] = df_prog_inst['PEDRA_2020'].map(pedra_nivel_inst)
df_prog_inst['NIVEL_2022'] = df_prog_inst['PEDRA_2022'].map(pedra_nivel_inst)
df_prog_inst = df_prog_inst.dropna(subset=['NIVEL_2020', 'NIVEL_2022'])

print('\nProgressao de Pedra por tipo de instituicao:')
progressao_por_tipo = {}
for tipo in tipos_ordem:
    g = df_prog_inst[df_prog_inst['TIPO_INST'] == tipo]
    if len(g) == 0:
        continue
    prog = int((g['NIVEL_2022'] > g['NIVEL_2020']).sum())
    mant = int((g['NIVEL_2022'] == g['NIVEL_2020']).sum())
    regr = int((g['NIVEL_2022'] < g['NIVEL_2020']).sum())
    progressao_por_tipo[tipo] = {
        'n': len(g),
        'progrediu': prog, 'pct_progrediu': round(prog/len(g)*100, 1),
        'manteve':   mant, 'pct_manteve':   round(mant/len(g)*100, 1),
        'regrediu':  regr, 'pct_regrediu':  round(regr/len(g)*100, 1),
    }
    print(f'  {tipo}: Progrediu={prog}({prog/len(g)*100:.0f}%)  Manteve={mant}({mant/len(g)*100:.0f}%)  Regrediu={regr}({regr/len(g)*100:.0f}%)')
insight5['progressao_por_tipo'] = progressao_por_tipo
resultados['insight5_instituicao'] = insight5

# -----------------------------------------------------------------------
# Insight 6 — INDICADO_BOLSA como marcador de mobilidade social
# -----------------------------------------------------------------------
bolsista_col = 'BOLSISTA_2022'
indicado_col = 'INDICADO_BOLSA_2022'
inds_6       = ['IAN', 'IDA', 'IEG', 'IAA', 'IPS', 'IPP', 'IPV', 'INDE']

cols_6 = [bolsista_col, indicado_col, 'PEDRA_2022', 'PONTO_VIRADA_2022', inst_col] + \
         [f'{ind}_2022' for ind in inds_6 if f'{ind}_2022' in df.columns]
df6 = df[[c for c in cols_6 if c in df.columns]].copy()
for col in [f'{ind}_2022' for ind in inds_6]:
    if col in df6.columns:
        df6[col] = pd.to_numeric(df6[col], errors='coerce')

n_bolsista = df6[bolsista_col].value_counts().to_dict() if bolsista_col in df6.columns else {}
n_indicado = df6[indicado_col].value_counts().to_dict() if indicado_col in df6.columns else {}

print('\n=== Insight 6 — BOLSISTA_2022 ===')
print(f'Distribuicao: {n_bolsista}')

insight6 = {
    'n_bolsista': {str(k): int(v) for k, v in n_bolsista.items()},
    'n_indicado': {str(k): int(v) for k, v in n_indicado.items()},
}

# Parte A: Bolsista vs nao bolsista
if bolsista_col in df6.columns:
    grupos_b = sorted(df6[bolsista_col].dropna().unique())
    difs_bolsista = {}
    for ind in inds_6:
        col = f'{ind}_2022'
        if col not in df6.columns:
            continue
        medias = {str(g): round(df6[df6[bolsista_col] == g][col].mean(), 3) for g in grupos_b}
        dif = round(medias.get('Sim', 0) - medias.get('N\u00e3o', 0), 3)
        difs_bolsista[ind] = {'medias': medias, 'dif_sim_nao': dif}
    insight6['parte_a_bolsista'] = difs_bolsista

# Parte B: INDICADO_BOLSA
if indicado_col in df6.columns:
    df6_ind = df6[df6[indicado_col].notna()].copy()
    grupos_i = sorted(df6_ind[indicado_col].unique())

    difs_indicado = {}
    for ind in inds_6:
        col = f'{ind}_2022'
        if col not in df6_ind.columns:
            continue
        medias = {str(g): round(df6_ind[df6_ind[indicado_col] == g][col].mean(), 3) for g in grupos_i}
        dif = round(medias.get('Sim', 0) - medias.get('N\u00e3o', 0), 3)
        difs_indicado[ind] = {'medias': medias, 'dif_sim_nao': dif}
    insight6['parte_b_indicado'] = difs_indicado

    # Ordem por diferenca absoluta
    difs_ord = sorted(difs_indicado.items(), key=lambda x: abs(x[1]['dif_sim_nao']), reverse=True)
    print('\nDiferenca por indicador (Indicado Sim - Nao, ordenado):')
    for ind, entry in difs_ord:
        print(f'  {ind:<6}: {entry["dif_sim_nao"]:>+6.3f}')
    insight6['ranking_diferenca'] = [{'indicador': ind, 'dif': entry['dif_sim_nao']} for ind, entry in difs_ord]

    # Origem escolar dos indicados
    if inst_col in df6.columns:
        df6_sim = df6[df6[indicado_col] == 'Sim']
        total_sim = len(df6_sim)
        df6_sim_tipo = df6_sim.copy()
        df6_sim_tipo['TIPO_INST'] = df6_sim_tipo[inst_col].map(mapa_tipo)
        dist_tipo = df6_sim_tipo['TIPO_INST'].value_counts().to_dict()
        origem = {str(k): {'n': int(v), 'pct': round(v/total_sim*100, 1)} for k, v in dist_tipo.items()}
        insight6['origem_escolar_indicados'] = origem
        print(f'\nOrigem escolar dos indicados (n={total_sim}):')
        for tipo, entry in origem.items():
            print(f'  {tipo}: {entry["n"]} ({entry["pct"]}%)')

    # Ponto de virada dos indicados
    if 'PONTO_VIRADA_2022' in df6_ind.columns:
        pv = {}
        for grupo in grupos_i:
            g = df6_ind[df6_ind[indicado_col] == grupo]
            pv[str(grupo)] = {str(k): round(v*100, 1) for k, v in g['PONTO_VIRADA_2022'].value_counts(normalize=True).items()}
        insight6['ponto_virada_por_indicacao'] = pv

    # Pipeline: INDICADO x BOLSISTA
    if bolsista_col in df6.columns:
        cross = pd.crosstab(df6[indicado_col], df6[bolsista_col]).to_dict()
        insight6['pipeline_indicado_x_bolsista'] = {str(k): {str(kk): int(vv) for kk, vv in v.items()} for k, v in cross.items()}

resultados['insight6_mobilidade'] = insight6

# -----------------------------------------------------------------------
# Graficos
# -----------------------------------------------------------------------
cores_tipo = ['#d9534f', '#f0ad4e', '#5cb85c']

# Figura 1: Insights 4 e 3 (variacao indicadores + coorte)
fig1, axes = plt.subplots(1, 2, figsize=(14, 6))

inds_comp = ['IAN', 'IDA', 'IEG', 'IAA', 'IPS', 'IPP', 'IPV', 'INDE']
medias_20 = [insight4[ind]['media_2020'] if ind in insight4 else np.nan for ind in inds_comp]
medias_22 = [insight4[ind]['media_2022'] if ind in insight4 else np.nan for ind in inds_comp]
x = np.arange(len(inds_comp))
w = 0.35
axes[0].bar(x - w/2, medias_20, w, label='2020', color='#5bc0de', alpha=0.85)
axes[0].bar(x + w/2, medias_22, w, label='2022', color='#5cb85c', alpha=0.85)
axes[0].set_xticks(x)
axes[0].set_xticklabels(inds_comp, fontsize=9)
axes[0].set_title('Insight 4 — Todos os Indicadores\n2020 vs 2022')
axes[0].set_ylim(0, 11)
axes[0].legend(fontsize=9)

labels_coorte = ['Apenas\n2020', 'Apenas\n2021', 'Apenas\n2022',
                 '2020+2021', '2020+2022', '2021+2022', 'Todos\n3 anos']
vals_coorte   = [n_2020_only, n_2021_only, n_2022_only, n_20_21, n_20_22, n_21_22, n_todos]
cores_coorte  = ['#d9534f', '#f0ad4e', '#5bc0de', '#d9534f', '#d9534f', '#f0ad4e', '#5cb85c']
bars3 = axes[1].bar(labels_coorte, vals_coorte, color=cores_coorte, alpha=0.85)
for bar, val in zip(bars3, vals_coorte):
    axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                 str(val), ha='center', va='bottom', fontsize=9)
axes[1].set_title('Insight 3 — Composicao da Coorte\npor Presenca nos Anos')
axes[1].set_ylabel('Quantidade de Alunos')

plt.suptitle('Insights Adicionais — Evolucao Geral e Composicao da Coorte', fontsize=13)
plt.tight_layout()
plt.savefig('../figures/fig_p11_insights34.png', dpi=100, bbox_inches='tight')
plt.close()
print('Figura salva: fig_p11_insights34.png')

# Figura 2: Insight 5 — instituicoes
fig2, axes_i5 = plt.subplots(1, 3, figsize=(18, 6))

for tipo, cor in zip(tipos_ordem, cores_tipo):
    g = df_inst[df_inst['TIPO_INST'] == tipo]
    vals = []
    for ano in [2020, 2021, 2022]:
        col = f'INDE_{ano}'
        v = pd.to_numeric(g[col], errors='coerce').mean() if col in df_inst.columns else np.nan
        vals.append(v)
    axes_i5[0].plot(['2020', '2021', '2022'], vals, marker='o', label=tipo, color=cor, linewidth=2)
    for i, v in enumerate(vals):
        if not np.isnan(v):
            axes_i5[0].text(i, v + 0.12, f'{v:.2f}', ha='center', fontsize=8, color=cor)
axes_i5[0].set_title('INDE por Tipo de\nInstituicao (2020-2022)')
axes_i5[0].set_ylim(0, 10)
axes_i5[0].legend(fontsize=8)

inds_i5 = ['IAN', 'IDA', 'IEG', 'IAA', 'IPS', 'IPP']
x_i5 = np.arange(len(inds_i5))
w_i5 = 0.25
for j, (tipo, cor) in enumerate(zip(tipos_ordem, cores_tipo)):
    g = df_inst[df_inst['TIPO_INST'] == tipo]
    vals = [pd.to_numeric(g[f'{ind}_2022'], errors='coerce').mean()
            if f'{ind}_2022' in df_inst.columns else np.nan for ind in inds_i5]
    axes_i5[1].bar(x_i5 + (j-1)*w_i5, [v if not np.isnan(v) else 0 for v in vals],
                   w_i5, label=tipo, color=cor, alpha=0.85)
axes_i5[1].set_xticks(x_i5)
axes_i5[1].set_xticklabels(inds_i5, fontsize=9)
axes_i5[1].set_title('Indicadores 2022\npor Tipo de Instituicao')
axes_i5[1].set_ylim(0, 11)
axes_i5[1].legend(fontsize=8)

pedras_status   = ['Progrediu', 'Manteve', 'Regrediu']
cores_status_i5 = ['#5cb85c', '#f0ad4e', '#d9534f']
tipos_com_dados = [t for t in tipos_ordem if t in progressao_por_tipo]
data_prog_inst  = {tipo: [
    progressao_por_tipo[tipo]['pct_progrediu'],
    progressao_por_tipo[tipo]['pct_manteve'],
    progressao_por_tipo[tipo]['pct_regrediu'],
] for tipo in tipos_com_dados}
for i, (status, cor) in enumerate(zip(pedras_status, cores_status_i5)):
    vals_s  = [data_prog_inst[t][i] for t in tipos_com_dados]
    bottom_s = [sum(data_prog_inst[t][:i]) for t in tipos_com_dados]
    axes_i5[2].bar(tipos_com_dados, vals_s, bottom=bottom_s, label=status, color=cor, alpha=0.85)
axes_i5[2].set_title('Progressao de Pedra\npor Tipo de Instituicao')
axes_i5[2].set_ylim(0, 100)
axes_i5[2].legend(fontsize=8)

plt.suptitle('Insight 5 — Tipo de Instituicao como Fator Contextual', fontsize=13)
plt.tight_layout()
plt.savefig('../figures/fig_p11_insight5.png', dpi=100, bbox_inches='tight')
plt.close()
print('Figura salva: fig_p11_insight5.png')

# Figura 3: Insight 6 — INDICADO_BOLSA
if indicado_col in df6.columns:
    fig3, axes_i6 = plt.subplots(1, 3, figsize=(18, 6))

    x_i6 = np.arange(len(inds_6))
    w_i6 = 0.35
    for j, (grupo, cor) in enumerate(zip(['N\u00e3o', 'Sim'], ['#5bc0de', '#5cb85c'])):
        g = df6_ind[df6_ind[indicado_col] == grupo] if grupo in grupos_i else pd.DataFrame()
        vals = [g[f'{ind}_2022'].mean() if not g.empty and f'{ind}_2022' in g.columns else 0
                for ind in inds_6]
        axes_i6[0].bar(x_i6 + (j-0.5)*w_i6, vals, w_i6,
                       label=f'Indicado: {grupo} (n={len(g)})', color=cor, alpha=0.85)
    axes_i6[0].set_xticks(x_i6)
    axes_i6[0].set_xticklabels(inds_6, fontsize=9)
    axes_i6[0].set_title('Indicadores 2022\nIndicado Bolsa: Sim vs Nao')
    axes_i6[0].set_ylim(0, 11)
    axes_i6[0].legend(fontsize=8)

    if inst_col in df6.columns and 'TIPO_INST' in df6_sim_tipo.columns:
        dist_tipo_plot = df6_sim_tipo['TIPO_INST'].value_counts()
        cores_tipo_i6  = [cores_tipo[tipos_ordem.index(t)] if t in tipos_ordem else '#aaa'
                          for t in dist_tipo_plot.index]
        bars_i6 = axes_i6[1].bar(dist_tipo_plot.index, dist_tipo_plot.values,
                                  color=cores_tipo_i6, alpha=0.85)
        for bar, val in zip(bars_i6, dist_tipo_plot.values):
            pct = val / total_sim * 100
            axes_i6[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                             f'{val}\n({pct:.1f}%)', ha='center', va='bottom', fontsize=10)
        axes_i6[1].set_title('Origem Escolar dos\nIndicados para Bolsa')

    if 'IEG_2022' in df6.columns and 'IDA_2022' in df6.columns:
        for grupo, cor, alpha in zip(['N\u00e3o', 'Sim'], ['#5bc0de', '#d9534f'], [0.3, 0.8]):
            g = df6_ind[df6_ind[indicado_col] == grupo]
            axes_i6[2].scatter(g['IDA_2022'], g['IEG_2022'], color=cor, alpha=alpha,
                               label=f'Indicado: {grupo}', s=20)
        for grupo, cor, marker in zip(['N\u00e3o', 'Sim'], ['#5bc0de', '#d9534f'], ['o', '*']):
            g = df6_ind[df6_ind[indicado_col] == grupo]
            axes_i6[2].scatter(g['IDA_2022'].mean(), g['IEG_2022'].mean(),
                               color=cor, s=200, marker=marker, edgecolors='black', zorder=5)
        axes_i6[2].set_xlabel('IDA (desempenho academico)')
        axes_i6[2].set_ylabel('IEG (engajamento no programa)')
        axes_i6[2].set_title('IDA vs IEG por Indicacao\n(estrela = media do grupo)')
        axes_i6[2].legend(fontsize=7)
        axes_i6[2].set_xlim(0, 11)
        axes_i6[2].set_ylim(0, 11)

    plt.suptitle('Insight 6 — INDICADO_BOLSA: Marcador de Mobilidade Social', fontsize=13)
    plt.tight_layout()
    plt.savefig('../figures/fig_p11_insight6.png', dpi=100, bbox_inches='tight')
    plt.close()
    print('Figura salva: fig_p11_insight6.png')

# -----------------------------------------------------------------------
# Exportar resultados
# -----------------------------------------------------------------------
output = {
    'pergunta': 11,
    'titulo': 'Insights e Criatividade',
    **resultados,
    'tese_central': (
        'O programa Passos Magicos e um mecanismo de mobilidade social mensuravel. '
        'Os vetores centrais de resultado sao IEG e IDA; o tempo no programa amplifica ambos. '
        'A defasagem curricular (IAN) e persistente mas nao e determinante: alunos de escola '
        'publica, com IAN inferior, apresentam o maior engajamento e constituem o principal '
        'grupo de candidatos a bolsas em parceiras privadas.'
    ),
}

with open('../outputs/output_p11.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
print('Resultado salvo: output_p11.json')
