import synapseclient
syn = synapseclient.Synapse()
syn.login(authToken="eyJ0eXAiOiJKV1QiLCJraWQiOiJXN05OOldMSlQ6SjVSSzpMN1RMOlQ3TDc6M1ZYNjpKRU9VOjY0NFI6VTNJWDo1S1oyOjdaQ0s6RlBUSCIsImFsZyI6IlJTMjU2In0.eyJhY2Nlc3MiOnsic2NvcGUiOlsidmlldyJdLCJvaWRjX2NsYWltcyI6e319LCJ0b2tlbl90eXBlIjoiUEVSU09OQUxfQUNDRVNTX1RPS0VOIiwiaXNzIjoiaHR0cHM6Ly9yZXBvLXByb2QucHJvZC5zYWdlYmFzZS5vcmcvYXV0aC92MSIsImF1ZCI6IjAiLCJuYmYiOjE3NzY2ODU3ODksImlhdCI6MTc3NjY4NTc4OSwianRpIjoiMzU5MzgiLCJzdWIiOiIzNTg0OTYxIn0.evAV9MC8i0vH8Q_XPETZtJDiIaYnd2FAsiGeLBt5a1cQrKNJyyzfQ7pH3rqW52IiGkJMo3tO-yUicAjOm78AabqvlFDhq66ZbqRfsD-SRi8MlNGwIEzpYWawukrFilpJp7Sm5DLmkI0J_VTwGX8n9sTYEMqqT7FvCDD4_W9qI8k7jUOmTxB-7Oh2l0bvD-lhwWNjZj3aIlJfLLWNfn0SfupruoUn_YuyIcDVZpuW_4xXZKCxxx-0GkBp0I01WQQS5I9tjUX1xaf-e8fw1VhrB5oGRlL5WbIA9_G9MDpNk6ex3b89Ay4HJ73bvu8PzKFvDm9sxTsVP7o3iH1Mys5-LA")
import streamlit as st
import pandas as pd
import plotly.express as px
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

