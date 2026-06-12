import json                          # per creare file JSON
from datetime import datetime, timezone  # per aggiungere la data e ora corrente
from xml.etree.ElementTree import Element, SubElement, tostring  # per creare file XML
from xml.dom import minidom             # per rendere l'XML più leggibile (con rientri)

import pandas as pd
import streamlit as st
import synapseclient

# ============================================================
# CONFIGURAZIONE PAGINA
# ============================================================
st.set_page_config(page_title="Esportazione FHIR", page_icon="☁", layout="wide")

# Controlla che l'utente abbia fatto login dalla homepage
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("⚠️ Please log in from the Homepage.")
    st.stop()

# Connessione a Synapse usando il token salvato al login
syn = synapseclient.Synapse()
syn.login(authToken=st.session_state.auth_token)

# ============================================================
# DIZIONARIO DEI CODICI LOINC
#
# Ogni voce contiene:
#   "code"    → il codice LOINC ufficiale (verificato su loinc.org)
#   "display" → il nome leggibile che appare nel file esportato
# ============================================================
LOINC_CODES = {

    # --- DATI DEMOGRAFICI ---
    "age": {
        "code": "30525-0",
        "display": "Age"
        # Fonte: loinc.org/30525-0
    },
    "gender": {
        "code": "46098-0",
        "display": "Sex"
        # Fonte: loinc.org/46098-0
    },
    "weight": {
        "code": "29463-7",
        "display": "Body weight"
        # Fonte: loinc.org/29463-7
    },
    "height": {
        "code": "8302-2",
        "display": "Body height"
        # Fonte: loinc.org/8302-2
    },

    # --- DATI CLINICI PARKINSON ---
    "hoehn_yahr": {
        "code": "77718-5",
        "display": "Hoehn and Yahr scale [UPDRS]"
        # Fonte: loinc.org/77718-5
        # Scala da 0 a 5 che descrive lo stadio globale della malattia di Parkinson.
        # Nel CSV si chiama: "Modified Hoehn & Yahr Score"
    },
    "years_diagnosis": {
        "code": "65163-7",
        "display": "Disease duration"
        # Fonte: loinc.org/65163-7
        # Anni trascorsi dalla diagnosi di Parkinson.
        # Nel CSV si chiama: "Years since PD diagnosis"
    },
    "dbs": {
        "code": "45261-3",
        "display": "Device present"
        # Fonte: loinc.org/45261-3
        # Indica se il paziente ha un dispositivo DBS (Deep Brain Stimulation) impiantato.
        # Nel CSV si chiama: "DBS?"
    },
}

# ============================================================
# CARICAMENTO DEI FILE CSV
#
# header=1 significa che la riga 0 è ignorata (nel tuo CSV
# c'è una riga extra di intestazione prima dei veri nomi colonna)
# ============================================================
df_control = pd.read_csv("CONTROLS.csv", sep=",", header=1)
df_pd      = pd.read_csv("PD.csv",       sep=",", header=1)


# ============================================================
# FUNZIONE: crea una singola "Observation" FHIR in formato dizionario
#
# Una Observation FHIR è un'unità di misura clinica standard.
# Contiene: chi è il paziente, cosa si misura, e il valore misurato.
#
# Parametri:
#   patient_id  → es. "NLS002"
#   nome_campo  → es. "age" (deve essere una chiave in LOINC_CODES)
#   valore      → il valore misurato (numero o testo)
#   unita       → l'unità di misura, es. "years", "kg" (opzionale)
# ============================================================
def crea_observation_loinc(patient_id, nome_campo, valore, unita=None):

    # Prende il codice LOINC corrispondente dal dizionario
    codice_loinc = LOINC_CODES[nome_campo]

    # Struttura base dell'Observation FHIR
    observation = {
        "resourceType": "Observation",
        "status": "final",
        "code": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": codice_loinc["code"],
                    "display": codice_loinc["display"]
                }
            ],
            "text": codice_loinc["display"]
        },
        "subject": {
            "reference": f"Patient/{patient_id}"   # collega l'osservazione al paziente
        },
        "effectiveDateTime": datetime.now(timezone.utc).isoformat()  # data e ora attuali
    }

    # Prova a trattare il valore come numero
    try:
        valore_num = float(valore)
        observation["valueQuantity"] = {"value": valore_num}
        if unita is not None:
            observation["valueQuantity"]["unit"] = unita

    # Se non è un numero, lo salva come testo
    except:
        observation["valueString"] = str(valore)

    return observation


