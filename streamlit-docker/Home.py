import streamlit as st



st.set_page_config(layout="wide")

st.title('Conversation with Documents')
st.subheader('Powered by AWS Generative AI and AI Services for SEC Document Processing.')

st.info(
    """**DISCLAIMER:** 
    This demo uses a HuggingFace large language model and not intended to collect any personally identifiable information (PII) from users. 
    Please do not provide any PII when interacting with this demo. The content generated by this demo is for informational purposes only.
    """
    )


st.subheader('**About this Demo**')
st.success(
    """**Conversation with Documents** is a Generative AI and AWS IDP-based document assistant that can quickly extract data, categorize documents, extract insights, summarize, and have conversation with any types of documents."""
    ) 

st.subheader("""
        Select an Industry Demo from the sidebar to get started.
        """)



