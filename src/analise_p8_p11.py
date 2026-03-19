# %% [markdown]
"""
### Pergunta 8 — Multidimensionalidade do INDE

> Quais combinacoes de indicadores melhor explicam o INDE?

O INDE (Indice de Desenvolvimento Educacional) e o indicador-sintese do programa Passos Magicos.
Ele agrega os demais indicadores (IAN, IDA, IEG, IAA, IPS, IPP, IPV) em uma unica nota que
resume o desenvolvimento multidimensional do aluno.

**Hipoteses investigadas:**

- **H1:** Qual indicador tem maior peso individual no INDE?
- **H2:** A correlacao entre indicadores e INDE e estavel ao longo dos anos?
- **H3:** Ha indicadores redundantes (alta correlacao entre si)?
- **H4:** O INDE discrimina bem as Pedras (Quartzo < Ágata < Ametista < Topázio)?
"""

# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('./PEDE_PASSOS_DATASET_FIAP.csv', delimiter=';')

# H1 e H2 — Correlacao de cada indicador com INDE por ano
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

# %%
# H3 — Correlacao entre os proprios indicadores (2022)
cols_2022 = [f'{ind}_2022' for ind in indicadores_base if f'{ind}_2022' in df.columns]
cols_2022.append('INDE_2022')

df_corr = df[cols_2022].apply(pd.to_numeric, errors='coerce').dropna()
df_corr.columns = [c.replace('_2022', '') for c in df_corr.columns]

print(f'H3 — Matriz de correlacao entre indicadores (2022, n={len(df_corr)}):')
print(df_corr.corr().round(2).to_string())

# %%
# H4 — INDE por Pedra (distribuicao)
pedra_col  = 'PEDRA_2022'
inde_col   = 'INDE_2022'
pedra_order = ['Quartzo', 'Ágata', 'Ametista', 'Topázio']

df_h4 = df[[pedra_col, inde_col]].copy()
df_h4[inde_col] = pd.to_numeric(df_h4[inde_col], errors='coerce')
df_h4 = df_h4.dropna()

print('H4 — INDE medio por Pedra (2022):')
for pedra in pedra_order:
    g = df_h4[df_h4[pedra_col] == pedra][inde_col]
    if len(g) > 0:
        print(f'  {pedra:<12}: media={g.mean():.3f}  mediana={g.median():.3f}  n={len(g)}')

# %%
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

# --- Grafico 1: Heatmap de correlacao (2022) ---
corr_matrix = df_corr.corr()
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
sns.heatmap(corr_matrix, ax=axes[0], annot=True, fmt='.2f', cmap='RdYlGn',
            vmin=-1, vmax=1, mask=mask, square=True, linewidths=0.5,
            annot_kws={'size': 8})
axes[0].set_title('H3 — Correlacao entre\nIndicadores (2022)')

# --- Grafico 2: Correlacao de cada indicador com INDE por ano ---
x = np.arange(len(indicadores_base))
w = 0.25
anos = [2020, 2021, 2022]
cores_anos = ['#5bc0de', '#f0ad4e', '#5cb85c']
for j, (ano, cor) in enumerate(zip(anos, cores_anos)):
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

# --- Grafico 3: Boxplot INDE por Pedra ---
existentes_h4 = [p for p in pedra_order if p in df_h4[pedra_col].unique()]
data_box = [df_h4[df_h4[pedra_col] == p][inde_col].values for p in existentes_h4]
bp = axes[2].boxplot(data_box, labels=existentes_h4, patch_artist=True)
cores_pedra = {'Quartzo': '#d9534f', 'Ágata': '#f0ad4e',
               'Ametista': '#5bc0de', 'Topázio': '#5cb85c'}
for patch, pedra in zip(bp['boxes'], existentes_h4):
    patch.set_facecolor(cores_pedra.get(pedra, 'gray'))
    patch.set_alpha(0.7)
axes[2].set_title('H4 — Distribuicao do INDE\npor Pedra (2022)')
axes[2].set_ylabel('INDE')
axes[2].set_ylim(0, 10)

plt.suptitle('INDE — Multidimensionalidade, Correlacoes e Discriminacao por Pedra', fontsize=13)
plt.tight_layout()
plt.show()

# %% [markdown]
"""
#### Conclusao — Pergunta 8

| Hipotese | Resposta | Achado |
|----------|----------|--------|
| H1 — Maior peso individual? | **IDA e IEG** | Maiores correlacoes com INDE nos tres anos |
| H2 — Estabilidade temporal? | **Sim** | Ranking dos indicadores e consistente em 2020, 2021 e 2022 |
| H3 — Ha redundancia? | **Parcial** | IDA e IEG correlacionados entre si; IAN e mais independente |
| H4 — INDE discrimina Pedras? | **Sim — com clareza** | INDE medio aumenta monotonicamente de Quartzo para Topázio |

**Interpretacao:**

O INDE e um indice coerente: discrimina bem as fases do programa (Pedras) e reflete
de forma estavel os indicadores de desempenho e engajamento ao longo dos tres anos.

IDA e IEG sao os componentes de maior peso, o que confirma a logica pedagogica do programa:
desempenho academico e participacao ativa sao as dimensoes centrais do desenvolvimento.

O IAN tem menor correlacao com INDE, o que e consistente com seu perfil discreto (apenas 3 valores
possiveis: 2.5, 5.0, 10.0) — ele sinaliza defasagem curricular mas nao captura a riqueza do
desenvolvimento multidimensional medido pelo INDE.

A estrutura de correlacoes e estavel nos tres anos, o que valida a robustez do modelo de indicadores
mesmo com as mudancas metodologicas identificadas na Secao 1.8.
"""

# %% [markdown]
"""
### Pergunta 9 — Modelo Preditivo de Risco de Defasagem

> Construir modelo que prevê probabilidade de risco de defasagem.

O objetivo e identificar alunos com alta probabilidade de estar em defasagem no ano seguinte,
permitindo intervencoes preventivas. A defasagem e definida como IAN < 10 (moderado ou severo).

**Estrategia:**

- **Target:** `DEFASAGEM_2022` = 1 se IAN_2022 < 10, 0 se IAN_2022 = 10
- **Features:** indicadores de 2020 e 2021 (perfil historico do aluno)
- **Treino:** alunos presentes em 2020 e 2021
- **Teste:** validacao cruzada + avaliacao em alunos de 2022
- **Modelos:** Logistic Regression, Random Forest, XGBoost
"""

# %%
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
import xgboost as xgb
import warnings
warnings.filterwarnings('ignore')

# --- Construcao do dataset para o modelo ---
feat_cols = [
    'IAN_2020', 'IDA_2020', 'IEG_2020', 'IAA_2020', 'IPS_2020', 'IPP_2020',
    'IAN_2021', 'IDA_2021', 'IEG_2021', 'IAA_2021', 'IPS_2021', 'IPP_2021',
]
feat_cols = [c for c in feat_cols if c in df.columns]

target_col = 'IAN_2022'

df_ml = df[feat_cols + [target_col]].copy()
for col in df_ml.columns:
    df_ml[col] = pd.to_numeric(df_ml[col], errors='coerce')

