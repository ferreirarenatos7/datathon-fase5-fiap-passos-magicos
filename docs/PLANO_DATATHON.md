# Plano de Entrega — Datathon Fase 5 | Passos Mágicos
**Aluna:** Ana Raquel | **Curso:** POSTECH DTAT — Data Analytics

---

## Arquivos do Projeto

| Arquivo | Descricao |
|---------|-----------|
| `DATATHON-ANALISE.ipynb` | Notebook principal de trabalho |
| `PEDE_PASSOS_DATASET_FIAP.csv` | Dataset principal (2020, 2021, 2022) |
| `PEDE_PASSOS_DATASET_FIAP.xlsx` | Copia identica do CSV em formato Excel — descartada |
| `Base de dados - Passos Magicos.zip` | Banco relacional bruto (dados ate junho/2024) — uso auxiliar |
| `dados_2022_2023_2024_padronizados.txt` | Dicionario de padronizacao de colunas — referencia |
| `PLANO_DATATHON.md` | Este arquivo de acompanhamento |

---

## Decisao sobre a Base de Dados

**Base escolhida: `PEDE_PASSOS_DATASET_FIAP.csv`**

**Justificativa:**

Foram avaliados os seguintes arquivos disponiveis:

1. `PEDE_PASSOS_DATASET_FIAP.csv` — Dataset pre-processado com todos os indicadores calculados (IAN, IDA, IEG, IAA, IPS, IPP, IPV, INDE) para os anos 2020, 2021 e 2022. 1.349 registros de alunas. Unico arquivo que contem os indicadores especificos exigidos pelas 11 perguntas do datathon.

2. `PEDE_PASSOS_DATASET_FIAP.xlsx` — Copia identica ao CSV, apenas em formato diferente. Descartado por redundancia.

3. `Base de dados - Passos Magicos.zip` — Banco de dados relacional bruto com multiplas tabelas (alunas, notas, frequencia, turmas, professores). Contem dados ate junho de 2024, porem sem os indicadores calculados. Exigiria joins complexos entre tabelas para chegar nos mesmos indicadores. Disponivel como fonte auxiliar caso necessario.

4. `dados_2022_2023_2024_padronizados.txt` — Dicionario de padronizacao de colunas indicando que existiriam dados de 2023 e 2024 (inde_23, pedra_23, inde_24, pedra_24), porem esses dados nao estao disponiveis em nenhum dos arquivos fornecidos com os indicadores calculados.

**Conclusao:** O CSV e a unica base com os indicadores necessarios para o datathon. A analise sera baseada nos anos 2020, 2021 e 2022.

---

## Entregas Obrigatórias

- [ ] **GitHub** — repositório com código de limpeza e análise
- [ ] **Apresentação** — PPT ou PDF com storytelling
- [ ] **Notebook Python** — modelo preditivo completo
- [ ] **App Streamlit** — deploy no Community Cloud
- [ ] **Vídeo** — até 5 minutos apresentando resultados

---

## Fase 1 — Preparação dos Dados

- [x] Carregamento do CSV
- [x] Funções auxiliares (`filter_columns`, `cleaning_dataset`, etc.)
- [x] DataFrames separados por ano (df_2020, df_2021, df_2022)
- [ ] Tratamento de valores ausentes (NaN)
- [ ] Padronização de tipos de dados

---

## Fase 2 — Análises (11 Perguntas)

### Pergunta 1 — Adequação do Nível (IAN)
> Qual é o perfil geral de defasagem dos alunas e como ele evolui ao longo do ano?

- [ ] Distribuição do IAN por ano
- [ ] Percentual de alunas moderada/severamente defasados
- [ ] Evolução do IAN entre 2020, 2021 e 2022

---

### Pergunta 2 — Desempenho Acadêmico (IDA)
> O IDA está melhorando, estagnado ou caindo ao longo das fases e anos?

- [ ] IDA médio por ano
- [ ] IDA por fase (Quartzo, Ágata, Ametista, Topázio)
- [ ] Linha temporal da evolução

---

### Pergunta 3 — Engajamento (IEG)
> O IEG tem relação com IDA e IPV?

- [ ] Scatter plot IEG x IDA
- [ ] Scatter plot IEG x IPV
- [ ] Correlação estatística

---

### Pergunta 4 — Autoavaliação (IAA)
> A autoavaliação é coerente com desempenho real (IDA) e engajamento (IEG)?

- [ ] Scatter IAA x IDA
- [ ] Scatter IAA x IEG
- [ ] Análise de discrepância (alunas que se superestimam / subestimam)

---

### Pergunta 5 — Aspectos Psicossociais (IPS)
> Há padrões de IPS que antecedem quedas de desempenho?

- [ ] Correlação IPS x IDA por ano
- [ ] Análise temporal: IPS baixo em T → queda IDA em T+1?

---

### Pergunta 6 — Aspectos Psicopedagógicos (IPP)
> As avaliações psicopedagógicas confirmam ou contradizem o IAN?

- [ ] Comparação IPP x IAN
- [ ] Casos de divergência (IPP alto, IAN baixo e vice-versa)

---

### Pergunta 7 — Ponto de Virada (IPV)
> Quais comportamentos mais influenciam o IPV?

- [ ] Correlação de IDA, IEG, IPS, IAA com IPV
- [ ] Perfil de alunas que atingiram Ponto de Virada = Sim

---

### Pergunta 8 — Multidimensionalidade (INDE)
> Quais combinações de indicadores melhor explicam o INDE?

- [ ] Heatmap de correlação: IDA + IEG + IPS + IPP x INDE
- [ ] Análise de peso de cada indicador no INDE

---

### Pergunta 9 — Modelo Preditivo (ML)
> Construir modelo que prevê probabilidade de risco de defasagem.

- [ ] Feature engineering (deltas entre anos, flags de risco)
- [ ] Definição do target (ex: DEFASAGEM > 0 ou queda no INDE)
- [ ] Separação treino (2020+2021) / teste (2022)
- [ ] Treinar modelos: Random Forest, XGBoost, Logistic Regression
- [ ] Avaliação: AUC-ROC, F1, Matriz de Confusão
- [ ] Exportar modelo (`modelo_risco.pkl`)

---

### Pergunta 10 — Efetividade do Programa
> Os indicadores mostram melhora consistente nas fases ao longo do ciclo?

- [ ] Evolução por Pedra (Quartzo → Topázio) entre 2020 e 2022
- [ ] Taxa de progressão de pedra por aluna
- [ ] Comparativo geral do programa ao longo dos anos

---

### Pergunta 11 — Insights e Criatividade
> Insights adicionais além das perguntas.

- [ ] Impacto do tempo no programa (ANOS_PM) no desempenho
- [ ] Perfil de alunas bolsistas vs. não bolsistas
- [ ] Taxa de evasão (alunas presentes em 2020 mas não em 2022)
- [ ] Outros insights identificados durante a análise

---

## Fase 3 — App Streamlit

- [ ] Interface para inserir indicadores de um aluna
- [ ] Retornar probabilidade de risco de defasagem
- [ ] Visualizações dos indicadores do aluna
- [ ] Deploy no Streamlit Community Cloud

---

## Fase 4 — Entregáveis Finais

- [ ] Organizar repositório GitHub com README
- [ ] Criar apresentação PPT/PDF (storytelling)
- [ ] Gravar vídeo de até 5 minutos

---

## Legenda de Status

| Símbolo | Significado |
|---------|-------------|
| `[ ]` | Pendente |
| `[~]` | Em andamento |
| `[x]` | Concluído |
