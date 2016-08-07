from scipy.sparse import *
from sklearn import svm
import pickle, glob
import numpy as np

def get_rank_for_state_plan(query_cluster, click_data, log, feature_loc):
    '''
    function     : train LETOR models for queries against one state
    query_cluster: list of [nx1] integers to indicate query cluster of one state
    click_data   : list of [nx2] lists of plan_id - each query has two lists:
                   1st - total plan ranking from ES results
                   2nd - list of clicked plan_id
    feature_loc  : S3 folder name that contains the feature pickles to use
    '''

    # get state info from click data
    state_ids = np.unique([s[5:7] for j in click_data for s in j[0]])
    state = state_ids[0]
    if state_ids.size > 1:
        log.warning('click data has plans from multiple states, training for ' + state)

    # load pickle
    state_pickle = glob.glob('%s/%s*.pickle' %(feature_loc, state))
    if not state_pickle:
        return None, None
    if len(state_pickle) > 1:
        log.warning('find multiple state feature pickles, using %s' %state_pickle[0])
    with open(state_pickle[0]) as f:
        feature, plans = pickle.load(f)
    n_plan, n_fea = feature.shape
    log.trace('load %d plans from feature data with dimension %d' %(n_plan, n_fea))

    # for each query cluster
    log.trace('training started for %d query clusters' %(np.max(query_cluster)+1))
    p_index = {p:plans.index(p) for p in plans} # this comprehension only works for python 2.7 and after
    letor_rank = []
    for c in np.unique(query_cluster):
        log.trace('getting training data from cluster %d with %d queries' %(c, sum(query_cluster==c)))
        fea_mat, tgt_vec = [0], [-1]
        # assemble training points from its queries
        for rank,click in click_data[query_cluster==c]:
            # loop through each click to get training pairs
            click_indice = [rank.index(p) for p in click]
            log.trace('query has %d clicks' %(len(click)))
            for c_index in click_indice:
                log.trace('extracting feature for clicked plan %s' %rank[c_index])
                # loop through all items before current clicked item
                for i in range(c_index):
                    if (i in click_indice) or (rank[i] not in p_index) or (rank[c_index] not in p_index):
                        continue
                    fea_mat.append( (feature.getrow(p_index[rank[c_index]]) - feature.getrow(p_index[rank[i]]))
                                     if tgt_vec[-1]==-1 else (feature.getrow(p_index[rank[i]]) - feature.getrow(p_index[rank[c_index]])) )
                    tgt_vec.append(-tgt_vec[-1])
        # train SVM letor model
        if len(tgt_vec)-1<3:
            log.trace('not enough training data for query cluster %d, return 0\'s as results' %c)
            letor_rank.append(np.zeros(n_plan))
        else:
            log.trace('start training with %d pair features with %d +1' %(len(tgt_vec)-1, sum(np.array(tgt_vec)==1)))
            clf = svm.SVC(kernel='linear', C=.1, max_iter=33000000)
            clf.fit(vstack(fea_mat[1:], format='csr'), tgt_vec[1:])
            log.trace('training completed, obtain plan ranking')
            r_weight = clf.coef_.dot(feature.T).toarray()[0]
            r_min = np.min(r_weight)
            r_range = np.max(r_weight) - r_min
            letor_rank.append(5*(r_weight-r_min)/r_range)

    return np.array(letor_rank), plans
