#HISTOGRAM
fig = px.histogram(
    df,
    x=col_age,
    nbins=20,
    title="Distribuzione età"
)
st.plotly_chart(fig)

#codice base
fig = px.histogram(df, x="colonna")
fig.show()



#TORTA
fig = px.pie(
    df,
    names=col_sex,
    title="Distribuzione genere"
)
st.plotly_chart(fig)

#codice base
fig = px.pie(df, names="categoria")
fig.show()



#BAR
fig = px.bar(
    df,
    x=col_sex,
    title="Numero pazienti per genere"
)
st.plotly_chart(fig)

#codice base
fig = px.bar(df, x="categoria")
fig.show()



#BOX 
fig = px.box(
    df,
    x=col_sex,
    y=col_age,
    title="Età per genere"
)
st.plotly_chart(fig)

#codice base
fig = px.box(df, x="categoria", y="valore")
fig.show()



#SWARM
fig = px.strip(
    df,
    x=col_sex,
    y=col_age,
    color=col_sex,
    title="Distribuzione pazienti"
)
st.plotly_chart(fig)

#codice base
fig = px.strip(df, x="categoria", y="valore")
fig.show()



#SCATTER
fig = px.scatter(
    df,
    x="Weight (kg)",
    y=col_age,
    color=col_sex
)
st.plotly_chart(fig)

#codice base
fig = px.scatter(df, x="x", y="y")
fig.show()



#VIOLIN PLOT 
fig = px.violin(
    df,
    x=col_sex,
    y=col_age,
    box=True
)
st.plotly_chart(fig)

#codice base
fig = px.violin(df, x="categoria", y="valore")
fig.show()