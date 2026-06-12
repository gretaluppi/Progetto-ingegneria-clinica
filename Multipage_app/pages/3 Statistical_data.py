import os
import glob
import re
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import ttest_ind

# 1. CONFIGURAZIONE DELLA PAGINA
st.set_page_config(page_title="Statistical Analysis Dashboard", page_icon="📊", layout="wide")

# VERIFICA LOGIN
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("⚠️ Please log in from the Homepage.")
    st.stop()

# 2. COSTANTI E CONFIGURAZIONI DEI GRAFICI
UPDRS_ORDER = ["Mild (0-32)", "Moderate (33-58)", "Severe (59-102)", "Critical (>103)"]
COLOR_UPDRS = {"Mild (0-32)": "#378ADD", "Moderate (33-58)": "#EF9F27", "Severe (59-102)": "#E24B4A", "Critical (>103)": "#7F77DD"}
COLOR_MOBILITY = {"High mobility (higher velocity)": "#5DCAA5", "Low mobility (lower velocity)": "#E24B4A"}
TREMOR_COLS = ["MDSUPDRS_3-15-R", "MDSUPDRS_3-15-L", "MDSUPDRS_3-16-L", "MDSUPDRS_3-16-R", "MDSUPDRS_3-17-RUE", "MDSUPDRS_3-17-LUE", "MDSUPDRS_3-17-RLE", "MDSUPDRS_3-17-LLE", "MDSUPDRS_3-17-LipJaw"]

# 3. FUNZIONI DI SUPPORTO (FILE E PULIZIA DATI)
def find_file(candidates):
    for name in candidates:
        if os.path.exists(name): return name
    all_csv = glob.glob("**/*.csv", recursive=True)
    for name in candidates:
        key = name.lower().replace(".csv", "")
        for file in all_csv:
            if key in file.lower(): return file
    return None

def read_csv_with_column(file, required_column):
    for h in [0, 1, 2, 3]:
        try:
            df = pd.read_csv(file, header=h)
            df.columns = df.columns.astype(str).str.strip()
            if required_column in df.columns: return df
        except Exception:
            pass
    st.error(f"Could not find {required_column} in {file}")
    st.stop()

@st.cache_data
def load_data():
    pd_file = find_file(["PD.csv", "PD(1).csv", "PD - Demographic+Clinical - datasetV1.csv"])
    control_file = find_file(["CONTROLS.csv", "CONTROLS(1).csv", "CONTROLS - Demographic+Clinical - datasetV1.csv"])
    gait_file = find_file(["PKMAS Walkway Gait Metrics - HP+SP.csv"])
    
    if pd_file is None: st.error("PD file not found"); st.stop()
    if control_file is None: st.error("CONTROLS file not found"); st.stop()
    if gait_file is None: st.error("PKMAS gait file not found"); st.stop()
    
    df_pd = read_csv_with_column(pd_file, "Subject ID")
    df_control = read_csv_with_column(control_file, "Subject ID")
    df_gait = read_csv_with_column(gait_file, "Participant ID")
    return df_pd, df_control, df_gait, pd_file, control_file, gait_file

def clean_id(value):
    value = str(value).strip()
    match = re.search(r"[A-Za-z]+\d+", value)
    return match.group(0) if match else value

# 4. FUNZIONI DI CALCOLO CLINICO
def updrs_columns():
    part1 = [f"MDSUPDRS_1-{i}" for i in range(1, 14)]
    part2 = [f"MDSUPDRS_2-{i}" for i in range(1, 14)]
    part3 = ["MDSUPDRS_3-1", "MDSUPDRS_3-2", "MDSUPDRS_3-3-Neck", "MDSUPDRS_3-3-RUE", "MDSUPDRS_3-3-LUE", "MDSUPDRS_3-3-RLE", "MDSUPDRS_3-3-LLE", "MDSUPDRS_3-4-R", "MDSUPDRS_3-4-L", "MDSUPDRS_3-5-R", "MDSUPDRS_3-5-L", "MDSUPDRS_3-6-R", "MDSUPDRS_3-6-L", "MDSUPDRS_3-7-R", "MDSUPDRS_3-7-L", "MDSUPDRS_3-8-R", "MDSUPDRS_3-8-L", "MDSUPDRS_3-9", "MDSUPDRS_3-10", "MDSUPDRS_3-11", "MDSUPDRS_3-12", "MDSUPDRS_3-13", "MDSUPDRS_3-14", "MDSUPDRS_3-15-R", "MDSUPDRS_3-15-L", "MDSUPDRS_3-16-R", "MDSUPDRS_3-16-L", "MDSUPDRS_3-17-RUE", "MDSUPDRS_3-17-LUE", "MDSUPDRS_3-17-RLE", "MDSUPDRS_3-17-LLE", "MDSUPDRS_3-17-LipJaw", "MDSUPDRS_3-18"]
    part4 = [f"MDSUPDRS_4-{i}" for i in range(1, 7)]
    return part1 + part2 + part3 + part4

