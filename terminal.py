import streamlit as st

pages = {
    "Market": [
        st.Page("indices.py", title="Equity"),
        st.Page("yield.py", title="Fixed Income"),
        st.Page("currency.py", title="Currency"),
        st.Page("economic.py", title="Economic Indicators"),
        st.Page("heatmap.py", title="Heat Map")
    ],
    "Analysis": [
        st.Page("performance.py", title="Performance & Risk"),
        st.Page("portfolio.py", title="Portfolio Optimization"),
        st.Page("factors.py", title="Factor"),
        st.Page("peers.py", title="Peer Group"),
    ],
    "Model": [
        st.Page("options.py", title="Options"),
        st.Page("alm.py", title="Yield Curve"),
    ],
}

st.set_page_config(page_title="Financial Terminal", layout="wide")
pg = st.navigation(pages, position="top")
pg.run()
