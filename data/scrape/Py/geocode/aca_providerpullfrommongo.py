#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
@author:  Tigi Thomas
@project: MIDS W210 Capstone - ACA Semantic Search
@module:  aca_providerpullfrommongo
@desc :   This module extracts all the provider data from mongodb
	  to seprate files chunked by State.
	  These provider data can then be used to obtain geo codes
	  and used for scraping provider ratings. This is essentiall
	  just a simple dump to json from the providers collection.
    Note: This will run for a while - but only required once.
"""

import pymongo
import csv
from urllib import urlopen
from urllib import urlretrieve
import json
import os
from bson.json_util import dumps
    

states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", 
          "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
          "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
          "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
          "SD", "TN", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "TX"]

try:
    conn=pymongo.MongoClient("server", 27017)
    print "Connected!"
except pymongo.errors.ConnectionFailure, e:
   print "Connection failed : %s" % e 
conn


providers_db = conn['providers']
provcoll = providers_db.providers

outfile_prefix = 'Data/ProvidersByState/Providers_'
for state in states:
    with open(outfile_prefix + state + '.json',"w+") as outfile:  
        first = True
        cursor = provcoll.find({'addresses.state': {'$eq': state }}, {"npi":1, "speciality": { '$slice' : 1 },"name" : { '$slice' : 1 } ,"addresses" : { '$slice' : 1 } }).batch_size(30)
        for item in cursor:
            outfile.write('[')
            outfile.write(dumps(item))
            outfile.write(']\n') 
        cursor.close()