def score_from_columns(row, cols):
    vals = pd.to_numeric(pd.Series([row.get(c) for c in cols]), errors="coerce")
    if vals.notna().sum() == 0: return None
    return float(vals.sum(skipna=True))

def classifica_updrs(x):
    if pd.isna(x): return None
    if x <= 32: return "Mild (0-32)"
    if x <= 58: return "Moderate (33-58)"
    if x <= 102: return "Severe (59-102)"
    return "Critical (>103)"

# 5. PIPELINE DI PREPARAZIONE DEI DATI
def prepare_pd_data(df_pd):
    df_pd = df_pd.copy()
    if "Age (years)" in df_pd.columns: 
        df_pd = df_pd.rename(columns={"Age (years)": "Age"})
    df_pd["Subject ID"] = df_pd["Subject ID"].apply(clean_id)
    df_pd["UPDRS"] = df_pd.apply(lambda row: score_from_columns(row, updrs_columns()), axis=1)
    df_pd["TREMOR_SCORE"] = df_pd.apply(lambda row: score_from_columns(row, TREMOR_COLS), axis=1)
    df_pd["UPDRS"] = pd.to_numeric(df_pd["UPDRS"], errors="coerce")
    df_pd["TREMOR_SCORE"] = pd.to_numeric(df_pd["TREMOR_SCORE"], errors="coerce")
    df_pd = df_pd.dropna(subset=["UPDRS"]).copy()
    df_pd["UPDRS_CLASS"] = df_pd["UPDRS"].apply(classifica_updrs)
    df_pd["Age"] = pd.to_numeric(df_pd.get("Age"), errors="coerce")
    df_pd["Years since PD diagnosis"] = pd.to_numeric(df_pd.get("Years since PD diagnosis"), errors="coerce")
    return df_pd

def prepare_gait_data(df_gait):
    df_gait = df_gait.copy().dropna(subset=["Participant ID"])
    needed = ["Task", "Participant ID", "PD vs Control", "Velocity (cm./sec.)", "Cadence (steps/min.)", "Stride Length (cm.)", "FAP", "Mean eGVI"]
    missing = [c for c in needed if c not in df_gait.columns]
    if missing: st.error(f"Missing columns in the PKMAS file: {missing}"); st.stop()
    df_gait["Task"] = df_gait["Task"].astype(str).str.strip()
    df_gait["Participant ID"] = df_gait["Participant ID"].apply(clean_id)
    for col in ["Velocity (cm./sec.)", "Cadence (steps/min.)", "Stride Length (cm.)", "FAP", "Mean eGVI"]: 
        df_gait[col] = pd.to_numeric(df_gait[col], errors="coerce")
    df_gait = df_gait[df_gait["Task"].isin(["SelfPace", "HurriedPace"])].copy()
    df_gait = df_gait.groupby(["Participant ID", "PD vs Control"], as_index=False).agg(
        {"Velocity (cm./sec.)": "mean", "Cadence (steps/min.)": "mean", "Stride Length (cm.)": "mean", "FAP": "mean", "Mean eGVI": "mean"}
    )
    df_gait = df_gait.rename(columns={"Participant ID": "Subject ID", "Velocity (cm./sec.)": "Velocity", "Cadence (steps/min.)": "Cadence", "Stride Length (cm.)": "Stride Length"})
    return df_gait

