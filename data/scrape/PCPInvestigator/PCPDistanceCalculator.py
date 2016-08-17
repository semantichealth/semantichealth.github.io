from math import sin, cos, radians, acos
from pymongo import Connection
import PCPConstants as CONSTANTS


EARTH_RADIUS_IN_MILES = 3958.761

connection = Connection(CONSTANTS.DB_HOST, CONSTANTS.DB_PORT) # default port for mongo
db = connection.test # attach to test db


def calculate(lat_a, long_a, lat_b, long_b):
    """all angles in degrees, result in miles"""
    lat_a = radians(lat_a)
    lat_b = radians(lat_b)
    delta_long = radians(long_a - long_b)
    cos_x = (
        sin(lat_a) * sin(lat_b) +
        cos(lat_a) * cos(lat_b) * cos(delta_long)
        )
    return acos(cos_x) * EARTH_RADIUS_IN_MILES




def getDistance(homeZipCode, awayZipCode) :

	homeZip = db.zips.find_one({ "_id" : str(homeZipCode)})
	awayZip = db.zips.find_one({ "_id" : str(awayZipCode)})

	#print "homeZip %s"%homeZip
	#print "awayZip %s"%awayZip

	if not homeZip : return "Unknown"
	if not awayZip: return "Unknown"


	distance = 0.0
	distance = calculate(float(homeZip["loc"][0]), float(homeZip["loc"][1]), float(awayZip["loc"][0]), float(awayZip["loc"][1]) )
	if distance >= 0 :
		distance = "%.1f"%round(distance,2)
	return distance


