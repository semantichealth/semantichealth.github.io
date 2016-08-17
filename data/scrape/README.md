# Scrape (Drugs data, Geocodes & Provider Ratings)

Some form of Website scraping and or REST API calls were employed during the project for a number of reasons:

* Drugs and associated Diseases/Conditions
* Geo-coding on over a million provider addresses
* Provider ratings (Yelp, HealthGrades, Vitals , UcompareHealthcare)

Scripts were written so that they could run on a number of VMs to parallelize some of the load. For eg., in some cases like GeoCoding, the source data - consisting of millions of (including duplicate) provider address data extracted from MongoDb, were pushed over to the VMs. For the most part, the scripts are self contained.

## Drugs and associated Diseases/Conditions

Includes scripts for scraping from [Centerwatch](http://www.centerwatch.com/drug-information/fda-approved-drugs/medical-conditions/) and [Drugs.com](https://www.drugs.com/medical_conditions.html). Also additional scripts required manipulate scraped data for easy ingestion into ElasticSearch/MongoDb for consumption later on.

## Geo-coding on over a million provider addresses

* Includes scripts to - pull geocodes from three different sources:
 * [SamartyStreets](https://smartystreets.com/docs/us-street-api#http-request-url) - Special
 * [geocder.google](http://geocoder.readthedocs.io/)
 * [geopy Nominatim](https://github.com/geopy/geopy)  


* Push scraped geocodes to MongoDB

* Lookup provider name and associated Geo codes for a given Plan (used for Providers Nearby feature)


## Provider ratings
[Yelp](http://www.yelp.com), [HealthGrades](http://www.healthgrades.com), [Vitals](http://www.vitals.com) , [UcompareHealthcare](http://www.ucomparehealthcare.com)

Code for scraping Provider Ratings were forked from [PCPInvestigator - by Tory Hoke](https://github.com/AteYourLembas/PCPInvestigator). Changes were made to three of the scrapers to accommodate new changes to the respective rating websites. Addtional code changes generating scraped results in Json files for ingestion to MongoDb/Elastic Search.

Although the code is functional and tested, it has one major limitation with running on a large set of providers - the code uses Google to do a search and then scrapes the search results for any mention in one of the rating sites and then crawls the specific rating websites. Even with randomizing request headers and timing between request, search results returned 403 errors, mostly from Google blocking IP calls. So we were not able to use Provider ratings. The code still captures the scrape elements and is usable for smaller data sets.
