import numpy as np

class letor_online:
    ''' runtime component for letor, give plan ranking weights for query
    '''
    vocabulary = None
    centroids = None
    similarity_limit = 0.8

    def __init__(self, query_vocab, cluster_centroids, similarity = 0.8):
        '''
        query_vocab        : vocabulary dictionary fitted for learned queries
        cluster_centroids   : center points of query clusters
        '''
        # initialize encoder
        self.vocabulary = query_vocab
        self.centroids = np.array(cluster_centroids)
        self.similarity_limit = similarity

    def get_rank_weight(self, query):
        '''
        get a vector to dot product with indexed ranking in ES from training
        '''
        if type(query) is not str:
            print 'Input parameter query should be a string.'
            return None

        # encode the query, if it's orthogonal to all learnt queries, no ranking
        vQuery = np.zeros(len(self.vocabulary))
        query = query.lower()
        for i in range(len(vQuery)):
            if self.vocabulary[i] in query:
                vQuery[i] = 1

        if vQuery.sum() == 0:
            print 'No similar query is found, no ranking from LETOR'
            return None

        # find the most similar query, by cosine distance
        norm = np.sqrt(sum(vQuery**2))
        similarity = (vQuery/norm).dot(self.centroids.T)
        candidates = similarity > self.similarity_limit
        # if no one above limit, return the synthesized ranking from the closest queries, or return None
        if candidates.sum() == 0:
            candidates = similarity == similarity.max()

        # weight vector for dot product
        return [s if c else 0 for s,c in zip(similarity,candidates)]
