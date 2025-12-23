import streamlit as st
import pdfplumber
from crewai import Agent, Task, Crew, Process
import os

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Dental Appeal Bot", page_icon="🦷")

# SECURITY STEP: We get the key from the Cloud Secrets, not the code.
# (This will work once we deploy it)
try:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
except:
    # This keeps it working in Replit if you set a Secret there, 
    # but for now, we are prepping for the Cloud.
    pass

# --- 2. AGENTS ---
analyst = Agent(
    role='Dental Claims Analyst',
    goal='Extract Patient Name and Denial Reason.',
    backstory='You are an expert biller. You find the patient name and the reason for denial.',
    verbose=True
)

writer = Agent(
    role='Appeal Writer',
    goal='Write a formal appeal letter.',
    backstory='You are a legal expert. You write professional appeal letters.',
    verbose=True
)

# --- 3. FUNCTIONS ---
def get_pdf_text(uploaded_file):
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text()
        return text
    except:
        return "Error reading PDF."

# --- 4. APP INTERFACE ---
st.title("🦷 Dental Appeal Generator")
st.markdown("### Automated Insurance Defense")

uploaded_file = st.file_uploader("Upload Denial Letter (PDF)", type="pdf")

if uploaded_file is not None:
    st.success("File Uploaded.")

    if st.button("Generate Appeal"):
        with st.spinner('Agents are working...'):

            raw_text = get_pdf_text(uploaded_file)

            task1 = Task(description=f"Analyze: {raw_text}", expected_output='Details', agent=analyst)
            task2 = Task(description="Write formal appeal with Markdown.", expected_output='Letter', agent=writer)

            crew = Crew(agents=[analyst, writer], tasks=[task1, task2])
            result = crew.kickoff()

            st.markdown("### Drafted Appeal")
            st.markdown(result)

            st.download_button("Download Letter", str(result), "Appeal.txt")