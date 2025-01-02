from helper import get_university_dataframe, load_pickle_file


university_dict = load_pickle_file('university_dict.pkl', 'rb')

similarity = load_pickle_file('similarity.pkl', 'rb')

universities_df = get_university_dataframe(university_dict)

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
