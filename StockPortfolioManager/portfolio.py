#!/usr/bin/python
#
# Oracle butt-finding
#
#

oracle_base = '/raid/oracle11g/app/oracle/product/11.2.0.1.0'
oracle_sid = 'CS339'
import os;
os.putenv('ORACLE_BASE',oracle_base);
os.putenv('ORACLE_HOME',oracle_base+'/db_1');
os.putenv('ORACLE_SID','CS339');
import ctypes; ctypes.cdll.LoadLibrary(oracle_base+'/db_1/lib/libclntsh.so.11.1')

##################################################################
# -------------------------------------------------------------- #
# - Potfolio Lab :: EECS 339, Winter 2019    
# - Author: Jeremy Midvidy, jam658
# - This is the index file for my portfolio lab
# -------------------------------------------------------------- #
##################################################################

import cx_Oracle as ora
import cgi
import sys

#
# Good grief, we have to generate our own headers?  Crazy.
#
print 'Content-type: text/html\n\n'


########### ---------- BASIC HTML HEADERS ---------- ##########

print("<html>")
print("<head>")
print("<title>JM Portfolio Lab</title>")
# connect to css
print "<link href=\"portfolio.css\" type=\"text/css\" rel=\"stylesheet\">"
print "<meta charset=\"utf-8\">"
# connect to jQuery
print "<script src=\"https://code.jquery.com/jquery-3.3.1.slim.min.js\"></script>"
# connect to javascript
print "<script src=\"ref/jquery.js\" type=\"text/javascript\"></script>"
print "<script src=\"portfolio.js\" type=\"text/javascript\"></script>"
print("</head>")

con = None
## -- Initialize connection to Oracle Database -- ##
try:
	con = ora.connect("jam658/z0xM6lllV")
	con.autocommit = True
#	print "Successfully connected to Oracle<p>"
	cur = con.cursor()
	#cur.execute("")
	#rows = cur.fetchall()
	#for row in rows:
	#	print row
	#	print "<p>"

except ora.Error, e:
	print "Error %s<p>" % (e.args[0])
	sys.exit(1)


print("<body>")

# gather CGI arguments passed from the URL
arguments = cgi.FieldStorage()

     

########## ---------- BODY OF DOCUMENT ---------- ##########
print "<div id=\"login-page\">"
print "<div class=\"jumbotron\">"
print "<h1 class=\"display-3\">Welcome to your portfolio portal!</h1>"
print "<p class=\"lead\"></p>"
print "<p class=\"lead\">"
print "<hr class=\"my-4\">"
print "<div>"
print "<button onclick=\"loginLogin()\"><a class=\"btn btn-danger btn-lg\" href=\"#\" role=\"button\">Login</a></button>"
print "&emsp;&emsp;&emsp;&emsp;" 
print "<button onclick=\"loginRegister()\"><a class=\"btn btn-primary btn-lg\" href=\"#\" role=\"button\">Register</a></button>"  
print "</div>"
## - print login/regsiter hidden divs
# ---------------------------------------- #
# ---------------------------------------- #
# LOGIN form:
print "<div class=\"login-form\" style=\"display:none \"  >"
print "<div class=\"card border-danger\">"
print "<div class=\"card-header\">Please login with your email and password.</div>"
#login
print "<div class=\"card-body\">"
#email/password
print ("<div class=\"form-group\">"+
"<label for=\"exampleInputEmail1\">Email address:</label>"+
"<input type=\"email\" class=\"form-control\" id=\"exampleInputEmail1\" aria-describedby=\"emailHelp\" placeholder=\"Enter email\">"+
"</div>"+
"<div class=\"form-group\">"+
"<label for=\"exampleInputPassword1\">Password:</label>"+
"<input type=\"password\" class=\"form-control\" id=\"exampleInputPassword1\" placeholder=\"Password\">"+
"</div>")
print "<br>"
print "<button onmousedown=\"loginSubmit()\"type=\"button\" class=\"btn btn-danger\">Login!</button>"
print "</div>"                                                                                
print "</div>"                                                                                                                                                               
print "</div>"
# ---------------------------------------- #
# ---------------------------------------- #
#  REGISTER form:
print "<div class=\"register-form\" style=\"display:none \"  >"
print "<div class=\"card border-primary\">"
print "<div class=\"card-header\">Please register with your email and password.</div>"
#login
print "<div class=\"card-body\">"
#email/password
print ("<div class=\"form-group\">"+
"<label for=\"registerName\">Name:</label>"+
"<input type=\"email\" class=\"form-control\" id=\"registerName\" aria-describedby=\"emailHelp\" placeholder=\"Enter name\">"+
"</div>"+
"<div class=\"form-group\">"+
"<label for=\"exampleInputEmail2\">Email address:</label>"+
"<input type=\"email\" class=\"form-control\" id=\"exampleInputEmail2\" aria-describedby=\"emailHelp\" placeholder=\"Enter email\">"+
"</div>"+
"<div class=\"form-group\">"+
"<label for=\"exampleInputPassword2\">Password:</label>"+
"<input type=\"password\" class=\"form-control\" id=\"exampleInputPassword2\" placeholder=\"Enter password\">"+
"</div>")
print "<br>"
print "<button onmousedown=\"registerSubmit()\"type=\"button\" class=\"btn btn-primary\">Register!</button>"
# ---------------------------------------- #



print "</div>"
print "</div>"
print "</div>"
print "</div>"
# end jumbotron div
print "</div>"
# end login-page div
print "</div>"	




## - Close db connection
if con:
	con.close()

## - END HTML
print("</body>")
print("</html>")

