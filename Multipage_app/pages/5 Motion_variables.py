#st.set_page_config(page_title="Variabili Movimento", page_icon="👟", layout="wide")

import synapseclient
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import synapseutils 
#import matplotlib.pyplot as plt

# LOGIN
def token(nome):
    file_token=pd.read_csv("TOKEN.csv")
    for i,row in file_token.iterrows():
        if row["Name"]==nome.lower():
            token_finale=row["Token"]
            st.success("Login successful.")
            return token_finale,True
    token_finale="No valid token found, please try again."
    return token_finale,False
        
def login(): 
    st.title("Login")
    codice_persona=st.text_input("Enter your user ID", placeholder="es: Francesca")
    if st.button("Login"):
        tf,result=token(codice_persona)
        if result:
            syn = synapseclient.Synapse()
            syn.login(authToken=tf)
            st.session_state.logged_in = True
            st.session_state.auth_token=tf
            st.success("Login successful.")
            st.rerun()
        else: 
            st.error(tf)

st.title("Movements metrics")
st.divider()
st.write("TESTO DA SCRIVERE ...")

# seleziona dalla sidebar la tipologia di grafico da mostrare
scelta_gruppo = st.sidebar.radio(
    "Choose one option:",
    options=["One specific patient", "Two specific patients", "General trend PD vs. CONTROLS"], 
    index=None
)

#1. grafico del CoP del paziente i in balance con occhi aperti vs chiusi
if scelta_gruppo == "One specific patient":
    st.subheader("Patient Balance: CoP Comparison (Eyes Open vs. Closed)")
    codice_paziente=st.text_input("Enter patient ID:", placeholder="es: NLS456")

    if codice_paziente:
        syn = synapseclient.Synapse()
        syn.login(authToken=st.session_state.auth_token)
        PD_mov = 'syn61370558'
        
        with st.spinner("Processing..."):
            files = list(syn.getChildren(PD_mov)) # Prende la lista dei file dentro la cartella
            paziente = [child['name'] for child in files]
            file_scelti = [f for f in paziente if codice_paziente in f] # Filtra i file che contengono l'ID inserito
   
            if file_scelti:
                balance_file = file_scelti[0] # prendiamo solo il primo file trovato per quel paziente = balance
                match = [c['id'] for c in files if c['name'] == balance_file]  #cerchiamo il rispettivo ID Synapse per il download
                if match: 
                    file_id = match[0] 
                    entità = syn.get(file_id) # syn.get serve a "leggere" il file per aprirlo in Pandas
                    df_paziente = pd.read_csv(entità.path, sep=",")
                    st.session_state.df_selezionato = df_paziente # Salviamo il dataframe in session_state per i grafici
                    st.session_state.paziente_corrente = balance_file
                   
                    st.write("...")
                    df_valido = df_paziente [df_paziente ["GeneralEvent"] != "unlabeled"]
                    #occhi aperti
                    df_EO = df_valido[df_valido["GeneralEvent"] == "EO_FeetShoWidth"]
                    df_EO = df_EO.copy()  #usiamo .copy() per evitare il Warning di Pandas quando creiamo nuove colonne
                    df_EO["ML"] = (df_EO["RCoP_X"] + df_EO["LCoP_X"]) / 2
                    df_EO["AP"] = (df_EO["RCoP_Y"] + df_EO["LCoP_Y"]) / 2
                    #occhi chiusi
                    df_EC = df_valido[df_valido["GeneralEvent"] == "EC_FeetShoWidth"]
                    df_EC = df_EC.copy()
                    df_EC["ML"] = (df_EC["RCoP_X"] + df_EC["LCoP_X"]) / 2
                    df_EC["AP"] = (df_EC["RCoP_Y"] + df_EC["LCoP_Y"]) / 2
                    df_EO["Legend:"] = "Eyes Open" #etichetta per legenda
                    df_EC["Legend:"] = "Eyes Close"
                    df_COP = pd.concat([df_EO, df_EC], ignore_index = True)
                    fig = px.line(df_COP, x = "ML", y = "AP", color = "Legend:", labels={"ML": "CoP in ML direction", "AP": "CoP in AP direction"})
                    st.plotly_chart(fig)
            else:
                st.error("ID not found for the selected patient.")









# def momenti_contatto(file): #serve per creare un sottofile con solo la riga e colonne di interesse (cioè colonna del tempo e righe in cui il valore cambia da 0 a 1 o da 1 a 0)
#     appoggio_o_salita_sx=[]
#     appoggio_o_salita_dx=[]
#     diff_sx = file["L Foot Contact"].diff() #.diff() è una funzione che sottrae il valore della riga precedente da quello della riga attuale permettendo di trovare i fronti di salita e discesa in un segnale binario
#     diff_dx= file["R Foot Contact"].diff()
#     file['Time']=file['Time'].str.replace("sec","").astype(float)
#     for i in range(len(file)):
#         if diff_sx.iloc[i]==1:
#             appoggio_o_salita_sx.append({"Time":file['Time'].iloc[i],"appoggio o salita":1})
#         else:
#             appoggio_o_salita_sx.append({"Time":file['Time'].iloc[i],"appoggio o salita":0}) 
#     for i in range(len(file)):
#         if diff_dx.iloc[i]==1:
#             appoggio_o_salita_dx.append({"Time":file['Time'].iloc[i],"appoggio o salita":1})
#         else:
#             appoggio_o_salita_dx.append({"Time":file['Time'].iloc[i],"appoggio o salita":0}) 
#     return appoggio_o_salita_sx,appoggio_o_salita_dx

# for element in tutti_file: 
#     if ("HurriedPace" in element['name'])and("_mat" not in element['name']):
#         file_selezionati.append(element)
# if file_selezionati: 
#     codice_paziente=st.sidebar.text_input("Inserire il codice paziente", placeholder="es: NLS456")
#     for j in file_selezionati:
#         if codice_paziente in j['name']:
#             entity = syn.get(j['id'], downloadFile=True)
#             open_file = pd.read_csv(entity.path)
#             appoggio_sx,appoggio_dx=momenti_contatto(open_file)
#             df_sx=pd.DataFrame(appoggio_sx)
#             df_dx=pd.DataFrame(appoggio_dx)

