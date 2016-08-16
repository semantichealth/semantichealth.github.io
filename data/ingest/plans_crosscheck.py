import pymongo
from pymongo.errors import ConnectionFailure
import psycopg2
import re
import argparse


"""

    This Python program does a check on the MongoDB plans in the Plan collection and checks
    the list against the plan identifiers in the PostgreSQL database. The MongoDB and PostgreSQL
    data come from different sources so this code is a test to see if plans are not in one that
    are in the other.

"""


arg_parser = argparse.ArgumentParser(description='Process aggregate plan data into elastic search')
arg_parser.add_argument('--mongo', dest='mongohost', default='ec2-52-53-173-200.us-west-1.compute.amazonaws.com')
arg_parser.add_argument('--pghost', dest='postgreshost', default='w210.cxihwctrc5di.us-west-1.rds.amazonaws.com')


args = arg_parser.parse_args()


# get a connection to the database
def connect_db(host):
    conn = psycopg2.connect(user="acaproject",
                            database="acaproject",
                            password="test1234",
                            host=host,
                            port="5432")
    return conn


def connect_mongodb(host):
    try:
        client = pymongo.MongoClient(host, 27017)
        return client
    except ConnectionFailure as e:
        print "Unable to connect to MongoDB instance\n{0}\n".format(str(e))


# Query MongoDB for a list of distinct plan ids
def find_all_plans(client):
    db = client.plans

    cursor = db.plans.distinct("plan_id")
    _plans = []
    for _plan in cursor:
        # combine first name and last name
        _plans.append(_plan)

    return _plans


def find_matching_plans(client, plan_id):
    db = client.plans

    cursor = db.plans.aggregate([{"$match": {"plan_id": plan_id}},
                                 {"$project": {"_id": 1}}])
    plans = []
    for plan in cursor:
        # combine first name and last name
        plans.append(plan)

    return plans


def find_providers_for_plan(client, plan_id):
    db = client.providers
    cursor = db.providers.aggregate([{"$match": {"plans.plan_id": plan_id}},
                                     {"$project": {"_id": 1}}])
    providers = []
    for provider in cursor:
        providers.append(provider)

    return providers


def find_drugs_for_plan(client, plan_id):
    db = client.formularies
    cursor = db.drugs.aggregate([{"$match": {"plans.plan_id": plan_id}},
                                 {"$project": {"_id": 1}}])
    drugs = []
    for drug in cursor:
        drugs.append(drug)

    return drugs

db_conn = connect_db(args.postgreshost)
cur = db_conn.cursor()

mongo_client = connect_mongodb(args.mongohost)

all_plans = find_all_plans(mongo_client)

# regular expression to pick off the number at the end of the Rating Area string
re_rating_area_number = re.compile(r'([0-9]+)$')

# all the states that are in the ACA data
all_states = ['PA', 'AZ', 'FL', 'LA', 'MT', 'NM', 'AK', 'NC', 'OR', 'MS', 'AR', 'MO', 'IL', 'IN', 'HI', 'WY', 'UT',
              'MI', 'KS', 'GA', 'WI', 'NE', 'OH', 'NV', 'OK', 'AL', 'ND', 'DE', 'WV', 'ME', 'TN', 'VA', 'SD', 'NH',
              'IA', 'SC', 'TX', 'NJ']

# states that we want to process
some_states = ['GA', 'AZ', 'FL', 'IA', 'TX']
#               'NM', 'NC', 'OR', 'MS', 'AR',
#               'MO', 'IL', 'IN', 'HI', 'WY',
#               'UT', 'NJ', 'MI', 'KS', 'GA',
#               'WI', 'NE', 'OH', 'NV', 'OK',
#               'AL', 'ND', 'DE', 'WV', 'ME',
#               'TN', 'VA', 'SD', 'NH', 'IA',
#               'TX', 'PA', 'AK']

for state in some_states:
    print "Processing {0}".format(state)

    parameters = {'statecode': state}

    print "Querying plan data for {0}".format(state)

    cur.execute('SELECT DISTINCT ON (pa.standardcomponentid) '
                'pa.standardcomponentid,'
                'pa.statecode '
                'FROM plan_attributes pa '
                'WHERE pa.statecode = %(statecode)s ',
                 parameters)

    plan_id = None

    actions = []
    es_doc = {}

    print "========================= {0} ===========================".format(state)

    for row in cur:
        plan_id = row[0]
        plans = find_matching_plans(mongo_client, plan_id)
        providers = find_providers_for_plan(mongo_client, plan_id)
        drugs = find_drugs_for_plan(mongo_client, plan_id)

        if len(plans) == 0:
            print "{0} missing from MongoDB Plans has {1} providers and {2} drugs".format(plan_id,
                                                                                          len(providers),
                                                                                          len(drugs))

    state_plans = [i for i in all_plans if state in i]
    for plan in state_plans:
        parameters = {'plan_id': plan}
        cur.execute('SELECT pa.standardcomponentid '
                    'FROM plan_attributes pa '
                    'WHERE pa.standardcomponentid=%(plan_id)s', parameters)
        if len(row) < 2:
            print "{0} found in MongoDB but missing from PostgreSQL".format(row[0])




