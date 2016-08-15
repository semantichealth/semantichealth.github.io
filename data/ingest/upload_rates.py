import csv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


# get a connection to MongoDB
def connect_mongodb():
    try:
        mongodb_conn = MongoClient('ec2-54-153-83-172.us-west-1.compute.amazonaws.com', 27017)
        return mongodb_conn
    except ConnectionFailure as e:
        print "Unable to connect to MongoDB instance\n{0}\n".format(str(e))

mongo_conn = connect_mongodb()
mongo_db = mongo_conn.rates

rateFields = ['IndividualRate', 'IndividualTobaccoRate', 'Couple', 'PrimarySubscriberAndOneDependent',
              'PrimarySubscriberAndTwoDependents', 'PrimarySubscriberAndThreeOrMoreDependents',
              'CoupleAndOneDependent', 'CoupleAndTwoDependents', 'CoupleAndThreeOrMoreDependents']

dateFields = ['ImportDate', 'RateEffectiveDate', 'RateExpirationDate']

rates = []
count = 0
with open("Rate_PUF.csv", "r") as puf:
    rates_gen = csv.DictReader(puf)
    for rate in rates_gen:
        # convert strings to floats
        for rateField in rateFields:
            if rateField in rate.keys():
                if rate[rateField]:
                    rate[rateField] = float(rate[rateField])
        rates.append(rate)
        count += 1
        if count % 5000 == 0:
            results = mongo_db.rates.insert_many(rates)
            rates = []

    if len(rates) > 0:
        results = mongo_db.rates.insert_many(rates)

mongo_conn.close()
