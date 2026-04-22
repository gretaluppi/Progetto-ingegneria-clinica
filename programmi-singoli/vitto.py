import synapseclient
import streamlit as st
import pandas as pd
import plotly.express as px
df = pd.read_csv("PD.csv", sep="," , header=1)
def token(nome):
    file_token=pd.read_csv("TOKEN.csv")
    for i,row in file_token.iterrows():
        if row["Name"]==nome.lower():
            token_finale=row["Token"]
    return token_finale
name=st.text_input("Inserire il nome", placeholder="es: Francesca")
syn = synapseclient.Synapse()
syn.login(authToken=token(name))
soggetti_selezionati = []
for i, row in df.iterrows():
    Lista1 = [row["MDSUPDRS_1-1"], row["MDSUPDRS_1-2"], row["MDSUPDRS_1-3"], row["MDSUPDRS_1-4"], row["MDSUPDRS_1-5"], row["MDSUPDRS_1-6"], row["MDSUPDRS_1-7"], row["MDSUPDRS_1-8"], row["MDSUPDRS_1-9"], row["MDSUPDRS_1-10"], row["MDSUPDRS_1-11"], row["MDSUPDRS_1-12"], row["MDSUPDRS_1-13"]]
    Lista2 = [row["MDSUPDRS_2-1"], row["MDSUPDRS_2-2"], row["MDSUPDRS_2-3"], row["MDSUPDRS_2-4"], row["MDSUPDRS_2-5"], row["MDSUPDRS_2-6"], row["MDSUPDRS_2-7"], row["MDSUPDRS_2-8"], row["MDSUPDRS_2-9"], row["MDSUPDRS_2-10"], row["MDSUPDRS_2-11"], row["MDSUPDRS_2-12"], row["MDSUPDRS_2-13"]]
    Lista3 = [row["MDSUPDRS_3-1"], row["MDSUPDRS_3-2"], row["MDSUPDRS_3-3-Neck"], row["MDSUPDRS_3-3-RUE"], row["MDSUPDRS_3-3-LLE"], row["MDSUPDRS_3-4-R"], row["MDSUPDRS_3-4-L"], row["MDSUPDRS_3-5-R"], row["MDSUPDRS_3-5-L"], row["MDSUPDRS_3-6-R"], row["MDSUPDRS_3-6-L"], row["MDSUPDRS_3-7-R"], row["MDSUPDRS_3-7-L"], row["MDSUPDRS_3-8-R"], row["MDSUPDRS_3-8-L"], row["MDSUPDRS_3-9"], row["MDSUPDRS_3-10"], row["MDSUPDRS_3-11"], row["MDSUPDRS_3-12"], row["MDSUPDRS_3-13"], row["MDSUPDRS_3-14"], row["MDSUPDRS_3-15-R"], row["MDSUPDRS_3-15-L"], row["MDSUPDRS_3-16-L"], row["MDSUPDRS_3-16-R"], row["MDSUPDRS_3-17-RUE"], row["MDSUPDRS_3-17-LUE"], row["MDSUPDRS_3-17-RLE"], row["MDSUPDRS_3-17-LLE"], row["MDSUPDRS_3-17-LipJaw"], row["MDSUPDRS_3-18"]]
    Lista4 = [row["MDSUPDRS_4-1"], row["MDSUPDRS_4-2"], row["MDSUPDRS_4-3"], row["MDSUPDRS_4-4"], row["MDSUPDRS_4-5"], row["MDSUPDRS_4-6"]]

    Lista1_num = pd.to_numeric(pd.Series(Lista1), errors="coerce")
    Lista2_num = pd.to_numeric(pd.Series(Lista2), errors="coerce")
    Lista3_num = pd.to_numeric(pd.Series(Lista3), errors="coerce")
    Lista4_num = pd.to_numeric(pd.Series(Lista4), errors="coerce")
    
    if (Lista1_num.isna().any() or Lista2_num.isna().any() or Lista3_num.isna().any() or Lista4_num.isna().any()):
        soggetti_selezionati.append({"Subject ID": row["Subject ID"],"MDS-UPDRS": "Valori Mancanti"})
    else:
        Parte1 = sum(Lista1_num)
        Parte2 = sum(Lista2_num)
        Parte3 = sum(Lista3_num)
        Parte4 = sum(Lista4_num)

        UPDRS = Parte1 + Parte2 + Parte3 + Parte4

        soggetti_selezionati.append({"Subject ID": row["Subject ID"],"MDS-UPDRS": UPDRS})

options = st.multiselect(
    "Range UPDRS",
    ["Lieve (0-32)", "Moderato (33-58)", "Severo (59-102)", "Grave (> 103)"],
)

soggetti_finali = []
for element in soggetti_selezionati:
    if element["MDS-UPDRS"] != "Valori Mancanti":
        if "Lieve (0-32)" in options:
            if element["MDS-UPDRS"] >= 0 and element["MDS-UPDRS"] <= 32:
                soggetti_finali.append({"Subject ID" : element["Subject ID"], "MDS-UPDRS": element["MDS-UPDRS"]})
        if "Moderato (33-58)" in options:
            if element["MDS-UPDRS"] >= 33 and element["MDS-UPDRS"] <= 58:
                soggetti_finali.append({"Subject ID" : element["Subject ID"], "MDS-UPDRS": element["MDS-UPDRS"]})
        if "Severo (59-102)" in options:
            if element["MDS-UPDRS"] >= 59 and element["MDS-UPDRS"] <= 102:
                soggetti_finali.append({"Subject ID" : element["Subject ID"], "MDS-UPDRS": element["MDS-UPDRS"]})
        if "Grave (> 103)" in options:
            if element["MDS-UPDRS"] >= 103:
                soggetti_finali.append({"Subject ID" : element["Subject ID"], "MDS-UPDRS": element["MDS-UPDRS"]})
    else: 
        soggetti_finali.append({"Subject ID" : element["Subject ID"], "MDS-UPDRS": "Valori Mancanti"})

data_frame_filtrato = pd.DataFrame(soggetti_finali)
st.dataframe(data_frame_filtrato)

