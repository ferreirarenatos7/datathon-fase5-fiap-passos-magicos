# gerar_md.py — Gera ANALISE_CONSOLIDADA.md a partir dos JSONs de saida
# Rodar apos: python p8_inde.py && python p9_modelo.py && python p10_efetividade.py && python p11_insights.py
# encoding: utf-8

import json
import os
from datetime import date

OUTPUT_FILE = '../docs/ANALISE_CONSOLIDADA.md'

def load(path):
    if not os.path.exists(path):
        return None
    with open(path, encoding='utf-8') as f:
        return json.load(f)

p8  = load('../outputs/output_p8.json')
p9  = load('../outputs/output_p9.json')
p10 = load('../outputs/output_p10.json')
p11 = load('../outputs/output_p11.json')

lines = []
def w(*args):
    lines.append(' '.join(str(a) for a in args))

w(f'# Análise Consolidada — Datathon Passos Mágicos')
w(f'**Gerado em:** {date.today()}  |  **Aluna:** Ana Raquel  |  **Curso:** POSTECH DTAT\n')
w('---\n')

# -----------------------------------------------------------------------
# PERGUNTA 8
# -----------------------------------------------------------------------
w('## Pergunta 8 — Multidimensionalidade do INDE\n')
if p8:
    ci = p8['corr_indicadores_inde']
    w('### H1/H2 — Correlação dos indicadores com INDE por ano\n')
    w(f"| Indicador | 2020 | 2021 | 2022 |")
    w(f"|-----------|------|------|------|")
    for ind, vals in ci.items():
        row = [f'{v:.3f}' if v is not None else 'N/A' for v in vals]
        w(f"| {ind} | {row[0]} | {row[1]} | {row[2]} |")
    w()
    c = p8['conclusoes']
    w(f"**H1 — Maior peso:** {c['H1_maior_peso']}")
    w(f"\n**H2 — Estabilidade:** {c['H2_estabilidade']}")
    w(f"\n**H3 — Redundância:** {c['H3_redundancia']}")
    w(f"\n**H4 — Discrimina Pedras:** {c['H4_discrimina_pedras']}")
    w()
    w('### H4 — INDE médio por Pedra (2022)\n')
    w('| Pedra | Média | Mediana | n |')
    w('|-------|-------|---------|---|')
    for pedra, entry in p8['inde_por_pedra_2022'].items():
        w(f"| {pedra} | {entry['media']} | {entry['mediana']} | {entry['n']} |")
else:
    w('> output_p8.json não encontrado — rode `python p8_inde.py`\n')
w('\n---\n')

# -----------------------------------------------------------------------
# PERGUNTA 9
# -----------------------------------------------------------------------
w('## Pergunta 9 — Modelo Preditivo de Risco de Defasagem\n')
if p9:
    ds = p9['dataset']
    w(f"**Dataset:** {ds['n_total']} registros  |  Defasados: {ds['n_defasado']} ({ds['pct_defasado']}%)  |  Adequados: {ds['n_adequado']}")
    w(f"\n**Features utilizadas:** {p9['n_features']} (indicadores 2020, 2021 + deltas)\n")

    w('### Comparativo de Modelos\n')
    w('| Modelo | AUC-CV | F1-CV | AUC-Holdout | F1-Holdout |')
    w('|--------|--------|-------|-------------|------------|')
    for nome, r in p9['resultados_modelos'].items():
        w(f"| {nome} | {r['auc_cv']:.3f} | {r['f1_cv']:.3f} | {r['auc_test']:.3f} | {r['f1_test']:.3f} |")
    w()
    w(f"**Modelo selecionado:** {p9['modelo_selecionado']}")
    w(f"\n**Justificativa:** {p9['justificativa']}\n")

    w('### Top 10 Features (Random Forest — importância)\n')
    w('| Feature | Importância |')
    w('|---------|-------------|')
    for feat, imp in p9['feature_importance_rf'].items():
        w(f"| {feat} | {imp:.4f} |")
    w()

    cm = p9['matriz_confusao']
    w('### Matriz de Confusão — Logistic Regression (holdout)\n')
    w('|  | Pred: Adequado | Pred: Defasado |')
    w('|--|----------------|----------------|')
    w(f"| **Real: Adequado** | {cm[0][0]} | {cm[0][1]} |")
    w(f"| **Real: Defasado** | {cm[1][0]} | {cm[1][1]} |")
    w()

    w('### Demonstração — Sistema de Recomendações\n')
    for perfil, demo in p9['demo_perfis'].items():
        w(f"**{perfil}** — Probabilidade: {demo['probabilidade']}% [{demo['nivel']}]")
        for r in demo['recomendacoes']:
            w(f"\n- [{r['indicador']}] contrib={r['contribuicao']:+.3f} → {r['recomendacao']}")
        w()
