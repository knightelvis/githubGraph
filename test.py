#!/Library/Frameworks/Python.framework/Versions/2.7/bin/python

from pygithub3 import Github
import pygithub3
import requests
import sys
import traceback

gh = Github(login='githubdata', password='Password123')

sha = 'b15ce4a006756a0b6cacfb9593d88c9a7dfd8eb0'
user = 'rails'
repo = 'rails'
commit = gh.repos.commits.get(sha,user=user,repo=repo)

print commit.stats.total
print commit.stats.additions

parents=[]
for i in commit.parents:
	parents.append(i.sha)

print parents


'''
for file in commit.files:
	print file.filename
	print file.status
	print file.additions
	print file.deletions
	print file.changes
'''


#octocat = gh.users.get() # Auth required
#copitux = gh.users.get('copitux')

# copitux = <User (copitux)>

#octocat_followers = gh.users.followers.list().all()
#githubdata = gh.users.followers.list_following('githubdata')
#copitux_followers = gh.users.followers.list('maccman')
#print len(copitux_followers.all())
#copitux_followers = gh.users.followers.list('copitux').all()

#auth = dict(login='githubdata', password='Password123')
#gh = Github(**auth)

#octocat_repo_issues = gh.issues.list_by_repo('octocat','Hello-World')
#members=gh.orgs.members.list('Railsware')
#orgs = gh.orgs.list('iurevych')

#teams = gh.orgs.teams.list('EventStore')

#stars = gh.repos.watchers.list('adamsinger','apple_push_notification')
#stars = gh.repos.watchers.list_repos('adamsinger')
#print len(stars.all())
