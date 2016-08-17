#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
@author: Tigi Thomas
@project: MIDS W210 Capstone - ACA Semantic Search
@module:  diseaserxnormlist 
@desc : This module will convert diseases and associated RxNormlist
        exported from MySql into json format.
"""

import csv
import json
import os
import json
import requests
import re
import sys
import uuid

outputjsonfile = r"Data/rxnorm_bydisease.json"
inputurlfile = r"Data/rxnorm_bycondition3.dat"

diseases = {}

with open(outputjsonfile,"w+") as outfile:   
    with open(inputurlfile,"r") as infile:
        for line in infile.readlines():
            #print line
            disease, drugname1, drugname2, rxnormid  = line.strip().replace('\xef\xbb\xbf','').replace('"','').split('|')
            diseasedata = {
                	"rxnormlist": [rxnormid]
                    }
            # We are storing one entry per unique url
            #
            if disease in diseases:
                if rxnormid not in diseases[str(disease)]["rxnormlist"]:
                    diseases[str(disease)]["rxnormlist"].append(rxnormid)
            else:
                diseases[str(disease)] = diseasedata
            #print urldata
    outfile.write('[\n')    
    json.dump(diseases, outfile)
    outfile.write(']')          

 
