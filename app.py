# app.py — Streamlit: Sistema de Previsão de Risco de Defasagem
# Passos Mágicos | POSTECH DTAT — Ana Raquel
# encoding: utf-8

import pickle
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# -----------------------------------------------------------------------
# Configuração da página
# -----------------------------------------------------------------------
st.set_page_config(
    page_title="Passos Mágicos — Risco de Defasagem",
    page_icon="🎓",
    layout="wide",
)

# -----------------------------------------------------------------------
# Carregar modelo
# -----------------------------------------------------------------------
@st.cache_resource
def load_model():
    with open("modelo_risco.pkl", "rb") as f:
        return pickle.load(f)

modelo = load_model()
model_lr    = modelo["model_lr"]
model_rf    = modelo["model_rf"]
scaler      = modelo["scaler"]
features    = modelo["features"]
recomendacoes = modelo["recomendacoes"]

INDICADORES = ["IAN", "IDA", "IEG", "IAA", "IPS", "IPP"]

DESCRICAO = {
    "IAN": "Adequação de Nível (alinhamento curricular)",
    "IDA": "Desempenho Acadêmico",
    "IEG": "Engajamento",
    "IAA": "Autoavaliação",
    "IPS": "Aspectos Psicossociais",
    "IPP": "Aspectos Psicopedagógicos",
}

# -----------------------------------------------------------------------
# Header
# -----------------------------------------------------------------------
col_logo, col_titulo = st.columns([1, 5])
with col_logo:
    st.markdown("## 🎓")
with col_titulo:
    st.title("Sistema de Previsão de Risco de Defasagem")
    st.caption("Passos Mágicos · POSTECH DTAT Fase 5 · Ana Raquel")

st.markdown("---")

# -----------------------------------------------------------------------
# Sidebar — entrada de dados
# -----------------------------------------------------------------------
st.sidebar.header("Indicadores do Aluno")
st.sidebar.markdown("Informe os indicadores de **2020** e **2021** (escala 0–10).")

vals_2020 = {}
vals_2021 = {}

for ind in INDICADORES:
    st.sidebar.markdown(f"**{ind}** — {DESCRICAO[ind]}")
    c1, c2 = st.sidebar.columns(2)
    vals_2020[ind] = c1.number_input(
        f"2020", min_value=0.0, max_value=10.0, value=7.0,
        step=0.1, key=f"{ind}_2020", label_visibility="visible"
    )
    vals_2021[ind] = c2.number_input(
        f"2021", min_value=0.0, max_value=10.0, value=7.0,
        step=0.1, key=f"{ind}_2021", label_visibility="visible"
    )

st.sidebar.markdown("---")
prever = st.sidebar.button("🔍 Calcular Risco", use_container_width=True, type="primary")

# -----------------------------------------------------------------------
# Cálculo
# -----------------------------------------------------------------------
def calcular_risco(v20, v21):
    row = []
    deltas = {}
    for ind in INDICADORES:
        row.append(v20[ind])
    for ind in INDICADORES:
        row.append(v21[ind])
    for ind in INDICADORES:
        d = v21[ind] - v20[ind]
        row.append(d)
        deltas[f"DELTA_{ind}"] = d

    X = np.array(row).reshape(1, -1)
    X_sc = scaler.transform(X)

    prob_lr = model_lr.predict_proba(X_sc)[0, 1]
    prob_rf = model_rf.predict_proba(X)[0, 1]
    prob_media = (prob_lr + prob_rf) / 2

    nivel = "ALTO" if prob_media > 0.60 else ("MÉDIO" if prob_media > 0.35 else "BAIXO")
    cor   = "#d9534f" if nivel == "ALTO" else ("#f0ad4e" if nivel == "MÉDIO" else "#5cb85c")

    # Identificar quais indicadores acionam recomendações
    recs_ativas = []
    for feat in features:
        if feat not in recomendacoes:
            continue
        tipo, texto = recomendacoes[feat]
        ind = feat.replace("DELTA_", "").replace("_2020", "").replace("_2021", "")

        if feat.startswith("DELTA_"):
            val = deltas[feat]
            if tipo == "negativo" and val < -0.5:
                recs_ativas.append({"feature": feat, "valor": val, "texto": texto, "prioridade": abs(val)})
        elif "_2020" in feat:
            val = v20[ind]
            if tipo == "baixo" and val < 6.0:
                recs_ativas.append({"feature": feat, "valor": val, "texto": texto, "prioridade": 6.0 - val})
        elif "_2021" in feat:
            val = v21[ind]
            if tipo == "baixo" and val < 6.0:
                recs_ativas.append({"feature": feat, "valor": val, "texto": texto, "prioridade": 6.0 - val})

    recs_ativas.sort(key=lambda x: x["prioridade"], reverse=True)

    return {
        "prob_lr": prob_lr,
        "prob_rf": prob_rf,
        "prob_media": prob_media,
        "nivel": nivel,
        "cor": cor,
        "recs": recs_ativas[:5],
        "deltas": deltas,
    }

