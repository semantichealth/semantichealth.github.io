#!/usr/bin/python
import pickle
from datetime import datetime
from time import gmtime, strftime
import pytz
import boto3
import argparse
from elasticsearch import Elasticsearch


"""

    This code looks through an S3 bucket for .pickle files and downloads those files.
    The contents of the .pickle files form the updated ranking vectors and are used
    to update the plan documents in the elasticsearch plans index.

    This script is designed to run periodically by cron

"""


arg_parser = argparse.ArgumentParser(description='Process aggregate plan data into elastic search')
arg_parser.add_argument('--eshost', dest='eshost',
                        default='http://169.45.104.77:80')

args = arg_parser.parse_args()

cutoff = datetime(2016, 7, 29, 0, 0, 0, 0, tzinfo=pytz.utc)

es = Elasticsearch(args.eshost)

s3 = boto3.client('s3')

response = s3.list_objects(Bucket='w210.data', Prefix='training/', Delimiter='/')
file_list = [x for x in response['Contents'] if x['LastModified'] > cutoff]

with open('/home/ec2-user/letor_update.log', 'a') as logfile:

    for pkl_file in file_list:
        fname = pkl_file['Key'].split('/')[1]
        state = fname[:2]
        s3.download_file('w210.data', pkl_file['Key'], fname)
        with open(fname, 'rb') as pkl:
            rank_data = pickle.load(pkl)

        plan_ids = rank_data[0]
        rank_vectors = rank_data[1]

        logfile.write('{0}\t----------------------- ' + state + ' -------------------------\n'.format(
            strftime("%Y-%m-%d %H:%M:%S", gmtime())))
        for i, plan_id in enumerate(plan_ids):
            # print plan_id
            try:
                vector = rank_vectors[:, i].tolist()
                plan_ranks = {}
                for j, _rank in enumerate(vector):
                    plan_ranks['plan_rank_' + str(j)] = vector[j]

                body = {'doc': plan_ranks}

                es.update(index='plans', doc_type='plan', id=plan_id, body=body)
                logfile.write('{0}\tUpdated {1}\n'.format(strftime("%Y-%m-%d %H:%M:%S", gmtime()), plan_id))
            except Exception as e:
                logfile.write('{0}\t{1}\n'.format(strftime("%Y-%m-%d %H:%M:%S", gmtime()), e))
