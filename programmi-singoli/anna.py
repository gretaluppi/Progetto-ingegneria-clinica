import synapseclient
import streamlit as st
import pandas as pd
import plotly.express as px

syn = synapseclient.Synapse() 
syn.login(authToken="eyJ0eXAiOiJKV1QiLCJraWQiOiJXN05OOldMSlQ6SjVSSzpMN1RMOlQ3TDc6M1ZYNjpKRU9VOjY0NFI6VTNJWDo1S1oyOjdaQ0s6RlBUSCIsImFsZyI6IlJTMjU2In0.eyJhY2Nlc3MiOnsic2NvcGUiOlsidmlldyIsImRvd25sb2FkIiwibW9kaWZ5Il0sIm9pZGNfY2xhaW1zIjp7fX0sInRva2VuX3R5cGUiOiJQRVJTT05BTF9BQ0NFU1NfVE9LRU4iLCJpc3MiOiJodHRwczovL3JlcG8tcHJvZC5wcm9kLnNhZ2ViYXNlLm9yZy9hdXRoL3YxIiwiYXVkIjoiMCIsIm5iZiI6MTc3NzI3NzE5MywiaWF0IjoxNzc3Mjc3MTkzLCJqdGkiOiIzNjM5NSIsInN1YiI6IjM1ODY4MzAifQ.c45mAiBBYyMKzictOESnFmWnM0Rd9qsg2O0CPGiK__L5foI8AlvoQYyOiJ5rCIz5hESh-GOYmumIcXspPgTkj8xMYv4N5KKjyDu6ud5upKfZQdrqq0xDR7mmZMZsgbpUjl2RNw-wtaZ_td-vPaFjEhvr759V40RE_PUWgi1_klh8tIZUWLUYuKCjEQrehibo4zPHN0sAGw63AlTS17153Opx05BCUEqV0dDgqvR-kPNhJVHOqazbPrbHpJtBF7cuv0o5QV6QUiYiDwRGPn5v-d9wKtWIJu2MJT3Ycu1WCTAJFPIVwpcpBh15DdFHNanMzLnOwg4qYe9BaVLi_gPBng") 

folder_file="syn61370558" 
df_pd = pd.read_csv("PD.csv", sep="," , header=1)

# filtro genere
st.sidebar.header("Analisi per genere:")
selezione_genere=st.sidebar.selectbox("Scegliere il genere:", ["Uomo","Donna"])
soggetti_selezionati = []
if selezione_genere == "Uomo": 
    for i,row in df_pd.iterrows(): 
        if row["Gender"]== "Male":
            soggetti_selezionati.append ({"subject ID":row["Subject ID"], "genere":row["Gender"]})
if selezione_genere == "Donna":
    for i,row in df_pd.iterrows():
       if row["Gender"]== "Female":
          soggetti_selezionati.append ({"subject ID":row["Subject ID"], "genere":row["Gender"]})

data_frame_filtrato = pd.DataFrame(soggetti_selezionati)
st.dataframe(data_frame_filtrato)

# filtro step contact
st.sidebar.header("Tempo di contatto al suolo:")
selezione_contact = st.sidebar.slider("Scegliere la durata del passo in secondi:", 0, 100)
def momenti_contatto(df_pd, column): #serve per creare un sottofile con solo la riga e colonne di interesse (cioè colonna del tempo e righe in cui il valore cambia da 0 a 1 o da 1 a 0)
    diff = df_pd[column].diff() #.diff() è una funzione che sottrae il valore della riga precedente da quello della riga attuale permettendo di trovare i fronti di salita e discesa in un segnale binario
    for i,row in df_pd.iterrows():
        tempo_inizio = df_pd[diff == 1]["Time"]
        tempo_fine = df_pd[diff == -1]["Time"]
    durata_passo = tempo_fine - tempo_inizio

L_tempo_contact = momenti_contatto(df_pd, 'L Foot Contact')
# R_tempo_contact = momenti_contatto(df_pd, "R Foot Contact")
tempi_selezionati = []
if L_tempo_contact == selezione_contact:
    tempi_selezionati.append ({"subject ID":row["Subject ID"]})