# -----------------------------------------------------------------------
# Resultado
# -----------------------------------------------------------------------
if prever:
    resultado = calcular_risco(vals_2020, vals_2021)
    prob   = resultado["prob_media"]
    nivel  = resultado["nivel"]
    cor    = resultado["cor"]

    # --- Painel principal ---
    col_gauge, col_modelos, col_radar = st.columns([2, 1, 2])

    with col_gauge:
        st.subheader("Probabilidade de Defasagem")

        fig_g, ax_g = plt.subplots(figsize=(4, 2.2), subplot_kw={"aspect": "equal"})
        ax_g.set_xlim(-1.2, 1.2)
        ax_g.set_ylim(-0.3, 1.2)

        # Fundo semicircular
        for (start, end, c) in [(180, 120, "#5cb85c"), (120, 60, "#f0ad4e"), (60, 0, "#d9534f")]:
            theta = np.linspace(np.radians(start), np.radians(end), 100)
            ax_g.fill_between(np.cos(theta), np.sin(theta) * 0.55,
                              np.cos(theta) * 0 + 0, alpha=0.0)
            wedge = mpatches.Wedge((0, 0), 1.0, end, start, width=0.35, color=c, alpha=0.85)
            ax_g.add_patch(wedge)

        # Ponteiro
        angle = np.radians(180 - prob * 180)
        ax_g.annotate("", xy=(np.cos(angle) * 0.75, np.sin(angle) * 0.75),
                      xytext=(0, 0),
                      arrowprops=dict(arrowstyle="-|>", color="black", lw=2))
        ax_g.plot(0, 0, "ko", markersize=8)

        ax_g.text(0, -0.15, f"{prob*100:.1f}%", ha="center", va="center",
                  fontsize=22, fontweight="bold", color=cor)
        ax_g.text(-1.0, -0.25, "BAIXO", ha="center", fontsize=8, color="#5cb85c")
        ax_g.text(0,    -0.25, "MÉDIO", ha="center", fontsize=8, color="#f0ad4e")
        ax_g.text(1.0,  -0.25, "ALTO",  ha="center", fontsize=8, color="#d9534f")
        ax_g.axis("off")
        st.pyplot(fig_g, use_container_width=True)
        plt.close()

        nivel_emoji = "🔴" if nivel == "ALTO" else ("🟡" if nivel == "MÉDIO" else "🟢")
        st.markdown(
            f"<h3 style='text-align:center; color:{cor}'>{nivel_emoji} Risco {nivel}</h3>",
            unsafe_allow_html=True
        )

    with col_modelos:
        st.subheader("Por modelo")
        st.metric("Logistic Regression", f"{resultado['prob_lr']*100:.1f}%")
        st.metric("Random Forest",       f"{resultado['prob_rf']*100:.1f}%")
        st.metric("Média (usado)",        f"{prob*100:.1f}%")
        st.caption("Limites: < 35% = Baixo · 35–60% = Médio · > 60% = Alto")

    with col_radar:
        st.subheader("Perfil dos indicadores")

        labels = INDICADORES
        vals20 = [vals_2020[i] for i in labels]
        vals21 = [vals_2021[i] for i in labels]

        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        angles += angles[:1]
        vals20 += vals20[:1]
        vals21 += vals21[:1]

        fig_r, ax_r = plt.subplots(figsize=(4, 4), subplot_kw={"polar": True})
        ax_r.plot(angles, vals20, "o-", color="#5bc0de", linewidth=1.5, label="2020")
        ax_r.fill(angles, vals20, alpha=0.15, color="#5bc0de")
        ax_r.plot(angles, vals21, "o-", color="#d9534f", linewidth=1.5, label="2021")
        ax_r.fill(angles, vals21, alpha=0.15, color="#d9534f")
        ax_r.set_thetagrids(np.degrees(angles[:-1]), labels, fontsize=10)
        ax_r.set_ylim(0, 10)
        ax_r.set_yticks([2.5, 5, 7.5, 10])
        ax_r.set_yticklabels(["2.5", "5", "7.5", "10"], fontsize=7)
        ax_r.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=9)
        ax_r.grid(True, alpha=0.3)
        st.pyplot(fig_r, use_container_width=True)
        plt.close()

    st.markdown("---")

    # --- Deltas ---
    st.subheader("Evolução 2020 → 2021")
    dcols = st.columns(len(INDICADORES))
    for i, ind in enumerate(INDICADORES):
        d = resultado["deltas"][f"DELTA_{ind}"]
        sinal = "↑" if d > 0.1 else ("↓" if d < -0.1 else "→")
        cor_d = "#5cb85c" if d > 0.1 else ("#d9534f" if d < -0.1 else "#888")
        dcols[i].markdown(
            f"<div style='text-align:center'>"
            f"<b>{ind}</b><br>"
            f"<span style='font-size:1.4em; color:{cor_d}'>{sinal} {d:+.1f}</span>"
            f"</div>",
            unsafe_allow_html=True
        )

    st.markdown("---")

    # --- Recomendações ---
    st.subheader("🎯 Recomendações de Intervenção")
    if resultado["recs"]:
        for rec in resultado["recs"]:
            icone = "🔴" if rec["prioridade"] > 2.5 else ("🟡" if rec["prioridade"] > 1.0 else "🟠")
            st.markdown(f"{icone} **{rec['feature']}** (valor: {rec['valor']:.2f}) — {rec['texto']}")
    else:
        st.success("✅ Nenhum indicador crítico identificado. O perfil do aluno está dentro dos parâmetros adequados.")

    # --- Nota metodológica ---
    with st.expander("ℹ️ Nota metodológica"):
        st.markdown("""
        **Modelo:** Logistic Regression (principal) + Random Forest (complementar), média das probabilidades.

        **Features:** 6 indicadores × 2 anos (2020 e 2021) + 6 deltas = 18 features.

        **Performance (holdout 20%):** LR AUC=0.907 / F1=0.889 · RF AUC=0.866 / F1=0.879

        **Limitações:**
        - Treinado em coorte longitudinal pequena (~314 alunos com dados em 2020, 2021 e 2022)
        - IDA muda de metodologia em 2022 — o target pode conter ruído sistêmico
        - Sem validação prospectiva (dados 2023/2024 não disponíveis)

        Este sistema é um **indicador de direção** para intervenção preventiva, não um sistema de previsão de alta confiança.
        """)

