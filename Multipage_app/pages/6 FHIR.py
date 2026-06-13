import json
from datetime import datetime, timezone
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
import pandas as pd
import streamlit as st
import synapseclient

#configurazione pagine 
st.set_page_config(page_title="Esportazione FHIR", page_icon="☁", layout="wide")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("⚠️ Please log in from the Homepage.")
    st.stop()

# Connessione a Synapse con il token salvato al login
syn = synapseclient.Synapse()
syn.login(authToken=st.session_state.auth_token)

# ID delle cartelle Synapse separate per i due gruppi
folder_id_controlli = "syn61370532"   # cartella pazienti sani (controlli)
folder_id_pd        = "syn61370536"   # cartella pazienti con Parkinson

# ______________________________________________________________
# DIZIONARIO DEI CODICI LOINC
# ogni elemento selezionabile è una chiave a cui è associato un'
# altro dizionario in cui ho:
#   "code"    → codice ufficiale LOINC (verificato su loinc.org)
#   "display" → nome leggibile che appare nel file esportato
# ______________________________________________________________
LOINC_CODES = {
    # Dati demografici
    "age":    {"code": "30525-0", "display": "Age"},             # loinc.org/30525-0
    "gender": {"code": "46098-0", "display": "Sex"},             # loinc.org/46098-0
    "weight": {"code": "29463-7", "display": "Body weight"},     # loinc.org/29463-7
    "height": {"code": "8302-2",  "display": "Body height"},     # loinc.org/8302-2
    # Dati clinici Parkinson
    "hoehn_yahr":      {"code": "77718-5", "display": "Hoehn and Yahr scale [UPDRS]"},  # loinc.org/77718-5
    "years_diagnosis": {"code": "65163-7", "display": "Disease duration"},              # loinc.org/65163-7
    "dbs":             {"code": "45261-3", "display": "Device present"},                # loinc.org/45261-3
    # Dati di cammino ed equilibrio (calcolati dai file sensori)
    "numero_passi": {"code": "55423-8", "display": "Number of steps in unspecified time Pedometer"}, # loinc.org/55423-8
    "cadenza":      {"code": "55414-6", "display": "Step rate"},                                      # loinc.org/55414-6
    "durata_tug":   {"code": "89423-8", "display": "Timed Up and Go Test time"},                     # loinc.org/89423-8
    "sway_ap_eo":   {"code": "83178-4", "display": "Sway anteroposterior eyes open"},                # loinc.org/83178-4
    "velocita":     {"code": "55394-0", "display": "Walking speed"},                                  # loinc.org/55394-0
}

# ________________________________________________________________
# CARICAMENTO DEI FILE CLINICI CSV
# header=1 → la prima riga del CSV è ignorata
# (c'è una riga extra di intestazione prima dei veri nomi colonna)
# ________________________________________________________________
df_control = pd.read_csv("CONTROLS.csv", sep=",", header=1)
df_pd      = pd.read_csv("PD.csv",       sep=",", header=1)
percorso_pkmas = syn.get("syn64589881").path
df_pkmas = pd.read_csv(percorso_pkmas, header=[0, 1])

# ________________________________________________________________
# FUNZIONE: crea una singola Observation FHIR
#
# Una Observation è l'unità base dello standard FHIR:
# descrive UNA misurazione clinica per UN paziente.
#
# Parametri:
#   patient_id → es. "NLS002"
#   nome_campo → es. "age" (chiave del dizionario LOINC_CODES)
#   valore     → il valore misurato (numero o testo)
#   unita      → unità di misura, es. "kg", "years" (opzionale)
# ________________________________________________________________
def crea_observation_loinc(patient_id, nome_campo, valore, unita=None):
    codice_loinc = LOINC_CODES[nome_campo] #prende il dizionario {code,display} associato 
                                            # al campo passato in ingresso
    observation = {
        "resourceType": "Observation",
        "status": "final",
        "code": {   "coding": [{"system": "http://loinc.org","code":codice_loinc["code"],
                              "display": codice_loinc["display"]}],
                    "text": codice_loinc["display"]},
        "subject": {"reference": f"Patient/{patient_id}"},
        "effectiveDateTime": datetime.now(timezone.utc).isoformat() #
    }

    try:  # se il valore è un numero, lo salva come quantità
        valore_num = float(valore)
        observation["valueQuantity"] = {"value": round(valore_num, 2)}
        if unita is not None:
            observation["valueQuantity"]["unit"] = unita
    except:  # se non è un numero, lo salva come testo
        observation["valueString"] = str(valore)
    
    return observation