# ============================================================
# FUNZIONE: converte una lista di Observations in XML FHIR
#
# Crea un "Bundle" FHIR (contenitore standard) con dentro
# tutte le Observations come risorse XML.
# ============================================================
def converti_in_xml(observations):

    # Elemento radice del Bundle FHIR
    bundle = Element("Bundle")
    bundle.set("xmlns", "http://hl7.org/fhir")

    # Tipo di Bundle: "collection" significa una raccolta di risorse
    tipo = SubElement(bundle, "type")
    tipo.set("value", "collection")

    # Per ogni observation, crea un <entry> dentro il Bundle
    for obs in observations:

        entry = SubElement(bundle, "entry")
        resource = SubElement(entry, "resource")
        observation_el = SubElement(resource, "Observation")

        # Status
        status_el = SubElement(observation_el, "status")
        status_el.set("value", obs["status"])

        # Codice LOINC
        code_el = SubElement(observation_el, "code")
        coding_el = SubElement(code_el, "coding")

        system_el = SubElement(coding_el, "system")
        system_el.set("value", obs["code"]["coding"][0]["system"])

        code_val_el = SubElement(coding_el, "code")
        code_val_el.set("value", obs["code"]["coding"][0]["code"])

        display_el = SubElement(coding_el, "display")
        display_el.set("value", obs["code"]["coding"][0]["display"])

        # Paziente
        subject_el = SubElement(observation_el, "subject")
        reference_el = SubElement(subject_el, "reference")
        reference_el.set("value", obs["subject"]["reference"])

        # Data e ora
        date_el = SubElement(observation_el, "effectiveDateTime")
        date_el.set("value", obs["effectiveDateTime"])

        # Valore: numerico o testuale
        if "valueQuantity" in obs:
            val_el = SubElement(observation_el, "valueQuantity")
            value_el = SubElement(val_el, "value")
            value_el.set("value", str(obs["valueQuantity"]["value"]))
            if "unit" in obs["valueQuantity"]:
                unit_el = SubElement(val_el, "unit")
                unit_el.set("value", obs["valueQuantity"]["unit"])

        elif "valueString" in obs:
            val_el = SubElement(observation_el, "valueString")
            val_el.set("value", obs["valueString"])

    # Converte l'XML in testo leggibile (con rientri)
    xml_grezzo = tostring(bundle, encoding="unicode")
    xml_bello  = minidom.parseString(xml_grezzo).toprettyxml(indent="  ")
    return xml_bello


# ============================================================
# INTERFACCIA STREAMLIT
# ============================================================
st.title("FHIR Export")
st.divider()

# --- Scelta formato ---
# L'utente sceglie se esportare in JSON o XML
formato = st.radio("Seleziona il formato di esportazione", ["JSON", "XML"])

# --- Inserimento ID paziente ---
patient_id = st.text_input("Inserisci l'ID paziente", placeholder="es. NLS002")

# --- Selezione dati da esportare ---
col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.text("Dati demografici")
        age    = st.checkbox("Età (Age)")
        gender = st.checkbox("Sesso (Gender)")
        weight = st.checkbox("Peso (Weight)")
        height = st.checkbox("Altezza (Height)")

with col2:
    with st.container(border=True):
        st.text("Dati clinici Parkinson")
        hoehn_yahr      = st.checkbox("Hoehn & Yahr Score")
        years_diagnosis = st.checkbox("Anni dalla diagnosi (Years since PD diagnosis)")
        dbs             = st.checkbox("DBS impiantato (DBS?)")


# ============================================================
# RICERCA DEL PAZIENTE NEI CSV
#
# Prima cerca nel file dei controlli sani,
# poi nel file dei pazienti con Parkinson.
# ============================================================
paziente_scelto = None   # ID del paziente trovato
stato_paziente  = None   # "control" oppure "pd"
riga_paziente   = None   # la riga del CSV con tutti i dati

# Cerca nei controlli
for i, row in df_control.iterrows():
    if row["Subject ID"] == patient_id:
        paziente_scelto = patient_id
        stato_paziente  = "control"
        riga_paziente   = row
        break

