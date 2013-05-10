import time
import urllib2
import re
import ast
import pickle
import pygithub3
import requests
import sys
import traceback

from tempfile import mkstemp
from shutil import move
from os import remove, close
from pygithub3 import Github
from pymongo import MongoClient
from time import gmtime, strftime
from pygithub3 import Github

def removeDuplicateCommits(dbname,collection):
	
	connection = MongoClient()
	db = connection[dbname]
	userCommitsClt = db[collection]
	
	for doc in userCommitsClt.find():
		if userCommitsClt.find({'repo_name':doc['repo_name'],'sha':doc['sha']}).count() > 1:
			userCommitsClt.remove({'_id':doc['_id']})
	
	
	connection.close()
		
	
	#userCommitsClt.find({'fullname':fullname,'sha':sha}).count() == 0:
	
	 
	 
if __name__ == "__main__":
	dbname = "github_commits1"
	collection = "repo_commits"
	removeDuplicateCommits(dbname,collection)
	
	
	
	
	
