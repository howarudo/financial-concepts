import streamlit as st

st.set_page_config(
    page_title="Financial Concepts",
    page_icon="💰",
)

st.sidebar.success("Select a concept from above.")

st.markdown("""
            # Financial Analysis & Market Concepts

            A collection of market concepts, trading strategies, and investment principles visualized in Python.

            By [**Howard T.**](https://howarudo.github.io/)
            """)

st.markdown("""### Quantitative Analysis""")
st.page_link("pages/1_The_NVIDIA_Miracle.py", label="**The NVIDIA Miracle: A Comprehensive Analysis** (*15 min read*)", icon="📈"    )
st.page_link("pages/2_Event_Study_Analysis.py", label="**Event Study Analysis: An Introduction** (*5 min read*)", icon="📈")

st.markdown("### Other Concepts")
st.page_link("pages/3_The_Yield_Curve.py", label="**The Yield Curve** (*8 min read*)", icon="📈")
st.page_link("pages/4_Golden_Cross_Death_Cross.py", label="**Golden Cross & Death Cross** (*4 min read*)", icon="📈")
