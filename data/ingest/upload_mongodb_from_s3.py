from ijson.backends import yajl2
from ijson import common, JSONError
from itertools import imap
import boto3
import dateinfer
import os
import psycopg2
import time
import argparse
import pymongo
from pymongo.errors import ConnectionFailure

arg_parser = argparse.ArgumentParser(description='Process JSON CMS PUF data')
arg_parser.add_argument('--drugs', dest='drugs', action='store_true', default=False)
arg_parser.add_argument('--plans', dest='plans', action='store_true', default=False)
arg_parser.add_argument('--providers', dest='providers', action='store_true', default=False)
arg_parser.add_argument('--mongo', dest='mongohost', default='127.0.0.1')

args = arg_parser.parse_args()


# download from S3 bucket into local temp file
def xfer_from_s3(key, bucket):
    print "Starting to download {0}...".format(key)
    filename = 'tmp.json'
    # remove the temp file if it exists
    try:
        os.remove(filename)
    except OSError:
        pass
    s3 = boto3.client('s3')
    response = s3.download_file(bucket, key, filename)
    print "Download of {0} complete\n".format(key)
    return filename


# get a connection to the database
def connect_db():
    conn = psycopg2.connect(user="acaproject",
                            database="acaproject",
                            password="test1234",
                            host="w210.cxihwctrc5di.us-west-1.rds.amazonaws.com",
                            port="5432")
    return conn


# get a connection to MongoDB
def connect_mongodb(host):
    try:
        mongodb_conn = pymongo.MongoClient(host, 27017)
        return mongodb_conn
    except ConnectionFailure as e:
        print "Unable to connect to MongoDB instance\n{0}\n".format(str(e))


# utility function to test if a string is a valid floating point number
def ensure_is_float(s):
    if s is None:
        return 0.0
    try:
        t = float(s)
        return t
    except ValueError:
        return 0.0


# override ijson Decimal implementation for numeric values to use float
def floaten(event):
    if event[1] == 'number':
        return (event[0], event[1], float(event[2]))
    else:
        return event


# prepare the JSON documents for loading into mongodb
def process_formulary_into_mongo(fname, db, conn):
    status = False
    count = 0
    with open(fname, 'r') as infile:
        event = imap(floaten, yajl2.parse(infile))
        data = common.items(event, 'item')
        try:
            for doc in data:
                db.drugs.save(doc)
                count += 1
            status = True
            print "Wrote {0} drug docs to MongoDB\n".format(count)
        except (KeyboardInterrupt, SystemExit):
            conn.rollback()
            raise
        except (UnicodeDecodeError, ValueError, JSONError) as ex:
            print "{0}\n".format(str(ex))
            print
    return status


# prepare the JSON documents for loading into mongodb
def process_plan_into_mongo(fname, db, conn):
    status = False
    count = 0
    with open(fname, 'r') as infile:
        # use the float override for ijson parser to prevent Decimal values
        event = imap(floaten, yajl2.parse(infile))
        data = common.items(event, 'item')
        try:
            for doc in data:
                # not everyone adheres to the ISO date requirement
                if 'last_updated_on' in doc:
                    inferred_date_format = dateinfer.infer([doc['last_updated_on']])
                    _date = time.strptime(doc['last_updated_on'], inferred_date_format)
                    doc['last_updated_on'] = time.strftime('%Y-%m-%d', _date)

                # first of all make sure that the coinsurance rate is a number and not a string
                # second of all check to see if it is a Decimal and convert it to a float if it is.
                if 'formulary' in doc:
                    if type(doc['formulary']) == dict:
                        formulary = []
                        formulary.append(doc['formulary'])
                        doc['formulary']=formulary

                    if type(doc['formulary']) == list:
                        for f in doc['formulary']:
                            if 'cost_sharing' in f:
                                if type(f['cost_sharing']) != list:
                                    if f['cost_sharing']['coinsurance_rate']:
                                        if f['cost_sharing']['coinsurance_rate']:
                                            f['cost_sharing']['coinsurance_rate'] = \
                                                ensure_is_float(f['cost_sharing']['coinsurance_rate'])
                                        if f['cost_sharing']['copay_amount']:
                                            f['cost_sharing']['copay_amount'] = \
                                                ensure_is_float(f['cost_sharing']['copay_amount'])
                                else:
                                    for item in f['cost_sharing']:
                                        if 'coinsurance_rate' in item:
                                            item['coinsurance_rate'] = ensure_is_float(item['coinsurance_rate'])
                                        if 'copay_amount' in item:
                                            item['copay_amount'] = ensure_is_float(item['copay_amount'])



                db.plans.save(doc)
                count += 1
            status = True
            print "Wrote {0} plan docs to mongodb\n".format(count)
        except (KeyboardInterrupt, SystemExit):
            conn.rollback()
            raise
        except (UnicodeDecodeError, ValueError, JSONError) as ex:
            print "{0}\n".format(str(ex))
        except Exception as ex:
            print "{0}\n".format(str(ex))
    return status