else:
    # Estado inicial — instruções
    st.info("👈 Preencha os indicadores na barra lateral e clique em **Calcular Risco**.")

    st.markdown("### Como usar")
    st.markdown("""
    1. Informe os valores dos **6 indicadores** do aluno nos anos de **2020 e 2021** (escala 0–10)
    2. Clique em **Calcular Risco**
    3. O sistema retorna a **probabilidade de defasagem em 2022** + recomendações de intervenção

    | Indicador | Descrição |
    |-----------|-----------|
    | IAN | Adequação de Nível — alinhamento entre série e desempenho |
    | IDA | Desempenho Acadêmico |
    | IEG | Engajamento nas atividades do programa |
    | IAA | Autoavaliação do próprio aluno |
    | IPS | Aspectos Psicossociais (contexto de vida) |
    | IPP | Aspectos Psicopedagógicos (suporte de aprendizagem) |
    """)

    st.markdown("### Sobre o modelo")
    col1, col2, col3 = st.columns(3)
    col1.metric("AUC-ROC (holdout)", "0.907", "Logistic Regression")
    col2.metric("F1-Score (holdout)", "0.889", "Logistic Regression")
    col3.metric("Alunos na coorte", "314", "~23% da base total")

    st.caption("Passos Mágicos · POSTECH DTAT Fase 5 · Ana Raquel · 2026")
