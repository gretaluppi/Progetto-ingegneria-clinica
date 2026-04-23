import synapseclient
import streamlit as st
import pandas as pd
import plotly.express as px
def token(nome):
    file_token=pd.read_csv("TOKEN.csv")
    for i,row in file_token.iterrows():
        if row["Name"]==nome.lower():
            token_finale=row["Token"]
    return token_finale
name=st.text_input("Inserire il nome", placeholder="es: Francesca")
if name:
    syn = synapseclient.Synapse()
    auth_token = token(name)
    if auth_token:
        syn.login(authToken=auth_token)
        st.success(f"Accesso effettuato con successo per {name}")

    folder_file="syn61370558"
    files=list(syn.getChildren(folder_file))
    prova=[child['name'] for child in files]
#filtro in base alla prova eseguita
    st.sidebar.header("seleziona tipo di prova")
    selezione=st.sidebar.selectbox("prova eseguita", ["SelfPace","HurriedPace","SelfPace_mat","HurriedPace_mat","SelfPace_matTURN","TandemGait","TUG","Balance","SElfPace_doorpat","FreeWalk"])
    file_scelti= [f for f in prova if selezione in f and (("_mat" in selezione) == ("_mat" in f)) and (("TURN" in selezione) == ("TURN" in f))]
    if file_scelti:
        file_da_aprire=st.selectbox("seleziona il file del soggetto da analizzare", file_scelti)
        if file_da_aprire:
            match = [c['id'] for c in files if c['name'] == file_da_aprire]
            if match:
                file_id =match[0] 
                with st.spinner("Caricamento del file..."):
                    entità = syn.get(file_id)
                    df = pd.read_csv(entità.path, sep="," , header=1)
                    st.success(f"File {file_da_aprire} caricato con successo!")
                    st.title(f"analisi: {file_da_aprire}")
                    st.dataframe(df)
            else:
                st.error("Nessun file trovato per la prova selezionata")
        else:
            st.warning(f"Nessun file trovato per la prova '{selezione}' (esclusi mat e TURN)")
    if len(match) > 0:
            file_id = match[0]
            entità = syn.get(file_id)
            df = pd.read_csv(entità.path, sep="," , header=1)
            st.title("ANALISI DATI PARKINSON")
            st.dataframe(df)
    else:
        st.error("Nessun file trovato per la prova selezionata")
else:
    st.info("Per favore, inserisci un nome per accedere ai dati")

