import synapseclient
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Search and Open Files", page_icon="🔍", layout="wide")

# LOGIN CHECK
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("⚠️ Please log in from the Homepage.")
    st.stop()

#funzione per calcolare l'UPDRS
def calcolo_UPDRS(lis1,lis2,lis3,lis4):
    somma_finale=0
    Lista1_num = pd.to_numeric(pd.Series(Lista1), errors="coerce") # converto le liste in serie pandas e poi in numerico, se ci sono valori non convertibili vengono trasformati in NaN
    Lista2_num = pd.to_numeric(pd.Series(Lista2), errors="coerce")
    Lista3_num = pd.to_numeric(pd.Series(Lista3), errors="coerce")
    Lista4_num = pd.to_numeric(pd.Series(Lista4), errors="coerce")
    if not (Lista1_num.isna().any() or Lista2_num.isna().any() or Lista3_num.isna().any() or Lista4_num.isna().any()):
        Parte1 = sum(Lista1_num)
        Parte2 = sum(Lista2_num)
        Parte3 = sum(Lista3_num)
        Parte4 = sum(Lista4_num)
        somma_finale = Parte1 + Parte2 + Parte3 + Parte4
    else:
        somma_finale=-1
    return somma_finale


# lettura dei csv dei controlli e dei pazienti
df_control = pd.read_csv("CONTROLS.csv", sep="," , header=1)
df_pd = pd.read_csv("PD.csv", sep="," , header=1)

# IMPOSTAZIONE PAGINA
st.title("Search and Open Files") #titolo della pagina
st.info("If you do not want to search for files using search criteria, enter the patient ID in the designated field to view all files available in the dataset for that patient.")  
# crea una piccola didascalia per spiegare la funzionalità della pagina

# RICERCA PER ID PAZIENTE E APERTURA FILE

# inizializzazione variabili di sessione per mostrare i filtri e per la ricerca per ID
if "show_filters" not in st.session_state:
    st.session_state.show_filters = False # variabile di sessione per mostrare o nascondere i filtri di ricerca

if "search_by_id" not in st.session_state:
    st.session_state.search_by_id = False # variabile di sessione per mostrare o nascondere la ricerca per ID paziente

if st.sidebar.button("Search by criteria"):
    st.session_state.show_filters = True # mostra i filtri di ricerca
    st.session_state.search_by_id = False # nasconde la ricerca per ID paziente
    st.rerun() # aggiorna la pagina per mostrare i filtri di ricerca

if st.sidebar.button("Patient ID search"):
    st.session_state.show_filters = False # nasconde i filtri di ricerca
    st.session_state.search_by_id = True # mostra la ricerca per ID paziente
    st.rerun() # aggiorna la pagina per mostrare la ricerca per ID paziente
    
