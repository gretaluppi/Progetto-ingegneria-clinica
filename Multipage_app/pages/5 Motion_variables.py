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
#UPDRS
def calcolo_UPDRS(lis1,lis2,lis3,lis4):
        somma_finale=0
        Lista1_num = pd.to_numeric(pd.Series(lis1), errors="coerce")
        Lista2_num = pd.to_numeric(pd.Series(lis2), errors="coerce")
        Lista3_num = pd.to_numeric(pd.Series(lis3), errors="coerce")
        Lista4_num = pd.to_numeric(pd.Series(lis4), errors="coerce")
        if not (Lista1_num.isna().any() or Lista2_num.isna().any() or Lista3_num.isna().any() or Lista4_num.isna().any()):
            Parte1 = sum(Lista1_num)
            Parte2 = sum(Lista2_num)
            Parte3 = sum(Lista3_num)
            Parte4 = sum(Lista4_num)
            somma_finale = Parte1 + Parte2 + Parte3 + Parte4
        else:
            somma_finale=-1
        return somma_finale

st.title("Movements metrics")
st.divider()
st.write("TESTO ANCORA DA SCRIVERE ...")

tab1, tab2 = st.tabs(["Balance", "Selfpace"])

with tab1:  #1. grafico del CoP del paziente i in balance con occhi aperti vs chiusi
    opzioni = st.radio(
    "**Choose one option:**",
    options=["One specific patient", "Two specific patients"],
    index=0
    )
    if opzioni == "One specific patient":
        codice_paziente = st.text_input("Enter PD patient ID:", placeholder = "es: NLS456")
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

                        st.subheader("Patient Balance: CoP comparison (Eyes Open vs. Eyes Closed)")
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
                        df_COP = pd.concat([df_EC, df_EO], ignore_index = True)
                        fig = px.line(df_COP, x = "ML", y = "AP", color = "Legend:", labels={"ML": "CoP in ML direction", "AP": "CoP in AP direction"})
                        st.plotly_chart(fig)
                else:
                    st.error("ID not found for the selected patient.")
    else: 
        codice_paz1= st.text_input("Enter PD patient one ID:", placeholder = "es: NLS456")
        codice_paz2 = st.text_input("Enter PD patient two ID:", placeholder = "es: NLS456")
        if codice_paz1 and codice_paz2:
            syn = synapseclient.Synapse()
            syn.login(authToken=st.session_state.auth_token)
            PD_mov = 'syn61370558'

            with st.spinner("Processing..."):
                files_1 = list(syn.getChildren(PD_mov)) # Prende la lista dei file dentro la cartella
                paz_1 = [child['name'] for child in files_1]
                file_scelti_1 = [f for f in paz_1 if codice_paz1 in f] # Filtra i file che contengono l'ID inserito
                
                files_2 = list(syn.getChildren(PD_mov))
                paz_2 = [child['name'] for child in files_2]
                file_scelti_2 = [f for f in paz_2 if codice_paz2 in f] 

                if file_scelti_1 and file_scelti_2:
                    balance_1 = file_scelti_1[0] # prendiamo solo il primo file trovato per quel paziente = balance
                    match_1 = [c['id'] for c in files_1 if c['name'] == balance_1]  #cerchiamo il rispettivo ID Synapse per il download
                    
                    balance_2 = file_scelti_2[0] 
                    match_2 = [c['id'] for c in files_2 if c['name'] == balance_2] 

                    if match_1 and match_2: 
                        file_1id = match_1[0] 
                        entità_1= syn.get(file_1id) # syn.get serve a "leggere" il file per aprirlo in Pandas
                        df_paz1 = pd.read_csv(entità_1.path, sep=",")
                        st.session_state.df_selezionato = df_paz1 # Salviamo il dataframe in session_state per i grafici
                        st.session_state.paziente_corrente = balance_1

                        file_2id = match_2[0] 
                        entità_2= syn.get(file_2id) # syn.get serve a "leggere" il file per aprirlo in Pandas
                        df_paz2 = pd.read_csv(entità_2.path, sep=",")
                        st.session_state.df_selezionato = df_paz2 # Salviamo il dataframe in session_state per i grafici
                        st.session_state.paziente_corrente = balance_2
                        #st.success("OK")

                        #calcolo UPDRS per capire chi tra i 2 pazienti è più grave
                        df_pd = pd.read_csv("PD.csv", sep="," , header=1)
                        df_pd["UPDRS"] = None
                        for i, row in df_pd.iterrows():
                            Lista1 = [row["MDSUPDRS_1-1"], row["MDSUPDRS_1-2"], row["MDSUPDRS_1-3"], row["MDSUPDRS_1-4"], row["MDSUPDRS_1-5"], row["MDSUPDRS_1-6"], row["MDSUPDRS_1-7"], row["MDSUPDRS_1-8"], row["MDSUPDRS_1-9"], row["MDSUPDRS_1-10"], row["MDSUPDRS_1-11"], row["MDSUPDRS_1-12"], row["MDSUPDRS_1-13"]]
                            Lista2 = [row["MDSUPDRS_2-1"], row["MDSUPDRS_2-2"], row["MDSUPDRS_2-3"], row["MDSUPDRS_2-4"], row["MDSUPDRS_2-5"], row["MDSUPDRS_2-6"], row["MDSUPDRS_2-7"], row["MDSUPDRS_2-8"], row["MDSUPDRS_2-9"], row["MDSUPDRS_2-10"], row["MDSUPDRS_2-11"], row["MDSUPDRS_2-12"], row["MDSUPDRS_2-13"]]
                            Lista3 = [row["MDSUPDRS_3-1"], row["MDSUPDRS_3-2"], row["MDSUPDRS_3-3-Neck"], row["MDSUPDRS_3-3-RUE"], row["MDSUPDRS_3-3-LLE"], row["MDSUPDRS_3-4-R"], row["MDSUPDRS_3-4-L"], row["MDSUPDRS_3-5-R"], row["MDSUPDRS_3-5-L"], row["MDSUPDRS_3-6-R"], row["MDSUPDRS_3-6-L"], row["MDSUPDRS_3-7-R"], row["MDSUPDRS_3-7-L"], row["MDSUPDRS_3-8-R"], row["MDSUPDRS_3-8-L"], row["MDSUPDRS_3-9"], row["MDSUPDRS_3-10"], row["MDSUPDRS_3-11"], row["MDSUPDRS_3-12"], row["MDSUPDRS_3-13"], row["MDSUPDRS_3-14"], row["MDSUPDRS_3-15-R"], row["MDSUPDRS_3-15-L"], row["MDSUPDRS_3-16-L"], row["MDSUPDRS_3-16-R"], row["MDSUPDRS_3-17-RUE"], row["MDSUPDRS_3-17-LUE"], row["MDSUPDRS_3-17-RLE"], row["MDSUPDRS_3-17-LLE"], row["MDSUPDRS_3-17-LipJaw"], row["MDSUPDRS_3-18"]]
                            Lista4 = [row["MDSUPDRS_4-1"], row["MDSUPDRS_4-2"], row["MDSUPDRS_4-3"], row["MDSUPDRS_4-4"], row["MDSUPDRS_4-5"], row["MDSUPDRS_4-6"]]
                            UPDRS=calcolo_UPDRS(Lista1,Lista2,Lista3,Lista4)
                            if UPDRS >=0:
                                df_pd.at[i,"UPDRS"] = UPDRS
                        
                        # Estraiamo direttamente il valore. Se non esiste, usiamo "N/A" come fallback.
                        val_updrs1 = df_pd.loc[df_pd["Subject ID"] == codice_paz1, "UPDRS"].to_list() or ["N/A"]
                        val_updrs2 = df_pd.loc[df_pd["Subject ID"] == codice_paz2, "UPDRS"].to_list() or ["N/A"]
                        val_updrs1 = val_updrs1[0]
                        val_updrs2 = val_updrs2[0]

                        #consideriamo occhi aperti sempre !!
                        st.subheader("Patients Balance: CoP comparison btween two PD patients")
                        #grafico PD1
                        df_valido_1 = df_paz1[df_paz1["GeneralEvent"] != "unlabeled"]
                        df_1 = df_valido_1[df_valido_1["GeneralEvent"] == "EO_FeetShoWidth"]
                        df_1 = df_1.copy()
                        df_1["ML"] = (df_1["RCoP_X"] + df_1["LCoP_X"]) / 2
                        df_1["AP"] = (df_1["RCoP_Y"] + df_1["LCoP_Y"]) / 2
                        #grafico PD2
                        df_valido_2 = df_paz2[df_paz2["GeneralEvent"] != "unlabeled"]
                        df_2 = df_valido_2[df_valido_2["GeneralEvent"] == "EO_FeetShoWidth"]
                        df_2 = df_2.copy()
                        df_2["ML"] = (df_2["RCoP_X"] + df_2["LCoP_X"]) / 2
                        df_2["AP"] = (df_2["RCoP_Y"] + df_2["LCoP_Y"]) / 2
                        df_1["Legend:"] = codice_paz1
                        df_1["UPDRS"] = val_updrs1
                        df_2["Legend:"] = codice_paz2
                        df_2["UPDRS"] = val_updrs2
                        df_COP = pd.concat([df_1, df_2], ignore_index = True)
                        fig = px.line(df_COP, x = "ML", y = "AP", color = "Legend:", hover_data = ["UPDRS"], labels={"ML": "CoP in ML direction", "AP": "CoP in AP direction"})
                        st.plotly_chart(fig)
                else:
                    st.error("ID not found for the selected patient.")

