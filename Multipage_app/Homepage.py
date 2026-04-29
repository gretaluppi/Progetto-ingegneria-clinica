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
            st.success("Login effettuato")
            return token_finale,True
    token_finale="Nessun token valido trovato, riprovare"
    return token_finale,False
        
def login(): 
    st.title("Login")
    codice_persona=st.text_input("Inserire il codice persona per l'accesso", placeholder="es: Francesca")
    if st.button("Accedi"):
        tf,result=token(codice_persona)
        if result:
            syn = synapseclient.Synapse()
            syn.login(authToken=tf)
            st.session_state.logged_in = True
            st.session_state.auth_token=tf
            st.success("Login effettuato")
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
st.subheader("Dashboard per l’analisi dei dati dei pazienti con Parkinson")

st.write(
    "Questa applicazione permette al medico di consultare dati demografici, "
    "dati statistici, variabili cliniche, variabili di movimento e dati "
    "strutturabili secondo standard sanitari."
)

st.divider()

# PRIMA RIGA
col1, col2 = st.columns(2)

with col1:
    st.subheader("👤 Dati demografici")
    st.write("Visualizza le informazioni generali dei pazienti, come identificativo, "
        "età, sesso e altri dati anagrafici.")

    if st.button("Vai alla sezione", key="btn_demo", use_container_width=True):
        st.switch_page("pages/1 Dati_demografici.py")

with col2:
    st.subheader("📊 Dati statistici")
    st.write("Consulta statistiche descrittive, medie, deviazioni standard "
        "e confronti tra variabili.")

    if st.button("Vai alla sezione", key="btn_stat", use_container_width=True):
        st.switch_page("pages/2 Dati_statistici.py")

st.divider()

# SECONDA RIGA
col3, col4 = st.columns(2)

with col3:
    st.subheader("🔎 Ricerca e apertura files")
    st.write("Esplora il dataset e accedi ai file tramite ricerca per parametri")

    if st.button("Vai alla sezione", key="btn_dataset", use_container_width=True):
        st.switch_page("pages/3 Ricerca_e_Apertura_files.py")

with col4:
    st.subheader("🩺 Variabili cliniche")
    st.write("Analizza le variabili cliniche dei pazienti, inclusi punteggi "
        "e indicatori collegati alla scala UPDRS.")

    if st.button("Vai alla sezione", key="btn_clin", use_container_width=True):
        st.switch_page("pages/4 Variabili_cliniche.py")

st.divider()

# TERZA RIGA
col5, col6 = st.columns(2)

with col5:
    st.subheader("🚶 Variabili movimento")
    st.write("Esamina le variabili relative al movimento, alla postura "
        "e alle caratteristiche motorie dei pazienti.")

    if st.button("Vai alla sezione", key="btn_mov", use_container_width=True):
        st.switch_page("pages/5 Variabili_movimento.py")

with col6:
    st.subheader("🧬 FHIR")
    st.write("Gestione e struttura dei dati secondo standard sanitari.")

    if st.button("Vai alla sezione", key="btn_fhir", use_container_width=True):
        st.switch_page("pages/6 FHIR.py")