else:
    w('> output_p9.json não encontrado — rode `python p9_modelo.py`\n')
w('\n---\n')

# -----------------------------------------------------------------------
# PERGUNTA 10
# -----------------------------------------------------------------------
w('## Pergunta 10 — Efetividade do Programa\n')
if p10:
    w('### INDE Médio Geral por Ano\n')
    w('| Ano | Média | n |')
    w('|-----|-------|---|')
    for ano, entry in sorted(p10['inde_geral_por_ano'].items()):
        w(f"| {ano} | {entry['media']:.3f} | {entry['n']} |")
    w()

    prog = p10['progressao_pedra']
    w(f"### Progressão de Pedra — 2020 → 2022 (n={prog['n_total']})\n")
    w('| Status | n | % |')
    w('|--------|---|---|')
    w(f"| Progrediu | {prog['progrediu']} | {prog['pct_progrediu']}% |")
    w(f"| Manteve   | {prog['manteve']}   | {prog['pct_manteve']}% |")
    w(f"| Regrediu  | {prog['regrediu']}  | {prog['pct_regrediu']}% |")
    w()

    c = p10['conclusoes']
    w(f"**Conclusão:** {c['INDE_geral']}. {c['progressao']}.")
    w(f"\n\n**Limitação:** {c['limitacao']}.")
    w(f"\n\n**Alerta metodológico:** {c['alerta_metodologico']}.")
    w()
else:
    w('> output_p10.json não encontrado — rode `python p10_efetividade.py`\n')
w('\n---\n')

