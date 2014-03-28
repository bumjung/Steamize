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

import logging
logging.basicConfig(filename='exceptions.log',level=logging.DEBUG)

def load_url(url, timeout):
    conn = requests.get(url=url, timeout=timeout)
    return simplejson.loads(conn.content)

def index(request) :
	key='753C3B3FF04FD9A4B520F90BB97059D6'
	steamid='76561198064586875'
	#76561198064586875 paul
	#76561198035798554 rix
	startTimeTotal = datetime.now()

	startTime = datetime.now()
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
	# We can use a with statement to ensure threads are cleaned up promptly
	with concurrent.futures.ProcessPoolExecutor(max_workers=10) as executor:
    # Start the load operations and mark each future with its URL
	    future_to_url = {executor.submit(load_url, url, 60): url for url in URLS}
	    for future in concurrent.futures.as_completed(future_to_url):
	        url = future_to_url[future]
	        try:
	            data = future.result() 
	            profile=data['response']['players'][0]
	        except Exception as exc:
	            #print('%r generated an exception: %s' % (url, exc))
	            try:
	            	gameLib=data['response']['games']
	            except Exception as exc:
	            	friendsList=data['friendslist']['friends']
	            	logging.debug('%r generated an exception: %s' % (url, exc))
	            #print('%r page is %d bytes' % (url, len(data)))
	
	# Save appropriate json API URLs into an array
	del URLS[:]
	URLS=[]
	hours_played=0



	print("profile:")
	print(datetime.now()-startTime)


	startTime = datetime.now()

	for i in gameLib:
		if i['playtime_forever'] > -1:
			hours_played+=i['playtime_forever']/60
			appid = i['appid']
			URLS.append('http://store.steampowered.com/api/appdetails/?appids='
				+str(appid)
				+'&appid='
				+str(appid)
				+'&key='
				+'&cc=US&l=english&v=1%20HTTP/1.1')

			URLS.append('http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid='
				+str(appid)
				+'&key='
				+key
				+'&steamid='
				+steamid)

	# We can use a with statement to ensure threads are cleaned up promptly
	totalSpent=0
	totalAchievement=0
	achievements=[]

	with concurrent.futures.ProcessPoolExecutor(max_workers=100) as executor:
    # Start the load operations and mark each future with its URL
	    future_to_url = {executor.submit(load_url, url, 60): url for url in URLS}
	    for future in concurrent.futures.as_completed(future_to_url):
	        url = future_to_url[future]

	        try:
	            data = future.result()
	            a=url.find("appid=")+6
	            b=url.find("&key")
	            idnum=url[a:b]
	            #print("++++++++" + str(idnum))
	            totalSpent+=data.values()[0]['data']['price_overview']['final']
	        except Exception as exc:
	        	logging.debug('%r generated an exception: %s' % (url, exc))
            	try:
            		test=data['playerstats']['achievements']
            	except Exception as exc:
            		logging.debug('%r generated an exception: %s' % (url, exc))
            	else:
            		temp=[]
            		for achiv in data['playerstats']['achievements']:
            			if(achiv['achieved'] > 0):
	            			totalAchievement+=1
	            			temp.append([data['playerstats']['gameName'],achiv['apiname'],idnum])
	            	achievements.append(temp)

	# We can use a with statement to ensure threads are cleaned up promptly

	print("cost and achievements:")
	print(datetime.now()-startTime)

	totalSpent=totalSpent/100.0

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
	render=render_to_response('base.html',profile_data,context_instance=RequestContext(request))
	return render

