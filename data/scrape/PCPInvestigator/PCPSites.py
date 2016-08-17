import time, inspect
from datetime import datetime

from bs4 import BeautifulSoup
import re
import urllib, urllib2
from urllib2 import urlopen
from nltk import metrics, stem, tokenize
import jellyfish
import os
#os.chdir('/home/dsq/Dropbox/DataScienceBerkeley/CAPSTONE/ACA_Capstone/github/PCPInvestigator/')
######################################
# Scrapeable
######################################

stemmer = stem.PorterStemmer()
def normalize(s):
	words = tokenize.wordpunct_tokenize(s.lower().strip())
	return ' '.join([stemmer.stem(w) for w in words])
 
def fuzzy_match(s1, s2, max_dist=3):
	return metrics.edit_distance(normalize(s1), normalize(s2)) <= max_dist
	
class Scrapeable(object):

	NICKNAME 	= None
	URL 		= None
	MAXRATING 	= 0

	def __init__(self, sourcePath=None):

		self.setSourcePath(sourcePath)



	######################################
	# clean
	######################################	
	def clean(self, streeng) :

		return streeng.strip('"').strip().strip("\r\n")


	####################################################################		
	####################################################################
	# ABSTRACT METHODS
	####################################################################
	####################################################################
	def abstract():
		caller = inspect.getouterframes(inspect.currentframe())[1][3]
		raise NotImplementedError(caller + ' must be implemented in subclass')
								
								
	def scrape(self, sourcePath):
		abstract()


	####################################################################
	# INSTANCE METHODS
	####################################################################

	######################################
	# setSourcePath
	######################################
	def setSourcePath(self, sourcePath) :

		self.sourcePath = sourcePath
		self.initializeFindings()


	######################################
	# initializeFindings
	######################################
	def initializeFindings(self) :

		self.reviews = []
		self.overallscore = 0
		self.summary = None
		self.numreviews = 0


	######################################
	# nameMatches
	######################################
	def nameMatches(self, businessName, nameTerms) :

		business = ' '.join(businessName)
		provname = ' '.join(nameTerms)

		print "For %s, comparing %s to %s..."%(self.NICKNAME, businessName, nameTerms)

		#use the Jaro_winkler distance algo 
		jarowinkdist = jellyfish.jaro_winkler(business, provname)
		if(jarowinkdist > 0.97):
			print "Match!"
			return True
				
		for nameTerm in nameTerms :
			if nameTerm not in businessName :
				return False

		print "Match!"
		return True

	def addressMatches(self, businessAddress, addressTerms) :

		print "For %s, comparing %s to %s..."%(self.NICKNAME, businessAddress, addressTerms)
  
		   #Compare the City, State and Zip first.. if these don't match, then exit.
		for addressTerm in addressTerms[1:] :
			if addressTerm not in businessAddress[1:] :
				return False
				
		#use the Jaro_winkler distance algo 
		jarowinkdist = jellyfish.jaro_winkler(businessAddress[0], addressTerms[0])
		if(jarowinkdist > 0.80):
				print "Match!"
				return True
  
####################################################################
# HealthGrades
####################################################################
class HealthGrades(Scrapeable):

	NICKNAME 	= "healthgrades"
	URL 		= "http://www.healthgrades.com"
	MAXRATING 	= 5.0


	######################################
	# scrape
	######################################				
	def scrape(self, nameTerms=[], addressTerms=[]):


		self.sourcePath = "%s/patient-ratings"%("http://%s"%"/".join(self.sourcePath.split("/")[2:5]))

		try :
			html = urlopen(self.sourcePath).read()
		except urllib2.HTTPError, e :
			return False

		return self._scrape(html, nameTerms, addressTerms)


	######################################
	# _scrape
	######################################	
	def _scrape(self, html, nameTerms=[], addressTerms=[]) :

		soup = BeautifulSoup(html, "lxml")

		if nameTerms :

			# Verify the name is what we expect
			#
			businessName = soup.find("span", {"itemprop": "name"}).string
			if not self.nameMatches(businessName, nameTerms) :
				print "Name does not match satisfactorily."
				return False
			else :
				print "Name match!"


		# Only count score if there are reviews
		#
		reviewItem = soup.find("div", "score rowItem")

		if not reviewItem :
			print "No review items found."
			return False

		self.overallscore	= float(reviewItem.find("span", {"itemprop": "ratingValue"}).string)/self.MAXRATING

		numReviewString 	= reviewItem.find("li").string
		numReviewString		= re.sub('responses', '', re.sub('response$', '', numReviewString.strip()))
		self.numreviews		= int(numReviewString)

		# Get reviews
		#
		surveyrows			= soup.find("div", "totalStarsRatings")(attrs={'class': 'ratingsRow'})
		
		for i, row in enumerate(surveyrows) :

			#print "Considering row %s of %s..."%(i, len(surveyrows))

			relevantlabel = row.find("h2", "starDescription")
			if relevantlabel :

				title 			= self.clean(relevantlabel.string)					
				result 			= row.find("p", "starRating")
				if result :
					result = result.string
					if " out of " in result :
						scoreValues = result.split(" out of ")
						score = (float(scoreValues[0]) * 10)/(self.MAXRATING * 10)
					else :
						score = self.clean(result.replace(u'\u2013', "-"))
				else :
					score = row.find("div", "waitTime").string

				overalldescription = ""

				comments = []

				self.reviews.append({"overalldescription": overalldescription, "title": title, "comments":comments, "score":score})


		# We successfully scraped!
		#
		return True



