from collections import defaultdict
import re, sys, optparse
import PCPConstants as CONSTANTS
import pymongo

# CHANGE THIS to connect to the json database you'd like to use
#
connection = pymongo.MongoClient(CONSTANTS.DB_HOST, CONSTANTS.DB_PORT) # default port for mongo
db = connection.test # attach to test db
providers = db.providers # get handle for providers


##############################
#
# Expected sample format of entries in the file to be read
#
#Provider ID #: 123456
#PROSPECT HEALTHSOURCE
#MEDGR, INC
#Lastname, Firstname, MD
#Internal Medicine
#12345 West Washington Blvd.
#Los Angeles, CA 90066
#(310) 123-4567 
#
#
##############################


# SAMPLE USE
#
# python PCPReader.py -n aetna_2015 -f /path/to/input/aetna_provider_01.txt



############################################################# 
#############################################################
######## PCPReader
############################################################# 
############################################################# 

class PCPReader(object) :


	def __init__(self):
		
		self.dryrun = None
		self.providerFile = None

		self._loadOptions()


	####################################################################
	# _loadOptions
	####################################################################	
	def _loadOptions(self):	
	
		self.options = optparse.OptionParser()

		self.options.add_option("-f", "--providerFile", 				action="store", 	dest="providerFile", 				default=None,
							help='Full path to providerFile. See sample provider file for desired format, or adjust format parser.')

		self.options.add_option("-n", "--nickname",	 					action="store", 	dest="nickname", 				default=None,
							help='Insurance nickname, to be stored with each provider (e.g. aetna, kaiser, bluecross)')

		self.options.add_option("-d", "--dryrun", action="store_true", default=False, 
							help="Simulate and generate output for first five entries. Do not add to database.")


	####################################################################
	# parseName
	####################################################################
	def parseName(self, nameLine) :

		re1='((?:[a-z][a-z\-]+))'	# Word 1
		re2='(,)'	# Any Single Character 1
		re3='(\\s+)'	# White Space 1
		re4='((?:[a-z][a-z\-]+))'	# Word 2
		re5='(\\s+)?'	# White Space 2, optional	
		re6='([a-z\-]+)?'	# Optional middle initial or name
		re7='(\\.)?'	# Any Single Character 2, optional		
		re8='(,)'	# Any Single Character 3
		re9='(\\s+)'	# White Space 3
		re10='((?:[a-z][a-z\-]+))'	# Word 4

		regToTest = re1+re2+re3+re4+re5+re6+re7+re8+re9+re10
		rg = re.compile(regToTest,re.IGNORECASE|re.DOTALL)
		m = rg.search(nameLine)
		if m:
			word1=m.group(1)
			c1=m.group(2)
			ws1=m.group(3)
			word2=m.group(4)
			word4 = ""
			if m.group(6) :
				word4 = m.group(6)
			if m.group(7) :
				word4 += m.group(7)				
			c2=m.group(8)
			ws2=m.group(9)
			word3=m.group(10)
			return [word1, word2, word3, word4]
			
		return []


	####################################################################
	# parsePhone
	####################################################################
	def parsePhone(self, phoneLine) :


		re1='(\\()'	# Any Single Character 1
		re2='(\\d+)'	# Integer Number 1
		re3='(\\))'	# Any Single Character 2
		re4='(\\s+)'	# White Space 1
		re5='(\\d+)'	# Integer Number 2
		re6='(-)'	# Any Single Character 3
		re7='(\\d+)'	# Integer Number 3

		rg = re.compile(re1+re2+re3+re4+re5+re6+re7,re.IGNORECASE|re.DOTALL)
		m = rg.search(phoneLine)
		if m:
			return True

		return False
		
	######################################
	# runAction
	######################################
	def runAction(self, options) :

		self.parsedOptions = None	
		(self.parsedOptions, self.remaining) = self.options.parse_args(list(options))

		fileName = self.parsedOptions.providerFile
		if fileName :
			providerFile = open(fileName, "r")
		else :
			parser.error('You must provide a path to a providerFile. Use -f to provide a path. Use --help for assistance.')
			return


		nickname = self.parsedOptions.nickname
		if not nickname :
			parser.error('You must provide an insurance company nickname (e.g. aetna). Use -n to provide a nickname. Use --help for assistance.')
			return



		dryrun = self.parsedOptions.dryrun


		providerLines = providerFile.readlines()

		providerDict = {}
		providerID = None
		count = 0

		for i, providerLine in enumerate(providerLines) : 

			providerLine = providerLine.replace("\r\n", "")

			# If we've encountered a new provider in the file, 
			# and we have data for a previous provider,
			# save the data we accumulated for the previous provider
			#
			#
			if CONSTANTS.PROVIDER_TRIGGER in providerLine :

				if "providerID" in providerDict :

					count += 1
					providerDict["insurancecompany"] = nickname
					
					print "PROVIDER %s: %s"%(count, providerDict)

					if not dryrun :

						providers.save(providerDict)

					providerDict = {}

				# Move on with the new provider
				#
				providerID = providerLine.split(":")[1].strip()
				providerDict["providerID"] = providerID


			elif self.parsePhone(providerLine) :
			
				providerDict["phone"] = providerLine.rstrip()


			elif providerLine.upper() == providerLine :

				if "group" in providerDict :
					providerDict["group"] = " - ".join([providerDict["group"], providerLine])
				else :
					providerDict["group"] = providerLine

			elif self.parseName(providerLine) :

				nameArray = self.parseName(providerLine)

				providerDict["lastname"] = nameArray[0]
				providerDict["firstname"] = nameArray[1]
				providerDict["title"] = nameArray[2]
				providerDict["middlename"] = nameArray[3]


			elif providerLine in CONSTANTS.KNOWN_PRACTICES :

				providerDict["type"] = providerLine

			else :

				if "address1" in providerDict :
					if "address2" in providerDict :
						if "address3" in providerDict :
							providerDict["address4"] = providerLine
						else :
							providerDict["address3"] = providerLine
					else :
						providerDict["address2"] = providerLine
				else :
					providerDict["address1"] = providerLine


		providerFile.close()


######################################
# Main action
######################################

if __name__ == '__main__':

	options = sys.argv
	workingObj = PCPReader()
	status = workingObj.runAction(options)		
 	sys.exit(status)

