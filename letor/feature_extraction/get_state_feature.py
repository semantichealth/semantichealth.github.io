from extract_provider_feature import *
from extract_drug_feature import *
from extract_plan_feature import *
from scipy.sparse import vstack, hstack

def get_state_feature(state_plan, plan, drug, provider, log):
    '''
    state_plan - plan IDs for the state
    plan       - MongoDB plan collection
    drug       - MongoDB drug collection
    provider   - MongoDB provider collection
    '''
    # extract features from plan, drug, and provider
    # fea_mat, state_plan = extract_plan_feature(plan, state_plan, log)
    fea_mat, state_plan = extract_drug_feature(drug, state_plan, log)
    # fea_mat += drug_mat
    prov_mat, state_plan = extract_provider_feature(provider, state_plan, log)
    fea_mat += prov_mat

    # get common keys (plan has all elements)
    # valid_plan = set(fea_mat[0].keys())
    # for i in range(1, len(fea_mat)):
    #     valid_plan = valid_plan.intersection(fea_mat[i].keys())
    # valid_plan = list(valid_plan)

    # combine all elements for each plan and return
    return state_plan, vstack([hstack([f[p] for f in fea_mat]) for p in state_plan], format='csr')