# prepare the JSON documents for loading into mongodb
def process_provider_into_mongo(fname, db, conn):
    provider_count = 0
    facilities_count = 0
    status = False
    with open(fname, 'r') as infile:
        event = imap(floaten, yajl2.parse(infile))
        data = common.items(event, 'item')
        try:
            for doc in data:
                if doc['type'] == 'INDIVIDUAL':
                    db.providers.save(doc)
                    provider_count += 1
                else:
                    db.facilities.save(doc)
                    facilities_count += 1
            status = True
        except (KeyboardInterrupt, SystemExit):
            conn.rollback()
            raise
        except (UnicodeDecodeError, ValueError, JSONError) as ex:
            print "{0}\n".format(str(ex))
    if (provider_count > 0):
        print "Wrote {0} provider documents to MongoDB\n".format(provider_count)
    if (facilities_count > 0):
        print "Wrote {0} provider documents to MongoDB\n".format(facilities_count)
    return status

do_drugs = args.drugs
do_plans = args.plans
do_providers = args.providers

db_conn = connect_db()
cur = db_conn.cursor()

mongo = connect_mongodb(args.mongohost)

# mongo_db = mongo.data


if do_drugs:
    # Get the formulary documents
    count = 0
    cur.execute("SELECT id,s3key FROM jsonurls WHERE mongodb_upload is FALSE AND type=3 AND s3key is not null")
    for idx, key in cur.fetchall():
        fname = xfer_from_s3('json/' + key, 'w210')
        if process_formulary_into_mongo(fname, mongo.formularies, db_conn):
            update_cursor = db_conn.cursor()
            update_cursor.execute("UPDATE jsonurls SET mongodb_upload=TRUE WHERE id=%(id)s", {'id': idx})
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
    cur.execute("SELECT id,s3key FROM jsonurls WHERE mongodb_upload is FALSE AND type=2 AND s3key is not null")
#    cur.execute("SELECT id,s3key FROM jsonurls WHERE type=2 AND s3key is not null")
    for idx, key in cur.fetchall():
        fname = xfer_from_s3('json/' + key, 'w210')
        if process_plan_into_mongo(fname, mongo.plans, db_conn):
            update_cursor = db_conn.cursor()
            update_cursor.execute("UPDATE jsonurls SET mongodb_upload=TRUE WHERE id=%(id)s", {'id': idx})
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
    cur.execute("SELECT id,s3key FROM jsonurls WHERE mongodb_upload is FALSE AND type=1 AND s3key is not null")
    for idx, key in cur.fetchall():
        fname = xfer_from_s3('json/' + key, 'w210')
        if process_provider_into_mongo(fname, mongo.providers, db_conn):
            update_cursor = db_conn.cursor()
            update_cursor.execute("UPDATE jsonurls SET mongodb_upload=TRUE WHERE id=%(id)s", {'id': idx})
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
