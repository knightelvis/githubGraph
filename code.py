'''For air'''
'''#!/Library/Frameworks/Python.framework/Versions/2.7/bin/python'''

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

def encodeUserData(user, password):
    # simple wrapper function to encode the username & pass
    return "Basic " + (user + ":" + password).encode("base64").rstrip()

def getRate(account, passw):
	u=account
	p=passw
	url='https://api.github.com/rate_limit'
	
	# create the request object and set some headers
	log('----getRate::Begin to get rate')
	req = urllib2.Request(url)
	req.add_header('Accept', 'application/json')
	req.add_header("Content-type", "application/x-www-form-urlencoded")
	req.add_header('Authorization', encodeUserData(u, p))
	
	times=0

	while(True):
		times += 1
		try:
			# make the request and print the results
			res = urllib2.urlopen(req)
			break
		except urllib2.HTTPError as he:
			if times >20:
				log('----urllib2.HTTPError@urllib2.urlopen(req):#'+account)
				
				#print '----urllib2.HTTPError@urllib2.urlopen(req):#'+account
				sys.exit()
			time.sleep(3)
			continue
						
	#print re.search('(?<=\"remaining\":)\w+',str(res.read())).group(0)
	rate = ast.literal_eval(res.read())['rate']['remaining']
	log('**remaining rate: '+str(rate)+'**')
	#print '**remaining rate: '+str(rate)+'**'
	return rate
    
def isrunning():
    #Used to kill the running program.
    # 1 means keep running
    # 0 means stop running
    f = open('signal.txt', 'r')
    flag=int(f.readline().strip())
    f.close()
    return flag==1;

def log(content):
	f = open('running_logs','a')
	#get GMT time as a string
	strTime = strftime("%Y-%m-%d %H:%M:%S")
	entry = strTime + '  ' + content + '\n'
	f.write(entry)
	f.close()

def getCandidateFromFile():
	f = open('userQueue.txt', 'r')
	line = f.readline();
	
	user = '@' #It means no more users in the queue
	while line:
		
		'''every line is like login#0, 1 means visited, 0 means not visited yet'''
		lineSegments = line.split('#')
		login = lineSegments[1].strip()
		status = lineSegments[2].strip()
		
		if int(status) == 1:
			line = f.readline();
			continue
		elif int(status) == 0:
			user = login
			break
		else:
			log('--getCandidateFromFile::Wrong User Queue Format!')
		
		line = f.readline();
	
	f.close()
	log ('--getCandidateFromFile::Get the User: '+ user)
	#If user =='@', it means the queue is empty
	return user

def changeACandidateStatus(user,status):

	file_path = 'userQueue.txt'
	pattern = '#'+user+'#'+'0'
	subst = '#'+user+'#'+str(status)
	#Create temp file
	fh, abs_path = mkstemp()
	new_file = open(abs_path,'w')
	old_file = open(file_path)
	for line in old_file:
		new_file.write(line.replace(pattern, subst))
	#close temp file
	new_file.close()
	close(fh)
	old_file.close()
	#Remove original file
	remove(file_path)
	#Move new file
	move(abs_path, file_path)
	log ('--Change Successfully')

def checkUserQueue(user):
	f = open('userQueue.txt', 'r')
	line = f.readline();
	while line:

		lineSegments = line.split('#')
		login = lineSegments[1].strip()
		if login == user:
			return True
		
		line = f.readline()
	f.close()
	return False

def removeDuplicates(users):
	f = open('userQueue.txt', 'r')
	line = f.readline();
	
	if len(users)==0:
		return []
	
	while line:

		lineSegments = line.split('#')
		login = lineSegments[1].strip()
		if login in users:
			users.remove(login)
			
		line = f.readline()
	f.close()
	return users

def appendToQueue(users):
	
	if len(users)==0:
		return
	
	#remove the duplicates in users
	users = removeDuplicates(users)
	if len(users)==0:
		return
		
	f = open('userQueue.txt', 'a')
	for user in users:
		f.write('#'+str(user)+'#0'+'\n')
	
	f.close()
	log ('--Add Users Successfully')
	
