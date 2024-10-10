import os
import openai
import requests
import streamlit as st

# Use Streamlit's secrets management to fetch the API key securely
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Function to query the OpenFDA API for drug information based on the user's query
def query_openfda(drug_name):
    url = f"https://api.fda.gov/drug/label.json?search=openfda.brand_name:{drug_name}&limit=1"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if "results" in data:
            return data["results"][0]  # Return the first result
        else:
            st.warning(f"No data found for {drug_name}")
            return None
    else:
        st.error(f"Error {response.status_code}: Could not retrieve data from OpenFDA")
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
        drug_info['Warnings'] = drug_json['results'][0]['boxed_warnings'][0]
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

# Function to generate response using GPT-3.5
def generate_gpt3_response(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use GPT-3.5 Turbo model
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,  # Limit the response length
            temperature=0.7  # Adjust temperature for more controlled, factual output
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        st.error(f"Error generating response: {str(e)}")
        return None

# Streamlit UI
st.title("Clinical Drug Information and Query Response Generator")

# Input field for clinicians to ask a question, including drug name
user_prompt = st.text_area("Enter your clinical question (include the drug name):", "")

if st.button("Search and Generate Response"):
    # Extract the drug name from the user's query (assuming first word as drug name)
    drug_name = user_prompt.split()[0]  # Assuming the drug name is the first word of the prompt
    fda_data = query_openfda(drug_name)

    if fda_data:
        # Extract drug information
        drug_info = extract_relevant_info(fda_data)
        st.write("Drug Information:")
        st.json(drug_info)
        
        # Create the prompt based on user question and FDA data
        prompt = f"""
        You are a clinician looking for detailed, professional information about {drug_name}. 
        Based on the following data, generate a relevant, professional and fact-based response:
        
        Drug Information:
        Brand Name: {drug_info.get('Brand Name', 'unknown')}
        Generic Name: {drug_info.get('Generic Name', 'unknown')}
        Indications: {drug_info.get('Indications', 'unknown')}
        Dosage: {drug_info.get('Dosage', 'unknown')}
        
        Question: {user_prompt}
        
        Respond in a sarcastic tone and provide factual information.
        #change the tone to your liking
        """
        
        # Generate a response using GPT-3.5
        generated_response = generate_gpt3_response(prompt)
        if generated_response:
            st.write("Generated Response:")
            st.write(generated_response)