####################################################################
# UCompareHealthCare
####################################################################
class UCompareHealthCare(Scrapeable):

	NICKNAME 	= "ucomparehealthcare"
	URL 		= "http://www.ucomparehealthcare.com"
	MAXRATING 	= 5.0



	######################################
	# scrape
	######################################				
	def scrape(self, nameTerms=[], addressTerms=[]):


		# Desired path looks like http://www.ucomparehealthcare.com/drs/ara_balkian/
		#
		self.sourcePath = "%s"%("http://%s"%"/".join(self.sourcePath.split("/")[2:5]))
		print self.sourcePath

		try :
			html = urlopen(self.sourcePath).read()
		except urllib2.HTTPError, e :
			return False

		return self._scrape(html, nameTerms, addressTerms)


	######################################
	# _scrape
	######################################	
	def _scrape(self, html, nameTerms=[], addressTerms=[]) :

		soup = BeautifulSoup(html, "lxml")

		if nameTerms :

			# Verify the name is what we expect
			#
			header = soup.find("h1", {"itemprop": "name"})
			mainName = header.find("span", "fn").string if header.find("span", "fn") and header.find("span", "fn").string else "" 
			#suffix = header.find("small").string if header.find("small") and header.find("small").string else ""
			businessName = mainName.lower().split(' ') #" ".join([mainName, suffix])
			
			#check addresses.
			addressinfo = soup.find("div" , {"class":"primary-location v-card"})
			if(addressinfo is not None) :
				 businessStreetAddress = soup.find("span", {"itemprop": "streetAddress"}).text.lower()
				 businessCity = soup.find("span", {"itemprop": "addressLocality"}).text.lower()
				 businessState = soup.find("span", {"itemprop": "addressRegion"}).text.lower()
				 businessZip = soup.find("span", {"itemprop": "postalCode"}).text.lower()
				
				 businessAddress = [businessStreetAddress, businessCity, businessState, businessZip]
			
			if businessName and businessAddress :
				if not self.nameMatches(businessName, nameTerms) and not self.addressMatches(businessAddress, addressTerms):
					print "Name and Address does not match satisfactorily."
					return False

		#overview = soup.find("div", "ind-reviews-summary ind-reviews-none")
		overview = soup.find("div", "col-sm-8 col-md-10 col-xs-8")
		
		if overview :

			summaryText = overview.find("p")
			summaryKeys = [key.string for key in summaryText.findAll("strong")]

			if summaryKeys :

				self.overallscore 	= float(summaryKeys[0])/self.MAXRATING
				self.summary 		= summaryKeys[1]
				self.numreviews 	= int(summaryKeys[2])

				# Get reviews
				#
				reviewblock = soup.find("ul", "list-group panel-listing")

				if reviewblock :

					reviewbullets =reviewblock.findAll("li", "list-group-item reviews-container-collapsed")

					for reviewbullet in reviewbullets :

						stars = reviewbullet.find("div", "stars-ph")
						overalldescription = stars.find("div", "reviews-overall-description").string

						titleblock = reviewbullet.find("strong", "reviews-headline")
						title = titleblock.string
						dateString = titleblock.find("span").string.lstrip(" posted on ")
						try :
							date = datetime.strptime(dateString, '%B %d, %Y').strftime("%Y-%m-%d") # Turn February 3, 2010 --> 2012-02-03
						except ValueError, e :
							date = dateString

						# Get comments
						#
						comments		= []
						breakdown = reviewbullet.find("div", "reviews-breakdown list-group")
						comments.extend([div.string for div in breakdown.findAll("div", "review-comment")])
						comments.extend([div.string for div in breakdown.findAll("p", "reviews-comments")])

						# Get number of stars
						#
						starclass = stars.find("span")["class"]
						numstars = starclass[0].strip("rsta").replace("-",".") # Remove "rstars" part of class to turn rstars1 into 1 and rstars1-5 into 1.5
						score = float(numstars)/self.MAXRATING

						self.reviews.append({"overalldescription": overalldescription, "title": title, "comments":comments, "score":score, "date":date})

					print " %s reviews found"%len(self.reviews)


					# We successfully scraped!
					#
					return True

		print "No reviews found."
		return False




