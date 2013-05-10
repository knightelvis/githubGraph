from pymongo import MongoClient
import networkx as nx
import matplotlib.pyplot as plt

def appendToQueue(users):
	
	#remove the duplicates in users
	dic = {}
	f = open('repo_list.txt', 'a')
	for user in users:
		if dic.has_key(user):
			continue
		else:
			dic[user] = 1
		if not checkUserQueue(user):
			f.write('#'+str(user)+'#0'+'\n')
	
	f.close()

def checkUserQueue(user):
	f = open('repo_list.txt', 'r')
	line = f.readline();
	while line:

		lineSegments = line.split('#')
		login = lineSegments[1].strip()
		if login == user:
			return True
		
		line = f.readline()
	f.close()
	return False
	
def log(content):
	f = open('runing_logs','a')
	#get GMT time as a string
	strTime = strftime("%Y-%m-%d %H:%M:%S")
	entry = strTime + '  ' + content + '\n'
	f.write(entry)
	f.close()
	


	
def CollaborationGraph_eachRepo(dbname,colname,repo):
	#construct graph based on editing the same file
	
	connection = MongoClient()
	db = connection[dbname]
	userCommitsClt = db[colname]		
	
	
	connection = {}
	count = 0
	for doc in userCommitsClt.find({'fullname':repo}):
		count += 1
		
		for file in doc['files']:
			if file['name'] in connection:
				connection[file['name']].append(doc['committer_name'])
			else:
				connection[file['name']] = [doc['committer_name']]
	
	g = nx.Graph()
	
	for key in connection.keys():
		if len(connection[key])==1:
			g.add_node(connection[key][0])		
		else:
			for i in range(len(connection[key])-1):
				for j in range(i+1,len(connection[key])):
					g.add_edge(connection[key][i],connection[key][j])
	
	connection.close()
	print g.number_of_nodes()
	print g.number_of_edges()
	nx.draw(g)
	plt.savefig("simple_path.png") # save as png
	plt.show() # display

	
def findTopEditedFiles(dbname,colname,):
	
	
	pass
		
	
	
	 
if __name__ == "__main__":
	dbname = "githubdata14"
	colname = "repo_info"
	
	CollaborationGraph_eachRepo(dbname,colname,'elasticsearch')
	#test()
