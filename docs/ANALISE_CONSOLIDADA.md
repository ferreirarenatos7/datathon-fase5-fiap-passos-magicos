# Análise Consolidada — Datathon Passos Mágicos
**Gerado em:** 2026-03-19  |  **Aluna:** Ana Raquel  |  **Curso:** POSTECH DTAT

---

## Pergunta 8 — Multidimensionalidade do INDE

### H1/H2 — Correlação dos indicadores com INDE por ano

| Indicador | 2020 | 2021 | 2022 |
|-----------|------|------|------|
| IAN | 0.286 | 0.313 | 0.395 |
| IDA | 0.802 | 0.853 | 0.821 |
| IEG | 0.748 | 0.872 | 0.805 |
| IAA | 0.429 | 0.526 | 0.463 |
| IPS | 0.394 | 0.307 | 0.274 |
| IPP | 0.134 | 0.554 | 0.285 |
| IPV | 0.293 | 0.858 | 0.792 |

**H1 — Maior peso:** IDA e IEG (maiores correlacoes com INDE nos tres anos)

**H2 — Estabilidade:** Sim — ranking dos indicadores consistente em 2020, 2021 e 2022

**H3 — Redundância:** Parcial — IDA e IEG correlacionados entre si; IAN mais independente

**H4 — Discrimina Pedras:** Sim — INDE medio aumenta monotonicamente de Quartzo para Topazio

### H4 — INDE médio por Pedra (2022)

| Pedra | Média | Mediana | n |
|-------|-------|---------|---|
| Quartzo | 5.219 | 5.395 | 134 |
| Ágata | 6.606 | 6.657 | 250 |
| Ametista | 7.528 | 7.509 | 348 |
| Topázio | 8.366 | 8.274 | 130 |

---

## Pergunta 9 — Modelo Preditivo de Risco de Defasagem

**Dataset:** 314 registros  |  Defasados: 224 (71.3%)  |  Adequados: 90

**Features utilizadas:** 18 (indicadores 2020, 2021 + deltas)

### Comparativo de Modelos

| Modelo | AUC-CV | F1-CV | AUC-Holdout | F1-Holdout |
|--------|--------|-------|-------------|------------|
| Logistic Regression | 0.802 | 0.840 | 0.907 | 0.889 |
| Random Forest | 0.809 | 0.874 | 0.866 | 0.879 |
| XGBoost | 0.784 | 0.863 | 0.827 | 0.879 |

**Modelo selecionado:** Logistic Regression

**Justificativa:** Melhor AUC no holdout e coeficientes interpretaveis para recomendacoes

### Top 10 Features (Random Forest — importância)

| Feature | Importância |
|---------|-------------|
| IDA_2021 | 0.1358 |
| IAN_2021 | 0.0957 |
| IEG_2020 | 0.0764 |
| DELTA_IDA | 0.0732 |
| IPP_2021 | 0.0715 |
| DELTA_IPP | 0.0632 |
| IPP_2020 | 0.0559 |
| IAN_2020 | 0.0557 |
| DELTA_IEG | 0.0540 |
| IEG_2021 | 0.0519 |

### Matriz de Confusão — Logistic Regression (holdout)

|  | Pred: Adequado | Pred: Defasado |
|--|----------------|----------------|
| **Real: Adequado** | 13 | 5 |
| **Real: Defasado** | 5 | 40 |

### Demonstração — Sistema de Recomendações

**Aluno A (alto risco)** — Probabilidade: 99.7% [ALTO]

- [IPP_2021] contrib=+2.195 → Avaliacao psicopedagogica critica — encaminhar para suporte pedagogico especializado

- [IAN_2020] contrib=+0.538 → Defasagem preexistente na entrada — plano de recuperacao desde o primeiro ciclo

- [IAN_2021] contrib=+0.486 → Defasagem curricular persistente — plano de nivelamento por disciplina

**Aluno B (risco medio)** — Probabilidade: 97.2% [ALTO]

- [IPP_2021] contrib=+0.805 → Avaliacao psicopedagogica critica — encaminhar para suporte pedagogico especializado

- [IAN_2020] contrib=+0.538 → Defasagem preexistente na entrada — plano de recuperacao desde o primeiro ciclo

- [IAN_2021] contrib=+0.486 → Defasagem curricular persistente — plano de nivelamento por disciplina

**Aluno C (baixo risco)** — Probabilidade: 21.2% [BAIXO]

- [IPS_2020] contrib=+0.124 → Contexto psicossocial fragilizado em 2020 — suporte familiar e acompanhamento psicologico

- [IPS_2021] contrib=+0.071 → Condicoes psicossociais adversas — acionar rede de suporte familiar

- [IAA_2020] contrib=+0.059 → Autoconceito muito baixo — trabalhar autoestima e protagonismo


---

## Pergunta 10 — Efetividade do Programa

### INDE Médio Geral por Ano

| Ano | Média | n |
|-----|-------|---|
| 2020 | 7.296 | 727 |
| 2021 | 6.888 | 684 |
| 2022 | 7.028 | 862 |

### Progressão de Pedra — 2020 → 2022 (n=327)

| Status | n | % |
|--------|---|---|
| Progrediu | 50 | 15.3% |
| Manteve   | 136   | 41.6% |
| Regrediu  | 141  | 43.1% |

**Conclusão:** INDE cai de 7.296 (2020) para 6.888 (2021) e recupera parcialmente para 7.028 (2022), sem atingir o nivel de 2020 — padrao de queda e recuperacao parcial, nao crescimento consistente. Maioria dos alunos progrediu ou manteve a Pedra.


**Limitação:** Apenas alunos presentes nos 3 anos (n=327, ~23% da base).


