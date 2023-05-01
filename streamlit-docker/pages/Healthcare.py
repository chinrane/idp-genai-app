import boto3
import streamlit as st
import pandas as pd
import numpy as np
from utils.model_interface import classification, summarization
from utils.textract_interface import detect_tables_forms, detect_text

#static files
idp_logo = "/app/idp-genai-app/streamlit-docker/idp-logo.png" 
idp_demo_data = "/app/idp-genai-app/streamlit-docker/static/examples/amazon-sec-demo.pdf"
st.set_page_config(layout="wide")
st.image(idp_logo, width=450, output_format='PNG')
st.subheader('Powered by AWS Generative AI and AI Services for SEC Document Processing.')

st.info(
    """**DISCLAIMER:** 
    This demo uses a HuggingFace large language model and not intended to collect any personally identifiable information (PII) from users. 
    Please do not provide any PII when interacting with this demo. The content generated by this demo is for informational purposes only.
    """
    )

st.header("Select a Demo")


tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "Document Classification", 
        "Structured and Semi-Structured Data Extraction",
        "Document Summarization",
        "Document Question & Answering",
        "Mathematical Calculations",
        ])

# make it so we dont call textract for each button click need to store the text 

with tab1:
    st.header("Document Classification")
    
    # prompt = st.text_area("Enter the text you want to classify", height=200)
    if st.button('Classify the Sample'):
        generated_text = detect_text(idp_demo_data)
        llm_text = classification(generated_text)
        
        st.write("This document is classified as: ",llm_text) 
    
with tab2:
    st.header("Structured and Semi-Structured Data Extraction")
    if st.button('Extract Tables'):
        
        generated_text = detect_tables_forms(idp_demo_data)
        st.dataframe(generated_text)
    
with tab3:
    st.header("Document Summarization")
    if st.button('Summarize the Sample'):
        generated_text = detect_text(idp_demo_data)
        llm_summary = summarization(generated_text)
        
        st.text(llm_summary)

with tab4:
    st.header("Document Question & Answering")
    
with tab5:
    st.header("Mathematical Calculations")