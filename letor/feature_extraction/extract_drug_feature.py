from query_drug_feature import *
from scipy.sparse import *
import numpy as np

def extract_drug_feature(drug_col, plan_ids, log):
    '''
    '''
    fea_mat = []
    log.trace('get all drugs covered by all plans')
    all_rxnorm = drug_col.find({'plans.plan_id':{'$in':plan_ids}}).distinct('rxnorm_id')
    n_rxnorm = len(all_rxnorm)
    log.trace('total rx: %d' %(n_rxnorm))

    log.trace('check drug coverage for each plan')
    drug_coverage = {}
    for pid in plan_ids:
        rxs = drug_col.find({'plans.plan_id':{'$eq':pid}}).distinct('rxnorm_id')
        n_rx = len(rxs)
        if n_rx == 0:
            log.warning('no drug coverage found for plan %s' %pid)
            drug_coverage[pid] = csr_matrix((1, n_rxnorm))
        else:
            col = np.where(np.in1d(all_rxnorm, rxs, assume_unique=True))[0]
            drug_coverage[pid] = csr_matrix(([1]*n_rx, ([0]*n_rx, col)), shape=(1,n_rxnorm))
    fea_mat.append(drug_coverage)
    log.trace('complete for %d plans' %(len(drug_coverage)))

    log.trace('get summary feature for drug')
    all_drug_states = getDrugAggregateAllStates(drug_col, plan_ids)
    n_state = len(all_drug_states)
    log.trace('total drug states: %d' %n_state)

    log.trace('extract drug sumstat for each plan')
    drug_sumstat = {}
    for pid in plan_ids:
        d_states = getDrugAggregateCountForOnePlan(drug_col, pid)
        n_ds = len(d_states)
        if n_ds == 0:
            log.warning('no drug state found for plan %s' %pid)
            drug_sumstat[pid] = csr_matrix((1,n_state))
        else:
            data, spec = [s['cnt'] for s in d_states], [s['key'] for s in d_states]
            col = [all_drug_states.index(i) for i in spec]
            drug_sumstat[pid] = csr_matrix((data, ([0]*n_ds, col)), shape=(1,n_state))
    fea_mat.append(drug_sumstat)
    log.trace('complete for %d plans' %(len(drug_sumstat)))

    return fea_mat, plan_ids
