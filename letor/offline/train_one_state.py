from s3_helpers import *
from get_rank_for_state_plan import *
from query_characterizer import *
import pickle


def train_one_state(click_data, state, log, s3_fea):
    '''
    '''
    # set folder name of S3
    s3clnt = s3_helper()
    log.trace('characterize queries for state %s' %state)
    s_rows = click_data[click_data['state']==state]
    q_cluster, vocab, centroids = query_characterizer(s_rows['query'], log)
    log.trace('run letor training for state %s' %state)
    letor_rank, plans = get_rank_for_state_plan(q_cluster, np.array([[r['ranks'],r['clicks']] for r in s_rows]), log, s3_fea)
    if not plans: # or (not letor_rank):
        log.warning('no feature file found for state %s, skip training.' %state)
        return
    # exclude missing plan IDs in ES
    with open('missing.pickle') as f:
        missing = pickle.load(f)
    picker = np.array([p not in missing for p in plans])    
    # upload the stuff to S3
    save_training = 'training/%s_%d.pickle' %(state, len(letor_rank))
    with open(save_training, 'w') as f:
        pickle.dump([list(np.array(plans)[picker]), letor_rank[:, picker]], f)
    s3clnt.delete_by_state('training/%s' %(state))
    s3clnt.upload(save_training)
    save_online = 'online/%s_runtime.pickle' %(state)
    cen = [list(c) for c in centroids]
    voc = [None]*len(vocab)
    for k,v in vocab.items():
        voc[v] = k
    with open(save_online, 'w') as f:
        pickle.dump([voc, cen], f)
    s3clnt.delete_by_state('online/%s' %(state))
    s3clnt.upload(save_online)
    log.trace('ranking & online file are saved on s3')
