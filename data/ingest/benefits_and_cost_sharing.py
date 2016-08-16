
import csv
import psycopg2


"""
    This code takes the benefits-and-cost-sharing PUF file and inserts each row from the CSV into
    the benefits and cost sharing table in PostgreSQL. This data is joined with other tables when
    creating the elasticsearch index.

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


rates = []
count = 0
with open("benefits-and-cost-sharing-puf.csv", "r") as puf:
    attr_gen = csv.DictReader(puf)
    line = 0
    for attr in attr_gen:
        cur.execute("INSERT INTO benefits_and_cost_sharing ("
                    "BusinessYear, StateCode, IssuerId, SourceName, VersionNum, ImportDate,"
                    "IssuerId2, StateCode2, StandardComponentId, PlanId, BenefitName, CopayInnTier1,"
                    "CopayInnTier2, CopayOutofNet, CoinsInnTier1, CoinsInnTier2, CoinsOutofNet, IsEHB,"
                    "IsStateMandate, IsCovered, QuantLimitOnSvc, LimitQty, LimitUnit, MinimumStay, Exclusions,"
                    "Explanation, EHBVarReason, IsExclFromInnMOOP, IsExclFromOonMOOP, RowNumber )"
                    "VALUES ( "
                    "%(BusinessYear)s,%(StateCode)s,%(IssuerId)s,%(SourceName)s,%(VersionNum)s,%(ImportDate)s,"
                    "%(IssuerId2)s,%(StateCode2)s,%(StandardComponentId)s,%(PlanId)s,%(BenefitName)s,"
                    "%(CopayInnTier1)s,%(CopayInnTier2)s,%(CopayOutofNet)s,%(CoinsInnTier1)s,%(CoinsInnTier2)s,"
                    "%(CoinsOutofNet)s,%(IsEHB)s,%(IsStateMandate)s,%(IsCovered)s,%(QuantLimitOnSvc)s,%(LimitQty)s,"
                    "%(LimitUnit)s,%(MinimumStay)s,%(Exclusions)s,%(Explanation)s,%(EHBVarReason)s,"
                    "%(IsExclFromInnMOOP)s, %(IsExclFromOonMOOP)s,%(RowNumber)s)",
                    attr)
        line += 1
        db_conn.commit()
    print "{0} entries processed...".format(line)
    cur.close()
    db_conn.close()