# _______________________________________________________________
# FUNZIONE: scarica un file da Synapse e lo legge come DataFrame
#
# Cerca il file con quel nome dentro la cartella Synapse,
# lo scarica in locale e lo restituisce come tabella pandas.
#
# Parametri:
#   nome_file → es. "NLS002_SelfPace.csv" 
#   cartella → contiene l'id della cartella a cui si deve accedere
# _______________________________________________________________
def carica_file_synapse(nome_file, cartella):
    # Cerca tutti i file nella cartella Synapse indicata
    elementi = list(syn.getChildren(cartella))
    for element in elementi:
        if element["name"]=="CSV files":
            file_cvs=list(syn.getChildren(element["id"]))

    # Cerca il file con il nome che ci serve
    for file in file_cvs:
        if file["name"] == nome_file :
            file_scaricato = syn.get(file["id"], downloadFile=True)
            percorso = file_scaricato.path   # scarica il file
            return pd.read_csv(percorso)            # lo legge come DataFrame
    return None # Se non lo trova, restituisce None
# ____________________________________________________________
# FUNZIONE: calcola passi e cadenza dal file SelfPace
#
# Conta quante volte il piede tocca terra durante il cammino
# e calcola la cadenza (passi al minuto).
# ____________________________________________________________
def calcola_passi_cadenza(df):
    # Prende solo le righe della fase "Walk"
    walk = df[df["GeneralEvent"] == "Walk"].copy()

    # Converte la colonna Time da testo a numero (es. "12.5 sec" → 12.5)
    walk["time_sec"] = walk["Time"].str.replace(" sec", "").astype(float)

    # Durata totale della camminata in secondi
    durata = walk["time_sec"].max() - walk["time_sec"].min()

    # Conta i passi: ogni volta che "L Foot Contact" passa da 0 a 1 = un passo sinistro
    # diff() calcola la differenza tra un valore e quello della riga precedente
    # se il risultato è =1 il piede si appoggia se il risultato è = -1 il piede si alza
    # se il risultato = 0 il piede continua a stare per aria o appoggiato
    passi_L = (walk["L Foot Contact"].diff() == 1).sum() 
    passi_R = (walk["R Foot Contact"].diff() == 1).sum()
    tot_passi = int(passi_L + passi_R)

    # Cadenza = passi al minuto
    cadenza = round((tot_passi / durata) * 60, 1)

    return tot_passi, cadenza


# ______________________________________________________________
# FUNZIONE: calcola la durata del TUG test
#
# Il TUG (Timed Up and Go) misura il tempo da quando il
# paziente si alza dalla sedia a quando si rigira e si siede.
# ______________________________________________________________
def calcola_tug(df):
    df = df.copy()
    # Converte la colonna Time da testo a numero (es. "12.5 sec" → 12.5)
    df["time_sec"] = df["Time"].str.replace(" sec", "").astype(float) 

    # Inizio = prima riga della fase SitToStand -> inizio a calcolare il tempo 
    # da quando il paziente si alza dalla sedia (quindi prendi il tempo minimo della fase "SitToStand")
    inizio = df[df["GeneralEvent"] == "SitToStand"]["time_sec"].min()

    # Fine = ultima riga della fase TurnToSit -> finisco di calcolare il tempo quando il paziente finisce 
    # di fare il giro e si risiede sulla sedia (quindi prendo il tempo massimo della fase "TurnToSit")
    fine   = df[df["GeneralEvent"] == "TurnToSit"]["time_sec"].max()

    durata_tug = round(fine - inizio, 2)    # round() è una funzione Python che arrotonda un numero decimale
                                            # l'altro parametro dato in ingresso è la cifra decimale a cui 
                                            # si vuole fare l'arrotondamento
    return durata_tug