df_ml = df_ml.dropna()
df_ml['TARGET'] = (df_ml[target_col] < 10).astype(int)

print(f'Dataset para modelo: {len(df_ml)} registros')
print(f'Defasagem (TARGET=1): {df_ml["TARGET"].sum()} ({df_ml["TARGET"].mean()*100:.1f}%)')
print(f'Adequado  (TARGET=0): {(df_ml["TARGET"]==0).sum()} ({(df_ml["TARGET"]==0).mean()*100:.1f}%)')
print(f'Features utilizadas: {feat_cols}')

# %%
# --- Feature engineering: deltas entre anos ---
for ind in ['IAN', 'IDA', 'IEG', 'IAA', 'IPS', 'IPP']:
    col_20 = f'{ind}_2020'
    col_21 = f'{ind}_2021'
    if col_20 in df_ml.columns and col_21 in df_ml.columns:
        df_ml[f'DELTA_{ind}'] = df_ml[col_21] - df_ml[col_20]

feat_cols_eng = [c for c in df_ml.columns if c not in [target_col, 'TARGET']]
X = df_ml[feat_cols_eng]
y = df_ml['TARGET']

print(f'Features apos engineering: {len(feat_cols_eng)}')
print(feat_cols_eng)

# %%
# --- Split treino/teste estratificado (80/20) ---
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import (classification_report, roc_auc_score,
                             confusion_matrix, ConfusionMatrixDisplay, f1_score)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f'Split treino/teste (stratified):')
print(f'  Treino : {len(X_train)} registros  | Defasados: {y_train.sum()} ({y_train.mean()*100:.1f}%)')
print(f'  Teste  : {len(X_test)}  registros  | Defasados: {y_test.sum()}  ({y_test.mean()*100:.1f}%)')

# --- Validacao cruzada no treino + avaliacao no teste ---
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc  = scaler.transform(X_test)

modelos = {
    'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
    'Random Forest':       RandomForestClassifier(n_estimators=100, random_state=42),
    'XGBoost':             xgb.XGBClassifier(n_estimators=100, random_state=42,
                                              eval_metric='logloss', verbosity=0),
}

resultados = {}
print(f'\n{"Modelo":<22} {"AUC-CV":>8} {"F1-CV":>7} {"AUC-Test":>10} {"F1-Test":>9}')
print('-' * 60)
for nome, modelo in modelos.items():
    X_tr = X_train_sc if nome == 'Logistic Regression' else X_train
    X_te = X_test_sc  if nome == 'Logistic Regression' else X_test

    auc_cv = cross_val_score(modelo, X_tr, y_train, cv=cv, scoring='roc_auc').mean()
    f1_cv  = cross_val_score(modelo, X_tr, y_train, cv=cv, scoring='f1').mean()

    modelo.fit(X_tr, y_train)
    y_pred      = modelo.predict(X_te)
    y_pred_prob = modelo.predict_proba(X_te)[:, 1]
    auc_test = roc_auc_score(y_test, y_pred_prob)
    f1_test  = f1_score(y_test, y_pred)

    resultados[nome] = {
        'auc_cv': auc_cv, 'f1_cv': f1_cv,
        'auc_test': auc_test, 'f1_test': f1_test,
        'y_pred': y_pred, 'modelo': modelo,
        'X_te': X_te,
    }
    print(f'{nome:<22} {auc_cv:>8.3f} {f1_cv:>7.3f} {auc_test:>10.3f} {f1_test:>9.3f}')

# %%
# --- Modelo selecionado: Logistic Regression ---
# Justificativa: melhor AUC no holdout (0.907) e coeficientes interpretaveis
# — cada coeficiente permite calcular a contribuicao exata de cada indicador
# para o risco individual, habilitando recomendacoes de intervencao.

lr_final = LogisticRegression(max_iter=1000, random_state=42)
lr_final.fit(X_train_sc, y_train)

# Coeficientes padronizados (impacto por desvio padrao)
coefs = pd.Series(lr_final.coef_[0], index=feat_cols_eng).sort_values(ascending=False)
print('Coeficientes Logistic Regression (ordenados por impacto no risco):')
print(coefs.round(3).to_string())

# Classification report
lr_pred = lr_final.predict(X_test_sc)
print(f'\nClassification Report — Logistic Regression (holdout):')
print(classification_report(y_test, lr_pred,
                             target_names=['Adequado (IAN=10)', 'Defasado (IAN<10)']))

# Random Forest para feature importance (complementar)
rf_final = RandomForestClassifier(n_estimators=200, random_state=42)
rf_final.fit(X, y)
feat_imp = pd.Series(rf_final.feature_importances_, index=feat_cols_eng).sort_values(ascending=False)
print('\nTop 10 features (Random Forest — referencia de importancia):')
print(feat_imp.head(10).round(4).to_string())

# %%
# --- Sistema de recomendacoes baseado nos achados das 11 perguntas ---

# Dicionario: feature -> (direcao_de_risco, recomendacao)
# direcao: 'baixo' = valor baixo aumenta risco | 'negativo' = delta negativo aumenta risco
RECOMENDACOES = {
    'IDA_2021'  : ('baixo',    'Desempenho academico recente baixo — priorizar reforco e tutoria individual'),
    'IAN_2021'  : ('baixo',    'Defasagem curricular persistente — plano de nivelamento por disciplina'),
    'IEG_2020'  : ('baixo',    'Engajamento inicial baixo — acompanhar frequencia e motivacao desde o 1o ano'),
    'DELTA_IDA' : ('negativo', 'Desempenho em queda — intervencao urgente: revisao de carga e mentoria'),
    'IPP_2021'  : ('baixo',    'Avaliacao psicopedagogica critica — encaminhar para suporte pedagogico especializado'),
    'DELTA_IPP' : ('negativo', 'Deterioracao psicopedagogica — reavaliar metodologia e suporte da equipe'),
    'IPP_2020'  : ('baixo',    'Historico psicopedagogico fragilizado — monitoramento continuo desde o ingresso'),
    'IAN_2020'  : ('baixo',    'Defasagem preexistente na entrada — plano de recuperacao desde o primeiro ciclo'),
    'IEG_2021'  : ('baixo',    'Engajamento caindo — conversa individual para identificar barreiras de participacao'),
    'DELTA_IEG' : ('negativo', 'Queda de engajamento — alertar coordenacao e buscar ativo do aluno'),
    'IDA_2020'  : ('baixo',    'Desempenho academico historicamente baixo — avaliar ritmo e metodologia'),
    'IPS_2020'  : ('baixo',    'Contexto psicossocial fragilizado em 2020 — suporte familiar e acompanhamento psicologico'),
    'IPS_2021'  : ('baixo',    'Condicoes psicossociais adversas — acionar rede de suporte familiar'),
    'DELTA_IPS' : ('negativo', 'Piora no contexto de vida — visita domiciliar ou contato com responsaveis'),
    'IAA_2020'  : ('baixo',    'Autoconceito muito baixo — trabalhar autoestima e protagonismo (ver achado P4)'),
    'IAA_2021'  : ('baixo',    'Autoconceito em queda — reforcar feedbacks positivos e conquistas do aluno'),
    'DELTA_IAN' : ('negativo', 'Defasagem curricular aumentando — nivelamento e avaliacao de progressao de fase'),
    'DELTA_IAA' : ('negativo', 'Autoestima deteriorando — intervencao motivacional prioritaria'),
}

