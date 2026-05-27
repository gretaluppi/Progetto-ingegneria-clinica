import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import ttest_ind

st.set_page_config(page_title="Statistical Analysis", page_icon="📊", layout="wide")

# =========================
# LOGIN CHECK
# =========================
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("⚠️ Please log in from the Homepage.")
    st.stop()

# =========================
# CARICAMENTO DATI
# =========================
@st.cache_data
def load_data():
    df_pd = pd.read_csv("PD.csv", sep=",", header=1)
    df_control = pd.read_csv("CONTROLS.csv", sep=",", header=1)

    df_pd = df_pd.rename(columns={"Age (years)": "Age"})
    df_control = df_control.rename(columns={"Age (years)": "Age"})

    df_pd["GRUPPO"] = "PD"
    df_control["GRUPPO"] = "CONTROL"

    df = pd.concat([df_pd, df_control], ignore_index=True)
    return df, df_pd, df_control


def calcolo_UPDRS(row):
    """Calcola UPDRS totale sommando MDS-UPDRS parte 1, 2, 3 e 4."""
    lista1 = [row.get(f"MDSUPDRS_1-{i}") for i in range(1, 14)]
    lista2 = [row.get(f"MDSUPDRS_2-{i}") for i in range(1, 14)]
    lista3 = [
        row.get("MDSUPDRS_3-1"), row.get("MDSUPDRS_3-2"),
        row.get("MDSUPDRS_3-3-Neck"), row.get("MDSUPDRS_3-3-RUE"), row.get("MDSUPDRS_3-3-LLE"),
        row.get("MDSUPDRS_3-4-R"), row.get("MDSUPDRS_3-4-L"),
        row.get("MDSUPDRS_3-5-R"), row.get("MDSUPDRS_3-5-L"),
        row.get("MDSUPDRS_3-6-R"), row.get("MDSUPDRS_3-6-L"),
        row.get("MDSUPDRS_3-7-R"), row.get("MDSUPDRS_3-7-L"),
        row.get("MDSUPDRS_3-8-R"), row.get("MDSUPDRS_3-8-L"),
        row.get("MDSUPDRS_3-9"), row.get("MDSUPDRS_3-10"), row.get("MDSUPDRS_3-11"),
        row.get("MDSUPDRS_3-12"), row.get("MDSUPDRS_3-13"), row.get("MDSUPDRS_3-14"),
        row.get("MDSUPDRS_3-15-R"), row.get("MDSUPDRS_3-15-L"),
        row.get("MDSUPDRS_3-16-L"), row.get("MDSUPDRS_3-16-R"),
        row.get("MDSUPDRS_3-17-RUE"), row.get("MDSUPDRS_3-17-LUE"),
        row.get("MDSUPDRS_3-17-RLE"), row.get("MDSUPDRS_3-17-LLE"),
        row.get("MDSUPDRS_3-17-LipJaw"), row.get("MDSUPDRS_3-18"),
    ]
    lista4 = [row.get(f"MDSUPDRS_4-{i}") for i in range(1, 7)]

    valori = lista1 + lista2 + lista3 + lista4
    valori_num = pd.to_numeric(pd.Series(valori), errors="coerce")

    if valori_num.isna().any():
        return None
    return float(valori_num.sum())


# Colonne tremori da MDS-UPDRS parte 3
TREMOR_COLS = [
    "MDSUPDRS_3-15-R", "MDSUPDRS_3-15-L",       # postural/action tremor
    "MDSUPDRS_3-16-L", "MDSUPDRS_3-16-R",       # kinetic/rest tremor amplitude
    "MDSUPDRS_3-17-RUE", "MDSUPDRS_3-17-LUE",   # rest tremor upper limbs
    "MDSUPDRS_3-17-RLE", "MDSUPDRS_3-17-LLE",   # rest tremor lower limbs
    "MDSUPDRS_3-17-LipJaw",                      # lip/jaw tremor
]


def calcola_tremori(row):
    """Somma le voci MDS-UPDRS relative ai tremori."""
    vals = pd.to_numeric(pd.Series([row.get(c) for c in TREMOR_COLS]), errors="coerce")
    if vals.isna().any():
        return None
    return float(vals.sum())


def classifica_updrs(x):
    if x <= 32:
        return "Mild (0–32)"
    elif x <= 58:
        return "Moderate (33–58)"
    elif x <= 102:
        return "Severe (59–102)"
    else:
        return "Critical (>103)"


