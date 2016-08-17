#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
@author:  Tigi Thomas
@project: MIDS W210 Capstone - ACA Semantic Search
@module:  aca_yelpreader
@desc :   Some test code to pull provider rating from yelp.
"""


from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator
import os
import json

auth = Oauth1Authenticator(
    consumer_key = "",
    consumer_secret="",
    token="",
    token_secret=""
)

client = Client(auth)

params = {
	'term': 'Optometry',
	'category_filter': 'health'
	'sort':2
}

a=client.search('341+West+Tudor+Road+Anchorage+AK+99503', **params)
a.businesses
for item in a.businesses:
    print item.name, item.rating, item.review_count
				

b = client.get_business('', **params)

"city": "Anchorage", "zip": "99503", "phone": "9077706652", "state": "AK", "address_2": "Suite 101", "address": "341 West Tudor Road"



b = client.get_business('Makar', **params)
a.businesses    
for item in a.businesses:
    print item.name, item.rating, item.review_count
    
    
params = {
    'category': 'health'
}

c = client.phone_search('+19077706652', **params)
c.businesses  
for item in c.businesses:
    print item
for item in c.businesses:
    print item.name, item.rating, item.review_count