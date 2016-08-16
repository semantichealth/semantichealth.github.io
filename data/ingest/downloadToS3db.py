import boto3
from boto3.s3.transfer import S3Transfer
import requests
import hashlib
import psycopg2


"""
    This code follows the urls from the jsonurls table in PostgreSQL database and downloads
    the JSON file contents to a local file, and then uploades that file into S3. The S3
    bucket and key are stored in the jsonurls table.

    There isn't a way that I've found to stream the data directly from the JSON file URL into
    the S3 bucket, hence the download to local file. This is meant to run on an EC2 instance
    so that multiple instances can run at the same time in parallel. However, there is no
    synchronization of multiple processes because this wasn't ever done.


"""


# Download to a local file
def download_file(_url, stream=False):
    h = hashlib.md5(_url).hexdigest()
    local_file = h + '.tmp'
    r = requests.get(_url, stream=stream)
    with open(local_file, 'wb') as f:
        if stream:
            for chunk in r.iter_content(chunk_size=8196*64):
                if chunk:
                    f.write(chunk)
        else:
            f.write(r.content)
    return local_file


# Upload to S3 bucket
def xfer_to_s3(file_name, bucket, key):
    client = boto3.client('s3', 'us-west-1')
    transfer = S3Transfer(client)
    transfer.upload_file(file_name, bucket, key)


# download to a local file and then transfer to S3
# using the hashed URL as the S3 key
def process_url(_url, bucket_name, prefix):
    print "Processing {0}".format(_url)
    hashed_url = hashlib.md5(_url).hexdigest()
    f = download_file(_url)
    xfer_to_s3(f, bucket_name, prefix + str(hashed_url))
    return hashed_url


def connect_db():
    conn = psycopg2.connect(user="acaproject",
                            database="acaproject",
                            password="test1234",
                            host="w210.cxihwctrc5di.us-west-1.rds.amazonaws.com",
                            port="5432")
    return conn

######################################################################
#
# MAIN SCRIPT STARTS HERE
#
######################################################################

db_conn = connect_db()
cur = db_conn.cursor()
update_cur = db_conn.cursor()
cur.execute("SELECT url FROM jsonurls WHERE s3key is NULL")
urls = cur.fetchall()

for u in urls:
    # results are tuples where the first item is the url in this case
    url = dict(url=u[0])
    try:
        url['s3key'] = process_url(url['url'], 'w210', 'json/')
        url['status'] = 'PROCESSED'
        update_cur.execute("UPDATE jsonurls SET "
                           "status = (SELECT id FROM retrieval_status WHERE status=%(status)s), "
                           "s3key = %(s3key)s "
                           "WHERE url = %(url)s",
                           url)
    except Exception as ex:
        print ex

    db_conn.commit()

cur.close()
update_cur.close()
db_conn.close()
