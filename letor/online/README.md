# Runtime Executer

###class
    letor_online(query_vocab, cluster_centroids, similarity = 0.8)
- query_vocab         : vocabulary dictionary fitted for learned queries
- cluster_centroids   : center points of query clusters
- return              : weights to synthesize ranking from previously seen queries

###runtime data
- located at s3: https://s3.amazonaws.com/w210.data/online/SS_runtime.pickle
- data is saved separately for each state, replace _SS_ in above link with state abbreviation, e.g. OR, NJ etc.
- a simulated file is called _sim_runtime.pickle_
- each file contains **cluster_centroids** and **query_vocab** for **letor_online** class initialization

###example
    import pickle
    with open('sim_runtime.pickle') as f:
    [vocabulary, centroids] = pickle.load(f)

    from letor_online import *
    letor = letor_online(vocabulary, centroids)
    rank = letor.get_rank_weight('glaucoma')