# _____________________________________________________________
# FUNZIONE: calcola lo Sway AP a occhi aperti
#
# Lo Sway è l'oscillazione del corpo durante l'equilibrio.
# AP = Antero-Posteriore (avanti-indietro).
# Lo calcoliamo come differenza tra valore massimo e minimo
# dell'accelerometro lombare durante la fase a occhi aperti.
# _____________________________________________________________
def calcola_sway_ap_eo(df):
    # Fase occhi aperti con piedi alla larghezza delle spalle
    eo = df[df["GeneralEvent"] == "EO_FeetShoWidth"]

    # LowerBack_FreeAcc_N = accelerazione libera direzione Nord = Antero-Posteriore
    sway_ap = round(eo["LowerBack_FreeAcc_N"].max() - eo["LowerBack_FreeAcc_N"].min(), 4)
    return sway_ap

# __________________________________________________________________
# FUNZIONE: estrae la velocità di cammino dal file PKMAS
#
# Il file PKMAS contiene metriche già calcolate per ogni paziente.
# La velocità è in cm/s, la convertiamo in m/s dividendo per 100.
#
# Parametri:
#   patient_id → es. "NLS002"
# __________________________________________________________________
def estrai_velocita_pkmas(patient_id):
    # Le colonne del PKMAS hanno doppia intestazione, quindi
    # usiamo una tupla (nome_metrica, tipo_valore) per accedere
    task_col = df_pkmas.columns[0]   # colonna "Task"
    id_col   = df_pkmas.columns[1]   # colonna "Participant ID"
    vel_col  = ("Velocity (cm./sec.)", "Unnamed: 9_level_1")  # colonna velocità media

    # Cerca la riga del paziente con task "SelfPace"
    riga = df_pkmas[(df_pkmas[id_col] == patient_id) & (df_pkmas[task_col] == "SelfPace")]

    if len(riga) == 0:
        return None  # paziente non trovato nel PKMAS

    # Prende il valore e lo converte da cm/s a m/s
    velocita_cm = float(riga[vel_col].values[0])    # .values prende i valori all'interno di riga[vel_col] 
                                                    # e con [0] prende solo il primo valore
    velocita_ms = round(velocita_cm / 100, 3)   # così passo da una velocitàda cm/s (che è quella data nel
                                                # file) ad una in m/s
    return velocita_ms

# ________________________________________________________________________
# FUNZIONE: converte la lista di Observations in XML FHIR
#
# Lo standard FHIR prevede un "Bundle" come contenitore:
# è una lista di risorse (in questo caso Observations) in un unico file.
# ________________________________________________________________________
def converti_in_xml(observations):
    bundle = Element("Bundle") # Crea il tag radice <Bundle> — la scatola più esterna che contiene tutto
    bundle.set("xmlns", "http://hl7.org/fhir") # .set() aggiunge un attributo al bundle

    tipo = SubElement(bundle, "type") # Subelement() crea un tag DENTRO un altro tag
    tipo.set("value", "collection") # .set("attributo", "valore") aggiunge un attributo al tag

    for obs in observations:
        # creo vari tag concatenati
        entry        = SubElement(bundle, "entry")
        resource     = SubElement(entry, "resource")
        obs_el       = SubElement(resource, "Observation")

        # Status
        st_el = SubElement(obs_el, "status")
        st_el.set("value", obs["status"]) # lo status lo prendo direttamente da observation

        # Codice LOINC
        code_el   = SubElement(obs_el, "code")
        coding_el = SubElement(code_el, "coding")
        # questi tag verranno visualizzati pari, non uno concatenato all'altro
        SubElement(coding_el, "system").set("value", obs["code"]["coding"][0]["system"])
        SubElement(coding_el, "code").set("value",   obs["code"]["coding"][0]["code"])
        SubElement(coding_el, "display").set("value", obs["code"]["coding"][0]["display"])

        # Paziente
        subj_el = SubElement(obs_el, "subject")
        SubElement(subj_el, "reference").set("value", obs["subject"]["reference"])

        # Data e ora
        SubElement(obs_el, "effectiveDateTime").set("value", obs["effectiveDateTime"])

        # Valore numerico o testuale
        if "valueQuantity" in obs:
            vq = SubElement(obs_el, "valueQuantity")
            SubElement(vq, "value").set("value", str(obs["valueQuantity"]["value"]))
            if "unit" in obs["valueQuantity"]:
                SubElement(vq, "unit").set("value", obs["valueQuantity"]["unit"])
        elif "valueString" in obs:
            SubElement(obs_el, "valueString").set("value", obs["valueString"])

    # tostring() prende l'oggetto Python bundle — che fino a questo momento è una struttura interna di 
    # Python, non un testo — e lo converte in una stringa di testo XML.
    # encoding="unicode" dice di usare caratteri normali (non byte), così possiamo lavorarci direttamente.
    # Il risultato è una stringa valida ma che presenta tutto su una riga sola senza spazi:
    xml_grezzo = tostring(bundle, encoding="unicode")
    # minidom.parseString(xml_grezzo) Rilegge la stringa "brutta" e la trasforma in un oggetto minidom — 
    # una libreria diversa da ElementTree, specializzata nella formattazione.
    # .toprettyxml(indent="  ")
    # toprettyxml significa letteralmente "converti in XML bello". Il parametro indent="  " 
    # dice di usare 2 spazi per ogni livello di rientro.
    xml_bello  = minidom.parseString(xml_grezzo).toprettyxml(indent="  ")
    return xml_bello


