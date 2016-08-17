#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
@author:  Tigi Thomas
@project: MIDS W210 Capstone - ACA Semantic Search
@module:  aca_updategeotomongo
@desc :   This module updates geocode data to mongodb providers collection.
	  	  match each geocoded address to addresses in the porovider collection
"""

import pymongo
import csv
import json
import os
from bson.json_util import dumps
import progressbar
				
inpath = r'/home/dsq/tomongo2/ProvidersGeo_'
			
#states = ["RI"]
#states = ["AK", "ND", "SD", "VT"]
#states = ["AL","AR","CO","CT","DC","DE"] 
#states = ["HI","IA","ID","KS","KY","LA","MA","MD","ME","MN","MS","NE","NH","NM"]
states = ["SC","UT","WA","WV","WY"]

connection_string = "mongodb://:@:27017/authMechanism=MONGODB-CR"

try:
	conn=pymongo.MongoClient(connection_string)	
	print "Connected!"
except pymongo.errors.ConnectionFailure, e:
   print "Connection failed : %s" % e 

db = conn['providers']
provcoll = db.providers

for state in states:
	pbar = progressbar.ProgressBar()
	filenm = inpath + state + '.json'
	print "Processing File: %s"%(filenm)
	with open(filenm,"r") as infile:
		for providerjson in pbar(infile.readlines()):
			providerObj = json.loads(providerjson)[0]
			try:	
				#check if we have all parameters to update.
				#if "npi" in providerObj and providerObj["npi"] 				\		
				if "geocode" in providerObj and providerObj["geocode"]	\
					and "address" in providerObj and providerObj["address"] 	\
					and "city" in providerObj and providerObj["city"] 		\
					and "state" in providerObj and providerObj["state"]		\
					and "zip" in providerObj and providerObj["zip"]:
						geocode = providerObj["geocode"]
						#npi = providerObj["npi"]
						address = providerObj["address"]
						city = providerObj["city"]
						state = providerObj["state"]
						zipcode = providerObj["zip"]
						result = provcoll.update_many(
							#{"npi": npi, "addresses.state" : state, "addresses.zip" : zipcode, "addresses.city": city, "addresses.address" : address},
							{"addresses.state" : state, "addresses.zip" : zipcode, "addresses.city": city, "addresses.address" : address},
							{"$set": {"addresses.$.geo": geocode}}
						)
			except Exception,e:
				pass
						
