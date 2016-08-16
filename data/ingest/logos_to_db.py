import psycopg2
import csv


"""

    This code takes a CSV file that contains URLs to health insurance company logos and
    updates the logos table in PostgreSQL with the information.

    The logos table is joined with other tables when the plans index is created.

"""


# get a connection to the database
def connect_db(host):
    conn = psycopg2.connect(user="acaproject",
                            database="acaproject",
                            password="test1234",
                            host=host,
                            port="5432")
    return conn


def load_issuers_logos_csv():
    db_conn = connect_db('w210.cxihwctrc5di.us-west-1.rds.amazonaws.com')
    cur = db_conn.cursor()

    with open('../konniam/elasticsearch-scripts/issuers_logos.csv', 'r') as f:
        reader = csv.reader(f, skipinitialspace=True)
        first_line = True
        field_names = []

        for row in reader:
            if first_line:
                field_names = row
                first_line = False
            else:
                d = {}
                for i, field in enumerate(row):
                    if i < 4:
                        d[field_names[i]] = field
                    else:
                        d[str(i)] = field

                try:
                    cur.execute('INSERT INTO logos ("issr_lgl_name", "marketingname", "state", "logo_url") '
                                'VALUES (%(ISSR_LGL_NAME)s, %(MarketingName)s, %(State)s, %(image_url_1)s)',
                                d)

                except Exception as ex:
                    print "error"
                    print ex
    db_conn.commit()
    cur.close()
    db_conn.close()


if __name__ == '__main__':
    load_issuers_logos_csv()
