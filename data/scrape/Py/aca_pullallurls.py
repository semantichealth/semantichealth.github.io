#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
@author:  Tigi Thomas
@project: MIDS W210 Capstone - ACA Semantic Search
@module:  aca_pullallurls
@desc :   This module extracts urls from the Aca dataset
"""

import csv
import json
import os
import json
import requests
import re
import sys
import uuid

masterurl = r"machine-readable-url-puf_formatted.json"

jsonfile =  open(masterurl, 'r')
acaproviderurls = json.load(jsonfile)

providercomplete = {}
providercompletename = ''

for unique_url in acaproviderurls:
    
    uid = uuid.uuid3(uuid.NAMESPACE_DNS, link.encode('utf-8'))
    try:
        r = requests.get(url)
        urls = json.loads(r.content)
    except Exception, e:
        #print str(e) 
        #we could not reach the end-url so we are going 
        #keep them empty..
        unreachablecount += 1
        urls = {u'formulary_urls': [], u'provider_urls': [], u'plan_urls': []}
        pass 
    #each row in the csv has a Issuer, but issuers could be from the 
    #same parent provider, but different issuer id for each state.. 
    issuer = {
		"issuer_name": row['IssuerName'],
		"issuer_id": row['IssuerID'],
		"issuer_state": row['State']
    }
    # this is going to be the main url data per unique 
    # external url.
    urldata = {
    	"url": row['URLSubmitted'],
    	"email": row['TechPOCEmail'],
    	"issuer": [{
    		"issuer_name": row['IssuerName'],
    		"issuer_id": row['IssuerID'],
    		"issuer_state": row['State']
          }],
    	"urljson": urls
        }