####################################################################
# Vitals
####################################################################
class Vitals(Scrapeable):

	NICKNAME 	= "vitals"
	URL 		= "http://www.vitals.com"
	MAXRATING 	= 5.0

	STAR_TRANSLATOR = {"one": 1, "two": 2, "three":3, "four": 4, "five": 5}


	######################################
	# scrape
	######################################				
	def scrape(self, nameTerms=[], addressTerms=[]):


		# Desired URL looks like http://www.vitals.com/doctors/Dr_Firstname_Lastname
		#
		self.sourcePath = "%s/reviews"%("http://%s"%"/".join(self.sourcePath.replace(".html", "").split("/")[2:5]))
		print self.sourcePath

		try :
			html = urlopen(self.sourcePath).read()
		except urllib2.HTTPError, e :
			return False

		return self._scrape(html, nameTerms, addressTerms)


	######################################
	# _scrape
	######################################	
	def _scrape(self, html, nameTerms=[], addressTerms=[]) :

		soup = BeautifulSoup(html, "lxml")
		
		if nameTerms :

			# Verify the name is what we expect
			#
			reviewspane = soup.find("div", {"class": "block minimal-nopad reviews"})

			if not reviewspane :
				print "No reviews pane found."
				return False

			businessProfile = soup.find("span", {"class": "claim-profile"})
			if businessProfile:
				businessProfileName = businessProfile.find("h3")
				if businessProfileName:
					businessName = businessProfileName.text.lower().split(',')[0].split(' ')
				
                #check addresses.
			addressinfo = soup.find("address" , {"itemprop":"address"})
			if(addressinfo is not None) :
				 businessStreetAddress = soup.find("span", {"class": "addr_line"}).text.lower()
				 businessCity = soup.find("span", {"itemprop": "addressLocality"}).text.lower()
				 businessState = soup.find("span", {"itemprop": "addressRegion"}).text.lower()
				 businessZip = soup.find("span", {"itemprop": "postalCode"}).text.lower()
				
				 businessAddress = [businessStreetAddress, businessCity, businessState, businessZip]

			#Check address as well.. and if we don't get a match we are done.. bail
			if businessName and businessAddress :
				if not self.nameMatches(businessName, nameTerms) and not self.addressMatches(businessAddress, addressTerms):
					print "Address does not match satisfactorily."
					return False
		
		#we have a match.. find the reviews and ratings
		overview = soup.find("div", "child overall")
		
		if overview :

			numstarsclause 			= overview.find("td", {"id": "overall_rating"})
			numstars				= numstarsclause.find("span").string
			self.overallscore 	= float(numstars)/self.MAXRATING
			self.summary 		= ""
			self.numreviews 	= int(overview.find("td", {"id": "overall_total_ratings"}).find("h3").string)

			reviewblock 		= soup.find("div", {"id": "reviewspane"})

			if reviewblock :

				print "found a block of reqviews"

				reviewbullets 		= reviewblock.findAll("div", "review")

				for i, reviewbullet in enumerate(reviewbullets) :

					#print "Considering review %s of %s..."%(i, len(reviewbullets))

					# Get number of stars
					#
					starclause = reviewbullet.find("ul", "score star medium")

					if starclause :

						starbullet = starclause.find("li")

						if not starbullet :
							print "Star bullet not found... moving on..."
							continue

						starclasses = starbullet['class']
						numstars = self.STAR_TRANSLATOR[starclasses[1]]
						if ("half" in starclasses) : numstars += 0.5
						#print "numstars: %s"%numstars
						score = float(numstars)/self.MAXRATING

						overalldescription = "" #Vitals doesn't do a "poor" or "good" type description
						title = reviewbullet.find("span", "summary").string if reviewbullet.find("span", "summary") else ""

						datestring = reviewbullet.find("span", "date c_date dtreviewed").find("span", "value-title")["title"]
						date = self.clean(datestring)

						# Get comments
						#
						comments		= []
						commentnode 	= reviewbullet.find("p", "description")
						if commentnode :
							comments.append(commentnode.string.strip('"'))

						self.reviews.append({"overalldescription": overalldescription, "title": title, "comments":comments, "score":score, "date": date})

				print " %s reviews found"%len(self.reviews)


			# We successfully scraped!
			#
			return True


		return False




