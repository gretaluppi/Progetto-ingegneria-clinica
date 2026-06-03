import synapseclient
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import synapseutils

st.set_page_config(page_title="Variabili Movimento", page_icon="👟", layout="wide")

# LOGIN CHECK
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("⚠️ Please log in from the Homepage.")
    st.stop()

st.title("Movements metrics")
st.divider()
def calcolo_UPDRS(lis1,lis2,lis3,lis4):
    somma_finale=0
    Lista1_num = pd.to_numeric(pd.Series(Lista1), errors="coerce")
    Lista2_num = pd.to_numeric(pd.Series(Lista2), errors="coerce")
    Lista3_num = pd.to_numeric(pd.Series(Lista3), errors="coerce")
    Lista4_num = pd.to_numeric(pd.Series(Lista4), errors="coerce")
    if not (Lista1_num.isna().any() or Lista2_num.isna().any() or Lista3_num.isna().any() or Lista4_num.isna().any()):
        Parte1 = sum(Lista1_num)
        Parte2 = sum(Lista2_num)
        Parte3 = sum(Lista3_num)
        Parte4 = sum(Lista4_num)
        somma_finale = Parte1 + Parte2 + Parte3 + Parte4
    else:
        somma_finale=-1
    return somma_finale

def calcola_velocita_medie_gruppo(folder_id, max_pazienti=50):
    all_files = list(syn.getChildren(folder_id))
    file_selezionati=[]
    paz = []
    i=0 # lo uso per tenere traccia di quanti pazienti ho raccolto
    for f in all_files:
        if ("SelfPace" in f['name']) and ("_mat" not in f['name']) and (i<50):
            p_id = f['name'][:6]
            if p_id not in paz:
                paz.add(p_id) #lo uso per controllare di non aver già preso il paziente
                f['id']=p_id #aggiungo al dizionario con le info del file anche l'id del paziente
                file_selezionati.append(f) #aggiungo alla lista contenente solo i file selezionati il nuvo dizionario contenente le info del file
                i=+1 # incremento l'indice così segno di aver preso l'i-esimo paziente
        
    velocita_medie_pazienti = []
    for element in file_selezionati: 
        entita = syn.get(element['id'])
        df_singolo = pd.read_csv(entita.path, sep=",")
        cols_minuscolo = [c.lower() for c in df_singolo.columns] #converte tutti i nomi delle colonne con caratteri tutti minuscoli -> è più facile fare ricerca
        nome_colonna_acc = None 
        nome_colonna_time= None
        for colonna in df_singolo.columns:
            if "time" in colonna.lower():
                nome_colonna_time=colonna
            if "lowerback_freeacc_n" in colonna.lowe():
                nome_colonna_acc = colonna
        
        #riprendi da qui

        
        # controllo se esiste la colonna time
            if nome_colonna_acc is not None:

                tempi = df_singolo[nome_colonna_time]
                accelerazioni = df_singolo[nome_colonna_acc]

                lista_tempi = []
                lista_accelerazioni = []

                # sistemo i valori uno alla volta
                for i in range(len(df_singolo)):
                    tempo = str(tempi.iloc[i])
                    tempo = tempo.replace("sec", "")
                    tempo = tempo.strip()

                    try:
                        tempo_numero = float(tempo)
                        acc_numero = float(accelerazioni.iloc[i])

                        lista_tempi.append(tempo_numero)
                        lista_accelerazioni.append(acc_numero)

                    except:
                        # se un valore non si può convertire, lo salto
                        pass

                df_paz = pd.DataFrame()
                df_paz["Time"] = lista_tempi
                df_paz["Acc"] = lista_accelerazioni

                df_paz = df_paz.sort_values("Time")
                df_paz = df_paz.reset_index(drop=True)

                if len(df_paz) > 0:

                    delta_t = []
                    velocita = []

                    velocita_corrente = 0

                    for i in range(len(df_paz)):

                        if i == 0:
                            differenza_tempo = 0
                        else:
                            tempo_attuale = df_paz["Time"].iloc[i]
                            tempo_prima = df_paz["Time"].iloc[i - 1]
                            differenza_tempo = tempo_attuale - tempo_prima

                        delta_t.append(differenza_tempo)

                        acc_attuale = df_paz["Acc"].iloc[i]

                        velocita_corrente = velocita_corrente + acc_attuale * differenza_tempo
                        velocita.append(velocita_corrente)

                    df_paz["delta_t"] = delta_t
                    df_paz["velocita"] = velocita

                    media_velocita = df_paz["velocita"].mean()
                    media_velocita = abs(media_velocita)

                    velocita_medie_pazienti.append(media_velocita)

    return velocita_medie_pazienti