# 6. FUNZIONI STATISTICHE E GRAFICI
def stat_table(series_dict):
    rows = []
    for name, s in series_dict.items():
        s = pd.to_numeric(s, errors="coerce").dropna()
        if len(s) == 0:
            rows.append({"Group": name, "N": 0, "Mean": None, "Median": None, "Mode": None, "Std Dev": None, "Min": None, "Max": None})
        else:
            mode = s.mode()
            rows.append({
                "Group": name, "N": int(len(s)), 
                "Mean": round(float(s.mean()), 2), "Median": round(float(s.median()), 2), 
                "Mode": round(float(mode.iloc[0]), 2) if not mode.empty else None, 
                "Std Dev": round(float(s.std()), 2), "Min": round(float(s.min()), 2), "Max": round(float(s.max()), 2)
            })
    return pd.DataFrame(rows).set_index("Group")

def run_ttest(s1, s2, label1, label2):
    s1 = pd.to_numeric(s1, errors="coerce").dropna()
    s2 = pd.to_numeric(s2, errors="coerce").dropna()
    if len(s1) < 2 or len(s2) < 2:
        st.warning("Not enough data to run the t-test.")
        return
    t_stat, p_val = ttest_ind(s1, s2, equal_var=False, nan_policy="omit")
    c1, c2, c3 = st.columns(3)
    c1.metric("T-statistic", round(float(t_stat), 4), help="T-statistic evaluates the size of the difference relative to the variation in your sample data.")
    c2.metric("P-value", round(float(p_val), 6), help="P-value measures the probability that the observed difference occurred by chance.")
    c3.metric("Significant (p < 0.05)", "✅ Yes" if p_val < 0.05 else "❌ No", help="Indicates if the statistical difference is robust at a 95% confidence level.")
    if p_val < 0.05: 
        st.success(f"Statistically significant difference between **{label1}** and **{label2}** (p = {round(float(p_val), 4)}).")
    else: 
        st.info(f"No statistically significant difference between **{label1}** and **{label2}** (p = {round(float(p_val), 4)}).")

def boxswarm(df_plot, x_col, y_col, color_map):
    fig = go.Figure()
    for group, color in color_map.items():
        sub = pd.to_numeric(df_plot[df_plot[x_col] == group][y_col], errors="coerce").dropna()
        if len(sub) == 0: continue
        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        fig.add_trace(go.Box(x=[group] * len(sub), y=sub, name=group, boxmean=True, line=dict(color=color), fillcolor=f"rgba({r},{g},{b},0.25)"))
        fig.add_trace(go.Scatter(x=[group] * len(sub), y=sub, mode="markers", marker=dict(size=6, color=color, opacity=0.7), showlegend=False))
    fig.update_layout(template="plotly_white", margin=dict(t=20, b=10), boxmode="overlay")
    return fig

# 7. CARICAMENTO DATI CORE
df_pd_raw, df_control_raw, df_gait_raw, pd_file, control_file, gait_file = load_data()
df_pd = df_pd_raw.copy()

# Numero totale iniziale di pazienti nel dataset grezzo
total_initial_patients = len(df_pd["Subject ID"].unique())

# 8. INTERFACCIA PRINCIPALE
st.title("Statistics and Data Analysis Panel")
st.caption("Descriptive statistics, t-test and p-value for clinical and motor variables in Parkinson's disease patients.")

