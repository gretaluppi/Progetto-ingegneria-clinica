import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="PDAI - Dati Demografici", page_icon="🧠", layout="wide")

# LOGIN CHECK
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("⚠️ Please log in from the Homepage.")
    st.stop()

# Sidebar
st.sidebar.title("🧠 PDAI")
st.sidebar.markdown("**Parkinsonian Data Analysis Interface**")
st.sidebar.divider()

# Dati
df_control = pd.read_csv("CONTROLS.csv", sep="," , header=1)
df_pd = pd.read_csv("PD.csv", sep="," , header=1)
df_pd = df_pd.rename(columns = {"Age (years)" : "Age"}) #rinomino le colonne dei due file per poterle prendere insieme

df_pd["GRUPPO"] = "PD"
df_control["GRUPPO"] = "CONTROL"

df_totale= pd.concat([df_pd, df_control], ignore_index = True) #unisce tutte le righe di df_pd con quelle di df_control (non controlla se ci sono duplicati quindi se un paziente è sia in control che in pd viene riportato due volte)

# Titolo
st.title("Demographics")
# st.caption("Panoramica generale delle informazioni demografiche dei pazienti.")
st.divider()

# Selezione gruppo
st.sidebar.subheader("📂 Dataset")
scelta_gruppo = st.sidebar.radio(
    "Show:",
    options=["PD", "Control", "All"],
    index=0
)

if scelta_gruppo == "PD":
    df_nuovo=df_pd
elif scelta_gruppo == "Control":
    df_nuovo= df_control
else:
    df_nuovo= df_totale

# FILTERS
# st.sidebar.divider()
# st.sidebar.subheader("🔍 Filters:")

#INSERIRE I FILTRI

# MAPPA COLORE
color_map = {"Male": "#4A90D9", "Female": "#E8729A"}

# Valori barra
#st.subheader("📋 Summary")
#col1, col2, col3 = st.columns(3)
#col1.metric("Pazienti", len(df))
#col2.metric("Età media", f"{df['Age'].mean():.1f} yrs")
#col3.metric("Maschi / Femmine", f"{(df['Gender']=='Maschi').sum()} / {(df['Gender']=='Femmine').sum()}")

# PRIMA RIGA
col1, col2 = st.columns(2)

with col1:
    st.subheader("Gender Distribution")
    df_male = df_nuovo[df_nuovo["Gender"] == "Male"]
    df_female = df_nuovo[df_nuovo["Gender"] == "Female"]
    df_gender = pd.concat([df_male, df_female], ignore_index = True) #così elimino eventuali caselle vuote
    fig_gender = px.pie(df_gender, names="Gender", color="Gender", color_discrete_map=color_map, hole=0.4 ) 
    #px.pie (valori,categoria da selezionare,colori - che nel nostro caso di riferiscono a color_map 
    # che assegna un particolare colore in base a genere-, assegno i colori, grandezza del buco al centro
    #- se metto hole=0 avrò un grafico a torta normale altrimenti ne avrò uno a "ciambella")
    fig_gender.update_layout(margin=dict(t=10, b=10)) #metto i margini t=top e b=bottom
    st.plotly_chart(fig_gender, use_container_width=True) #serve per mostrare il grafico, 
                                                        #use_container_width=True adatta in automatico la figura allo spazio

with col2:
    st.subheader("Age distribution")
    df_male = df_nuovo[df_nuovo["Gender"] == "Male"]
    df_female = df_nuovo[df_nuovo["Gender"] == "Female"]
    df_box = pd.concat([df_male, df_female], ignore_index = True)
    x_col = "Gender"
    y_col = "Age"
    color_col = "Gender" 
    title = " "
    fig_box_swarm = go.Figure()

# MALE BOX
    fig_box_swarm.add_trace(go.Box(
        x=["Male"] * len(df_male),
        y=df_male[y_col],
        name="Male",
        boxmean=True,
        line=dict(color="#4A90D9"),
        fillcolor="rgba(74,144,217,0.3)"
    ))

    # MALE SWARM
    fig_box_swarm.add_trace(go.Scatter(
        x=["Male"] * len(df_male),
        y=df_male[y_col],
        mode="markers",
        marker=dict(
            size=7,
            color="#1f5fbf",
            opacity=0.8
        ),
        showlegend=False
    ))

    # FEMALE BOX
    fig_box_swarm.add_trace(go.Box(
        x=["Female"] * len(df_female),
        y=df_female[y_col],
        name="Female",
        boxmean=True,
        line=dict(color="#E8729A"),
        fillcolor="rgba(232,114,154,0.3)"
    ))

    # FEMALE SWARM
    fig_box_swarm.add_trace(go.Scatter(
        x=["Female"] * len(df_female),
        y=df_female[y_col],
        mode="markers",
        marker=dict(
            size=7,
            color="#c2185b",
            opacity=0.8
        ),
        showlegend=False
    ))

    fig_box_swarm.update_layout(
        title=title,
        margin=dict(t=30, b=10),
        boxmode="overlay",
        yaxis = dict(title = "Age"),
        xaxis = dict(title = " ")
    )

    st.plotly_chart(fig_box_swarm, use_container_width=True)
st.divider()

#AGE DISTRIBUTION -> è stato sostituito dallo swarm plot
#    st.subheader("Age Distribution")
#   df_male = df_nuovo[df_nuovo["Gender"] == "Male"]
#   df_female = df_nuovo[df_nuovo["Gender"] == "Female"]
#   df_age = pd.concat([df_male, df_female], ignore_index = True)
#    fig_age = px.histogram(df_age, x="Age", color="Gender", barmode="group", color_discrete_map=color_map)
#   #barmode="group" permette di avere le barre unite o affiancate e non separate, posso avere anche 
#   #"overlay" che le mette impilate e "stack" che le mette impilate
#   fig_age.update_traces(xbins=dict(size=5))   #l'ampiezza di ogni intervallo è 10 anni
#   fig_age.update_layout(xaxis=dict(tick0=0, dtick=5))  # impostiamo la frequenza dei valori sull'asse X
#   fig_age.update_layout(margin=dict(t=10, b=10))
#   st.plotly_chart(fig_age, use_container_width=True)
 
