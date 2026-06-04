import json
from datetime import datetime, timezone
from pathlib import Path
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring

import pandas as pd
import streamlit as st
import synapseclient

st.set_page_config(page_title="Esportazione FHIR", page_icon="☁", layout="wide")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("⚠️ Please log in from the Homepage.")
    st.stop()

syn = synapseclient.Synapse()
syn.login(authToken=st.session_state.auth_token)
folder_file="syn61370558"
LOINC_CODES = {
    "age": {
        "code": "30525-0",
        "display": "Age"
    },
    "gender": {
        "code": "46098-0",
        "display": "Sex"
    },
    "weight": {
        "code": "29463-7",
        "display": "Body weight"
    },
    "height": {
        "code": "8302-2",
        "display": "Body height"
    }
}
df_control = pd.read_csv("CONTROLS.csv", sep="," , header=1)
df_pd = pd.read_csv("PD.csv", sep="," , header=1)

def crea_observation_loinc(patient_id, nome_campo, valore, unita=None):
    codice_loinc = LOINC_CODES[nome_campo]
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
            "reference": f"Patient/{patient_id}"
        },
        "effectiveDateTime": datetime.now(timezone.utc).isoformat()
    }

    try:
        valore_num = float(valore)

        observation["valueQuantity"] = {
            "value": valore_num
        }

        if unita is not None:
            observation["valueQuantity"]["unit"] = unita

    except:
        observation["valueString"] = str(valore)

    return observation
st.title("FHIR Export")
st.divider()
genre = st.radio("Select the export format", ["JSON","xml"])
patient_id = st.text_input("Enter patient ID", placeholder="e.g. NLS002")
col1, col2 = st.columns(2)
with col1: 
    with st.container(border=True):
        st.text("Select which demographic data to export")
        age = st.checkbox("Age")
        gender = st.checkbox("Gender")
        weight = st.checkbox("Weight")
        height = st.checkbox("Height")
with col2: 
    with st.container(border=True):
        st.text("Select which clinical data to export")
        speed = st.checkbox("Average speed")
        updrs= st.checkbox("UPDRS total score")
        years_diagnosis = st.checkbox("Years since PD diagnosis")

paziente_scelto = None
stato_paziente = None
riga_paziente = None

for i,row in df_control.iterrows():
    if row["Subject ID"]==patient_id:
        paziente_scelto=patient_id
        stato_paziente="control"
        riga_paziente = row
        break
    else:
        for i,row in df_pd.iterrows():
            if row["Subject ID"]==patient_id:
                paziente_scelto=patient_id
                stato_paziente="pd"
                riga_paziente = row
                break
if paziente_scelto:
    st.success(f"Patient found: {paziente_scelto} ({stato_paziente})")
    st.dataframe(pd.DataFrame([riga_paziente]))
    observations = []

    if age:
        if stato_paziente == "control":
            eta = riga_paziente["Age"]
        else:
            eta = riga_paziente["Age (years)"]
        observations.append(crea_observation_loinc(paziente_scelto,"age",eta,"years"))

    if gender:
        genere = riga_paziente["Gender"]
        observations.append(crea_observation_loinc(paziente_scelto,"gender",genere))

    if weight:
        peso = riga_paziente["Weight (kg)"]
        observations.append(crea_observation_loinc(paziente_scelto,"weight",peso,"kg"))

    if height:
        altezza = riga_paziente["Height (in)"]
        observations.append(crea_observation_loinc(paziente_scelto,"height",altezza,"in"))
    st.subheader("LOINC Observations preview")
    st.json(observations)
elif patient_id:
    st.error("Patient ID not found.")





