import faiss
import numpy as np
import pickle
import os


INDEX_PATH = "data/faiss.index"
META_PATH = "data/faiss_meta.pkl"


def save_index(index, metadata):

    faiss.write_index(index, INDEX_PATH)

    with open(META_PATH, "wb") as f:
        pickle.dump(metadata, f)


def load_index():

    if not os.path.exists(INDEX_PATH):
        return None, None

    index = faiss.read_index(INDEX_PATH)

    with open(META_PATH, "rb") as f:
        metadata = pickle.load(f)

    return index, metadata