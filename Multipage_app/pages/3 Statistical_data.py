# import streamlit as st
# import pandas as pd
# import plotly.express as px
# from scipy.stats import ttest_ind

st.set_page_config(page_title="Analisi Statistica", page_icon="📊", layout="wide")

# LOGIN CHECK
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("⚠️ Please log in from the Homepage.")
    st.stop()

# st.title("📊 Analisi Statistica")
# st.markdown("""
# Questa sezione permette di confrontare le caratteristiche motorie tra pazienti Parkinson e soggetti sani,
# oppure di analizzare la mobilità in relazione alla severità della patologia.
# """)

# # =========================
# # CARICAMENTO DATI
# # =========================

# @st.cache_data
# def load_data():
#     pd_data = pd.read_csv("PD.csv")
#     controls_data = pd.read_csv("CONTROLS.csv")

#     pd_data["GRUPPO"] = "PD"
#     controls_data["GRUPPO"] = "CONTROL"

#     df = pd.concat([pd_data, controls_data], ignore_index=True)
#     return df

# df = load_data()

# # =========================
# # CONTROLLO COLONNE
# # =========================

# numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()

# if len(numeric_cols) == 0:
#     st.error("Non sono presenti colonne numeriche utilizzabili per l'analisi.")
#     st.stop()

# # =========================
# # SIDEBAR
# # =========================

# st.sidebar.header("Impostazioni analisi")

# tipo_analisi = st.sidebar.selectbox(
#     "Seleziona il tipo di analisi",
#     [
#         "PD vs Controls",
#         "Mobilità vs Severità UPDRS",
#         "Mobilità Alta vs Bassa"
#     ]
# )

# variabile = st.sidebar.selectbox(
#     "Seleziona la variabile numerica",
#     numeric_cols
# )

# # Filtro sesso se presente
# if "Gender" in df.columns:
#     sesso = st.sidebar.multiselect(
#         "Filtra per sesso",
#         options=df["Gender"].dropna().unique(),
#         default=df["Gender"].dropna().unique()
#     )
#     df = df[df["Gender"].isin(sesso)]

# # Filtro età se presente
# if "Age" in df.columns:
#     min_age = int(df["Age"].min())
#     max_age = int(df["Age"].max())

#     age_range = st.sidebar.slider(
#         "Filtra per età",
#         min_value=min_age,
#         max_value=max_age,
#         value=(min_age, max_age)
#     )

#     df = df[(df["Age"] >= age_range[0]) & (df["Age"] <= age_range[1])]

# # =========================
# # FUNZIONE STATISTICHE
# # =========================

# def statistiche_descrittive(data, gruppo_col, value_col):
#     stats = data.groupby(gruppo_col)[value_col].agg(
#         Media="mean",
#         Mediana="median",
#         Deviazione_standard="std",
#         Minimo="min",
#         Massimo="max",
#         Numero_campioni="count"
#     )

#     stats["Moda"] = data.groupby(gruppo_col)[value_col].agg(
#         lambda x: x.mode().iloc[0] if not x.mode().empty else None
#     )

#     return stats.round(3)

# # =========================
# # ANALISI 1: PD VS CONTROLS
# # =========================

# if tipo_analisi == "PD vs Controls":

#     st.subheader("Confronto PD vs Controls")

#     df_analysis = df[["GRUPPO", variabile]].dropna()

#     st.markdown(f"""
#     In questa analisi viene confrontata la variabile **{variabile}** tra pazienti Parkinson e soggetti sani.
#     """)

#     st.dataframe(
#         statistiche_descrittive(df_analysis, "GRUPPO", variabile),
#         use_container_width=True
#     )

#     fig = px.box(
#         df_analysis,
#         x="GRUPPO",
#         y=variabile,
#         points="all",
#         title=f"Boxplot di {variabile} - PD vs Controls"
#     )

#     st.plotly_chart(fig, use_container_width=True)

#     pd_group = df_analysis[df_analysis["GRUPPO"] == "PD"][variabile]
#     control_group = df_analysis[df_analysis["GRUPPO"] == "CONTROL"][variabile]

#     if len(pd_group) > 1 and len(control_group) > 1:
#         t_stat, p_value = ttest_ind(
#             pd_group,
#             control_group,
#             equal_var=False,
#             nan_policy="omit"
#         )

#         col1, col2 = st.columns(2)