def trova_colonna(df, possibili_nomi):
    """Trova automaticamente una colonna tra nomi possibili."""
    for nome in possibili_nomi:
        if nome in df.columns:
            return nome
    return None


# =========================
# FUNZIONI STATISTICHE
# =========================
def stat_table(series_dict: dict) -> pd.DataFrame:
    """
    Restituisce media, mediana, moda, deviazione standard, min, max e N.
    """
    rows = []
    for nome, s in series_dict.items():
        s = pd.to_numeric(s, errors="coerce").dropna()

        if len(s) == 0:
            rows.append({
                "Group": nome,
                "N": 0,
                "Mean": None,
                "Median": None,
                "Mode": None,
                "Std Dev": None,
                "Min": None,
                "Max": None,
            })
            continue

        moda_vals = s.mode()
        moda = round(float(moda_vals.iloc[0]), 2) if not moda_vals.empty else None

        rows.append({
            "Group": nome,
            "N": len(s),
            "Mean": round(float(s.mean()), 2),
            "Median": round(float(s.median()), 2),
            "Mode": moda,
            "Std Dev": round(float(s.std()), 2),
            "Min": round(float(s.min()), 2),
            "Max": round(float(s.max()), 2),
        })

    return pd.DataFrame(rows).set_index("Group")


def run_ttest(s1: pd.Series, s2: pd.Series, label1: str, label2: str):
    """Esegue t-test di Welch e mostra t-statistic e p-value."""
    s1 = pd.to_numeric(s1, errors="coerce").dropna()
    s2 = pd.to_numeric(s2, errors="coerce").dropna()

    if len(s1) < 2 or len(s2) < 2:
        st.warning("Campioni insufficienti per il t-test.")
        return

    t_stat, p_val = ttest_ind(s1, s2, equal_var=False, nan_policy="omit")

    col1, col2, col3 = st.columns(3)
    col1.metric("T-statistic", round(float(t_stat), 4))
    col2.metric("P-value", round(float(p_val), 6))
    col3.metric("Significant (p < 0.05)", "✅ Yes" if p_val < 0.05 else "❌ No")

    if p_val < 0.05:
        st.success(f"Statistically significant difference between **{label1}** and **{label2}** (p = {round(float(p_val), 4)}).")
    else:
        st.info(f"No statistically significant difference between **{label1}** and **{label2}** (p = {round(float(p_val), 4)}).")


def boxswarm(df_plot, x_col, y_col, color_map, title=""):
    """Crea boxplot + punti individuali."""
    fig = go.Figure()

    for group, color in color_map.items():
        sub = df_plot[df_plot[x_col] == group][y_col].dropna()
        if len(sub) == 0:
            continue

        hex_color = color
        r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)

        fig.add_trace(go.Box(
            x=[group] * len(sub),
            y=sub,
            name=group,
            boxmean=True,
            line=dict(color=hex_color),
            fillcolor=f"rgba({r},{g},{b},0.25)",
        ))

        fig.add_trace(go.Scatter(
            x=[group] * len(sub),
            y=sub,
            mode="markers",
            marker=dict(size=6, color=hex_color, opacity=0.7),
            showlegend=False,
        ))

    fig.update_layout(
        title=title,
        margin=dict(t=30, b=10),
        boxmode="overlay",
        template="plotly_white",
    )
    return fig


# =========================
# PREPARAZIONE DATASET
# =========================
df, df_pd, df_control = load_data()

# Calcolo UPDRS solo sui pazienti PD
df_pd["UPDRS"] = df_pd.apply(calcolo_UPDRS, axis=1)
df_pd = df_pd.dropna(subset=["UPDRS"]).copy()
df_pd["UPDRS"] = df_pd["UPDRS"].astype(float)

# Classificazione severità
df_pd["UPDRS_CLASS"] = df_pd["UPDRS"].apply(classifica_updrs)

# Tremor score
df_pd["TREMOR_SCORE"] = df_pd.apply(calcola_tremori, axis=1)

# Mobilità alta/bassa: qui usiamo UPDRS come proxy clinico della mobilità
updrs_median = df_pd["UPDRS"].median()
df_pd["MOBILITY_CLASS"] = df_pd["UPDRS"].apply(
    lambda x: "High mobility (low UPDRS)" if x <= updrs_median else "Low mobility (high UPDRS)"
)

