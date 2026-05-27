import os
import glob
import re
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import ttest_ind

st.set_page_config(page_title="Statistical Analysis", page_icon="📊", layout="wide")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("⚠️ Please log in from the Homepage.")
    st.stop()

st.title("Statistics")
st.caption("Descriptive statistics, t-test and p-value for clinical and motor variables in Parkinson's disease patients.")
st.divider()

# File search
def find_file(candidates):
    for name in candidates:
        if os.path.exists(name): return name
    all_csv = glob.glob("*.csv")
    for name in candidates:
        key = name.lower().replace(".csv", "")
        for file in all_csv:
            if key in file.lower(): return file
    return None

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

# Clinical scores
def get_num(row, col): return pd.to_numeric(row.get(col), errors="coerce")

def clean_id(value):
    value = str(value).strip()
    match = re.search(r"[A-Za-z]+\d+", value)
    return match.group(0) if match else value

def updrs_columns():
    part1 = [f"MDSUPDRS_1-{i}" for i in range(1, 14)]
    part2 = [f"MDSUPDRS_2-{i}" for i in range(1, 14)]
    part3 = ["MDSUPDRS_3-1", "MDSUPDRS_3-2", "MDSUPDRS_3-3-Neck", "MDSUPDRS_3-3-RUE", "MDSUPDRS_3-3-LUE", "MDSUPDRS_3-3-RLE", "MDSUPDRS_3-3-LLE", "MDSUPDRS_3-4-R", "MDSUPDRS_3-4-L", "MDSUPDRS_3-5-R", "MDSUPDRS_3-5-L", "MDSUPDRS_3-6-R", "MDSUPDRS_3-6-L", "MDSUPDRS_3-7-R", "MDSUPDRS_3-7-L", "MDSUPDRS_3-8-R", "MDSUPDRS_3-8-L", "MDSUPDRS_3-9", "MDSUPDRS_3-10", "MDSUPDRS_3-11", "MDSUPDRS_3-12", "MDSUPDRS_3-13", "MDSUPDRS_3-14", "MDSUPDRS_3-15-R", "MDSUPDRS_3-15-L", "MDSUPDRS_3-16-R", "MDSUPDRS_3-16-L", "MDSUPDRS_3-17-RUE", "MDSUPDRS_3-17-LUE", "MDSUPDRS_3-17-RLE", "MDSUPDRS_3-17-LLE", "MDSUPDRS_3-17-LipJaw", "MDSUPDRS_3-18"]
    part4 = [f"MDSUPDRS_4-{i}" for i in range(1, 7)]
    return part1 + part2 + part3 + part4

TREMOR_COLS = ["MDSUPDRS_3-15-R", "MDSUPDRS_3-15-L", "MDSUPDRS_3-16-L", "MDSUPDRS_3-16-R", "MDSUPDRS_3-17-RUE", "MDSUPDRS_3-17-LUE", "MDSUPDRS_3-17-RLE", "MDSUPDRS_3-17-LLE", "MDSUPDRS_3-17-LipJaw"]

def score_from_columns(row, cols):
    vals = pd.to_numeric(pd.Series([row.get(c) for c in cols]), errors="coerce")
    if vals.notna().sum() == 0: return None
    return float(vals.sum(skipna=True))

def classifica_updrs(x):
    if x <= 32: return "Mild (0-32)"
    if x <= 58: return "Moderate (33-58)"
    if x <= 102: return "Severe (59-102)"
    return "Critical (>103)"

# Tables and tests
def stat_table(series_dict):
    rows = []
    for name, s in series_dict.items():
        s = pd.to_numeric(s, errors="coerce").dropna()
        if len(s) == 0:
            rows.append({"Group": name, "N": 0, "Mean": None, "Median": None, "Mode": None, "Std Dev": None, "Min": None, "Max": None})
        else:
            mode = s.mode()
            rows.append({"Group": name, "N": int(len(s)), "Mean": round(float(s.mean()), 2), "Median": round(float(s.median()), 2), "Mode": round(float(mode.iloc[0]), 2) if not mode.empty else None, "Std Dev": round(float(s.std()), 2), "Min": round(float(s.min()), 2), "Max": round(float(s.max()), 2)})
    return pd.DataFrame(rows).set_index("Group")