def calcular_risco_e_recomendacoes(perfil, modelo, scaler, feat_cols, top_n=3):
    """
    perfil : dict com valores dos indicadores (ex: {'IDA_2021': 5.2, 'IEG_2020': 6.1, ...})
    Retorna: (probabilidade_risco, lista_de_recomendacoes_ordenadas_por_impacto)
    """
    X_aluno = pd.DataFrame([perfil])[feat_cols].fillna(0)
    X_sc    = scaler.transform(X_aluno)

    prob = modelo.predict_proba(X_sc)[0][1]

    # Contribuicao de cada feature: coef * valor_padronizado
    # Contribuicao positiva = aumenta risco de defasagem
    contrib = pd.Series(modelo.coef_[0] * X_sc[0], index=feat_cols)
    top_fatores = contrib.sort_values(ascending=False).head(top_n)

    recomendacoes = []
    for feat, contrib_val in top_fatores.items():
        if feat in RECOMENDACOES and contrib_val > 0:
            _, msg = RECOMENDACOES[feat]
            recomendacoes.append({
                'indicador'    : feat,
                'contribuicao' : round(contrib_val, 3),
                'recomendacao' : msg,
            })

    return round(prob * 100, 1), recomendacoes

# %%
# --- Demonstracao: 3 perfis sinteticos ---
perfis_demo = {
    'Aluno A (alto risco)': {
        'IAN_2020': 5.0, 'IDA_2020': 4.5, 'IEG_2020': 5.8,
        'IAA_2020': 7.0, 'IPS_2020': 5.5, 'IPP_2020': 5.0,
        'IAN_2021': 5.0, 'IDA_2021': 4.0, 'IEG_2021': 5.5,
        'IAA_2021': 6.5, 'IPS_2021': 5.0, 'IPP_2021': 4.5,
        'DELTA_IAN': 0.0, 'DELTA_IDA': -0.5, 'DELTA_IEG': -0.3,
        'DELTA_IAA': -0.5, 'DELTA_IPS': -0.5, 'DELTA_IPP': -0.5,
    },
    'Aluno B (risco medio)': {
        'IAN_2020': 5.0, 'IDA_2020': 6.0, 'IEG_2020': 7.5,
        'IAA_2020': 8.0, 'IPS_2020': 6.5, 'IPP_2020': 7.0,
        'IAN_2021': 5.0, 'IDA_2021': 5.5, 'IEG_2021': 7.0,
        'IAA_2021': 7.5, 'IPS_2021': 6.0, 'IPP_2021': 6.5,
        'DELTA_IAN': 0.0, 'DELTA_IDA': -0.5, 'DELTA_IEG': -0.5,
        'DELTA_IAA': -0.5, 'DELTA_IPS': -0.5, 'DELTA_IPP': -0.5,
    },
    'Aluno C (baixo risco)': {
        'IAN_2020': 10.0, 'IDA_2020': 8.0, 'IEG_2020': 9.0,
        'IAA_2020': 8.5,  'IPS_2020': 7.5, 'IPP_2020': 8.5,
        'IAN_2021': 10.0, 'IDA_2021': 8.5, 'IEG_2021': 9.0,
        'IAA_2021': 8.5,  'IPS_2021': 7.8, 'IPP_2021': 8.8,
        'DELTA_IAN': 0.0, 'DELTA_IDA': 0.5, 'DELTA_IEG': 0.0,
        'DELTA_IAA': 0.0, 'DELTA_IPS': 0.3, 'DELTA_IPP': 0.3,
    },
}

print('=== Demonstracao do Sistema de Recomendacoes ===\n')
for nome_perfil, perfil in perfis_demo.items():
    prob, recs = calcular_risco_e_recomendacoes(
        perfil, lr_final, scaler, feat_cols_eng
    )
    nivel = 'ALTO' if prob >= 70 else 'MEDIO' if prob >= 40 else 'BAIXO'
    print(f'{nome_perfil}')
    print(f'  Probabilidade de defasagem: {prob:.1f}%  [{nivel}]')
    if recs:
        print('  Principais fatores e recomendacoes:')
        for r in recs:
            print(f'    [{r["indicador"]}] contrib={r["contribuicao"]:+.3f}')
            print(f'    -> {r["recomendacao"]}')
    else:
        print('  Sem fatores de risco dominantes — perfil adequado.')
    print()

# %%
# --- Exportar modelo LR (melhor holdout) + RF (feature importance) ---
import pickle
with open('modelo_risco.pkl', 'wb') as f:
    pickle.dump({
        'model_lr'      : lr_final,
        'model_rf'      : rf_final,
        'scaler'        : scaler,
        'features'      : feat_cols_eng,
        'recomendacoes' : RECOMENDACOES,
    }, f)
print('Modelo exportado: modelo_risco.pkl (LR + RF + scaler + recomendacoes)')

# %%
fig, axes = plt.subplots(1, 4, figsize=(22, 6))

# --- Grafico 1: AUC-ROC CV vs Teste por modelo ---
nomes_mod  = list(resultados.keys())
aucs_cv    = [resultados[n]['auc_cv']   for n in nomes_mod]
aucs_test  = [resultados[n]['auc_test'] for n in nomes_mod]
x_mod = np.arange(len(nomes_mod))
w_mod = 0.35
b1 = axes[0].bar(x_mod - w_mod/2, aucs_cv,   w_mod, label='CV (treino)', color='#5bc0de', alpha=0.85)
b2 = axes[0].bar(x_mod + w_mod/2, aucs_test, w_mod, label='Holdout (teste)', color='#5cb85c', alpha=0.85)
for bar, val in list(zip(b1, aucs_cv)) + list(zip(b2, aucs_test)):
    axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                 f'{val:.3f}', ha='center', va='bottom', fontsize=8)
axes[0].axhline(0.7, color='gray', linestyle='--', linewidth=1)
axes[0].set_title('AUC-ROC\nCV vs Holdout')
axes[0].set_ylabel('AUC-ROC')
axes[0].set_ylim(0.5, 1.0)
axes[0].set_xticks(x_mod)
axes[0].set_xticklabels(nomes_mod, fontsize=7)
axes[0].legend(fontsize=8)

# --- Grafico 2: F1 CV vs Teste ---
f1s_cv   = [resultados[n]['f1_cv']   for n in nomes_mod]
f1s_test = [resultados[n]['f1_test'] for n in nomes_mod]
b3 = axes[1].bar(x_mod - w_mod/2, f1s_cv,   w_mod, label='CV (treino)', color='#5bc0de', alpha=0.85)
b4 = axes[1].bar(x_mod + w_mod/2, f1s_test, w_mod, label='Holdout (teste)', color='#5cb85c', alpha=0.85)
for bar, val in list(zip(b3, f1s_cv)) + list(zip(b4, f1s_test)):
    axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                 f'{val:.3f}', ha='center', va='bottom', fontsize=8)
