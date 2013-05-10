import pickle
from pygithub3 import Github
from pymongo import MongoClient
'''
connection = MongoClient()

db = connection['githubdata_test']
db.drop_collection('users')
collection_user = db['users']

gh = Github(login='githubdata', password='Password123')

seed_users = gh.users.followers.list_following('githubdata')

print len(seed_users.all())


i=0
for user in seed_users.all():
	print user.login
	strg = pickle.dumps(user)
	entry = {'userobj':strg}
	print entry
	print collection_user.insert(entry)
	i+=1
	print i


i=0
for user in collection_user.find():
	print i
	i += 1
	usertemp = pickle.loads(user['userobj'])	
	print usertemp.login
'''

a={"a":1,"b":2,"c":3}

f = open('testpickle','a')

for i in range(0,10):
	f.write(pickle.dumps(a))
f.close()




