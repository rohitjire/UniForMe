from recommend import recommend_uni_by_uni
from helper import get_university_dataframe, load_pickle_file
import streamlit as st
import numpy as np
import pandas as pd

university_dict = load_pickle_file('university_dict.pkl', 'rb')

universities_df = get_university_dataframe(university_dict)

university_data = universities_df.groupby("Academy")["CourseNameShort"].apply(list).to_dict()

st.title("UniForMe")

user_preference , by_university = st.tabs(["By User Preference", "By University"])

with user_preference:

    with st.form("uni_form"):
        course_type = st.radio("Course Type", ["Specialized", "General Computer Science"])

        specialized_detail = None
        if course_type == "Specialized":
            specialized_detail = st.text_input("Please specify your specialization")

        language = st.multiselect("Preferred Language", ["English", "German"])

        num_semesters = st.selectbox("Number of Semesters", [2, 3, 4, 5, 6, 7, 8])

        fees = st.slider("Fees", 0, 10000, 5000)

        uni_type = st.radio("University Type", ["Technical University/Technische Universitat", "Technische Hochshule/University of Applied Sciences"])

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
            "Financials": fees,
            "University Type": uni_type,
            "City Area": city_area,
            "Job Opportunities": job_opportunities,
            "Additional Summary": additional_summary
        }


with by_university:

    selected_university = st.selectbox("Select a University", options=list(university_data.keys()), key="university_selector")

    if selected_university:
        courses = university_data[selected_university]
        selected_course = st.selectbox("Select a Course", options=courses, key="course_selector")

    if st.button("Submit Recommendation"):
        recommendation_data = {
            "Selected University": selected_university,
            "Selected Course": selected_course
        }
        recommeded_result = recommend_uni_by_uni(recommendation_data["Selected University"], recommendation_data["Selected Course"])

        if recommeded_result:
            
            st.write("### Recommended Universities and Courses:")
            recommendations_df = pd.DataFrame(recommeded_result, index=np.arange(1, len(recommeded_result)+1))
            st.table(recommendations_df)
            
            # st.write("### Recommended Universities and Courses:")
            # for rec in recommeded_result:
            #     st.write(f"- **{rec['Course Name']}** at **{rec['University']}**")
        else:
            st.write("No recommendations found.")