# Creazione del menu Popover per i filtri dei sottogruppi nella pagina principale
with st.popover("🎛️ Open Subgroup Selection Filters", use_container_width=True):
    st.markdown("### Subgroup Analysis Configuration") 
    scelta_parametri = st.multiselect(
        "Parameters to apply:", ["Gender", "Age"],
        help="Select the demographic features you want to use to narrow down the current patient cohort."
    )
    
    soggetti_selezionati_genere = []
    soggetti_selezionati_eta = []
    
    # Filtro Genere
    if "Gender" in scelta_parametri:
        st.markdown("**Gender**")
        selezione_genere = st.selectbox("Choose gender:", ["Male", "Female"])
        for i, row in df_pd.iterrows():
            if str(row.get("Gender")).strip() == selezione_genere:
                soggetti_selezionati_genere.append({"Subject ID": row["Subject ID"], "Gender": row["Gender"]})
    else:
        for i, row in df_pd.iterrows():
            soggetti_selezionati_genere.append({"Subject ID": row["Subject ID"], "Gender": row.get("Gender")})

    # Filtro Età
    if "Age" in scelta_parametri:
        st.markdown("**Age**")
        selezione_eta = st.selectbox("Mode:", ["Age range", "Specific age"])
        eta_col = "Age (years)" if "Age (years)" in df_pd.columns else "Age"
        
        if selezione_eta == "Age range":
            age_min, age_max = st.slider("Select range", 0, 110, (40, 80))
            for i, row in df_pd.iterrows():
                for element in soggetti_selezionati_genere:
                    if pd.to_numeric(row.get(eta_col), errors='coerce') <= age_max and pd.to_numeric(row.get(eta_col), errors='coerce') >= age_min:
                        if element["Subject ID"] == row["Subject ID"]:
                            soggetti_selezionati_eta.append({"Subject ID": element["Subject ID"], "Gender": element["Gender"], "Age": row.get(eta_col)})
        
        if selezione_eta == "Specific age":
            age = st.number_input("Specific age", 0, 110, 60, 1)
            for i, row in df_pd.iterrows():
                for element in soggetti_selezionati_genere:
                    if pd.to_numeric(row.get(eta_col), errors='coerce') == age and element["Subject ID"] == row["Subject ID"]:
                        soggetti_selezionati_eta.append({"Subject ID": element["Subject ID"], "Gender": element["Gender"], "Age": row.get(eta_col)})
    else:
        eta_col = "Age (years)" if "Age (years)" in df_pd.columns else "Age"
        for i, row in df_pd.iterrows():
            for element in soggetti_selezionati_genere:
                if row["Subject ID"] == element["Subject ID"]:
                    soggetti_selezionati_eta.append({"Subject ID": element["Subject ID"], "Gender": element["Gender"], "Age": row.get(eta_col)})
    
    st.success("Filters saved. Close the panel by clicking outside to update the charts.")

# Generazione del dataframe filtrato dinamico
if soggetti_selezionati_eta:
    df_soggetti_filtrati = pd.DataFrame(soggetti_selezionati_eta)
    id_pazienti_filtrati = df_soggetti_filtrati["Subject ID"].apply(clean_id).unique()
    df_pd_clean_id = df_pd.copy()
    df_pd_clean_id["Subject ID_Clean"] = df_pd_clean_id["Subject ID"].apply(clean_id)
    df_pd_filtered = df_pd_clean_id[df_pd_clean_id["Subject ID_Clean"].isin(id_pazienti_filtrati)].copy()
    df_pd_filtered = df_pd_filtered.drop(columns=["Subject ID_Clean"])
else:
    df_pd_filtered = df_pd.copy()

# Esecuzione della pipeline statistica sul sottogruppo filtrato
df_pd_prepared = prepare_pd_data(df_pd_filtered)
df_gait_prepared = prepare_gait_data(df_gait_raw)
df_pd_merged = pd.merge(df_pd_prepared, df_gait_prepared, on="Subject ID", how="left")
df_mobility = df_pd_merged.dropna(subset=["Velocity", "UPDRS"]).copy()

if len(df_mobility) == 0:
    st.error("❌ No patients matched the selected filters. Please expand your criteria inside the popover menu.")
    st.stop()

# Ricalcolo dinamico della mobilità sul sottogruppo selezionato
velocity_median = df_mobility["Velocity"].median()
df_mobility["MOBILITY_CLASS"] = df_mobility["Velocity"].apply(lambda x: "High mobility (higher velocity)" if x >= velocity_median else "Low mobility (lower velocity)")
df_pd_merged = pd.merge(df_pd_merged.drop(columns=["MOBILITY_CLASS"], errors="ignore"), df_mobility[["Subject ID", "MOBILITY_CLASS"]], on="Subject ID", how="left")

# KPI generali del sottogruppo
with st.expander("Current file and dataset details"):
    st.write(f"PD clinical file: `{pd_file}` | PKMAS file: `{gait_file}`")
    st.write(f"Total filtered patients: **{len(df_pd_prepared)}** | With Gait metrics: **{len(df_mobility)}**")
    st.write(f"Group calculated median velocity: **{round(float(velocity_median), 2)} cm/sec**")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Filtered Patients", len(df_pd_prepared), help="Total number of patients satisfying the demographic filter criteria.")
