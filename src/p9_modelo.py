# p9_modelo.py — Pergunta 9: Modelo Preditivo de Risco de Defasagem
# Salva resultados em output_p9.json  |  exporta modelo_risco.pkl
# encoding: utf-8

import json
import pickle
import warnings
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (classification_report, roc_auc_score,
                             confusion_matrix, ConfusionMatrixDisplay, f1_score)
import xgboost as xgb
warnings.filterwarnings('ignore')

df = pd.read_csv('../data/PEDE_PASSOS_DATASET_FIAP.csv', delimiter=';')

# --- Dataset para o modelo ---
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

n_total    = len(df_ml)
n_defasado = int(df_ml['TARGET'].sum())
n_adequado = int((df_ml['TARGET'] == 0).sum())
pct_defasado = round(df_ml['TARGET'].mean() * 100, 1)

print(f'Dataset: {n_total} registros  |  Defasados: {n_defasado} ({pct_defasado}%)  |  Adequados: {n_adequado}')

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

# --- Split treino/teste estratificado (80/20) ---
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f'Treino: {len(X_train)}  |  Teste: {len(X_test)}')

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
        'auc_cv': round(auc_cv, 4), 'f1_cv': round(f1_cv, 4),
        'auc_test': round(auc_test, 4), 'f1_test': round(f1_test, 4),
        'y_pred': y_pred, 'modelo': modelo, 'X_te': X_te,
    }
    print(f'{nome:<22} {auc_cv:>8.3f} {f1_cv:>7.3f} {auc_test:>10.3f} {f1_test:>9.3f}')

# --- Modelo selecionado: Logistic Regression ---
lr_final = LogisticRegression(max_iter=1000, random_state=42)
lr_final.fit(X_train_sc, y_train)

coefs = pd.Series(lr_final.coef_[0], index=feat_cols_eng).sort_values(ascending=False)
print('\nCoeficientes Logistic Regression (por impacto no risco):')
print(coefs.round(3).to_string())

lr_pred = lr_final.predict(X_test_sc)
print(f'\nClassification Report — Logistic Regression (holdout):')
print(classification_report(y_test, lr_pred,
                             target_names=['Adequado (IAN=10)', 'Defasado (IAN<10)']))

# Random Forest para feature importance
rf_final = RandomForestClassifier(n_estimators=200, random_state=42)
rf_final.fit(X, y)
feat_imp = pd.Series(rf_final.feature_importances_, index=feat_cols_eng).sort_values(ascending=False)
print('\nTop 10 features (Random Forest):')
print(feat_imp.head(10).round(4).to_string())

# --- Sistema de recomendacoes ---
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
    'IAA_2020'  : ('baixo',    'Autoconceito muito baixo — trabalhar autoestima e protagonismo'),
    'IAA_2021'  : ('baixo',    'Autoconceito em queda — reforcar feedbacks positivos e conquistas do aluno'),
    'DELTA_IAN' : ('negativo', 'Defasagem curricular aumentando — nivelamento e avaliacao de progressao de fase'),
    'DELTA_IAA' : ('negativo', 'Autoestima deteriorando — intervencao motivacional prioritaria'),
}

def calcular_risco_e_recomendacoes(perfil, modelo, scaler, feat_cols, top_n=3):
    X_aluno = pd.DataFrame([perfil])[feat_cols].fillna(0)
    X_sc    = scaler.transform(X_aluno)
    prob    = modelo.predict_proba(X_sc)[0][1]
    contrib = pd.Series(modelo.coef_[0] * X_sc[0], index=feat_cols)
    top_fatores = contrib.sort_values(ascending=False).head(top_n)
    recomendacoes = []
    for feat, contrib_val in top_fatores.items():
        if feat in RECOMENDACOES and contrib_val > 0:
            _, msg = RECOMENDACOES[feat]
            recomendacoes.append({
                'indicador': feat,
                'contribuicao': round(float(contrib_val), 3),
                'recomendacao': msg,
            })
    return round(prob * 100, 1), recomendacoes

# Demo com 3 perfis sinteticos
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

print('\n=== Demonstracao do Sistema de Recomendacoes ===\n')
demos_resultado = {}
for nome_perfil, perfil in perfis_demo.items():
    prob, recs = calcular_risco_e_recomendacoes(perfil, lr_final, scaler, feat_cols_eng)
    nivel = 'ALTO' if prob >= 70 else 'MEDIO' if prob >= 40 else 'BAIXO'
    print(f'{nome_perfil}')
    print(f'  Probabilidade de defasagem: {prob:.1f}%  [{nivel}]')
    for r in recs:
        print(f'    [{r["indicador"]}] -> {r["recomendacao"]}')
    print()
    demos_resultado[nome_perfil] = {'probabilidade': prob, 'nivel': nivel, 'recomendacoes': recs}