axes[1].set_title('F1-Score\nCV vs Holdout')
axes[1].set_ylabel('F1-Score')
axes[1].set_ylim(0.5, 1.0)
axes[1].set_xticks(x_mod)
axes[1].set_xticklabels(nomes_mod, fontsize=7)
axes[1].legend(fontsize=8)

# --- Grafico 3: Matriz de Confusao — Logistic Regression ---
cm = confusion_matrix(y_test, lr_pred)
disp = ConfusionMatrixDisplay(confusion_matrix=cm,
                               display_labels=['Adequado', 'Defasado'])
disp.plot(ax=axes[2], colorbar=False, cmap='Blues')
axes[2].set_title('Matriz de Confusao\nLogistic Regression (teste)')

# --- Grafico 4: Feature importance (top 10) ---
top10 = feat_imp.head(10)
cores_fi = ['#5cb85c' if 'DELTA' in n else '#5bc0de' for n in top10.index]
axes[3].barh(top10.index[::-1], top10.values[::-1], color=cores_fi[::-1])
axes[3].set_title('Top 10 Features\n(Random Forest)')
axes[3].set_xlabel('Importancia')

plt.suptitle('Modelo Preditivo — Comparacao CV vs Holdout + Matriz de Confusao', fontsize=13)
plt.tight_layout()
plt.show()

# %% [markdown]
"""
#### Conclusao — Pergunta 9

| Metrica | Logistic Regression | Random Forest | XGBoost |
|---------|---------------------|---------------|---------|
| AUC-ROC | ~0.XX | ~0.XX | ~0.XX |
| F1 Score | ~0.XX | ~0.XX | ~0.XX |

*(valores exatos gerados na execucao acima)*

**Modelo recomendado: Random Forest**

Random Forest apresenta o melhor balanco entre desempenho preditivo e interpretabilidade
das features. O modelo foi exportado em `modelo_risco.pkl` para uso no app Streamlit.

**Features mais importantes:**

As features de maior peso sao os indicadores de 2021 (ano mais recente disponivel) e
os deltas (variacao entre 2020 e 2021). Isso confirma que a **trajetoria do aluno**
(tendencia de melhora ou piora) e mais preditiva do que o valor absoluto em um unico ano.

**Limitacao:** o modelo foi treinado com alunos presentes nos 3 anos (n pequeno). Para
producao, deve ser re-treinado com mais dados conforme novos anos forem disponibilizados.
"""

# %% [markdown]
"""
### Pergunta 10 — Efetividade do Programa

> Os indicadores mostram melhora consistente nas fases ao longo do ciclo?

A analise de efetividade busca responder: o programa Passos Magicos produz resultados
mensuráveis no desenvolvimento dos alunos? Analisamos a evolucao por Pedra ao longo dos
tres anos e a taxa de progressao de fase.
"""

# %%
# --- Evolucao do INDE por Pedra entre 2020 e 2022 ---
print('Evolucao do INDE medio por Pedra ao longo dos anos:')
print()

pedra_order = ['Quartzo', 'Ágata', 'Ametista', 'Topázio']

for pedra in pedra_order:
    linha = f'{pedra:<12}: '
    for ano in [2020, 2021, 2022]:
        ped_col  = f'PEDRA_{ano}'
        inde_col = f'INDE_{ano}'
        if ped_col in df.columns and inde_col in df.columns:
            g = df[df[ped_col] == pedra][inde_col]
            g = pd.to_numeric(g, errors='coerce').dropna()
            linha += f'{ano}={g.mean():.2f}(n={len(g)})  '
    print(linha)

# %%
# --- Taxa de progressao de Pedra (alunos presentes em 2020 e 2022) ---
mask = df['PEDRA_2020'].notna() & df['PEDRA_2022'].notna()
df_prog = df[mask][['PEDRA_2020', 'PEDRA_2022']].copy()

pedra_nivel = {'Quartzo': 0, 'Ágata': 1, 'Ametista': 2, 'Topázio': 3}
df_prog['NIVEL_2020'] = df_prog['PEDRA_2020'].map(pedra_nivel)
df_prog['NIVEL_2022'] = df_prog['PEDRA_2022'].map(pedra_nivel)
df_prog = df_prog.dropna()

progrediu = (df_prog['NIVEL_2022'] > df_prog['NIVEL_2020']).sum()
manteve   = (df_prog['NIVEL_2022'] == df_prog['NIVEL_2020']).sum()
regrediu  = (df_prog['NIVEL_2022'] < df_prog['NIVEL_2020']).sum()
total_prog = len(df_prog)

print(f'Taxa de progressao de Pedra (2020 -> 2022, n={total_prog}):')
print(f'  Progrediu  : {progrediu:>3} ({progrediu/total_prog*100:.1f}%)')
print(f'  Manteve    : {manteve:>3} ({manteve/total_prog*100:.1f}%)')
print(f'  Regrediu   : {regrediu:>3} ({regrediu/total_prog*100:.1f}%)')

# %%
# --- INDE medio geral por ano ---
print('\nINDE medio geral por ano:')
inde_geral = {}
for ano in [2020, 2021, 2022]:
    col = f'INDE_{ano}'
    if col in df.columns:
        vals = pd.to_numeric(df[col], errors='coerce').dropna()
        inde_geral[ano] = vals.mean()
        print(f'  {ano}: {vals.mean():.3f}  (n={len(vals)})')

# %%
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

# --- Grafico 1: INDE por ano e Pedra ---
cores_pedra_map = {'Quartzo': '#d9534f', 'Ágata': '#f0ad4e',
                   'Ametista': '#5bc0de', 'Topázio': '#5cb85c'}
anos_plot = [2020, 2021, 2022]
for pedra in pedra_order:
    vals_line = []
    for ano in anos_plot:
        ped_col  = f'PEDRA_{ano}'
        inde_col = f'INDE_{ano}'
        if ped_col in df.columns and inde_col in df.columns:
            g = df[df[ped_col] == pedra][inde_col]
            g = pd.to_numeric(g, errors='coerce').dropna()
            vals_line.append(g.mean() if len(g) > 0 else np.nan)
        else:
            vals_line.append(np.nan)
    anos_validos = [a for a, v in zip(anos_plot, vals_line) if not np.isnan(v)]
    vals_validos = [v for v in vals_line if not np.isnan(v)]
    if anos_validos:
        axes[0].plot([str(a) for a in anos_validos], vals_validos,
                     marker='o', label=pedra, color=cores_pedra_map[pedra], linewidth=2)
axes[0].set_title('Evolucao do INDE Medio\npor Pedra (2020-2022)')
axes[0].set_ylabel('INDE Medio')
axes[0].set_ylim(0, 10)
axes[0].legend(fontsize=9)

# --- Grafico 2: Taxa de progressao ---
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

# --- Grafico 3: INDE geral por ano ---
if inde_geral:
    anos_g = [str(a) for a in sorted(inde_geral.keys())]
    vals_g = [inde_geral[a] for a in sorted(inde_geral.keys())]
    axes[2].plot(anos_g, vals_g, marker='o', color='#5bc0de', linewidth=2)
    for i, (a, v) in enumerate(zip(anos_g, vals_g)):
        axes[2].text(i, v + 0.05, f'{v:.3f}', ha='center', fontsize=11)
    axes[2].set_title('INDE Medio Geral\npor Ano')
    axes[2].set_ylabel('INDE Medio')
    axes[2].set_ylim(0, 10)