def getUserInfo(gh,seedUserLogin,dbname):
	#get the seed users
	try:
		times=0
		while(True):
			times += 1
			try:
				user_info = gh.users.get(seedUserLogin)
				break
			except requests.exceptions.HTTPError as he:
				if times >10:
					log('----requests.exceptions.HTTPError@gh.users.get:#'+seedUserLogin)
					#remove this user from userQueue!
					changeACandidateStatus(seedUserLogin,2)
					return False
				time.sleep(3)
				continue
				
	except pygithub3.exceptions.NotFound as nf:
		log('----pygithub3.exceptions.NotFound@gh.users.get:#'+seedUserLogin)
		#remove this user from userQueue!
		changeACandidateStatus(seedUserLogin,2)
		log('----Removed user:' + seedUserLogin) 
		return False
		
	uId = user_info.id
	uLogin = user_info.login
	uCreate = user_info.created_at
	uFollowing = user_info.following
	uFollowers = user_info.followers
	uGists  = user_info.public_gists
	uRepos = user_info.public_repos
	
	try:
		uType = user_info.type	
	except AttributeError as ae:
		uType = ''
		
	try:
		uName = user_info.name	
	except AttributeError as ae:
		uName = ''
	
	try:
		uEmail = user_info.email	
	except AttributeError as ae:
		uEmail = ''
	try:
		uBio = user_info.bio	
	except AttributeError as ae:
		uBio = ''	
		
	try:
		uCompany = user_info.company	
	except AttributeError as ae:
		uCompany = ''		
	try:
		uLocation = user_info.location	
	except AttributeError as ae:
		uLocation = ''	
	try:
		uHireable = user_info.hireable	
	except AttributeError as ae:
		uHireable = ''		
	
	log ('--getUserInfo::Successfully get users info')
	doc = {'id':uId, 'login':uLogin, 
		'created_at':uCreate, 
		'following': uFollowing, 
		'followers':uFollowers, 
		'public_gists': uGists, 
		'public_repos':uRepos, 
		'name':uName, 
		'email':uEmail,
		'bio':uBio,
		'location':uLocation,
		'company':uCompany,
		'hireable':uHireable,
		'type':uType}
    
	#MongoDB Connection
	connection = MongoClient()
	db = connection[dbname]
	userInfoClt = db['user_info']
	log ('--getUserInfo::Begin to add the user record into MongoDB')
	#print '--getUserInfo::Begin to add the user record into MongoDB'
	
	if userInfoClt.find({'login':uLogin}).count() == 0:
		userInfoClt.insert(doc)	
	
	connection.close()
	return True
	
	
