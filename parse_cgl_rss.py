#!/usr/bin/env python

import feedparser
import json
import re
import datetime
import pymongo
from pymongo import MongoClient
import redis
import statistics
import sys



CRAIGSLIST_APA_URL_BASE="http://sfbay.craigslist.org/search/apa"
CRAIGSLIST_QUERYSTRING="?format=rss&s="
CRAIGSLIST_RSS_PER_PAGE=25


def get_craigslist_apa_url(index):
	return CRAIGSLIST_APA_URL_BASE + CRAIGSLIST_QUERYSTRING + str(index)

class cgl_apa_post:
	def __init__(self, post_id, place, place_code, bd, price, sqft, pub_date):
		self.post_id = post_id
		self.place = place
		self.place_code = place_code
		self.bd = bd
		self.price = price
		self.sqft = sqft
		self.pub_date = pub_date


def parse_cgl_apa_title(title):
	place = ""
	price = 0
	bd = 0
	sqft = 0
	title_tuple = (place, bd, price, sqft)

	match = re.search('\((.*)\)', title)
	if not match:
		return title_tuple

	place = match.group(1)
	if "/" in place:
		place = place.split("/")[0]

	place = place.strip().lower()

	if re.search("[^a-zA-Z\s]", place):
		return title_tuple

	match = re.search('&#x0024;(\d+) (\d+)bd', title)
	if not match:
		return title_tuple
	
	price = int(match.group(1))
	bd = int(match.group(2))

	match = re.search("(\d+)sqft", title)
	if match:
		sqft = int(match.group(1))

	title_tuple = (place, bd, price, sqft)

	return title_tuple

		
def parse_cgl_apa_entry(entry):

	(place, bd, price, sqft) = parse_cgl_apa_title(entry["title"])

	#'link':'http://sfbay.craigslist.org/sfc/apa/4650586050.html',
	link = entry["link"]
	print("Link: " + link)
	link_split = link.split('/');
	if len(link_split) > 5:
		place_code = link_split[3]
		post_id = link_split[5].split('.')[0]
	else:
		post_id = None
	if not post_id:
		return None
	pub_date = entry["published"]
	if place == "":
		return None
	cpa = cgl_apa_post(post_id, place, place_code, bd, price, sqft, pub_date)
	return cpa


client = MongoClient('mongodb://localhost:27017/')
cgl_db = client["cgl_db"]
cgl_apa_sfbay = cgl_db["cgl_apa_sfbay"]

def parse_craigslist_apa():
	for i in range(1, 10000, CRAIGSLIST_RSS_PER_PAGE):
		feeds = feedparser.parse(get_craigslist_apa_url(i))
		for entry in feeds["entries"]:
			cpa = parse_cgl_apa_entry(entry)
			if not cpa:
				continue
			cpa_post = { "_id" : cpa.post_id,
					"place" : cpa.place,
				     	"place_code" : cpa.place_code,
					"bd": cpa.bd,
					"price": cpa.price,
					"sqft" : cpa.sqft,
					"pub_date" : cpa.pub_date}
			try:
				cgl_apa_sfbay.insert(cpa_post)
			except pymongo.errors.DuplicateKeyError:
				print("Duplicate entry:" + entry["title"])


redis = redis.Redis("localhost")

def cal_cgl_stats():
	rent_data = { }
	for cpa_post in cgl_apa_sfbay.find():
		price = cpa_post["price"]
		bd = cpa_post["bd"]
		price = cpa_post["price"]
		place = cpa_post["place"]
		if place not in rent_data:
			rent_data[place] = [ [], [], [], [], [], [], [], [], []]
		rent_data[place][bd].append(price)
		#print(("[%s][%d] = %d")%(place, bd, price))

	places = []
	for place in rent_data:
		dont_add = False
		for bd in range(1, 5):
			rents_bd = rent_data[place][bd]
			#print(("%s, %d")%(place, bd))
			#print(rents_bd)
			if len(rents_bd) <= 5:
				dont_add = True
				break
			mean = statistics.mean(rents_bd)
			mean = int(mean)
			median = statistics.median(rents_bd)
			median = int(median)
			variance = statistics.variance(rents_bd)
			variance = int(variance)
			redis.set("rent_data:" + place + ":" + str(bd) + ":mean", mean)
			redis.set("rent_data:" + place + ":" + str(bd) + ":median", median)
			redis.set("rent_data:" + place + ":" + str(bd) + ":variance", variance)
			redis.set("rent_data:" + place + ":" + str(bd) + ":count", len(rents_bd))
			del rents_bd[:]
		if not dont_add or bd >= 4:
			places.append(place)
		else:
			print("Not adding place " + place + " bd " + str(bd));

		
	redis.delete("cities")
	pipeline = redis.pipeline()
	places = sorted(places)
	for place in places:
		pipeline.rpush("cities", place)
	pipeline.execute()
		
		

if __name__ == "__main__":
	if len(sys.argv) > 1 and sys.argv[1] == "stats_only":
		cal_cgl_stats()
	else:
		parse_craigslist_apa()
		cal_cgl_stats()
	client.close()	
	
	
	
	

