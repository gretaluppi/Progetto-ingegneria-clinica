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

syn.login(authToken=token(name))
folder_file="syn61370558" #ho assegnato ad una variabile l'ID della cartella 