# SECONDA RIGA
col3, col4 = st.columns(2)

with col3:
    st.subheader("Weight Distribution")
    df_male = df_nuovo[df_nuovo["Gender"] == "Male"]
    df_female = df_nuovo[df_nuovo["Gender"] == "Female"]
    df_peso = pd.concat([df_male, df_female], ignore_index = True)
    fig_peso = px.histogram(df_peso, x="Weight (kg)", color="Gender", barmode="group", color_discrete_map=color_map)
    fig_peso.update_traces(xbins=dict(size=10))   #l'ampiezza di ogni intervallo è 10kg
    fig_peso.update_layout(xaxis=dict(tick0=0, dtick=10))  # impostiamo la frequenza dei valori sull'asse X
    st.plotly_chart(fig_peso, use_container_width=True)


with col4:
    st.subheader("Height Distribution")
    df_male = df_nuovo[df_nuovo["Gender"] == "Male"]
    df_female = df_nuovo[df_nuovo["Gender"] == "Female"]
    df_altezza = pd.concat([df_male, df_female], ignore_index = True)
    df_altezza["Height (cm)"] = df_altezza["Height (in)"] * 2.54 # trasformiamo l'altezza da inches in cm -> si moltiplica la colonna esistente per 2.54
    fig_altezza = px.histogram(df_altezza, x="Height (cm)", color="Gender", barmode="group", color_discrete_map=color_map)
    fig_altezza.update_traces(xbins=dict(size=10))   #l'ampiezza di ogni intervallo è 10 cm
    fig_altezza.update_layout(xaxis=dict(tick0=0, dtick=10)) # impostiamo la frequenza dei valori sull'asse X
    st.plotly_chart(fig_altezza, use_container_width=True)
st.divider()

# TERZA RIGA
# col5, col6 = st.columns(2)

# with col5:
#     st.subheader("Race Distribution")
#     df_white = df_nuovo[df_nuovo["Race"] == "White"]
#     df_asian = df_nuovo[df_nuovo["Race"] == "Asian"]
#     df_black = df_nuovo[df_nuovo["Race"] == "Black/African American"]
#     df_race = pd.concat([df_white, df_asian, df_black], ignore_index = True)
#     race_counts = pd.DataFrame({"Race" : ["White", "Asian", "Black/African American"], "Count" : [len(df_white), len(df_asian), len(df_black)]})
#     fig_race = px.bar(race_counts, x="Count", y="Race", orientation="h", color="Race", color_discrete_sequence=px.colors.qualitative.Safe)
#     fig_race.update_layout(margin=dict(t=10, b=10), showlegend=False)
#     st.plotly_chart(fig_race, use_container_width=True)


# with col6:
#     if scelta_gruppo == "PD":
#         st.subheader("Years since PD diagnosis")
#         df_male = df_nuovo[df_nuovo["Gender"] == "Male"]
#         df_female = df_nuovo[df_nuovo["Gender"] == "Female"]
#         df_box = pd.concat([df_male, df_female], ignore_index = True)
#         x_col = "Gender"
#         y_col = "Years since PD diagnosis"
#         color_col = "Gender"
#         title = " "
#         fig_box_swarm = go.Figure()

#         # MALE BOX
#         fig_box_swarm.add_trace(go.Box(
#             x=["Male"] * len(df_male),
#             y=df_male[y_col],
#             name="Male",
#             boxmean=True,
#             line=dict(color="#4A90D9"),
#             fillcolor="rgba(74,144,217,0.3)"
#         ))

#         # MALE SWARM
#         fig_box_swarm.add_trace(go.Scatter(
#             x=["Male"] * len(df_male),
#             y=df_male[y_col],
#             mode="markers",
#             marker=dict(
#                 size=7,
#                 color="#1f5fbf",
#                 opacity=0.8
#             ),
#             showlegend=False
#         ))

#         # FEMALE BOX
#         fig_box_swarm.add_trace(go.Box(
#             x=["Female"] * len(df_female),
#             y=df_female[y_col],
#             name="Female",
#             boxmean=True,
#             line=dict(color="#E8729A"),
#             fillcolor="rgba(232,114,154,0.3)"
#         ))

#         # FEMALE SWARM
#         fig_box_swarm.add_trace(go.Scatter(
#             x=["Female"] * len(df_female),
#             y=df_female[y_col],
#             mode="markers",
#             marker=dict(
#                 size=7,
#                 color="#c2185b",
#                 opacity=0.8
#             ),
#             showlegend=False
#         ))

#         fig_box_swarm.update_layout(
#             title=title,
#             margin=dict(t=30, b=10),
#             boxmode="overlay",
#             yaxis = dict(title = "Years"),
#             xaxis = dict(title = " ")
#         )

#         st.plotly_chart(fig_box_swarm, use_container_width=True)





# TABELLA NASCOSTA
#cols_to_show = ["Subject ID", "Age", "Gender", "Race", "Height (in)", "Weight (kg)"]

# if scelta_gruppo == "PD Patients":
#     cols_to_show.append("Years since PD diagnosis")

# if scelta_gruppo == "All":
#     cols_to_show.append("Group")

# with st.expander("📄 Visualizza dati filtrati"):
#     st.dataframe(
#         df[cols_to_show].reset_index(drop=True),
#         use_container_width=True
#     )