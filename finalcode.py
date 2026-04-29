import synapseclient
import streamlit as st
import pandas as pd
import plotly.express as px
# LOGIN
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

#funzione per calcolare l'UPDRS
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

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
    st.stop()

#lettura dei due file csv 
df_control = pd.read_csv("CONTROLS.csv", sep="," , header=1)
df_pd = pd.read_csv("PD.csv", sep="," , header=1)

# IMPOSTAZIONE PAGINA
st.title("ANALISI DATI PARKINSON")

if "show_filters" not in st.session_state:
    st.session_state.show_filters = False

if st.sidebar.button("Parametri di ricerca"):
    st.session_state.show_filters = True

if st.session_state.show_filters:
    scelta_parametri=st.sidebar.multiselect("Selezionare parametri",["Genere", "Età", "UPDRS", "Prova","Tempo di appoggio"])
    soggetti_selezionati_genere=[]
    soggetti_selezionati_eta=[]
    soggetti_selezionati_UPDRS=[]
    soggetti_selezionati_prova=[]
    soggetti_selezionati_finale=[]
    if "Genere" in scelta_parametri: 
        # ______________________
        # FILTRO PER GENERE - Ale
        # ______________________
        st.sidebar.header("Analisi per genere:")
        selezione_genere=st.sidebar.selectbox("Scegliere il genere:", ["Uomo","Donna"])
        if selezione_genere == "Uomo": 
            for i,row in df_pd.iterrows(): 
                if row["Gender"] == "Male":
                    soggetti_selezionati_genere.append ({"Subject ID":row["Subject ID"], "Gender":row["Gender"]})
        if selezione_genere == "Donna":
            for i,row in df_pd.iterrows():
                if row["Gender"]== "Female":
                    soggetti_selezionati_genere.append ({"Subject ID":row["Subject ID"], "Gender":row["Gender"]})
    else: 
        for i,row in df_pd.iterrows(): 
            soggetti_selezionati_genere.append ({"Subject ID":row["Subject ID"], "Gender":row["Gender"]})

    if "Età" in scelta_parametri: 
        # ______________________
        # FILTRO PER ETA' - Gre
        # ______________________
        st.sidebar.header("analisi per età")
        selezione_eta=st.sidebar.selectbox("scegliere un'opzione", ["range di età","età precisa"])
        if selezione_eta == "range di età": 
            age_min,age_max=st.sidebar.slider("selezionare un range di eta", 0, 110, (0,100)) 
            for i,row in df_pd.iterrows():
                for element in soggetti_selezionati_genere:
                    if ((row["Age (years)"]<=age_max and row["Age (years)"]>=age_min) and (element["Subject ID"] == row["Subject ID"])):
                        soggetti_selezionati_eta.append({"Subject ID":element["Subject ID"], "Gender":element["Gender"], "Age": row["Age (years)"]})
        if selezione_eta == "età precisa":
            age=st.sidebar.number_input("selezionare un età", 0, 110, 50, 1)
            for i,row in df_pd.iterrows():
                for element in soggetti_selezionati_genere:
                    if (row["Age (years)"]==age) and (element["Subject ID"]==row["Subject ID"]):
                        soggetti_selezionati_eta.append({"Subject ID":element["Subject ID"], "Gender":element["Gender"], "Age": row["Age (years)"]})
    else: 
        for i,row in df_pd.iterrows():
            for element in soggetti_selezionati_genere:
                if row["Subject ID"] == element["Subject ID"]:
                    soggetti_selezionati_eta.append({"Subject ID":element["Subject ID"], "Gender":element["Gender"], "Age": row["Age (years)"]})
    
    
    if "UPDRS" in scelta_parametri:
        st.sidebar.header("analisi UPDRS")
        options = st.sidebar.multiselect("Range UPDRS",["Lieve (0-32)", "Moderato (33-58)", "Severo (59-102)", "Grave (> 103)"],)
        for i, row in df_pd.iterrows():
            Lista1 = [row["MDSUPDRS_1-1"], row["MDSUPDRS_1-2"], row["MDSUPDRS_1-3"], row["MDSUPDRS_1-4"], row["MDSUPDRS_1-5"], row["MDSUPDRS_1-6"], row["MDSUPDRS_1-7"], row["MDSUPDRS_1-8"], row["MDSUPDRS_1-9"], row["MDSUPDRS_1-10"], row["MDSUPDRS_1-11"], row["MDSUPDRS_1-12"], row["MDSUPDRS_1-13"]]
            Lista2 = [row["MDSUPDRS_2-1"], row["MDSUPDRS_2-2"], row["MDSUPDRS_2-3"], row["MDSUPDRS_2-4"], row["MDSUPDRS_2-5"], row["MDSUPDRS_2-6"], row["MDSUPDRS_2-7"], row["MDSUPDRS_2-8"], row["MDSUPDRS_2-9"], row["MDSUPDRS_2-10"], row["MDSUPDRS_2-11"], row["MDSUPDRS_2-12"], row["MDSUPDRS_2-13"]]
            Lista3 = [row["MDSUPDRS_3-1"], row["MDSUPDRS_3-2"], row["MDSUPDRS_3-3-Neck"], row["MDSUPDRS_3-3-RUE"], row["MDSUPDRS_3-3-LLE"], row["MDSUPDRS_3-4-R"], row["MDSUPDRS_3-4-L"], row["MDSUPDRS_3-5-R"], row["MDSUPDRS_3-5-L"], row["MDSUPDRS_3-6-R"], row["MDSUPDRS_3-6-L"], row["MDSUPDRS_3-7-R"], row["MDSUPDRS_3-7-L"], row["MDSUPDRS_3-8-R"], row["MDSUPDRS_3-8-L"], row["MDSUPDRS_3-9"], row["MDSUPDRS_3-10"], row["MDSUPDRS_3-11"], row["MDSUPDRS_3-12"], row["MDSUPDRS_3-13"], row["MDSUPDRS_3-14"], row["MDSUPDRS_3-15-R"], row["MDSUPDRS_3-15-L"], row["MDSUPDRS_3-16-L"], row["MDSUPDRS_3-16-R"], row["MDSUPDRS_3-17-RUE"], row["MDSUPDRS_3-17-LUE"], row["MDSUPDRS_3-17-RLE"], row["MDSUPDRS_3-17-LLE"], row["MDSUPDRS_3-17-LipJaw"], row["MDSUPDRS_3-18"]]
            Lista4 = [row["MDSUPDRS_4-1"], row["MDSUPDRS_4-2"], row["MDSUPDRS_4-3"], row["MDSUPDRS_4-4"], row["MDSUPDRS_4-5"], row["MDSUPDRS_4-6"]]
            UPDRS=calcolo_UPDRS(Lista1,Lista2,Lista3,Lista4)
            for element in soggetti_selezionati_eta:
                if element["Subject ID"]==row["Subject ID"]: 
                    if "Lieve (0-32)" in options:
                        if UPDRS >= 0 and UPDRS <= 32:
                            soggetti_selezionati_UPDRS.append({"Subject ID":element["Subject ID"], "Gender":element["Gender"], "Age": element["Age"],"MDS-UPDRS": str(UPDRS)+"( lieve)"})
                    if "Moderato (33-58)" in options:
                        if UPDRS >= 33 and UPDRS <= 58:
                            soggetti_selezionati_UPDRS.append({"Subject ID":element["Subject ID"], "Gender":element["Gender"], "Age": element["Age"],"MDS-UPDRS": str(UPDRS)+"( moderato)"})                
                    if "Severo (59-102)" in options:
                        if UPDRS >= 59 and UPDRS <= 102:
                            soggetti_selezionati_UPDRS.append({"Subject ID":element["Subject ID"], "Gender":element["Gender"], "Age": element["Age"],"MDS-UPDRS": str(UPDRS)+"( severo)"})
                    if "Grave (> 103)" in options:
                        if UPDRS >= 103:
                            soggetti_selezionati_UPDRS.append({"Subject ID":element["Subject ID"], "Gender":element["Gender"], "Age": element["Age"],"MDS-UPDRS": str(UPDRS)+"( grave)"})
    else:
        for i,row in df_pd.iterrows():
            Lista1 = [row["MDSUPDRS_1-1"], row["MDSUPDRS_1-2"], row["MDSUPDRS_1-3"], row["MDSUPDRS_1-4"], row["MDSUPDRS_1-5"], row["MDSUPDRS_1-6"], row["MDSUPDRS_1-7"], row["MDSUPDRS_1-8"], row["MDSUPDRS_1-9"], row["MDSUPDRS_1-10"], row["MDSUPDRS_1-11"], row["MDSUPDRS_1-12"], row["MDSUPDRS_1-13"]]
            Lista2 = [row["MDSUPDRS_2-1"], row["MDSUPDRS_2-2"], row["MDSUPDRS_2-3"], row["MDSUPDRS_2-4"], row["MDSUPDRS_2-5"], row["MDSUPDRS_2-6"], row["MDSUPDRS_2-7"], row["MDSUPDRS_2-8"], row["MDSUPDRS_2-9"], row["MDSUPDRS_2-10"], row["MDSUPDRS_2-11"], row["MDSUPDRS_2-12"], row["MDSUPDRS_2-13"]]
            Lista3 = [row["MDSUPDRS_3-1"], row["MDSUPDRS_3-2"], row["MDSUPDRS_3-3-Neck"], row["MDSUPDRS_3-3-RUE"], row["MDSUPDRS_3-3-LLE"], row["MDSUPDRS_3-4-R"], row["MDSUPDRS_3-4-L"], row["MDSUPDRS_3-5-R"], row["MDSUPDRS_3-5-L"], row["MDSUPDRS_3-6-R"], row["MDSUPDRS_3-6-L"], row["MDSUPDRS_3-7-R"], row["MDSUPDRS_3-7-L"], row["MDSUPDRS_3-8-R"], row["MDSUPDRS_3-8-L"], row["MDSUPDRS_3-9"], row["MDSUPDRS_3-10"], row["MDSUPDRS_3-11"], row["MDSUPDRS_3-12"], row["MDSUPDRS_3-13"], row["MDSUPDRS_3-14"], row["MDSUPDRS_3-15-R"], row["MDSUPDRS_3-15-L"], row["MDSUPDRS_3-16-L"], row["MDSUPDRS_3-16-R"], row["MDSUPDRS_3-17-RUE"], row["MDSUPDRS_3-17-LUE"], row["MDSUPDRS_3-17-RLE"], row["MDSUPDRS_3-17-LLE"], row["MDSUPDRS_3-17-LipJaw"], row["MDSUPDRS_3-18"]]
            Lista4 = [row["MDSUPDRS_4-1"], row["MDSUPDRS_4-2"], row["MDSUPDRS_4-3"], row["MDSUPDRS_4-4"], row["MDSUPDRS_4-5"], row["MDSUPDRS_4-6"]]
            UPDRS=calcolo_UPDRS(Lista1,Lista2,Lista3,Lista4)
            for element in soggetti_selezionati_eta:
                if row["Subject ID"] == element["Subject ID"]:
                    if UPDRS >=0:
                        soggetti_selezionati_UPDRS.append({"Subject ID":element["Subject ID"], "Gender":element["Gender"], "Age": row["Age (years)"],"MDS-UPDRS": UPDRS})
        
    data_frame_filtrato = pd.DataFrame(soggetti_selezionati_UPDRS)
    st.subheader("Dati filtrati")
    st.dataframe(data_frame_filtrato)
    
