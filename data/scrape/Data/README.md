# Scrape - Data
Data Files included here

### Data sourced from Drugs.com
* **csashed.json** - CSA (Constrolled Substance Abuse) ratings for drugs
* **pregnancycodes.json** - Drugs impact on Pregnancy
* **disease_byrxnorm.json** - ElasticSearch ingestable json file mapping  RxNormId (drug id) to list of associated Diseases/Conditions
* **rxnrom_bydisease.json** - Maps disease to list of all drugs (RxNormIds) associated to the disease
* **drugsdotcom folder** - Contains all data scraped from Drugs.com chunked alphabetically

### Sample Provider Ratings Extract
* **ProvidersAK_Ratings.json** - Sample output from Provider Ratings Scrape process
* **ProvidersVT_Ratings.json** - Sample output from Provider Ratings Scrape process
* **ProvidersOR_Ratings.json** - Sample output from Provider Ratings Scrape process
* **[S3 Link to Providers Address by State](http://tgw210acaprovidersbystate.s3.amazonaws.com/)** - This was used as input for scraping Ratings and Geo Locations

### Other Files
* **various .dat files** - intermediate data files used for testing and further refined into Jsons
