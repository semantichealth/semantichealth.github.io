from bottle import route, run, template, debug, request, post, static_file
from collections import defaultdict
import pymongo
import PCPConstants as CONSTANTS
import PCPDistanceCalculator




@route('/PCPReport/')
def index():
    
     connection = pymongo.MongoClient(CONSTANTS.DB_HOST, CONSTANTS.DB_PORT)

	db = connection.test # attach to test db

	providers = db.providers # get handle for words
	count = db.command({ "count":'providers'})["n"]
	allProviders = providers.find()

	homeState = CONSTANTS.YOUR_HOME_STATE
	distances=defaultdict(str)
	for i in range(0, int(count) ) :

		zipline = allProviders[i]["address1"]
		if homeState not in zipline :
			zipline = allProviders[i]["address2"]
			if homeState not in zipline :
				zipline = allProviders[i]["address3"]
				if homeState not in zipline :
					zipline = allProviders[i]["address4"]

		if homeState not in zipline :
			print "No zip code line found (trying to match on state %s)"%homeState
			distances[i] = "Unknown"
			continue

		awayZip = None
		ziplineterms = zipline.split(" ")
		for term in ziplineterms :
			if len(term) == 5 and term.isdigit() :
				awayZip = term

		if not awayZip :
			print "No away zip code found"
			distances[i] = "Unknown"
			continue

		distances[i] = PCPDistanceCalculator.getDistance(CONSTANTS.YOUR_ZIP_CODE, awayZip)


	return template('PCPReport.tpl', {'providers':allProviders, "distances": distances })




@route('/PCPDetails/')
def PCPDetails():

	connection = Connection(CONSTANTS.DB_HOST, CONSTANTS.DB_PORT) # default port for mongo
	db = connection.test # attach to test db
	providers = db.providers # get handle for providers

	providerID = request.GET.get("providerID", "")

	currProvider = providers.find_one({"providerID": providerID})

	return template("PCPDetails.tpl", {"provider":currProvider})


# Static file handling

@route('/static/js/<javascript>')
def javascripts(javascript) :
	return static_file(javascript, root='./static/js')

@route('/static/css/<css>')
def stylesheets(css) :
	return static_file(css, root='./static/css')



debug(True)
run(host='localhost', port=8080)