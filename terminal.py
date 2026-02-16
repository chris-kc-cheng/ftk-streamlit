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
        st.Page("factors.py", title="Factor Exposure"),
        st.Page("peers.py", title="Peer Group"),
    ],
    "Model": [
        st.Page("options.py", title="Options"),
        st.Page("alm.py", title="Yield Curve"),
        st.Page("linking.py", title="Multi-Period Linking"),
    ],
}

st.set_page_config(
    page_title="Financial Terminal",
    page_icon=":material/terminal:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://chris-kc-cheng.github.io/financial-toolkit/toolkit.html",
        "Report a bug": "https://github.com/chris-kc-cheng",
        "About": "https://www.linkedin.com/in/chris-kc-cheng/"
    }
)

st.logo('images/icon.png', icon_image='images/icon.png', size='large')
pg = st.navigation(pages, position="top")
pg.run()