#         col1.metric("T-statistic", round(t_stat, 4))
#         col2.metric("P-value", round(p_value, 4))

#         if p_value < 0.05:
#             st.success("Differenza statisticamente significativa tra PD e Controls.")
#         else:
#             st.info("Non emerge una differenza statisticamente significativa tra PD e Controls.")
#     else:
#         st.warning("Campioni insufficienti per eseguire il t-test.")

# # =========================
# # ANALISI 2: MOBILITÀ VS UPDRS
# # =========================

# elif tipo_analisi == "Mobilità vs Severità UPDRS":

#     st.subheader("Analisi della mobilità in base alla severità UPDRS")

#     if "UPDRS" not in df.columns:
#         st.error("La colonna UPDRS non è presente nel dataset.")
#         st.stop()

#     df_pd = df[df["GRUPPO"] == "PD"].copy()
#     df_pd = df_pd[["UPDRS", variabile]].dropna()

#     def classifica_updrs(x):
#         if x <= 1:
#             return "Lieve"
#         elif x <= 3:
#             return "Moderata"
#         else:
#             return "Severa"

#     df_pd["Severità_UPDRS"] = df_pd["UPDRS"].apply(classifica_updrs)

#     st.markdown(f"""
#     In questa analisi viene valutata la variabile **{variabile}** nei pazienti Parkinson,
#     suddivisi in base alla severità clinica UPDRS.
#     """)

#     st.dataframe(
#         statistiche_descrittive(df_pd, "Severità_UPDRS", variabile),
#         use_container_width=True
#     )

#     fig = px.box(
#         df_pd,
#         x="Severità_UPDRS",
#         y=variabile,
#         points="all",
#         title=f"{variabile} in funzione della severità UPDRS"
#     )

#     st.plotly_chart(fig, use_container_width=True)

#     fig_scatter = px.scatter(
#         df_pd,
#         x="UPDRS",
#         y=variabile,
#         color="Severità_UPDRS",
#         trendline="ols",
#         title=f"Relazione tra UPDRS e {variabile}"
#     )

#     st.plotly_chart(fig_scatter, use_container_width=True)

# # =========================
# # ANALISI 3: MOBILITÀ ALTA VS BASSA
# # =========================

# elif tipo_analisi == "Mobilità Alta vs Bassa":

#     st.subheader("Classificazione Mobilità Alta vs Bassa")

#     if "UPDRS" not in df.columns:
#         st.error("La colonna UPDRS non è presente nel dataset.")
#         st.stop()

#     df_pd = df[df["GRUPPO"] == "PD"].copy()
#     df_pd = df_pd[["UPDRS", variabile]].dropna()

#     soglia = df_pd[variabile].median()

#     df_pd["Classe_Mobilità"] = df_pd[variabile].apply(
#         lambda x: "Mobilità Alta" if x >= soglia else "Mobilità Bassa"
#     )

#     st.markdown(f"""
#     I pazienti Parkinson vengono suddivisi in due gruppi sulla base della mediana della variabile **{variabile}**.

#     Soglia utilizzata: **{round(soglia, 3)}**
#     """)

#     st.dataframe(
#         statistiche_descrittive(df_pd, "Classe_Mobilità", "UPDRS"),
#         use_container_width=True
#     )

#     fig = px.box(
#         df_pd,
#         x="Classe_Mobilità",
#         y="UPDRS",
#         points="all",
#         title="Distribuzione UPDRS tra Mobilità Alta e Bassa"
#     )

#     st.plotly_chart(fig, use_container_width=True)

#     alta = df_pd[df_pd["Classe_Mobilità"] == "Mobilità Alta"]["UPDRS"]
#     bassa = df_pd[df_pd["Classe_Mobilità"] == "Mobilità Bassa"]["UPDRS"]

#     if len(alta) > 1 and len(bassa) > 1:
#         t_stat, p_value = ttest_ind(
#             alta,
#             bassa,
#             equal_var=False,
#             nan_policy="omit"
#         )

#         col1, col2 = st.columns(2)

#         col1.metric("T-statistic", round(t_stat, 4))
#         col2.metric("P-value", round(p_value, 4))

#         if p_value < 0.05:
#             st.success("La severità UPDRS differisce significativamente tra mobilità alta e bassa.")
#         else:
#             st.info("Non emerge una differenza statisticamente significativa tra i due gruppi.")
#     else:
#         st.warning("Campioni insufficienti per eseguire il t-test.")