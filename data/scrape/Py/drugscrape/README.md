## Scripts to scrape Drugs and associated Diseases/Conditions

Drugs, Associated Conditions were scraped from following sources:
* [www.centerwatch.com](http://www.centerwatch.com/drug-information/fda-approved-drugs/medical-conditions/)
* [www.drugs.com](https://www.drugs.com/medical_conditions.html)

Data from Drugs.com was more comprehensive and included additional information related to impact of drug on Pregnancy, Controlled Substance Abuse Rating/Code, Alcohol impact etc. These additional data elements can eventually be used to enhance Plan Search and provides additional features that can be used for LETOR or other Learning Algorithms. Finally we used data from Drugs.com, which looks like this:

```json
[
{"brandnames": "Generic Name: bethanechol (beth-AN-ih-kole)\nBrand Name: Urecholine", "drug_name": "bethanechol", "alcohol": "", "csasched": "N", "rating": "9.0", "rxtype": "Rx", "popularityscore": "83", "drug_generalinfo": "Bethanechol is a cholinergic agent. It works by stimulating the bladder to contract, which improves urine flow. ", "condition": "Abdominal bloating (Abdominal Distension)", "pregnancy": "C"},
{"brandnames": "Generic Name: bethanechol (beth-AN-ih-kole)\nBrand Name: Urecholine", "drug_name": "Urecholine", "alcohol": "", "csasched": "N", "rating": "9.0", "rxtype": "Rx", "popularityscore": "58", "drug_generalinfo": "Urecholine is a cholinergic agent. It works by stimulating the bladder to contract, which improves urine flow. ", "condition": "Abdominal bloating (Abdominal Distension)", "pregnancy": "C"},
{"brandnames": "Duvoid, Urecholine", "drug_name": "Duvoid", "alcohol": "", "csasched": "N", "rating": 0, "rxtype": "Rx", "popularityscore": "18", "drug_generalinfo": "Bethanechol is used to treat urinary retention (difficulty urinating), which may occur after surgery, after delivering a baby, and in other situations. Bethanechol may also be used for purposes other than those listed in this medication guide. ", "condition": "Abdominal bloating (Abdominal Distension)", "pregnancy": "C"},
{"brandnames": "Aqua-Ban, Diurex Aquagels, Diurex Water Capsules", "drug_name": "Aqua-Ban", "alcohol": "", "csasched": "N", "rating": 0, "rxtype": "OTC", "popularityscore": "8", "drug_generalinfo": "Pamabrom is used to treat bloating, swelling, feelings of fullness, and other signs of water weight gain related to menstrual symptoms. Pamabrom may also be used for purposes not listed in this medication guide. ", "condition": "Abdominal bloating (Abdominal Distension)", "pregnancy": "N"}
]
```

#### Mapping RxNorms to Disease Conditions
Once the Drugs and their associated conditions were obtained, it was necessary to map these to [RxNorms](https://www.nlm.nih.gov/research/umls/rxnorm/overview.html) (which is a normalized naming system for generic and branded drugs), covered by each of the Insurance Plans from our main data source - the [CMS.gov Healthcare MarketPlace Data Sets]("https://www.cms.gov/CCIIO/Resources/Data-Resources/marketplace-puf.html).  

The National Library of Medicine (NLM), which produces RxNorms, provided a full [static set of RxNorms](https://www.nlm.nih.gov/research/umls/rxnorm/docs/rxnormfiles.html) along with sql scripts required to injest data into a MySql database.

###### To map RxNorms to Diseases
1. Injest RxNorm data into a local MySql Instance
2. Injest Drugs and Diseases data into local MySql Instance
3. Using Sql : map RxNormId + DrugName => DrugName + Disease

The mapping was very simple using like %% statement in Sql and a relatively good mapping was possible for a good number of Drugs. The Mapped data was then extracted as a Json file for easy ingestion into ElasticSearch/MongoDb for consumption later on.

Finally, using the mapping data and some additional data munging with Python and Sql, the following data views can be generated (json example):

Mapping RxNormId to List of Diseases

```json
"197319": {
        "diseaselist": [
            "Bladder calculi (Urinary Tract Stones)",
            "Bladder Stones (Urinary Tract Stones)",
            "Calcium Oxalate Calculi with Hyperuricosuria",
            "Cardiothoracic Surgery",
            "Heart Failure (Congestive Heart Failure)",
            "High Risk Percutaneous Transluminal Angioplasty",
            "Hyperuricemia Secondary to Chemotherapy",
            "Hypomania (Mania)",
            "Leishmaniasis",
            "Mania",
            "Manic Disorder (Mania)",
            "Reactive Perforating Collangenosis",
            "Renal calculi (Urinary Tract Stones)",
            "Renal Tract Stones (Urinary Tract Stones)",
            "Stones, bladder (Urinary Tract Stones)",
            "Urinary Tract Stones"
        ]
    }
```

Mapping Disease to List of RxNormIds (of Drugs associated with that disease)

```json
[{
	"Schilling Test": {
		"rxnormlist": ["1041787", "105686", "1087414", "1114859", "11248", "1164624", "1166102", "1166103", "1173109", "1173730", "1174431", "1179809", "1179810", "1235389", "1241896", "1244146", "1245012", "1245015", "1246063", "1248737", "1291288", "1298224", "1364854", "1364855", "1368908", "1423423", "1442252", "1486245", "1488563", "1606305", "1653780", "1726629", "198891", "199184", "199240", "199364", "199365", "199374", "200353", "211965", "215510", "236302", "237776", "237777", "237779", "240516", "242347", "242698", "244190", "245557", "245558", "253083", "259086", "259191", "259711", "262128", "309593", "309594", "309595", "309604", "309606", "309611", "313896", "314982", "316066", "317106", "351527", "351528", "352547", "352577", "359541", "359542", "372434", "476628", "484925", "5514", "636371", "636528", "636840", "644787", "687707", "700495", "700496", "700497", "700498", "700499", "730920", "748672", "763597", "794976", "800518", "808513", "808611", "808900", "830162", "830736", "835519", "836268", "855213", "861113", "861115", "884828", "884829", "891444", "896789", "978676", "999799"]
	},
	"Pathological Hypersecretory Disorder": {
		"rxnormlist": ["1007120", "1091243", "1115795", "1119558", "1157497", "1157498", "1157503", "1157504", "1157505", "1177438", "1177439", "1186752", "1186753", "1245029", "1245030", "1305807", "1370013", "1599653", "1599654", "1599655", "1599656", "1599657", "1599658", "1599659", "1599660", "198740", "198741", "210958", "210961", "252430", "259240", "282777", "311429", "311430", "311431", "317120", "329951", "329952", "332147", "332148", "332149", "332150", "332539", "332540", "333112", "333691", "333962", "334409", "336085", "336438", "366421", "367832", "372691", "372692", "375149", "375150", "411877", "438220", "441106", "485703", "571434", "571437", "6582", "723737", "723738", "723739", "802785", "93204", "94474"]
	},
  "Hepatic Tumor": {
		"rxnormlist": ["1159691", "1159692", "1182862", "1182863", "495881", "597745", "597746", "597747", "615977", "615978", "615979", "619985"]
	}
}]
```

**Note**: Summary descriptions are provided as comments inside each script and contains additional details.