plt.suptitle('Efetividade do Programa Passos Magicos — Evolucao e Progressao', fontsize=13)
plt.tight_layout()
plt.show()

# %% [markdown]
"""
#### Conclusao — Pergunta 10

| Dimensao | Achado |
|----------|--------|
| INDE geral | Crescimento consistente de 2020 para 2022 |
| Progressao de Pedra | Maioria dos alunos progrediu ou manteve a Pedra (regressao e minoria) |
| INDE por Pedra | Cada Pedra mantem INDE consistente com seu nivel ao longo dos anos |

**Interpretacao:**

O programa demonstra efetividade mensuravel: o INDE medio geral cresceu entre 2020 e 2022,
e a maioria dos alunos com dados nos dois extremos progrediu de Pedra ou se manteve no mesmo nivel.

A regressao de Pedra (alunos que "desceram" de fase) e uma minoria — e pode refletir tanto
dificuldades reais quanto revisao dos criterios de classificacao entre anos (ver Secao 1.8).

**Limitacao critica:** apenas 314 alunos estao presentes nos 3 anos (23% da base total).
Qualquer analise de evolucao longitudinal subestima a realidade por excluir os alunos que
entraram ou sairam do programa ao longo do periodo.
"""

# %% [markdown]
"""
### Pergunta 11 — Insights e Criatividade

> Insights adicionais alem das perguntas obrigatorias.

Esta secao consolida descobertas que emergem da analise integrada de todos os indicadores
e que oferecem valor analitico adicional alem das 10 perguntas estruturadas.
"""

# %%
# Insight 1 — Impacto do tempo no programa (ANOS_PM) no desempenho
anos_pm_col = 'ANOS_PM_2022'
if anos_pm_col not in df.columns:
    anos_pm_col = None
    for col in df.columns:
        if 'ANOS' in col.upper() and 'PM' in col.upper():
            anos_pm_col = col
            break

if anos_pm_col:
    df_anos = df[[anos_pm_col, 'INDE_2022', 'IDA_2022']].copy()
    for col in [anos_pm_col, 'INDE_2022', 'IDA_2022']:
        df_anos[col] = pd.to_numeric(df_anos[col], errors='coerce')
    df_anos = df_anos.dropna()

    print('Insight 1 — INDE e IDA por tempo no programa (ANOS_PM):')
    for anos_val in sorted(df_anos[anos_pm_col].unique()):
        g = df_anos[df_anos[anos_pm_col] == anos_val]
        print(f'  {int(anos_val)} ano(s): INDE={g["INDE_2022"].mean():.3f}  IDA={g["IDA_2022"].mean():.3f}  n={len(g)}')
else:
    print('Coluna ANOS_PM nao encontrada — insight ignorado.')

# %%
# Insight 2 — Perfil de alunos bolsistas vs nao bolsistas
bolsa_col = None
for col in df.columns:
    if 'BOLSA' in col.upper() or 'BOLSISTA' in col.upper():
        bolsa_col = col
        break

if bolsa_col:
    df_bolsa = df[[bolsa_col, 'INDE_2022', 'IDA_2022']].copy()
    for col in ['INDE_2022', 'IDA_2022']:
        df_bolsa[col] = pd.to_numeric(df_bolsa[col], errors='coerce')
    df_bolsa = df_bolsa.dropna()

    print('Insight 2 — INDE e IDA por status de bolsa:')
    for grupo in df_bolsa[bolsa_col].unique():
        g = df_bolsa[df_bolsa[bolsa_col] == grupo]
        print(f'  {grupo}: INDE={g["INDE_2022"].mean():.3f}  IDA={g["IDA_2022"].mean():.3f}  n={len(g)}')
else:
    print('Coluna de bolsa nao encontrada na base.')

# %%
# Insight 3 — Taxa de evasao por ano de ingresso
print('Insight 3 — Taxa de retencao por coorte:')

s20 = df['INDE_2020'].notna()
s21 = df['INDE_2021'].notna()
s22 = df['INDE_2022'].notna()

n_2020_only = (s20 & ~s21 & ~s22).sum()
n_2021_only = (~s20 & s21 & ~s22).sum()
n_2022_only = (~s20 & ~s21 & s22).sum()
n_20_21     = (s20 & s21 & ~s22).sum()
n_20_22     = (s20 & ~s21 & s22).sum()
n_21_22     = (~s20 & s21 & s22).sum()
n_todos     = (s20 & s21 & s22).sum()

print(f'  Apenas 2020          : {n_2020_only}')
print(f'  Apenas 2021          : {n_2021_only}')
print(f'  Apenas 2022          : {n_2022_only}')
print(f'  2020 e 2021          : {n_20_21}')
print(f'  2020 e 2022          : {n_20_22}')
print(f'  2021 e 2022          : {n_21_22}')
print(f'  Todos os 3 anos      : {n_todos}')
print(f'  Total de registros   : {len(df)}')
print()
retencao_2020 = n_todos / (n_2020_only + n_20_21 + n_20_22 + n_todos) * 100
print(f'  Retencao 2020->2022 (alunos de 2020 que continuaram ate 2022): {retencao_2020:.1f}%')

# %%
# Insight 4 — Comparativo dos indicadores: 2020 vs 2022 (populacao total)
print('Insight 4 — Variacao dos indicadores: media 2020 vs 2022:')
print(f"{'Indicador':<8} {'2020':>8} {'2022':>8} {'Dif':>8}")
print('-' * 36)
for ind in ['IAN', 'IDA', 'IEG', 'IAA', 'IPS', 'IPP', 'IPV', 'INDE']:
    c20 = f'{ind}_2020'
    c22 = f'{ind}_2022'
    if c20 in df.columns and c22 in df.columns:
        m20 = pd.to_numeric(df[c20], errors='coerce').mean()
        m22 = pd.to_numeric(df[c22], errors='coerce').mean()
        print(f'{ind:<8} {m20:>8.3f} {m22:>8.3f} {m22-m20:>+8.3f}')

# %%
# %%
# Insight 5 — Instituicao de Ensino como fator contextual
inst_col = 'INSTITUICAO_ENSINO_ALUNO_2020'

mapa_tipo = {
    'Escola Pública'      : 'Pública',
    'Escola João Paulo II': 'Comunitária',
    'Rede Decisão/União'  : 'Comunitária',
    'Einstein'            : 'Parceira Privada',
    'FIAP'                : 'Parceira Privada',
    'UNISA'               : 'Parceira Privada',
    'Estácio'             : 'Parceira Privada',
}

df_inst = df.copy()
df_inst['TIPO_INST'] = df_inst[inst_col].map(mapa_tipo)
df_inst = df_inst[df_inst['TIPO_INST'].notna()]

tipos_ordem = ['Pública', 'Comunitária', 'Parceira Privada']
cores_tipo  = ['#d9534f', '#f0ad4e', '#5cb85c']
indicadores_inst = ['IAN', 'IDA', 'IEG', 'IAA', 'IPS', 'IPP', 'IPV', 'INDE']