m2.metric("Included in Mobility", len(df_mobility), help="Patients from the filtered subgroup who also have active, non-null PKMAS walkway velocity values.")
m3.metric("Subgroup Mean UPDRS", round(float(df_pd_prepared["UPDRS"].mean()), 2), help="Average MDS-UPDRS overall clinical total calculated for this specific cohort.")
m4.metric("Subgroup Mean Tremor", round(float(df_pd_prepared["TREMOR_SCORE"].mean()), 2), help="Average score extracted solely from the designated tremor item subset columns.")

# --- VERIFICA DELLA DIMENSIONE DEL CAMPIONE NEL CAPTION TRAMITE L'HELP DELL'API ---
if len(df_mobility) < 15:
    st.caption(
        f"⚠️ *Current sample size under review is small ({len(df_mobility)} subjects).* "
        f"The analysis will still be processed below.",
        help=f"Warning: The current subset under review is quite limited compared to the total patient population ({total_initial_patients}). Because the sample size is under 15 subjects, statistical power is significantly compromised, and results, variances, or t-test p-values may not be completely accurate or mathematically precise."
    )
else:
    st.caption(f"📊 Sample size is statistically sufficient ({len(df_mobility)} subjects matching active gait criteria).")

st.divider()

# STRUTTURA DEI TAB DEL MOTORE STATISTICO
tab1, tab2, tab3, tab4 = st.tabs(["🚶 Mobility × UPDRS", "🏃 High vs Low mobility", "⏱ Severity × Diagnosis", "🤝 Tremors"])

# TAB 1
with tab1:
    st.subheader("Mobility in relation to UPDRS")
    df_t1 = df_mobility.dropna(subset=["Velocity", "UPDRS", "UPDRS_CLASS"]).copy()
    groups = [g for g in UPDRS_ORDER if g in df_t1["UPDRS_CLASS"].unique()]
    st.markdown("##### Descriptive statistics — velocity by UPDRS class")
    st.dataframe(stat_table({g: df_t1[df_t1["UPDRS_CLASS"] == g]["Velocity"] for g in groups}), use_container_width=True)
    col_a, col_b = st.columns(2)
    with col_a:
        fig_box = boxswarm(df_t1, "UPDRS_CLASS", "Velocity", COLOR_UPDRS)
        st.plotly_chart(fig_box, use_container_width=True)
    with col_b:
        fig_scatter = px.scatter(df_t1, x="UPDRS", y="Velocity", color="UPDRS_CLASS", color_discrete_map=COLOR_UPDRS, hover_data=["Subject ID", "Age"])
        st.plotly_chart(fig_scatter, use_container_width=True)
    st.divider()
    run_ttest(df_t1[df_t1["UPDRS_CLASS"] == "Mild (0-32)"]["Velocity"], df_t1[df_t1["UPDRS_CLASS"] == "Severe (59-102)"]["Velocity"], "Mild", "Severe")

# TAB 2
with tab2:
    st.subheader("Mobility between high and low patients")
    df_t2 = df_mobility.dropna(subset=["Velocity", "MOBILITY_CLASS", "UPDRS"]).copy()
    st.markdown("##### Descriptive statistics — velocity by mobility class")
    st.dataframe(stat_table({g: df_t2[df_t2["MOBILITY_CLASS"] == g]["Velocity"] for g in COLOR_MOBILITY}), use_container_width=True)
    col_a, col_b = st.columns(2)
    with col_a:
        fig_mob = boxswarm(df_t2, "MOBILITY_CLASS", "Velocity", COLOR_MOBILITY)
        st.plotly_chart(fig_mob, use_container_width=True)
    with col_b:
        fig_updrs_mob = boxswarm(df_t2, "MOBILITY_CLASS", "UPDRS", COLOR_MOBILITY)
        st.plotly_chart(fig_updrs_mob, use_container_width=True)
    st.divider()
    run_ttest(df_t2[df_t2["MOBILITY_CLASS"] == "High mobility (higher velocity)"]["UPDRS"], df_t2[df_t2["MOBILITY_CLASS"] == "Low mobility (lower velocity)"]["UPDRS"], "High mobility", "Low mobility")

