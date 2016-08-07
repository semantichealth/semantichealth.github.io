from datetime import datetime, timedelta
from get_click_data import *
from train_one_state import *
from simulate_clicks import *
from do_setup import *
from logger import *
import traceback, time, sys
import numpy as np

from simulate_clicks import *

def main():
	'''
	'''
	next_run, hour, minute = datetime.now(), 1, 18
	s3_fea, test = 'feature_d', False
	log, ready = logger('training'), do_setup(s3_fea)

	while ready:
		# cyclic execution
		if datetime.now() < next_run:
			time.sleep((next_run-datetime.now()).total_seconds())
			continue
		# get click-through data
		try:
			log.start()
			click_data = get_click_data(log) if not test else simulate_clicks()
		except Exception as ex:
			traceback.print_exc(file=log.log_handler())
			log.error('error in getting click data, retry in %d minutes.' %minute)
			next_run = datetime.now() + timedelta(minutes=minute)
			log.stop()
			continue
		# train for each state
		failure, all_states = [], np.unique(click_data['state'])
		for state in all_states:
			try:
				train_one_state(click_data, state, log, s3_fea)
			except KeyboardInterrupt:
				log.stop()
				sys.exit('User termination')
			except Exception as ex:
				failure.append(state)
				traceback.print_exc(file=log.log_handler())
				log.trace('training has encountered an error for state %s' %state)
		# training completed, get next run time
		next_run = datetime.now() + timedelta(hours=hour)
		done_msg = 'training has completed for %d states, failed for %d states: %s' %(len(all_states)-len(failure), len(failure), str(failure))
		log.trace(done_msg)
		log.trace('next run time is %s, so long!' %str(next_run))
		log.stop()
		print '%s: %s' %(str(datetime.now()), done_msg)

if __name__ == "__main__":
	main()
