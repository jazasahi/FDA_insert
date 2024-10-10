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
        drug_info['Forms and strength'] = drug_json['results'][0]['dosage_forms_and_strengths'][0]
        drug_info['Contraindications'] = drug_json['results'][0]['contraindications'][0]
        drug_info['Precautions'] = drug_json['results'][0]['warnings_and_cautions'][0]
        drug_info['Adverse Reactions'] = drug_json['results'][0]['adverse_reactions'][0]
        drug_info['Drug Interactions'] = drug_json['results'][0]['drug_interactions'][0]
        drug_info['Pregnancy'] = drug_json['results'][0]['Pregnancy'][0]
        drug_info['Pediatric use'] = drug_json['results'][0]['pediatric_use'][0]
        drug_info['Geriatric use'] = drug_json['results'][0]['geriatric_use'][0]
        drug_info['Overdose'] = drug_json['results'][0]['overdosage'][0]
        drug_info['Mechanism of action'] = drug_json['results'][0]['mechanism_of_action'][0]
        drug_info['Pharmacodynamics'] = drug_json['results'][0]['pharmacodynamics'][0]
        drug_info['Pharmacokinetics'] = drug_json['results'][0]['pharmacokinetics'][0]
        drug_info['Clinical Studies'] = drug_json['results'][0]['clinical_studies'][0]
        drug_info['How supplied'] = drug_json['results'][0]['how_supplied'][0]
        drug_info['Instructions for use'] = drug_json['results'][0]['instructions_for_use'][0]
        drug_info['NDC'] = drug_json['results'][0]['package_ndc'][0]
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
        Forms and strength: {drug_info.get('Forms and strength', 'unknown')}
        Contraindications: {drug_info.get('Contraindications', 'unknown')}
        Precautions: {drug_info.get('Precautions', 'unknown')}
        Adverse Reactions: {drug_info.get('Adverse Reactions', 'unknown')}
        Drug Interactions: {drug_info.get('Drug Interactions', 'unknown')}
        Pregnancy: {drug_info.get('Pregnancy', 'unknown')}
        Pediatric use: {drug_info.get('Pediatric use', 'unknown')}
        Geriactric use: {drug_info.get('Geriactric use', 'unknown')}
        Overdose: {drug_info.get('Overdose', 'unknown')}
        Mechanism of action: {drug_info.get('Mechanism of action', 'unknown')}
        Pharmacodynamics: {drug_info.get('Pharmacodynamics', 'unknown')}
        Pharmacokinetics: {drug_info.get('Pharmacokinetics', 'unknown')}
        Clinical Studies: {drug_info.get('Clinical Studies', 'unknown')}
        How supplied: {drug_info.get('How supplied', 'unknown')}
        Instructions for use: {drug_info.get('Instructions for use', 'unknown')}
        NDC: {drug_info.get('NDC', 'unknown')}
        
        Question: {user_prompt}
        
        Please respond in a professional tone and provide factual information.
        """
        
        # Generate a response based on the user prompt and drug information
        generated_response = generator(prompt, max_length=200, num_return_sequences=1)
        st.write("Generated Response:")
        st.write(generated_response[0]['generated_text'])