# TAB 3
with tab3:
    st.subheader("Disease severity in relation to diagnosis duration")
    df_t3 = df_pd_merged.dropna(subset=["Years since PD diagnosis", "UPDRS", "UPDRS_CLASS"]).copy()
    if len(df_t3) == 0:
        st.warning("No valid values found for Years since PD diagnosis in this subgroup.")
    else:
        st.dataframe(stat_table({g: df_t3[df_t3["UPDRS_CLASS"] == g]["Years since PD diagnosis"] for g in UPDRS_ORDER if g in df_t3["UPDRS_CLASS"].unique()}), use_container_width=True)
        col_a, col_b = st.columns(2)
        with col_a:
            fig_diag = boxswarm(df_t3, "UPDRS_CLASS", "Years since PD diagnosis", COLOR_UPDRS)
            st.plotly_chart(fig_diag, use_container_width=True)
        with col_b:
            fig_scatter = px.scatter(df_t3, x="Years since PD diagnosis", y="UPDRS", color="UPDRS_CLASS", color_discrete_map=COLOR_UPDRS)
            st.plotly_chart(fig_scatter, use_container_width=True)
        st.divider()
        limit_years = st.slider("Choose threshold for disease duration groups (years)", 1, 20, 5, help="Splits patients into short vs. long disease exposure groups for comparative analysis.")
        run_ttest(df_t3[df_t3["Years since PD diagnosis"] < limit_years]["UPDRS"], df_t3[df_t3["Years since PD diagnosis"] >= limit_years]["UPDRS"], f"< {limit_years} years", f"≥ {limit_years} years")

# TAB 4
with tab4:
    st.subheader("Tremor analysis")
    df_t4 = df_pd_merged.dropna(subset=["TREMOR_SCORE", "UPDRS", "UPDRS_CLASS"]).copy()
    st.markdown("##### Descriptive statistics — tremor score by UPDRS class")
    st.dataframe(stat_table({g: df_t4[df_t4["UPDRS_CLASS"] == g]["TREMOR_SCORE"] for g in UPDRS_ORDER if g in df_t4["UPDRS_CLASS"].unique()}), use_container_width=True)
    col_a, col_b = st.columns(2)
    with col_a:
        fig_tremor = boxswarm(df_t4, "UPDRS_CLASS", "TREMOR_SCORE", COLOR_UPDRS)
        st.plotly_chart(fig_tremor, use_container_width=True)
    with col_b:
        fig_tremor_scatter = px.scatter(df_t4, x="UPDRS", y="TREMOR_SCORE", color="UPDRS_CLASS", color_discrete_map=COLOR_UPDRS)
        st.plotly_chart(fig_tremor_scatter, use_container_width=True)
    
    st.divider()
    col_c, col_d = st.columns(2)
    with col_c:
        df_t4_mob = df_t4.dropna(subset=["MOBILITY_CLASS"]).copy()
        fig_mob_tremor = boxswarm(df_t4_mob, "MOBILITY_CLASS", "TREMOR_SCORE", COLOR_MOBILITY)
        st.plotly_chart(fig_mob_tremor, use_container_width=True)
    with col_d:
        tr_means = {}
        for col in TREMOR_COLS:
            if col in df_t4.columns:
                vals = pd.to_numeric(df_t4[col], errors="coerce").dropna()
                if not vals.empty: tr_means[col.replace("MDSUPDRS_", "")] = round(float(vals.mean()), 3)
        if tr_means:
            fig_items = px.bar(x=list(tr_means.keys()), y=list(tr_means.values()), text=list(tr_means.values()))
            st.plotly_chart(fig_items, use_container_width=True)
    st.divider()
    df_t4_mob = df_t4.dropna(subset=["MOBILITY_CLASS"]).copy()
    run_ttest(df_t4_mob[df_t4_mob["MOBILITY_CLASS"] == "High mobility (higher velocity)"]["TREMOR_SCORE"], df_t4_mob[df_t4_mob["MOBILITY_CLASS"] == "Low mobility (lower velocity)"]["TREMOR_SCORE"], "High mobility", "Low mobility")