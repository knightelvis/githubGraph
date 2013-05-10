from pymongo import MongoClient



def CollaborationGraph_eachRepo(dbname,colname,repo_list):
	#construct graph based on editing the same file
	
	connection = MongoClient()
	db = connection[dbname]
	userCommitsClt = db[colname]		
	
	f = open('output/'+repo_list)
	line = f.readline()
	
	while line:
		fullname = line.strip()
		
		for commit om userCommitsClt.find({'fullname':fullname}):
			
			user = commit['committer_name']
			
			
			for file in commit['files']:
				
				
			 
		
		
		
		line = f.readline()
		
	f.close()
	connection.close()
	
	
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
	
	print g.number_of_nodes()
	print g.number_of_edges()
	nx.draw(g)
	plt.savefig("simple_path.png") # save as png
	plt.show() # display


def findFrequentEditFiles(userCommitsClt, repo, percent):

	filecount={}
	
	#users list
	user_count = len(getAllCommiters(userCommitsClt, repo))
	limit = user_count*percent
	for commit om userCommitsClt.find({'fullname':fullname}):
		
		for file in commit['files']:
			
			name = file['name']
			
			if name in filecount:
				filecount[name].add(commit['committer_name'])
			else:
				filecount[name] = set()
	
	filelist = []
	
	for key in filecount.keys():
		if len(filecount[key]) >= limit:
			filelist.append(key)
	
	return filelist
	
		
		
def getAllCommiters(userCommitsClt, repo):
	
	users={}
	for commit om userCommitsClt.find({'fullname':repo}):
			user = commit['committer_name']
		if user in users:
			users[user] += 1
		else:
			users[user] = 1
		
	return sorted(users.keys())




if __name__ == "__main__":
	dbname = "githubdata14"
	colname = "repo_commits"
	repo_list= 'repo_list_14.txt'
	
	
	CollaborationGraph_eachRepo(dbname,colname,repo_list)
	
	
