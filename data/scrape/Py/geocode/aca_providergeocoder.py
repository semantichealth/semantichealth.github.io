#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
@author:  Tigi Thomas
@project: MIDS W210 Capstone - ACA Semantic Search
@module:  aca_providergeocoder
@desc :   This module scapes fetches geocode using SmartyStreets, Google geocoder
	  and geopy's Nominatim. The input data is provider data (address , npi etc)
	  extracted from Mongodb to json files. The module takes an input path -i, 
	  an output path -o, a path for storing address for which geo data could not 
	  be pulled -r. 
	  Much thanks to Jefferson from SmartyStreets who allowed us an unlimitted pull
	  of Addresses for this project. Please visit SmartyStreets.com. They are awesome.

	  The code will attempt to use SmartyStreets and if not available, try Google and then 
	  eventually try Geopy's Nominatim. 
	  Soring those that could not be pulled on first attemtp will be run thru again in subsequent runs.
"""
# !/usr/bin/python

import time, sys, datetime, json
import geocoder
import os
import optparse
#import progressbar
from geopy.geocoders import Nominatim
import random
import aca_SMARTYSTREETSKEYS as smtykeys
import urllib

LOCATION = "https://api.smartystreets.com/street-address/"
	
#ProviderGeoCoder
class ProviderGeoCoder(object) :

    def __init__(self):
        
        self.goog = False
        self.parsedOptions = None 
        self.geostash = None
        self.geolocator = Nominatim()
        #self.smtystreet = Client(smtykeys.AUTH_ID, smtykeys.AUTH_TOKEN)
        self._loadOptions()

   
    def _loadOptions(self):    
    
		self.options = optparse.OptionParser()
					
		self.options.add_option("-g", "--goog", action="store_true", default=False, 
                            help="use google based geocoder to pull data.")
															
		self.options.add_option("-t", "--street", action="store_true", default=False, 
                            help="use smartystreet based geocoder to pull data.")
																												
		self.options.add_option("-s", "--states", action="store", type="string", dest="states", 
                            help="comma separted statelist")
																												
		self.options.add_option("-i", "--inpath", action="store", type="string", dest="inpath", 
                            help="input path")
																												
		self.options.add_option("-o", "--outpath", action="store", type="string", dest="outpath", 
                            help="output path")
																												
		self.options.add_option("-r", "--ropath", action="store", type="string", dest="ropath", 
                            help="rerun out path ")

	#Use Google api behind geocoder - limited to 2500 queries per day / IP		
    def geocoderFetchGeoCode(self, query):	

		geocode = None	
		try:
			g = geocoder.google(query)
			geocode = g.latlng
		except:
			pass
		
		return geocode

	# use SmartyStreets API
    def smartyStreetFetchGeoCode(self, address, city, state, zipcode):	
		geocode = None
		
		try:
			QUERY_STRING = urllib.urlencode({   # entire query sting must be URL-Encoded
			    "auth-id": smtykeys.AUTH_ID,
			    "auth-token": smtykeys.AUTH_TOKEN,
			    "street": address,
			    "city": city,
			    "state": state,
			    "zipcode": zipcode,
			    "candidates": "1",
			})
			URL = LOCATION + "?" + QUERY_STRING
			
			response = urllib.urlopen(URL).read()
			structure = json.loads(response)
			
			if(	structure \
				and structure[0]["metadata"] \
				and structure[0]["metadata"]["latitude"] \
				and structure[0]["metadata"]["longitude"]):	
					geocode = [structure[0]["metadata"]["latitude"], structure[0]["metadata"]["longitude"]]
					
		except Exception, e:
			pass
			#print str(e)
				
		return geocode
		
	#Use Geopy's Nominatim - no limit, but really slow 	
    def geopyFetchGeoCode(self, query):		
		
		geocode = None
		try:
			location = self.geolocator.geocode(query,timeout=10)
			if(location and location.latitude and location.longitude):
				geocode = [location.latitude, location.longitude]
		except:
			pass

		return geocode

    def parseOptions(self, options) :

		self.parsedOptions = None    
		(self.parsedOptions, self.remaining) = self.options.parse_args(list(options))
           
		if getattr(self.parsedOptions, "goog") :
			self.goog = self.parsedOptions.goog
			
		if getattr(self.parsedOptions, "street") :
			self.street = self.parsedOptions.street
			
		if getattr(self.parsedOptions, "states") :
			self.states = self.parsedOptions.states.split(',')
			
		if getattr(self.parsedOptions, "inpath") :
			self.inpath = self.parsedOptions.inpath
			
		if getattr(self.parsedOptions, "outpath") :
			self.outpath = self.parsedOptions.outpath
		
		if getattr(self.parsedOptions, "ropath") :
			self.ropath = self.parsedOptions.ropath

	#Pre-process Provider data
    def createProviderObj(self, providerjson) :
          providerObj = {}
          
          '''
          if "npi" in providerjson and providerjson["npi"]:
               providerObj["npi"] = providerjson["npi"]
          else:
		    providerObj["npi"] = ""
          '''	
											
          if "address" in providerjson["addresses"][0] and providerjson["addresses"][0]["address"]:
              providerObj["address"] = providerjson["addresses"][0]["address"]
          else:
              providerObj["address"] = ""
														
          if "city" in providerjson["addresses"][0] and providerjson["addresses"][0]["city"]:
              providerObj["city"] = providerjson["addresses"][0]["city"]
          else:
              providerObj["city"] = ""
              
          if "state" in providerjson["addresses"][0] and providerjson["addresses"][0]["state"]:
              providerObj["state"] = providerjson["addresses"][0]["state"]
          else:
              providerObj["state"] = ""
              
          if "zip" in providerjson["addresses"][0] and providerjson["addresses"][0]["zip"]:
              providerObj["zip"] = providerjson["addresses"][0]["zip"]
          else:
              providerObj["zip"] = ""
              
          return providerObj
										
    def runAction(self) :

		infile_prefix = self.inpath #infile prefix where input files are
		outfile_prefix = self.outpath #output for those what we successfully pulled geo
		rerurnout_prefix = self.ropath #Stash for re-run
		
		#states = ["AK", "AL"]
		for state in self.states:
			self.geostash={}
			#pbar = progressbar.ProgressBar()
			print "Geocoding Providers in Sate %s..."%state
			
			#Prepare prefix for our files.
			infilename = infile_prefix + state + '.json'
			outfilename = outfile_prefix + state + '.json'
			rerunfilename = rerurnout_prefix + state + '.json'
			
			with open(outfilename,"w+") as outfile, open(rerunfilename, "w+") as rerunfile:  
				with open(infilename,"r") as infile: 
					for providerjson in infile.readlines():
						providerObj = self.createProviderObj(json.loads(providerjson)[0])
						
						address, city, state, zipcode = providerObj["address"], providerObj["city"], providerObj["state"], providerObj["zip"]
						query = "%s, %s, %s, %s"%(address, city, state, zipcode)
						
						if not (query in self.geostash):
							#use SmartyStreets
							geocode = self.smartyStreetFetchGeoCode(
									providerObj["address"], \
									providerObj["city"], \
									providerObj["state"], \
									providerObj["zip"])
									
							#if we did not get valid geo , try google	
							if not geocode:
								geocode = self.geocoderFetchGeoCode(query)
								
							#finally try geopy
							if not geocode:
								geocode = self.geopyFetchGeoCode(query)
		            
							self.geostash[query] = geocode
							# if we got an empty geocode, we just push it to the re-run
							if not geocode:
								jsdump = json.dumps(providerObj)
								rerunfile.write('[')
								rerunfile.write(jsdump)
								rerunfile.write(']\n') 
							else:
								# we got a valid code, write it to the out file, which we can then just import into Mongo.
								providerObj["geocode"] = geocode
								#print "--------------------------"
								#print providerObj
								jsdump = json.dumps(providerObj)
								outfile.write('[')
								outfile.write(jsdump)
								outfile.write(']\n')                     
								#print "*** DONE SAVING ***"

		print 'All Done'


if __name__ == '__main__':
	options = sys.argv
	workingObj = ProviderGeoCoder()
	workingObj.parseOptions(options)
	workingObj.runAction() 

