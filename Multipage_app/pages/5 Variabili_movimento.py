import synapseclient
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

syn = synapseclient.Synapse()
syn.login(authToken="eyJ0eXAiOiJKV1QiLCJraWQiOiJXN05OOldMSlQ6SjVSSzpMN1RMOlQ3TDc6M1ZYNjpKRU9VOjY0NFI6VTNJWDo1S1oyOjdaQ0s6RlBUSCIsImFsZyI6IlJTMjU2In0.eyJhY2Nlc3MiOnsic2NvcGUiOlsidmlldyIsImRvd25sb2FkIiwibW9kaWZ5Il0sIm9pZGNfY2xhaW1zIjp7fX0sInRva2VuX3R5cGUiOiJQRVJTT05BTF9BQ0NFU1NfVE9LRU4iLCJpc3MiOiJodHRwczovL3JlcG8tcHJvZC5wcm9kLnNhZ2ViYXNlLm9yZy9hdXRoL3YxIiwiYXVkIjoiMCIsIm5iZiI6MTc3NjkyNzg3MSwiaWF0IjoxNzc2OTI3ODcxLCJqdGkiOiIzNjE1MSIsInN1YiI6IjM1ODQ3MjcifQ.NWCaIH5Fv5Eqc1aQAMW0r3PPAbQ4K2vEJ1TxCUI6RFpEcMtesTafdBupjW3luxC57nRP8ApyqnMVKu2g3av9Clcccn818tHyN0cu-VILTt8_bunmpADKwUIuKeqU9eczo_pqjorUW0h-BusMOkitSaFvbwa4mK6co_K0e7YqG7uFlD1t9VPPhQQalZOl8XUw3pXHjkazTAx8qHia1dqU9BdK_822PwRQ3OWsM36SGgg5muBGCmmfhhOmmF7GwxXXLH073WHut70JZwjkpLcuvQ3l7xIh5wlO0eShfdpZDy7hJDZSpx2sPn3DfM_B39HkTdosgW-gpi-1QTfJFJZdnw")
# syn.login(authToken=st.session_state.auth_token)
folder_file="syn61370558"
tutti_file=list(syn.getChildren(folder_file))
file_selezionati=[]

def momenti_contatto(file): #serve per creare un sottofile con solo la riga e colonne di interesse (cioè colonna del tempo e righe in cui il valore cambia da 0 a 1 o da 1 a 0)
    appoggio_o_salita_sx=[]
    appoggio_o_salita_dx=[]
    diff_sx = file["L Foot Contact"].diff() #.diff() è una funzione che sottrae il valore della riga precedente da quello della riga attuale permettendo di trovare i fronti di salita e discesa in un segnale binario
    diff_dx= file["R Foot Contact"].diff()
    file['Time']=file['Time'].str.replace("sec","").astype(float)
    for i in range(len(file)):
        if diff_sx.iloc[i]==1:
            appoggio_o_salita_sx.append({"Time":file['Time'].iloc[i],"appoggio o salita":1})
        else:
            appoggio_o_salita_sx.append({"Time":file['Time'].iloc[i],"appoggio o salita":0}) 
    for i in range(len(file)):
        if diff_dx.iloc[i]==1:
            appoggio_o_salita_dx.append({"Time":file['Time'].iloc[i],"appoggio o salita":1})
        else:
            appoggio_o_salita_dx.append({"Time":file['Time'].iloc[i],"appoggio o salita":0}) 
    return appoggio_o_salita_sx,appoggio_o_salita_dx

for element in tutti_file: 
    if ("HurriedPace" in element['name'])and("_mat" not in element['name']):
        file_selezionati.append(element)
if file_selezionati: 
    codice_paziente=st.sidebar.text_input("Inserire il codice paziente", placeholder="es: NLS456")
    for j in file_selezionati:
        if codice_paziente in j['name']:
            entity = syn.get(j['id'], downloadFile=True)
            open_file = pd.read_csv(entity.path)
            appoggio_sx,appoggio_dx=momenti_contatto(open_file)
            df_sx=pd.DataFrame(appoggio_sx)
            df_dx=pd.DataFrame(appoggio_dx)

