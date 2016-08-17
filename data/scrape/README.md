# Scrape (Drugs data, Geocodes & Provider Ratings) 

Some form of Website scraping and or REST API calls were employed during the project for a number of reasons:

* Drugs and assiociated Diseases/Conditions
* Geo-coding on over a million provider addresses
* Provider ratings (Yelp, HealthGrades, Vitals , UcompareHealthcare)

Scripts were written so that they could run on a number of VMs to parallelize some of the load. For eg., in some cases like GeoCoding, the source data - consisting of millions of (including duplicate) provider address data extracted from MongoDb, were pushed over to the VMs. For the most part, the scripts are self contained. 

## Drugs and assiociated Diseases/Conditions
	
Includes scripts for scraping from Centerwatch.com and Drugs.com. Also additional scripts required manipulate scraped data for easy ingestion into ElasticSearch/MongoDb for consumtion later on.

## Geo-coding on over a million provider addresses

* Includes scripts to - pull geocodes from three different sources:
..* [SamartyStreets](https://smartystreets.com/docs/us-street-api#http-request-url)
..* [geocder.google](http://geocoder.readthedocs.io/) and 
..* [geopy Nominatim](https://github.com/geopy/geopy) 

* Push scraped geocodes to MongoDB
* Lookup provider name and associated Geo codes for a given Plan (used for Providers Nearby feature)


## Provider ratings from ([Yelp](http://www.yelp.com), [HealthGrades](http://www.healthgrades.com), [Vitals]http://www.vitals.com) , [UcompareHealthcare](http://www.ucomparehealthcare.com))

Code for scraping Provider Ratings were forked from [PCPInvestigator - by Tory Hoke](https://github.com/AteYourLembas/PCPInvestigator). Changes were made to three of the scrapers to accomdate new changes to the respective rating websites. Addtional code changes generating scraped results in Json files for ingestion to MongoDb/Elastic Search.

Although the code is functional and tested, it has one major limitation with running on a large set of providers - the code uses google to do a search and then scrapes the search results for any mention in one of the rating sites and then crawls the specific rating websites. Even with randomizing request headers and timing between request, search results returned 403 errors, mostly from google blocking IP calls. So we were not able to use Provider ratings. The code still captures the scrape elemets and is usable for smaller data sets.

