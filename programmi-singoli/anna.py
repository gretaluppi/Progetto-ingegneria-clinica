import synapseclient
import streamlit as st
import pandas as pd
import plotly.express as px

def token(nome):
    file_token=pd.read_csv("TOKEN.csv")
    for i,row in file_token.iterrows():
        if row["Name"]==nome.lower():
            return row["Token"]
    return None
st.session_state.logged=False
name=st.text_input("Inserire il nome", placeholder="es: Francesca")
if token(name)==None: #pd.isna(variabile) mi restituisce true se la cella è vuota e quindi ne variabile = Nan che è il tipo di dato che restituisce row["token"] se la cella corrispondente è vuota
    st.error("Nome non corretto o Token mancante")
else:
     st.session_state.logged=True

syn = synapseclient.Synapse()
syn.login(authToken=token(name))
folder_file="syn61370558" #ho assegnato ad una variabile l'ID della cartella 
df = pd.read_csv("CONTROLS.csv", sep="," , header=1)

st.sidebar.header("Analisi per genere")
selezione=st.sidebar.selectbox("Scegliere un'opzione", ["Uomo","Donna"])
soggetti_selezionati = []
if selezione == "Uomo": 
    for i,row in df.iterrows(): 
        if row["Gender"]== "Male":
            soggetti_selezionati.append ({"subject ID":row["Subject ID"], "gender":row["Gender"]})
if selezione == "Donna":
    for i,row in df.iterrows():
       if row["Gender"]== "Female":
          soggetti_selezionati.append ({"subject ID":row["Subject ID"], "gender":row["Gender"]})

data_frame_filtrato = pd.DataFrame(soggetti_selezionati)
st.dataframe(data_frame_filtrato)