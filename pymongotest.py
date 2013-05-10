from pymongo import MongoClient

connection = MongoClient()
#connection = MongoClient('localhost', 27017)

#get the database, if it doesn't exist, it will be created automatically.
db = connection['githubdata_test']
collection_user = db['users']

print db.test.find('a')

user = {"author": "Mike", "text": "My first blog post!", "tags": ["mongodb", "python", "pymongo"], "date": datetime.datetime.utcnow()}
users = db['users']
users.insert(user)











