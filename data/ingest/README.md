# Data Ingest

## Data Sources

Most of the data sources for Semantic Health are from the [CMS.gov Public Use Files](https://www.cms.gov/CCIIO/Resources/Data-Resources/marketplace-puf.html) and are the data dictionaries and Public Use Files available on that site. The PUF of primary interest is the [Machine Readable URL PUF](http://download.cms.gov/marketplace-puf/2016/machine-readable-url-puf.zip). The MRURL PUF contains a row for each state and insurance provider with the URL to a JSON file that points to the Plans, Providers and Formularies. This is the source of the physicians, addresses, plans for which they are in-network and accepting patients and more. The Formularies contain the drugs that are covered in the plans, and the Plan JSON files contain the plan attributes.

These files are updated every 30 days.

The basic hierarchy of the machine readable JSON files is shown in the following diagram:

![Machine Readable Files](json_data_structures.png "JSON File Hierarchy")

## Data Ingest

Data from the CMS.gov Machine Readable URL PUF is partially processed in the example code found in the iPython notebook `CMS_data_hack.ipynb`. This notebook has example code that reads a JSON file from the provided URL and then follows the pointers in the JSON to the Provider, Plan and Formulary JSON documents. These documents in turn are read and pushed into an Elasticsearch instance where every field is indexed.

The Machine Readable URL PUF contains approximately 36K URLs that must be followed to get all the data for all the states that participate in the national ACA exchange at Healthcare.gov.

## Data Issues

Inspection of the JSON data is reasonable enough - except that none of the JSON documents contain any of the metadata for state or other aspects. Since each row in the top level Machine Readable URL PUF corresponds to a state and an insuror for that state the state information is external to the JSON.

While the JSON documents are well structured, the data within them is not. For example, some insurors put all states in each of the Plans, Providers or Forumulary JSON despite the top level row being for a single state. Sometimes the JSON is separated into states but most of the time it is all together when this occurs. There is no consistent URL naming convention that helps prevent issues. For example, a JSON URL may be indicated for each state under the top level JSON, such as `Provider-AK.json, Provider-OR.json`. Most of the time this is not the case and the data is chunked by file size with states data across the chunks. While these cases are unusual they occurr frequently enough to make the data intake process tricky.

### JSON URL examples
An example of the JSON hierarchy goes something like this: *All information is fictional and for illustrative purposes only*

	|
	|- State AK, Insuror Moda, https://get-moda.com/json/cms.json
	|
	|---- Formulary : http://get-moda.com/json/formulary-AK.json, http://get-moda.com/json/formulary-OR.json
	|---- Provider  : http://get-moda.com/json/providers-AK.json, http://get-moda.com/json/providers-AK.json
	|---- Plans     : http://get-moda.com/json/plans-AK.json, http://get-moda.com/json/plans-OR.json
	|
	|- State OR, Insuror Moda, https://get-moda.com/json/cms.json
	|
	|---- Formulary : http://get-moda.com/json/formulary-AK.json, http://get-moda.com/json/formulary-OR.json
	|---- Provider  : http://get-moda.com/json/providers-AK.json, http://get-moda.com/json/providers-AK.json
	|---- Plans     : http://get-moda.com/json/plans-AK.json, http://get-moda.com/json/plans-OR.json
	|	
	|- State VA, Insuror MetLife, https://met-life.com/json/met-life.json
	|
	|---- Formulary : http://met-life.com/json/formulary1.json, http://met-life.com/json/formulary2.json
	|---- Providers : http://met-life.com/json/providers1.json, http://met-life.com/json/providers2.json
	|---- Plans     : http://met-life.com/json/plans.json


Here you see that Moda has two states, OR and AK, and for both states they provide the same set of files. In this case they name the JSON with the state as part of the URL, but that is rare.

The Met-Life example shows how multiple files can be used for the information in the one state, which may or may not contain information from other states. Most of the time they don't but there is no metadata that tells us this.

## Processing the Data

The iPython notebook `CMS_data_hack.ipynb` is a simple example for one or two states and one or two insurors for each state of how the data is processed into elasticsearch. The variability of the JSON content prevents trying to process very many of the JSON documents.

### Elasticsearch Index Structure

The first cut at an indexing structure is to separate each state into its own top level index. For example, an index for `ak`, `or`,`va`, etc. 

Each of these indexes have three document types: `plans`, `providers`, `formulary`. As the JSON for each insuror and state are pulled down the JSON for each of these is pushed to the index for that state, indicating the document type.

A query for a particular plan by name would look like:

	es.search(index="ak", body={"query": {"match": {'marketing_name':'Be Equipped'}}})

A query for a particular doctor by last name in Alaska might look like:

	es.search(index="ak", body={"query": {"match": {'provider_name':'* Smith'}}})

Since the plan data is available, plans can be searched by attribute and the results joined with doctors that participate in thost plans.

## Yelp API

Finally there is a bit of an experiment with third party rating data from sources such as Yelp. This being the first time I've used the Yelp API we experimented a bit with how to look up businesses and the number of ratings. I'll leave the documentation for the [Yelp API](https://www.yelp.com/developers/documentation/v2/overview) to Yelp.