####################################################################
# Yelp
####################################################################
class Yelp(Scrapeable):

	NICKNAME 	= "yelp"
	URL 		= "http://www.yelp.com"
	MAXRATING 	= 5.0

	######################################
	# scrape
	######################################				
	def scrape(self, nameTerms=[], addressTerms=[]):


		#self.sourcePath = "%s?ob=1"%(self.sourcePath)
		#print self.sourcePath

		try :
			html = urlopen(self.sourcePath).read()
		except urllib2.HTTPError, e :
			return False

		return self._scrape(html, nameTerms, addressTerms)


	######################################
	# _scrape
	######################################	
	def _scrape(self, html, nameTerms=[], addressTerms=[]) :

		soup = BeautifulSoup(html, "lxml")
		   
		for e in soup.findAll('br'):
			e.replace_with(' ')()

		if nameTerms :

			# Verify the name is what we expect
			#  <span itemprop="streetAddress">341 W Tudor Rd<br>Ste 101</span><br><span itemprop="addressLocality">Anchorage</span>, <span itemprop="addressRegion">AK</span> <span itemprop="postalCode">99503</span><br><meta content="US" itemprop="addressCountry">
			businessName = soup.find("h1", {"itemprop": "name"})
			businessStreetAddress = soup.find("span", {"itemprop": "streetAddress"}).text.lower()
			businessCity = soup.find("span", {"itemprop": "addressLocality"}).text.lower()
			businessState = soup.find("span", {"itemprop": "addressRegion"}).text.lower()
			businessZip = soup.find("span", {"itemprop": "postalCode"}).text.lower()
				
			businessAddress = [businessStreetAddress, businessCity, businessState, businessZip]
				
			if not businessName or not self.nameMatches(businessName.string, nameTerms) :
				print "Name does not match satisfactorily."
				
			#Check address as well.. and if we don't get a match we are done.. bail
			if not businessAddress or not self.addressMatches(businessAddress, addressTerms):
				print "Address does not match satisfactorily."
				return False


		ratingContent = soup.find("meta", {"itemprop": "ratingValue"})

		if not ratingContent :
			print "No rating content found."
			return False

		self.overallscore 	= float(ratingContent["content"])/self.MAXRATING
		self.numreviews 	= int(soup.find("span", {"itemprop": "reviewCount"}).string)
		self.summary 		= ""

		reviewblock 		= soup.find("div", "feed")

		if not reviewblock :
			print "No review block found."
			return False

		if reviewblock :

			reviewbullets 		= reviewblock.findAll("div", "review-content")

			for reviewbullet in reviewbullets :

				# Get number of stars
				#
				numstars = reviewbullet.find("meta", {"itemprop": "ratingValue"})["content"]
				score = float(numstars)/self.MAXRATING

				overalldescription 	= "" # Yelp doesn't do a "poor" or "good" type description
				title 				= "" # Yelp doesn't do comment titles either

				date = reviewbullet.find("meta", {"itemprop": "datePublished"})["content"]

				# Get comments
				#
				comments		= []

				commentnode 	= reviewbullet.find("p", {"itemprop": "description"})

				if commentnode :
					comments.append(commentnode.string)

				self.reviews.append({"overalldescription": overalldescription, "title": title, "comments":comments, "score":score, "date": date})

			print " %s reviews found"%len(self.reviews)

			# We successfully scraped!
			#
			return True