# --- Exportar modelo ---
with open('../modelo_risco.pkl', 'wb') as f:
    pickle.dump({
        'model_lr'      : lr_final,
        'model_rf'      : rf_final,
        'scaler'        : scaler,
        'features'      : feat_cols_eng,
        'recomendacoes' : RECOMENDACOES,
    }, f)
print('Modelo exportado: modelo_risco.pkl')

# --- Graficos ---
fig, axes = plt.subplots(1, 4, figsize=(22, 6))

nomes_mod  = list(resultados.keys())
aucs_cv    = [resultados[n]['auc_cv']   for n in nomes_mod]
aucs_test  = [resultados[n]['auc_test'] for n in nomes_mod]
f1s_cv     = [resultados[n]['f1_cv']    for n in nomes_mod]
f1s_test   = [resultados[n]['f1_test']  for n in nomes_mod]
x_mod = np.arange(len(nomes_mod))
w_mod = 0.35

b1 = axes[0].bar(x_mod - w_mod/2, aucs_cv,   w_mod, label='CV (treino)', color='#5bc0de', alpha=0.85)
b2 = axes[0].bar(x_mod + w_mod/2, aucs_test, w_mod, label='Holdout (teste)', color='#5cb85c', alpha=0.85)
for bar, val in list(zip(b1, aucs_cv)) + list(zip(b2, aucs_test)):
    axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                 f'{val:.3f}', ha='center', va='bottom', fontsize=8)
axes[0].axhline(0.7, color='gray', linestyle='--', linewidth=1)
axes[0].set_title('AUC-ROC\nCV vs Holdout')
axes[0].set_ylim(0.5, 1.0)
axes[0].set_xticks(x_mod)
axes[0].set_xticklabels(nomes_mod, fontsize=7)
axes[0].legend(fontsize=8)

b3 = axes[1].bar(x_mod - w_mod/2, f1s_cv,   w_mod, label='CV (treino)', color='#5bc0de', alpha=0.85)
b4 = axes[1].bar(x_mod + w_mod/2, f1s_test, w_mod, label='Holdout (teste)', color='#5cb85c', alpha=0.85)
for bar, val in list(zip(b3, f1s_cv)) + list(zip(b4, f1s_test)):
    axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                 f'{val:.3f}', ha='center', va='bottom', fontsize=8)
axes[1].set_title('F1-Score\nCV vs Holdout')
axes[1].set_ylim(0.5, 1.0)
axes[1].set_xticks(x_mod)
axes[1].set_xticklabels(nomes_mod, fontsize=7)
axes[1].legend(fontsize=8)

cm = confusion_matrix(y_test, lr_pred)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=['Adequado', 'Defasado'])
disp.plot(ax=axes[2], colorbar=False, cmap='Blues')
axes[2].set_title('Matriz de Confusao\nLogistic Regression (teste)')

top10 = feat_imp.head(10)
cores_fi = ['#5cb85c' if 'DELTA' in n else '#5bc0de' for n in top10.index]
axes[3].barh(top10.index[::-1], top10.values[::-1], color=cores_fi[::-1])
axes[3].set_title('Top 10 Features\n(Random Forest)')
axes[3].set_xlabel('Importancia')

plt.suptitle('Modelo Preditivo — CV vs Holdout + Matriz de Confusao', fontsize=13)
plt.tight_layout()
plt.savefig('../figures/fig_p9_modelo.png', dpi=100, bbox_inches='tight')
plt.close()
print('Figura salva: fig_p9_modelo.png')

# --- Exportar resultados ---
output = {
    'pergunta': 9,
    'titulo': 'Modelo Preditivo de Risco de Defasagem',
    'dataset': {
        'n_total': n_total, 'n_defasado': n_defasado,
        'n_adequado': n_adequado, 'pct_defasado': pct_defasado,
    },
    'n_features': len(feat_cols_eng),
    'features': feat_cols_eng,
    'resultados_modelos': {
        nome: {k: v for k, v in vals.items() if k not in ['y_pred', 'modelo', 'X_te']}
        for nome, vals in resultados.items()
    },
    'coeficientes_lr': {feat: round(float(val), 4) for feat, val in coefs.items()},
    'feature_importance_rf': {feat: round(float(val), 4) for feat, val in feat_imp.head(10).items()},
    'matriz_confusao': cm.tolist(),
    'demo_perfis': demos_resultado,
    'modelo_selecionado': 'Logistic Regression',
    'justificativa': 'Melhor AUC no holdout e coeficientes interpretaveis para recomendacoes',
}

with open('../outputs/output_p9.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
print('Resultado salvo: output_p9.json')
