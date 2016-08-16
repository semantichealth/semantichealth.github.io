import boto3
import dateinfer
import ijson
import os
import psycopg2
import time
import argparse
import pymongo

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


# get a connection to MongoDB
def connect_mongodb():
    try:
        mongodb_conn = pymongo.MongoClient('172-31-29-150', 27017)
        return mongodb_conn
    except pymongo.errors.ConnectionFailure as e:
        print "Unable to connect to MongoDB instance\n{0}\n".format(str(e))


# utility function to test if a string is a valid floating point number
def ensure_is_float(s):
    if type(s) == str:
        if 'Decimal' in s:
            pass
    try:
        t = float(s)
        return t
    except ValueError:
        return 0.0


# prepare the JSON documents for loading into mongodb
def process_formulary_into_mongo(fname, db, conn):
    status = False
    count = 0
    with open(fname, 'r') as infile:
        try:
            for doc in ijson.items(infile, "item"):
                count += 1
#                db.drugs.save(doc)
            status = True
        except (KeyboardInterrupt, SystemExit):
            conn.rollback()
            raise
        except (UnicodeDecodeError, ValueError, ijson.JSONError) as ex:
            print "{0}\n".format(str(ex))
            print
    print "Saved {0} drug documents"
    return status


# prepare the JSON documents for loading into mongodb
def process_plan_into_mongo(fname, db, conn):
    status = False
    count = 0
    with open(fname, 'r') as infile:
        try:
            for doc in ijson.items(infile, "item"):
                # not everyone adheres to the ISO date requirement
                if 'last_updated_on' in doc:
                    inferred_date_format = dateinfer.infer([doc['last_updated_on']])
                    _date = time.strptime(doc['last_updated_on'], inferred_date_format)
                    doc['last_updated_on'] = time.strftime('%Y-%m-%d', _date)

                # first of all make sure that the coinsurance rate is a number and not a string
                # second of all check to see if it is a Decimal and convert it to a float if it is.
                if 'formulary' in doc:
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
                    else:
                        if 'cost_sharing' in doc['formulary'].keys():
                            if type(doc['formulary']['cost_sharing']) != list:
                                if doc['formulary']['cost_sharing']['coinsurance_rate']:
                                    doc['formulary']['cost_sharing']['coinsurance_rate'] = \
                                        ensure_is_float(doc['formulary']['cost_sharing']['coinsurance_rate'])
                                if doc['formulary']['cost_sharing']['copay_amount']:
                                    doc['formulary']['cost_sharing']['copay_amount'] = \
                                        ensure_is_float(doc['formulary']['cost_sharing']['copay_amount'])
                            else:
                                for cost_share in doc['formulary']['cost_sharing']:
                                    if 'coinsurance_rate' in cost_share:
                                        cost_share['coinsurance_rate'] = ensure_is_float(cost_share['coinsurance_rate'])
                                    if 'copay_amount' in cost_share:
                                        cost_share['copay_amount'] = ensure_is_float(cost_share['copay_amount'])
                # db.plans.save(doc)
                count += 1
            status = True
            print "Wrote {0} plan docs".format(count)
        except (KeyboardInterrupt, SystemExit):
            conn.rollback()
            raise
        except (UnicodeDecodeError, ValueError, ijson.JSONError) as ex:
            print "{0}\n".format(str(ex))
        except Exception as ex:
            print "{0}\n".format(str(ex))
    return status


# prepare the JSON documents for loading into mongodb
def process_provider_into_mongo(fname, db, conn):
    status = False
    with open(fname, 'r') as infile:
        try:
            for doc in ijson.items(infile, "item"):
                if doc['type'] == 'INDIVIDUAL':
                    db.providers.save(doc)
                else:
                    db.facilities.save(doc)
            status = True
        except (KeyboardInterrupt, SystemExit):
            conn.rollback()
            raise
        except (UnicodeDecodeError, ValueError, ijson.JSONError) as ex:
            print "{0}\n".format(str(ex))
    return status

do_drugs = args.drugs
do_plans = args.plans
do_providers = args.providers

db_conn = connect_db()
cur = db_conn.cursor()

mongo = connect_mongodb()
# mongo_db = mongo.data


if do_drugs:
    # Get the formulary documents
    count = 0
    cur.execute("SELECT id,s3key FROM jsonurls WHERE mongodb_upload is FALSE AND type=3 AND s3key is not null")
    for idx, key in cur.fetchall():
#        fname = xfer_from_s3('json/' + key, 'w210')
        fname='tmp.json'
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
    for idx, key in cur.fetchall():
        fname = 'tmp.json'
#        fname = xfer_from_s3('json/' + key, 'w210')
        if process_plan_into_mongo(fname, mongo.plans, db_conn):
            pass
#            update_cursor = db_conn.cursor()
#            update_cursor.execute("UPDATE jsonurls SET mongodb_upload=TRUE WHERE id=%(id)s", {'id': idx})
#            db_conn.commit()
#            update_cursor.close()
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
