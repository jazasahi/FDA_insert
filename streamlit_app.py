import streamlit as st
import requests

# Define the function to query OpenFDA
def query_openfda(drug_name):
    url = f"https://api.fda.gov/drug/label.json?search=openfda.brand_name:{drug_name}&limit=1"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if "results" in data and len(data["results"]) > 0:
            return data["results"][0]  # Return the first result
        else:
            st.warning(f"No data found for the drug: {drug_name}")
            return None
    else:
        st.error(f"Error {response.status_code}: Could not retrieve data from OpenFDA")
        return None

# Function to filter and organize the drug information
def organize_drug_info(drug_json):
    fields = {
        'Brand Name': ['openfda', 'brand_name'],
        'Generic Name': ['openfda', 'generic_name'],
        'Indications': ['indications_and_usage'],
        'Warnings': ['warnings'],
        'Dosage': ['dosage_and_administration'],
        'Forms and Strength': ['dosage_forms_and_strengths'],
        'Contraindications': ['contraindications'],
        'Precautions': ['warnings_and_cautions'],
        'Adverse Reactions': ['adverse_reactions'],
        'Drug Interactions': ['drug_interactions'],
        'Pregnancy': ['pregnancy'],
        'Pediatric Use': ['pediatric_use'],
        'Geriatric Use': ['geriatric_use'],
        'Overdose': ['overdosage'],
        'Mechanism of Action': ['mechanism_of_action'],
        'Pharmacodynamics': ['pharmacodynamics'],
        'Pharmacokinetics': ['pharmacokinetics'],
        'Clinical Studies': ['clinical_studies'],
        'How Supplied': ['how_supplied'],
        'Instructions for Use': ['instructions_for_use'],
        'NDC': ['package_ndc']
    }
    
    drug_info = {}
    
    for field, path in fields.items():
        try:
            # Traverse the JSON data based on the path in the fields dictionary
            data = drug_json
            for key in path:
                data = data[key]  # Drill down to the required data
            drug_info[field] = data[0] if isinstance(data, list) else data
        except (KeyError, IndexError):
            drug_info[field] = "Information not available"
    
    return drug_info

# Streamlit app code
st.title("Drug Information Query")

# Input field for drug name
drug_name = st.text_input("Enter the drug name:")

if st.button("Get Drug Information"):
    if drug_name:
        drug_data = query_openfda(drug_name)
        if drug_data:
            # Organize the drug information
            drug_info = organize_drug_info(drug_data)
            
            # Display the organized drug information
            for key, value in drug_info.items():
                st.write(f"**{key}:** {value}")
