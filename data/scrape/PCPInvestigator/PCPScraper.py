
import time, sys, datetime, json
from collections import defaultdict

from bs4 import BeautifulSoup
import urllib, urllib2
from urllib2 import urlopen

import jellyfish
import os
import optparse

import PCPSites
import PCPConstants as CONSTANTS
import random

SEARCH_TOOL = "https://www.google.com"

SOURCE_SITES = [PCPSites.HealthGrades,
                PCPSites.Vitals,
                PCPSites.UCompareHealthCare,
                PCPSites.Yelp
                ]

#headers = {'User-Agent':'Mosilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11'}

hdr1 = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}

hdr2 = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}

hdr3 = {
    'User-Agent': 'Opera/9.80 (X11; Linux i686; Ubuntu/14.10) Presto/2.12.388 Version/12.16',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}				

headers = [hdr1, hdr2, hdr3]	
			
############################################################# 
#############################################################
######## PCPScraper
############################################################# 
############################################################# 

class PCPScraper(object) :


    def __init__(self):
        
        self.dryrun = False
        self.parsedOptions = None    

        self._loadOptions()


    ####################################################################
    # _loadOptions
    ####################################################################    
    def _loadOptions(self):    
    
		self.options = optparse.OptionParser()

		self.options.add_option("-d", "--dryrun", action="store_true", default=False, 
                            help="Simulate and generate output for first five entries. Do not add to database.")
																												
		self.options.add_option("-s", "--states", action="store", type="string", dest="states", 
                            help="comma separted statelist")
																												
		self.options.add_option("-i", "--inpath", action="store", type="string", dest="inpath", 
                            help="input path")
																												
		self.options.add_option("-o", "--outpath", action="store", type="string", dest="outpath", 
                            help="output path")

    ######################################
    # scrapeSearch
    ######################################
    def scrapeSearch(self, firstname, middlename, lastname, address, city, state, zipcode, speciality, moveonIfFail=True) :
        """
        Action:        Perform search for provider and return all resulting links
        
        """    
        # Number of results to search for (20 usually gets us what we want)
        #
        maxResults = 20

        # Perform search
        #    
        firstname = firstname if not middlename else "%s+%s"%(firstname, middlename)
        query = "%s+%s+%s+%s+%s+%s+s%+reviews"%(firstname, lastname, address, city, state, zipcode, speciality)

        #print "query %s"%query

        # Scrape all links in the results
        #
        address = "%s/search?q=%s&num=%s&hl=en&start=0" % (SEARCH_TOOL, urllib.quote_plus(query), maxResults)
        print "Address %s"%address

        request = urllib2.Request(address, None, random.choice(headers))

        try :

            urlfile = urllib2.urlopen(request)

        except urllib2.HTTPError, e :

            print "Hit an HTTPError %s. Retrying..."%e
            time.sleep(random.choice(CONSTANTS.SEARCH_SLEEPTIME))
            if moveonIfFail :
                return self.scrapeSearch(firstname, middlename, lastname, address, city, state, zipcode, speciality, moveonIfFail=False)
            else :
                return []


        page = urlfile.read()

        #print "Page: %s"%page

        soup = BeautifulSoup(page, 'html.parser')

        allLinks = []
        for h3 in soup.findAll('h3', attrs={'class':'r'}):
            #print "h3: %s"%h3
            sLink = h3.find('a')
            #print "sLink %s"%sLink['href']
            allLinks.append(sLink['href'])

        return allLinks


    ######################################
    # loadSites
    ######################################
    def loadSites(self, searchResults, lastname) :
        """
        Action:        From a list of URLs, return the URLs we're interested in
        
        """    

        loadedSites = []

        for siteclass in SOURCE_SITES :

            for sourcepath in searchResults :

                # Verify that the URL is from a source we like and has the given last name in the URL
                # This is not foolproof, but we'll do a better sanity check when we scrape
                #
                if sourcepath.startswith(siteclass.URL) and lastname.lower() in sourcepath.lower() :                           
                    loadedSites.append(siteclass(sourcepath))
                    print "h3: %s"%sourcepath
     
        return loadedSites

    ######################################
    # parseOptions
    ######################################
    def parseOptions(self, options) :

		self.parsedOptions = None    
		(self.parsedOptions, self.remaining) = self.options.parse_args(list(options))

		if getattr(self.parsedOptions, "dryrun") :
			self.dryrun = self.parsedOptions.dryrun
           
		if getattr(self.parsedOptions, "states") :
			self.states = self.parsedOptions.states.split(',')
			
		if getattr(self.parsedOptions, "inpath") :
			self.inpath = self.parsedOptions.inpath
			
		if getattr(self.parsedOptions, "outpath") :
			self.outpath = self.parsedOptions.outpath
												
    def createProviderObj(self, providerjson) :
          providerObj = {}
          if "first" in providerjson["name"] and providerjson["name"]["first"]:
               providerObj["firstname"] = providerjson["name"]["first"]   
               
          if "last" in providerjson["name"] and providerjson["name"]["last"]:
              providerObj["lastname"] = providerjson["name"]["last"]  
              
          if "middle" in providerjson["name"] and providerjson["name"]["middle"]:
              providerObj["middlename"] = providerjson["name"]["middle"] 
          else:
              providerObj["middlename"] = ""
              
          if "prefix" in providerjson["name"] and providerjson["name"]["prefix"]:
              providerObj["prefix"] = providerjson["name"]["prefix"] 
          else:
              providerObj["prefix"] = ""
              
          if "address" in providerjson["addresses"][0] and providerjson["addresses"][0]["address"]:
              providerObj["address"] = providerjson["addresses"][0]["address"].lower()
          else:
              providerObj["address"] = ""
              
          if "address_2" in providerjson["addresses"][0] and providerjson["addresses"][0]["address_2"]:
              providerObj["address"] += ' ' + providerjson["addresses"][0]["address_2"].lower()
              
          if "city" in providerjson["addresses"][0] and providerjson["addresses"][0]["city"]:
              providerObj["city"] = providerjson["addresses"][0]["city"].lower()
          else:
              providerObj["city"] = ""
              
          if "state" in providerjson["addresses"][0] and providerjson["addresses"][0]["state"]:
              providerObj["state"] = providerjson["addresses"][0]["state"].lower()
          else:
              providerObj["state"] = ""
              
          if "zip" in providerjson["addresses"][0] and providerjson["addresses"][0]["zip"]:
              providerObj["zip"] = providerjson["addresses"][0]["zip"]
          else:
              providerObj["zip"] = ""
              
          if "speciality" in providerjson and providerjson["speciality"][0]:
              providerObj["speciality"] = providerjson["speciality"][0]
          else:
              providerObj["speciality"] = ""
              
          return providerObj
         
    ######################################
    # runAction
    ######################################
    def runAction(self) :

		infile_prefix = self.inpath
		outfile_prefix = self.outpath
		#states = ["AK", "AL"]
		for state in self.states:
			print "Searching for providers in %s..."%state
			infilename = infile_prefix + state + '.json'
			outfilename = outfile_prefix  + state + '.json'
			#infilename = r'/home/dsq/Dropbox/DataScienceBerkeley/CAPSTONE/ACA_Capstone/Data/ProvidersByState/TestProvidersAK.json'
			#outfilename = r'/home/dsq/Dropbox/DataScienceBerkeley/CAPSTONE/ACA_Capstone/Data/ProvidersByState/TestProvidersAK_Reviewed.json'
			with open(outfilename,"w+") as outfile:  
				with open(infilename,"r") as infile: 
					for providerjson in infile.readlines():
						providerObj = self.createProviderObj(json.loads(providerjson)[0])
						
						# Proceed only if we have found a name to search for
						#
						if "lastname" in providerObj :
							# Fetch dict of form {"vitals": "http://...."}
							#
							print "------------------------------------------------------------"
							print "*** SEARCHING for %s ***"%([providerObj["firstname"], providerObj["middlename"], providerObj["lastname"], providerObj["prefix"]])
							print "------------------------------------------------------------"
		            
							searchResults = self.scrapeSearch(providerObj["firstname"], \
								providerObj["middlename"], \
								providerObj["lastname"], \
								providerObj["address"], \
								providerObj["city"], \
								providerObj["state"], \
								providerObj["zip"], \
								providerObj["speciality"]) 
								
							sites = self.loadSites(searchResults, providerObj["lastname"])
		            
							print "FOUND POTENTIAL SITES: " + str([site.NICKNAME for site in sites])
		            
							ratings = []
							completedSites = []
		            
							for site in sites :
		            
								# If we already scraped this site, move on
		                                #
								if site.NICKNAME in completedSites :
									continue
		            
								time.sleep(random.choice(CONSTANTS.SITE_SLEEPTIME))
		            
								print "SCRAPING SITE %s via %s..."%(site.NICKNAME, site.sourcePath)
		            
								# Verify that first, last and title (e.g. MD, DDS) are in the business name of the site

								nameTerms = [providerObj["firstname"].lower(), providerObj["middlename"].lower(), providerObj["lastname"].lower()]
								addressTerms = [providerObj["address"],providerObj["city"], providerObj["state"], providerObj["zip"]]
		            
								scrapeSuccessful = site.scrape(nameTerms, addressTerms)
		            
								# If our scrape succeeded,
								# we can check this site off the list
								#
								if scrapeSuccessful :
		            
									print "--------------------------"
									print "%s RESULTS: %s"%(site.NICKNAME, str([site.overallscore, site.summary, site.numreviews])) #, json.dumps(site.reviews)]))
									print "--------------------------"
		            
									ratings.append({"sourcetype": site.NICKNAME,
										"path": site.sourcePath,
										"overallscore": site.overallscore,
										"numreviews": site.numreviews
										#"summary": site.summary,
										#"reviews": site.reviews
										})
		            
									completedSites.append(site.NICKNAME)
		            
								else :
		            
									print "SCRAPE FAILED. PROVIDER MISMATCH OR NO REVIEWS?"
		            
								print "--------------------------"
		            

							providerObj["ratings"] = ratings
							providerObj["lastscraped"] = datetime.date.today().strftime("%Y-%m-%d %H:%M:%S")
	                            
							if not self.dryrun :
								print "--------------------------"
								print "*** SAVING results of %s to %s %s %s ***"%(completedSites, providerObj["firstname"], providerObj["lastname"], providerObj["prefix"])
								#print providerObj
								jsdump = json.dumps(providerObj)
								outfile.write('[')
								outfile.write(jsdump)
								outfile.write(']\n')                     
								#providers.save(providerObj)
								print "*** DONE SAVING ***"
								print "--------------------------"
			            
							print "------------------------------------------------------------"


######################################
# Main action
######################################

if __name__ == '__main__':
	options = sys.argv
	workingObj = PCPScraper()
	workingObj.parseOptions(options)
	status = workingObj.runAction()        
	sys.exit(status)
