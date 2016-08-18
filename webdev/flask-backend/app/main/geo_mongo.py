# -*- coding: utf-8 -*-
"""
Created on Thu Aug  4 23:05:15 2016

@author: dsq
"""
from flask import current_app, g
import pymongo

def get_mongo():
    mongo = getattr(g, '_mongo', None)
    if mongo is None:
        mongo = g._mongo = pymongo.MongoClient(current_app.config['MONGO_CONNECTION_STRING'])
    return mongo

def FetchProviderGeoCodes(state, zipcode, planid):
    conn = get_mongo()
    providers_db = conn['providers']
    provcoll = providers_db.providers
    geolist = []
    try:
    	provlist = list(provcoll.find(
    		{"addresses.state": state, "addresses.zip": zipcode, "plans.plan_id": planid, "addresses.geo": { '$exists': True, '$ne': [] } },
    		{"name.first":1, "name.last":1,  "addresses":"geo" }).limit(100))

    	for prov in provlist:
    		name = prov["name"]["first"] + ' ' + prov["name"]["last"]
    		for address in prov["addresses"]:
    			geo = address["geo"]
    			geolist.append([name, geo])

    except: # Exception, e:
    	#print 'Failed to query : %s' % (str(e) )
    	pass

    return geolist
