import sys
import os
from pymongo import Connection
from bson.objectid import ObjectId
from bson.json_util import dumps

server='oceanic.mongohq.com'
port=10017#10097
db_name='app23517336'
username="bum"
password='jung'

print ('Connecting...')
connection=Connection(server, port)
print('Done Connecting')
print('Getting database...')
db=connection[db_name]
print('Done Getting Database')
print('Authenticating...')
db.authenticate(username,password)
print('Done Authenticating')


class steamAcc(object):
	
	profiles=db.profiles
	
	@staticmethod
	def init_account(steam_id):
		if profiles.find({'steam_id':steam_id}).count() == 0 :
			profiles.insert({
				"steam_id":steam_id,
				"account":{
					"name":"",
					"avatar":"",
					"hours_played":-1,
					"total_spent":-1,
					"total_achv":-1
				}
			})

	@staticmethod
	def init_game(steam_id,app_id):
		if profiles.find({"steam_id":steam_id,"games.app_id":app_id}).count() == 0 :
			profiles.update(
				{
				'steam_id':steam_id
				},
				{
				'$push':{
					"games":{
			        	"app_id":app_id,
			    		"achievements":[],
			    		"all_achv":-1,
			    		"hours_played":-1,
			    		"name":"",
			    		"price":-1,
			    		"completed_achv":-1
			        }
		        }
			})

	@staticmethod
	def update_account(steam_id,data):
		profiles.update(
			{
				'steam_id': steam_id
			},
			{
			'$set':{
				'account':data
				}
			},upsert = True)

		#76561198064586875
	@staticmethod
	def update_games(steam_id, app_id, field_name, field_data):
		#print("COUNT: " + str(profiles.find({"steam_id":steam_id,"games.app_id":app_id}).count()))
		
			#print("**********NOT INSIDE")
		profiles.update(
		{
			'games.app_id':app_id,
			'steam_id':steam_id
		},
		{
			'$set':{
				'games.$.'+field_name:field_data
			}
		},upsert = True)

	@staticmethod
	def return_account_info(steam_id):
		return profiles.find_one({"steam_id":steam_id})


	@staticmethod
	def return_game_info(steam_id,app_id):
		for game in profiles.find_one({"steam_id":steam_id},{"games":1, "games.app_id":app_id})['games']:
			if game['app_id'] == app_id:
				return game

