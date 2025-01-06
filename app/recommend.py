from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from helper import get_university_dataframe, load_pickle_file
import numpy as np

# load pickle files
university_dict = load_pickle_file('university_dict.pkl', 'rb')

university_by_user_dict = load_pickle_file('university_by_user_dict.pkl', 'rb')

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
    
    weights['Jobs in City'] = weights.get('Jobs in City') / 10
    weights['Job_Density_Neighbor'] = weights.get('Job_Density_Neighbor') / 10
    weights['Connectivity_Score'] = weights.get('Connectivity_Score') / 10
    weights['City_Importance_Score'] = weights.get('City_Importance_Score') / 10
    
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
