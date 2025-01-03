from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from helper import get_university_dataframe, load_pickle_file


university_dict = load_pickle_file('university_dict.pkl', 'rb')

similarity = load_pickle_file('by_uni_similarity.pkl', 'rb')

universities_df = get_university_dataframe(university_dict)

tfidf = TfidfVectorizer(max_features=5000, stop_words='english')

vectors = tfidf.fit_transform(universities_df['tags']).toarray()

def recommend_uni_by_uni(uni, course_name):

    uni_index = universities_df[(universities_df['Academy'] == uni) & (universities_df['CourseNameShort'] == course_name)].index[0]
    
    distances = similarity[uni_index]
    uni_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:11]

    recommendations = [
        {
            "Course Name": universities_df.iloc[i[0]].CourseNameShort,
            "University": universities_df.iloc[i[0]].Academy
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
            "Course Name": universities_df.iloc[i[0]].CourseNameShort,
            "University": universities_df.iloc[i[0]].Academy,
            "Similarity Score (%)": round(i[1] * 100, 2)
        }
        for i in top_indices
    ]
    return recommendations