if st.session_state.search_by_id:
    codice_persona=st.sidebar.text_input("Patient ID", placeholder="es: NLS456") # campo di testo per inserire l'ID del paziente, con un placeholder per indicare il formato dell'ID
    if codice_persona:
        syn = synapseclient.Synapse() # creo un'istanza del client di Synapse
        syn.login(authToken=st.session_state.auth_token) # effettuo il login a Synapse utilizzando il token di autenticazione memorizzato nella variabile di sessione
        folder_file="syn61370558"
        files=list(syn.getChildren(folder_file)) # ottengo la lista di tutti i file presenti nella cartella specificata, utilizzando il metodo getChildren del client di Synapse
        paziente=[child['name'] for child in files] # creo una lista con i nomi di tutti i file presenti nella cartella, estraendo il campo 'name' da ogni elemento della lista di file ottenuta in precedenza
        file_scelti = [] # creo una lista vuota
        for f in paziente: # ciclo su ogni nome file
            if codice_persona in f: # controllo se il codice è presente
                file_scelti.append(f) # se sì, lo aggiungo alla lista
        if file_scelti: # se la lista non è vuota:
            file_da_aprire=st.selectbox("Select file to analyze", file_scelti) # creo un menu a tendina con i nomi dei file trovati, utilizzando il widget selectbox di Streamlit
        if file_da_aprire: # se è stato selezionato un file dal menu a tendina:
            match = [c['id'] for c in files if c['name'] == file_da_aprire] # cerco l'ID del file selezionato, confrontando il nome del file con i nomi dei file presenti nella cartella e estraendo l'ID corrispondente
            if match: # se è stato trovato un match per il nome del file selezionato:
                file_id =match[0] # prendo il primo elemento della lista di match (dovrebbe essere l'unico) e lo assegno alla variabile file_id
                with st.spinner("Downloading file..."): # mostro un messaggio di caricamento mentre il file viene scaricato, utilizzando il widget spinner di Streamlit
                    entità = syn.get(file_id) # ottengo l'entità del file selezionato, utilizzando il metodo get del client di Synapse e passando l'ID del file
                    df_paziente = pd.read_csv(entità.path, sep="," , header=1) # leggo il file scaricato come un dataframe di Pandas, utilizzando la funzione read_csv e passando il percorso del file ottenuto dall'entità, specificando il separatore e l'intestazione del file
                    st.success(f"File {file_da_aprire} downloaded successfully!") # mostro un messaggio di successo dopo che il file è stato scaricato, utilizzando il widget success di Streamlit e includendo il nome del file scaricato
                    st.title(f"File: {file_da_aprire}") # mostro il nome del file come titolo della sezione, utilizzando il widget title di Streamlit e includendo il nome del file selezionato
                    st.dataframe(df_paziente) # mostro il contenuto del file come un dataframe, utilizzando il widget dataframe di Streamlit e passando il dataframe ottenuto dalla lettura del file
            else:
                st.error("ID not found for the selected patient") # se non è stato trovato un match per il nome del file selezionato, mostro un messaggio di errore, utilizzando il widget error di Streamlit
        else:
            st.warning(f"No files found for patient '{codice_persona}'") # se non è stato selezionato un file dal menu a tendina, mostro un messaggio di avviso, utilizzando il widget warning di Streamlit e includendo il codice del paziente inserito

