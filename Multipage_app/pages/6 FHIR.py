st.set_page_config(page_title="Esportazione FHIR", page_icon="☁", layout="wide")

# LOGIN CHECK
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("⚠️ Please log in from the Homepage.")
    st.stop()
