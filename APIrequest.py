import urllib2
import re
import ast

def getrate():

    u='githubdata'
    p='Password123'
    url='https://api.github.com/rate_limit'


    # create the request object and set some headers
    req = urllib2.Request(url)
    req.add_header('Accept', 'application/json')
    req.add_header("Content-type", "application/x-www-form-urlencoded")
    req.add_header('Authorization', encodeUserData(u, p))
    # make the request and print the results
    res = urllib2.urlopen(req)

    print ast.literal_eval(res.read())['rate']['remaining']
    #print re.search('(?<=\"remaining\":)\w+',str(res.read())).group(0)

# simple wrapper function to encode the username & pass
def encodeUserData(user, password):
    return "Basic " + (user + ":" + password).encode("base64").rstrip()



if __name__ == '__main__':
	getrate();
