# Scrape (Drugs data, Geocodes & Provider Ratings)

Besides the main data source used for the SemanticHealth project, from [CMS.gov Healthcare MarketPlace Data Sets]("https://www.cms.gov/CCIIO/Resources/Data-Resources/marketplace-puf.html), we collected additional external data sets enhance the semantic search capability and thus improving user experience.

Three of the external data sets we focused on were:
* **Drugs and associated Diseases/Conditions** - This will allow users to search for plans by specific disease or condition they have and also additionally used for auto-complete.
* **Geo-coding on over a million provider addresses** - This will allow users to look up Providers from a plan they selected that are near-by.
* **Provider ratings (Yelp, HealthGrades, Vitals , UcompareHealthcare)** - This data would help with enhancing Learning and Ranking based on existing provider ratings (Note: We were not able to fully collect Provider Ratings due to some technical limitations we ran into)

Most of the Scraping/Data Extraction scripts for the above were implemented as stand-alone Python scripts which were then executed on a number of VMs to parallelize some of the load, as needed. For eg., in some cases like extracting Geo Locations for millions of provider address(including duplicates), data was extracted from Provider Collection on our MongoDb Server, and pushed over to Virtual Machines (VMs) running on the IBM [SoftLayer](http://www.softlayer.com/) Cloud Platform.

Outlined below are high level overview of what's covered by the scripts.

### Drugs and associated Diseases/Conditions

Includes scripts for scraping Drugs data from [Centerwatch](http://www.centerwatch.com/drug-information/fda-approved-drugs/medical-conditions/) and [Drugs.com](https://www.drugs.com/medical_conditions.html). Additional scripts were required to manipulate scraped data for easy ingestion into ElasticSearch/MongoDb for consumption later on.

### Geo-coding on over a million provider addresses

* Includes scripts to - pull geocodes from three different sources:
 * [SamartyStreets](https://smartystreets.com/docs/us-street-api#http-request-url)
 * [geocder.google](http://geocoder.readthedocs.io/)
 * [geopy Nominatim](https://github.com/geopy/geopy)  

* Push scraped geocodes to MongoDB

* Lookup provider name and associated Geo codes for a given Plan (used for Providers Nearby feature)


### Provider ratings
[Yelp](http://www.yelp.com), [HealthGrades](http://www.healthgrades.com), [Vitals](http://www.vitals.com) , [UcompareHealthcare](http://www.ucomparehealthcare.com)

Code for scraping Provider Ratings were forked from [PCPInvestigator - by Tory Hoke](https://github.com/AteYourLembas/PCPInvestigator). Changes were made to three of the scrapers to accommodate new changes to the respective rating websites. Addtional code changes generating scraped results in Json files for ingestion to MongoDb/Elastic Search.

Although the code is functional and tested, it has one major limitation with running on a large set of providers - the code uses Google to do a search and then scrapes the search results for any mention in one of the rating sites and then crawls the specific rating websites. Even with randomizing request headers and timing between request, search results returned 403 errors, mostly from Google blocking IP calls. So we were not able to use Provider ratings. The code still captures the scrape elements and is usable for smaller data sets.