# Colonna diagnosi: prova a riconoscerla automaticamente
DIAGNOSIS_COL = trova_colonna(df_pd, [
    "Years since PD diagnosis",
    "Years since diagnosis",
    "Disease duration",
    "Disease Duration",
    "PD duration",
    "Years from diagnosis",
])

# Ordini e colori
UPDRS_ORDER = ["Mild (0–32)", "Moderate (33–58)", "Severe (59–102)", "Critical (>103)"]
COLOR_UPDRS = {
    "Mild (0–32)": "#378ADD",
    "Moderate (33–58)": "#EF9F27",
    "Severe (59–102)": "#E24B4A",
    "Critical (>103)": "#7F77DD",
}
COLOR_MOBILITY = {
    "High mobility (low UPDRS)": "#5DCAA5",
    "Low mobility (high UPDRS)": "#E24B4A",
}
COLOR_GENDER = {
    "Male": "#4A90D9",
    "Female": "#E8729A",
}

# =========================
# PAGINA STREAMLIT
# =========================
st.title("Statistical Analysis")
st.caption("Descriptive statistics, t-test and p-value for clinical and motor variables in Parkinson's disease patients.")
st.divider()

# Metriche iniziali
col1, col2, col3, col4 = st.columns(4)
col1.metric("PD patients", len(df_pd))
col2.metric("Mean UPDRS", round(df_pd["UPDRS"].mean(), 2))
col3.metric("Median UPDRS", round(df_pd["UPDRS"].median(), 2))
col4.metric("Mean tremor score", round(pd.to_numeric(df_pd["TREMOR_SCORE"], errors="coerce").mean(), 2))

st.divider()

tab1, tab2, tab3, tab4 = st.tabs([
    "📐 Mobility × UPDRS",
    "🏃 High vs Low mobility",
    "⏱️ Severity × Diagnosis",
    "🤝 Tremors",
])

# ================================================
# TAB 1 — Mobilità PD per UPDRS
# ================================================
with tab1:
    st.subheader("Mobility in relation to UPDRS severity")
    st.write(
        "In this section, UPDRS is used to stratify PD patients by clinical/motor severity. "
        "For each severity class, the table reports mode, mean, median, standard deviation, minimum, maximum and sample size."
    )

    df_t1 = df_pd[["UPDRS", "UPDRS_CLASS"]].dropna().copy()
    groups_present = [g for g in UPDRS_ORDER if g in df_t1["UPDRS_CLASS"].unique()]

    st.markdown("##### Descriptive statistics — UPDRS by severity class")
    st.dataframe(
        stat_table({g: df_t1[df_t1["UPDRS_CLASS"] == g]["UPDRS"] for g in groups_present}),
        use_container_width=True,
    )

    st.divider()
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("##### UPDRS distribution by severity class")
        fig_box = boxswarm(df_t1, "UPDRS_CLASS", "UPDRS", COLOR_UPDRS)
        fig_box.update_layout(yaxis_title="UPDRS score", xaxis_title="Severity class")
        st.plotly_chart(fig_box, use_container_width=True)

    with col_b:
        st.markdown("##### Number of patients per severity class")
        counts = df_t1["UPDRS_CLASS"].value_counts().reset_index()
        counts.columns = ["Class", "Count"]
        fig_bar = px.bar(
            counts,
            x="Class",
            y="Count",
            color="Class",
            color_discrete_map=COLOR_UPDRS,
            text="Count",
        )
        fig_bar.update_layout(showlegend=False, template="plotly_white", margin=dict(t=10, b=10))
        st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()
    st.markdown("##### T-test and p-value — Mild vs Severe UPDRS")
    mild = df_t1[df_t1["UPDRS_CLASS"] == "Mild (0–32)"]["UPDRS"]
    severe = df_t1[df_t1["UPDRS_CLASS"] == "Severe (59–102)"]["UPDRS"]
    run_ttest(mild, severe, "Mild", "Severe")

