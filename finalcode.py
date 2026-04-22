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
    return token_finale
syn = synapseclient.Synapse()
syn.login(authToken=token(name))
