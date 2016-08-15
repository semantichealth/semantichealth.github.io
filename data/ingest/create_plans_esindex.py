from elasticsearch import Elasticsearch, helpers
from elasticsearch.client import IndicesClient
from elasticsearch.exceptions import ConnectionTimeout
import pymongo
from pymongo.errors import ConnectionFailure
import psycopg2
import re
import argparse
import csv
import json


"""

    Create the elasticsearch plans index by building a plan document populated for each plan.
    The elasticsearch document id is set to the plan id.
    The mapping for the plan document is plan_mapping.json.
    Providers are queried from mongodb and built to contain only full name, NDI and address.
    The primary guide for which plans are inserted into the index is the plan_attributes table
    in the PostgreSQL database.
    A plans_index table is used to track what plans have been inserted into the index.

"""


arg_parser = argparse.ArgumentParser(description='Process aggregate plan data into elastic search')
arg_parser.add_argument('--mongo', dest='mongohost', default='ec2-52-53-173-200.us-west-1.compute.amazonaws.com')
arg_parser.add_argument('--pghost', dest='postgreshost', default='w210.cxihwctrc5di.us-west-1.rds.amazonaws.com')
arg_parser.add_argument('--eshost', dest='eshost',
                        default='http://169.45.104.82:9200/')

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


# custom drug name stop word filter
def filter_drug_names(drug_name):
    # stop_words = ['MG', 'TAB', 'SUB', 'CAP', 'GEL', 'OTIC', 'SOL', 'ER', 'OIN', 'CHW', 'VAL',
    #               'INJ', 'LOZ', 'MET', 'XR', 'OP', 'INH', 'DISKU', 'AER', 'SUSML', 'CLA', 'DRO',
    #               'DIS', 'POW', 'LOT', 'NEB', 'SYP', 'CRE', 'MAL', 'SD', 'ODT', 'CLAV', 'PAK']

    regex_list = [re.compile(r'\s[0-9.-]*\s*[MCG]+[/0-9]*', re.IGNORECASE),
                  re.compile(r'\s[0-9.-]*%'),
                  re.compile(r'\s[0-9.]*/[0-9]*'),
                  re.compile(r'\s[0-9]*UNIT', re.IGNORECASE),
                  re.compile(r'\s[0-9]*&'),
                  re.compile(r'\s[0-9.]*-[0-9.]*-[0-9.]*'),
                  re.compile(r'\s*[0-9.]*\s*')]

#    drug_name = ' '.join([word for word in drug_name.split() if word.upper() not in stop_words])

    # this one takes only the first word
    drug_name = drug_name.split()[0]

    for regex in regex_list:
        drug_name = regex.sub('', drug_name)

    return drug_name


#  query mongodb formulary db for all the drugs in the drug collection under this plan id.
def fetch_drugs_for_plan(client, _plan_id):
    db = client.formularies

    cursor = db.drugs.find({"plans.plan_id": _plan_id}, {"_id": 0, "drug_name": 1})
    drugs = []
    for drug in cursor:
        drug_name = filter_drug_names(drug['drug_name'])
        if drug_name not in drugs:
            drugs.append(drug_name)
    return drugs


# query mongodb provider db for all the providers in the provider collection under this plan id
# TODO: do same for facilities
def fetch_providers_for_plan(client, _plan_id):
    db = client.providers

    """
    cursor = db.providers.aggregate([{"$match": {"plans.plan_id": _plan_id}},
                                     {"$project": {"_id": 0, "npi": 1,
                                                   "provider_name": {"$concat": ["$name.first", " ", "$name.last"]},
                                                   "addresses": 1, "speciality": 1}}])

    cursor = db.providers.aggregate([{"$match": {"plans.plan_id": _plan_id}},
                                     {"$project": {"_id": 0, "provider_name":
                                         {"$concat": ["$name.first", " ", "$name.last"]}}}])
                                                   "addresses": 1, "speciality": 1}}])
    """
    cursor = db.providers.aggregate([{"$match": {"plans.plan_id": _plan_id}},
                                     {"$project": {"_id": 0, "npi": 1,
                                                   "provider_name": {"$concat": ["$name.first", " ", "$name.last"]},
                                                   "speciality": 1}}])
    _providers = []
    for provider in cursor:
        # combine first name and last name
        _providers.append(provider)

    return _providers