print('Insight 5 — Indicadores por tipo de instituicao (medias):')
for tipo in tipos_ordem:
    g = df_inst[df_inst['TIPO_INST'] == tipo]
    print(f'\n  {tipo} (n={len(g)}):')
    for ano in [2020, 2021, 2022]:
        vals = []
        for ind in indicadores_inst:
            col = f'{ind}_{ano}'
            if col in df_inst.columns:
                v = pd.to_numeric(g[col], errors='coerce').mean()
                vals.append(f'{ind}={v:.2f}' if not np.isnan(v) else f'{ind}=N/A')
        if vals:
            print(f'    {ano}: ' + '  '.join(vals))

# %%
# Progressao de Pedra por tipo de instituicao
pedra_nivel_inst = {'Quartzo': 0, 'Ágata': 1, 'Ametista': 2, 'Topázio': 3}
df_prog_inst = df_inst[df_inst['PEDRA_2020'].notna() & df_inst['PEDRA_2022'].notna()].copy()
df_prog_inst['NIVEL_2020'] = df_prog_inst['PEDRA_2020'].map(pedra_nivel_inst)
df_prog_inst['NIVEL_2022'] = df_prog_inst['PEDRA_2022'].map(pedra_nivel_inst)
df_prog_inst = df_prog_inst.dropna(subset=['NIVEL_2020', 'NIVEL_2022'])

print('\nProgressao de Pedra (2020->2022) por tipo de instituicao:')
for tipo in tipos_ordem:
    g = df_prog_inst[df_prog_inst['TIPO_INST'] == tipo]
    if len(g) == 0:
        continue
    prog = (g['NIVEL_2022'] > g['NIVEL_2020']).sum()
    mant = (g['NIVEL_2022'] == g['NIVEL_2020']).sum()
    regr = (g['NIVEL_2022'] < g['NIVEL_2020']).sum()
    print(f'  {tipo} (n={len(g)}): Progrediu={prog}({prog/len(g)*100:.0f}%)  Manteve={mant}({mant/len(g)*100:.0f}%)  Regrediu={regr}({regr/len(g)*100:.0f}%)')

# %%
fig_i5, axes_i5 = plt.subplots(1, 3, figsize=(18, 6))

# --- Grafico 1: INDE medio por tipo de instituicao ao longo dos anos ---
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
axes_i5[0].set_title('INDE Medio por Tipo de\nInstituicao (2020-2022)')
axes_i5[0].set_ylabel('INDE Medio')
axes_i5[0].set_ylim(0, 10)
axes_i5[0].legend(fontsize=8)

# --- Grafico 2: Indicadores em 2022 por tipo de instituicao ---
inds_i5 = ['IAN', 'IDA', 'IEG', 'IAA', 'IPS', 'IPP']
x_i5 = np.arange(len(inds_i5))
w_i5 = 0.25
for j, (tipo, cor) in enumerate(zip(tipos_ordem, cores_tipo)):
    g = df_inst[df_inst['TIPO_INST'] == tipo]
    vals = [pd.to_numeric(g[f'{ind}_2022'], errors='coerce').mean()
            if f'{ind}_2022' in df_inst.columns else np.nan for ind in inds_i5]
    vals_p = [v if not np.isnan(v) else 0 for v in vals]
    axes_i5[1].bar(x_i5 + (j - 1) * w_i5, vals_p, w_i5, label=tipo, color=cor, alpha=0.85)
axes_i5[1].set_xticks(x_i5)
axes_i5[1].set_xticklabels(inds_i5, fontsize=9)
axes_i5[1].set_title('Indicadores 2022\npor Tipo de Instituicao')
axes_i5[1].set_ylabel('Media')
axes_i5[1].set_ylim(0, 11)
axes_i5[1].legend(fontsize=8)

# --- Grafico 3: Progressao de Pedra por tipo (stacked bar %) ---
pedras_status   = ['Progrediu', 'Manteve', 'Regrediu']
cores_status_i5 = ['#5cb85c', '#f0ad4e', '#d9534f']
tipos_com_dados = [t for t in tipos_ordem if (df_prog_inst['TIPO_INST'] == t).sum() > 0]
data_prog_inst  = {}
for tipo in tipos_com_dados:
    g = df_prog_inst[df_prog_inst['TIPO_INST'] == tipo]
    data_prog_inst[tipo] = [
        (g['NIVEL_2022'] > g['NIVEL_2020']).sum() / len(g) * 100,
        (g['NIVEL_2022'] == g['NIVEL_2020']).sum() / len(g) * 100,
        (g['NIVEL_2022'] < g['NIVEL_2020']).sum() / len(g) * 100,
    ]
for i, (status, cor) in enumerate(zip(pedras_status, cores_status_i5)):
    vals_s = [data_prog_inst[t][i] for t in tipos_com_dados]
    bottom_s = [sum(data_prog_inst[t][:i]) for t in tipos_com_dados]
    axes_i5[2].bar(tipos_com_dados, vals_s, bottom=bottom_s, label=status, color=cor, alpha=0.85)
axes_i5[2].set_title(f'Progressao de Pedra 2020->2022\npor Tipo de Instituicao')
axes_i5[2].set_ylabel('% de Alunos')
axes_i5[2].set_ylim(0, 100)
axes_i5[2].legend(fontsize=8)

plt.suptitle('Insight 5 — Tipo de Instituicao como Fator Contextual', fontsize=13)
plt.tight_layout()
plt.show()

# %% [markdown]
"""
### Insight 6 — Mobilidade Social via Programa: a Tese do INDICADO_BOLSA

**Contexto — alerta sobre BOLSISTA_2022 (efeito de selecao):**

A variavel `BOLSISTA_2022` indica alunos que JA recebem bolsa em parceira privada.
Bolsistas superam nao bolsistas em todos os indicadores (INDE +0.77, IDA +1.20, IEG +0.75),
mas isso reflete SELECAO, nao causalidade: o criterio de concessao ja favorece alunos
de maior desempenho. Nao e possivel afirmar impacto da bolsa sem dados pre/pos concessao.

**Tese — INDICADO_BOLSA_2022 como marcador de mobilidade:**

O programa identifica alunos de origem vulneravel com perfil de desenvolvimento
multidimensional e os indica para bolsas em instituicoes privadas de qualidade.
`INDICADO_BOLSA_2022` e o marcador observavel dessa trajetoria de mobilidade social.

**Hipotese central:** alunos indicados para bolsa vem predominantemente de escola publica
e se destacam pelo IEG (engajamento) — nao apenas pelo IDA (desempenho academico).
Isso significa que o programa recompensa comprometimento, nao somente capital academico previo.
"""

# %%
# Parte A — Alerta: perfil comparativo BOLSISTA vs nao bolsista
bolsista_col  = 'BOLSISTA_2022'
indicado_col  = 'INDICADO_BOLSA_2022'
inds_6        = ['IAN', 'IDA', 'IEG', 'IAA', 'IPS', 'IPP', 'IPV', 'INDE']
pedra_order_6 = ['Quartzo', 'Ágata', 'Ametista', 'Topázio']

cols_6 = [bolsista_col, indicado_col, 'PEDRA_2022', 'PONTO_VIRADA_2022',
          inst_col] + [f'{ind}_2022' for ind in inds_6 if f'{ind}_2022' in df.columns]
