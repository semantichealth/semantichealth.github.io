## Provider Ratings Scrape from Yelp, HealthGrades, UCompareHealthcare & Vitals

Code for scraping Provider Ratings were forked from [PCPInvestigator - by Tory Hoke](https://github.com/AteYourLembas/PCPInvestigator).

The PCPInvestigator supports scraping from four different Health Care Provider rating sites:
* [Yelp](http://www.yelp.com)
* [HealthGrades](http://www.healthgrades.com)
* [Vitals](http://www.vitals.com)
* [UcompareHealthcare](http://www.ucomparehealthcare.com)

For the SemanticHealth Project we made changes to scrapers to accommodate latest updates to respective rating websites. Additional code changes generating scraped results in Json files for ingestion to MongoDb/Elastic Search were also implemented.

Below are sample results (json) from scraping Provider ratings after incorporating our changes. As you can see, some of the providers don't have any hits from any of the rating sites and the ratings field is empty.

```json
[{"city": "portland", "zip": "97216", "firstname": "MICHAEL", "ratings": [{"path": "http://www.vitals.com/doctors/Dr_Michael_Bohley/reviews", "sourcetype": "vitals", "numreviews": 15, "overallscore": 0.9}], "middlename": "F", "lastname": "BOHLEY", "lastscraped": "2016-08-17 00:00:00", "state": "or", "prefix": "", "address": "10201 se main st  suite 20", "speciality": "PLASTIC SURGERY"}]
[{"city": "mcminnville", "zip": "97128", "firstname": "MARGARET", "ratings": [], "middlename": "JEAN", "lastname": "MILLER", "lastscraped": "2016-08-17 00:00:00", "state": "or", "prefix": "", "address": "2435 ne cumulus ave  suite a", "speciality": "PEDIATRICS"}]
[{"city": "salem", "zip": "97301", "firstname": "Julie", "ratings": [], "middlename": "Elizabeth", "lastname": "York", "lastscraped": "2016-08-17 00:00:00", "state": "or", "prefix": "Dr.", "address": "875 oak st se ste 5085", "speciality": "Neurologic Surgery"}]
[{"city": "corvallis", "zip": "97330", "firstname": "Kristy", "ratings": [{"path": "http://www.vitals.com/doctors/Dr_Kristy_JessopShankowski/reviews", "sourcetype": "vitals", "numreviews": 8, "overallscore": 0.7}], "middlename": "L", "lastname": "JessopShankowski", "lastscraped": "2016-08-17 00:00:00", "state": "or", "prefix": "", "address": "3521 nw samaritan dr ste 201", "speciality": "Internal Medicine"}]
[{"city": "klamath falls", "zip": "97601", "firstname": "Peter", "ratings": [{"path": "http://www.vitals.com/doctors/Dr_Peter_Lusich/reviews", "sourcetype": "vitals", "numreviews": 4, "overallscore": 0.6}], "middlename": "L", "lastname": "Lusich", "lastscraped": "2016-08-17 00:00:00", "state": "or", "prefix": "", "address": "2865 daggett ave", "speciality": "Anesthesiology"}]
[{"city": "kodiak", "zip": "99615", "firstname": "BRETT", "ratings": [{"path": "http://www.vitals.com/dentists/Dr_Brett_Bass/reviews", "sourcetype": "vitals", "numreviews": 0, "overallscore": 0.0}], "middlename": "A", "lastname": "BASS", "lastscraped": "2016-08-17 00:00:00", "state": "ak", "prefix": "", "address": "1317 mill bay rd", "speciality": "General Dentist"}]
[{"city": "anchorage", "zip": "99503", "firstname": "DONALD", "ratings": [], "middlename": "E", "lastname": "BURK", "lastscraped": "2016-08-17 00:00:00", "state": "ak", "prefix": "", "address": "2805 dawson st ste 1", "speciality": "General Dentist"}]
[{"city": "wasilla", "zip": "99654", "firstname": "STEPHEN", "ratings": [{"path": "http://www.vitals.com/dentists/Dr_Stephen_W_Christensen/reviews", "sourcetype": "vitals", "numreviews": 0, "overallscore": 0.0}], "middlename": "W", "lastname": "CHRISTENSEN", "lastscraped": "2016-08-17 00:00:00", "state": "ak", "prefix": "", "address": "1401 s seward meridian pkwy", "speciality": "General Dentist"}]
[{"city": "tok", "zip": "99780", "firstname": "SUSAN", "ratings": [{"path": "http://www.vitals.com/dentists/Dr_Susan_Y_Crawford/reviews", "sourcetype": "vitals", "numreviews": 2, "overallscore": 1.0}], "middlename": "", "lastname": "CRAWFORD", "lastscraped": "2016-08-17 00:00:00", "state": "ak", "prefix": "", "address": "no 1245 tok cutoff", "speciality": "General Dentist"}]
```
Here is a sample log from the Scrape process:

```
------------------------------------------------------------
*** SEARCHING for [u'Vered', '', u'Sobel', u'Dr.'] ***
------------------------------------------------------------
query Vered+Sobel+65 allen st+rutland+vt+05701+Ophthalmology+reviews
Address https://www.google.com/search?q=Vered%2BSobel%2B65+allen+st%2Brutland%2Bvt%2B05701%2BOphthalmology%2Breviews&num=20&hl=en&start=0
h3: http://www.vitals.com/doctors/Dr_Vered_Sobel.html
h3: http://www.vitals.com/doctors/Dr_Vered_Sobel/reviews
FOUND POTENTIAL SITES: ['vitals', 'vitals']
SCRAPING SITE vitals via http://www.vitals.com/doctors/Dr_Vered_Sobel.html...
http://www.vitals.com/doctors/Dr_Vered_Sobel/reviews
For vitals, comparing [u'vered', u'sobel'] to [u'vered', '', u'sobel']...
Match!
found a block of reqviews
 6 reviews found
--------------------------
vitals RESULTS: [0.7, '', 16]
--------------------------
--------------------------
--------------------------
*** SAVING results of ['vitals'] to Vered Sobel Dr. ***
*** DONE SAVING ***
```

Although the code is functional and tested, it has one major limitation with running on a large set of providers - the code uses Google to do a search and then scrapes the search results for any mention in one of the rating sites and then crawls the specific rating websites. Even with randomizing request headers and timing between request, search results returned 403 errors, mostly from Google blocking IP calls. So we were not able to use Provider ratings. The code still captures the scrape elements and is usable for smaller data sets.

Ratings from such public ratings sites are also not entirely accurate and we expect them to be even missing for large number of providers. That said as time permits this code can be further enhanced to overcome such limitations. Additional rating sites can be includes as they become available.
