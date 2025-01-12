from helper import get_university_dataframe, normalize_weights
from recommend import Recommender
import streamlit as st
import numpy as np
import pandas as pd

## Page Configurations
st.set_page_config(
    page_title="UniForMe - University Recommendation System",
    page_icon="🎓",
    layout="wide",
)

recommender = Recommender(
    'university_dict.pkl', 
    'university_by_user_dict.pkl', 
    'university_dict_dataset.pkl'
)

universities_df = get_university_dataframe(recommender.university_dict)

university_data = universities_df.groupby("Academy")["CourseNameShort"].apply(list).to_dict()

title_style = """
    <style>
    .title-container {
        text-align: center;
        margin-top: -50px;
        margin-bottom: 20px;
    }
    .title {
        font-size: 3rem;
        font-weight: bold;
        color: #FF4B4B; /* Cool red color */
    }
    .subtitle {
        font-size: 1.5rem;
        color: #6C757D; /* Cool grey for the subtitle */
        font-style: italic;
    }
    </style>
"""
st.markdown(title_style, unsafe_allow_html=True)
st.markdown(
    """
    <div class="title-container">
        <div class="title">UniForMe</div>
        <div class="subtitle">Your Personalized University Recommendation System</div>
    </div>
    """,
    unsafe_allow_html=True
)
# Custom CSS for the landing page description
description_style = """
    <style>
    .description-container {
        text-align: center;
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
        margin-bottom: 20px;
    }
    .description-text {
        font-size: 1.2rem;
        color: #6C757D;
        line-height: 1.8;
        margin-top: 10px;
    }
    </style>
"""

st.markdown(description_style, unsafe_allow_html=True)

st.markdown(
    """
    <div class="description-container">
        <div class="description-text">
            UniForMe is an AI-driven university recommendation system designed to help you discover the best German universities 
            for pursuing a master's degree in computer science. Tailored to your preferences, the system considers factors like 
            job density, travel connections, and city importance to provide personalized recommendations.
            <br><br>
            Whether you're looking for a vibrant city with ample job opportunities or a quiet town with a strong academic focus, 
            UniForMe ensures you make an informed decision for your future. Let's find your dream university together!
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


user_preference, check_university_neighbour, by_university, by_description = st.tabs(["By User Preference", "Check University Neighbour", "By University", "By Description"])


## UI Components
with user_preference:

    with st.form("uni_form"):
                
        job_density_city = st.slider("How important is it for your city to have strong job prospects in your field?", 0, 10, 5)
        with st.expander("See explanation"):
            st.write('''
                1 : Jobs don’t matter my focus is education. \n
                10: The city must have a thriving job market with ample opportunities.
            ''')
            
        job_density_neighbour_city = st.slider("How important are job opportunities in cities close to your university?", 0, 10, 5)
        with st.expander("See explanation"):
            st.write('''
                1 : I don’t care about job opportunities in neighboring cities. \n
                10: I want to have a variety of job opportunities in neighboring cities.
            ''')

        travel_connections = st.slider("How well-connected should your university’s location be?", 0, 10, 5)
        with st.expander("See explanation"):
            st.write('''
                1 : I don’t care about travel connections. \n
                10: I want to have easy access to public transport and airports.
            ''')

        city_importance = st.slider("Do you prefer your university in a small town, city, or metro area?", 0, 10, 5)
        with st.expander("See explanation"):
            st.write('''
                1 : I prefer small-town simplicity and peace. \n
                10 : I need a vibrant metropolitan lifestyle with dynamic opportunities.
            ''')

        submitted = st.form_submit_button("Submit Preferences")

    if submitted:
        
        form_data = {
            "Jobs in City": job_density_city,
            "Job_Density_Neighbor": job_density_neighbour_city,
            "Connectivity_Score": travel_connections,
            "City_Importance_Score": city_importance
        }
        normalized_weights = normalize_weights(form_data)
        recommendations = recommender.recommend_by_user_preference(normalized_weights)
        st.write("### Recommended Universities and Courses:")
        st.caption("Disclaimer: Our AI has curated these recommendations for you. Verify the details to ensure they match your expectations.")
        st.write(recommendations)

        
        
with check_university_neighbour:
    
    selected_university = st.selectbox("Select a University", options=list(university_data.keys()), key="university_neighbour_selector")
    
    if st.button("Submit"):
        
        neighbour_university = recommender.get_university_neighbour(selected_university)
        
        st.write("### Neighbour Universities:")
        st.caption("Disclaimer: We've generated this data for you using AI! Be sure to review and confirm it before making decisions.")
        st.write(neighbour_university)   

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
        recommeded_result = recommender.recommend_by_uni_and_course(recommendation_data["Selected University"], recommendation_data["Selected Course"])

        if recommeded_result:
            
            st.write("### Recommended Universities and Courses:")
            recommendations_df = pd.DataFrame(recommeded_result, index=np.arange(1, len(recommeded_result)+1))
            st.caption("Disclaimer: Our AI has curated these recommendations for you. Verify the details to ensure they match your expectations.")
            st.table(recommendations_df)
            
        else:
            st.write("No recommendations found.")
            
with by_description:
    
    description = st.text_area("Enter a paragraph describing your preferences",
                                placeholder="I am passionate about data science and analytics, with hands-on experience in data preprocessing, statistical modeling...",
                                height=200)

    if st.button("Submit Description"):
        
        if description == "":
            st.error("Please enter a paragraph describing your preferences.")
            st.stop()
        
        recommendations = recommender.recommend_by_paragraph(description)
        
        if recommendations:
            st.write("### Recommended Universities and Courses:")
            recommendations_df = pd.DataFrame(recommendations, index=np.arange(1, len(recommendations)+1))
            st.caption("Disclaimer: Our AI has curated these recommendations for you. Verify the details to ensure they match your expectations.")
            st.table(recommendations_df)
            
        else:
            st.write("No recommendations found.")




footer_style = """
    <style>
    .footer {
        position: relative;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #0e1117;
        color: white;
        text-align: center;
        padding: 10px 0;
        font-size: 14px;
    }
    </style>
"""
st.markdown(footer_style, unsafe_allow_html=True)
st.markdown('<div class="footer">Made with ❤️ by <b>Rohit, Gaurav and Hetvi</b></div>', unsafe_allow_html=True)