from pymongo import MongoClient
import networkx as nx
import matplotlib.pyplot as plt

def findAllLangs(dbname,colname,outputFilename):
	
	connection = MongoClient()
	db = connection[dbname]
	collection = db[colname]
	
	lang = {}
	total = 0
	nolang = 0
	for doc in collection.find():
		total += 1
		temp = doc['langauages']
		
		if len(temp)>0:
			
			for key in temp.keys():
				if key in lang:
					lang[key] += 1
				else:
					lang[key] = 1
		else:
			nolang += 1
			#print doc['fullname']
		
	print 'total:' + str(total)
	print 'nolang:' + str(nolang)
	outputToFile(lang,outputFilename)
	

def outputToFile(dic, filename):
	f = open('output/'+filename,'w')
	
	for key in sorted(dic.keys()):
		if dic[key]>=0:
			f.write(key+'\n')

	f.close()


if __name__ == "__main__":
	dbname = "github_commits2"
	colname = "repo_info"
	
	findAllLangs(dbname,colname,'github_commits2_langs.txt')
	
