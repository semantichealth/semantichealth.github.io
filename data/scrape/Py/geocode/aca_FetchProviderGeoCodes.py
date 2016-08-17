#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
@author:  Tigi Thomas
@project: MIDS W210 Capstone - ACA Semantic Search
@module:  aca_FetchProviderGeoCodes 
@desc :   This module will be used on the flask Website 
	  to pull provider name and associated geo codes
	  based on provider planID. Issue a Mongo search and 
	  flatten out the data 
"""

import time, sys, json
import os
import pymongo


connection_string = "mongodb://user:pwd@server:27017/?authMechanism=MONGODB-CR"

try:
	conn=pymongo.MongoClient(connection_string)	
	print "Connected!"
except pymongo.errors.ConnectionFailure, e:
   print "Connection failed : %s" % e 
	
providers_db = conn['providers']
provcoll = providers_db.providers
		
# givena State, Zip Code and Plan Id, find geocodes, for plan , [ Name [l,l], Name ]							
def FetchProviderGeoCodes(state, zipcode, planid): 
	geolist=[]
	try:      
		provlist = list(provcoll.find(
			{"addresses.state":state, "addresses.zip": zipcode, "plans.plan_id": planid, "addresses.geo": { '$exists': True, '$ne': [] } },
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


	
# HEre are some sample queries..
print FetchProviderGeoCodes("SD", "57106", "76168DE0390001")
print FetchProviderGeoCodes("AL", "35555", "48963MS0500007")
print FetchProviderGeoCodes("ID", "83843", "60597ID0150003")
print FetchProviderGeoCodes("ID", "83642", "60597ID0150002")
print FetchProviderGeoCodes("KY", "40216", "76168DE0390001")
print FetchProviderGeoCodes("IN", "47129", "76168DE0390001")


conn.close()

# We can use the following query in Mongo to find those that have already been geo-encoded
'''
# providers that have geocoded addresses for a particular state...
# db.getCollection('providers').find({"addresses.state":"KY","addresses.geo": { '$exists': true, '$ne': [] }})

# or providers that have geocoded addresses for all states.
# db.getCollection('providers').find({"addresses.geo": { '$exists': true, '$ne': [] }})
'''


'''
#from pandas.io.json import json_normalize
# givena State, Zip Code and Plan Id, find geocodes, for plan , [ Name [l,l], Name ]							
def FetchProviderGeoCodes(state, zipcode, planid): 
	geolist=[]
	try:      
		result = json_normalize(provcoll.find(
					{"addresses.state":state, "addresses.zip": zipcode, "plans.plan_id":planid, "addresses.geo": { '$exists': True, '$ne': [] } },
					{"name.first":1, "name.last":1,  "addresses":"geo" }).limit(100))	
	
		for item in result.values.tolist():
			if len(item) == 4:
				geolist.append([item[2] + ' ' + item[3], item[1][0]["geo"]])
	except Exception, e:
		#print 'Failed to query : %s' % (str(e) )
		pass
	
	return geolist

'''