def getUsersRepoInfo(gh,seedUserLogin,dbname):

	try:
		times=0
		while(True):
			times += 1
			try:
				seed_repos = gh.repos.list(seedUserLogin)
				break
			except requests.exceptions.HTTPError as he:
				if times >5:
					log('----requests.exceptions.HTTPError@gh.repos.list:#'+seedUserLogin)
					seed_repos=[]
					break
				time.sleep(3)
				continue
				
	except pygithub3.exceptions.NotFound as nf:
		seed_repos=[]

	
	repo_all =[]
	repo_nonfork={}
	users = []
	
	for repo in seed_repos.all():
		
		
		rID = repo.id
		rName = repo.name
		rFork = repo.fork
		rCreate = repo.created_at
		rOwner = repo.owner.login
		rFullName = repo.owner.login+'#'+repo.name
		rPrivate = repo.private
		rDesp = repo.description
		rLan = repo.language
		rForksCount = repo.forks_count
		rWatchersCount = repo.watchers_count
		rSize = repo.size
		rIssues = repo.open_issues
		rPush = repo.pushed_at
		rUpdate = repo.updated_at
		
		#couldn't get these attributes right now
		#print repo.parent
		#print repo.source
		
		#MongoDB Connection
		connection = MongoClient()
		db = connection[dbname]
		repoInfoClt = db['repo_info']
		if repoInfoClt.find({'fullname':rFullName}).count() > 0:
			connection.close()
			continue
		connection.close()
		
		collaborators = []
		tags = []
		contributors = []
		forks = []
		langs = []
		branches =[]
		
		try:
			times=0
			while(True):
				times += 1
				try:
					colset = gh.repos.collaborators.list(user=rOwner, repo=rName).all()
					break
				except requests.exceptions.HTTPError as he:
					if times >5:
						log('----requests.exceptions.HTTPError@gh.repos.collaborators.list:#'+rOwner+'#'+rName)
						colset=[]
						break
					time.sleep(3)
					continue
				
		except pygithub3.exceptions.NotFound as nf:
			colset=[]
			
		for coll in colset:
			collaborators.append(coll.login)
		'''
		try:
			times=0
			while(True):
				times += 1
				try:
					tagset = gh.repos.list_tags(user=rOwner, repo=rName).all()
					break
				except requests.exceptions.HTTPError as he:
					if times >5:
						log('----requests.exceptions.HTTPError@gh.repos.list_tags:#'+rOwner+'#'+rName)
						tagset=[]
						break
					time.sleep(3)
					continue
				
		except pygithub3.exceptions.NotFound as nf:
			tagset=[]
		except AttributeError as ab:
			tagset=[]
		
		for tag in tagset:
			tags.append(tag.name)
		'''
		try:
			times=0
			while(True):
				times += 1
				try:
					conset = gh.repos.list_contributors_with_anonymous(user=rOwner, repo=rName).all()
					break
				except requests.exceptions.HTTPError as he:
					if times >5:
						log('----requests.exceptions.HTTPError@gh.repos.list_contributors_with_anonymous:#'+rOwner+'#'+rName)
						conset=[]
						break
					time.sleep(3)
					continue
				
		except pygithub3.exceptions.NotFound as nf:
			conset=[]
			
		for contr in conset:
			contributors.append(contr.login)
		
		try:
			times=0
			while(True):
				times += 1
				try:
					forkset = gh.repos.forks.list(user=rOwner, repo=rName, sort='newest').all()
					break
				except requests.exceptions.HTTPError as he:
					if times >5:
						log('----requests.exceptions.HTTPError@gh.repos.forks.list:#'+rOwner+'#'+rName+'#'+'newest')
						forkset=[]
						break
					time.sleep(3)
					continue
				
		except pygithub3.exceptions.NotFound as nf:
			forkset=[]
					
		for fork in forkset:
			try:
				forks.append(fork.owner.login+'#'+fork.name)
			except AttributeError as ab:
				continue
				
				
		#list_languages will return a dictionary not a result set
		try:
			times=0
			while(True):
				times += 1
				try:
					langs = gh.repos.list_languages(user=rOwner, repo=rName)
					break
				except requests.exceptions.HTTPError as he:
					if times >5:
						log('----requests.exceptions.HTTPError@gh.repos.list_languages:#'+rOwner+'#'+rName)
						langs=[]
						break
					time.sleep(3)
					continue
				
		except pygithub3.exceptions.NotFound as nf:
			langs={}
		#langs.append(pickle.dumps(lan))
		
		
		try:
			times=0
			while(True):
				times += 1
				try:
					branchset = gh.repos.list_branches(user=rOwner, repo=rName).all()
					break
				except requests.exceptions.HTTPError as he:
					if times >5:
						log('----requests.exceptions.HTTPError@gh.repos.list_branches:#'+rOwner+'#'+rName)
						branchset=[]
						break
					time.sleep(3)
					continue
				
		except pygithub3.exceptions.NotFound as nf:
			branchset=[]

		for branch in branchset:
			branches.append(branch.commit.sha)	
		
		
		
		doc = {'id':rID, 'name':rName, 'fullname':rFullName,
		'created_at':rCreate, 
		'fork': rFork, 
		'owner':rOwner, 
		'private': rPrivate, 
		'description':rDesp, 
		'langauage':rLan,
		 'forks_count':rForksCount,
		 'watcher_count':rWatchersCount,
		 'size':rSize,
		 'open_issues':rIssues,
		 'push_at':rPush,
		 'update_at':rUpdate,
		 'tags': tags,
		 'contributors':contributors,
		 'forks':forks,
		 'langauages':langs,
		 'collaborators':collaborators,
		 'branches':branches
		 }
	
		users = contributors + collaborators
		
		#MongoDB Connection
		connection = MongoClient()
		db = connection[dbname]
		repoInfoClt = db['repo_info']
		
		if repoInfoClt.find({'fullname':rFullName}).count() == 0:
			repoInfoClt.insert(doc)
		
		connection.close()
		
		repo_all.append(repo.name)
		if not rFork:
			repo_nonfork[repo.name] = branches
			
		
	return {'repo_all':repo_all,'repo_nonfork':repo_nonfork, 'users':users}
	
