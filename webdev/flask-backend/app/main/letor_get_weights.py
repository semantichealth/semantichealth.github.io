from io import BytesIO
from letor_online import letor_online
import pickle
import requests

def get_weights(state, query):
    url = "https://s3.amazonaws.com/w210.data/online/%s_runtime.pickle" % state
    r = requests.get(url)
    if r.status_code == 200:
        [vocabulary, centroids] = pickle.load(BytesIO(r.content))
        letor = letor_online(vocabulary, centroids)
        return letor.get_rank_weight(query) or 0
    else:
        return 0