if st.session_state.show_filters: # se la variabile di sessione per mostrare i filtri è True, mostro i filtri di ricerca
    scelta_parametri=st.sidebar.multiselect("Select parameters",["Gender", "Age", "UPDRS", "Test"]) # creo un menu a tendina con più selezioni per scegliere i parametri di ricerca, utilizzando il widget multiselect di Streamlit e passando una lista di opzioni
    soggetti_selezionati_genere=[] # creo una lista vuota per memorizzare i soggetti selezionati in base al genere
    soggetti_selezionati_eta=[] # creo una lista vuota per memorizzare i soggetti selezionati in base all'età
    soggetti_selezionati_UPDRS=[] # creo una lista vuota per memorizzare i soggetti selezionati in base all'UPDRS
    soggetti_selezionati_prova=[] # creo una lista vuota per memorizzare i soggetti selezionati in base al test eseguito
    soggetti_selezionati_finale=[] # creo una lista vuota per memorizzare i soggetti selezionati in base a tutti i parametri scelti
    if "Gender" in scelta_parametri: # se il parametro "Gender" è stato selezionato, mostro le opzioni per la selezione del genere e filtro i soggetti in base al genere scelto
        st.sidebar.header("Analysis by gender:") # creo un'intestazione per la sezione di analisi per genere, utilizzando il widget header di Streamlit
        selezione_genere=st.sidebar.selectbox("Choose gender:", ["Male","Female"]) # creo un menu a tendina per scegliere il genere, utilizzando il widget selectbox di Streamlit e passando una lista di opzioni
        if selezione_genere == "Male": # se è stato selezionato il genere "Male":
            for i,row in df_pd.iterrows(): # ciclo su ogni riga del dataframe dei pazienti, utilizzando il metodo iterrows di Pandas
                if row["Gender"] == "Male": # se il valore della colonna "Gender" è uguale a "Male":
                    soggetti_selezionati_genere.append ({"Subject ID":row["Subject ID"], "Gender":row["Gender"]}) # aggiungo un dizionario con l'ID del soggetto e il genere alla lista dei soggetti selezionati in base al genere
        if selezione_genere == "Female": #faccio la stessa cosa se è stato selezionato il genere "Female":
            for i,row in df_pd.iterrows():
                if row["Gender"]== "Female":
                    soggetti_selezionati_genere.append ({"Subject ID":row["Subject ID"], "Gender":row["Gender"]})
    else: 
        for i,row in df_pd.iterrows(): # se il parametro "Gender" non è stato selezionato, aggiungo tutti i soggetti alla lista dei soggetti selezionati in base al genere, senza filtrare per genere
            soggetti_selezionati_genere.append ({"Subject ID":row["Subject ID"], "Gender":row["Gender"]})

    if "Age" in scelta_parametri: # se il parametro "Age" è stato selezionato, mostro le opzioni per la selezione dell'età e filtro i soggetti in base all'età scelta:
        st.sidebar.header("Analysis by age:") # creo un'intestazione per la sezione di analisi per età, utilizzando il widget header di Streamlit
        selezione_eta=st.sidebar.selectbox("Choose an option:", ["Age range","Specific age"]) # creo un menu a tendina per scegliere se filtrare per range di età o per età specifica, utilizzando il widget selectbox di Streamlit e passando una lista di opzioni
        if selezione_eta == "Age range": # se è stato selezionato il filtro per range di età:
            age_min,age_max=st.sidebar.slider("select age range", 0, 110, (0,100)) # creo un slider per selezionare il range di età, utilizzando il widget slider di Streamlit e passando i valori minimi, massimi e iniziali del range
            for i,row in df_pd.iterrows(): # ciclo su ogni riga del dataframe dei pazienti, utilizzando il metodo iterrows di Pandas
                for element in soggetti_selezionati_genere: # ciclo su ogni elemento della lista dei soggetti selezionati in base al genere, per filtrare ulteriormente i soggetti in base all'età
                    if ((row["Age (years)"]<=age_max and row["Age (years)"]>=age_min) and (element["Subject ID"] == row["Subject ID"])): # se il valore della colonna "Age (years)" è compreso tra il valore minimo e massimo selezionati e l'ID del soggetto corrisponde a quello dell'elemento della lista dei soggetti selezionati in base al genere:
                        soggetti_selezionati_eta.append({"Subject ID":element["Subject ID"], "Gender":element["Gender"], "Age": row["Age (years)"]}) # aggiungo un dizionario con l'ID del soggetto, il genere e l'età alla lista dei soggetti selezionati in base all'età
        if selezione_eta == "Specific age": # se è stato selezionato il filtro per età specifica:
            age=st.sidebar.number_input("select age", 0, 110, 50, 1) # creo un campo di input per inserire l'età specifica, utilizzando il widget number_input di Streamlit e passando i valori minimi, massimi, iniziali e il passo per l'età
            for i,row in df_pd.iterrows(): # ciclo su ogni riga del dataframe dei pazienti, utilizzando il metodo iterrows di Pandas
                for element in soggetti_selezionati_genere: # ciclo su ogni elemento della lista dei soggetti selezionati in base al genere, per filtrare ulteriormente i soggetti in base all'età
                    if (row["Age (years)"]==age) and (element["Subject ID"]==row["Subject ID"]): # se il valore della colonna "Age (years)" è uguale all'età specifica inserita e l'ID del soggetto corrisponde a quello dell'elemento della lista dei soggetti selezionati in base al genere:
                        soggetti_selezionati_eta.append({"Subject ID":element["Subject ID"], "Gender":element["Gender"], "Age": row["Age (years)"]}) # aggiungo un dizionario con l'ID del soggetto, il genere e l'età alla lista dei soggetti selezionati in base all'età
    else: 
        for i,row in df_pd.iterrows():
            for element in soggetti_selezionati_genere: # se il parametro "Age" non è stato selezionato:
                if row["Subject ID"] == element["Subject ID"]: # aggiungo tutti i soggetti alla lista dei soggetti selezionati in base all'età, senza filtrare per età, ma solo per genere se è stato selezionato
                    soggetti_selezionati_eta.append({"Subject ID":element["Subject ID"], "Gender":element["Gender"], "Age": row["Age (years)"]}) # aggiungo un dizionario con l'ID del soggetto, il genere e l'età alla lista dei soggetti selezionati in base all'età, senza filtrare per età, ma solo per genere se è stato selezionato
    
    
    if "UPDRS" in scelta_parametri: # se il parametro "UPDRS" è stato selezionato, mostro le opzioni per la selezione dell'UPDRS e filtro i soggetti in base all'UPDRS calcolato
        st.sidebar.header("UPDRS Analysis") # creo un'intestazione per la sezione di analisi per UPDRS, utilizzando il widget header di Streamlit
        options = st.sidebar.multiselect("UPDRS Range",["Mild (0-32)", "Moderate (33-58)", "Severe (59-102)", "Critical (> 103)"],) # creo un menu a tendina con più selezioni per scegliere il range di UPDRS, utilizzando il widget multiselect di Streamlit e passando una lista di opzioni
        for i, row in df_pd.iterrows():
            Lista1 = [row["MDSUPDRS_1-1"], row["MDSUPDRS_1-2"], row["MDSUPDRS_1-3"], row["MDSUPDRS_1-4"], row["MDSUPDRS_1-5"], row["MDSUPDRS_1-6"], row["MDSUPDRS_1-7"], row["MDSUPDRS_1-8"], row["MDSUPDRS_1-9"], row["MDSUPDRS_1-10"], row["MDSUPDRS_1-11"], row["MDSUPDRS_1-12"], row["MDSUPDRS_1-13"]]
            Lista2 = [row["MDSUPDRS_2-1"], row["MDSUPDRS_2-2"], row["MDSUPDRS_2-3"], row["MDSUPDRS_2-4"], row["MDSUPDRS_2-5"], row["MDSUPDRS_2-6"], row["MDSUPDRS_2-7"], row["MDSUPDRS_2-8"], row["MDSUPDRS_2-9"], row["MDSUPDRS_2-10"], row["MDSUPDRS_2-11"], row["MDSUPDRS_2-12"], row["MDSUPDRS_2-13"]]
            Lista3 = [row["MDSUPDRS_3-1"], row["MDSUPDRS_3-2"], row["MDSUPDRS_3-3-Neck"], row["MDSUPDRS_3-3-RUE"], row["MDSUPDRS_3-3-LLE"], row["MDSUPDRS_3-4-R"], row["MDSUPDRS_3-4-L"], row["MDSUPDRS_3-5-R"], row["MDSUPDRS_3-5-L"], row["MDSUPDRS_3-6-R"], row["MDSUPDRS_3-6-L"], row["MDSUPDRS_3-7-R"], row["MDSUPDRS_3-7-L"], row["MDSUPDRS_3-8-R"], row["MDSUPDRS_3-8-L"], row["MDSUPDRS_3-9"], row["MDSUPDRS_3-10"], row["MDSUPDRS_3-11"], row["MDSUPDRS_3-12"], row["MDSUPDRS_3-13"], row["MDSUPDRS_3-14"], row["MDSUPDRS_3-15-R"], row["MDSUPDRS_3-15-L"], row["MDSUPDRS_3-16-L"], row["MDSUPDRS_3-16-R"], row["MDSUPDRS_3-17-RUE"], row["MDSUPDRS_3-17-LUE"], row["MDSUPDRS_3-17-RLE"], row["MDSUPDRS_3-17-LLE"], row["MDSUPDRS_3-17-LipJaw"], row["MDSUPDRS_3-18"]]
            Lista4 = [row["MDSUPDRS_4-1"], row["MDSUPDRS_4-2"], row["MDSUPDRS_4-3"], row["MDSUPDRS_4-4"], row["MDSUPDRS_4-5"], row["MDSUPDRS_4-6"]] # creo quattro liste con i valori delle colonne corrispondenti alle parti 1, 2, 3 e 4 dell'MDS-UPDRS, per ogni riga del dataframe dei pazienti, utilizzando la sintassi di accesso alle colonne di Pandas
            UPDRS=calcolo_UPDRS(Lista1,Lista2,Lista3,Lista4) # calcolo l'UPDRS totale per ogni riga del dataframe dei pazienti, utilizzando la funzione calcolo_UPDRS definita in precedenza e passando le quattro liste di valori come argomenti
            for element in soggetti_selezionati_eta: # ciclo su ogni elemento della lista dei soggetti selezionati in base all'età, per filtrare ulteriormente i soggetti in base all'UPDRS
                if element["Subject ID"]==row["Subject ID"]: # se l'ID del soggetto corrisponde a quello dell'elemento della lista dei soggetti selezionati in base all'età:
                    if "Mild (0-32)" in options: # se è stato selezionato il range di UPDRS "Mild (0-32)":
                        if UPDRS >= 0 and UPDRS <= 32: # se il valore dell'UPDRS calcolato è compreso tra 0 e 32:
                            soggetti_selezionati_UPDRS.append({"Subject ID":element["Subject ID"], "Gender":element["Gender"], "Age": element["Age"],"MDS-UPDRS": str(UPDRS)+"( mild)"}) # aggiungo un dizionario con l'ID del soggetto, il genere, l'età e il valore dell'UPDRS alla lista dei soggetti selezionati in base all'UPDRS, indicando anche il range di UPDRS a cui appartiene
                    if "Moderate (33-58)" in options: # se è stato selezionato il range di UPDRS "Moderate (33-58)":
                        if UPDRS >= 33 and UPDRS <= 58: # se il valore dell'UPDRS calcolato è compreso tra 33 e 58:
                            soggetti_selezionati_UPDRS.append({"Subject ID":element["Subject ID"], "Gender":element["Gender"], "Age": element["Age"],"MDS-UPDRS": str(UPDRS)+"( moderate)"})                
                    if "Severe (59-102)" in options:
                        if UPDRS >= 59 and UPDRS <= 102:
                            soggetti_selezionati_UPDRS.append({"Subject ID":element["Subject ID"], "Gender":element["Gender"], "Age": element["Age"],"MDS-UPDRS": str(UPDRS)+"( severe)"})
                    if "Critical (> 103)" in options:
                        if UPDRS >= 103:
                            soggetti_selezionati_UPDRS.append({"Subject ID":element["Subject ID"], "Gender":element["Gender"], "Age": element["Age"],"MDS-UPDRS": str(UPDRS)+"( grave)"})
    else:
        for i,row in df_pd.iterrows(): # se il parametro "UPDRS" non è stato selezionato:
            Lista1 = [row["MDSUPDRS_1-1"], row["MDSUPDRS_1-2"], row["MDSUPDRS_1-3"], row["MDSUPDRS_1-4"], row["MDSUPDRS_1-5"], row["MDSUPDRS_1-6"], row["MDSUPDRS_1-7"], row["MDSUPDRS_1-8"], row["MDSUPDRS_1-9"], row["MDSUPDRS_1-10"], row["MDSUPDRS_1-11"], row["MDSUPDRS_1-12"], row["MDSUPDRS_1-13"]]
            Lista2 = [row["MDSUPDRS_2-1"], row["MDSUPDRS_2-2"], row["MDSUPDRS_2-3"], row["MDSUPDRS_2-4"], row["MDSUPDRS_2-5"], row["MDSUPDRS_2-6"], row["MDSUPDRS_2-7"], row["MDSUPDRS_2-8"], row["MDSUPDRS_2-9"], row["MDSUPDRS_2-10"], row["MDSUPDRS_2-11"], row["MDSUPDRS_2-12"], row["MDSUPDRS_2-13"]]
            Lista3 = [row["MDSUPDRS_3-1"], row["MDSUPDRS_3-2"], row["MDSUPDRS_3-3-Neck"], row["MDSUPDRS_3-3-RUE"], row["MDSUPDRS_3-3-LLE"], row["MDSUPDRS_3-4-R"], row["MDSUPDRS_3-4-L"], row["MDSUPDRS_3-5-R"], row["MDSUPDRS_3-5-L"], row["MDSUPDRS_3-6-R"], row["MDSUPDRS_3-6-L"], row["MDSUPDRS_3-7-R"], row["MDSUPDRS_3-7-L"], row["MDSUPDRS_3-8-R"], row["MDSUPDRS_3-8-L"], row["MDSUPDRS_3-9"], row["MDSUPDRS_3-10"], row["MDSUPDRS_3-11"], row["MDSUPDRS_3-12"], row["MDSUPDRS_3-13"], row["MDSUPDRS_3-14"], row["MDSUPDRS_3-15-R"], row["MDSUPDRS_3-15-L"], row["MDSUPDRS_3-16-L"], row["MDSUPDRS_3-16-R"], row["MDSUPDRS_3-17-RUE"], row["MDSUPDRS_3-17-LUE"], row["MDSUPDRS_3-17-RLE"], row["MDSUPDRS_3-17-LLE"], row["MDSUPDRS_3-17-LipJaw"], row["MDSUPDRS_3-18"]]
            Lista4 = [row["MDSUPDRS_4-1"], row["MDSUPDRS_4-2"], row["MDSUPDRS_4-3"], row["MDSUPDRS_4-4"], row["MDSUPDRS_4-5"], row["MDSUPDRS_4-6"]]
            UPDRS=calcolo_UPDRS(Lista1,Lista2,Lista3,Lista4)
            for element in soggetti_selezionati_eta: # ciclo su ogni elemento della lista dei soggetti selezionati in base all'età, per filtrare ulteriormente i soggetti in base all'UPDRS, anche se il parametro "UPDRS" non è stato selezionato, in modo da aggiungere comunque il valore dell'UPDRS al dizionario dei soggetti selezionati in base all'età
                if row["Subject ID"] == element["Subject ID"]: # se l'ID del soggetto corrisponde a quello dell'elemento della lista dei soggetti selezionati in base all'età:
                    if UPDRS >=0:
                        soggetti_selezionati_UPDRS.append({"Subject ID":element["Subject ID"], "Gender":element["Gender"], "Age": row["Age (years)"],"MDS-UPDRS": UPDRS}) # aggiungo un dizionario con l'ID del soggetto, il genere, l'età e il valore dell'UPDRS alla lista dei soggetti selezionati in base all'UPDRS, anche se il parametro "UPDRS" non è stato selezionato, in modo da avere comunque il valore dell'UPDRS per ogni soggetto selezionato in base all'età, senza filtrare per UPDRS
        
    data_frame_filtrato = pd.DataFrame(soggetti_selezionati_UPDRS) # creo un dataframe con i soggetti selezionati in base all'UPDRS, che contiene anche le informazioni sul genere e sull'età, utilizzando la funzione DataFrame di Pandas e passando la lista dei soggetti selezionati in base all'UPDRS come argomento
    st.subheader("Filtered subjects based on selected criteria:") # creo un sottotitolo per la sezione dei soggetti filtrati, utilizzando il widget subheader di Streamlit
    st.dataframe(data_frame_filtrato) # mostro il dataframe dei soggetti filtrati, utilizzando il widget dataframe di Streamlit e passando il dataframe creato in precedenza
    
    if "Test" in scelta_parametri:
        syn = synapseclient.Synapse()
        syn.login(authToken=st.session_state.auth_token)
        folder_file="syn61370558"
        all_files_in_folder = list(syn.getChildren(folder_file))
        files_disponibili = []
        for child in all_files_in_folder: # ciclo su ogni file presente nella cartella specificata, utilizzando il metodo getChildren del client di Synapse e passando l'ID della cartella
            nome_file= str(child['name']).upper() # prendo il nome del file e lo converto in maiuscolo, per facilitare la ricerca dei file in base ai criteri di selezione, senza dover considerare le differenze tra maiuscole e minuscole
            for element in soggetti_selezionati_UPDRS: # ciclo su ogni elemento della lista dei soggetti selezionati in base all'UPDRS, per filtrare i file disponibili in base all'ID del soggetto presente nel nome del file
                if element["Subject ID"] in child['name']: # se l'ID del soggetto è presente nel nome del file corrisponde a quello dell'elemento della lista dei soggetti selezionati in base all'UPDRS:
                    files_disponibili.append(child) # aggiungo il file alla lista dei file disponibili, se il nome del file contiene l'ID del soggetto selezionato in base all'UPDRS, in modo da filtrare i file disponibili in base ai soggetti selezionati in base all'UPDRS
        st.sidebar.header("select test:") # creo un'intestazione per la sezione di selezione del test, utilizzando il widget header di Streamlit
        selezione_prova=st.sidebar.selectbox("test executed", ["SelfPace","HurriedPace","SelfPace_mat","HurriedPace_mat","SelfPace_matTURN","TandemGait","TUG","Balance","SElfPace_doorpat","FreeWalk"]) # creo un menu a tendina per scegliere il test eseguito, utilizzando il widget selectbox di Streamlit e passando una lista di opzioni che rappresentano i test disponibili
        nomi_disponibili = [f['name'] for f in files_disponibili] # creo una lista con i nomi dei file disponibili, estraendo il campo 'name' da ogni elemento della lista di file disponibili ottenuta in precedenza, in modo da avere una lista di nomi di file filtrati in base ai soggetti selezionati in base all'UPDRS, per facilitare la ricerca dei file in base al test eseguito
        file_scelti = [] # creo una lista vuota per memorizzare i file scelti in base al test eseguito, che verranno mostrati nel menu a tendina per la selezione del file da analizzare
        for nome in nomi_disponibili: # ciclo su ogni nome di file disponibile
            if selezione_prova in nome and (("_mat" in selezione_prova)==("_mat" in nome)) and (("TURN" in selezione_prova)==("TURN" in nome)): # se il nome del file contiene il nome del test selezionato e se entrambi contengono o non contengono la stringa "_mat" e se entrambi contengono o non contengono la stringa "TURN", in modo da filtrare i file disponibili in base al test eseguito, escludendo i file che contengono la stringa "_mat" o "TURN" se il test selezionato non li contiene
                file_scelti.append(nome) # aggiungo il nome del file alla lista dei file scelti, se il nome del file soddisfa i criteri di selezione basati sul test eseguito, in modo da avere una lista di nomi di file filtrati in base al test eseguito, che verranno mostrati nel menu a tendina per la selezione del file da analizzare
        if file_scelti:
            file_da_aprire=st.selectbox("select the file to analyze", file_scelti) # creo un menu a tendina per scegliere il file da analizzare, utilizzando il widget selectbox di Streamlit e passando la lista dei file scelti in base al test eseguito come opzioni del menu a tendina
            if file_da_aprire: # se è stato selezionato un file dal menu a tendina:
                match = [c['id'] for c in files_disponibili if c['name'] == file_da_aprire] # cerco l'ID del file selezionato, confrontando il nome del file con i nomi dei file disponibili filtrati in base al test eseguito e estraendo l'ID corrispondente, in modo da avere l'ID del file selezionato per poterlo scaricare e analizzare
                if match: # se è stato trovato un match per il nome del file selezionato tra i file disponibili filtrati in base al test eseguito:
                    file_id =match[0] # prendo il primo elemento della lista di match (dovrebbe essere l'unico) e lo assegno alla variabile file_id
                    with st.spinner("Downloading file..."):
                        entità = syn.get(file_id) # ottengo l'entità del file selezionato, utilizzando il metodo get del client di Synapse e passando l'ID del file ottenuto dalla ricerca tra i file disponibili filtrati in base al test eseguito
                        df_prova = pd.read_csv(entità.path, sep="," , header=1) # leggo il file scaricato come un dataframe di Pandas, utilizzando la funzione read_csv e passando il percorso del file ottenuto dall'entità, specificando il separatore e l'intestazione del file
                        st.success(f"File {file_da_aprire} downloaded successfully!")
                        st.title(f"File: {file_da_aprire}")
                        st.dataframe(df_prova)
                else:
                    st.error("No file found for the selected test")
            else:
                st.warning(f"No file found for the test '{selezione_prova}' (excluded mat and TURN)")
        else:
            st.info("No file available")
    


