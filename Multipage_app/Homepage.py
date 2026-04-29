import streamlit as st

st.set_page_config(
    page_title="PDAI",
    page_icon="🧠",
    layout="wide"
)

# SIDEBAR
st.sidebar.title("🧠 PDAI")
st.sidebar.markdown("**Parkinsonian Data Analysis Interface**")

st.sidebar.divider()

st.sidebar.write("📌 Navigazione:")
st.sidebar.write("Usa il menu sopra per accedere alle sezioni")

st.sidebar.divider()

st.sidebar.success("Sistema pronto all'uso")

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

    if st.button("Vai alla sezione", key="demo", use_container_width=True):
        st.switch_page("pages/1 Dati_demografici.py")

with col2:
    st.subheader("📊 Dati statistici")
    st.write("Consulta statistiche descrittive, medie, deviazioni standard "
        "e confronti tra variabili.")

    if st.button("Vai alla sezione", key="stat", use_container_width=True):
        st.switch_page("pages/2 Dati_statistici.py")

# SECONDA RIGA
col3, col4 = st.columns(2)

with col3:
    st.subheader("🩺 Variabili cliniche")
    st.write("Analizza le variabili cliniche dei pazienti, inclusi punteggi "
        "e indicatori collegati alla scala UPDRS.")

    if st.button("Vai alla sezione", key="clin", use_container_width=True):
        st.switch_page("pages/3 Variabili_cliniche.py")

with col4:
    st.subheader("🚶 Variabili movimento")
    st.write("Esamina le variabili relative al movimento, alla postura "
        "e alle caratteristiche motorie dei pazienti.")

    if st.button("Vai alla sezione", key="mov", use_container_width=True):
        st.switch_page("pages/4 Variabili_movimento.py")

st.divider()

# TERZA SEZIONE (FHIR)
st.subheader("🧬 FHIR")
st.write("Gestione e struttura dei dati secondo standard sanitari.")

if st.button("Vai alla sezione", key="fhir", use_container_width=True):
    st.switch_page("pages/5 FHIR.py")
