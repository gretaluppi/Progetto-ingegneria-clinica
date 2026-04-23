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

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
    st.stop()
    
df_control = pd.read_csv("CONTROLS.csv", sep="," , header=1)
df_pd = pd.read_csv("PD.csv", sep="," , header=1)
# IMPOSTAZIONE PAGINA
st.title("ANALISI DATI PARKINSON")

parametri=st.sidebar.button("Parametri di ricerca")

if parametri:
    # ______________________
    # FILTRO PER ETA' - Gre
    # ______________________
    st.sidebar.header("analisi per età")
    selezione_eta=st.sidebar.selectbox("scegliere un'opzione", ["range di età","età precisa"])
    soggetti_selezionati_eta = []
    if selezione_eta == "range di età": 
        age=st.sidebar.slider("selezionare un range di eta", 0, 110, 50)
        for i,row in df_control.iterrows(): # df.iterrows() è una funzione che restituisce ciclicamente un indice e la riga corrispettiva 
            # esempio: al primo ciclo i sarà = 0 e rows conterrà tutti i dati riferiti al paziente della prima riga
            # e così via
            if row["Age"]<=age:
                soggetti_selezionati_eta.append ({"subject ID":row["Subject ID"], "age":row["Age"]})
    if selezione_eta == "età precisa":
        age=st.sidebar.number_input("selezionare un età", 0, 110, 50, 1)
        for i,row in df_control.iterrows():
            if row["Age"]==age:
                soggetti_selezionati_eta.append({"subject ID":row["Subject ID"], "age":row["Age"]})

    # ____________________
    # FILTRO UPDRS - Vitto
    # ____________________

    st.sidebar.header("analisi UPDRS")
    soggetti_selezionati_updrs = []
    for i, row in df_pd.iterrows():
        Lista1 = [row["MDSUPDRS_1-1"], row["MDSUPDRS_1-2"], row["MDSUPDRS_1-3"], row["MDSUPDRS_1-4"], row["MDSUPDRS_1-5"], row["MDSUPDRS_1-6"], row["MDSUPDRS_1-7"], row["MDSUPDRS_1-8"], row["MDSUPDRS_1-9"], row["MDSUPDRS_1-10"], row["MDSUPDRS_1-11"], row["MDSUPDRS_1-12"], row["MDSUPDRS_1-13"]]
        Lista2 = [row["MDSUPDRS_2-1"], row["MDSUPDRS_2-2"], row["MDSUPDRS_2-3"], row["MDSUPDRS_2-4"], row["MDSUPDRS_2-5"], row["MDSUPDRS_2-6"], row["MDSUPDRS_2-7"], row["MDSUPDRS_2-8"], row["MDSUPDRS_2-9"], row["MDSUPDRS_2-10"], row["MDSUPDRS_2-11"], row["MDSUPDRS_2-12"], row["MDSUPDRS_2-13"]]
        Lista3 = [row["MDSUPDRS_3-1"], row["MDSUPDRS_3-2"], row["MDSUPDRS_3-3-Neck"], row["MDSUPDRS_3-3-RUE"], row["MDSUPDRS_3-3-LLE"], row["MDSUPDRS_3-4-R"], row["MDSUPDRS_3-4-L"], row["MDSUPDRS_3-5-R"], row["MDSUPDRS_3-5-L"], row["MDSUPDRS_3-6-R"], row["MDSUPDRS_3-6-L"], row["MDSUPDRS_3-7-R"], row["MDSUPDRS_3-7-L"], row["MDSUPDRS_3-8-R"], row["MDSUPDRS_3-8-L"], row["MDSUPDRS_3-9"], row["MDSUPDRS_3-10"], row["MDSUPDRS_3-11"], row["MDSUPDRS_3-12"], row["MDSUPDRS_3-13"], row["MDSUPDRS_3-14"], row["MDSUPDRS_3-15-R"], row["MDSUPDRS_3-15-L"], row["MDSUPDRS_3-16-L"], row["MDSUPDRS_3-16-R"], row["MDSUPDRS_3-17-RUE"], row["MDSUPDRS_3-17-LUE"], row["MDSUPDRS_3-17-RLE"], row["MDSUPDRS_3-17-LLE"], row["MDSUPDRS_3-17-LipJaw"], row["MDSUPDRS_3-18"]]
        Lista4 = [row["MDSUPDRS_4-1"], row["MDSUPDRS_4-2"], row["MDSUPDRS_4-3"], row["MDSUPDRS_4-4"], row["MDSUPDRS_4-5"], row["MDSUPDRS_4-6"]]
        Lista1_num = pd.to_numeric(pd.Series(Lista1), errors="coerce")
        Lista2_num = pd.to_numeric(pd.Series(Lista2), errors="coerce")
        Lista3_num = pd.to_numeric(pd.Series(Lista3), errors="coerce")
        Lista4_num = pd.to_numeric(pd.Series(Lista4), errors="coerce")
        if (Lista1_num.isna().any() or Lista2_num.isna().any() or Lista3_num.isna().any() or Lista4_num.isna().any()):
            soggetti_selezionati_updrs.append({"Subject ID": row["Subject ID"],"MDS-UPDRS": "Valori Mancanti"})
        else:
            Parte1 = sum(Lista1_num)
            Parte2 = sum(Lista2_num)
            Parte3 = sum(Lista3_num)
            Parte4 = sum(Lista4_num)
            UPDRS = Parte1 + Parte2 + Parte3 + Parte4
            soggetti_selezionati_updrs.append({"Subject ID": row["Subject ID"],"MDS-UPDRS": UPDRS})
    options = st.sidebar.multiselect(
        "Range UPDRS",
        ["Lieve (0-32)", "Moderato (33-58)", "Severo (59-102)", "Grave (> 103)"],
    )
    soggetti_finali_updrs = []
    for element in soggetti_selezionati_updrs:
        if element["MDS-UPDRS"] != "Valori Mancanti":
            if "Lieve (0-32)" in options:
                if element["MDS-UPDRS"] >= 0 and element["MDS-UPDRS"] <= 32:
                    soggetti_finali_updrs.append({"Subject ID" : element["Subject ID"], "MDS-UPDRS": element["MDS-UPDRS"]})
            if "Moderato (33-58)" in options:
                if element["MDS-UPDRS"] >= 33 and element["MDS-UPDRS"] <= 58:
                    soggetti_finali_updrs.append({"Subject ID" : element["Subject ID"], "MDS-UPDRS": element["MDS-UPDRS"]})
            if "Severo (59-102)" in options:
                if element["MDS-UPDRS"] >= 59 and element["MDS-UPDRS"] <= 102:
                    soggetti_finali_updrs.append({"Subject ID" : element["Subject ID"], "MDS-UPDRS": element["MDS-UPDRS"]})
            if "Grave (> 103)" in options:
                if element["MDS-UPDRS"] >= 103:
                    soggetti_finali_updrs.append({"Subject ID" : element["Subject ID"], "MDS-UPDRS": element["MDS-UPDRS"]})
        else: 
            soggetti_finali_updrs.append({"Subject ID" : element["Subject ID"], "MDS-UPDRS": "Valori Mancanti"})
    # ____________________
    # FILTRO PROVA - Adry
    # ____________________

    syn = synapseclient.Synapse()
    syn.login(authToken=st.session_state.auth_token)
    folder_file="syn61370558"
    files=list(syn.getChildren(folder_file))
    prova=[child['name'] for child in files]
    st.sidebar.header("seleziona tipo di prova")
    selezione_prova=st.sidebar.selectbox("prova eseguita", ["SelfPace","HurriedPace","SelfPace_mat","HurriedPace_mat","SelfPace_matTURN","TandemGait","TUG","Balance","SElfPace_doorpat","FreeWalk"])
    file_scelti= [f for f in prova if selezione_prova in f and (("_mat" in selezione_prova) == ("_mat" in f)) and (("TURN" in selezione_prova) == ("TURN" in f))]
    if file_scelti:
        file_da_aprire=st.selectbox("seleziona il file del soggetto da analizzare", file_scelti)
        if file_da_aprire:
            match = [c['id'] for c in files if c['name'] == file_da_aprire]
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
    
    data_frame_filtrato_eta = pd.DataFrame(soggetti_selezionati_eta)
    st.subheader("Dati filtrati per età")
    st.dataframe(data_frame_filtrato_eta)
    data_frame_filtrato_updrs = pd.DataFrame(soggetti_finali_updrs)
    st.subheader("Dati filtrati per UPDRS")
    st.dataframe(data_frame_filtrato_updrs)
    back=st.sidebar.button("Torna alla ricerca per paziente")
    if back: 
        codice_persona=st.sidebar.text_input("Inserire il codice paziente", placeholder="es: NLS456")
else: 
    syn = synapseclient.Synapse()
    syn.login(authToken=st.session_state.auth_token)
    folder_file="syn61370558"
    files=list(syn.getChildren(folder_file))
    paziente=[child['name'] for child in files]
    codice_persona=st.sidebar.text_input("Inserire il codice paziente", placeholder="es: NLS456")
    if codice_persona:
        file_scelti= [f for f in paziente if codice_persona in f]
        if file_scelti:
            file_da_aprire=st.selectbox("seleziona il file del soggetto da analizzare", file_scelti)
        if file_da_aprire:
            match = [c['id'] for c in files if c['name'] == file_da_aprire]
            if match:
                file_id =match[0] 
                with st.spinner("Caricamento del file..."):
                    entità = syn.get(file_id)
                    df_paziente = pd.read_csv(entità.path, sep="," , header=1)
                    st.success(f"File {file_da_aprire} caricato con successo!")
                    st.title(f"analisi: {file_da_aprire}")
                    st.dataframe(df_paziente)
            else:
                st.error("ID non trovato per il paziente selezionato")
        else:
            st.warning(f"Nessun file trovato per il paziente '{codice_persona}'")




   