# TODO: implement
def fetch_conditions_for_plan(_plan_id):
    return _plan_id


def load_aggregated_premiums():
    d = {}
    with open('../konniam/elasticsearch-scripts/premiums_aggregated.csv', 'r') as f:
        rows = csv.DictReader(f)
        for r in rows:
            d[r['PlanId']] = r
    return d


def load_drugs_for_conditions():
    with open('rxnorm_bydisease.json', 'r') as f:
        d = json.load(f)
    return d


premiums = load_aggregated_premiums()

drugs_for_conditions = load_drugs_for_conditions()

db_conn = connect_db(args.postgreshost)
cur = db_conn.cursor()

es = Elasticsearch(args.eshost)
ic = IndicesClient(es)

mongo_client = connect_mongodb(args.mongohost)


# regular expression to pick off the number at the end of the Rating Area string
re_rating_area_number = re.compile(r'([0-9]+)$')

# all the states that are in the ACA data
all_states = ['PA', 'AZ', 'FL', 'LA', 'MT', 'NM', 'AK', 'NC', 'OR', 'MS', 'AR', 'MO', 'IL', 'IN', 'HI', 'WY', 'UT',
              'MI', 'KS', 'GA', 'WI', 'NE', 'OH', 'NV', 'OK', 'AL', 'ND', 'DE', 'WV', 'ME', 'TN', 'VA', 'SD', 'NH',
              'IA', 'SC', 'TX', 'NJ']

# states that we want to process
some_states = ['SC', 'AZ', 'FL', 'LA', 'MT']
#               'NM', 'NC', 'OR', 'MS', 'AR',
#               'MO', 'IL', 'IN', 'HI', 'WY',
#               'UT', 'NJ', 'MI', 'KS', 'GA',
#               'WI', 'NE', 'OH', 'NV', 'OK',
#               'AL', 'ND', 'DE', 'WV', 'ME',
#               'TN', 'VA', 'SD', 'NH', 'IA',
#               'TX', 'PA', 'AK']