with tab2:
    st.subheader("PD vs. CONTROLS CoP (General Trend)")
    

#  codice_paz_PD = st.text_input("Enter PD patient ID:", placeholder = "es: NLS456")
#         codice_paz_CON = st.text_input("Enter CONTROL patient ID:", placeholder = "es: HC123")
#         if codice_paz_PD and codice_paz_CON:
#             syn = synapseclient.Synapse()
#             syn.login(authToken=st.session_state.auth_token)
#             PD_mov = 'syn61370558'
#             CON_mov = 'syn61370552'

#             with st.spinner("Processing..."):
#                 files_PD = list(syn.getChildren(PD_mov)) # Prende la lista dei file dentro la cartella
#                 paz_PD = [child['name'] for child in files_PD]
#                 file_scelti_PD = [f for f in paz_PD if codice_paz_PD in f] # Filtra i file che contengono l'ID inserito
                
#                 files_CON = list(syn.getChildren(CON_mov))
#                 paz_CON = [child['name'] for child in files_CON]
#                 file_scelti_CON = [f for f in paz_CON if codice_paz_CON in f] 

#                 if file_scelti_PD and file_scelti_CON:
#                     balance_PD = file_scelti_PD[0] # prendiamo solo il primo file trovato per quel paziente = balance
#                     match_PD = [c['id'] for c in files_PD if c['name'] == balance_PD]  #cerchiamo il rispettivo ID Synapse per il download
                    