def run_ttest(s1, s2, label1, label2):
    s1 = pd.to_numeric(s1, errors="coerce").dropna()
    s2 = pd.to_numeric(s2, errors="coerce").dropna()
    if len(s1) < 2 or len(s2) < 2:
        st.warning("Not enough data to run the t-test.")
        return
    t_stat, p_val = ttest_ind(s1, s2, equal_var=False, nan_policy="omit")
    c1, c2, c3 = st.columns(3)
    c1.metric("T-statistic", round(float(t_stat), 4))
    c2.metric("P-value", round(float(p_val), 6))
    c3.metric("Significant (p < 0.05)", "✅ Yes" if p_val < 0.05 else "❌ No")
    if p_val < 0.05: st.success(f"Statistically significant difference between **{label1}** and **{label2}** (p = {round(float(p_val), 4)}).")
    else: st.info(f"No statistically significant difference between **{label1}** and **{label2}** (p = {round(float(p_val), 4)}).")

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

# Data cleaning
def prepare_pd_data(df_pd):
    df_pd = df_pd.copy()
    if "Age (years)" in df_pd.columns: df_pd = df_pd.rename(columns={"Age (years)": "Age"})
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
    for col in ["Velocity (cm./sec.)", "Cadence (steps/min.)", "Stride Length (cm.)", "FAP", "Mean eGVI"]: df_gait[col] = pd.to_numeric(df_gait[col], errors="coerce")
    df_gait = df_gait[df_gait["Task"].isin(["SelfPace", "HurriedPace"])].copy()
    df_gait = df_gait.groupby(["Participant ID", "PD vs Control"], as_index=False).agg({"Velocity (cm./sec.)": "mean", "Cadence (steps/min.)": "mean", "Stride Length (cm.)": "mean", "FAP": "mean", "Mean eGVI": "mean"})
    df_gait = df_gait.rename(columns={"Participant ID": "Subject ID", "Velocity (cm./sec.)": "Velocity", "Cadence (steps/min.)": "Cadence", "Stride Length (cm.)": "Stride Length"})
    return df_gait

# Main data
df_pd_raw, df_control_raw, df_gait_raw, pd_file, control_file, gait_file = load_data()
df_pd = prepare_pd_data(df_pd_raw)
df_gait = prepare_gait_data(df_gait_raw)
df_pd_merged = pd.merge(df_pd, df_gait, on="Subject ID", how="left")
df_mobility = df_pd_merged.dropna(subset=["Velocity", "UPDRS"]).copy()

if len(df_mobility) == 0:
    st.error("No PD patients could be matched with PKMAS gait metrics. Check Subject ID / Participant ID.")
    st.stop()

velocity_median = df_mobility["Velocity"].median()
df_mobility["MOBILITY_CLASS"] = df_mobility["Velocity"].apply(lambda x: "High mobility (higher velocity)" if x >= velocity_median else "Low mobility (lower velocity)")
df_pd_merged = pd.merge(df_pd_merged.drop(columns=["MOBILITY_CLASS"], errors="ignore"), df_mobility[["Subject ID", "MOBILITY_CLASS"]], on="Subject ID", how="left")

UPDRS_ORDER = ["Mild (0-32)", "Moderate (33-58)", "Severe (59-102)", "Critical (>103)"]
COLOR_UPDRS = {"Mild (0-32)": "#378ADD", "Moderate (33-58)": "#EF9F27", "Severe (59-102)": "#E24B4A", "Critical (>103)": "#7F77DD"}
COLOR_MOBILITY = {"High mobility (higher velocity)": "#5DCAA5", "Low mobility (lower velocity)": "#E24B4A"}
COLOR_GENDER = {"Male": "#4A90D9", "Female": "#E8729A"}

with st.expander("Loaded files"):
    st.write(f"PD clinical file: `{pd_file}`")
    st.write(f"Control clinical file: `{control_file}`")
    st.write(f"PKMAS gait metrics file: `{gait_file}`")
    st.write(f"PD patients: **{len(df_pd)}**")
    st.write(f"PD patients with gait metrics: **{len(df_mobility)}**")

col1, col2, col3, col4 = st.columns(4)
col1.metric("PD patients", len(df_pd))
col2.metric("PD with gait metrics", len(df_mobility))
col3.metric("Mean UPDRS", round(float(df_pd["UPDRS"].mean()), 2))
col4.metric("Mean tremor score", round(float(df_pd["TREMOR_SCORE"].mean()), 2))

st.divider()
tab1, tab2, tab3, tab4 = st.tabs(["🚶 Mobility × UPDRS", "🏃 High vs Low mobility", "⏱ Severity × Diagnosis", "🤝 Tremors"])