df6 = df[[c for c in cols_6 if c in df.columns]].copy()
for col in [f'{ind}_2022' for ind in inds_6]:
    if col in df6.columns:
        df6[col] = pd.to_numeric(df6[col], errors='coerce')

# Volume
n_bolsista = df6[bolsista_col].value_counts() if bolsista_col in df6.columns else pd.Series()
n_indicado = df6[indicado_col].value_counts() if indicado_col in df6.columns else pd.Series()
print('=== Parte A — BOLSISTA_2022 (alerta de selecao) ===')
print(f'Distribuicao: {n_bolsista.to_dict()}')
print()
if bolsista_col in df6.columns:
    grupos_b = sorted(df6[bolsista_col].dropna().unique())
    print(f"{'Indicador':<8}", end='')
    for g in grupos_b:
        print(f'{str(g):>13}', end='')
    print(f'{"Dif (Sim-Nao)":>15}')
    print('-' * (8 + 13 * len(grupos_b) + 15))
    for ind in inds_6:
        col = f'{ind}_2022'
        if col not in df6.columns:
            continue
        medias = {g: df6[df6[bolsista_col] == g][col].mean() for g in grupos_b}
        dif = medias.get('Sim', np.nan) - medias.get('Não', np.nan)
        print(f'{ind:<8}', end='')
        for g in grupos_b:
            print(f'{medias.get(g, np.nan):>13.3f}', end='')
        print(f'{dif:>+15.3f}')
    print('\n[!] Efeito de selecao: bolsistas ja eram de maior desempenho antes da bolsa.')

# %%
# Parte B — Tese: perfil dos INDICADO_BOLSA_2022
print('\n=== Parte B — INDICADO_BOLSA_2022 (tese de mobilidade) ===')
print(f'Distribuicao: {n_indicado.to_dict()}')
print()

if indicado_col in df6.columns:
    df6_ind = df6[df6[indicado_col].notna()].copy()
    grupos_i = sorted(df6_ind[indicado_col].unique())

    # Indicadores por grupo
    print(f"{'Indicador':<8}", end='')
    for g in grupos_i:
        print(f'{str(g):>13}', end='')
    print(f'{"Dif (Sim-Nao)":>15}')
    print('-' * (8 + 13 * len(grupos_i) + 15))
    for ind in inds_6:
        col = f'{ind}_2022'
        if col not in df6_ind.columns:
            continue
        medias = {g: df6_ind[df6_ind[indicado_col] == g][col].mean() for g in grupos_i}
        dif = medias.get('Sim', np.nan) - medias.get('Não', np.nan)
        print(f'{ind:<8}', end='')
        for g in grupos_i:
            print(f'{medias.get(g, np.nan):>13.3f}', end='')
        print(f'{dif:>+15.3f}')

# %%
# Parte B — Origem escolar dos indicados (hipotese central)
print('\n--- Origem escolar dos INDICADO_BOLSA = Sim ---')
if indicado_col in df6.columns and inst_col in df6.columns:
    df6_sim = df6[df6[indicado_col] == 'Sim']
    dist_inst = df6_sim[inst_col].value_counts()
    total_sim = len(df6_sim)
    for inst, cnt in dist_inst.items():
        print(f'  {inst:<30}: {cnt:>3} ({cnt/total_sim*100:.1f}%)')

    df6_sim_tipo = df6_sim.copy()
    df6_sim_tipo['TIPO_INST'] = df6_sim_tipo[inst_col].map(mapa_tipo)
    dist_tipo = df6_sim_tipo['TIPO_INST'].value_counts()
    print(f'\n  Por tipo:')
    for tipo, cnt in dist_tipo.items():
        print(f'    {tipo:<20}: {cnt:>3} ({cnt/total_sim*100:.1f}%)')

# Parte B — Ponto de Virada dos indicados
print('\n--- Ponto de Virada dos INDICADO_BOLSA ---')
if indicado_col in df6.columns and 'PONTO_VIRADA_2022' in df6.columns:
    for grupo in grupos_i:
        g = df6_ind[df6_ind[indicado_col] == grupo]
        pv = g['PONTO_VIRADA_2022'].value_counts(normalize=True) * 100
        print(f'  {grupo}: ' + '  '.join([f'{k}={v:.1f}%' for k, v in pv.items()]))

# Parte B — Pipeline: indicados que ja sao bolsistas
print('\n--- Pipeline: INDICADO_BOLSA x BOLSISTA_2022 ---')
if indicado_col in df6.columns and bolsista_col in df6.columns:
    cross = pd.crosstab(df6[indicado_col], df6[bolsista_col], margins=True)
    print(cross.to_string())

# %%
# Parte B — Qual indicador mais diferencia indicados de nao indicados?
print('\n--- Diferenca por indicador (Indicado Sim - Nao, ordenado) ---')
if indicado_col in df6.columns:
    difs = {}
    for ind in inds_6:
        col = f'{ind}_2022'
        if col in df6_ind.columns:
            m_sim = df6_ind[df6_ind[indicado_col] == 'Sim'][col].mean()
            m_nao = df6_ind[df6_ind[indicado_col] == 'Não'][col].mean()
            difs[ind] = m_sim - m_nao
    for ind, dif in sorted(difs.items(), key=lambda x: abs(x[1]), reverse=True):
        barra = '|' * int(abs(dif) * 5)
        sinal = '+' if dif >= 0 else '-'
        print(f'  {ind:<6}: {dif:>+6.3f}  {barra}')

# %%
fig_i6, axes_i6 = plt.subplots(1, 3, figsize=(18, 6))

# --- Grafico 1: Indicadores — Indicado Sim vs Nao ---
if indicado_col in df6.columns:
    x_i6 = np.arange(len(inds_6))
    w_i6 = 0.35
    for j, (grupo, cor) in enumerate(zip(['Não', 'Sim'], ['#5bc0de', '#5cb85c'])):
        g = df6_ind[df6_ind[indicado_col] == grupo] if grupo in grupos_i else pd.DataFrame()
        vals = [g[f'{ind}_2022'].mean() if not g.empty and f'{ind}_2022' in g.columns else 0
                for ind in inds_6]
        axes_i6[0].bar(x_i6 + (j - 0.5) * w_i6, vals, w_i6,
                       label=f'Indicado: {grupo} (n={len(g)})', color=cor, alpha=0.85)
    axes_i6[0].set_xticks(x_i6)
    axes_i6[0].set_xticklabels(inds_6, fontsize=9)
    axes_i6[0].set_title('Indicadores 2022\nIndicado Bolsa: Sim vs Nao')
    axes_i6[0].set_ylabel('Media')
    axes_i6[0].set_ylim(0, 11)
    axes_i6[0].legend(fontsize=8)

# --- Grafico 2: Origem escolar dos indicados ---
if indicado_col in df6.columns and inst_col in df6.columns and 'TIPO_INST' in df6_sim_tipo.columns:
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
    axes_i6[1].set_ylabel('Quantidade de Alunos')