#                     balance_CON = file_scelti_CON[0] 
#                     match_CON = [c['id'] for c in files_CON if c['name'] == balance_CON] 

#                     if match_PD and match_CON: 
#                         file_PDid = match_PD[0] 
#                         entità_PD= syn.get(file_PDid) # syn.get serve a "leggere" il file per aprirlo in Pandas
#                         df_pazPD = pd.read_csv(entità_PD.path, sep=",")
#                         st.session_state.df_selezionato = df_pazPD # Salviamo il dataframe in session_state per i grafici
#                         st.session_state.paziente_corrente = balance_PD

#                         file_CONid = match_CON[0] 
#                         entità_CON= syn.get(file_CONid) # syn.get serve a "leggere" il file per aprirlo in Pandas
#                         df_pazCON = pd.read_csv(entità_CON.path, sep=",")
#                         st.session_state.df_selezionato = df_pazCON # Salviamo il dataframe in session_state per i grafici
#                         st.session_state.paziente_corrente = balance_CON
#                         st.success("OK")

#                         #consideriamo occhi aperti sempre !!
#                         st.subheader("Patients Balance: CoP comparison (PD vs. CONTROL)")
#                         #grafico PD
#                         df_valido_PD = df_pazPD[df_pazPD["GeneralEvent"] != "unlabeled"]
#                         df_PD = df_valido_PD[df_valido_PD["GeneralEvent"] == "EO_FeetShoWidth"]
#                         df_PD = df_PD.copy()
#                         df_PD["ML"] = (df_PD["RCoP_X"] + df_PD["LCoP_X"]) / 2
#                         df_PD["AP"] = (df_PD["RCoP_Y"] + df_PD["LCoP_Y"]) / 2
#                         #grafico CONTROLLI
#                         df_valido_CON = df_pazCON[df_pazCON["GeneralEvent"] != "unlabeled"]
#                         df_CON = df_valido_CON[df_valido_CON["GeneralEvent"] == "EO_FeetShoWidth"]
#                         df_CON = df_CON.copy()
#                         df_CON["ML"] = (df_CON["RCoP_X"] + df_CON["LCoP_X"]) / 2
#                         df_CON["AP"] = (df_CON["RCoP_Y"] + df_CON["LCoP_Y"]) / 2
#                         df_PD["Legend:"] = "PD"
#                         df_CON["Legend:"] = "CONTROL"
#                         df_COP = pd.concat([df_PD, df_CON], ignore_index = True)
#                         fig = px.line(df_COP, x = "ML", y = "AP", color = "Legend:", labels={"ML": "CoP in ML direction", "AP": "CoP in AP direction"})
#                         st.plotly_chart(fig)
#                 else:
#                     st.error("ID not found for the selected patient.")





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