for state in all_states:
    print "Processing {0}".format(state)

    # this list of column names makes the reference into the cursor more readable
    column = {'standardcomponentid': 0,
              'planid': 1,
              'planname': 2,
              'plantype': 3,
              'metallevel': 4,
              'url': 5,
              'issuer': 6,
              'issuerid': 7,
              'issuerName': 8,
              }

    parameters = {'statecode': state}

    print "Querying plan data for {0}".format(state)

    cur.execute('SELECT DISTINCT ON (pa.standardcomponentid) '
                'pa.standardcomponentid,'
                'pa.planid,'
                'pa.planmarketingname,'
                'pa.plantype,'
                'pa.metallevel,'
                'pa.planbrochure,'
                'hi."ISSR_LGL_NAME" AS issuer,'
                'hi."HIOS_ISSUER_ID" AS issuerid,'
                'hi."MarketingName" AS issuerName '
                'FROM plan_attributes pa,'
                'hios_issuer hi,'
                'rates r '
                'WHERE pa.issuerid = hi."HIOS_ISSUER_ID" '
                'AND r.planid = pa.standardcomponentid '
                'AND pa.statecode = %(statecode)s AND pa.dentalonlyplan=\'No\' '
                'AND r.rateexpirationdate > CURRENT_DATE '
                'AND r.rateeffectivedate <= CURRENT_DATE '
                'ORDER BY '
                'pa.standardcomponentid, pa.planid',
                parameters)

    plan_id = None
    plan_name = None
    issuer_name = None
    url = None

    es_doc = {}

    print "Processing plan data for {0}".format(state)

    actions = []

    for row in cur:
        # NOTE: the plan_id and standardcomponentid are not quite the same thing, but the plan_id has multiple meanings
        # that overlap with the standard component id. In these cases we are using the term plan_id even though for
        # plan_attributes and benefits_and_cost_sharing it is equivalent to the standardcomponentid. The
        # standardcomponentid looks like the plan_id but with a suffix of -01 or similar.

        plan_id = row[column['standardcomponentid']]

        providers = fetch_providers_for_plan(mongo_client, plan_id)
        formulary = fetch_drugs_for_plan(mongo_client, plan_id)

        # if we have nor formulary or list of providers, skip this plan
        if len(providers) == 0 or len(formulary) == 0:
            print 'Skipping {0} due to missing providers or missing formulary'.format(plan_id)
            continue

        params = {'plan_id': plan_id}
        indexed_plans_cursor = db_conn.cursor()
        indexed_plans_cursor.execute('SELECT idxp.plan_id FROM indexed_plans idxp '
                                     'WHERE idxp.plan_id = %(plan_id)s '
                                     'AND idxp.indexed_plans2 = TRUE',
                                     params)

        index_plan = True
        for indexed_plan in indexed_plans_cursor:
            if plan_id == indexed_plan[0]:
                print "Skipping {0}".format(plan_id)
                index_plan = False
                break

        if index_plan:
            issuer_name = row[column['issuerName']]

            # look up the logo url
            params = {'plan_id': plan_id}
            logo_cursor = db_conn.cursor()
            logo_cursor.execute('SELECT l.logo_url FROM logos l, plan_attributes pa '
                                'WHERE l.id = pa.logo_url_id '
                                'AND pa.standardcomponentid = %(plan_id)s',
                                params)

            logo_url = ''
            for logo_row in logo_cursor:
                logo_url = logo_row[0]
                break

            if not issuer_name:
                issuer_name = row[column['issuer']]

            if plan_id in premiums:
                # finalize the document
                es_doc = {'plan_name': row[column['planname']],
                          'issuer': issuer_name,
                          'plan_type': row[column['plantype']],
                          'level': row[column['metallevel']],
                          'url': row[column['url']],
                          'logo_url': logo_url,
                          'state': state,
                          'premiums_median': premiums[plan_id]['median'],
                          'premiums_q1': premiums[plan_id]['q1'],
                          'premiums_q3': premiums[plan_id]['q3'],
                          'drugs': formulary,
                          'providers': providers,
                          'conditions': fetch_conditions_for_plan(plan_id),
                          'plan_rank_0': None,
                          'plan_rank_1': None,
                          'plan_rank_2': None,
                          'plan_rank_3': None,
                          'plan_rank_4': None,
                          'plan_rank_5': None,
                          'plan_rank_6': None,
                          'plan_rank_7': None,
                          'plan_rank_8': None,
                          'plan_rank_9': None}
                action = {
                    "_index": "plans_v3",
                    "_type": "plan",
                    "_id": plan_id,
                    "_source": es_doc
                }
                actions.append(action)

            try:
                helpers.bulk(es, actions, chunk_size=1, request_timeout=60)
            except ConnectionTimeout, ConnectionError:
                print "ES Connection Timeout on plan {0}".format(plan_id)

            params = {'plan_id': plan_id}
            indexed_plans_cursor.execute('INSERT INTO indexed_plans (plan_id, indexed_plans2) '
                                         'VALUES (%(plan_id)s, True) '
                                         'ON CONFLICT (plan_id) '
                                         'DO UPDATE SET (Indexed, indexed_plans2) = (FALSE, TRUE) '
                                         'WHERE indexed_plans.plan_id = %(plan_id)s',
                                         params)
            db_conn.commit()

            print "Processed {0} {1}".format(plan_id, issuer_name)
            # reset for the next state
            del actions[:]