# =======================================================
# INTERFACCIA STREAMLIT
# =======================================================
st.title("FHIR Export")
st.divider()

# Scelta del formato di esportazione
formato = st.radio("Seleziona il formato di esportazione", ["JSON", "XML"])

# Inserimento ID paziente
patient_id = st.text_input("Inserisci l'ID paziente", placeholder="es. NLS002")

# Variabili iniziali (vuote finché non si trova il paziente)
paziente_scelto = None
stato_paziente  = None
riga_paziente   = None

# Cerca prima nei controlli sani
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


if paziente_scelto: # i checkbox e il bottone per il download appaiono solo se il paziente è stato trovato

    st.success(f"✅ Paziente trovato: {paziente_scelto} ({stato_paziente})")
    observations = []  # lista vuota che riempiremo con le osservazioni selezionate

    if stato_paziente == "control":
        col1, col2 = st.columns(2)
    else:
        col1, col2, col3 = st.columns(3)

    # Colonna 1: dati demografici (uguale per tutti)
    with col1:
        with st.container(border=True):
            st.text("Dati demografici 👤")
            age    = st.checkbox("Età (Age)")
            gender = st.checkbox("Sesso (Gender)")
            weight = st.checkbox("Peso (Weight)")
            height = st.checkbox("Altezza (Height)")

    # Colonna 2: dati clinici Parkinson (solo per i PD)
    if stato_paziente == "pd":
        with col2:
            with st.container(border=True):
                st.text("Dati clinici Parkinson 📋")
                hoehn_yahr      = st.checkbox("Hoehn & Yahr Score")
                years_diagnosis = st.checkbox("Anni dalla diagnosi")
                dbs             = st.checkbox("DBS impiantato (DBS?)")

    # Ultima colonna: dati di cammino ed equilibrio (uguale per tutti)
    # Per i controlli è col2, per i PD è col3
    if stato_paziente=="control":
        ultima_col=col2
    else: 
        ultima_col=col3
    
    with ultima_col:
        with st.container(border=True):
            st.text("Cammino e Equilibrio 🚶")
            cb_passi     = st.checkbox("Numero passi (SelfPace)")
            cb_cadenza   = st.checkbox("Cadenza (passi/min)")
            cb_tug       = st.checkbox("Durata TUG test (sec)")
            cb_sway      = st.checkbox("Sway AP occhi aperti")
            cb_velocita  = st.checkbox("Velocità di cammino (m/s)")

    st.divider()

    # ___________________________________________________________________
    # Per ogni checkbox selezionata, aggiunge una Observation alla lista
    # ___________________________________________________________________

    # --- Dati demografici ---
    if age:
        if stato_paziente=="control":
            eta=riga_paziente["Age"]
        else: 
            eta=riga_paziente["Age (years)"]
        observations.append(crea_observation_loinc(paziente_scelto, "age", eta, "years"))

    if gender:
        observations.append(crea_observation_loinc(paziente_scelto, "gender", riga_paziente["Gender"]))

    if weight:
        observations.append(crea_observation_loinc(paziente_scelto, "weight", riga_paziente["Weight (kg)"], "kg"))

    if height:
        observations.append(crea_observation_loinc(paziente_scelto, "height", riga_paziente["Height (in)"], "in"))

    # --- Dati clinici Parkinson (solo se il paziente è PD) ---
    if stato_paziente == "pd":
        if hoehn_yahr:
            observations.append(crea_observation_loinc(paziente_scelto, "hoehn_yahr", riga_paziente["Modified Hoehn & Yahr Score"]))

        if years_diagnosis:
            observations.append(crea_observation_loinc(paziente_scelto, "years_diagnosis", riga_paziente["Years since PD diagnosis"], "years"))

        if dbs:
            observations.append(crea_observation_loinc(paziente_scelto, "dbs", riga_paziente["DBS?"]))

    # Sceglie la cartella giusta in base al tipo di paziente
    if stato_paziente=="pd":
        cartella=folder_id_pd
    else:
        cartella=folder_id_controlli

    # Passi e cadenza → file SelfPace
    if cb_passi or cb_cadenza:
        nome_selfpace = f"{paziente_scelto}_SelfPace.csv"
        with st.spinner(f"Scarico {nome_selfpace} da Synapse..."):
            df_selfpace = carica_file_synapse(nome_selfpace, cartella)

        if df_selfpace is not None:
            tot_passi, cadenza_val = calcola_passi_cadenza(df_selfpace)
            if cb_passi:
                observations.append(crea_observation_loinc(paziente_scelto, "numero_passi", tot_passi, "steps"))
            if cb_cadenza:
                observations.append(crea_observation_loinc(paziente_scelto, "cadenza", cadenza_val, "steps/min"))
        else:
            st.warning(f"⚠️ File {nome_selfpace} non trovato su Synapse.")

    # Durata TUG → file TUG
    if cb_tug:
        nome_tug = f"{paziente_scelto}_TUG.csv"
        with st.spinner(f"Scarico {nome_tug} da Synapse..."):
            df_tug = carica_file_synapse(nome_tug, cartella)

        if df_tug is not None:
            durata = calcola_tug(df_tug)
            observations.append(crea_observation_loinc(paziente_scelto, "durata_tug", durata, "s"))
        else:
            st.warning(f"⚠️ File {nome_tug} non trovato su Synapse.")

    # Sway AP → file Balance
    if cb_sway:
        nome_balance = f"{paziente_scelto}_Balance.csv"
        with st.spinner(f"Scarico {nome_balance} da Synapse..."):
            df_balance = carica_file_synapse(nome_balance, cartella)

        if df_balance is not None:
            sway = calcola_sway_ap_eo(df_balance)
            observations.append(crea_observation_loinc(paziente_scelto, "sway_ap_eo", sway, "m/s2"))
        else:
            st.warning(f"⚠️ File {nome_balance} non trovato su Synapse.")

    # Velocità → file PKMAS (già caricato in memoria, non serve Synapse)
    # Il PKMAS è un file unico con tutti i pazienti, quindi cerchiamo
    # direttamente il paziente scelto senza scaricare nulla
    if cb_velocita:
        vel = estrai_velocita_pkmas(paziente_scelto)
        if vel is not None:
            observations.append(crea_observation_loinc(paziente_scelto, "velocita", vel, "m/s"))
        else:
            st.warning(f"⚠️ Paziente {paziente_scelto} non trovato nel file PKMAS.")

    if len(observations) == 0:
        st.info("Seleziona almeno un dato da esportare.")
    else:
        st.divider()
        st.subheader("Esporta il file")
        if formato == "JSON":
            # json.dumps converte la lista Python in testo JSON
            # indent=2 aggiunge i rientri per renderlo leggibile
            contenuto_file = json.dumps(observations, indent=2)
            nome_file = f"FHIR_{paziente_scelto}.json"
            tipo_mime = "application/json"  # dice al browser che tipo di file sta per ricevere quando 
                                            # clicchi il bottone di download -> serve al browser per sapere
                                            # come trattare i file
        else:  # XML
            contenuto_file = converti_in_xml(observations)
            nome_file = f"FHIR_{paziente_scelto}.xml"
            tipo_mime = "application/xml"

        st.download_button(
            label     = f"⬇️ Scarica file {formato}",
            data      = contenuto_file,
            file_name = nome_file,
            mime      = tipo_mime
        )
# Se l'utente ha scritto qualcosa ma il paziente non esiste
elif patient_id:
    st.error("❌ ID paziente non trovato. Controlla di aver inserito l'ID corretto.")