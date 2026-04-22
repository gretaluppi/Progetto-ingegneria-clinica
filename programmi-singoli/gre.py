import synapseclient
import streamlit as st
import pandas as pd
import plotly.express as px
def token(nome):
    name=st.text_input("Inserire il nome", placeholder="es: Francesca")
    file_token=pd.read_csv("TOKEN.csv")
    for i,row in file_token.iterrows():
        if row["Name"]==nome.lower():
            token_finale=row["Token"]
    return token_finale
syn = synapseclient.Synapse()
syn.login(authToken=token(name))
folder_file="syn61370558" #ho assegnato ad una variabile l'ID della cartella 
df = pd.read_csv("CONTROLS.csv", sep="," , header=1) # questo mi serve per aprire il file cvs 
# e per mettere come prima riga la riga che in automatico va come seconda (non so perchè ma quando 
# legge il file non riconsoce la prima come intestazione delle colonne e crea delle colonne chiamate 
# Unnamed, da chiedere al prof come risolvere)
# df.columns = df.columns.str.strip()
# st.title("Dataset Parkinson")
# st.dataframe(df)
st.title("ANALISI DATI PARKINSON")
st.sidebar.header("analisi per età")
selezione=st.sidebar.selectbox("scegliere un'opzione", ["range di età","età precisa"])
soggetti_selezionati = []
if selezione == "range di età": 
    age=st.sidebar.slider("selezionare un range di eta", 0, 110, 50)
    for i,row in df.iterrows(): # df.iterrows() è una funzione che restituisce ciclicamente un indice e la riga corrispettiva 
        # esempio: al primo ciclo i sarà = 0 e rows conterrà tutti i dati riferiti al paziente della prima riga
        # e così via
        if row["Age"]<=age:
            soggetti_selezionati.append ({"subject ID":row["Subject ID"], "age":row["Age"]})
if selezione == "età precisa":
    age=st.sidebar.number_input("selezionare un età", 0, 110, 50, 1)
    for i,row in df.iterrows():
       if row["Age"]==age:
          soggetti_selezionati.append ({"subject ID":row["Subject ID"], "age":row["Age"]})

data_frame_filtrato = pd.DataFrame(soggetti_selezionati)
st.dataframe(data_frame_filtrato)

