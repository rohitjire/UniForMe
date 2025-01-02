import pandas as pd
import pickle

def get_university_dataframe(universiti_dict):
    return pd.DataFrame.from_dict(universiti_dict)


def load_pickle_file(filename, mode):
    with open(filename, mode) as file:
        data = pickle.load(file)
    return data