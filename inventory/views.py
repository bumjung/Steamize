from django.shortcuts import render,render_to_response
from django.http import HttpResponse, HttpRequest
from django.utils import simplejson
from django.template import Context, loader, RequestContext

import sys
import os
import math
#import urllib2

def index(request) :

	#jsonurltest=urllib2.urlopen('http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=753C3B3FF04FD9A4B520F90BB97059D6&steamids=76561198064586875').read()
	#jsonurl=urllib2.urlopen('http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=753C3B3FF04FD9A4B520F90BB97059D6&steamids=76561198064586875')
	
	json=simplejson.load(jsonurl)

	#return HttpResponse(json['response']['players'][0]['steamid'])
	#return HttpResponse("Hello World")
	response = render_to_response('base.html', context_instance=RequestContext(request))
	return response