def getUserRelations(gh,seedUserLogin,dbname):
	
	connection = MongoClient()
	db = connection[dbname]
	userRelationsClt = db['user_relations']
	
	if userRelationsClt.find({'login':seedUserLogin}).count() > 0:
		return []
		
	try:
		times=0
		while(True):
			times += 1
			try:
				ufollowings = gh.users.followers.list_following(seedUserLogin).all()
				break
			except requests.exceptions.HTTPError as he:
				if times >5:
					log('----requests.exceptions.HTTPError@gh.users.followers.list_following:#'+seedUserLogin)
					ufollowings=[]
					break
				time.sleep(3)
				continue
				
	except pygithub3.exceptions.NotFound as nf:
		ufollowings=[]

	try:
		times=0
		while(True):
			times += 1
			try:
				ufollowers = gh.users.followers.list(seedUserLogin).all()
				break
			except requests.exceptions.HTTPError as he:
				if times >5:
					log('----requests.exceptions.HTTPError@gh.users.followers.list:#'+seedUserLogin)
					ufollowers=[]
					break
				time.sleep(3)
				continue
				
	except pygithub3.exceptions.NotFound as nf:
		ufollowers=[]
		
	followers=[]
	followings=[]
	
	for user in ufollowings:
		followings.append(user.login)
		
	for user in ufollowers:
		followers.append(user.login)
	
	doc = {'login':seedUserLogin, 'followers':followers, 'followings':followings}
	userRelationsClt.insert(doc)
	connection.close()
	
	return followers + followings

def getWathers(gh,owner,repos,dbname):
	
	return_users = []
	for repo in repos:
		
		fullname = owner+'#'+repo
		connection = MongoClient()
		db = connection[dbname]
		userRelationsClt = db['repo_watchers']
		
		if userRelationsClt.find({'fullname':fullname}).count() > 0:
			connection.close()
			continue
		
		#owner,repo_name = repo.split('#')
		users =[]
		
		try:
			times=0
			while(True):
				times += 1
				try:
					watcherset = gh.repos.watchers.list(user=owner, repo=repo).all()
					break
				except requests.exceptions.HTTPError as he:
					if times >5:
						log('----requests.exceptions.HTTPError@gh.repos.watchers.list:#'+owner+'#'+repo)
						watcherset=[]
						break
					time.sleep(3)
					continue
				
		except pygithub3.exceptions.NotFound as nf:
			continue
		
		
		for user in watcherset:
			users.append(user.login)

		doc = {'owner':owner, 'repo_name':repo, 'fullname':fullname, 'watchers':users}
		
		userRelationsClt.insert(doc)
		connection.close()
		
		#return_users = return_users + users
	
	return

