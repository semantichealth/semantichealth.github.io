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

outputjsonfile = r"Data/disease_byrxnorm.json"
inputurlfile = r"Data/disease_byrxnorm.dat"

rxnormlist = {}

with open(outputjsonfile,"w+") as outfile:   
    with open(inputurlfile,"r") as infile:
        for line in infile.readlines():
            #print line
            rxnormid, disease, diseasecount  = line.strip().replace('\xef\xbb\xbf','').replace('"','').split('|')
            diseasedata = {
                	"diseaselist": [disease]
                    }
            # We are storing one entry per unique url
            #
            if rxnormid in rxnormlist:
                if disease not in rxnormlist[str(rxnormid)]["diseaselist"]:
                    rxnormlist[str(rxnormid)]["diseaselist"].append(disease)
            else:
                rxnormlist[str(rxnormid)] = diseasedata
            #print urldata
    outfile.write('[\n')    
    json.dump(rxnormlist, outfile, indent=4, sort_keys=True)
    outfile.write(']')          

 
