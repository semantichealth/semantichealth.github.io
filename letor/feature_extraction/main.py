from pymongo import MongoClient
from get_state_feature import *
from s3_helpers import *
from logger import *
import numpy as np
import traceback, pickle, os

def main():
    '''
    main procedure to extract features for all states
    '''
    log, s3clnt, s3folder = logger('feature'), s3_helper(), 'feature_u'
    for f in ['log', s3folder]:
        if not os.path.exists(f):
            os.makedirs(f)
    log.start()

    # connect to MongoDB and get collections
    m_url = 'ec2-52-53-173-200.us-west-1.compute.amazonaws.com'
    client = MongoClient(m_url, 27017)
    plan_col = client.plans.plans
    drug_col = client.formularies.drugs
    prov_col = client.providers.providers
    faci_col = client.providers.facilities
    log.trace('connected to MongoDB at %s' %m_url)
    # parse out plan ID for states
    all_plan = plan_col.distinct('plan_id') #drug_col.distinct('plans.plan_id')
    state_ids = np.unique([i[5:7] for i in all_plan])
    log.trace('find plan from %d states: %s' %(len(state_ids), ', '.join(state_ids)))
    # run procedure for each state
    failure = []
    for state in state_ids:
        try:
            if state == '':
                continue
            state_plan = [i for i in all_plan if state in i]
            log.trace('processing %d plans for %s' %(len(state_plan), state))
            plan, feature = get_state_feature(state_plan, plan_col, drug_col, prov_col, log)
            log.trace('completed feature extraction for %d plans, with dimension %s' %(len(plan), str(feature.shape)))
            # savee pickle to s3
            save_name = '%s/%s_%d_%d.pickle' %(s3folder, state, feature.shape[0], feature.shape[1])
            with open(save_name, 'w') as f:
                pickle.dump([feature, plan], f)
            s3clnt.delete_by_state('%s/%s' %(s3folder, state))
            s3clnt.upload(save_name)
            log.trace('feature pickle saved to s3, complete for %s' %state)
        except Exception as ex:
            traceback.print_exc(file=log.log_handler())
            failure.append(state)
            log.error('feature extraction has encountered error for state %s' %state)

    log.trace('feature extraction completed, failed for %d states: %s' %(len(failure), ', '.join(failure)))
    log.stop()
    client.close()

if __name__ == "__main__":
	main()
