from recommend import recommend_by_user_preference, recommend_for_paragraph, recommend_uni_by_uni
from helper import get_university_dataframe, load_pickle_file
import streamlit as st
import numpy as np
import pandas as pd

## Page Configurations
st.set_page_config(
    page_title="UniForMe - University Recommendation System",
    page_icon="🎓",
    layout="wide",
)

## Data Loading
university_dict = load_pickle_file('university_dict.pkl', 'rb')

universities_df = get_university_dataframe(university_dict)

university_data = universities_df.groupby("Academy")["CourseNameShort"].apply(list).to_dict()

st.title("UniForMe")

user_preference, by_university, by_description = st.tabs(["By User Preference", "By University", "By Description"])


## UI Components
with user_preference:

    with st.form("uni_form"):
        job_density_city = st.slider("Job Density in City", 0, 10, 5)

        job_density_neighbour_city = st.slider("Job Density in Neighbor Cities", 0, 10, 5)

        travel_connections = st.slider("Travel Connections", 0, 10, 5)

        city_importance = st.slider("City Importance ", 0, 10, 5)

        submitted = st.form_submit_button("Submit Preferences")

    if submitted:
        
        total_score = job_density_city + job_density_neighbour_city + travel_connections + city_importance

        if total_score > 10:
            st.error("The total score of all inputs exceeds 10. Please adjust the values so that the summation is equal to 10.")
        elif total_score < 10:
            st.error("The total score of all inputs is less than 10. Please adjust the values so that the summation is equal to 10.")
        else:
            form_data = {
                "Jobs in City": job_density_city,
                "Job_Density_Neighbor": job_density_neighbour_city,
                "Connectivity_Score": travel_connections,
                "City_Importance_Score": city_importance
            }
            recommendations = recommend_by_user_preference(form_data)
            st.write("### Recommended Universities and Courses:")
            st.write(recommendations)


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
            
        else:
            st.write("No recommendations found.")
            
with by_description:
    
    description = st.text_area("Enter a paragraph describing your preferences",
                                placeholder="I am passionate about data science and analytics, with hands-on experience in data preprocessing, statistical modeling...",
                                height=200)

    if st.button("Submit Description"):
        recommendations = recommend_for_paragraph(description)
        
        if recommendations:
            st.write("### Recommended Universities and Courses:")
            recommendations_df = pd.DataFrame(recommendations, index=np.arange(1, len(recommendations)+1))
            st.table(recommendations_df)
            
        else:
            st.write("No recommendations found.")
            