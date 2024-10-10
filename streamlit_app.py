import streamlit as st
import requests
from transformers import GPT2Tokenizer, GPT2LMHeadModel, pipeline

# Load the GPT-2 tokenizer and model
tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
model = GPT2LMHeadModel.from_pretrained('gpt2')

# Hugging Face pipeline for text generation
generator = pipeline('text-generation', model=model, tokenizer=tokenizer)

# Function to query the OpenFDA API for drug information
def query_openfda(drug_name):
    base_url = 'https://api.fda.gov/drug/label.json'
    params = {'search': f'openfda.brand_name:{drug_name}', 'limit': 1}
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Could not retrieve data from OpenFDA.")
        return None

# Function to extract relevant drug information
def extract_relevant_info(drug_json):
    if not drug_json:
        return {}
    drug_info = {}
    try:
        drug_info['Brand Name'] = drug_json['results'][0]['openfda']['brand_name'][0]
        drug_info['Generic Name'] = drug_json['results'][0]['openfda']['generic_name'][0]
        drug_info['Indications'] = drug_json['results'][0]['indications_and_usage'][0]
        drug_info['Warnings'] = drug_json['results'][0]['warnings'][0]
        drug_info['Dosage'] = drug_json['results'][0]['dosage_and_administration'][0]
    except KeyError as e:
        st.warning(f"Some fields are missing: {e}")
    return drug_info

# Streamlit UI
st.title("Clinical Drug Information and Query Response Generator")

# Input field for clinicians to enter drug name
drug_name = st.text_input("Enter the Drug Name:", "")

# Input field for clinicians to ask a question
user_prompt = st.text_area("Enter your clinical question:", "")

if st.button("Search and Generate Response"):
    # Query the OpenFDA API and retrieve drug data
    fda_data = query_openfda(drug_name)
    if fda_data:
        # Extract drug information
        drug_info = extract_relevant_info(fda_data)
        st.write("Drug Information:")
        st.json(drug_info)
        
        # Generate a professional answer based on user input and FDA data
        prompt = f"""
        You are a clinician who is looking for detailed, professional information about {drug_name}. 
        Based on the following data, generate a professional, fact-based response:
        
        Drug Information:
        Brand Name: {drug_info.get('Brand Name', 'unknown')}
        Generic Name: {drug_info.get('Generic Name', 'unknown')}
        Indications: {drug_info.get('Indications', 'unknown')}
        Warnings: {drug_info.get('Warnings', 'unknown')}
        Dosage: {drug_info.get('Dosage', 'unknown')}
        
        Question: {user_prompt}
        
        Please respond in a professional tone and provide factual information.
        """
        
        # Generate a response based on the user prompt and drug information
        generated_response = generator(prompt, max_length=200, num_return_sequences=1)
        st.write("Generated Response:")
        st.write(generated_response[0]['generated_text'])
