import streamlit as st
import synapseclient
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="PDAI",
    page_icon="🧠",
    layout="wide"
)

#LOGIN
def token(nome):
    file_token=pd.read_csv("TOKEN.csv")
    for i,row in file_token.iterrows():
        if row["Name"]==nome.lower():
            token_finale=row["Token"]
            st.success("Access granted.")
            return token_finale,True
    token_finale="No token found, try again."
    return token_finale,False
        
def login(): 
    st.title("Access")
    codice_persona=st.text_input("Enter your user ID", placeholder="es: Francesca")
    if st.button("Login"):
        tf,result=token(codice_persona)
        if result:
            syn = synapseclient.Synapse()
            syn.login(authToken=tf)
            st.session_state.logged_in = True
            st.session_state.auth_token=tf
            st.success("Access granted.")
            st.rerun()
        else: 
            st.error(tf)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
    st.stop()

# SIDEBAR
st.sidebar.title("🧠 PDAI")
st.sidebar.markdown("**Parkinsonian Data Analysis Interface**")

st.sidebar.divider()

# HOMEPAGE
st.title("Parkinsonian Data Analysis Interface")
st.subheader("Parkinson's Disease patient analytics")

st.write(
    "This application allows physicians to view demographic data, "
    "statistical data, clinical variables, movement variables, and data "
    "that can be structured according to healthcare standards."
)

st.divider()

# RIGA 1
col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("👤 Demographics")
        st.write("View general patient information: ID, age, gender, and other personal details.")
        if st.button("Visit section →", key="btn_demo", use_container_width=True, type="primary"):
            st.switch_page("pages/1 Dati_demografici.py")

with col2:
    with st.container(border=True):
        st.subheader("📊 Statistics")
        st.write("View descriptive statistics, means, standard deviations, and comparisons between variables.")
        if st.button("Visit section →", key="btn_stat", use_container_width=True, type="primary"):
            st.switch_page("pages/2 Dati_statistici.py")

st.divider()

# RIGA 2
col3, col4 = st.columns(2)

with col3:
    with st.container(border=True):
        st.subheader("🔎 Research & Open Files")
        st.write("Explore the dataset and access files through parameter-based search.")
        if st.button("Visit section →", key="btn_dataset", use_container_width=True, type="primary"):
            st.switch_page("pages/3 Ricerca_e_Apertura_files.py")

with col4:
    with st.container(border=True):
        st.subheader("🩺 Clinical metrics")
        st.write("Analyze the clinical variables of patients, including scores and indicators related to the UPDRS scale.")
        if st.button("Visit section →", key="btn_clin", use_container_width=True, type="primary"):
            st.switch_page("pages/4 Variabili_cliniche.py")

st.divider()

# RIGA 3
col5, col6 = st.columns(2)

with col5:
    with st.container(border=True):
        st.subheader("🚶 Movements metrics")
        st.write("Analyze the variables related to movement, posture, and motor characteristics of patients.")
        if st.button("Visit section →", key="btn_mov", use_container_width=True, type="primary"):
            st.switch_page("pages/5 Variabili_movimento.py")

with col6:
    with st.container(border=True):
        st.subheader("🧬 FHIR")
        st.write("Management and structuring of data according to international healthcare standards.")
        if st.button("Visit section →", key="btn_fhir", use_container_width=True, type="primary"):
            st.switch_page("pages/6 FHIR.py")