#     if "Tempo di appoggio" in scelta_parametri:
#         syn = synapseclient.Synapse()
#         syn.login(authToken=st.session_state.auth_token)
#         folder_file="syn61370558"
#         tutti_file=list(syn.getChildren(folder_file))
#         file_selezionati=[]

#         for element in tutti_file: 
#             if ("HurriedPace" in element['name'])and("_mat" not in element['name']):
#                 file_selezionati.append(element)
#         if file_selezionati: 
#             codice_paziente=st.sidebar.text_input("Inserire il codice paziente", placeholder="es: NLS456")
#             for j in file_selezionati:
#                 if codice_paziente in j:
#                     open_file=pd.DataFrame(j)
#                     appoggio_sx,appoggio_dx=momenti_contatto(open_file,)

                    
# def momenti_contatto(file): #serve per creare un sottofile con solo la riga e colonne di interesse (cioè colonna del tempo e righe in cui il valore cambia da 0 a 1 o da 1 a 0)
#     appoggio_o_salita_sx=[]
#     appoggio_o_salita_dx=[]
#     secondi_sx=0
#     secondi_dx=0
#     for i,row in file.iterrows():
#         diff_sx = file["L Foot Contact"].diff() #.diff() è una funzione che sottrae il valore della riga precedente da quello della riga attuale permettendo di trovare i fronti di salita e discesa in un segnale binario
#         if diff_sx==1:
#             appoggio_o_salita_sx.append({"Time":secondi_sx,"appoggio o salita":1})
#         else:
#             appoggio_o_salita_sx.append({"Time":secondi_sx,"appoggio o salita":0}) 
#         secondi_sx+=0.01
#     for i,row in file.iterrows():
#         diff_dx= file["R Foot Contact"].diff()
#         if diff_dx==1:
#             appoggio_o_salita_dx.append({"Time":secondi_dx,"appoggio o salita":1})
#         else:
#             appoggio_o_salita_dx.append({"Time":secondi_dx,"appoggio o salita":0}) 
#         secondi_dx+=0.01
#     return appoggio_o_salita_sx,appoggio_o_salita_dx


    if "Prova" in scelta_parametri:
    # FILTRO PROVA - Adry___________________
        syn = synapseclient.Synapse()
        syn.login(authToken=st.session_state.auth_token)
        folder_file="syn61370558"
        all_files_in_folder = list(syn.getChildren(folder_file))
        files_disponibili = []
        for child in all_files_in_folder:
            nome_file= str(child['name']).upper()
            for element in soggetti_selezionati_UPDRS:
                if element["Subject ID"] in child['name']:
                    files_disponibili.append(child)
        st.sidebar.header("seleziona tipo di prova")
        selezione_prova=st.sidebar.selectbox("prova eseguita", ["SelfPace","HurriedPace","SelfPace_mat","HurriedPace_mat","SelfPace_matTURN","TandemGait","TUG","Balance","SElfPace_doorpat","FreeWalk"])
        nomi_disponibili = [f['name'] for f in files_disponibili]
        file_scelti = []
        for nome in nomi_disponibili:
            if selezione_prova in nome and (("_mat" in selezione_prova)==("_mat" in nome)) and (("TURN" in selezione_prova)==("TURN" in nome)):
                file_scelti.append(nome)
        if file_scelti:
            file_da_aprire=st.selectbox("seleziona il file del soggetto da analizzare", file_scelti)
            if file_da_aprire:
                match = [c['id'] for c in files_disponibili if c['name'] == file_da_aprire]
                if match:
                    file_id =match[0] 
                    with st.spinner("Caricamento del file..."):
                        entità = syn.get(file_id)
                        df_prova = pd.read_csv(entità.path, sep="," , header=1)
                        st.success(f"File {file_da_aprire} caricato con successo!")
                        st.title(f"analisi: {file_da_aprire}")
                        st.dataframe(df_prova)
                else:
                    st.error("Nessun file trovato per la prova selezionata")
            else:
                st.warning(f"Nessun file trovato per la prova '{selezione_prova}' (esclusi mat e TURN)")
        else:
            st.info("Nessun file disponibile")
    else:
        back=st.sidebar.button("Torna alla ricerca per paziente")
        if back: 
            codice_persona=st.sidebar.text_input("Inserire il codice paziente", placeholder="es: NLS456")


# else: 
#     syn = synapseclient.Synapse()
#     syn.login(authToken=st.session_state.auth_token)
#     folder_file="syn61370558"
#     files=list(syn.getChildren(folder_file))
#     paziente=[child['name'] for child in files]
#     codice_persona=st.sidebar.text_input("Inserire il codice paziente", placeholder="es: NLS456")
#     if codice_persona:
#         file_scelti= [f for f in paziente if codice_persona in f]
#         if file_scelti:
#             file_da_aprire=st.selectbox("seleziona il file del soggetto da analizzare", file_scelti)
#         if file_da_aprire:
#             match = [c['id'] for c in files if c['name'] == file_da_aprire]
#             if match:
#                 file_id =match[0] 
#                 with st.spinner("Caricamento del file..."):
#                     entità = syn.get(file_id)
#                     df_paziente = pd.read_csv(entità.path, sep="," , header=1)
#                     st.success(f"File {file_da_aprire} caricato con successo!")
#                     st.title(f"analisi: {file_da_aprire}")
#                     st.dataframe(df_paziente)
#             else:
#                 st.error("ID non trovato per il paziente selezionato")
#         else:
#             st.warning(f"Nessun file trovato per il paziente '{codice_persona}'")






   