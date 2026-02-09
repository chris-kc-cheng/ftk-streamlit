import streamlit as st

pages = {
    "Market": [
        st.Page("indices.py", title="Equity"),
        st.Page("yield.py", title="Fixed Income"),
        st.Page("economic.py", title="Economic Indicators"),
        st.Page("heatmap.py", title="Heat Map")
    ],
    "Analysis": [
        st.Page("portfolio.py", title="Portfolio"),
        st.Page("factors.py", title="Factor"),
        st.Page("peers.py", title="Peer Group"),
    ],
    "Model": [
        st.Page("options.py", title="Options"),
        st.Page("alm.py", title="Yield Curve"),
    ],
}

pg = st.navigation(pages, position="top")
pg.run()