def getUsersReposCommitInfo(gh,owner,repos,dbname):
	
	for repo,branches in repos.items():
		
		connection = MongoClient()
		db = connection[dbname]
		userCommitsClt = db['repo_commits']
		fullname = owner+'#'+repo
		
		for branch in branches:
			
			try:
				times=0
				while(True):
					times += 1
					try:
						commitset = gh.repos.commits.list(user=owner, repo=repo,sha=branch).all()
						break
					except requests.exceptions.HTTPError as he:
						if times >5:
							log('----requests.exceptions.HTTPError@gh.repos.commits.list:#'+owner+'#'+repo+'#'+sha)
							commitset=[]
							break
						time.sleep(3)
						continue
				
			except pygithub3.exceptions.NotFound as nf:
				continue	
		
			bulk=[]
			i=0
			for commit in commitset:
				i += 1
				date = commit.commit.committer.date
				msg = commit.commit.message
				sha = commit.sha
				committer_name = commit.commit.committer.name
				email = commit.commit.committer.email
			
				try:
					committer = commit.committer.login
				except AttributeError as ae:
					committer = ''
				
				doc = {'owner':owner, 'repo_name':repo, 
				'fullname':fullname,
				'branch':branch,
				'date': date, 
				'message':msg, 
				'sha':sha, 
				'committer_login':committer, 
				'committer_name':committer_name,
				'email':email}
			
				bulk.append(doc)
			
				if i > 7000:
					userCommitsClt.insert(bulk)
					i=0
					bulk=[]
			
			if len(bulk) != 0:
				userCommitsClt.insert(bulk)
		
		connection.close()


def getUsersReposPullRequest(gh,owner,repos,state_str):
	
	for repo in repos:
		fullname = owner+'#'+repo
			
		try:
			times=0
			while(True):
				times += 1
				try:
					prset = gh.pull_requests.list(state=state_str,user=owner,repo=repo).all()
					break
				except requests.exceptions.HTTPError as he:
					if times >5:
						log('----requests.exceptions.HTTPError@gh.pull_requests.list:#'+state_str+'#'+owner+'#'+repo)
						prset=[]
						break
					time.sleep(3)
					continue
				
		except pygithub3.exceptions.NotFound as nf:
			continue		
		
		connection = MongoClient()
		db = connection['githubdata']
		clt = db['pullrequest_commits']
		pullRequestClt = db['repo_pullrequests']
		
		for pr in prset:
		
			number = pr.number
			state = pr.state
			title = pr.title
			body = pr.body
			create = pr.created_at
			update = pr.updated_at
			close = pr.closed_at
			if pr.user != None:
				user = pr.user['login']
			else:
				user=''
				
			doc = {'owner':owner, 'repo_name':repo, 'fullname':fullname,'number': number, 'state':state, 'title':title, 'body':body, 'created_at':create, 'updated_at':update, 'closed_at':close,'user':user}
			
			#if pullRequestClt.find({'fullname':fullname, 'number':number}).count()==0:
			pullRequestClt.insert(doc)
			
			try:
				times=0
				while(True):
					times += 1
					try:
						prcset = gh.pull_requests.list_commits(number,user=owner,repo=repo).all()
						break
					except requests.exceptions.HTTPError as he:
						if times >5:
							log('----requests.exceptions.HTTPError@gh.pull_requests.list_commits:#'+str(number)+'#'+owner+'#'+repo)
							prcset=[]
							break
						time.sleep(3)
						continue
				
			except pygithub3.exceptions.NotFound as nf:
				continue	
			
			for commit in prcset:
				date = commit.commit['committer']['date']
				committer_name = commit.commit['committer']['name']
				email = commit.commit['committer']['email']
				msg = commit.commit['message']
				sha = commit.sha
				
				try:
					committer = commit.committer.login
				except AttributeError as ae:
					committer = ''

				doc = {'owner':owner, 'repo_name':repo, 'fullname':fullname,'number':number ,'date': date, 'message':msg, 'sha':sha, 'committer_login':committer, 'committer_name':committer_name,'email':email}
				
				#if clt.find({'sha':sha})==0:
				clt.insert(doc)
			
		connection.close()
			

def getUsersReposIssues(gh,seedUserLogin,repo):
	#the library doesn'r support this function
	pass
	

