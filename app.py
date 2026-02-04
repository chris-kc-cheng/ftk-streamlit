import streamlit as st

pages = {
    "Market": [
        st.Page("indices.py", title="Index"),
        st.Page("factors.py", title="Factor"),
        st.Page("peers.py", title="Peers"),
    ],
    "Model": [
        st.Page("options.py", title="BSM"),
        st.Page("alm.py", title="CIR"),
    ],
}

pg = st.navigation(pages, position="top")
pg.run()