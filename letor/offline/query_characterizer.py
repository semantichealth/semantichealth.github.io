from sklearn.feature_extraction.text import CountVectorizer
from get_query_clusters import *
import numpy as np

def query_characterizer(queries, log, similarity_limit = 0.9):
    '''
    queries - list of string for queries
    return  - list of integers to indicate cluster for each query
    '''
    # vectorize queries
    log.trace('characterizing %d queries' %queries.shape[0])
    characterizer = CountVectorizer()
    encoded_query = characterizer.fit_transform(queries)
    # set all values to 1 of encoded query (don't care duplicate terms in query)
    encoded_query.data = np.ones(encoded_query.data.size)

    # find the optimal clusters based on minimum within cluster distance
    min_sim, k = 0, 0
    while min_sim < similarity_limit:
        k += 1
        clusters, min_sim, centroids = get_query_clusters(encoded_query, k, log)
        log.trace('characterizing queries with k = %d, minimum similarity is %.4f' %(k, min_sim))

    return clusters, characterizer.vocabulary_, centroids.toarray() #, avg_sim, k
