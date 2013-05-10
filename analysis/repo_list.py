from pymongo import MongoClient


def generateData(dbname,colname,filename):
	
	connection = MongoClient()
	db = connection[dbname]
	collection = db[colname]
	
	f = open('output/'+filename,'w')
	
	for doc in collection.find():
		
		fullname = doc['fullname']
		
		f.write(fullname+'\n')
		
	f.close()
	

if __name__ == "__main__":
	#dbname = "github_commits1"
	dbname = 'githubdata14'
	colname = "repo_info"
	
	generateData(dbname,colname,'repo_list.txt',)