# -----------------------------------------------------------------------
# PERGUNTA 11 — INSIGHTS
# -----------------------------------------------------------------------
w('## Pergunta 11 — Insights e Criatividade\n')
if p11:
    # Insight 1
    w('### Insight 1 — Impacto do Tempo no Programa (ANOS_PM)\n')
    if p11.get('insight1_anos_pm'):
        w('| Anos no PM | INDE médio | IDA médio | n |')
        w('|------------|------------|-----------|---|')
        for anos, entry in sorted(p11['insight1_anos_pm'].items(), key=lambda x: int(x[0])):
            w(f"| {anos} | {entry['inde_medio']} | {entry['ida_medio']} | {entry['n']} |")
        w('\n> Impacto positivo e cumulativo: cada ano adicional no programa está associado a melhora nos indicadores.\n')

    # Insight 2
    w('### Insight 2 — Perfil Bolsistas vs Não Bolsistas\n')
    if p11.get('insight2_bolsistas'):
        w('| Grupo | INDE médio | IDA médio | n |')
        w('|-------|------------|-----------|---|')
        for grupo, entry in p11['insight2_bolsistas'].items():
            w(f"| {grupo} | {entry['inde_medio']} | {entry['ida_medio']} | {entry['n']} |")
        w('\n> Atenção: efeito de seleção — bolsistas já eram de maior desempenho antes da bolsa.\n')

    # Insight 3
    w('### Insight 3 — Rotatividade da Coorte\n')
    if p11.get('insight3_coorte'):
        c = p11['insight3_coorte']
        w(f"| Coorte | n |")
        w(f"|--------|---|")
        w(f"| Apenas 2020 | {c['n_2020_only']} |")
        w(f"| Apenas 2021 | {c['n_2021_only']} |")
        w(f"| Apenas 2022 | {c['n_2022_only']} |")
        w(f"| 2020 + 2021 | {c['n_20_21']} |")
        w(f"| 2020 + 2022 | {c['n_20_22']} |")
        w(f"| 2021 + 2022 | {c['n_21_22']} |")
        w(f"| Todos 3 anos | {c['n_todos_3_anos']} ({c['pct_todos_3_anos']}%) |")
        w(f"\n**Retenção 2020→2022:** {c['retencao_2020_2022_pct']}% dos alunos de 2020 continuaram até 2022.\n")

    # Insight 4
    w('### Insight 4 — Variação dos Indicadores 2020 vs 2022\n')
    if p11.get('insight4_variacao_indicadores'):
        w('| Indicador | Média 2020 | Média 2022 | Δ |')
        w('|-----------|------------|------------|---|')
        for ind, entry in p11['insight4_variacao_indicadores'].items():
            sinal = '+' if entry['dif'] >= 0 else ''
            w(f"| {ind} | {entry['media_2020']:.3f} | {entry['media_2022']:.3f} | {sinal}{entry['dif']:.3f} |")
        w()

    # Insight 5
    w('### Insight 5 — Tipo de Instituição como Fator Contextual\n')
    if p11.get('insight5_instituicao'):
        inst = p11['insight5_instituicao']
        # Tabela de indicadores 2022 por tipo
        tipos = [k for k in inst if k != 'progressao_por_tipo']
        inds_show = ['IAN', 'IDA', 'IEG', 'IAA', 'INDE']
        header = '| Tipo | n | ' + ' | '.join(inds_show) + ' |'
        sep    = '|------|---|' + '---|' * len(inds_show)
        w(header)
        w(sep)
        for tipo in tipos:
            entry = inst[tipo]
            n = entry['n']
            vals = [f"{entry['indicadores'].get(ind, 'N/A'):.3f}" if isinstance(entry['indicadores'].get(ind), float) else 'N/A' for ind in inds_show]
            w(f"| {tipo} | {n} | " + ' | '.join(vals) + ' |')
        w()
        if 'progressao_por_tipo' in inst:
            w('**Progressão de Pedra por tipo:**\n')
            w('| Tipo | n | Progrediu | Manteve | Regrediu |')
            w('|------|---|-----------|---------|----------|')
            for tipo, prog in inst['progressao_por_tipo'].items():
                w(f"| {tipo} | {prog['n']} | {prog['progrediu']} ({prog['pct_progrediu']}%) | {prog['manteve']} ({prog['pct_manteve']}%) | {prog['regrediu']} ({prog['pct_regrediu']}%) |")
        w()
        w('> Alunos de escola pública têm IAN e IDA inferiores, mas apresentam o **maior IEG** — engajamento independe do capital acadêmico prévio.\n')

    # Insight 6
    w('### Insight 6 — INDICADO_BOLSA: Marcador de Mobilidade Social\n')
    if p11.get('insight6_mobilidade'):
        mob = p11['insight6_mobilidade']

        w('**Distribuição BOLSISTA_2022:**', str(mob.get('n_bolsista', {})))
        w('\n**Distribuição INDICADO_BOLSA_2022:**', str(mob.get('n_indicado', {})))
        w()

        if 'parte_b_indicado' in mob:
            w('#### Indicadores: Indicado Sim vs Não (2022)\n')
            w('| Indicador | Não indicado | Indicado | Δ (Sim−Não) |')
            w('|-----------|-------------|----------|-------------|')
            for ind, entry in mob['parte_b_indicado'].items():
                nao = entry['medias'].get('Não', 'N/A')
                sim = entry['medias'].get('Sim', 'N/A')
                dif = entry['dif_sim_nao']
                sinal = '+' if dif >= 0 else ''
                w(f"| {ind} | {nao} | {sim} | {sinal}{dif} |")
            w()

        if 'ranking_diferenca' in mob:
            w('**Ranking por diferença absoluta (Sim−Não):**')
            for entry in mob['ranking_diferenca']:
                sinal = '+' if entry['dif'] >= 0 else ''
                w(f"\n- {entry['indicador']}: {sinal}{entry['dif']}")
            w()

        if 'origem_escolar_indicados' in mob:
            w('\n**Origem escolar dos indicados:**\n')
            w('| Tipo de Instituição | n | % |')
            w('|---------------------|---|---|')
            for tipo, entry in mob['origem_escolar_indicados'].items():
                w(f"| {tipo} | {entry['n']} | {entry['pct']}% |")
            w()

        if 'pipeline_indicado_x_bolsista' in mob:
            w('**Pipeline INDICADO × BOLSISTA:**')
            w('\n> Overlap entre indicados e bolsistas = 0 (estágios sequenciais, não simultâneos).\n')

    w('\n### Tese Central\n')
    if p11.get('tese_central'):
        w(f"> {p11['tese_central']}\n")
else:
    w('> output_p11.json não encontrado — rode `python p11_insights.py`\n')

w('\n---\n')
w(f'*Gerado automaticamente por `gerar_md.py` em {date.today()}*')

# Escrever arquivo
content = '\n'.join(lines)
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'Arquivo gerado: {OUTPUT_FILE}')
print(f'Total de linhas: {len(lines)}')