# --- Grafico 3: IEG vs IDA — scatter Indicado x Nao indicado ---
if indicado_col in df6.columns and 'IEG_2022' in df6.columns and 'IDA_2022' in df6.columns:
    for grupo, cor, alpha in zip(['Não', 'Sim'], ['#5bc0de', '#d9534f'], [0.3, 0.8]):
        g = df6_ind[df6_ind[indicado_col] == grupo]
        axes_i6[2].scatter(g['IDA_2022'], g['IEG_2022'],
                           color=cor, alpha=alpha, label=f'Indicado: {grupo}', s=20)
    # Medias dos grupos
    for grupo, cor, marker in zip(['Não', 'Sim'], ['#5bc0de', '#d9534f'], ['o', '*']):
        g = df6_ind[df6_ind[indicado_col] == grupo]
        axes_i6[2].scatter(g['IDA_2022'].mean(), g['IEG_2022'].mean(),
                           color=cor, s=200, marker=marker, edgecolors='black',
                           zorder=5, label=f'Media {grupo}')
    axes_i6[2].set_xlabel('IDA (desempenho academico)')
    axes_i6[2].set_ylabel('IEG (engajamento no programa)')
    axes_i6[2].set_title('IDA vs IEG por Indicacao\n(estrela = media do grupo)')
    axes_i6[2].legend(fontsize=7)
    axes_i6[2].set_xlim(0, 11)
    axes_i6[2].set_ylim(0, 11)

plt.suptitle('Insight 6 — INDICADO_BOLSA: Marcador de Mobilidade Social', fontsize=13)
plt.tight_layout()
plt.show()

# %%
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# --- Grafico 1: Variacao dos indicadores 2020 vs 2022 ---
inds_comp = ['IAN', 'IDA', 'IEG', 'IAA', 'IPS', 'IPP', 'IPV', 'INDE']
medias_20, medias_22 = [], []
for ind in inds_comp:
    c20 = f'{ind}_2020'
    c22 = f'{ind}_2022'
    if c20 in df.columns and c22 in df.columns:
        medias_20.append(pd.to_numeric(df[c20], errors='coerce').mean())
        medias_22.append(pd.to_numeric(df[c22], errors='coerce').mean())
    else:
        medias_20.append(np.nan)
        medias_22.append(np.nan)

x = np.arange(len(inds_comp))
w = 0.35
b1 = axes[0].bar(x - w/2, medias_20, w, label='2020', color='#5bc0de', alpha=0.85)
b2 = axes[0].bar(x + w/2, medias_22, w, label='2022', color='#5cb85c', alpha=0.85)
axes[0].set_xticks(x)
axes[0].set_xticklabels(inds_comp, fontsize=9)
axes[0].set_title('Insight 4 — Todos os Indicadores\n2020 vs 2022 (populacao total)')
axes[0].set_ylabel('Media do Indicador')
axes[0].set_ylim(0, 11)
axes[0].legend(fontsize=9)
axes[0].axhline(10, color='gray', linestyle='--', linewidth=1)

# --- Grafico 2: Coorte — composicao dos alunos por presenca nos anos ---
labels_coorte = ['Apenas\n2020', 'Apenas\n2021', 'Apenas\n2022',
                 '2020+2021', '2020+2022', '2021+2022', 'Todos\n3 anos']
vals_coorte   = [n_2020_only, n_2021_only, n_2022_only,
                 n_20_21, n_20_22, n_21_22, n_todos]
cores_coorte  = ['#d9534f','#f0ad4e','#5bc0de',
                 '#d9534f','#d9534f','#f0ad4e','#5cb85c']
bars3 = axes[1].bar(labels_coorte, vals_coorte, color=cores_coorte, alpha=0.85)
for bar, val in zip(bars3, vals_coorte):
    axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                 str(val), ha='center', va='bottom', fontsize=9)
axes[1].set_title('Insight 3 — Composicao da Coorte\npor Presenca nos Anos')
axes[1].set_ylabel('Quantidade de Alunos')

plt.suptitle('Insights Adicionais — Evolucao Geral e Composicao da Coorte', fontsize=13)
plt.tight_layout()
plt.show()

# %% [markdown]
"""
#### Conclusao — Pergunta 11

**Insight 1 — Tempo no programa:**
Alunos com mais anos no programa Passos Magicos apresentam INDE e IDA superiores.
A relacao e positiva e consistente: cada ano adicional no programa esta associado a
melhora mensuravel nos indicadores. Isso sugere que o impacto do programa e cumulativo
e que a retencao de longo prazo e estrategica.

**Insight 2 — Bolsistas:**
*(resultado depende da disponibilidade da coluna na base)*
Se disponivel, permite comparar o perfil de alunos que recebem bolsa de estudos com
os demais — uma segmentacao relevante para priorizar recursos.

**Insight 3 — Rotatividade da coorte:**
A base e altamente transiente: apenas 23% dos alunos estao presentes nos 3 anos.
Cada ano incorpora uma parcela significativa de novos alunos (apenas 2022 = maior grupo).
Isso implica que analises longitudinais representam apenas a fracao mais persistente do
programa — provavelmente os alunos mais engajados e de melhor desempenho.

**Insight 4 — Evolucao geral 2020 -> 2022:**
A maioria dos indicadores mostra evolucao positiva ou estabilidade entre 2020 e 2022
quando comparamos as medias das populacoes disponiveis em cada ano. A cautela necessaria
e que as populacoes de cada ano sao diferentes (estrutural null), entao a comparacao
nao e totalmente equivalente a um painel longitudinal.

**Insight 5 — Tipo de instituicao:**
O contexto escolar externo e diferenciador, mas o programa mitiga parcialmente as
desvantagens. Alunos de escola publica tem IAN e IDA inferiores (reflexo da qualidade
do ensino regular), porem apresentam o maior IEG de todos os grupos — confirmando que
o engajamento no programa e independente do capital academico previo.

**Insight 6 — INDICADO_BOLSA como marcador de mobilidade social:**

*Alerta (Parte A):* BOLSISTA_2022 apresenta efeito de selecao. Bolsistas superam nao
bolsistas em todos os indicadores, mas isso reflete o criterio de concessao (que ja
favorece os de maior desempenho), nao o impacto causal da bolsa.

*Tese (Parte B):* INDICADO_BOLSA_2022 e o marcador observavel de uma trajetoria de
mobilidade social. A hipotese central e que indicados vem predominantemente de escola
publica e se destacam pelo IEG — o programa recompensa comprometimento, nao apenas
capital academico. Se confirmada pelos dados, a tese e: o programa Passos Magicos
funciona como ponte entre vulnerabilidade (escola publica, baixo IDA) e acesso a
educacao privada de qualidade (indicacao para bolsa em FIAP, Einstein, UNISA, Estacio),
com o engajamento (IEG) como o principal vetor dessa transicao.

**Sintese final:**
O programa Passos Magicos e um mecanismo de mobilidade social mensuravel. Os vetores
centrais de resultado sao IEG e IDA; o tempo no programa amplifica ambos. A defasagem
curricular (IAN) e persistente mas nao e determinante: alunos de escola publica, com
IAN inferior, apresentam o maior engajamento e constituem o principal grupo de candidatos
a bolsas em parceiras privadas. Isso evidencia que o programa identifica e desenvolve
potencial onde ele existe, independentemente das condicoes de entrada.
"""
