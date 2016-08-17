#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
@author:  Tigi Thomas
@project: MIDS W210 Capstone - ACA Semantic Search
@module:  aca_drugsdotcom scarper
@desc :   This module scapes diseases/conditions and associated
	  drugus from drugs.com. There are multiple nested pages
	  and recursive function is used to scrape leaf level pages
"""

import sys
import os
import time
import datetime
import threading
import ntpath

from time import time, ctime, sleep
from datetime import date as dt

import shutil
import socket
import re

import urllib2
from urllib2 import urlopen
import cookielib, urllib2
from cookielib import CookieJar

from urlparse import urlparse
from bs4 import BeautifulSoup
import uuid

import json
from subprocess import check_output

from boto.s3.connection import S3Connection
from boto.s3.key import Key

import pymongo

#To upload directly to Mongodb
'''
mdbconn = None
storedb = None
storecol = None

try:
   mdbconn=pymongo.MongoClient()
   if mdbconn is not None:
       storedb = mdbconn['drugsdotcom']
       storecol = storedb.drugbycondition
       print ("Connected to MongoDb")
 
except pymongo.errors.ConnectionFailure, e:
   print ("Connection failed : %s" % e )
   print ("Proceeding to Capture without storing to DB")
'''   
   
hdr = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}

rooturl = 'https://www.drugs.com/condition'
rootdomain = 'https://www.drugs.com'
    
conn = None #S3Connection('', '')
HwBucket = None #conn.get_bucket('') 

#searchalphabet = sys.argv[1]
#outputpath = sys.argv[2]

# -----------------------------------------------------------------------------
# The Idea for this Thread object is to be able to save a file to S3 without
# blocking the caller. Also running in a separate thread will make sure 
# the main program runs incase of any failure with connecting/saving to S3
#
# -----------------------------------------------------------------------------
class SaveToS3Thread(threading.Thread):
    """Thread to Save File to S3. Assumes Bucket HwBucket has been initialized """
    def __init__(self, filepath):
        threading.Thread.__init__(self)
        self.name = ntpath.basename(filepath)
        self.filepath = filepath
        print "Initializing SaveToS3Thread.."
    def run(self):
        try:
            if HwBucket is not None:
                sKeyWriter = HwBucket.new_key(self.name)
                sKeyWriter.set_contents_from_filename(self.filepath)
                print "Saved File: %s to S3 Successfully" % self.name
                return
            else:
                print 'Failed to save %s to S3 : HwBucket has not been inialized' % self.name
        except Exception, e:
                print 'Failed to save %s to S3 : %s ' % ( self.name, str(e) )
                pass
# -----------------------------------------------------------------------------
# JsonDocSerializer
# Serializes json doc to file and also auto chunks based on the file name..
# The class keep tracks of current file (name) and when a new file name
# is provided, closes out the old one and creates new one.. 
# Also saves the old one to S3 , by calling the SaveToS3Thread.
# -----------------------------------------------------------------------------           
class JsonDocSerializer:
    """Allows single json doc serialization, with automatic chunking
    and ability to save to S3."""
    def __init__(self, fullfilename, enables3save = False):
         self.fullfilename = fullfilename
         self.enables3save = enables3save
         self.first = True
         self.fileobj = open(self.fullfilename,'w+')
    
    def SaveToS3(self):
         if self.enables3save:
             print "Save to S3 Called %s" % self.fullfilename 
             s3savethrd = SaveToS3Thread(self.fullfilename)
             s3savethrd.start()

    def close(self):
         self.fileobj.write("]\n")
         self.fileobj.close()
         self.fileobj = None
         #save the old file to s3 before
         #switching to new file.
         self.SaveToS3()

    def write(self, jsondoc, newfullfilename = None):
         if(newfullfilename and self.fullfilename <> newfullfilename):
             if (self.fileobj):                
                 #new file.. so close out the old one and save.                 
                 self.close()
             else:
                 #set CurFile
                 self.fullfilename = newfullfilename
                 self.first = True
                 self.fileobj = open(self.fullfilename,'w+')
              
         if(self.fileobj):
             if not self.first:
                 self.fileobj.write(",\n")
             else:
                 self.fileobj.write("[\n")
                 self.first = False                     
             jsdump = json.dumps(jsondoc)
             self.fileobj.write(jsdump)
   
# This is the main crawler class.         
class DrugsDotComRootAlphabetCrawler:
    """
       Crawls from the main root landing page for drugs starting
       with a particular alphabet
    """ 
    def __init__(self):
          self.hdr = {
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                    'Accept-Encoding': 'none',
                    'Accept-Language': 'en-US,en;q=0.8',
                    'Connection': 'keep-alive'}
          self.rootdomain = 'https://www.drugs.com'
          self.docserializer = None
    
    def item_is_in_set(item, setlist):
        if item in setlist:
            return True
        else:
            return False

    
    #Set of functions below to extract data from specific tags    
    
    def get_drugname(self, drug):
        elem = drug.find("td", { "class" : "condition-table__drug-name"} )
        if(elem and elem.span and elem.span.a):
            return elem.span.a.get_text().strip()   
        else:
            return ""
            
    def get_drugnamelink(self, drug):
        elem = drug.find("a", { "class" : "condition-table__drug-name__link"} )
        if(elem):
            return rootdomain + elem['href']
        else:
            return ""
    
    def get_prescrptiontype(self, drug):
        elem = drug.find("td", { "class" : "condition-table__rx-otc"} )
        if(elem and elem.span):
            return elem.span.get_text().strip()   
        else:
            return ""
    
    def get_rating(self, drug):
        elem = drug.find("td", { "class" : "condition-table__rating"} )
        if(elem and elem.div):
            return elem.div.get_text().strip()   
        else:
            return 0
            
    def get_csa(self, drug):
        elem = drug.find("td", { "class" : "condition-table__csa"} )
        if(elem and elem.span):
            return elem.span.get_text().strip()   
        else:
            return ""
     
    def get_pregcategory(self, drug):
        elem = drug.find("td", { "class" : "condition-table__pregnancy"} )
        if(elem and elem.span):
            return elem.span.get_text().strip()   
        else:
            return ""
            
    def get_popularity(self, drug):
        elem = drug.find("td", { "class" : "condition-table__popularity"} )
        if(elem and elem.div.div.div.span):
            return elem.div.div.div.span['style'].strip().split(':')[1].split('%')[0] 
        else:
            return 0
            
    def get_alcoholinteraction(self, drug):
        elem = drug.find("td", { "class" : "condition-table__alcohol"} )
        if(elem and elem.span):
            return elem.span.get_text().strip()   
        else:
            return ""
    
    # scrape general info about the drug, brand name etc.. 
    # this is usually on a separate page.
    def scrape_generalinfo(self, url):
        req = urllib2.Request(url, headers=self.hdr)
        try:
            # First extract brand names/ Generic name..
            brandnames = ""
            description = ""
            resplink = urllib2.urlopen(req, timeout=60)
            resplinkdata = resplink.read()
            soup = BeautifulSoup(resplinkdata, 'html.parser')  
            subtitle = soup.find("p", { "class" : "drug-subtitle" })
            
            if(subtitle):
                if(subtitle.i):
                    brandnames = subtitle.i.get_text().strip()
                else:
                    brandnames = subtitle.get_text().strip()
            
            # now extract a description
            descsection = soup.find("p", { "itemprop" : "description" })
    
            # there is a header and some paragraph for the main summary
            # description. We only want the summary, and exit out if we
            # hit the next heading (usually additional usage info on the drug)
            if(descsection):
                nextNode = descsection
                while nextNode and nextNode.name != 'h2':
                    nextNode = nextNode.nextSibling
                    try:
                        tag_name = nextNode.name
                    except AttributeError:
                        tag_name = ""
                    if tag_name == "p":
                        if(nextNode and nextNode.string):
                            description += nextNode.string + " "
                        else:
                            break
          
        except Exception,e:
            print str(e)
        except urllib2.URLError:
            pass
        except socket.timeout:
            pass  
        
        return [brandnames, description]
     
     # drugs for each condition are listed 25 a page and to get to all the drugs
     # we have crawl each of the pages
     # scrape_druglist is a recursive function that scrapes the first 
     # landing page and then crawls subsequent pages
    def scrape_druglist(self, condition, pagedurl, islandingpage=True):
        req = urllib2.Request(pagedurl, headers=self.hdr)
        try:
            
            # First get the drug list table. Landing page has some, but there
            # might be additional pages.
            resplink = urllib2.urlopen(req, timeout=60)
            resplinkdata = resplink.read()
            soup = BeautifulSoup(resplinkdata, 'html.parser')        
            conditionTable = soup.find("table", { "class" : "condition-table" })
            
            if(conditionTable):
                # if we hit the condition page, we look for the row 'tr' element
                # containing data we want.
                drugs = conditionTable.tbody.findAll('tr', attrs={'class': re.compile(r"^condition-table__summary")})
                #print "There are " + str(len(drugs)) + " drugs listed on this page."
                for drug in drugs:
                    
                    # for each drug extract attributes
                    drugname = self.get_drugname(drug)
                    drugnamelink = self.get_drugnamelink(drug)
                    rxotc = self.get_prescrptiontype(drug)
                    rating = self.get_rating(drug)
                    popularity = self.get_popularity(drug)
                    csa = self.get_csa(drug)
                    pregcategory = self.get_pregcategory(drug)
                    alcohol = self.get_alcoholinteraction(drug)
                    
                    # crawl one more link to scrape general drug info summary
                    # brand name etc.. 
                    brandnames, description = self.scrape_generalinfo(drugnamelink)   
                    
                    #print "drugname = " + drugname + ", PrescType = " + rxotc + ", Rating = " + str(rating) + ", Popularity = " + str(popularity)
    
                    #put everything into json
                    condition_drug_doc = {
                                 "condition" : condition,
                                 "drug_name" : drugname,
                                 "rxtype" : rxotc,
                                 "rating" : rating,
                                 "popularityscore" : popularity,
                                 "csasched" : csa,
                                 "alcohol" : alcohol,
                                 "pregnancy": pregcategory,
                                 "drug_generalinfo" : description,
                                 "brandnames" : brandnames
                            }
                    
                    # serialize to file.. 
                    if(self.docserializer):
                        self.docserializer.write(condition_drug_doc)
                        
                    # To write to MONGO. 
		    # TODO: parameterize this..   
                    #storecol.insert(condition_drug_doc)  
                
                #if we are on the landing page, find how many pages we have..
                if(islandingpage):
                    pages = soup.find("td", { "class" : "paging-list-page" })
                    if(pages and pages.get_text().lower() == 'page'):
                        pgindxes = soup.find("td", { "class" : "paging-list-index" }).findAll('a')
                        #print "Number of pages = " + str(len(pgindxes) + 1)
                        for page in pgindxes:
                            # recursively scrape the remaining pages from the landing page.
                            self.scrape_druglist(condition, rootdomain+page['href'], False)
                            
        except Exception,e:
            print str(e)
        except urllib2.URLError:
            pass
        except socket.timeout:
            pass
    
    # This is the main entry point to crawling the website
    # This is at the alphabetical page level. eg. all conditions starting with 'a'
    # will be from this page.
    def crawl(self, url, docserializer = None):
        # intialize our doc serializer.
        self.docserializer = docserializer        
        try:
            req = urllib2.Request(url, headers=self.hdr)
            success = 0
            try:
                resplink = urllib2.urlopen(req, timeout=60)
                success = 1
            except urllib2.URLError:
                pass
            except socket.timeout:
                pass

            if (success == 1):
                try:
                    resplinkdata = resplink.read()
                    soup = BeautifulSoup(resplinkdata, 'html.parser')
                    
                    # on the page we want all the conditions for the 
                    # current alphabet we are processing..
                    conditionlist = soup.find("ul", { "class" : "column-list-2" })
                    if (conditionlist):
                        # all the conditions are listed with li elemets
                        for node in conditionlist.findChildren("li"):
                            condition = node.get_text().strip()
                            
                            # we want to extract the link to get to the drug
                            # list for that condition. the href is from the 
                            # root www page, and not from current page.
                            conditionlink = rootdomain + node.a['href']
                            print "Processing " + condition + " : " + conditionlink
                            
                            # start scraping drug lists for this condition.
                            self.scrape_druglist(condition, conditionlink, True)                        
                except:
                    pass
    
        except Exception:
            pass
            
def main():
    
    docserializer = None
    
    # since drugs by condition on drugs dot com is organzied alphabetically
    # we just crawl the page for each alphabet.
    for searchalphabet in "abcdefghijklmnopqrstuvwxyz":
        #$for searchalphabet in "ab":   
        try:
            
            #adjust this output file accordingly
            drugsjson = os.getcwd() + r'/Data/drugsdotcom/' + searchalphabet + '_drugsbycondition.json'   
            
            # this is the main entry point to the list of condtions starting
            # with a particular alphabet.
            link = rooturl + '/' + searchalphabet + '.html'
            
            # ---------------------------------------------------------------------
            # DEBUG.....            
                #link = "https://www.drugs.com/condition/seizures.html"
                #scrape_druglist("a", link, hdr, True)
                #scrape_generalinfo('https://www.drugs.com/briviact.html', hdr)
            # ---------------------------------------------------------------------
            
            # initialize doc serializer
            docserializer = JsonDocSerializer(drugsjson)
            
            # initialize the crawler and start crawling
            crawler = DrugsDotComRootAlphabetCrawler()            
            if(crawler):
                crawler.crawl(link, docserializer)
            
            # close serializer.
            docserializer.close()
            
        except Exception,e:
            print str(e)
            #Close our serializer to complete save anything we have to file.
            if(docserializer != None):
                docserializer.close()
            
main()
