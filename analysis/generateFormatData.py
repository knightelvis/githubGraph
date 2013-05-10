from pymongo import MongoClient
import time


def readLanguagesDict(filename):
	f=open('output/'+filename)
	line = f.readline()
	dic={}
	while line:
		dic[line.strip()]=0
		line = f.readline()
	
	return dic

def generateData(dbname,colname,filename,langFilename):
	
	connection = MongoClient()
	db = connection[dbname]
	collection = db[colname]
	
	dic = readLanguagesDict(langFilename)
	
	f = open('output/'+filename,'w')
	f2 = open('output/'+'repo_list.txt','w')
	
	for doc in collection.find():
		langdic = dic.copy()
		
		name = doc['name']
		owner = doc['owner']
		size = doc['size']
		description = doc['description']
		open_issues = doc['open_issues']
		branch_count = len(doc['branches'])
		contributor_count = len(doc['contributors'])
		collaborator_count = len(doc['collaborators'])
		created_at = doc['created_at']
		update_at = doc['update_at']
		lang = doc['langauage']
		
		
		if len(doc['langauages'])>0:
			for key in doc['langauages'].keys():
				if key in langdic:
					langdic[key] = doc['langauages'][key]
					
		watcher_count = doc['watcher_count']
		fork_count = doc['forks_count']
		
		pattern = '%Y-%m-%d %H:%M:%S'
		epoch = int(time.mktime(time.strptime(str(created_at), pattern)))
		may8_epoch = int(time.mktime(time.strptime('2013-05-09 0:0:0', pattern)))
		
		create_differ_may8 = may8_epoch - int(time.mktime(time.strptime(str(created_at), pattern)))
		update_differ_may8 = may8_epoch - int(time.mktime(time.strptime(str(update_at), pattern)))
		update_differ_create = create_differ_may8 - update_differ_may8
		
		strg_name = doc['fullname']+'\n'
		f2.write(strg_name)
		
		strg = str(lang)+'#'+str(size)+'#'+str(open_issues)+'#' + str(branch_count)+'#'+ \
		str(contributor_count)+'#'+ str(collaborator_count) +'#'+str(create_differ_may8)+'#'+ str(update_differ_may8)+'#'+str(update_differ_create) + '#'
		
		
		for key in sorted(langdic.keys()):
			strg+= str(langdic[key])+'#'
		
		strg += str(watcher_count)+'#'+str(fork_count)+'\n'
		
		f.write(strg)
		
	f.close()
	f2.close()
	connection.close()

if __name__ == "__main__":
	#dbname = "github_commits1"
	dbname = 'githubdata14'
	colname = "repo_info"
	
	generateData(dbname,colname,'repo_data_14.txt','langs.txt')