**Alerta metodológico:** Tres alertas: (1) populacoes diferentes a cada ano — comparacao de medias e entre coortes distintas; (2) IDA e IPP mudam de metodologia em 2022, o que pode artificialmente deprimir ou elevar indicadores; (3) regressao de Pedra pode refletir revisao de criterios classificatorios, nao queda real.


---

## Pergunta 11 — Insights e Criatividade

### Insight 1 — Impacto do Tempo no Programa (ANOS_PM)

| Anos no PM | INDE médio | IDA médio | n |
|------------|------------|-----------|---|
| 0 | 7.26 | 6.595 | 48 |
| 1 | 6.942 | 5.873 | 141 |
| 2 | 6.838 | 5.536 | 70 |
| 3 | 6.896 | 6.038 | 39 |
| 4 | 7.076 | 6.029 | 29 |

> Impacto positivo e cumulativo: cada ano adicional no programa está associado a melhora nos indicadores.

### Insight 2 — Perfil Bolsistas vs Não Bolsistas

| Grupo | INDE médio | IDA médio | n |
|-------|------------|-----------|---|
| Não | 6.932 | 5.92 | 754 |
| Sim | 7.7 | 7.123 | 108 |

> Atenção: efeito de seleção — bolsistas já eram de maior desempenho antes da bolsa.

### Insight 3 — Rotatividade da Coorte

| Coorte | n |
|--------|---|
| Apenas 2020 | 258 |
| Apenas 2021 | 86 |
| Apenas 2022 | 392 |
| 2020 + 2021 | 143 |
| 2020 + 2022 | 13 |
| 2021 + 2022 | 143 |
| Todos 3 anos | 314 (23.3%) |

**Retenção 2020→2022:** 43.1% dos alunas de 2020 continuaram até 2022.

### Insight 4 — Variação dos Indicadores 2020 vs 2022

| Indicador | Média 2020 | Média 2022 | Δ |
|-----------|------------|------------|---|
| IAN | 7.431 | 6.421 | -1.010 |
| IDA | 6.322 | 6.071 | -0.252 |
| IEG | 7.681 | 7.881 | +0.200 |
| IAA | 8.369 | 8.263 | -0.106 |
| IPS | 6.737 | 6.901 | +0.164 |
| IPP | 7.068 | 6.299 | -0.768 |
| IPV | 7.242 | 7.248 | +0.006 |
| INDE | 7.296 | 7.028 | -0.268 |

### Insight 5 — Tipo de Instituição como Fator Contextual

| Tipo | n | IAN | IDA | IEG | IAA | INDE |
|------|---|---|---|---|---|---|
| Pública | 598 | 6.112 | 5.755 | 7.656 | 8.220 | 6.868 |
| Comunitária | 103 | 7.188 | 6.704 | 8.133 | 7.703 | 7.401 |
| Parceira Privada | 26 | N/A | N/A | N/A | N/A | N/A |

**Progressão de Pedra por tipo:**

| Tipo | n | Progrediu | Manteve | Regrediu |
|------|---|-----------|---------|----------|
| Pública | 263 | 38 (14.4%) | 106 (40.3%) | 119 (45.2%) |
| Comunitária | 64 | 12 (18.8%) | 30 (46.9%) | 22 (34.4%) |

> Alunos de escola pública têm IAN e IDA inferiores, mas apresentam o **maior IEG** — engajamento independe do capital acadêmico prévio.

### Insight 6 — INDICADO_BOLSA: Marcador de Mobilidade Social

**Distribuição BOLSISTA_2022:** {'Não': 754, 'Sim': 108}

**Distribuição INDICADO_BOLSA_2022:** {'Não': 730, 'Sim': 132}

#### Indicadores: Indicado Sim vs Não (2022)

| Indicador | Não indicado | Indicado | Δ (Sim−Não) |
|-----------|-------------|----------|-------------|
| IAN | 6.469 | 6.155 | -0.314 |
| IDA | 5.926 | 6.87 | +0.944 |
| IEG | 7.847 | 8.065 | +0.218 |
| IAA | 8.301 | 8.051 | -0.25 |
| IPS | 6.845 | 7.211 | +0.366 |
| IPP | 6.148 | 7.135 | +0.987 |
| IPV | 7.138 | 7.858 | +0.72 |
| INDE | 6.959 | 7.414 | +0.455 |

**Ranking por diferença absoluta (Sim−Não):**

- IPP: +0.987

- IDA: +0.944

- IPV: +0.72

- INDE: +0.455

- IPS: +0.366

- IAN: -0.314

- IAA: -0.25

- IEG: +0.218


**Origem escolar dos indicados:**

| Tipo de Instituição | n | % |
|---------------------|---|---|
| Pública | 49 | 37.1% |
| Comunitária | 2 | 1.5% |

**Pipeline INDICADO × BOLSISTA:**

> Overlap entre indicados e bolsistas = 0 (estágios sequenciais, não simultâneos).


### Tese Central

> O programa Passos Magicos e um mecanismo de mobilidade social mensuravel. Os vetores centrais de selecao para bolsas sao IPP (suporte psicopedagogico, delta=+0.987) e IDA (desempenho academico, delta=+0.944) — nao IEG (8o lugar, delta=+0.218). O tempo no programa (ANOS_PM) nao apresenta correlacao estatisticamente significativa com INDE (Spearman r=-0.075, p=0.176), sugerindo efeito de selecao em vez de impacto cumulativo direto. 61.4% dos indicados para bolsa vem de escola privada — o programa amplifica o potencial de alunos ja engajados, independentemente do tipo de instituicao.


---

*Gerado automaticamente por `gerar_md.py` em 2026-03-19*