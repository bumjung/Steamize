from django.shortcuts import render,render_to_response
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.utils import simplejson
from django.template import RequestContext

from datetime import datetime
from random import randrange
import sys
import os
import math
import json
import logging
import json

from database import *

import requests
import concurrent.futures

logging.basicConfig(filename='exceptions.log',level=logging.DEBUG)

def load_url(url, timeout):
    conn = requests.get(url=url, timeout=timeout) # Get JSON from steam API and save it to conn
    return simplejson.loads(conn.content) # Load stringified JSON to a JSON object

def index(request) :
	render=render_to_response('summary_index.html',{},context_instance=RequestContext(request))
	return render

def get_profile(request) :
	steam_id=request.GET.get('steamid')
	return HttpResponseRedirect("/summary/profile/"+steam_id)

#@cache_page(60 * 5)
def profile(request, steam_id=-1) :
	if(steam_id == -1):
		steam_id=request.GET.get('steamid')
	key='753C3B3FF04FD9A4B520F90BB97059D6' # TODO: HIDE KEY
	#steamid=request.GET.get('steamid')#'76561198064586875' # TODO: INPUT request.GET.get('steamid') FROM INDEX
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
	+steam_id,
	
	'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key='
	+key
	+'&steamid='
	+steam_id
	+'&format=json&include_played_free_games=1&include_appinfo=1'#,
	
	#'http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key='
	#+key
	#+'&steamid='
	#+steamid
	#+'&relationship=friend'
	]

	steamAcc.init_account(steam_id)

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
	total_hours_played=0


	print("profile:")
	print(datetime.now()-startTime) # Calculate profile performance time

 	# Start time count for second asynchronous load
	startTime = datetime.now()

	# Loop through all of user's games
	for i in gameLib:
		if i['playtime_forever'] > -1: 						# Excludes not-owned games
			total_hours_played+=i['playtime_forever']/60 	# Increment hours played in hours
			appid = str(i['appid'])
			steamAcc.init_game(steam_id,appid)
			steamAcc.update_games(steam_id,appid,'hours_played',i['playtime_forever']/60)						
			#print(i['name'])
			steamAcc.update_games(steam_id,appid,'name',i['name'])	
			# Contains JSON for game price + other info
			URLS2.append('http://store.steampowered.com/api/appdetails/?appids='
				+appid
				+'&appid='
				+appid
				+'&key='
				+'&cc=US&l=english&v=1%20HTTP/1.1')

			# Contains all achievements for all games
			URLS2.append('http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid='
				+appid
				+'&key='
				+key
				+'&steamid='
				+steam_id)
	# Initialize variables
	total_spent=0
	total_achievements=0
	achievements=[]
	games=[]
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
	            test=data['playerstats']['achievements']
	       	except Exception:
	         	try:
	         		price=data.values()[0]['data']['price_overview']['final']
	         		steamAcc.update_games(steam_id,appid,'price',price/100.0)	
	         		total_spent+=price
	         		#steamAcc.update_database(appid,'price',data.values()[0]['data']['price_overview']['final'])
	         	except Exception:
	         		pass
	        else:
	        	achievement_list=[]
	        	for achiev in data['playerstats']['achievements']:
	        		if(achiev['achieved'] > 0):
	        			achievement_list.append(achiev['apiname']
					.lower()
					.replace('_',' ')
					.replace('achievement', '')
					.replace('ach', '')
					)
	        			total_achievements+=1
	        	steamAcc.update_games(steam_id,appid,'achievements',achievement_list)
	        	steamAcc.update_games(steam_id,appid,'all_achv',len(data['playerstats']['achievements']))
	        	steamAcc.update_games(steam_id,appid,'completed_achv',len(achievement_list))



	print("cost and achievements:")
	print(datetime.now()-startTime) # Calculate profile performance time

	total_spent=total_spent/100.0 # Convert to dollar amount

	print("Total time:")
	print(datetime.now()-startTimeTotal)


	account_data_dict = {
		"name":profile['personaname'],
		"avatar":profile['avatar'],
		"total_hours_played":total_hours_played,
		"total_spent":total_spent,
		"total_completed_achv":total_achievements
	}
	steamAcc.update_account(steam_id,account_data_dict)

	profile=steamAcc.return_account_info(steam_id)

	preview = []
	if total_achievements >= 10:
		achivNum=10
	else:
		achivNum=total_achievements

	for i in range(0,achivNum):
		while True:
			x = randrange(0,len(profile['games']))

			if len(profile['games'][x]['achievements']) > 0:
				y = randrange(0, len(profile['games'][x]['achievements']))
				achivTitle = (profile['games'][x]['achievements'][y]
					.lower()
					.replace('_',' ')
					.replace('achievement', '')
					.replace('ach', '')
					)
				achiv_dict={
					'achievement' : achivTitle,
					'name' : profile['games'][x]['name'],
					'app_id' : profile['games'][x]['app_id']
					}
				if "new " not in achivTitle:
					if achiv_dict not in preview:
						preview.append(achiv_dict)
						break

	profile_data={
		'profile':steamAcc.return_account_info(steam_id),
		'achv_preview':preview
	}
	#print(profile_data)
	render=render_to_response('summary_main.html',profile_data,context_instance=RequestContext(request))
	return render

def game(request,steam_id,app_id) :
	
	game=steamAcc.return_game_info(steam_id,app_id)
	profile=steamAcc.return_account_info(steam_id)
	#print(game)
	hours_time={
		'weeks' : (game['hours_played']/168),
		'days' : (game['hours_played']%168)/24,
		'hours' : ((game['hours_played']%168)%24)
	}
	hr_data_game=game['hours_played']
	hr_data_other=profile['account']['total_hours_played']-hr_data_game
	achv_data_game=game['completed_achv']
	achv_data_other=profile['account']['total_completed_achv']-achv_data_game
	achv_data_percent=int(round((float(game['completed_achv'])/float(game['all_achv'])) * 100))#float(profile['account']['total_completed_achv'])) * 100))
	#print(achv_data_percent)
	#print(hr_data_game)
	#print(hr_data_other)
	game_data={
		'profile':profile,
		'game':game,
		'hours_time':hours_time,
		'hr_data':[hr_data_game,hr_data_other],
		'achv_data':[achv_data_percent,achv_data_game,achv_data_other]
	}
	render=render_to_response('summary_game.html',game_data,context_instance=RequestContext(request))
	return render