tab1, tab2 = st.tabs(["Balance", "Selfpace"])
syn = synapseclient.Synapse()
syn.login(authToken=st.session_state.auth_token)
PD_mov = 'syn61370558'
with tab1:  #1. grafico del CoP del paziente i in balance con occhi aperti vs chiusi
    opzioni = st.radio("**Choose one option:**",options=["One specific patient", "Two specific patients"],index=0)
    if opzioni == "One specific patient":
        codice_paziente = st.text_input("Enter PD patient ID:", placeholder = "es: NLS456")
        if codice_paziente:
            with st.spinner("Processing..."):
                files = list(syn.getChildren(PD_mov)) # Prende la lista dei file dentro la cartella direttamente da synaps
                paziente = [child['name'] for child in files]
                file_scelti = [f for f in paziente if codice_paziente in f] # Filtra i file che contengono l'ID inserito
   
                if file_scelti:
                    for element in file_scelti: 
                        if "Balance" in element['name']:
                            balance_file = element['name'] # prendiamo solo il primo file trovato per quel paziente = balance
                    match = [c['id'] for c in files if c['name'] == balance_file]  # mi crea una lista di ID dei file su synapse, li userò per ricostruire il percorso da fare per arrivare al file che mi serve
                    if match: 
                        entità = syn.get(match[0]) # syn.get serve a "leggere" il file per aprirlo in Pandas
                                                    # scrivo match[0] perchè la funzione syn.get necessita di una stringa in ingresso e match è una lista di stringhe
                                                    # che normalmente dovrebbe contenere solamente un valore
                        df_paziente = pd.read_csv(entità.path, sep=",") # vado a leggere il file che ha l'ID che ho trovato
                        st.session_state.df_selezionato = df_paziente # Salviamo il dataframe in session_state per i grafici
                        st.session_state.paziente_corrente = balance_file # uso session.state per permettermi di usare questa variabile anche in altri pannlli/in altre circostanze all'interno dello stesso pannello (titoli o scritte)
                        st.subheader("Patient Balance: CoP comparison (Eyes Open vs. Eyes Closed)")
                        eo=[]
                        ec=[]
                        for i,row in df_paziente.iterrows(): 
                            if row["GeneralEvent"] != "unlabeled":
                                if row["GeneralEvent"]=="EC_FeetShoWidth": 
                                    ec.append({"LCoP_X":row["LCoP_X"], "LCoP_Y":row["LCoP_X"],"RCoP_X":row["RCoP_X"],"RCoP_Y":row["RCoP_Y"]})
                                if row["GeneralEvent"]=="EO_FeetShoWidth":
                                    eo.append({"LCoP_X":row["LCoP_X"], "LCoP_Y":row["LCoP_X"],"RCoP_X":row["RCoP_X"],"RCoP_Y":row["RCoP_Y"]})
                        df_EO=pd.DataFrame(eo)
                        df_EC=pd.DataFrame(ec)
                        #occhi aperti
                        df_EO = df_EO.copy()  #usiamo .copy() per evitare il Warning di Pandas quando creiamo nuove colonne
                        df_EO["ML"] = (df_EO["RCoP_X"] + df_EO["LCoP_X"]) / 2
                        df_EO["AP"] = (df_EO["RCoP_Y"] + df_EO["LCoP_Y"]) / 2
                        #occhi chiusi
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
            with st.spinner("Processing..."):
                files= list(syn.getChildren(PD_mov)) # Prende la lista dei file dentro la cartella
                paz= [child['name'] for child in files] #prende i nomi di tutti i pazienti
                file_scelti_1 = [f for f in paz if codice_paz1 in f] # Filtra i file che contengono l'ID inserit
                file_scelti_2 = [f for f in paz if codice_paz2 in f] 

                if file_scelti_1 and file_scelti_2:
                    for element in file_scelti_1: 
                        if "Balance" in element['name']:
                            balance_1 = element['name'] # prendiamo solo il primo file trovato per quel paziente = balance
                    match_1 = [c['id'] for c in files if c['name'] == balance_1]  #cerchiamo il rispettivo ID Synapse per il download
                    for element in file_scelti_2: 
                        if "Balance" in element['name']:
                            balance_2 = element['name'] 
                    match_2 = [c['id'] for c in files if c['name'] == balance_2] 

                    if match_1 and match_2:  
                        entità_1= syn.get(match_1[0]) # syn.get serve a "leggere" il file per aprirlo in Pandas
                        df_paz1 = pd.read_csv(entità_1.path, sep=",")
                        st.session_state.df_selezionato = df_paz1 # Salviamo il dataframe in session_state per i grafici
                        st.session_state.paziente_corrente = balance_1

                        entità_2= syn.get(match_2[0]) # syn.get serve a "leggere" il file per aprirlo in Pandas
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
                        #preparo il dataframe del paziente 1
                        eo1=[]
                        for i,row in df_paz1.iterrows(): 
                            if row["GeneralEvent"] != "unlabeled":
                                if row["GeneralEvent"]=="EO_FeetShoWidth":
                                    eo1.append({"LCoP_X":row["LCoP_X"], "LCoP_Y":row["LCoP_X"],"RCoP_X":row["RCoP_X"],"RCoP_Y":row["RCoP_Y"]})
                        df_EO1=pd.DataFrame(eo1)
                        #preparo il dataframe del paziente 2
                        eo2=[]
                        for i,row in df_paz1.iterrows(): 
                            if row["GeneralEvent"] != "unlabeled":
                                if row["GeneralEvent"]=="EO_FeetShoWidth":
                                    eo2.append({"LCoP_X":row["LCoP_X"], "LCoP_Y":row["LCoP_X"],"RCoP_X":row["RCoP_X"],"RCoP_Y":row["RCoP_Y"]})
                        df_EO2=pd.DataFrame(eo2)
                        df_1 = df_EO1.copy()
                        df_1["ML"] = (df_1["RCoP_X"] + df_1["LCoP_X"]) / 2
                        df_1["AP"] = (df_1["RCoP_Y"] + df_1["LCoP_Y"]) / 2
                        #grafico PD2
                        df_2 = df_EO2.copy()
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