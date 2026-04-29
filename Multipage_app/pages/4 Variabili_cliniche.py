import synapseclient
import streamlit as st
import pandas as pd
import plotly.express as px

def calcolo_UPDRS(lis1,lis2,lis3,lis4):
        somma_finale=0
        Lista1_num = pd.to_numeric(pd.Series(lis1), errors="coerce")
        Lista2_num = pd.to_numeric(pd.Series(lis2), errors="coerce")
        Lista3_num = pd.to_numeric(pd.Series(lis3), errors="coerce")
        Lista4_num = pd.to_numeric(pd.Series(lis4), errors="coerce")
        if not (Lista1_num.isna().any() or Lista2_num.isna().any() or Lista3_num.isna().any() or Lista4_num.isna().any()):
            Parte1 = sum(Lista1_num)
            Parte2 = sum(Lista2_num)
            Parte3 = sum(Lista3_num)
            Parte4 = sum(Lista4_num)
            somma_finale = Parte1 + Parte2 + Parte3 + Parte4
        else:
            somma_finale=-1
        return somma_finale

st.title("Variabili cliniche")
st.write("In questa pagina troviamo le Variabili Cliniche.")
tab1, tab2=st.tabs(["UPDRS","terapia paziente"])
with tab1:
    df_pd = pd.read_csv("PD.csv", sep="," , header=1)
    df_pd["UPDRS"] = None
    for i, row in df_pd.iterrows():
        Lista1 = [row["MDSUPDRS_1-1"], row["MDSUPDRS_1-2"], row["MDSUPDRS_1-3"], row["MDSUPDRS_1-4"], row["MDSUPDRS_1-5"], row["MDSUPDRS_1-6"], row["MDSUPDRS_1-7"], row["MDSUPDRS_1-8"], row["MDSUPDRS_1-9"], row["MDSUPDRS_1-10"], row["MDSUPDRS_1-11"], row["MDSUPDRS_1-12"], row["MDSUPDRS_1-13"]]
        Lista2 = [row["MDSUPDRS_2-1"], row["MDSUPDRS_2-2"], row["MDSUPDRS_2-3"], row["MDSUPDRS_2-4"], row["MDSUPDRS_2-5"], row["MDSUPDRS_2-6"], row["MDSUPDRS_2-7"], row["MDSUPDRS_2-8"], row["MDSUPDRS_2-9"], row["MDSUPDRS_2-10"], row["MDSUPDRS_2-11"], row["MDSUPDRS_2-12"], row["MDSUPDRS_2-13"]]
        Lista3 = [row["MDSUPDRS_3-1"], row["MDSUPDRS_3-2"], row["MDSUPDRS_3-3-Neck"], row["MDSUPDRS_3-3-RUE"], row["MDSUPDRS_3-3-LLE"], row["MDSUPDRS_3-4-R"], row["MDSUPDRS_3-4-L"], row["MDSUPDRS_3-5-R"], row["MDSUPDRS_3-5-L"], row["MDSUPDRS_3-6-R"], row["MDSUPDRS_3-6-L"], row["MDSUPDRS_3-7-R"], row["MDSUPDRS_3-7-L"], row["MDSUPDRS_3-8-R"], row["MDSUPDRS_3-8-L"], row["MDSUPDRS_3-9"], row["MDSUPDRS_3-10"], row["MDSUPDRS_3-11"], row["MDSUPDRS_3-12"], row["MDSUPDRS_3-13"], row["MDSUPDRS_3-14"], row["MDSUPDRS_3-15-R"], row["MDSUPDRS_3-15-L"], row["MDSUPDRS_3-16-L"], row["MDSUPDRS_3-16-R"], row["MDSUPDRS_3-17-RUE"], row["MDSUPDRS_3-17-LUE"], row["MDSUPDRS_3-17-RLE"], row["MDSUPDRS_3-17-LLE"], row["MDSUPDRS_3-17-LipJaw"], row["MDSUPDRS_3-18"]]
        Lista4 = [row["MDSUPDRS_4-1"], row["MDSUPDRS_4-2"], row["MDSUPDRS_4-3"], row["MDSUPDRS_4-4"], row["MDSUPDRS_4-5"], row["MDSUPDRS_4-6"]]
        UPDRS=calcolo_UPDRS(Lista1,Lista2,Lista3,Lista4)
        if UPDRS >=0 and row["Gender"]!="-":
            df_pd.at[i,"UPDRS"] = UPDRS
    col1, col2 = st.columns(2)
    with col1:
        fig_sesso_updrs = px.strip(df_pd, x="Gender", y="UPDRS", color = "Gender", hover_data=["Subject ID", "Age (years)"], title = "Distribuzione UPDRS per genere")
        fig_sesso_updrs.update_layout(xaxis_title="Genere", yaxis_title="Indice UPDRS", showlegend = False)
        st.plotly_chart(fig_sesso_updrs) 

    with col2:
        fig_eta_updrs= px.strip(df_pd, x="Age (years)", y="UPDRS", color = "Age (years)", hover_data=["Subject ID", "Gender"], title = "Distribuzione UPDRS per età")
        fig_eta_updrs.update_layout(xaxis_title="Età", yaxis_title="Indice UPDRS", showlegend = False)
        st.plotly_chart(fig_eta_updrs)

with tab2: 
    codice_paziente=st.text_input("Inserire il codice paziente", placeholder="es: NLS456")
    for i,row in df_pd.iterrows():
        if row["Subject ID"]==codice_paziente: 
            if row["Current Medications"] != "-":
                terapia = row["Current Medications"]
                righe_terapia = terapia.split("\n")
                st.write("La terapia del paziente "+codice_paziente+" è: \n")
                for r in righe_terapia:
                    st.write("  • "+r+"\n")
                if row["PD Medication Dose"] != "-":
                    dosaggio=row["PD Medication Dose"]
                    righe_dosaggio=dosaggio.split("\n")
                    st.write("I medicinali hanno le seguenti dosi: \n")
                    for r in righe_dosaggio:
                        st.write("  • "+r+"\n")
                else:
                    st.error("Dosaggio non inserito")
            else:
                if row["PD Medication Dose"] != "-":
                    dosaggio=row["PD Medication Dose"]
                    righe_dosaggio=dosaggio.split("\n")
                    st.write("I medicinali hanno le seguenti dosi: \n")
                    for r in righe_dosaggio:
                        st.write("  • "+r+"\n")
                else: 
                    st.error("Terapia non esistente o non inserita")
            
        

