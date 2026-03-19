# Datathon POSTECH DTAT — Passos Mágicos

**Aluno:** Renato Ferreira — RM 384836
**Curso:** POSTECH Data Analytics — Fase 5
**Programa analisado:** [Passos Mágicos](https://passosmagicos.org.br) — ONG que apoia o desenvolvimento educacional de crianças e jovens em situação de vulnerabilidade social (Embu-Guaçu, SP)

---

## Objetivo

Analisar os dados educacionais do programa Passos Mágicos (2020–2022) para responder 11 perguntas de pesquisa, construir um modelo preditivo de risco de defasagem curricular e propor um sistema de recomendações de intervenção preventiva.

---

## Estrutura do Repositório

```
├── app.py                          # Streamlit app (raiz — deploy)
├── modelo_risco.pkl                # Modelo treinado (LR + RF + scaler)
├── requirements.txt
│
├── notebooks/
│   └── DATATHON-ANALISE.ipynb      # Notebook principal — análise completa (P1–P11)
│
├── src/                            # Scripts de análise
│   ├── p8_inde.py
│   ├── p9_modelo.py
│   ├── p10_efetividade.py
│   ├── p11_insights.py
│   ├── gerar_md.py
│   └── validacao_estatistica.py
│
├── outputs/                        # JSONs gerados pelos scripts
│   └── output_p*.json
│
├── figures/                        # Figuras geradas (gitignored)
│   └── fig_*.png
│
├── docs/                           # Documentação
│   ├── ANALISE_CONSOLIDADA.md
│   └── NOTAS_VALIDACAO.md
│
└── data/                           # Gitignored — dados de terceiros
    └── PEDE_PASSOS_DATASET_FIAP.csv
```

---

## Dataset

**Fonte:** `PEDE_PASSOS_DATASET_FIAP.csv`
**Registros:** 1.349 alunos × 69 colunas
**Período:** 2020, 2021 e 2022 (colunas sufixadas por ano)
**Separador:** ponto e vírgula (`;`)

**Indicadores principais:**

| Indicador | Descrição |
|-----------|-----------|
| IAN | Adequação de Nível (alinhamento curricular) |
| IDA | Desempenho Acadêmico |
| IEG | Engajamento |
| IAA | Autoavaliação |
| IPS | Aspectos Psicossociais |
| IPP | Aspectos Psicopedagógicos |
| IPV | Ponto de Virada |
| **INDE** | Índice de Desenvolvimento Educacional (composto) |
| PEDRA | Fase do aluno: Quartzo < Ágata < Ametista < Topázio |

---

## Como Rodar

```bash
# 1. Criar e ativar ambiente virtual
python -m venv .venv
source .venv/Scripts/activate   # Git Bash / WSL
# .venv\Scripts\activate        # Windows CMD

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Rodar o Streamlit app
streamlit run app.py

# 4. Abrir o notebook
jupyter notebook notebooks/DATATHON-ANALISE.ipynb

# 5. Regenerar JSONs e figuras (rodar de dentro de src/)
cd src
python p8_inde.py && python p9_modelo.py && python p10_efetividade.py && python p11_insights.py && python gerar_md.py
```

---

## Modelo Preditivo (Pergunta 9)

**Problema:** prever se um aluno terá defasagem curricular em 2022 (`IAN_2022 < 10`) usando indicadores de 2020 e 2021.

**Features:** 18 (6 indicadores × 2 anos + 6 deltas de evolução)
**Split:** 80% treino estratificado / 20% holdout
**Validação:** 5-fold Stratified Cross-Validation

| Modelo | AUC-CV | F1-CV | AUC-Holdout | F1-Holdout |
|--------|--------|-------|-------------|------------|
| **Logistic Regression** | 0.802 | 0.840 | **0.907** | **0.889** |
| Random Forest | 0.809 | 0.874 | 0.866 | 0.879 |
| XGBoost | 0.784 | 0.863 | 0.827 | 0.879 |

**Modelo em produção:** Logistic Regression (melhor AUC holdout + interpretabilidade via coeficientes).

> ⚠️ **Limitação:** coorte longitudinal de apenas 314 alunos (~23% da base). Modelo é um indicador de direção para intervenção preventiva.

---

## Principais Achados

- **INDE discrimina Pedras** com altíssima significância estatística (Kruskal-Wallis H=777, p≈0)
- **IDA** é o indicador mais correlacionado com INDE (Spearman r=0.74–0.82 nos 3 anos)
- **INDE** caiu em 2021 (7.296→6.888) e recuperou parcialmente em 2022 (7.028) — não houve crescimento consistente
- **Vetores reais de indicação para bolsa:** IPP (+0.987) e IDA (+0.944), não IEG (8º lugar, +0.218)
- **ANOS_PM** não tem correlação significativa com INDE (Spearman r=−0.075, p=0.176)
- **61.4%** dos indicados para bolsa vêm de escola privada

Veja `NOTAS_VALIDACAO.md` para documentação completa do processo de validação.

---

## Streamlit App

O app permite inserir os indicadores de um aluno (2020 e 2021) e obter:
- Probabilidade de defasagem em 2022 (gauge visual)
- Nível de risco: BAIXO / MÉDIO / ALTO
- Radar chart do perfil do aluno
- Evolução por indicador (deltas)
- Recomendações de intervenção priorizadas

**Deploy:** [https://datathon-fase5-fiap-paapps-magicos-d5bwxdafu6dtfp2gjfj4gr.streamlit.app](https://datathon-fase5-fiap-paapps-magicos-d5bwxdafu6dtfp2gjfj4gr.streamlit.app)

---

## Rigor Analítico — Hipóteses Testadas e Corrigidas

A análise incluiu uma etapa de **validação estatística independente** que precedeu a redação das conclusões. O processo identificou **4 divergências materiais** entre as hipóteses iniciais e os dados:

| # | Hipótese inicial | O que os dados mostraram |
|---|-----------------|--------------------------|
| 1 | IEG seria o principal diferenciador para bolsas | IEG é o **último** (8º lugar). IPP (+0,987) e IDA (+0,944) lideram |
| 2 | Mais anos no programa → maior INDE | Spearman r = −0,075, **p = 0,176** — não significativo |
| 3 | Escola pública = principal grupo de indicados | **61,4% dos indicados** vêm de escola privada |
| 4 | INDE cresceu consistentemente 2020–2022 | Queda em 2021 (7,296→6,888), recuperação parcial em 2022 (7,028) |

Todas as conclusões foram corrigidas antes da versão final. Documentação completa em [`docs/NOTAS_VALIDACAO.md`](docs/NOTAS_VALIDACAO.md).

---

## Validação Estatística

Processo de validação independente em 5 etapas (`src/validacao_estatistica.py`):

1. Integridade da base — cobertura, NaN estrutural, valores inválidos (D9XX, #NULO!)
2. Estatísticas descritivas por indicador (média, mediana, skewness, normalidade)
3. Correlações Spearman com p-valores explícitos
4. Investigações específicas (IPP, IPS, ANOS_PM, escola pública)
5. Verificações de coerência entre hipóteses narrativas e dados

Nenhum indicador segue distribuição normal (Shapiro-Wilk p < 0,05 em todos) — justificando o uso de **testes não-paramétricos** (Spearman, Kruskal-Wallis) em todas as análises.
