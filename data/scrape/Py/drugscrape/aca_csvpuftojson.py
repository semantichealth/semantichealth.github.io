#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
@author: Tigi Thomas
@project: MIDS W210 Capstone - ACA Semantic Search
@module: aca url puf csv to json 
@desc : This module will the machine readable url puf file (.csv)
        explore the (first level) provider urls to extract 
        (second level) json file containing formulary, provider and plan 
        urls. This file can then be used for exploring and downloading 
        data fromt the second level urls.
"""

import csv
import json
import os
import json
import requests
import re
import sys
import uuid

inputurlfile = sys.argv[1]  
outputjsonfile = sys.argv[2]

#csvfile = open(r"Data/2016/machine-readable-url-puf.csv", 'r')
#jsonfile = open(r'Data/2016/machine-readable-url-puf.json', 'w')
fieldnames = ('State','IssuerID','IssuerName','URLSubmitted','TechPOCEmail')
urlstruct = {}
uniqueurlcount = 0
unreachablecount = 0
notprovidedcount = 0

with open(outputjsonfile,"w") as jsonfile:   
    with open(inputurlfile,"r") as csvfile:
        reader = csv.DictReader( csvfile, fieldnames)
        for row in reader: 
            url = row['URLSubmitted']
            # Examine Url tag - if it is 
            # this is pretty straight forward, could use urlparse
            # or something, but then will also validate with an actual
            # request and ignore if the url cannot be reached.
            if url == 'URL Submitted' or url == 'NOT SUBMITTED':
                notprovidedcount += 1 
            else:
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
                #uid = uuid.uuid3(uuid.NAMESPACE_DNS, url.encode('utf-8'))
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
                # We are storing one entry per unique url
                #
                if url in urlstruct:
                    urlstruct[str(url)]["issuer"].append(issuer)
                else:
                    uniqueurlcount += 1
                    urlstruct[str(url)] = urldata
                #print urldata
        
    json.dump(urlstruct, jsonfile)
    jsonfile.write('\n')      

print "Unique Urls visited:  %d" % (uniqueurlcount)
print "Unreachable Urls:  %d" % (unreachablecount)
print "Urls not provided:  %d" % (notprovidedcount)
 
