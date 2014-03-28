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
import gevent
from gevent import monkey
gevent.monkey.patch_all()

import logging
logging.basicConfig(filename='exceptions.log',level=logging.DEBUG)

def load_url(url, timeout, second=False, idnum=-1):
	conn=requests.get(url=url, timeout=timeout)
	conn=simplejson.loads(conn.content)
	if second:
		conn.update({
    			"idnum":idnum
    		})
	return conn

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
	jobs = [gevent.spawn(load_url, url,60) for url in URLS]
	gevent.joinall(jobs)
	profile=jobs[0].value['response']['players'][0]
	gameLib=jobs[1].value['response']['games']
	#print(simplejson.dumps(gameLib, indent=4, separators=(',', ': ')))
	# Save appropriate json API URLs into an array
	del URLS[:]
	urls=[]
	hours_played=0

	print("profile:")
	print(datetime.now()-startTime)


	startTime = datetime.now()

	for i in gameLib:
		if i['playtime_forever'] >= 0:
			hours_played+=i['playtime_forever']/60
			appid = i['appid']
			urls.append('http://store.steampowered.com/api/appdetails/?appids='
				+str(appid)
				+'&appid='
				+str(appid)
				+'&key='
				+'&cc=US&l=english&v=1%20HTTP/1.1')

			urls.append('http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid='
				+str(appid)
				+'&key='
				+key
				+'&steamid='
				+steamid)

	# We can use a with statement to ensure threads are cleaned up promptly
	totalSpent=0
	totalAchievement=0
	achievements={}
	jsons=[gevent.spawn(load_url,url,60, True, url[(url.find("appid=")+6):(url.find("&key"))] ) for url in urls]
	gevent.joinall(jsons)
	for json in jsons:
		json=json.value
		try:
			totalSpent+=json[json['idnum']]['data']['price_overview']['final']
		except Exception as exc:
			logging.debug('%r generated an exception: %s' % (url, exc))
        	try:
        		test=json['playerstats']['achievements']
        	except Exception as exc:
        		logging.debug('%r generated an exception: %s' % (url, exc))
        	else:
        		temp=[]
        		for achiv in json['playerstats']['achievements']:
        			if(achiv['achieved'] > 0):
        				totalAchievement+=1
        				temp.append(achiv['apiname'])
    			achievements.update({
    				json['playerstats']['gameName']:temp
    			})

   	#print simplejson.dumps(achievements, indent=4, separators=(',', ': '))
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
			if len(achievements.values()[x]) > 0:
				y = randrange(0, len(achievements.values()[x]))
				#print(y)
				achivTitle = (achievements.values()[x][y]
					.lower()
					.replace('_',' ')
					.replace('achievement', '')
					.replace('ach', '')
					)
				achivBoth=[achivTitle,achievements.keys()[x]]
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

