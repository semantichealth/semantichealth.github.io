#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
@author:  Tigi Thomas
@project: MIDS W210 Capstone - ACA Semantic Search
@module:  aca_drugsbyconditiontomysql 
@desc :   This module inserts drugs by condition data 
	  scraped from drugs.com into  a mysql database
	  Eventually we can use some joins in the database
	  to get closest matching drugs to diseases. 
"""

from __future__ import print_function
from datetime import date, datetime, timedelta
import mysql.connector
import os, json


cnx = mysql.connector.connect(user='dsq', database='prescribe')
cursor = cnx.cursor()

add_drug = (
"insert into drugsbycondition"
    "(condition_name,"
    "	drug_name,"
    "	rxtype,"
    "	rating," 
    "	popularityscore,"
    "	csasched,"
    "	alcohol,"
    "	pregnancy,"
    "	drug_generalinfo,"
    "	brand_name)"
"values ("
    "%(condition)s," 
    "%(drug_name)s," 
    "%(rxtype)s," 
    "%(rating)s," 
    "%(popularityscore)s," 
    "%(csasched)s," 
    "%(alcohol)s," 
    "%(pregnancy)s," 
    "%(drug_generalinfo)s,"
    "%(brandnames)s)")

path_to_json = os.getcwd() + r'/Data/drugsdotcom/'
json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
 
drugcount = 0
for js in json_files:
    with open(os.path.join(path_to_json, js)) as json_file:
        #print "Processing... " + os.path.join(path_to_json, js)
        drug_list = json.load(json_file)
        for drug in drug_list:
            drug[u'brandnames'] = drug[u'brandnames'].replace('\n', ' ')
            cursor.execute(add_drug, drug)
            cnx.commit()

cursor.close()
cnx.close()

'''
 condition_drug_doc = {
                         "condition" : 'asdas',
                         "drug_name" : 'asdasd',
                         "rxtype" : 'asd',
                         "rating" : '3',
                         "popularityscore" : '4',
                         "csasched" : 'sdsd',
                         "alcohol" : 'f',
                         "pregnancy": 'c',
                         "drug_generalinfo" : 'sddfsdfs',
                         "brandnames" : 'szdfasdas'
                    }
'''
