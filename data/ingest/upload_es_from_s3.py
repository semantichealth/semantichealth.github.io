from elasticsearch import Elasticsearch, helpers
from elasticsearch.client import IndicesClient
import boto3
import dateinfer
import ijson
import os
import psycopg2
import time
import argparse


arg_parser = argparse.ArgumentParser(description='Process JSON CMS PUF data')
arg_parser.add_argument('--drugs', dest='drugs', action='store_true', default=False)
arg_parser.add_argument('--plans', dest='plans', action='store_true', default=False)
arg_parser.add_argument('--providers', dest='providers', action='store_true', default=False)

args = arg_parser.parse_args()


# download from S3 bucket into local temp file
def xfer_from_s3(key, bucket):
    filename = 'tmp.json'
    # remove the temp file if it exists
    try:
        os.remove(filename)
    except OSError:
        pass
    s3 = boto3.client('s3')
    response = s3.download_file(bucket, key, filename)
    return filename


# get a connection to the database
def connect_db():
    conn = psycopg2.connect(user="acaproject",
                            database="acaproject",
                            password="test1234",
                            host="w210.cxihwctrc5di.us-west-1.rds.amazonaws.com",
                            port="5432")
    return conn


# utility function to test if a string is a valid floating point number
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


# prepare the JSON documents for bulk load into elasticsearch
def process_formulary_into_es(fname, es, conn):
    status = False
    with open(fname, 'r') as infile:
        actions = []
        try:
            for doc in ijson.items(infile, "item"):
                action = {
                    "_index": "data",
                    "_type": "drug",
                    "_source": doc
                }
                actions.append(action)
                if len(actions) > 0 and len(actions) % 50 == 0:
                    helpers.bulk(es, actions)
                    status = True
                    actions = []
        except (KeyboardInterrupt, SystemExit):
            conn.rollback()
            raise
        except (UnicodeDecodeError, ValueError, ijson.JSONError) as ex:
            print "{0}\n".format(str(ex))
            print
        return status


# prepare the JSON documents for bulk load into elasticsearch
def process_plan_into_es(fname, es, conn):
    status = False
    with open(fname, 'r') as infile:
        actions = []
        try:
            for doc in ijson.items(infile, "item"):
                # not everyone adheres to the ISO date requirement
                if 'last_updated_on' in doc:
                    inferred_date_format = dateinfer.infer([doc['last_updated_on']])
                    _date = time.strptime(doc['last_updated_on'], inferred_date_format)
                    doc['last_updated_on'] = time.strftime('%Y-%m-%d', _date)

                if 'formulary' in doc:
                    if type(doc['formulary']) == list:
                        for f in doc['formulary']:
                            if type(f) == unicode:
                                a = doc['formulary'].keys()
                                print doc
                                pass
                            if 'cost_sharing' in f:
                                if type(f['cost_sharing']) != list:
                                    if f['cost_sharing']['coinsurance_rate']:
                                        if f['cost_sharing']['coinsurance_rate']:
                                            if not is_number(f['cost_sharing']['coinsurance_rate']):
                                                f['cost_sharing']['coinsurance_rate'] = 0.0
                                else:
                                    for item in f['cost_sharing']:
                                        if item['coinsurance_rate']:
                                            if not is_number(item['coinsurance_rate']):
                                                item['coinsurance_rate'] = 0.0
                    else:
                        if 'cost_sharing' in doc['formulary'].keys():
                            if type(doc['formulary']['cost_sharing']) != list:
                                if doc['formulary']['cost_sharing']['coinsurance_rate']:
                                    if doc['formulary']['cost_sharing']['coinsurance_rate']:
                                        if not is_number(doc['formulary']['cost_sharing']['coinsurance_rate']):
                                            doc['formulary']['cost_sharing']['coinsurance_rate'] = 0
                            else:
                                for cost_share in doc['formulary']['cost_sharing']:
                                    if cost_share['coinsurance_rate']:
                                        if not is_number(cost_share['coinsurance_rate']):
                                            cost_share['coinsurance_rate'] = 0

                action = {
                    "_index": "data",
                    "_type": "plan",
                    "_source": doc
                }
                actions.append(action)
                if len(actions) > 0 and len(actions) % 10 == 0:
                    helpers.bulk(es, actions)
                    status = True
                    actions = []
        except (KeyboardInterrupt, SystemExit):
            conn.rollback()
            raise
        except (UnicodeDecodeError, ValueError, ijson.JSONError) as ex:
            print "{0}\n".format(str(ex))
        return status


