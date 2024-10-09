import streamlit as st
import requests
from transformers import GPT2Tokenizer, GPT2LMHeadModel

# Load the pre-trained GPT2 tokenizer and model
tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
model = GPT2LMHeadModel.from_pretrained('gpt2')

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

# Streamlit UI components
st.title("Clinical Drug Information Search")
drug_name = st.text_input("Enter the Drug Name:", "")

if st.button("Search"):
    # Query OpenFDA API and retrieve drug data
    fda_data = query_openfda(drug_name)
    if fda_data:
        # Extract and display relevant information
        drug_info = extract_relevant_info(fda_data)
        st.write("Drug Information:")
        st.json(drug_info)