# ================================================
# TAB 2 — Pazienti alti e bassi / mobilità alta-bassa
# ================================================
with tab2:
    st.subheader("Mobility between high and low patients")
    st.write(
        f"Patients are divided according to the median UPDRS value ({round(float(updrs_median), 2)}). "
        "Patients below or equal to the median are classified as high mobility, while patients above the median are classified as low mobility."
    )

    df_t2 = df_pd[["UPDRS", "MOBILITY_CLASS", "Age", "Gender"]].dropna().copy()

    st.markdown("##### Descriptive statistics — UPDRS by mobility class")
    st.dataframe(
        stat_table({g: df_t2[df_t2["MOBILITY_CLASS"] == g]["UPDRS"] for g in COLOR_MOBILITY}),
        use_container_width=True,
    )

    st.divider()
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("##### UPDRS distribution by mobility class")
        fig_mob = boxswarm(df_t2, "MOBILITY_CLASS", "UPDRS", COLOR_MOBILITY)
        fig_mob.update_layout(yaxis_title="UPDRS score", xaxis_title="Mobility class")
        st.plotly_chart(fig_mob, use_container_width=True)

    with col_b:
        st.markdown("##### Age distribution by mobility class")
        fig_age = px.histogram(
            df_t2,
            x="Age",
            color="MOBILITY_CLASS",
            barmode="overlay",
            opacity=0.7,
            color_discrete_map=COLOR_MOBILITY,
            labels={"Age": "Age", "MOBILITY_CLASS": "Mobility class"},
        )
        fig_age.update_layout(template="plotly_white", margin=dict(t=10, b=10))
        st.plotly_chart(fig_age, use_container_width=True)

    st.divider()
    st.markdown("##### T-test and p-value — High mobility vs Low mobility")
    high = df_t2[df_t2["MOBILITY_CLASS"] == "High mobility (low UPDRS)"]["UPDRS"]
    low = df_t2[df_t2["MOBILITY_CLASS"] == "Low mobility (high UPDRS)"]["UPDRS"]
    run_ttest(high, low, "High mobility", "Low mobility")

    st.divider()
    st.markdown("##### Gender split within mobility classes")
    gender_mob = df_t2.groupby(["MOBILITY_CLASS", "Gender"]).size().reset_index(name="Count")
    fig_gender = px.bar(
        gender_mob,
        x="MOBILITY_CLASS",
        y="Count",
        color="Gender",
        barmode="group",
        color_discrete_map=COLOR_GENDER,
        labels={"MOBILITY_CLASS": "Mobility class"},
    )
    fig_gender.update_layout(template="plotly_white", margin=dict(t=10, b=10))
    st.plotly_chart(fig_gender, use_container_width=True)

# ================================================
# TAB 3 — Severità patologia in relazione alla diagnosi
# ================================================
with tab3:
    st.subheader("Disease severity in relation to diagnosis duration")

    if DIAGNOSIS_COL is None:
        st.error(
            "No column related to years since diagnosis was found. "
            "Check the exact column name in PD.csv and add it to the DIAGNOSIS_COL search list."
        )
        st.write("Available columns:")
        st.write(list(df_pd.columns))
    else:
        st.write(f"Diagnosis duration column used: **{DIAGNOSIS_COL}**")

        df_t3 = df_pd[["UPDRS", "UPDRS_CLASS", DIAGNOSIS_COL]].copy()
        df_t3[DIAGNOSIS_COL] = pd.to_numeric(df_t3[DIAGNOSIS_COL], errors="coerce")
        df_t3 = df_t3.dropna()

        st.markdown("##### Descriptive statistics — years since diagnosis by UPDRS severity class")
        st.dataframe(
            stat_table({
                g: df_t3[df_t3["UPDRS_CLASS"] == g][DIAGNOSIS_COL]
                for g in UPDRS_ORDER if g in df_t3["UPDRS_CLASS"].unique()
            }),
            use_container_width=True,
        )

        st.divider()
        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("##### Years since diagnosis by severity class")
            fig_diag = boxswarm(df_t3, "UPDRS_CLASS", DIAGNOSIS_COL, COLOR_UPDRS)
            fig_diag.update_layout(yaxis_title="Years since diagnosis", xaxis_title="UPDRS class")
            st.plotly_chart(fig_diag, use_container_width=True)

        with col_b:
            st.markdown("##### UPDRS vs years since diagnosis")

            fig_scatter = px.scatter(
            df_t3,
            x=DIAGNOSIS_COL,
            y="UPDRS",
            color="UPDRS_CLASS",
            labels={
                DIAGNOSIS_COL: "Years since diagnosis",
                "UPDRS": "UPDRS score"
            }
        )

    fig_scatter.update_layout(
        template="plotly_white",
        margin=dict(t=10, b=10)
    )

    st.plotly_chart(
        fig_scatter,
        use_container_width=True
    )
    st.divider()
    st.markdown("##### T-test and p-value — Short vs Long disease duration")
    soglia = st.slider("Choose threshold for disease duration groups (years)", 1, 20, 5)
    early = df_t3[df_t3[DIAGNOSIS_COL] < soglia]["UPDRS"]
    late = df_t3[df_t3[DIAGNOSIS_COL] >= soglia]["UPDRS"]
    run_ttest(early, late, f"< {soglia} years", f"≥ {soglia} years")

