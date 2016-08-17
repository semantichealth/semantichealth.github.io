#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
@author:  Tigi Thomas
@project: MIDS W210 Capstone - ACA Semantic Search
@module:  aca_drugscraper 
@desc :   This module scapes diseases/conditions and associated
	  drgus from centerwatch.com 
"""
import time
from subprocess import check_output
import sys

import urllib2
from urllib2 import urlopen
import json
import re
import cookielib, urllib2
from cookielib import CookieJar
import datetime
import os
import socket
import shutil
from time import time, ctime, sleep
from urlparse import urlparse
from bs4 import BeautifulSoup
import uuid

import pymongo

mdbconn = None
storedb = None
storecol = None

try:
   mdbconn=pymongo.MongoClient(host='localhost', port=27017 )
   if mdbconn is not None:
       storedb = mdbconn['data']
       storecol = storedb.drugbycondition
       print ("Connected to MongoDb")
 
except pymongo.errors.ConnectionFailure, e:
   print ("Connection failed : %s" % e )
   print ("Proceeding to Capture without storing to DB")
   
hdr = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}

rooturl = 'http://www.centerwatch.com/drug-information/fda-approved-drugs/medical-conditions'
domain = 'http://www.centerwatch.com'

def main():
    #data organized aphabetically
    for c in "abcdefghijklmnopqrstuvwxyz":
    #for c in "a":
        link = rooturl + '/' + c
        try:
            req = urllib2.Request(link, headers=hdr)
            success = 0
            try:
                resplink = urllib2.urlopen(req, timeout=60)
                success = 1
            except urllib2.URLError:
                pass
            except socket.timeout:
                pass

	    #Note the below code won't work if there are changes
	    #drugs.com html page
            if (success == 1):
                try:
                    resplinkdata = resplink.read()
                    soup = BeautifulSoup(resplinkdata, 'html.parser')
                    for node in soup.findAll("a", { "class" : "ToggleDrugCategory" }):
                        Condition = node.get_text().strip()
                        drugs = node.parent.findNext('div', { "class" : "CategoryListSection" })
                        for drug in drugs.findAll('a', id = re.compile("DrugNameLink$")):
                            DrugName = drug.get_text().strip()    
                            Manufacturer = drug.findNext('a', id = re.compile("CompanyNameLink?")).get_text().strip()
                            druginfolink = domain + drug['href']
                            req2 = urllib2.Request(druginfolink, headers=hdr)
                            try:
                                resplink2 = urllib2.urlopen(req2, timeout=60)
                                resplinkdata2 = resplink2.read()
                                soup2 = BeautifulSoup(resplinkdata2, 'html.parser')
                                for gi_node in soup2.findAll('h3', text = 'General Information'):
                                    generalinfo = gi_node.findNext('p').get_text().strip().replace('\n', ' ').replace('\r', '')

                                #put everything into json and push to MongoDB.
                                condition_drug_doc = {
                                             "condition" : Condition,
                                             "drug_name" : DrugName,
                                             "drug_manufacturer" : Manufacturer,
                                             "drug_generalinfo" : generalinfo
                                        }
                                storecol.insert(condition_drug_doc)  
                            except Exception,e:
                                print str(e)
                            except urllib2.URLError:
                                pass
                            except socket.timeout:
                                pass
                except:
                    pass
        except Exception:
            pass
main()


