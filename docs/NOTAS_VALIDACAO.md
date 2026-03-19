# Notas de Validação Estatística

**Projeto:** Datathon POSTECH DTAT — Fase 5 | Passos Mágicos
**Aluna:** Ana Raquel
**Data:** 2026-03-18
**Script de validação:** `validacao_estatistica.py` → `output_validacao.json`

---

## Por que esta validação foi feita

Antes de redigir as conclusões finais, realizamos uma validação independente da base de dados
e de todos os números produzidos pelas análises. O objetivo foi:

1. Confirmar a integridade estrutural do dataset
2. Caracterizar cada indicador estatisticamente (distribuição, outliers, normalidade)
3. Medir correlações com p-valores (não apenas coeficientes)
4. Identificar incoerências entre hipóteses narrativas e os dados

Esse processo revelou **4 divergências materiais** em relação às hipóteses iniciais, descritas abaixo.

---

## Qualidade dos Dados — Problemas Identificados na Base

Varredura sistemática de todas as 43 colunas categóricas e numéricas do dataset.

### Categoria A — Registros corrompidos (tratados como NaN pelo código)

| Problema | Coluna(s) | Valor inválido | Registros afetados |
|----------|-----------|----------------|--------------------|
| Registro inteiro corrompido | Todos os indicadores 2020 | `D9XX` (D970, D940, D980…) | **1** (ALUNO-1259) |
| Null do Excel exportado | PEDRA_2021, INDE_2021, PONTO_VIRADA_2021 | `#NULO!` | **2** (ALUNO-71, ALUNO-506) |
| Valor inválido de nível | NIVEL_IDEAL_2021 | `ERRO` | **2** (ALUNO-374, ALUNO-1196) |

**Impacto:** nenhum — todos descartados automaticamente por `pd.to_numeric(errors='coerce') + dropna()`.
Os 2 registros com `ERRO` em NIVEL_IDEAL têm PEDRA e INDE válidos; apenas o campo de nível ideal está quebrado.

### Categoria B — Inconsistência de nomenclatura entre anos (armadilhas para análise cruzada)

**NIVEL_IDEAL renomeado de 2021 para 2022:**

| 2021 | 2022 |
|------|------|
| Nível 1 (4o ano) | Fase 1 (4º ano) |
| Nível 2 (5o e 6o ano) | Fase 2 (5º e 6º ano) |
| … | … |
| Nível 8 (Universitários) | Fase 8 (Universitários) |

Comparação direta entre anos retornaria 0 matches. **Não afeta nossas análises** (coluna não utilizada).

**INSTITUICAO_ENSINO_ALUNO com nomes diferentes por ano:**

| 2020 | 2021 |
|------|------|
| Escola João Paulo II | Escola JP II |
| Rede Decisão/União | Rede Decisão |
| UNISA, Einstein, Estácio, FIAP, V202 | *(ausentes)* |

Não existe `INSTITUICAO_ENSINO_ALUNO_2022`. Rastrear aluno por instituição entre anos retornaria falsos negativos. A análise de escola pública foi feita corretamente usando apenas o campo de 2022 (`INSTITUICAO_ENSINO_ALUNO_2020` como proxy para origem escolar dos indicados).

### Categoria C — Estrutura diferente em 2022 (methodologia expandida)

- `NOTA_ING_2022`: apenas **285 de 860 alunos** têm nota de inglês (vs 860 com Port e Mat). Alunos de ALFA/Fase 1 não têm inglês — `IDA_2022` para eles é calculado com 2 notas em vez de 3. Já embutido no campo pré-calculado da base.
- Coluna `REC_EQUIPE_N_2021` renomeada para `REC_AVA_N_2022` — mesmo conteúdo, nome diferente.
- 2022 tem 30 colunas vs 18 em 2020 (expansão da metodologia, não erro).

### Resumo de impacto real

