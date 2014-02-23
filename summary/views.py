from django.shortcuts import render,render_to_response
from django.http import HttpResponse, HttpRequest
from django.utils import simplejson
from django.template import RequestContext
 
import sys
import os
import math
import requests
import concurrent.futures

def load_url(url, timeout):
    conn = requests.get(url=url, timeout=timeout)
    return simplejson.loads(conn.content)

def index(request) :
	from datetime import datetime
	key='753C3B3FF04FD9A4B520F90BB97059D6'
	steamid='76561198064586875'
	startTime = datetime.now()
	URLS=['http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key='
	+key
	+'&steamids='
	+steamid,
	'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key='
	+key
	+'&steamid=76561198064586875&format=json&include_appinfo=1&include_played_free_games=1'
	]
	# We can use a with statement to ensure threads are cleaned up promptly
	with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    # Start the load operations and mark each future with its URL
	    future_to_url = {executor.submit(load_url, url, 60): url for url in URLS}
	    for future in concurrent.futures.as_completed(future_to_url):
	        url = future_to_url[future]
	        try:
	            data = future.result() 
	            profile=data['response']['players'][0]
	            # do json processing here
	        except Exception as exc:
	            print('%r generated an exception: %s' % (url, exc))
	            gameLib=data['response']['games']
	        else:
	            print('%r page is %d bytes' % (url, len(data)))
	
	# Save appropriate json API URLs into an array

	URLS=[]
	URLS2=[]
	hours_played=0

	for i in gameLib:
		if i['playtime_forever'] > 0:
			hours_played+=i['playtime_forever']/60.0
			appid = i['appid']
			URLS.append('http://store.steampowered.com/api/appdetails/?appids='
				+str(appid)
				+'&cc=US&l=english&v=1%20HTTP/1.1')

			URLS2.append('http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid='
				+str(appid)
				+'&key='
				+key
				+'&steamid='
				+steamid)

	# We can use a with statement to ensure threads are cleaned up promptly
	spentTotal=0
	totalAchievement=0

	with concurrent.futures.ThreadPoolExecutor(max_workers=35) as executor:
    # Start the load operations and mark each future with its URL
	    future_to_url = {executor.submit(load_url, url, 60): url for url in URLS}
	    for future in concurrent.futures.as_completed(future_to_url):
	        url = future_to_url[future]
	        try:
	            data = future.result()
	            spentTotal+=data.values()[0]['data']['price_overview']['final']
	            # do json processing here
	        except Exception as exc:
	            print('%r generated an exception: %s' % (url, exc))
	            
	        else:
	            print('%r page is %d bytes' % (url, len(data)))

	# We can use a with statement to ensure threads are cleaned up promptly
	totalAchievement=0

	with concurrent.futures.ThreadPoolExecutor(max_workers=35) as executor:
    # Start the load operations and mark each future with its URL
	    future_to_url = {executor.submit(load_url, url, 60): url for url in URLS2}
	    for future in concurrent.futures.as_completed(future_to_url):
	        url = future_to_url[future]
	        try:
	            data = future.result()
	            for achiv in data['playerstats']['achievements']:
	            	if achiv['achieved'] > 0:
	            		totalAchievement+=1
	            # do json processing here
	        except Exception as exc:
	            print('%r generated an exception: %s' % (url, exc))
	            
	        else:
	            print('%r page is %d bytes' % (url, len(data)))

	spentTotal=spentTotal/100.0;
	print("2")
	print(hours_played)
	print(spentTotal)
	print(totalAchievement)
	print(datetime.now()-startTime)
	profile_data={
		'profile' : profile,
		'hours_played':hours_played,
		'spentTotal' : spentTotal
	}
	render=render_to_response('base.html',profile_data,context_instance=RequestContext(request))
	return render

