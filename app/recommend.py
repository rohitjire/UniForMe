from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from helper import get_university_dataframe, load_pickle_file
import numpy as np
import pandas as pd

# load pickle files
university_dict = load_pickle_file('university_dict.pkl', 'rb')

university_by_user_dict = load_pickle_file('university_by_user_dict.pkl', 'rb')

university_dataset_dict = load_pickle_file('university_dict_dataset.pkl', 'rb')

similarity = load_pickle_file('by_uni_similarity.pkl', 'rb')

# get university dataframes
universities_df = get_university_dataframe(university_dict)

universities_by_user_df = get_university_dataframe(university_by_user_dict)

tfidf = TfidfVectorizer(max_features=5000, stop_words='english')

vectors = tfidf.fit_transform(universities_df['tags']).toarray()

def recommend_uni_by_uni(uni, course_name):

    uni_index = universities_df[(universities_df['Academy'] == uni) & (universities_df['CourseNameShort'] == course_name)].index[0]
    
    distances = similarity[uni_index]
    uni_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:11]

    recommendations = [
        {
            "University": universities_df.iloc[i[0]].Academy,
            "Course Name": universities_df.iloc[i[0]].CourseNameShort,
            "Similarity Score (%)": round(i[1] * 100, 2)
        }
        for i in uni_list
    ]
    return recommendations


def recommend_for_paragraph(paragraph):
    
    paragraph_vector = tfidf.transform([paragraph]).toarray()
    
    similarity_scores = cosine_similarity(paragraph_vector, vectors).flatten()
    
    top_indices = sorted(list(enumerate(similarity_scores)), reverse=True, key=lambda x: x[1])[:10]
    
    recommendations = [
        {
            "University": universities_df.iloc[i[0]].Academy,
            "Course Name": universities_df.iloc[i[0]].CourseNameShort,
            "Similarity Score (%)": round(i[1] * 100, 2)
        }
        for i in top_indices
    ]
    return recommendations


def recommend_by_user_preference(weights):
    
    weights['Jobs in City'] = weights.get('Jobs in City')
    weights['Job_Density_Neighbor'] = weights.get('Job_Density_Neighbor')
    weights['Connectivity_Score'] = weights.get('Connectivity_Score')
    weights['City_Importance_Score'] = weights.get('City_Importance_Score')
    
    universities_by_user_df['Recommendation_Score'] = (
    weights['Jobs in City'] * universities_by_user_df['Jobs in City'] +
    weights['Job_Density_Neighbor'] * universities_by_user_df['Job_Density_Neighbor'] +
    weights['Connectivity_Score'] * universities_by_user_df['Connectivity_Score'] +
    weights['City_Importance_Score'] * universities_by_user_df['City_Importance_Score']  
    )
    
    recommended_universities = universities_by_user_df.sort_values(by='Recommendation_Score', ascending=False)

    recomendations = recommended_universities[['Academy', 'CourseNameShort', 'City', 'Recommendation_Score']].head(10)
    
    recomendations.rename(columns={'CourseNameShort': 'Course Name', 'Academy': 'University', 'City': 'City', 'Recommendation_Score': 'Recommendation Score'}, inplace=True)
    recomendations.index = np.arange(1, len(recomendations) + 1)
    recomendations['City'] = recomendations['City'].str.title()
    recomendations['Recommendation Score'] = recomendations['Recommendation Score'].apply(lambda x: round(x * 100, 2))
    
    return recomendations

def get_university_neighbour(univeristy_name):
     
    university_df = get_university_dataframe(university_dataset_dict)
    
    uni = university_df[university_df['Academy'] == univeristy_name]
    
    neighbours = uni[['To','Time','Distance (km)','Jobs in neighbour cities','NeighbourCity_Population','NeighbourCity_Type']].drop_duplicates()
        
    sort_order = ['Metropolitan City', 'City', 'Medium Town', 'Small Town']
    
    neighbours['NeighbourCity_Type'] = pd.Categorical(neighbours['NeighbourCity_Type'], categories=sort_order, ordered=True)

    neighbours['NeighbourCity_Population'] = neighbours['NeighbourCity_Population'].str.replace(',', '').astype(int)

    neighbours = neighbours.sort_values(by=['NeighbourCity_Type', 'NeighbourCity_Population'], ascending=[True, False])
    
    neighbours.rename(columns={'To': 'Neighbour City', 'Time': 'Time (min)', 'Distance (km)': 'Distance (km)', 'Jobs in neighbour cities': 'Jobs in Neighbour Cities',
    'NeighbourCity_Population': 'Neighbour City Population', 'NeighbourCity_Type': 'Neighbour City Type'}, inplace=True)
    
    neighbours['Neighbour City'] = neighbours['Neighbour City'].str.title()
    
    neighbours.index = np.arange(1, len(neighbours) + 1)
    
    return neighbours