# prepare the JSON documents for bulk load into elasticsearch
def process_provider_into_es(fname, es, conn):
    status = False
    with open(fname, 'r') as infile:
        actions = []
        try:
            for doc in ijson.items(infile, "item"):
                if doc['type'] == 'INDIVIDUAL':
                    action = {
                        "_index": "data",
                        "_type": "provider",
                        "_source": doc
                        }
                else:
                    action = {
                        "_index": "data",
                        "_type": "facility",
                        "_source": doc
                    }
                actions.append(action)
                if len(actions) > 0 and len(actions) % 50 == 0:
                    helpers.bulk(es, actions)
                    status = True
                    actions = []
        except (KeyboardInterrupt, SystemExit):
            conn.rollback()
            raise
        except (UnicodeDecodeError, ValueError, ijson.JSONError):
            print "{0}\n".format(str(ex))
    return status

# for debugging control
do_drugs = args.drugs
do_plans = args.plans
do_providers = args.providers

db_conn = connect_db()
cur = db_conn.cursor()

es = Elasticsearch("https://search-acaproject-yayvqakrnkdvdfd5m6kyqonp5a.us-west-1.es.amazonaws.com/")
ic = IndicesClient(es)

if do_drugs:
    # Get the formulary documents
    count = 0
    cur.execute("SELECT id,s3key FROM jsonurls WHERE es_index is FALSE AND type=3 AND s3key is not null")
    for idx, key in cur.fetchall():
        fname = xfer_from_s3('json/' + key, 'w210')
        if process_formulary_into_es(fname, es, db_conn):
            update_cursor = db_conn.cursor()
            update_cursor.execute("UPDATE jsonurls SET es_index=TRUE WHERE id=%(id)s", {'id': idx})
            db_conn.commit()
            update_cursor.close()
        else:
            print "---------------------------------------------------------------"
            print "Formulary ID {0} S3Key {1} failed to load".format(idx, key)
            print "---------------------------------------------------------------"
            count += 1
    print "{0} formularies failed to upload".format(count)

if do_plans:
    # Get the plan documents
    count = 0
    cur.execute("SELECT id,s3key FROM jsonurls WHERE es_index is FALSE AND type=2 AND s3key is not null")
    for idx, key in cur.fetchall():
        fname = xfer_from_s3('json/' + key, 'w210')
        if process_plan_into_es(fname, es, db_conn):
            update_cursor = db_conn.cursor()
            update_cursor.execute("UPDATE jsonurls SET es_index=TRUE WHERE id=%(id)s", {'id': idx})
            db_conn.commit()
            update_cursor.close()
        else:
            print "---------------------------------------------------------------"
            print "Plan ID {0} S3Key {1} failed to load".format(idx, key)
            print "---------------------------------------------------------------"
            count += 1
    print "{0} plans failed to upload".format(count)

if do_providers:
    # Get the provider and facility documents
    count = 0
    cur.execute("SELECT id,s3key FROM jsonurls WHERE es_index is FALSE AND type=1 AND s3key is not null")
    for idx, key in cur.fetchall():
        fname = xfer_from_s3('json/' + key, 'w210')
        if process_provider_into_es(fname, es, db_conn):
            update_cursor = db_conn.cursor()
            update_cursor.execute("UPDATE jsonurls SET es_index=TRUE WHERE id=%(id)s", {'id': idx})
            db_conn.commit()
            update_cursor.close()
        else:
            print "---------------------------------------------------------------"
            print "Provider ID {0} S3Key {1} failed to load".format(idx, key)
            print "---------------------------------------------------------------"
            count += 1
    print "{0} providers failed to upload".format(count)

# close all database connections
cur.close()
db_conn.close()
