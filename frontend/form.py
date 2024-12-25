import streamlit as st

def process_form_data(data):
    st.write("Form Data Received:", data)

st.title("UniForMe")

with st.form("uni_form"):
    course_type = st.radio("Course Type", ["Specialized", "General Computer Science"])

    specialized_detail = None
    if course_type == "Specialized":
        specialized_detail = st.text_input("Please specify your specialization")

    language = st.radio("Preferred Language", ["English (En)", "German (De)"])

    num_semesters = st.selectbox("Number of Semesters", [2, 3, 4, 5, 6, 7, 8])

    university_type = st.radio("Type", ["Public", "Private"])

    uni_type = st.radio("University Type", ["TU", "TH"])

    city_area = st.slider("City Area Preference", 0.0, 1.0, 0.5)

    job_opportunities = st.slider("Job Opportunities", 0.0, 1.0, 0.5)

    additional_summary = st.text_area("Additional Summary", placeholder="Enter any additional preferences or comments here...")

    submitted = st.form_submit_button("Submit")

if submitted:
    form_data = {
        "Course Type": course_type,
        "Specialze Subject" : specialized_detail,
        "Language": language,
        "Number of Semesters": num_semesters,
        "Type": university_type,
        "University Type": uni_type,
        "City Area": city_area,
        "Job Opportunities": job_opportunities,
        "Additional Summary": additional_summary
    }
    process_form_data(form_data)
