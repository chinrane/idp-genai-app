import boto3 
import json

#make this a class

access_key_id = st.secrets["access_key_id"]
secret_access_key = st.secrets["secret_access_key"]
region = "us-east-2"
session = boto3.session.Session(aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key, region_name=region)

# Create a low-level client representing Amazon SageMaker Runtime
sagemaker_runtime = session.client("sagemaker-runtime", region_name=region)
endpoint_name = 'jumpstart-dft-hf-text2text-flan-t5-xxl'

def query_endpoint(encoded_text):
    return sagemaker_runtime.invoke_endpoint(
        EndpointName=endpoint_name,
        ContentType='application/x-text',
        Body=encoded_text,
    )    

def parse_response(query_response):
    model_predictions = json.loads(query_response['Body'].read())
    return model_predictions['generated_text']

def classification(textract_text):
    prompt_text = f"Given the following text, is this document an SEC filing document or something else? {textract_text}"
    query_response = query_endpoint(json.dumps(prompt_text).encode('utf-8'))
    return parse_response(query_response)  

def summarization(textract_text):
    prompt_text = f"Given the following text, provide a numbered list of key information for this document. {textract_text}"
    query_response = query_endpoint(json.dumps(prompt_text).encode('utf-8'))
    return parse_response(query_response)  

def math_llm(textract_text):
    prompt_text = f"From the following document, what is delta between the total leased square footage and the total owned square footage? {textract_text}"
    query_response = query_endpoint(json.dumps(prompt_text).encode('utf-8'))
    return parse_response(query_response)

def main(prompt):
    prompt_text = f"From the following document, what is total owned square footage for North America? {prompt}"
    query_response = query_endpoint(json.dumps(prompt_text).encode('utf-8'))
    return parse_response(query_response)

if __name__ == "__main__":
    
    prefix = "from this document ----"
    test_document = "Mary Jane Smith 100 Pine Street Metro, AA 09371 ## Account Summary : | 0 | 1 | |---------------------------------|-----------| | Opening Balance | $5,234.09 | | Withdrawals | $2,395.67 | | Deposits | $2,872.45 | | Closing Balance on Apr 18, 2010 | $5,710.87 | ## You are eligible for a $100 bonus Scan this QR code with your Smartphone To find out more about a High Interest Savings Account - with the first $100 Deposit on us! You may need to get a QR Codex reader from your SmartPhone App Store ## Your Transaction Details For Mar 15, 2010 to Apr 18, 2010 Account Number : 00-123456 Branch Transit Number : 098765 ## Contact Information : 1-800-222-0123 Contact us by phone for questions, on this statement, change of personal information, and general inquiries, 24 hours a day. 7 days a week TTY for the hearing impaired: 1-800-123-0007 Outside North America: +1-123-4567 Your branch : Main and Elm 100 Main Street Metropolis, AA 01234 | Date | Details | Withdrawals | Deposits | Balance | |--------|-------------------|-----------------|------------|-----------| | Apr 8 | Opening Balance | | | 5,234.09 | | Apr 8 | Insurance | | 272.45 | 5,506.54 | | Apr 10 | ATM | 200.00 | | 5,306.54 | | Apr 12 | Internet Transfer | | 250.00 | 5,556.54 | | Apr 12 | Payroll | | 2100.00 | 7,656.54 | | Apr 13 | Bill payment | 135.07 | | 7,521.47 | | Apr 14 | Direct debit | 200.00 | | 7,321.47 | | Apr 14 | Deposit | | 250.00 | 7.567.87 | | Apr 15 | Bill payment | 525.72 | | 7,042.15 | | Apr 17 | Bill payment | 327.63 | | 6,714.52 | | Apr 17 | Bill payment | 729.96 | | 5,984.56 | | Apr 18 | Bill payment | 223.69 | | 5,710.87 | | | | Closing Balance | | $5,710.87 |"
    question = "--- can you calculate the mathematical sum for the deposits column?"

    payload = f"{prefix}{test_document}{question}"
    print(main(payload))