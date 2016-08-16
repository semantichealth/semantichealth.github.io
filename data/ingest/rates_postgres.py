import csv
import psycopg2

"""

    Populate the PostgreSQL rate table from the rates.CSV file from CMS.gov.

"""


# get a connection to the database
def connect_db():
    conn = psycopg2.connect(user="acaproject",
                            database="acaproject",
                            password="test1234",
                            host="w210.cxihwctrc5di.us-west-1.rds.amazonaws.com",
                            port="5432")
    return conn

db_conn = connect_db()
cur = db_conn.cursor()

rateFields = ['IndividualRate', 'IndividualTobaccoRate', 'Couple', 'PrimarySubscriberAndOneDependent',
              'PrimarySubscriberAndTwoDependents', 'PrimarySubscriberAndThreeOrMoreDependents',
              'CoupleAndOneDependent', 'CoupleAndTwoDependents', 'CoupleAndThreeOrMoreDependents']

with open("Rate_PUF.csv", "r") as puf:
    rates_gen = csv.DictReader(puf)
    line = 0
    for rate in rates_gen:
        # convert empty string to "null"
        for rateField in rateFields:
            if rateField in rate.keys():
                if not rate[rateField]:
                    rate[rateField] = None

        cur.execute("INSERT INTO rates ("
                    "BusinessYear, StateCode, IssuerId, SourceName, VersionNum, ImportDate, IssuerId2,"
                    "FederalTIN, RateEffectiveDate, RateExpirationDate, PlanId, RatingAreaId, Tobacco, "
                    "Age, IndividualRate, IndividualTobaccoRate, Couple, PrimarySubscriberAndOneDependent, "
                    "PrimarySubscriberAndTwoDependents, PrimarySubscriberAndThreeOrMoreDependents, "
                    "CoupleAndOneDependent, CoupleAndTwoDependents, CoupleAndThreeOrMoreDependents, RowNumber) "
                    "VALUES ( "
                    "%(BusinessYear)s, %(StateCode)s, %(IssuerId)s, %(SourceName)s, %(VersionNum)s, %(ImportDate)s,"
                    "%(IssuerId2)s, %(FederalTIN)s, %(RateEffectiveDate)s, %(RateExpirationDate)s, %(PlanId)s, "
                    "%(RatingAreaId)s, %(Tobacco)s, %(Age)s, %(IndividualRate)s, %(IndividualTobaccoRate)s, "
                    "%(Couple)s, %(PrimarySubscriberAndOneDependent)s, %(PrimarySubscriberAndTwoDependents)s, "
                    "%(PrimarySubscriberAndThreeOrMoreDependents)s, %(CoupleAndOneDependent)s, "
                    "%(CoupleAndTwoDependents)s, %(CoupleAndThreeOrMoreDependents)s, %(RowNumber)s )",
                    rate)

        line += 1
        db_conn.commit()
    print "{0} entries processed...".format(line)
    cur.close()
    db_conn.close()
