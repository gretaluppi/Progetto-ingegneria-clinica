#st.set_page_config(page_title="Variabili Movimento", page_icon="👟", layout="wide")

import synapseclient
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import synapseutils


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
                        
                        val_updrs1 = df_pd.loc[df_pd["Subject ID"] == codice_paz1, "UPDRS"].to_list() or ["N/A"]  # estraiamo direttamente il valore, se non esiste usiamo "N/A" come fallback.
                        val_updrs2 = df_pd.loc[df_pd["Subject ID"] == codice_paz2, "UPDRS"].to_list() or ["N/A"]
                        val_updrs1 = val_updrs1[0]
                        val_updrs2 = val_updrs2[0]

                        #consideriamo occhi aperti sempre !!
                        st.subheader("Patients Balance: CoP comparison between two PD patients")
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
    st.subheader("PD vs. CONTROLS (Average speed)")
    syn = synapseclient.Synapse()
    syn.login(authToken=st.session_state.auth_token)
    PD_mov = 'syn61370558'
    CON_mov = 'syn61370552'
    
    def calcola_velocita_medie_gruppo(folder_id, max_pazienti=50):
        all_files = list(syn.getChildren(folder_id))
        paz_dict = {}
        for f in all_files:
            nome = f['name']
            p_id = nome[:6]
            if p_id not in paz_dict:
                paz_dict[p_id] = []
            paz_dict[p_id].append(f)
        
        velocita_medie_pazienti = []
        pazienti_selezionati = list(paz_dict.items())[:max_pazienti]
        
        for p_id, files in pazienti_selezionati:
            files = sorted(files, key=lambda x: x['name'])
            if len(files) >= 4:
                selfpace_file = files[3]
                entita = syn.get(selfpace_file['id'])
                df_singolo = pd.read_csv(entita.path, sep=",")
                
                cols_totali = [c.lower() for c in df_singolo.columns]
                
                if "time" in cols_totali:
                    time_col_exact = df_singolo.columns[cols_totali.index("time")]
                    
                    acc_col_exact = None
                    for c in df_singolo.columns:
                        if "lowerback_freeacc_n" in c.lower():
                            acc_col_exact = c
                            break
                    
                    if acc_col_exact:
                        # ATTENZIONE: rimuvere dal testo "sec" poi fare conversione numerica
                        t_pulito = df_singolo[time_col_exact].astype(str).str.replace("sec", "", case=False).str.strip()
                        t_numeric = pd.to_numeric(t_pulito, errors='coerce')
                        a_numeric = pd.to_numeric(df_singolo[acc_col_exact], errors='coerce')
                        
                        df_paz = pd.DataFrame({"Time": t_numeric, "Acc": a_numeric}).dropna().sort_values("Time").reset_index(drop=True)
                        
                        if not df_paz.empty:
                            df_paz["delta_t"] = df_paz["Time"].diff().fillna(0)
                            df_paz["velocita"] = (df_paz["Acc"] * df_paz["delta_t"]).cumsum()
                            
                            # Calcolo del modulo della velocità media
                            velocita_medie_pazienti.append(abs(df_paz["velocita"].mean()))                
        return velocita_medie_pazienti
   
    with st.spinner("Processing..."):
        vel_PD = calcola_velocita_medie_gruppo(PD_mov, max_pazienti=50)
        vel_CON = calcola_velocita_medie_gruppo(CON_mov, max_pazienti=50)

    # Controllo sicurezza
    if not vel_PD and not vel_CON:
        st.error("Error")
        st.stop()


    fig_box_swarm = go.Figure()
    if vel_PD:    #PD BOX
        fig_box_swarm.add_trace(go.Box(
            y=vel_PD,
            name="PD",
            boxmean=True,
            line=dict(color="#4A90D9"),
            fillcolor="rgba(74,144,217,0.3)"
        ))

        fig_box_swarm.add_trace(go.Scatter( #PD SWARM
            x=["PD"] * len(vel_PD),
            y=vel_PD,
            mode="markers",
            marker=dict(
                size=7,
                color="#1f5fbf",
                opacity=0.8
            ),
            showlegend=False
        ))

    if vel_CON: # CONTROLS BOX 
        fig_box_swarm.add_trace(go.Box(
            y=vel_CON,
            name="Controls",
            boxmean=True, 
            line=dict(color="#E8729A"),
            fillcolor="rgba(232,114,154,0.3)"
        ))

        fig_box_swarm.add_trace(go.Scatter(    # CONTROLS SWARM
            x=["Controls"] * len(vel_CON),
            y=vel_CON,
            mode="markers",
            marker=dict(
                size=7,
                color="#c2185b",
                opacity=0.8
            ),
            showlegend=False
        ))

    fig_box_swarm.update_layout(
        title=" ",
        margin=dict(t=40, b=30, l=40, r=40),
        boxmode="overlay", # per sovrapposizione di box e punti
        yaxis=dict(title="Average speed (m/s)", gridcolor="rgba(200, 200, 200, 0.2)"),
        xaxis=dict(title=" "),
        template="plotly_white",
        hovermode=False
    )
    st.plotly_chart(fig_box_swarm, use_container_width=True)