import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="PDAI - Dati Demografici", page_icon="🧠", layout="wide")

# LOGIN CHECK
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("⚠️ Please log in from the Homepage.")
    st.stop()

# Sidebar
st.sidebar.title("🧠 PDAI")
st.sidebar.markdown("**Parkinsonian Data Analysis Interface**")
st.sidebar.divider()

# Dati
df_control = pd.read_csv("CONTROLS.csv", sep="," , header=1)
df_pd = pd.read_csv("PD.csv", sep="," , header=1)
df_pd = df_pd.rename(columns = {"Age (years)" : "Age"}) #rinomino le colonne dei due file per poterle prendere insieme

df_pd["GRUPPO"] = "PD"
df_control["GRUPPO"] = "CONTROL"

df = pd.concat([df_pd, df_control], ignore_index = True)

# Titolo
st.title("👤 Dati Demografici")
st.caption("Panoramica generale delle informazioni demografiche dei pazienti.")
st.divider()

# Selezione gruppo
st.sidebar.subheader("📂 Dataset")
scelta_gruppo = st.sidebar.radio(
    "Mostra i dati per:",
    options=["PD", "Control", "Tutti"],
    index=0
)

if scelta_gruppo == "PD":
    df = df_pd.copy()
elif scelta_gruppo == "Control":
    df = df_control.copy()
else:
    df = df.copy()

# FILTERS
st.sidebar.divider()
st.sidebar.subheader("🔍 Filtri")

#INSERIRE I FILTRI

# MAPPA COLORE
color_map = {"Male": "#4A90D9", "Female": "#E8729A"}

# Valori barra
#st.subheader("📋 Summary")
#col1, col2, col3 = st.columns(3)
#col1.metric("Pazienti", len(df))
#col2.metric("Età media", f"{df['Age'].mean():.1f} yrs")
#col3.metric("Maschi / Femmine", f"{(df['Gender']=='Maschi').sum()} / {(df['Gender']=='Femmine').sum()}")

st.divider()

# PRIMA RIGA
col1, col2 = st.columns(2)

with col1:
    st.subheader("Distribuzione per genere")

    df_male = df[df["Gender"] == "Male"]
    df_female = df[df["Gender"] == "Female"]

    df_gender = pd.concat([df_male, df_female], ignore_index = True)

    fig_gender = px.pie(df_gender, names="Gender", color="Gender", color_discrete_map=color_map, hole=0.4 )
    fig_gender.update_layout(margin=dict(t=10, b=10))
    st.plotly_chart(fig_gender, use_container_width=True)

with col2:
    st.subheader("Distribuzione dell'età")

    df_male = df[df["Gender"] == "Male"]
    df_female = df[df["Gender"] == "Female"]

    df_age = pd.concat([df_male, df_female], ignore_index = True)

    fig_age = px.histogram(df_age, x="Age", color="Gender", barmode="group", color_discrete_map=color_map, nbins=15)
    fig_age.update_layout(margin=dict(t=10, b=10))
    st.plotly_chart(fig_age, use_container_width=True)

# SECONDA RIGA
col3, col4 = st.columns(2)

with col3:
    st.subheader("Distribuzione per etnia")

    df_white = df[df["Race"] == "White"]
    df_asian = df[df["Race"] == "Asian"]
    df_black = df[df["Race"] == "Black/African American"]

    df_race = pd.concat([df_white, df_asian, df_black], ignore_index = True)

    race_counts = pd.DataFrame({
        "Race" : ["White", "Asian", "Black/African American"],
        "Count" : [len(df_white), len(df_asian), len(df_black)]})

    fig_race = px.bar(race_counts, x="Count", y="Race", orientation="h", color="Race", color_discrete_sequence=px.colors.qualitative.Safe)
    fig_race.update_layout(margin=dict(t=10, b=10), showlegend=False)
    st.plotly_chart(fig_race, use_container_width=True)

with col4:
    st.subheader("Boxplot e swarm plot")

    df_male = df[df["Gender"] == "Male"]
    df_female = df[df["Gender"] == "Female"]

    df_box = pd.concat([df_male, df_female], ignore_index = True)

    if scelta_gruppo == "PD":
        x_col = "Gender"
        y_col = "Years since PD diagnosis"
        color_col = "Gender"
        title = "Anni dalla diagnosi di PD per genere"
    else:
        x_col = "Gender" 
        y_col = "Age"
        title = "Distribuzione dell'età per gruppo"

    fig_box_swarm = go.Figure()

    # MALE BOX
    fig_box_swarm.add_trace(go.Box(
        x=["Male"] * len(df_male),
        y=df_male[y_col],
        name="Male",
        boxmean=True,
        line=dict(color="#4A90D9"),
        fillcolor="rgba(74,144,217,0.3)"
    ))

    # MALE SWARM
    fig_box_swarm.add_trace(go.Scatter(
        x=["Male"] * len(df_male),
        y=df_male[y_col],
        mode="markers",
        marker=dict(
            size=7,
            color="#1f5fbf",
            opacity=0.8
        ),
        showlegend=False
    ))

    # FEMALE BOX
    fig_box_swarm.add_trace(go.Box(
        x=["Female"] * len(df_female),
        y=df_female[y_col],
        name="Female",
        boxmean=True,
        line=dict(color="#E8729A"),
        fillcolor="rgba(232,114,154,0.3)"
    ))

    # FEMALE SWARM
    fig_box_swarm.add_trace(go.Scatter(
        x=["Female"] * len(df_female),
        y=df_female[y_col],
        mode="markers",
        marker=dict(
            size=7,
            color="#c2185b",
            opacity=0.8
        ),
        showlegend=False
    ))

    fig_box_swarm.update_layout(
        title=title,
        margin=dict(t=30, b=10),
        boxmode="overlay"
    )

    st.plotly_chart(fig_box_swarm, use_container_width=True)
st.divider()

# TABELLA NASCOSTA
#cols_to_show = ["Subject ID", "Age", "Gender", "Race", "Height (in)", "Weight (kg)"]

# if scelta_gruppo == "PD Patients":
#     cols_to_show.append("Years since PD diagnosis")

# if scelta_gruppo == "All":
#     cols_to_show.append("Group")

# with st.expander("📄 Visualizza dati filtrati"):
#     st.dataframe(
#         df[cols_to_show].reset_index(drop=True),
#         use_container_width=True
#     )