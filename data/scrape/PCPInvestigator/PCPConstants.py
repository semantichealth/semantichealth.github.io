
# CHANGE THIS TO YOUR EXPECTED INDICATOR of a new provider in the text file
#
PROVIDER_TRIGGER = "Provider ID:"

# CHANGE THIS TO YOUR EXPECTED PRACTICES or a suitable regex
#
KNOWN_PRACTICES = ["Family Practice", "General Practice", "Pediatrics", "Internal Medicine", "Obstetrics & Gynecology - CA PCP", "Obstetrics & Gynecology"]


# CHANGE THIS to connect to the json database you'd like to use
#
DB_PORT = 27017
DB_HOST = "localhost"

# CHANGE THESE to be the state and zip code you'd like to calculate distances from 
#
YOUR_ZIP_CODE = "91311"
YOUR_HOME_STATE = "CA"


# KEEP THESE NICE AND HIGH. Scraping violates Google's ToS. Proceed at your own risk.
#
SEARCH_SLEEPTIME = [12, 15, 18, 20, 22, 25, 30]  # seconds to sleep between searches so Google doesn't block your IP
SITE_SLEEPTIME = [10, 15, 18, 20] # seconds between site searches for the same reason


