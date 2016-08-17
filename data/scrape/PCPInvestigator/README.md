This code is a tweaked version of Tory Hoke's PCPInvestigator
Tweaked for aca Semantic Health Proeject
- Scripts tested on Linux.
- Not all modules were used.
- Most changes made to PCPScraper and PCPSites
- PCPScraper and PCPSites scripts changed to reflect updates on Rating websites


Below is original Readme file.
---------------------------------------------------------------------------
       PCPInvestigator
       Copyright 2015 Tory Hoke

                 Program URI: http://github.com/AteYourLembas/PCPInvestigator
                 Description: Web scraper for aggregating reviews of health care providers. Scraping violates Google ToS. For educational purposes only.
                     Version: 0.2.0
                      Author: Tory Hoke
                  Author URI: http://www.toryhoke.com
                     License: GNU General Public License
                 License URI: http://www.opensource.org/licenses/gpl-license.php
                  Repository: https://github.com/AteYourLembas/PCPInvestigator



DESCRIPTION

This package includes

- PCPReader: parses text file of health care providers and adds results to mongodb collection (db.providers)
- PCPScraper: scrapes medical review websites (HealthGrades, UCompareHealthCare, Vitals, Yelp) for reviews of each health care provider
- PCPReport: launches a local report server for viewing the report via browser


INCLUDED IN THIS REPOSITORY

- jQuery 1.11.0
- jQuery TableSorter
 * TableSorter 2.0 - Client-side table sorting with ease!
 * Version 2.0.5b
 * @requires jQuery v1.2.3
 * 
 * Copyright (c) 2007 Christian Bach
 * Examples and docs at: http://tablesorter.com



DEPENDENCIES

 REQUIRED
 mongodb, Beautiful Soup, lxml
 * pymongo, jellyfish

	
> brew install mongodb

> pip install beautifulsoup4

> pip install lxml

(Installation may require sudo. Consider a virtual environment for maximum peace of mind.)



 OPTIONAL

If you want to be able to calculate distance between your zip and the health care provider's zip (for sorting), you will need a database of zip codes and longitude/latitude. If you don't care about distance calculation, you can skip this step.

- Download the mongoDB zipcodes data set from https://docs.mongodb.org/manual/tutorial/aggregation-zip-code-data-set/ (or search for "mongodb zip code database")
- From a command line, run

> mongoimport --db test --collection zips --file /your/download/location/zips.json



HOW TO USE

1) Prepare a text file of all the health care providers you'd like to search for. 

For example, you could

- Log in to your health insurance website
- Perform a search for "Primary Care Providers"
- Print the results to a PDF
- Open the PDF and copy-paste the contents into a text file
- Clean up any unwanted text


Expected sample format of entries in the file to be read

Provider ID #: 123456
PROSPECT HEALTHSOURCE
MEDGR, INC
Lastname, Firstname, MD
Internal Medicine
12345 West Washington Blvd.
Los Angeles, CA 90066
(310) 123-4567 


In this case, "Provider ID #" indicates the start of a new entry. Change the PROVIDER_TRIGGER constant in PCPConstants to reflect whatever indicates the start of a new entry in your text file.


If your text file isn't exactly in this format, PCPReader may still work. Try a dry run and check the output.
If the parsed information isn't correct, you may need to modify the order lines are stored in PCPReader.runAction(). Sorry!



2) Start mongod so this script can connect (keep it running in its own terminal tab)
> mongod


3) Change KNOWN_PRACTICES constant in PCPConstants to contain the list of practices expected in your text file (e.g. ["Family Practice", "General Practice", "Pediatrics", ... ]

4) Change any other constants in PCPConstants that you need to.


5) Use PCPReader to parse the text file and mark it with any group name you like. 

python PCPReader.py --help
Usage: PCPReader.py [options]

Options:
  -h, --help            show this help message and exit
  -f PROVIDERFILE, --providerFile=PROVIDERFILE
                        Full path to providerFile. See sample provider file
                        for desired format, or adjust format parser.
  -n NICKNAME, --nickname=NICKNAME
                        Insurance nickname, to be stored with each provider
                        (e.g. aetna, kaiser, bluecross)
  -d, --dryrun          Simulate and generate output for first five entries.
                        Do not add to database.


For example, to try a dry run of reading providers into the group "aetna_2015":

python PCPReader.py -n aetna_2015 -f /path/to/input/aetna_provider_01.txt -d


To actually perform the scrape and add reviews to the database:

python PCPReader.py -n aetna_2015 -f /path/to/input/aetna_provider_01.txt -d



6) To see your new records, start a mongo session in a new Terminal window and search:

> db.providers.find()


7) In case you have duplicate entries, use something like this on your final mongo db.
USE CAUTION AND MAKE BACKUPS in case this doesn't behave as you expect.

from the mongo prompt:

> db.providers.ensureIndex({lastname: 1, firstname: 1, middlename: 1, phone: 1}, {unique: true, dropDups:true})


8) Now that your database is populated, run the web scrape. It will search for results for providers in the database that have no "lastscraped" value. (Thus the ones you just added. If you ever want to re-scrape a provider, clear its "lastscraped" value.) 

Again, -d will launch a dry run: outputting results for the first five doctors without adding them to the database. This will let you see whether the scrape is working.

> python PCPScraper.py -d

To diagnose errors, use the tests in this package's "test" directory.

When you're ready for production, run the scraper without the dry run flag:

> python PCPScraper.py

Check the output once in a while to see if it's performing as you expect.




9) When scraping is finished, view the report by running

> python PCPReport.py



10) In PCPReport.py's output, verify where script is "Listening" (http://localhost:8080/) and open that address in your web browser to get to PCPDetails:

http://localhost:8080/PCPReport/


11) If you like, you can save this report as a static HTML file for offline reference. 



WARNINGS

- Web scraping violates Google ToS. Irresponsible use may result in your IP getting blocked.
- Pymongo cursor has no timeout (due to long intervals between scrapes.) Proceed w/ caution.




KNOWN ISSUES


- Health care review website formats change without notice.
- Searches by doctor name and so may suffer false positives (i.e. include reviews for other doctors of the same name) or false negatives (i.e. omit some available reviews)
- Disparities between your input file and the expected input format may require elbow grease to resolve.
- Script developed on OSX. Installation/execution not tested on any other system.




Hope this helps. Good luck, and enjoy!
