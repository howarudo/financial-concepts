import streamlit as st

st.set_page_config(
    page_title="Financial Concepts",
    page_icon="💰",
)

st.sidebar.success("Select a concept from above.")

st.markdown("""
            # Financial Concepts

            A collection of market concepts, trading strategies, and investment principles visualized in Python.

            [**By Howard T.**](https://howarudo.github.io/)
            """)

st.markdown("""## Trading Strategies""")

st.page_link("pages/1_Golden_Cross_Death_Cross.py", label="Golden Cross & Death Cross", icon="📈")

st.markdown("""## Market Concepts""")

st.page_link("pages/2_The_Yield_Curve.py", label="The Yield Curve", icon="📈")
