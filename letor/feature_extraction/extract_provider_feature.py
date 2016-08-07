from query_provider_feature import *
from scipy.sparse import *
from bson.code import Code
import numpy as np

def mergeSpec(t2):
    sp = []
    for tt in t2:
        sp += tt['speciality']
    cnt = {s:0 for s in np.unique(sp)}
    for tt in t2:
        for s in tt['speciality']:
            cnt[s] += tt['count']
    if '' in cnt:
        cnt.pop('')
    if None in cnt:
        cnt.pop(None)
    return cnt

def extract_provider_feature(prov_col, plan_ids, log):
    '''
    '''
    fea_mat = []
    log.trace('get provider under the plans')
    all_npi = prov_col.find({'plans.plan_id':{'$in':plan_ids}}).distinct('npi')
    n_npi = len(all_npi)
    log.trace('total providers: %d' %n_npi)

    log.trace('check provider coverage for each plan') ##### slow #####
    provider_coverage = {}
    for pid in plan_ids:
        plan_npi = prov_col.find({'plans.plan_id':{'$eq':pid}}).distinct('npi')
        npn = len(plan_npi)
        if npn==0:
            log.warning('no provider found for flan %s' %pid)
            provider_coverage[pid] = csr_matrix((1, n_npi))
        else:
            col = np.where(np.in1d(all_npi, plan_npi, assume_unique=True))[0]
            provider_coverage[pid] = csr_matrix(([1]*npn, ([0]*npn, col)), shape=(1, n_npi))
    fea_mat.append(provider_coverage)
    log.trace('complete for %d plans' %(len(provider_coverage)))

    log.trace('get summary feature for provider')
    all_provider_states = getProviderAllStates(prov_col, plan_ids)
    n_prov = len(all_provider_states)
    log.trace('total provider summary: %d' %(n_prov))

    log.trace('extract provider sumstat for each plan')
    reducer = Code("""
                function(obj, prev){
                  prev.count++;
                }
                """)
    provider_sumstat = {}
    for pid in plan_ids:
        p_states = prov_col.group(key={'speciality':1}, condition={'plans.plan_id':{'$eq':pid}}, initial={"count": 0}, reduce=reducer)
        p_states = mergeSpec(p_states)
        # p_states = getProviderStateForOnePlan(prov_col, pid)
        n_ps = len(p_states)
        if n_ps == 0:
            log.warning('no provider state found for plan %s' %pid)
            provider_sumstat[pid] = csr_matrix((1, n_prov))
        else:
            spec = p_states.keys()
            data = [p_states[s] for s in spec]
            col = [all_provider_states.index(s) for s in spec]
            provider_sumstat[pid] = csr_matrix((data, ([0]*n_ps, col)), shape=(1, n_prov))
    fea_mat.append(provider_sumstat)
    log.trace('complete for %d plans' %(len(provider_sumstat)))

    return fea_mat, plan_ids
