import streamlit_dataframe as st
import pandas as pd
import plotly.express as px
import numpy as np


@st.cache_data
def get_un_data() -> pd.DataFrame:
    aws_bucket_url = "https://streamlit-demo-data.s3-us-west-2.amazonaws.com"
    df = pd.read_csv(aws_bucket_url + "/agri.csv.gz")
    return df.set_index("Region")  # type: ignore[no-any-return, unused-ignore]

try:
    df = get_un_data()
    countries = st.multiselect(
        "Choose countries", list(df.index), ["China", "United States of America"]
    )
    if not countries:
        st.error("Please select at least one country.")
    else:
        data = df.loc[countries]
        data /= 1000000.0
        st.subheader("Gross agricultural production ($B)")
        st.dataframe(data.sort_index())

        data = data.T.reset_index()
        data = pd.melt(data, id_vars=["index"]).rename(
            columns={"index": "year", "value": "Gross Agricultural Product ($B)"}
        )
        chart = (
            alt.Chart(data)
            .mark_area(opacity=0.3)
            .encode(
                x="year:T",
                y=alt.Y("Gross Agricultural Product ($B):Q", stack=None),
                color="Region:N",
            )
        )
        st.altair_chart(chart, width="stretch")
except URLError as e:
    st.error(f"This demo requires internet access. Connection error: {e.reason}")