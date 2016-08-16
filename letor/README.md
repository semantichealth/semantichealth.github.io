# Learn to Rank (LETOR) for Obamacare Plan

###Components
- **Feature extraction:** data preprocessing to extract feature from MongoDB
- **Offline training:** train LETOR model based on user click through data, using extracted features
- **Online prediction:** called by ElasticSearch to incorporate LETOR ranking with local search results

###Data Flow
![alt tag](https://github.com/leiyang-mids/aca_letor/blob/master/ACA%20LETOR%20Data%20Flow.jpg)

###Use Cases
![alt tag](https://github.com/semantichealth/semantichealth.github.io/blob/master/letor/doc/example1.jpg)
![alt tag](https://github.com/semantichealth/semantichealth.github.io/blob/master/letor/doc/example2.jpg)
![alt tag](https://github.com/semantichealth/semantichealth.github.io/blob/master/letor/doc/example3.jpg)