| Categoria | Impacto nas análises |
|-----------|----------------------|
| Registros corrompidos (D9XX, #NULO!, ERRO) | **Nenhum** — descartados por `dropna()` |
| NIVEL_IDEAL renomeado | **Nenhum** — coluna não usada |
| INSTITUICAO nomes diferentes | **Baixo** — análise usa apenas campo 2022 |
| NOTA_ING_2022 parcial | **Baixo** — já embutido no IDA_2022 pré-calculado |
| Problema original `Ágata` | **Corrigido** — código comparava `upper()=='AGATA'` mas `'Ágata'.upper()=='ÁGATA'`; fix aplicado em P8 e P7 |

---

## Etapa 1 — Validação da Base

| Ano | Alunos com dados | NaN INDE |
|-----|-----------------|----------|
| 2020 | 728 | 46.0% |
| 2021 | 686 | 49.1% |
| 2022 | 862 | 36.1% |

**Achado:** O padrão de NaN é **estrutural** (ausência = aluno não matriculado naquele ano), não aleatório.
Todos os indicadores têm a mesma taxa de NaN por ano, o que confirma que o missing reflete
a coorte transversal de cada período — não falha de coleta.

**Implicação:** Comparações de médias entre anos refletem **populações diferentes** a cada ano.
Apenas 314 alunos (~23% da base) têm dados nos 3 anos. Análises longitudinais devem ser
explicitamente rotuladas como "coorte restrita".

**Achado adicional — 2022 tem metodologia diferente:**
- `IDA_2022` = média de `NOTA_PORT`, `NOTA_MAT`, `NOTA_ING` (notas de prova)
- `IDA_2020/2021` = avaliação pedagógica por faixa
- `IPP` usa 3 fórmulas distintas nos 3 anos
- 2022 tem 30 colunas vs 18 em 2020 — expansão da metodologia

**Conclusão:** Comparações diretas de IDA e IPP entre anos devem ser acompanhadas de ressalva explícita.

---

## Etapa 2 — Estatísticas por Indicador (2020, referência)

| Indicador | n | Média | Mediana | Std | Skew | Normal? |
|-----------|---|-------|---------|-----|------|---------|
| IAN | 727 | 7.43 | 5.00 | 2.56 | -0.39 | Não |
| IDA | 727 | 6.32 | 7.00 | 2.96 | -0.82 | Não |
| IEG | 727 | 7.68 | 8.50 | 2.38 | -1.47 | Não |
| IAA | 727 | 8.37 | 8.75 | 1.73 | -2.12 | Não |
| IPS | 727 | 6.74 | 7.50 | 1.37 | -0.73 | Não |
| IPP | 727 | 7.07 | 7.50 | 1.99 | -0.72 | Não |
| IPV | 727 | 7.24 | 7.58 | 1.78 | -0.82 | Não |
| **INDE** | 727 | **7.30** | **7.58** | 1.20 | -0.53 | Não |

**Achado:** Nenhum indicador segue distribuição normal (Shapiro-Wilk p < 0.05 em todos).
Isso justifica o uso de **testes não-paramétricos** (Spearman, Kruskal-Wallis) em vez de Pearson/ANOVA.
Todas as correlações foram calculadas com Spearman e p-valores explícitos.

---

## Etapa 3 — Correlações com INDE (Spearman + p-valor)

| Indicador | r 2020 | r 2021 | r 2022 | Significativo? |
|-----------|--------|--------|--------|----------------|
| IAN | 0.320 | 0.247 | 0.424 | *** (todos) |
| IDA | 0.740 | 0.784 | 0.817 | *** |
| IEG | 0.594 | 0.611 | 0.742 | *** |
| IAA | 0.474 | 0.480 | 0.474 | *** |
| IPS | 0.398 | 0.316 | 0.328 | *** |
| IPP | 0.619 | 0.612 | 0.589 | *** |
| IPV | 0.552 | 0.572 | 0.628 | *** |

**IDA é consistentemente o indicador mais correlacionado com INDE** (r ≈ 0.74–0.82),
seguido de IEG (r ≈ 0.59–0.74) e IPP (r ≈ 0.59–0.62).

**Pares de alta correlação (2022, r > 0.6):**
- IDA × INDE: r = 0.817, p ≈ 0
- IEG × INDE: r = 0.742, p ≈ 0
- IDA × IPV: r = 0.628, p ≈ 0

---

## Etapa 5 — Verificações de Coerência (4 Divergências Identificadas)

### Divergência 1 — Tese central: IEG não é o principal diferenciador para INDICADO_BOLSA

**Hipótese original:** IEG seria o principal vetor de resultado e o principal diferenciador
dos alunos indicados para bolsa.

**Dado validado (ranking de diferença Indicado Sim − Não):**

| Posição | Indicador | Δ (Sim − Não) |
|---------|-----------|---------------|
| 1 | **IPP** | **+0.987** |
| 2 | **IDA** | **+0.944** |
| 3 | IPV | +0.720 |
| 4 | INDE | +0.455 |
| 5 | IPS | +0.366 |
| 6 | IAN | −0.314 |
| 7 | IAA | −0.250 |
| **8 (último)** | **IEG** | **+0.218** |

**Conclusão:** IEG é o *menos* diferenciador entre os indicados. O critério de indicação prioriza
**suporte psicopedagógico (IPP)** e **desempenho acadêmico (IDA)** — não engajamento.

**Tese revisada:** vetores centrais da indicação para bolsa são IPP e IDA.

---

### Divergência 2 — ANOS_PM: tempo no programa não tem efeito significativo no INDE

**Hipótese original:** mais anos no programa → maior INDE (impacto cumulativo positivo).

**Dado validado:**
- Spearman r = −0.075, p = 0.176 → **não significativo**
- INDE por grupo: 0 anos=7.26, 1 ano=6.94, 2 anos=6.84, 3 anos=6.90, 4 anos=7.08

A relação não é monotônica positiva. Provavelmente há **efeito de seleção**: alunos que entram
recentemente podem já ter perfil de maior desempenho relativo ao ano em que ingressam.

**Conclusão:** O claim "cada ano adicional está associado a melhora mensurável" **não é
estatisticamente sustentado** (p = 0.176).

---

### Divergência 3 — Escola pública não é o principal grupo de indicados para bolsa

**Hipótese original:** alunos de escola pública constituiriam o principal grupo candidato a bolsas.

**Dado validado (origem escolar dos indicados):**

| Tipo | n | % |
|------|---|---|
| **Privada** | 81 | **61.4%** |
| Pública | 49 | 37.1% |
| Comunitária | 2 | 1.5% |

**Conclusão:** A maioria dos indicados (61.4%) vem de escola **privada**, não pública.
A hipótese não é sustentada pelos dados (threshold < 50%).

---

### Divergência 4 — INDE geral não cresceu consistentemente de 2020 a 2022

**Dado validado:**

| Ano | INDE médio | n |
|-----|-----------|---|
| 2020 | **7.296** | 727 |
| 2021 | **6.888** | 684 |
| 2022 | **7.028** | 862 |

O INDE caiu −0.408 em 2021 e recuperou parcialmente +0.140 em 2022, mas **não atingiu
o nível de 2020**. A conclusão "crescimento consistente de 2020 para 2022" está incorreta.

**Ressalva metodológica:** as populações de cada ano são diferentes (coorte transversal),
e a metodologia de alguns indicadores muda em 2022 — por isso a queda pode ser parcialmente
artefato metodológico, não necessariamente queda real de desempenho.

---

### Discriminação por Pedra — validado

Kruskal-Wallis INDE × Pedra: **H = 777.16, p ≈ 0**

O INDE discrimina as Pedras com altíssima significância estatística — o índice composto
cumpre sua função classificatória de forma robusta.

---

## Evidências do Processo de Validação

| Artefato | Descrição |
|----------|-----------|
| `validacao_estatistica.py` | Script completo de validação (5 etapas) |
| `output_validacao.json` | Resultados estruturados: stats, correlações, coerência |
| `fig_validacao_correlacoes.png` | Heatmap Spearman 2022 com p-valores |
| `fig_validacao_distribuicoes.png` | Histogramas + boxplots por indicador e ano |
| `fig_validacao_dispersao.png` | Scatter IDA/IEG/IPP vs INDE (2022) |

---

## Como usar estas notas

Estas notas documentam que as análises foram revisadas e corrigidas à luz dos dados.
As correções materiais estão refletidas nas conclusões das Perguntas 10 e 11
e na tese central revisada do projeto.

*Gerado em 2026-03-18*
