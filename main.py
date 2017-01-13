#!/usr/bin/python3.5

#This program was made to upload html files to any
#WordPress site given it has the wp-api plugin and Oauth 2.0 Server installed.
#Copyright (C) 2017  Jonathan Newton

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.


from collections import defaultdict
import getpass
import sys
import configparser
import re
import os.path
import http.client
import json
import time
import fnmatch
import requests
import urllib3
urllib3.disable_warnings()
#These can be change to change the settings

# It is best to have an encrypted file with the user data in it.
# class get_usr_data

# user name and pass
# oauth client_id and secret

cfg_name = 'config.ini'

def get_usr_data():
	config = configparser.ConfigParser()
	config['DEFAULT'] = {}
	config['DEFAULT']['grant_type'] = 'password'
	config['OAUTH'] = {}
	config['OAUTH']['client_id'] = input("Enter the oauth client id:")
	config['OAUTH']['client_secret'] = input("Enter the oauth client secret:")
	config['OAUTH']['username'] = input("Enter the wordpress username:")
	config['OAUTH']['password'] = getpass.getpass("Enter the wordpress password:")
	config['OAUTH']['cycle_buffer'] = 1
	config['WP_SITE'] = {}
	config['WP_SITE']['url'] = input("Enter the wordpress site URL:")
	
	with open(cfg_name, 'w') as configfile:
		config.write(configfile)


class OAUTH():
	def __init__(self):
		config = configparser.ConfigParser()
		config.read(cfg_name)
		conn = http.client.HTTPSConnection(config['WP_SITE']['url'])
		payload = "client_id=" + config['OAUTH']['client_id'] + "&client_secret=" + config['OAUTH']['client_secret'] + "&grant_type=" + config['DEFAULT']['grant_type'] + "&username=" + config['OAUTH']['username'] + "&password=" + config['OAUTH']['password']
		headers = {
			'content-type': "application/x-www-form-urlencoded",
			'cache-control': "no-cache",
			'postman-token': "62ca314e-ce83-efe2-43dd-8b69b56f8773"
			}

		conn.request("POST", "/oauth/token", payload, headers)
		res = conn.getresponse()
		data = res.read()
		self.jdata = data.decode("utf-8")
		self.authv = json.loads(self.jdata)
		self.datecheck =  time.time() + self.authv["expires_in"] - (float(config['OAUTH']['cycle_buffer']) * 60)
	def cycle(self):
		if time.time() > self.datecheck:
			self.__init__()
			return(self.authv["access_token"])
	def count_down(self):
		print(str(self.authv["access_token"] + " good for {0:.2f}".format((self.datecheck - time.time()) / 60)) + " Minutes", end="\r")

# Parent needs to be set if there is a parent, 
# and if parent is null then the https call needs to not have that value.

def main():
	if not os.path.exists(cfg_name):
		get_usr_data()
	auth = OAUTH()
	while 1 > 0:
		token = auth.cycle()
		auth.count_down()
		
main()
