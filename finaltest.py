# questo è un esempio di come scaricare i dati clinici da Synapse, esplorarli e visualizzarli con Streamlit
import synapseclient
syn = synapseclient.Synapse()
syn.login(authToken="eyJ0eXAiOiJKV1QiLCJraWQiOiJXN05OOldMSlQ6SjVSSzpMN1RMOlQ3TDc6M1ZYNjpKRU9VOjY0NFI6VTNJWDo1S1oyOjdaQ0s6RlBUSCIsImFsZyI6IlJTMjU2In0.eyJhY2Nlc3MiOnsic2NvcGUiOlsidmlldyIsImRvd25sb2FkIiwibW9kaWZ5Il0sIm9pZGNfY2xhaW1zIjp7fX0sInRva2VuX3R5cGUiOiJQRVJTT05BTF9BQ0NFU1NfVE9LRU4iLCJpc3MiOiJodHRwczovL3JlcG8tcHJvZC5wcm9kLnNhZ2ViYXNlLm9yZy9hdXRoL3YxIiwiYXVkIjoiMCIsIm5iZiI6MTc3NjI3ODAwMCwiaWF0IjoxNzc2Mjc4MDAwLCJqdGkiOiIzNTY2NCIsInN1YiI6IjM1ODQ3MjcifQ.oKMvvZCmv4gbCYlL91CpKHpB6AFkc0H2KMlTYZc7_aC85M1kl9qtgLUTMwGDIBvyVAT3UuVJWRdbrffBzppoYMbroglsWdT3VeI2xPOvUyNwddEy7tLLRwjnGh5xcmVSrO7r2VvGD6wVdo0mTxpvbEzPgiF9alU3gUgNvbQSImQnoopeddtl2I60uodW0TeJAVGZZUbWayO4o81KxYwIY3iji9PJUm4hgJ_1XHwmOWb-BghS6SyyOcbnNCfI74wkLTLqkN4lnXrp0B8hEKAvxM6xqudtm7lubJYddJEFD-cIuv9ENc9BaRcMTlEDbzhIzHIPVEGvmOw4cVu6_1LXuQ")
import streamlit as st
import pandas as pd
import plotly.express as px #ottimo per i grafici interattivi
#entity = syn.get("syn61498244") se voglio scaricare un singolo file da Synapse, altrimenti uso i metodi per scaricare più file da una cartella o filtrare per nome
#MODO PER LAVORARE CON TUTTI I FILE IN UNA CARTELLA SYNAPSE (es. cartella con i dati clinici)
#folder_id = "syn61370558"
#files = syn.getChildren(folder_id, includeTypes=["file"])
#for child in files:
#    entity = syn.get(child["id"])
#    print(f"scaricato: {entity.name} in {entity.path}")

#SE VOGLIO LAVORARE CON I PRIMI 30 FILE DI UNA CARTELLA SYNAPSE:
#children_iterator = syn.getChildren("syn61370558", includeTypes=["file"])
#lista_file = list(children_iterator)[:30] #prendo solo i primi 30 file
#lista_df = []
#for child in lista_file:
#    entity = syn.get(child["id"])
#    st.write(f"scaricato: {entity.name}")

#SE VOGLIO LAVORARE CON TUTTI I FILE DI UNA CERTA PROVA:
#folder_id = "syn61370558" solo se dopo voglio usare il nome folder_id invece del numero della cartella
children_iterator = syn.getChildren('syn61370558', includeTypes=["file"])
files = list(children_iterator) #prendo tutti i file
st.sidebar.header("configurazione analisi") #sidebar per la scelta del test 
tipo_test = st.sidebar.selectbox("Quale test vuoi analizzare?", ["Tutti", "Balance", "HurriedPace", "SelfPace", "TUG", "TandemGait"])
limite_file = st.sidebar.slider("Limite numero file da caricare", 5, 50, 20) #slider per limitare il numero di file da caricare
#filtraggio
if tipo_test != "Tutti":
    files_filtrati= [f for f in files if tipo_test.lower() in f["name"].lower()]
    files_da_caricare = files_filtrati[:limite_file] #prendo solo i primi 20 file filtrati per evitare di sovraccaricare la memoria
else: 
    files_da_caricare = files[:limite_file] #prendo solo i primi 20 file per evitare di sovraccaricare la memoria
st.info(f"stai analizzando il gruppo: **{tipo_test}** ({len(files_da_caricare)} file trovati)")
#caricamento dei soli files selezionati
lista_df = []
with st.spinner("caricamento file..."):
 for child in files_da_caricare:
    entity = syn.get(child["id"])
    temp_df = pd.read_csv(entity.path)
# aggiungo colonna per sapere da quale file arriva il dato
    temp_df["file"] = entity.name
    lista_df.append(temp_df)
if lista_df:
    df = pd.concat(lista_df, ignore_index=True)
    st.write(df.head()) #mostra i primi dati del dataframe unito

#leggi il file csv e aggiungilo alla lista dei dataframe
temp_df = pd.read_csv(entity.path)
lista_df.append(temp_df)
#unisci tutti i dataframe in uno solo
if lista_df:
    df = pd.concat(lista_df, ignore_index=True)
else:
    st.error("Nessun file trovato nella cartella Synapse.")
#ora df contiene tutti i dati clinici uniti, puoi esplorarli e visualizzarli con Streamlit
st.write("totale righe caricate:", len(df))


st.set_page_config(page_title="clinical data explorer", layout="wide") #configurazione pagina
st.title("esplorazione dati clinici")

#sidebar filtri
st.sidebar.header("filtri") #intestazione sidebar

colonne = df.columns.tolist()
colonna_scelta = st.sidebar.selectbox("Scegli una colonna", colonne)
# esempio di filtro dinamico
valore_unico = df[colonna_scelta].unique()
selezione = st.sidebar.multiselect(f"valori in {colonna_scelta}", valore_unico, default=valore_unico)

#applicazione filtro
df_filtrato = df[df[colonna_scelta].isin(selezione)]

#visualizzazione del dataframe filtrato
st.subheader("DataFrame filtrato")
st.dataframe(df_filtrato) #tabella interattiva con i dati filtrati

#operazioni semplici es. media
if st.button("mostra statistiche"):
    st.write(df_filtrato.describe())

#esempio: filtro pressione piede destro
max_p = int(df["R Foot Pressure"].max())
filtro_pressione = st.sidebar.slider("Range pressione destra", 0, max_p, (0, max_p))
#applicazione filtro pressione
df_filtrato = df[df["R Foot Pressure"].between(filtro_pressione[0], filtro_pressione[1])]
#layout principale
col1, col2 = st.columns(2) #creazione layout a 2 colonne
with col1:
    st.subheader("Distribuzione Variabili")
    var = st.selectbox("seleziona variabile", ["L Foot Pressure", "R Foot Pressure"])
    fig_dist = px.histogram(df_filtrato, x=var, nbins=30, marginal="box")
    st.plotly_chart(fig_dist)
with col2:
    st.subheader("statistiche descrittive")
    st.write(df_filtrato.describe())

#pattern e anomalie
st.divider()
st.subheader("Pattern (contatti nel tempo)")
#esempio di grafico a linee per visualizzare i contatti del piede nel tempo
fig_line = px.line(df_filtrato.iloc[:500], x=df_filtrato.index[:500], y=["L Foot Contact", "R Foot Contact"])
st.plotly_chart(fig_line, use_container_width=True)

