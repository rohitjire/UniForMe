import pandas as pd
import pickle

def get_university_dataframe(universiti_dict):
    return pd.DataFrame.from_dict(universiti_dict)


def load_pickle_file(filename, mode):
    with open(filename, mode) as file:
        data = pickle.load(file)
    return data

def normalize_weights(weights_dict):
    total = sum(weights_dict.values())
    
    if total == 0:
        num_items = len(weights_dict)
        if num_items == 0:
            raise ValueError("The weights dictionary is empty.")
        return {key: 1 / num_items for key in weights_dict}
    
    normalized_weights = {key: value / total for key, value in weights_dict.items()}
    return normalized_weights
