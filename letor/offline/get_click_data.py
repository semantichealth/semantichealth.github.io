import psycopg2
import numpy as np
from datetime import datetime

def get_click_data(log, page_interval = 1.5):
    '''
    '''
    host = 'aca-db-dev.cv6yjavd16jd.us-west-1.rds.amazonaws.com'
    conn = psycopg2.connect(database='aca_db', user='aca_db_dev', password='123', host=host, port='5432')
    cur = conn.cursor()

    sql_click = '(select c.session_id as sid, array_agg(c.click) as c_t from (select session_id, plan_id || \',\' || created_clicks as click from Clicks) c group by c.session_id) c2'
    sql_rank = '(select r.session_id as sid, array_agg(r.rank) as r_t from (select session_id, plan_id || \',\' || created_ranks || \',\' || plan_score as rank from Ranks) r group by r.session_id) r2'
    sql_exe = 'select q.session_id as sid, q.state as state, q.health as health, c2.c_t as click, r2.r_t as rank from Queries q join %s on q.session_id=c2.sid join %s on c2.sid=r2.sid' %(sql_click, sql_rank)
    cur.execute(sql_exe)
    records = cur.fetchall()
    log.trace('get query and click data with SQL: "%s"' %sql_exe)
    # define data type
    plan_type = [('plan_id','S16'), ('ts',datetime), ('score',float)]
    click_type = [('plan_id','S16'), ('ts',datetime)]
    click_rtn = []
    for sid, state, health, click, rank in records:
        # get plan ranks and clicks, and parse out timestamp
        plans, clicks = [], []
        for r in rank:
            _r = r.split(',')
            _r[1] = datetime.strptime(_r[1],'%Y-%m-%d %H:%M:%S.%f')
            _r[2] = -float(_r[2]) # take minus so ascending sort works
            plans.append(tuple(_r))
        for c in click:
            _c = c.split(',')
            _c[1] = datetime.strptime(_c[1],'%Y-%m-%d %H:%M:%S.%f')
            clicks.append(tuple(_c))
        # sort timestamp to get click order
        p_click = [c['plan_id'] for c in np.sort(np.array(clicks, dtype=click_type), order=['ts'])]
        # check timestamp block for page, then sort on score to get plan order
        plans = np.sort(np.array(plans, dtype=plan_type), order=['ts'])
        pages, p_rank = np.zeros(len(plans)), []
        for i in range(1, len(plans)):
            pages[i] = pages[i-1] if (plans[i]['ts']-plans[i-1]['ts']).total_seconds()<page_interval else pages[i-1]+1
        for pg in np.unique(pages):
            p_rank += [pl['plan_id'] for pl in np.sort(plans[pages==pg], order=['score','ts'])]
        # assemble the query info
        log.trace('%s - "%s" - ES ranks %s - clicks %s' %(state, health, str(p_rank), str(p_click)))
        click_rtn.append((state, health, p_rank, p_click))

    # close connection and return
    cur.close()
    conn.close()
    rtn_type = [('state','S2'), ('query','S512'), ('ranks',list), ('clicks',list)]
    return np.array(click_rtn, dtype=rtn_type)


# if __name__ == "__main__":
# 	get_click_data()
