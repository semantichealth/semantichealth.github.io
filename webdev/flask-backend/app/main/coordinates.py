from geo_mongo import FetchProviderGeoCodes
from database import get_db
from flask import g

def get_coordinates(plan_id, zipcode, state):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT lat, lon FROM ZipToCoord WHERE zipcode = %s", (zipcode, ))
    result = cur.fetchone()
    if result:
        center = list(result)
    else:
        center = [37.7684856, -122.457516] # Default: San Francisco
    conn.commit()
    cur.close()
    provider_array = FetchProviderGeoCodes(state=state, zipcode=zipcode, planid=plan_id)
    return (center, provider_array)
