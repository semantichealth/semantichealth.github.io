import os, glob
from s3_helpers import *

def do_setup(feature):
    '''
    '''

    try:
        # create folder
        for f in ['training','online','log']+[feature]:
            if not os.path.exists(f):
                os.makedirs(f)
        # download feature pickles
        s3_helper().download_all(feature)
        return True
    except:
        return False
