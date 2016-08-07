import numpy as np
import pickle

def simulate_clicks(n_query = 8, n_click_max = 8):
    '''
    '''

    with open('plan_ids.pickle') as f:
        all_plan = pickle.load(f)

    # sim health
    sim_health = np.array(['Alzheimer', 'Glaucoma', 'Hypertension', 'Obesophobia', 'diabetes', 'fatigue'])

    # get states
    sim_data = []
    state_ids = np.unique([i[5:7] for i in all_plan[0]])
    for state in state_ids:
        state_plan = np.array([i for i in all_plan[0] if state in i])
        n_plan = len(state_plan)
#         print 'state %s has %d plans' %(state, n_plan)
        # simulate query
        for i in range(n_query):
            health = ' '.join(sim_health[np.random.permutation(sim_health.size)[0:i+1]])
            sim_rank = state_plan[np.random.permutation(n_plan)]
            sim_click = state_plan[np.random.permutation(n_plan)][0:np.random.randint(low=1, high=min(n_plan,n_click_max))]
            sim_data.append((state, health, list(sim_rank), list(sim_click)))

    rtn_type = [('state','S2'), ('query','S512'), ('ranks',list), ('clicks',list)]
    return np.array(sim_data, dtype=rtn_type)
