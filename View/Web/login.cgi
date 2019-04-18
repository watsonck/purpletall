#!/usr/bin/python
import common
import cgi

def success():
	common.header("Success")
	print("""       <p><a href='home.html'>Login Successful!</a></p>""")
	
def sorry():
	common.header("Unsuccess")
	print("""		<p><a href='login.html'>Login Unsucessful, please try again.</a></p>""")
	common.footer()

#def checkUsername():
#	form = insert table of valid usernames here
#	also figure out how to sanatize inputs
#	if not "username" in form:
#		sorry()
#		return
#	else:
#		success()common.footer()
