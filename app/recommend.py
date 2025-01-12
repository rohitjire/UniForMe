from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from helper import get_university_dataframe, load_pickle_file
import numpy as np
import pandas as pd


class Recommender:
    def __init__(self, university_dict_path, university_user_dict_path, university_dataset_dict_path):
        # Load pickle files
        self.university_dict = load_pickle_file(university_dict_path, 'rb')
        self.university_by_user_dict = load_pickle_file(university_user_dict_path, 'rb')
        self.university_dataset_dict = load_pickle_file(university_dataset_dict_path, 'rb')
        
        # Load dataframes
        self.universities_df = get_university_dataframe(self.university_dict)
        self.universities_by_user_df = get_university_dataframe(self.university_by_user_dict)
        self.universities_dataset_df = get_university_dataframe(self.university_dataset_dict)

        # Create and fit TF-IDF vectorizer
        self.tfidf = TfidfVectorizer(max_features=5000, stop_words='english')
        self.vectors = self.tfidf.fit_transform(self.universities_df['tags']).toarray()
    
    def recommend_by_uni_and_course(self, uni, course_name):
        try:
            uni_index = self.universities_df[
                (self.universities_df['Academy'] == uni) & 
                (self.universities_df['CourseNameShort'] == course_name)
            ].index[0]
        except IndexError:
            raise ValueError("The specified university or course name was not found.")

        similarity = cosine_similarity(self.vectors)
        distances = similarity[uni_index]

        uni_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:11]
        recommendations = [
            {
                "University": self.universities_df.iloc[i[0]].Academy,
                "Course Name": self.universities_df.iloc[i[0]].CourseNameShort,
                "Similarity Score (%)": round(i[1] * 100, 2)
            }
            for i in uni_list
        ]
        return recommendations

    def recommend_by_paragraph(self, paragraph):
        paragraph_vector = self.tfidf.transform([paragraph]).toarray()
        similarity_scores = cosine_similarity(paragraph_vector, self.vectors).flatten()

        top_indices = sorted(list(enumerate(similarity_scores)), reverse=True, key=lambda x: x[1])[:10]
        recommendations = [
            {
                "University": self.universities_df.iloc[i[0]].Academy,
                "Course Name": self.universities_df.iloc[i[0]].CourseNameShort,
                "Similarity Score (%)": round(i[1] * 100, 2)
            }
            for i in top_indices
        ]
        return recommendations

    def recommend_by_user_preference(self, weights):
        if not all(key in weights for key in ['Jobs in City', 'Job_Density_Neighbor', 'Connectivity_Score', 'City_Importance_Score']):
            raise ValueError("Weights must include 'Jobs in City', 'Job_Density_Neighbor', 'Connectivity_Score', and 'City_Importance_Score'.")
        
        self.universities_by_user_df['Recommendation_Score'] = (
            weights['Jobs in City'] * self.universities_by_user_df['Jobs in City'] +
            weights['Job_Density_Neighbor'] * self.universities_by_user_df['Job_Density_Neighbor'] +
            weights['Connectivity_Score'] * self.universities_by_user_df['Connectivity_Score'] +
            weights['City_Importance_Score'] * self.universities_by_user_df['City_Importance_Score']
        )

        recommended_universities = self.universities_by_user_df.sort_values(by='Recommendation_Score', ascending=False)
        recommendations = recommended_universities[['Academy', 'CourseNameShort', 'City', 'Recommendation_Score']].head(10)

        recommendations.rename(columns={
            'CourseNameShort': 'Course Name',
            'Academy': 'University',
            'City': 'City',
            'Recommendation_Score': 'Recommendation Score'
        }, inplace=True)

        recommendations.index = np.arange(1, len(recommendations) + 1)
        recommendations['City'] = recommendations['City'].str.title()
        recommendations['Recommendation Score'] = recommendations['Recommendation Score'].apply(lambda x: round(x * 100, 2))

        return recommendations

    def get_university_neighbour(self, university_name):
        uni = self.universities_dataset_df[self.universities_dataset_df['Academy'] == university_name]

        if uni.empty:
            raise ValueError(f"No data found for the university: {university_name}")

        neighbours = uni[['To', 'Time', 'Distance (km)', 'Jobs in neighbour cities','NeighbourCity_Population', 'NeighbourCity_Type']].drop_duplicates()

        sort_order = ['Metropolitan City', 'City', 'Medium Town', 'Small Town']
        neighbours['NeighbourCity_Type'] = pd.Categorical(neighbours['NeighbourCity_Type'], categories=sort_order, ordered=True)

        neighbours['NeighbourCity_Population'] = neighbours['NeighbourCity_Population'].str.replace(',', '').astype(int)
        neighbours = neighbours.sort_values(by=['NeighbourCity_Type', 'NeighbourCity_Population'], ascending=[True, False])

        neighbours.rename(columns={
            'To': 'Neighbour City',
            'Time': 'Time (min)',
            'Distance (km)': 'Distance (km)',
            'Jobs in neighbour cities': 'Jobs in Neighbour Cities',
            'NeighbourCity_Population': 'Neighbour City Population',
            'NeighbourCity_Type': 'Neighbour City Type'
        }, inplace=True)

        neighbours['Neighbour City'] = neighbours['Neighbour City'].str.title()
        neighbours.index = np.arange(1, len(neighbours) + 1)

        return neighbours