# TAB 1
with tab1:
    st.subheader("Mobility in relation to UPDRS")
    st.write("Mobility is represented by **Velocity (cm/sec)** from PKMAS walkway-derived metrics.")
    df_t1 = df_mobility.dropna(subset=["Velocity", "UPDRS", "UPDRS_CLASS"]).copy()
    groups = [g for g in UPDRS_ORDER if g in df_t1["UPDRS_CLASS"].unique()]
    st.markdown("##### Descriptive statistics — velocity by UPDRS class")
    st.dataframe(stat_table({g: df_t1[df_t1["UPDRS_CLASS"] == g]["Velocity"] for g in groups}), use_container_width=True)
    st.divider()
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("##### Velocity distribution by UPDRS class")
        fig_box = boxswarm(df_t1, "UPDRS_CLASS", "Velocity", COLOR_UPDRS)
        fig_box.update_layout(yaxis_title="Velocity (cm/sec)", xaxis_title="UPDRS class")
        st.plotly_chart(fig_box, use_container_width=True)
    with col_b:
        st.markdown("##### UPDRS vs velocity")
        fig_scatter = px.scatter(df_t1, x="UPDRS", y="Velocity", color="UPDRS_CLASS", color_discrete_map=COLOR_UPDRS, labels={"UPDRS": "UPDRS score", "Velocity": "Velocity (cm/sec)"}, hover_data=["Subject ID", "Age", "Gender"])
        fig_scatter.update_layout(template="plotly_white", margin=dict(t=10, b=10))
        st.plotly_chart(fig_scatter, use_container_width=True)
    st.divider()
    st.markdown("##### T-test and p-value — velocity: Mild vs Severe UPDRS")
    run_ttest(df_t1[df_t1["UPDRS_CLASS"] == "Mild (0-32)"]["Velocity"], df_t1[df_t1["UPDRS_CLASS"] == "Severe (59-102)"]["Velocity"], "Mild", "Severe")

# TAB 2
with tab2:
    st.subheader("Mobility between high and low patients")
    st.write(f"Patients are divided according to the median velocity value ({round(float(velocity_median), 2)} cm/sec).")
    df_t2 = df_mobility.dropna(subset=["Velocity", "MOBILITY_CLASS", "UPDRS"]).copy()
    st.markdown("##### Descriptive statistics — velocity by mobility class")
    st.dataframe(stat_table({g: df_t2[df_t2["MOBILITY_CLASS"] == g]["Velocity"] for g in COLOR_MOBILITY}), use_container_width=True)
    st.divider()
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("##### Velocity distribution by mobility class")
        fig_mob = boxswarm(df_t2, "MOBILITY_CLASS", "Velocity", COLOR_MOBILITY)
        fig_mob.update_layout(yaxis_title="Velocity (cm/sec)", xaxis_title="Mobility class")
        st.plotly_chart(fig_mob, use_container_width=True)
    with col_b:
        st.markdown("##### UPDRS distribution by mobility class")
        fig_updrs_mob = boxswarm(df_t2, "MOBILITY_CLASS", "UPDRS", COLOR_MOBILITY)
        fig_updrs_mob.update_layout(yaxis_title="UPDRS score", xaxis_title="Mobility class")
        st.plotly_chart(fig_updrs_mob, use_container_width=True)
    st.divider()
    st.markdown("##### T-test and p-value — UPDRS: High mobility vs Low mobility")
    run_ttest(df_t2[df_t2["MOBILITY_CLASS"] == "High mobility (higher velocity)"]["UPDRS"], df_t2[df_t2["MOBILITY_CLASS"] == "Low mobility (lower velocity)"]["UPDRS"], "High mobility", "Low mobility")

# TAB 3
with tab3:
    st.subheader("Disease severity in relation to diagnosis duration")
    df_t3 = df_pd_merged.dropna(subset=["Years since PD diagnosis", "UPDRS", "UPDRS_CLASS"]).copy()
    if len(df_t3) == 0:
        st.warning("No valid values were found for Years since PD diagnosis.")
    else:
        st.markdown("##### Descriptive statistics — years since diagnosis by UPDRS class")
        st.dataframe(stat_table({g: df_t3[df_t3["UPDRS_CLASS"] == g]["Years since PD diagnosis"] for g in UPDRS_ORDER if g in df_t3["UPDRS_CLASS"].unique()}), use_container_width=True)
        st.divider()
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("##### Years since diagnosis by UPDRS class")
            fig_diag = boxswarm(df_t3, "UPDRS_CLASS", "Years since PD diagnosis", COLOR_UPDRS)
            fig_diag.update_layout(yaxis_title="Years since PD diagnosis", xaxis_title="UPDRS class")
            st.plotly_chart(fig_diag, use_container_width=True)
        with col_b:
            st.markdown("##### UPDRS vs years since diagnosis")
            fig_scatter = px.scatter(df_t3, x="Years since PD diagnosis", y="UPDRS", color="UPDRS_CLASS", color_discrete_map=COLOR_UPDRS, labels={"Years since PD diagnosis": "Years since diagnosis", "UPDRS": "UPDRS score"}, hover_data=["Subject ID", "Age", "Gender"])
            fig_scatter.update_layout(template="plotly_white", margin=dict(t=10, b=10))
            st.plotly_chart(fig_scatter, use_container_width=True)
        st.divider()
        st.markdown("##### T-test and p-value — UPDRS: Short vs Long disease duration")
        limit_years = st.slider("Choose threshold for disease duration groups (years)", 1, 20, 5)
        run_ttest(df_t3[df_t3["Years since PD diagnosis"] < limit_years]["UPDRS"], df_t3[df_t3["Years since PD diagnosis"] >= limit_years]["UPDRS"], f"< {limit_years} years", f"≥ {limit_years} years")

