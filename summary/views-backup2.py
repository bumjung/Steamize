from django.shortcuts import render,render_to_response
from django.http import HttpResponse, HttpRequest
from django.utils import simplejson
from django.template import RequestContext

from datetime import datetime
from random import randrange
 
import sys
import os
import math
import requests
import concurrent.futures
import json

import logging
logging.basicConfig(filename='exceptions.log',level=logging.DEBUG)

def load_url(url, timeout):
    conn = requests.get(url=url, timeout=timeout) # Get JSON from steam API and save it to conn
    return simplejson.loads(conn.content) # Load stringified JSON to a JSON object

def initialize_json():
	return {
			"steam_id":-1,
			"account":{
				"name":"",
				"avatar":"",
				"hours_played":-1,
				"total_spent":-1,
				"total_achiv":-1
			},
			"games":[
				{
					"app_id":-1,
					"name":"",
					"price":-1,
					"hours_played":-1,
					"total_achiv":-1,
					"achievements":[],
				}
			]
		}

def profile(request) :
	key='753C3B3FF04FD9A4B520F90BB97059D6' # TODO: HIDE KEY
	steamid='76561198064586875' # TODO: INPUT request.GET.get('steamid') FROM INDEX
	#76561198064586875 paul
	#76561198035798554 rix

	# Start time count for entire python build
	startTimeTotal = datetime.now() 

	# Start time count for first asynchronous load
	startTime = datetime.now() 

	# Insert Steam API urls to be requested
	URLS=['http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key='
	+key
	+'&steamids='
	+steamid,
	
	'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key='
	+key
	+'&steamid='
	+steamid
	+'&format=json&include_played_free_games=1'#,
	
	#'http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key='
	#+key
	#+'&steamid='
	#+steamid
	#+'&relationship=friend'
	]

	# Start asynchronous #1

	# We can use a with statement to ensure threads are cleaned up promptly
	with concurrent.futures.ProcessPoolExecutor(max_workers=10) as executor:
    	# Start the load operations and mark each future with its URL
	    future_to_url = {executor.submit(load_url, url, 60): url for url in URLS}
	    # Loop through futures as soon as it load_url function completes
	    for future in concurrent.futures.as_completed(future_to_url):
	        url = future_to_url[future]
	        try:
	        	# Save request JSON object
	            data = future.result() 
	            # Check if data is a summary JSON object
	            profile=data['response']['players'][0]
	        except Exception as exc:
	            try:
	            	gameLib=data['response']['games']
	            except Exception as exc:
	            	print('%r generated an exception: %s' % (url, exc))

	            	############################################
	            	# TODO: Make friends list
	            	############################################
	            	#friendsList=data['friendslist']['friends']
	            	############################################
	            	############################################
	
	# Save appropriate json API URLs into an array
	del URLS[:]
	URLS2=[] # Initialize second URL list
	hours_played=0

	print("profile:")
	print(datetime.now()-startTime) # Calculate profile performance time

 	# Start time count for second asynchronous load
	startTime = datetime.now()

	# Loop through all of user's games
	for i in gameLib:
		if i['playtime_forever'] > -1: 				# Excludes not-owned games
			hours_played+=i['playtime_forever']/60 	# Increment hours played in hours
			appid = i['appid']						

			# Contains JSON for game price + other info
			URLS2.append('http://store.steampowered.com/api/appdetails/?appids='
				+str(appid)
				+'&appid='
				+str(appid)
				+'&key='
				+'&cc=US&l=english&v=1%20HTTP/1.1')

			# Contains all achievements for all games
			URLS2.append('http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid='
				+str(appid)
				+'&key='
				+key
				+'&steamid='
				+steamid)

	# Initialize variables
	totalSpent=0
	totalAchievement=0
	achievements=[]
	
	# We can use a with statement to ensure threads are cleaned up promptly
	with concurrent.futures.ProcessPoolExecutor(max_workers=50) as executor:
    	# Start the load operations and mark each future with its URL
	    future_to_url = {executor.submit(load_url, url, 60): url for url in URLS2}
	    # Loop through futures as soon as it load_url function completes
	    for future in concurrent.futures.as_completed(future_to_url):
	        url = future_to_url[future]

	        try:
	        	# Save request JSON object
	            data = future.result()
	            # Extract appid
	            a=url.find("appid=")+6
	            b=url.find("&key")
	            # Save appid
	            appid=url[a:b]

	            #print("++++++++" + str(idnum))

	            # Attempt to use first URL JSON object (for game $ and other info)
	            totalSpent+=data.values()[0]['data']['price_overview']['final']
	        except Exception as exc:
	        	pass
            	try:
            		# Attempt to use second URL JSON object (for achievements)
            		test=data['playerstats']['achievements']
            	except Exception as exc:
            		pass
            	else:
            		temp=[]
            		for achiv in data['playerstats']['achievements']:
            			if(achiv['achieved'] > 0):
            				# Increment total achievements
	            			totalAchievement+=1
	            			# [ gameName, achivName, appid ]
	            			temp.append([ data['playerstats']['gameName'] , achiv['apiname'] , appid ])
	            	achievements.append(temp)

	print("cost and achievements:")
	print(datetime.now()-startTime) # Calculate profile performance time

	totalSpent=totalSpent/100.0 # Convert to dollar amount

	#for i in achievements:
	#	print("NEW APP")
	#	for j in i:
	#		print(j)
	tempTotalAchiv=totalAchievement
	achivShow = []
	if totalAchievement >= 10:
		achivNum=10
	else:
		achivNum=tempTotalAchiv

	for i in range(0,achivNum):
		while True:
			#print(len(achievements))
			x = randrange(0,len(achievements))
			#print("x"+ " " + str(x))

			if len(achievements[x]) > 0:
				y = randrange(0, len(achievements[x]))
				achivTitle = (achievements[x][y][1]
					.lower()
					.replace('_',' ')
					.replace('achievement', '')
					.replace('ach', '')
					)
				achivBoth=[achivTitle,achievements[x][y][0],achievements[x][y][2]]
				if "new " not in achivTitle:
					if achivBoth not in achivShow:
						achivShow.append(achivBoth)
						break

	print("Total time:")
	print(datetime.now()-startTimeTotal)
	profile_data={
		'profile' : profile,
		'hours_played':hours_played,
		'totalSpent' : totalSpent,
		'totalAchievement' : totalAchievement,
		'gameLib' : gameLib,
		'achivShow' : achivShow#,
		#'friendsList' : friendsList
	}
	render=render_to_response('summary_main.html',profile_data,context_instance=RequestContext(request))
	return render

from pymongo import Connection
from bson.objectid import ObjectId
def game(request) :

	connection=Connection()
	db=connection['test']
	profiles = db.profiles
	json=initialize_json()
	db.profiles.insert(json)

	render=render_to_response('summary_game.html',{},context_instance=RequestContext(request))
	return render

