import synapseclient
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.title("Movements metrics")
st.divider()

st.sidebar.subheader("📂 Dataset")
scelta_gruppo = st.sidebar.radio(
    "Show:",
    options=["SelfPace", "HurriedPace"],
    index=0
)

if scelta_gruppo == "PD":
    df_nuovo=df_pd
elif scelta_gruppo == "Control":
    df_nuovo= df_control
else:
    df_nuovo= df_totale




if "Test" in scelta_parametri:
        syn = synapseclient.Synapse()
        syn.login(authToken=st.session_state.auth_token)
        folder_file="syn61370558"
        all_files_in_folder = list(syn.getChildren(folder_file))
        files_disponibili = []
        for child in all_files_in_folder:
            nome_file= str(child['name']).upper()
            for element in soggetti_selezionati_UPDRS:
                if element["Subject ID"] in child['name']:
                    files_disponibili.append(child)
        st.sidebar.header("select test:")
        selezione_prova=st.sidebar.selectbox("test executed", ["SelfPace","HurriedPace","SelfPace_mat","HurriedPace_mat","SelfPace_matTURN","TandemGait","TUG","Balance","SElfPace_doorpat","FreeWalk"])
        nomi_disponibili = [f['name'] for f in files_disponibili]
        file_scelti = []
        for nome in nomi_disponibili:
            if selezione_prova in nome and (("_mat" in selezione_prova)==("_mat" in nome)) and (("TURN" in selezione_prova)==("TURN" in nome)):
                file_scelti.append(nome)
        if file_scelti:
            file_da_aprire=st.selectbox("select the file to analyze", file_scelti)
            if file_da_aprire:
                match = [c['id'] for c in files_disponibili if c['name'] == file_da_aprire]
                if match:
                    file_id =match[0] 
                    with st.spinner("Downloading file..."):
                        entità = syn.get(file_id)
                        df_prova = pd.read_csv(entità.path, sep="," , header=1)
                        st.success(f"File {file_da_aprire} downloaded successfully!")
                        st.title(f"File: {file_da_aprire}")
                        st.dataframe(df_prova)
                else:
                    st.error("No file found for the selected test")
            else:
                st.warning(f"No file found for the test '{selezione_prova}' (excluded mat and TURN)")
        else:
            st.info("No file available")


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