# Se non trovato nei controlli, cerca nei pazienti PD
if paziente_scelto is None:
    for i, row in df_pd.iterrows():
        if row["Subject ID"] == patient_id:
            paziente_scelto = patient_id
            stato_paziente  = "pd"
            riga_paziente   = row
            break


# ============================================================
# SE IL PAZIENTE È STATO TROVATO
# ============================================================
if paziente_scelto:
    st.success(f"Paziente trovato: {paziente_scelto} ({stato_paziente})")
    st.dataframe(pd.DataFrame([riga_paziente]))

    # --- Costruzione della lista di Observations ---
    # Ogni checkbox selezionata aggiunge una Observation alla lista
    observations = []

    # Età
    # Nota: la colonna si chiama diversamente nei due CSV
    if age:
        if stato_paziente == "control":
            eta = riga_paziente["Age"]
        else:
            eta = riga_paziente["Age (years)"]
        observations.append(crea_observation_loinc(paziente_scelto, "age", eta, "years"))

    # Sesso
    if gender:
        genere = riga_paziente["Gender"]
        observations.append(crea_observation_loinc(paziente_scelto, "gender", genere))

    # Peso
    if weight:
        peso = riga_paziente["Weight (kg)"]
        observations.append(crea_observation_loinc(paziente_scelto, "weight", peso, "kg"))

    # Altezza
    if height:
        altezza = riga_paziente["Height (in)"]
        observations.append(crea_observation_loinc(paziente_scelto, "height", altezza, "in"))

    # Hoehn & Yahr: disponibile SOLO per pazienti PD, non per i controlli
    if hoehn_yahr:
        if stato_paziente == "pd":
            hy = riga_paziente["Modified Hoehn & Yahr Score"]
            observations.append(crea_observation_loinc(paziente_scelto, "hoehn_yahr", hy))
        else:
            st.warning("⚠️ Hoehn & Yahr non disponibile per i soggetti di controllo.")

    # Anni dalla diagnosi: disponibile SOLO per pazienti PD
    if years_diagnosis:
        if stato_paziente == "pd":
            anni = riga_paziente["Years since PD diagnosis"]
            observations.append(crea_observation_loinc(paziente_scelto, "years_diagnosis", anni, "years"))
        else:
            st.warning("⚠️ Anni dalla diagnosi non disponibile per i soggetti di controllo.")

    # DBS: disponibile SOLO per pazienti PD
    if dbs:
        if stato_paziente == "pd":
            dbs_val = riga_paziente["DBS?"]
            observations.append(crea_observation_loinc(paziente_scelto, "dbs", dbs_val))
        else:
            st.warning("⚠️ DBS non disponibile per i soggetti di controllo.")

    # --- Anteprima dati ---
    st.subheader("Anteprima dati LOINC selezionati")

    if len(observations) == 0:
        st.info("Seleziona almeno un dato da esportare.")
    else:
        st.json(observations)  # mostra sempre un'anteprima in JSON, indipendentemente dal formato scelto

        # ============================================================
        # BOTTONE DI ESPORTAZIONE
        #
        # A seconda del formato scelto in cima, prepara il file
        # corretto e mostra il bottone per scaricarlo.
        # ============================================================
        st.divider()
        st.subheader("Esporta il file")

        if formato == "JSON":
            # Converte la lista di Observations in testo JSON formattato
            # indent=2 aggiunge i rientri per renderlo leggibile
            contenuto_file = json.dumps(observations, indent=2)

            nome_file = f"FHIR_{paziente_scelto}.json"
            tipo_mime = "application/json"

        else:  # formato == "XML"
            # Converte la lista di Observations in XML FHIR
            contenuto_file = converti_in_xml(observations)

            nome_file = f"FHIR_{paziente_scelto}.xml"
            tipo_mime = "application/xml"

        # Mostra il bottone di download
        st.download_button(
            label     = f"⬇️ Scarica file {formato}",
            data      = contenuto_file,           # il contenuto del file
            file_name = nome_file,                # il nome del file scaricato
            mime      = tipo_mime                 # il tipo di file (detto al browser)
        )

# Se l'utente ha scritto qualcosa ma il paziente non è stato trovato
elif patient_id:
    st.error("❌ ID paziente non trovato. Controlla di aver inserito l'ID corretto.")