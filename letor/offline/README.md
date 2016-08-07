# LETOR Training

### Strategy:
- a k-mean algorithm with cosine similarity is developed to classify queries from click-through data
- a threshold is specified by the user, _k_ will keep increasing until the mean similarity between queries within a cluster is above the threshold
- pair-wise feature from queries within a cluster will be combined to train a LETOR model
- SVM classifier is trained for each cluster to rank plans
- each cluster will have a recommended ranking for the plans
- pre-ranked weight will be indexed for each state in ElasticSearch server for online prediction

### File Description:
Name|Function
---|---
**main.py** | main procedure to execute training
**get_click_data.py** | retrieve and organize click-through data from PostgreSQL
**query_characterizer.py** | find the optimal clusters for query
**get_query_cluster.py** | run k-mean clustering on a group of queries
**get_rank_for_state_plan.py** | train SVM to build LETOR model for each query cluster
**train_one_state.py** | build LETOR models for one state
**s3_helpers.py** | retrieve feature data from S3, and upload training data to S3
**add_query.sql** | generate testing data for click-through database
**simulate_clicks.py** | generate testing data for plan ranking

### Deployment:
- system requirement: python 2.7 or after, sklearn, boto3, psycopg2, awscli
 - `sudo yum install postgresql-devel`
 - `sudo pip install psycopg2`

- set AWS credential for S3 access: `aws configure`
- set retry interval `hour` and `minute` in _main.py_
- execute main procedure on the backgroud: `python main.py &`
