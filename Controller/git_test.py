from git import Git

path = '/home/purpletall/purpletall'
datetime='2019-03-30 12:00:00'

g = Git(path) 
loginfo = g.log('--since='+datetime,'--name-only')
print(loginfo)