if __name__ == "__main__":
    
	log('**********Crawler Started!**********')
		
	name = ['githubdata','githubdata2','githubdata3','githubdata4','githubdata5','githubdata6','githubdata7','githubdata8']
	pasw = ['Password123','Password123','Password123','Password123','Password123','Password123','Password123','Password123']
		
	idx = 5
	flag = False
	
	#log('------Login Github')
	#gh = Github(login=name[idx%len(name)], password=pasw[idx%len(name)])

	log('------Get the First User')
	seedUserLogin = getCandidateFromFile()

	log('------Start Crawling!')
	number = 1
	
	dbname = 'githubdata10'
	
	while(isrunning()):
		try:	
			
			while seedUserLogin != '@':
				
				if not isrunning():
					log('********User Broke Running*******')
					break
							
				idx += 1
				
				#Check rate
				while int(getRate(name[idx%len(name)],pasw[idx%len(name)]))<1000:
					#print name[idx%4]
					flag = True
					idx += 1
				'''
				if flag:
					flag = False
					gh = Github(login=name[idx%len(name)], password=pasw[idx%len(name)])
				'''
				#print name[idx%len(name)]
				
				gh = Github(login=name[idx%len(name)], password=pasw[idx%len(name)])	
				
				log('------Get User Info!')
				#print '------Get User Info! '+ seedUserLogin
				
				isGet = getUserInfo(gh,seedUserLogin,dbname)
				
				#If the user is cannot be got
				if not isGet:
					seedUserLogin = getCandidateFromFile()
					continue
				
				time.sleep(1)
				log('------Get User Relations!')
				#print '------Get User Relations!'
				userslist1 = getUserRelations(gh,seedUserLogin,dbname)
				time.sleep(1)
				log('------Get User Repo Info!')
				#print '------Get User Repo Info!'
				repos = getUsersRepoInfo(gh,seedUserLogin,dbname)
				time.sleep(1)
			
				log('------Get Watchers!')
				#print '------Get Watchers!'
				getWathers(gh,seedUserLogin,repos['repo_all'],dbname)
				
				
				#Check rate
				while int(getRate(name[idx%len(name)],pasw[idx%len(name)]))<800:
					flag = True
					idx += 1
				
				if flag:
					flag = False
					gh = Github(login=name[idx%len(name)], password=pasw[idx%len(name)])				
				
				time.sleep(1)
				log('------Get Repos Commits!')
				#print '------Get Repos Commits!'
			
				getUsersReposCommitInfo(gh,seedUserLogin,repos['repo_nonfork'],dbname)
				time.sleep(1)

				'''
				while int(getRate())<500:
					time.sleep(300)
			
				log('------Get Repos Pull Requests-open!')
				print '------Get Repos Pull Requests-open!'
				getUsersReposPullRequest(gh,seedUserLogin,repos,'open')
				time.sleep(1)
				log('------Get Repos Pull Requests-closed!')
				print '------Get Repos Pull Requests-closed!'
				getUsersReposPullRequest(gh,seedUserLogin,repos,'closed')
				time.sleep(1)
				'''
			
				#log('------Append New Users!')
				#print '------Append New Users!'
				#appendToQueue(list(set(userslist1 + repos['users'])))
			
				log('------Update Current User Status!')
				#print '------Update Current User Status!'
				changeACandidateStatus(seedUserLogin,1)
			
				log('------Successfully Crawled user: '+str(number))
			
				log('------Get Next Candidate!')
				#print '------Get Next Candidate!'
				seedUserLogin = getCandidateFromFile()
			
				repos=[]
				userslist1=[]
				
				#print '------Successfully Crawled user: '+str(number)
				number += 1
		    
		except Exception,error:
			exc_type, exc_value, exc_traceback = sys.exc_info()
			log(repr(traceback.format_exception(exc_type, exc_value,exc_traceback)))
			seedUserLogin = getCandidateFromFile()
			time.sleep(5)
			continue
		
		
		