# TAB 4
with tab4:
    st.subheader("Tremor analysis")
    st.write("Tremor score is calculated as the sum of MDS-UPDRS Part III tremor items 3-15, 3-16 and 3-17.")
    df_t4 = df_pd_merged.dropna(subset=["TREMOR_SCORE", "UPDRS", "UPDRS_CLASS"]).copy()
    st.markdown("##### Descriptive statistics — tremor score by UPDRS class")
    st.dataframe(stat_table({g: df_t4[df_t4["UPDRS_CLASS"] == g]["TREMOR_SCORE"] for g in UPDRS_ORDER if g in df_t4["UPDRS_CLASS"].unique()}), use_container_width=True)
    st.divider()
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("##### Tremor score distribution by UPDRS class")
        fig_tremor = boxswarm(df_t4, "UPDRS_CLASS", "TREMOR_SCORE", COLOR_UPDRS)
        fig_tremor.update_layout(yaxis_title="Tremor score", xaxis_title="UPDRS class")
        st.plotly_chart(fig_tremor, use_container_width=True)
    with col_b:
        st.markdown("##### Tremor score vs UPDRS")
        fig_tremor_scatter = px.scatter(df_t4, x="UPDRS", y="TREMOR_SCORE", color="UPDRS_CLASS", color_discrete_map=COLOR_UPDRS, labels={"UPDRS": "UPDRS score", "TREMOR_SCORE": "Tremor score"}, hover_data=["Subject ID", "Age", "Gender"])
        fig_tremor_scatter.update_layout(template="plotly_white", margin=dict(t=10, b=10))
        st.plotly_chart(fig_tremor_scatter, use_container_width=True)
    st.divider()
    col_c, col_d = st.columns(2)
    with col_c:
        st.markdown("##### Tremor score by mobility class")
        df_t4_mob = df_t4.dropna(subset=["MOBILITY_CLASS"]).copy()
        fig_mob_tremor = boxswarm(df_t4_mob, "MOBILITY_CLASS", "TREMOR_SCORE", COLOR_MOBILITY)
        fig_mob_tremor.update_layout(yaxis_title="Tremor score", xaxis_title="Mobility class")
        st.plotly_chart(fig_mob_tremor, use_container_width=True)
    with col_d:
        st.markdown("##### Mean score of individual tremor items")
        tr_means = {}
        for col in TREMOR_COLS:
            if col in df_t4.columns:
                vals = pd.to_numeric(df_t4[col], errors="coerce").dropna()
                if not vals.empty: tr_means[col.replace("MDSUPDRS_", "")] = round(float(vals.mean()), 3)
        if tr_means:
            fig_items = px.bar(x=list(tr_means.keys()), y=list(tr_means.values()), labels={"x": "UPDRS item", "y": "Mean score"}, text=list(tr_means.values()))
            fig_items.update_layout(template="plotly_white", margin=dict(t=10, b=10))
            st.plotly_chart(fig_items, use_container_width=True)
        else:
            st.warning("No tremor item columns were found.")
    st.divider()
    st.markdown("##### T-test and p-value — Tremor score: High mobility vs Low mobility")
    df_t4_mob = df_t4.dropna(subset=["MOBILITY_CLASS"]).copy()
    run_ttest(df_t4_mob[df_t4_mob["MOBILITY_CLASS"] == "High mobility (higher velocity)"]["TREMOR_SCORE"], df_t4_mob[df_t4_mob["MOBILITY_CLASS"] == "Low mobility (lower velocity)"]["TREMOR_SCORE"], "High mobility", "Low mobility")
