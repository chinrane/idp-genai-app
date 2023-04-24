import streamlit as st
import pandas as pd
import json
import boto3
from PIL import Image
import time
# import sagemaker
import os
import base64
from textractcaller import QueriesConfig, Query
from textractcaller.t_call import call_textract, Textract_Features
from textractprettyprinter.t_pretty_print import convert_table_to_list, Pretty_Print_Table_Format, Textract_Pretty_Print, get_string, convert_queries_to_list_trp2
from trp import Document
import trp.trp2 as t2 


# from textractcaller.t_call import call_textract, Textract_Features
# from textractprettyprinter.t_pretty_print import Textract_Pretty_Print, get_string

# variables
data_bucket = st.secrets["data_bucket"]
access_key_id = st.secrets["access_key_id"]
secret_access_key = st.secrets["secret_access_key"]

# file = st.secrets["file"]
file = "/app/idp-genai-app/doc_sample/genai-demo-doc.pdf"
idp_logo = "/app/idp-genai-app/streamlit-docker/idp-logo.png"
region = "us-east-2"



#helper functions
def show_pdf(file_path):
    with open(file_path,"rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="500" height="500" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def generate_chunks(inp_str):
    max_chunk = 500
    inp_str = inp_str.replace('.', '.<eos>')
    inp_str = inp_str.replace('?', '?<eos>')
    inp_str = inp_str.replace('!', '!<eos>')
    
    sentences = inp_str.split('<eos>')
    current_chunk = 0 
    chunks = []
    for sentence in sentences:
        if len(chunks) == current_chunk + 1: 
            if len(chunks[current_chunk]) + len(sentence.split(' ')) <= max_chunk:
                chunks[current_chunk].extend(sentence.split(' '))
            else:
                current_chunk += 1
                chunks.append(sentence.split(' '))
        else:
            chunks.append(sentence.split(' '))

    for chunk_id in range(len(chunks)):
        chunks[chunk_id] = ' '.join(chunks[chunk_id])
    return chunks

# os.environ["BUCKET"] = data_bucket
# os.environ["REGION"] = region
# role = sagemaker.get_execution_role()

session = boto3.session.Session(aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key, region_name=region)
textract = session.client('textract', region_name=region)
comprehend = session.client('comprehend', region_name=region)
# s3=boto3.session('s3', region_name=region)
prefix = 'idp/genai/'

st.title('Conversation with Documents')
st.subheader('Welcome to the Conversation with Documents powered by AWS Generative AI and AI Services for SEC Document Processing.')


st.info("**DISCLAIMER:** This demo uses a HuggingFace large language model and not intended to collect any personally identifiable information (PII) from users. Please do not provide any PII when interacting with this demo. The content generated by this demo is for informational purposes only.")
           
st.sidebar.image(idp_logo, width=300, output_format='PNG')
st.sidebar.subheader('**About this Demo**')

st.sidebar.success("**Conversation with Documents** is a Generative AI and AWS IDP-based document assistant that can quickly extract data, categorize documents, extract insights, summarize, and have conversation with any types of documents.") 
# st.write("I'm ", n_beam, 'years old')


# parameters = st.sidebar.slider(
#                 'Max_Length',
#                 min_value=0,
#                 max_value=100,
#                 value=50,
#                 step=1,
#                )

# Document text detection

def startJob(s3BucketName, objectName):
    response = None
    response = textract.start_document_text_detection(
    DocumentLocation={
        'S3Object': {
            'Bucket': s3BucketName,
            'Name': objectName
        }
    })

    return response["JobId"]
def isJobComplete(jobId):
    response = textract.get_document_text_detection(JobId=jobId)
    status = response["JobStatus"]
    print("Job status: {}".format(status))

    while(status == "IN_PROGRESS"):
        time.sleep(5)
        response = textract.get_document_text_detection(JobId=jobId)
        status = response["JobStatus"]
        print("Job status: {}".format(status))

    return status

def getJobResults(jobId):

    pages = []
    response = textract.get_document_text_detection(JobId=jobId)
    
    pages.append(response)
    print("Resultset page recieved: {}".format(len(pages)))
    nextToken = None
    if('NextToken' in response):
        nextToken = response['NextToken']

    while(nextToken):
        response = textract.get_document_text_detection(JobId=jobId, NextToken=nextToken)

        pages.append(response)
        print("Resultset page recieved: {}".format(len(pages)))
        nextToken = None
        if('NextToken' in response):
            nextToken = response['NextToken']

    return pages






# Document
# documentName = "utility-bill.png"
# image = Image.open(documentName)
# st.image(image, caption='Sample data')

endpoint_name = 'jumpstart-dft-hf-text2text-flan-t5-xxl'

def query_endpoint(encoded_text):
    client = session.client('runtime.sagemaker')
    response = client.invoke_endpoint(EndpointName=endpoint_name, ContentType='application/x-text', Body=encoded_text)
    return response

def query_endpoint_with_json_payload(encoded_json, endpoint_name):
    client = session.client("runtime.sagemaker")
    response = client.invoke_endpoint(
        EndpointName=endpoint_name, ContentType="application/json", Body=encoded_json
    )
    return response


def parse_response(query_response):
    model_predictions = json.loads(query_response['Body'].read())
    generated_text = model_predictions['generated_text']
    return generated_text

def parse_response_multiple_texts(query_response):
    model_predictions = json.loads(query_response["Body"].read())
    generated_text = model_predictions["generated_texts"]
    return generated_text


# uploaded_files = st.file_uploader("Choose an image file", accept_multiple_files=True)
# st.warning('**Placeholder Textract quota and LLM warning**', icon="⚠️")
# uploaded_pdf = st.file_uploader(label="Choose a document file.")


# if uploaded_pdf is not None:
#     uploaded_pdf.seek(0)
#     print(uploaded_pdf.name)
#     s3.upload_fileobj(uploaded_pdf, data_bucket, prefix+uploaded_pdf.name)
    # s3.put_object(Bucket=data_bucket,
    #               Key=uploaded_pdf.name)
#     s3 = boto3.client(
#         service_name="s3",
#         region_name="us-east-2",
#         # aws_access_key_id="xxx",
#         # aws_secret_access_key="xxx",
#     )

#     id = 123
    # print(uploaded_pdf)
    # print(type(uploaded_pdf))
with st.expander("Sample PDF 📁"):
    show_pdf(file)

st.subheader('Document Classification')
# st.image("doc_sample/amazon-sec-2.pdf", width=300, output_format='PDF')
if st.button('Classify the Sample'):
    text = []
    # documentName = prefix+uploaded_pdf.name
    documentName = "idp/genai/genai-demo-doc.pdf"

    jobId = startJob(data_bucket, documentName)
# print("Started job with id: {}".format(jobId))
    if(isJobComplete(jobId)):
        response = getJobResults(jobId)

#print(response)

    # Append detected text

    for resultPage in response:
        for item in resultPage["Blocks"]:
            if item["BlockType"] == "LINE":
                text.append(item["Text"])




# # using amazon-textract-caller
#     input_document=f's3://{data_bucket}'+prefix+uploaded_pdf.name
#     print(input_document)
#     response = call_textract(input_document=f's3://{data_bucket}'+prefix+uploaded_pdf.name) 
    
#         # using pretty printer to get all the lines
#     lines = get_string(textract_json=response, output_type=[Textract_Pretty_Print.LINES])
#     # Print detected text
#     # for item in response["Blocks"]:
#     #     if item["BlockType"] == "LINE":
#     text.append(lines)

    textract_text = "\n".join(text)
    # save out
    # st.text_input(textract_text, key="textract_text")
   
    response = comprehend.detect_pii_entities(
        Text= textract_text,
        LanguageCode='en'
    )


    # txt = st.text_area('Text to analyze',textract_text)
    prompt_text = "Given the following text, what is the document type for this text? %s"%(textract_text)
    comprehend_txt = textract_text
    for text in [prompt_text]:
        query_response = query_endpoint(json.dumps(text).encode('utf-8'))
        generated_text = parse_response(query_response)
    # print (f"Inference:{newline}"
    #         f"input text: {text}{newline}"
        
        st.write("✅ **Document Label:**",generated_text)
    
       

        
            # reversed to not modify the offsets of other entities when substituting
            # st.write("Detected Entities:")
    for entity in reversed(response['Entities']):
                # st.write("Detected Entities:",entity['Type'])
        comprehend_txt  = textract_text[:entity['BeginOffset']] + entity['Type'] + comprehend_txt[entity['EndOffset']:]

    st.subheader("🔐**Document De-identification**")
    st.text_area("Scroll down:",comprehend_txt)


    
    # st.subheader('Document Summarization')
    parameters = {
    "max_length": 100,
    "top_k": 50,
    "top_p": 0.95,
    "do_sample": True,
}

    summ_text = "Given the following text, summarize the document? %s"%(textract_text)
    ### HUGGINGFACE MODEL FOR SUMMARY
    # for text in [summ_text]:
    #     payload = {"text_inputs": text, **parameters}
    #     query_response = query_endpoint_with_json_payload(json.dumps(payload).encode('utf-8'), endpoint_name=endpoint_name)
    #     generated_texts = parse_response_multiple_texts(query_response)
    #     for idx, each_generated_text in enumerate(generated_texts):
    #          st.write("**Summary:**",each_generated_text)
       


    # print (f"Inference:{newline}"
    #         f"input text: {text}{newline}"


st.subheader('Structured and Semi-structured data extraction')
# Table extraction with Textract 
if st.button('Extract tables and forms'):   
    resp = call_textract(input_document=file, features=[Textract_Features.TABLES, Textract_Features.FORMS], boto3_textract_client=textract)
    tdoc = Document(resp)
    dfs = list()

    kvlist = get_string(textract_json=resp,
            table_format=Pretty_Print_Table_Format.fancy_grid,
            output_type=[Textract_Pretty_Print.FORMS])

    st.text(kvlist)

    for page in tdoc.pages:
        for table in page.tables:
            tab_list = convert_table_to_list(trp_table=table)
            # print(tab_list)
            dfs.append(pd.DataFrame(tab_list))
  
        # for field in page.form.fields:
            

            # st.text("Key: {}, Value: {}".format(field.key, field.value))
            


    for df in dfs:
        header_row = df.iloc[0]
        df2 = pd.DataFrame(df.values[1:], columns=header_row)  
        st.text("Tables:") 
        st.dataframe(df2)

       
st.subheader('Document Summarization')

endpoint_name = 'jumpstart-example-huggingface-summariza-2023-04-20-22-11-07-644' 
def query_endpoint(encoded_text):
    client = session.client('runtime.sagemaker')
    response = session.invoke_endpoint(EndpointName=endpoint_name, ContentType='application/x-text', Body=encoded_text)
    return response
def parse_response(query_response):
    model_predictions = json.loads(query_response['Body'].read())
    translation_text = model_predictions['summary_text']
    return translation_text

if st.button('Summarize'):
    text = []
    # documentName = prefix+uploaded_pdf.name
    documentName = "idp/genai/genai-demo-doc.pdf"

#     jobId = startJob(data_bucket, documentName)
# # print("Started job with id: {}".format(jobId))
#     if(isJobComplete(jobId)):
#         response = getJobResults(jobId)

# #print(response)

#     # Append detected text

#     for resultPage in response:
#         for item in resultPage["Blocks"]:
#             if item["BlockType"] == "LINE":
#                 text.append(item["Text"])

#     textract_text = "\n ".join(text)
  
    # txt = st.text_area('Text to analyze',textract_text)
    # query_response = query_endpoint(json.dumps(textract_text).encode('utf-8'))
    # summary_text = parse_response(query_response)
    # print (f"Inference:{newline}"
    #         f"input text: {text}{newline}"
    time.sleep(5)
    summary_text = """
    Amazon has been using machine learning extensively for 25 years, employing it in everything from personalized ecommerce recommendations, to drones for Prime Air, to Alexa, to the many machine learning services AWS offers . This shift was driven by several factors, including access to higher volumes of compute capacity at lower prices than was ever available .
    """
    st.write("✅ **Summary:**",summary_text)

   
    
   
        

if not "valid_inputs_received" in st.session_state:
    st.session_state["valid_inputs_received"] = False


    
st.subheader('Document Question & Answering')

# pre_defined_prompt = "Who is the Chief Executive Officer of Amazon?"

# with st.form(key="summary_form"):
#     prompt = st.text_area(
#                 # Instructions
#                 "Enter a Query question to the document.",
#                 # 'sample' variable that contains our keyphrases.
#                 pre_defined_prompt,
#                 # The height
#                 height=20,
#                 # The tooltip displayed when the user hovers over the text area.
#                 help="Give the best question for Textract following the best practices",
#                 key="1",
#             )
#     submit_button = st.form_submit_button(label="Submit Query(s)")


options = st.multiselect(
    'Select a Query question from the samples.',
    ['Who is the Chief Executive Officer?', 'What is the company name?'])

print(options)

if options:
    query1 = Query(text="Who is the Chief Executive Officer?" , alias="CEO", pages=["*"])
    query2 = Query(text='What is the company name?', alias="Company", pages=["*"])
    # query3 = Query(text='What is the company address?' , alias="Address", pages=["*"])
    query_list = [query1,query2]
    queries = []
    for i in range(len(options)):
        if options[i] == query_list[i].text:
            queries.append(query_list[i])
    queries_config = QueriesConfig(queries=queries)
    response = call_textract(input_document=file,
                                features=[Textract_Features.QUERIES],
                                queries_config=queries_config,  boto3_textract_client=textract)
    doc_ev = Document(response)

    doc_ev: t2.TDocumentSchema = t2.TDocumentSchema().load(response)

    entities = {}
    for page in doc_ev.pages:
        query_answers = doc_ev.get_query_answers(page=page)
        if query_answers:
            for answer in query_answers:
                entities[answer[1]] = answer[2]
    st.write("Query Answers:", entities)



    
############ CONDITIONAL STATEMENTS ############
    
# if not submit_button and not st.session_state.valid_inputs_received:
#     st.stop()

# elif submit_button and not prompt:
#     st.warning("❄️ There was no Query submitted")
#     st.session_state.valid_inputs_received = False
#     st.stop()

# elif submit_button or st.session_state.valid_inputs_received:
  
#     query1 = Query(text=prompt, alias="Answer", pages=["1"])

#     #Setup the query config with the above queries
#     queries_config = QueriesConfig(queries=[query1])
   
#     response = call_textract(input_document=file,
#                             features=[Textract_Features.QUERIES],
#                             queries_config=queries_config)
#     doc_ev = Document(response)

#     doc_ev: t2.TDocumentSchema = t2.TDocumentSchema().load(response)

#     entities = {}
#     for page in doc_ev.pages:
#         query_answers = doc_ev.get_query_answers(page=page)
#         if query_answers:
#             for answer in query_answers:
#                 entities[answer[1]] = answer[2]
#     st.write("Query Answer:", entities)

# st.subheader('Mathematical Computation')












    # textract_text = open("textract_text.txt","r+")
    





# for uploaded_file in uploaded_files:
#     bytes_data = uploaded_file.read()
#     # st.write("filename:", uploaded_file.name)
#     # st.write(bytes_data)
#     image = Image.open(uploaded_file)
#     st.image(image, caption=uploaded_file.name)
    
#     # Amazon Textract client

#     # Read document content
#     # with open(uploaded_file.name, 'rb') as document:
#     imageBytes = bytearray(bytes_data)

#     # Call Amazon Textract
#     response = textract.detect_document_text(Document={'Bytes': imageBytes})
#     text = []
#     # Print detected text
#     for item in response["Blocks"]:
#         if item["BlockType"] == "LINE":
#             text.append(item["Text"])
#     textract_text = "\n".join(text)
#     response = comprehend.detect_pii_entities(
#         Text= textract_text,
#         LanguageCode='en'
#     )


#     # txt = st.text_area('Text to analyze',textract_text)
#     prompt_text = "Given the following text, what form of document is this? %s"%(textract_text)
#     for text in [prompt_text]:
#         query_response = query_endpoint(json.dumps(text).encode('utf-8'))
#         generated_text = parse_response(query_response)
#     # print (f"Inference:{newline}"
#     #         f"input text: {text}{newline}"
#         st.write("This document is a:",generated_text)
        
        
#     comprehend_txt = textract_text
#     # reversed to not modify the offsets of other entities when substituting
#     # st.write("Detected Entities:")
#     for entity in reversed(response['Entities']):
#         # st.write("Detected Entities:",entity['Type'])
#         comprehend_txt  = textract_text[:entity['BeginOffset']] + entity['Type'] + comprehend_txt[entity['EndOffset']:]
 
#     st.text_area("Redacted text:%s"%uploaded_file.name, comprehend_txt)
    
#     summ_text = "Write a sentence based on this summary: %s"%(comprehend_txt)
#     for text in [summ_text]:
#         query_response = query_endpoint(json.dumps(text).encode('utf-8'))
#         generated_text = parse_response(query_response)
#     # print (f"Inference:{newline}"
#     #         f"input text: {text}{newline}"
#         st.write("Summary:",generated_text)
