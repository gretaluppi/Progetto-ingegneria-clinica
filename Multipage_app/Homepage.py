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
    "Questa applicazione permette al medico di consultare dati demografici, "
    "dati statistici, variabili cliniche, variabili di movimento e dati "
    "strutturabili secondo standard sanitari."
)

st.divider()

# RIGA 1
col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("👤 Demographics")
        st.write("Visualizza le informazioni generali dei pazienti: identificativo, età, sesso e altri dati anagrafici.")
        if st.button("Visit section →", key="btn_demo", use_container_width=True, type="primary"):
            st.switch_page("pages/1 Dati_demografici.py")

with col2:
    with st.container(border=True):
        st.subheader("📊 Statistics")
        st.write("Consulta statistiche descrittive, medie, deviazioni standard e confronti tra variabili.")
        if st.button("Visit section →", key="btn_stat", use_container_width=True, type="primary"):
            st.switch_page("pages/2 Dati_statistici.py")

st.divider()

# RIGA 2
col3, col4 = st.columns(2)

with col3:
    with st.container(border=True):
        st.subheader("🔎 Research & Open Files")
        st.write("Esplora il dataset e accedi ai file tramite ricerca per parametri.")
        if st.button("Visit section →", key="btn_dataset", use_container_width=True, type="primary"):
            st.switch_page("pages/3 Ricerca_e_Apertura_files.py")

with col4:
    with st.container(border=True):
        st.subheader("🩺 Clinical metrics")
        st.write("Analizza le variabili cliniche dei pazienti, inclusi punteggi e indicatori collegati alla scala UPDRS.")
        if st.button("Visit section →", key="btn_clin", use_container_width=True, type="primary"):
            st.switch_page("pages/4 Variabili_cliniche.py")

st.divider()

# RIGA 3
col5, col6 = st.columns(2)

with col5:
    with st.container(border=True):
        st.subheader("🚶 Movements metrics")
        st.write("Esamina le variabili relative al movimento, alla postura e alle caratteristiche motorie dei pazienti.")
        if st.button("Visit section →", key="btn_mov", use_container_width=True, type="primary"):
            st.switch_page("pages/5 Variabili_movimento.py")

with col6:
    with st.container(border=True):
        st.subheader("🧬 FHIR")
        st.write("Gestione e struttura dei dati secondo standard sanitari internazionali.")
        if st.button("Visit section →", key="btn_fhir", use_container_width=True, type="primary"):
            st.switch_page("pages/6 FHIR.py")