# ================================================
# TAB 4 — Tremori
# ================================================
with tab4:
    st.subheader("Tremor analysis")
    st.write(
        "Tremor score is calculated as the sum of specific MDS-UPDRS Part III tremor items: "
        "3-15, 3-16 and 3-17."
    )

    df_t4 = df_pd[["UPDRS", "UPDRS_CLASS", "MOBILITY_CLASS", "Gender", "Age", "TREMOR_SCORE"]].copy()
    df_t4["TREMOR_SCORE"] = pd.to_numeric(df_t4["TREMOR_SCORE"], errors="coerce")
    df_t4 = df_t4.dropna(subset=["TREMOR_SCORE"])

    st.markdown("##### Descriptive statistics — tremor score by UPDRS severity class")
    st.dataframe(
        stat_table({
            g: df_t4[df_t4["UPDRS_CLASS"] == g]["TREMOR_SCORE"]
            for g in UPDRS_ORDER if g in df_t4["UPDRS_CLASS"].unique()
        }),
        use_container_width=True,
    )

    st.divider()
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("##### Tremor score distribution by severity class")
        fig_tremor = boxswarm(df_t4, "UPDRS_CLASS", "TREMOR_SCORE", COLOR_UPDRS)
        fig_tremor.update_layout(yaxis_title="Tremor score", xaxis_title="UPDRS class")
        st.plotly_chart(fig_tremor, use_container_width=True)

    with col_b:
        st.markdown("##### Tremor score vs total UPDRS")
        fig_tremor_scatter = px.scatter(
            df_t4,
            x="UPDRS",
            y="TREMOR_SCORE",
            color="UPDRS_CLASS",
            color_discrete_map=COLOR_UPDRS,
            trendline="ols",
            labels={"UPDRS": "Total UPDRS", "TREMOR_SCORE": "Tremor score"},
            hover_data=["Age", "Gender"],
        )
        fig_tremor_scatter.update_layout(template="plotly_white", margin=dict(t=10, b=10))
        st.plotly_chart(fig_tremor_scatter, use_container_width=True)

    st.divider()
    col_c, col_d = st.columns(2)

    with col_c:
        st.markdown("##### Tremor score by gender")
        fig_gender_tremor = boxswarm(df_t4, "Gender", "TREMOR_SCORE", COLOR_GENDER)
        fig_gender_tremor.update_layout(yaxis_title="Tremor score", xaxis_title="Gender")
        st.plotly_chart(fig_gender_tremor, use_container_width=True)

    with col_d:
        st.markdown("##### Tremor score by mobility class")
        fig_mob_tremor = boxswarm(df_t4, "MOBILITY_CLASS", "TREMOR_SCORE", COLOR_MOBILITY)
        fig_mob_tremor.update_layout(yaxis_title="Tremor score", xaxis_title="Mobility class")
        st.plotly_chart(fig_mob_tremor, use_container_width=True)

    st.divider()
    st.markdown("##### T-test and p-value — Tremor score: High mobility vs Low mobility")
    high_tr = df_t4[df_t4["MOBILITY_CLASS"] == "High mobility (low UPDRS)"]["TREMOR_SCORE"]
    low_tr = df_t4[df_t4["MOBILITY_CLASS"] == "Low mobility (high UPDRS)"]["TREMOR_SCORE"]
    run_ttest(high_tr, low_tr, "High mobility", "Low mobility")

    st.divider()
    st.markdown("##### Mean score of individual tremor items")
    tr_means = {}
    for c in TREMOR_COLS:
        if c in df_pd.columns:
            vals = pd.to_numeric(df_pd[c], errors="coerce").dropna()
            if not vals.empty:
                tr_means[c.replace("MDSUPDRS_", "")] = round(float(vals.mean()), 3)

    if tr_means:
        fig_items = px.bar(
            x=list(tr_means.keys()),
            y=list(tr_means.values()),
            labels={"x": "UPDRS item", "y": "Mean score"},
            text=list(tr_means.values()),
        )
        fig_items.update_layout(
            template="plotly_white",
            margin=dict(t=10, b=10),
            showlegend=False,
        )
        st.plotly_chart(fig_items, use_container_width=True)
    else:
        st.warning("No tremor item columns found in the dataset.")
