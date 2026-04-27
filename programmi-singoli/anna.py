import synapseclient
import streamlit as st
import pandas as pd
import plotly.express as px

syn = synapseclient.Synapse() 
syn.login(authToken="eyJ0eXAiOiJKV1QiLCJraWQiOiJXN05OOldMSlQ6SjVSSzpMN1RMOlQ3TDc6M1ZYNjpKRU9VOjY0NFI6VTNJWDo1S1oyOjdaQ0s6RlBUSCIsImFsZyI6IlJTMjU2In0.eyJhY2Nlc3MiOnsic2NvcGUiOlsidmlldyIsImRvd25sb2FkIiwibW9kaWZ5Il0sIm9pZGNfY2xhaW1zIjp7fX0sInRva2VuX3R5cGUiOiJQRVJTT05BTF9BQ0NFU1NfVE9LRU4iLCJpc3MiOiJodHRwczovL3JlcG8tcHJvZC5wcm9kLnNhZ2ViYXNlLm9yZy9hdXRoL3YxIiwiYXVkIjoiMCIsIm5iZiI6MTc3NzI3NzE5MywiaWF0IjoxNzc3Mjc3MTkzLCJqdGkiOiIzNjM5NSIsInN1YiI6IjM1ODY4MzAifQ.c45mAiBBYyMKzictOESnFmWnM0Rd9qsg2O0CPGiK__L5foI8AlvoQYyOiJ5rCIz5hESh-GOYmumIcXspPgTkj8xMYv4N5KKjyDu6ud5upKfZQdrqq0xDR7mmZMZsgbpUjl2RNw-wtaZ_td-vPaFjEhvr759V40RE_PUWgi1_klh8tIZUWLUYuKCjEQrehibo4zPHN0sAGw63AlTS17153Opx05BCUEqV0dDgqvR-kPNhJVHOqazbPrbHpJtBF7cuv0o5QV6QUiYiDwRGPn5v-d9wKtWIJu2MJT3Ycu1WCTAJFPIVwpcpBh15DdFHNanMzLnOwg4qYe9BaVLi_gPBng") 

folder_file="syn61370558" 
df = pd.read_csv("CONTROLS.csv", sep="," , header=1)

st.sidebar.header("Analisi per genere")
selezione_genere=st.sidebar.selectbox("Scegliere un'opzione", ["Uomo","Donna"])
soggetti_selezionati = []
if selezione_genere == "Uomo": 
    for i,row in df.iterrows(): 
        if row["Gender"]== "Male":
            soggetti_selezionati.append ({"subject ID":row["Subject ID"], "gender":row["Gender"]})
if selezione_genere == "Donna":
    for i,row in df.iterrows():
       if row["Gender"]== "Female":
          soggetti_selezionati.append ({"subject ID":row["Subject ID"], "gender":row["Gender"]})

data_frame_filtrato = pd.DataFrame(soggetti_selezionati)
st.dataframe(data_frame_filtrato)