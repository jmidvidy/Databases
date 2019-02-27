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
# - This is the PORTFOLIO REVIEW PAGE for my main file
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
    #print "Successfully connected to Oracle<p>"
    cur = con.cursor()
    #cur.execute("")
    #rows = cur.fetchall()
    #for row in rows:
    #print row
    #print "<p>"

except ora.Error, e:
    print "Error %s<p>" % (e.args[0])
    sys.exit(1)


print("<body>")

########## ---------- GATHER CGI ARGUMENTS ---------- ##########
def DBexit():
    if con:
        con.close()
    exit()

arguments = cgi.FieldStorage()
act = ""
email = ""
password = ""
name = ""
newPortName = ""
if arguments:
    act = arguments["act"].value
    email = arguments["email"].value
    try:
        password = arguments["password"].value
    except:
        pass
    if act == "register":
        name = arguments["name"].value
    try:
        newPortName = arguments["addPortfolio"].value
    except:
        pass

#print "<h4>" + str([act, email, password, name, newPortName]) + "</h4>"
###################################################################################################
# ----------------------------------------------------------------------------------------------- #
#                                     ERROR HANDLING                                              #

########## ---------- CONFIRM LOGIN ---------- ##########
def loginFailure(code):
    error_message = ""
    if code == 1:
        error_message = "Email address not found in database."
    elif code == 2:
        error_message = "Email address/password combination incorrect."

    print("<div class = \"login-failure\">"+
"<div class=\"card text-white bg-danger mb-3\">"+
          "<div class=\"card-header\">Error!</div>"+
          "<div class=\"card-body\">"+
          "<h4 class=\"card-title\">Login Attempt Failed</h4>"+
          "<p class=\"card-text\">" + error_message +  "  Please return to the homepage and try again.</p>"+
          "<br><br> <button onmousedown=\"returnToHomePage()\"  type=\"button\" class=\"btn btn-secondary\">Return to Home Page</button>" +
          "</div>"+ "</div>" +           "</div>")
    return

if act == "login" or act == "back":
    try:
        #print "<p>" + "email: "+ email + "</p>"
        query = "select * from portfolio_users where email=\'" + email + "\'"
        cur.execute(query)
        # fetch rows - should just be a single row
        rows = cur.fetchall()
        #print("<p>SQL debug</p>")
        # no row with that login, produce loginFailure and return
        if not rows:
            #print "&emsp;no rows"
            loginFailure(1)
            DBexit()
        #else:
        #    print "<p>"
        #    print rows[0]
        #    print "</p>"

        #password must match
        tuples = rows[0]
        db_password = tuples[1]
        if db_password != password and act != "back":
            loginFailure(2)
            DBexit()

    except ora.Error, e:
        print "SQL ERROR!"
        print "Errir %s<p>" % (e.args[0])
        print "<p>"


########## ---------- CONFIRM NEW PORTFOLIO ---------- ##########
def addPortfolioFailure():
    error_message = "User already has a portfolio by that name.  Please use an unused name for a new portfolio."
    ret_url = "?act=back&email=" + email + "&password=" + password
    print("<div class = \"login-failure\">"+
          "<div class=\"card text-white bg-danger mb-3\">"+
          "<div class=\"card-header\">Error!</div>"+
          "<div class=\"card-body\">"+
          "<h4 class=\"card-title\">Add portfolio attempt failed!</h4>"+
          "<p class=\"card-text\">" + error_message +  "  Please return to the homepage and try again.</p>"+
          "<br><br> <button onmousedown=\"returnToPortPage("+ "\'"   + ret_url + "\'"  +")\"  type=\"button\" class=\"btn btn-secondary\">Return to Portfolio Page</button>" +
          "</div>"+ "</div>" +           "</div>")

    exitDB();
    return

def addPortfolioSuccess():
    error_message = "Successfully added portolio to the database!"
    ret_url = "?act=back&email=" + email + "&password=" + password
    print("<div class = \"login-failure\">"+
          "<div class=\"card text-white bg-primary mb-3\">"+
          "<div class=\"card-header\">Success!</div>"+
          "<div class=\"card-body\">"+
          "<h4 class=\"card-title\">Portfolio successfully added!</h4>"+
          "<p class=\"card-text\">" + error_message +  "  Please return to the portolio create and view page to access the new portfolio..</p>"+
          "<br><br> <button onmousedown=\"returnToPortPage("+ "\'"   + ret_url + "\'"  +")\"  type=\"button\" class=\"btn btn-secondary\">Return to Portfolio Page</button>" +
          "</div>"+ "</div>" +           "</div>")

    exitDB();
    return

if newPortName != "":
    val_email = "" + "\'" + email + "\'"
    val_portName = "" + "\'" + newPortName + "\'"
    vals = "(" + val_email + ", " + val_portName + ")"
    query1 = "insert into portfolio_list values " + vals
    try:
        cur.execute(query1)
        # curr.execute("select * from portfolio_list") still not working here
        # add email-portfolio to databaces
        val_key = "\'" + email + "_" + newPortName + "\'"
        vals = "(" + val_key + ")"
        query2 = "insert into portfolio_balance (portfolioID) values " + vals
        cur.execute(query2)
        addPortfolioSuccess()
    except ora.Error, e:
        # since login is already success, any error must be using
        # a portfolio name that already exists
        print "SQL ERROR!"
        print "Errir %s<p>" % (e.args[0])
        print "<p>"
        addPortfolioFailure()




########## ---------- CONFIRM REGISTRATION ---------- ##########
def registerFailure():
    error_message = "Unable to register with that email.  Either email poorly formatted or already in database."
    print("<div class = \"login-failure\">"+
"<div class=\"card text-white bg-danger mb-3\">"+
          "<div class=\"card-header\">Error!</div>"+
          "<div class=\"card-body\">"+
          "<h4 class=\"card-title\">Registration Attempt Failed</h4>"+
          "<p class=\"card-text\">" + error_message +  "  Please return to the homepage and try again.</p>"+
          "<br><br> <button onmousedown=\"returnToHomePage()\"  type=\"button\" class=\"btn btn-secondary\">Return to Home Page</button>" +
          "</div>"+ "</div>" +           "</div>")

    exitDB()
    return

if act == "register":
    try:
        val_name = "" + "\'" + name + "\'"
        val_password = "" + "\'" + password + "\'"
        val_email = "" + "\'" + email + "\'"
        vals = "(" + val_name + ", " + val_password + ", " + val_email + ")"
#        print "<p>" + vals + "</p>"
        query = "insert into portfolio_users values " + vals
 #       print "<p>" + query + "</p>"
        cur.execute(query)        
        cur.execute("select * from portfolio_users")
        rows = cur.fetchall()
  #      for row in rows:
   #         print "<p>" + str(row) + "</p>"

    except ora.Error, e:
        registerFailure()
        



# ------------------------------------------------------------------------------------------------ #     
####################################################################################################

###################################################################################################
# ----------------------------------------------------------------------------------------------- #
#                                     GENERATE HTML                                               #


########## ---------- BODY OF DOCUMENT ---------- ##########
print "<div id=\"review-page\">"
print "<div class=\"jumbotron\">"
print "<h1 class=\"display-3\">Create and view portfolios</h1>"
#print "<p class=\"lead\"></p>"
#print "<p class=\"lead\">"
print "<hr class=\"my-4\">"
print "<div class=\"inner-card\">"
# open left card div
print "<div class=\"review-left\">"
print("<div class=\"card text-white bg-success mb-3\">"+
"<div class=\"card-header\">Create a new portfolio:</div>"+
"<div class=\"card-body\">"+

## form collect new name
"<br><br><br><br><div class=\"form-group\">"+
"<label class=\"col-form-label\" for=\"inputDefault\">Enter portfolio name:</label>"+
"<input type=\"text\" class=\"form-control\" placeholder=\"New name...\" id=\"newPortName\">"+
"</div>"+

## form collect submit button
"<br><br><button onmousedown=\"createPortfolioSubmit()\"type=\"button\" class=\"btn btn-secondary\">Create!</button>"+

"</div>"+
"</div>")
#close left card div
print "</div>"

# gather portfolios for THIS USER ---------------------------------------
try:
    query = "select * from portfolio_list where email=\'" + email + "\'"
    cur.execute(query)
    portfolio_list = cur.fetchall()
    #for row in portfolio_list:
        #print "<p>" + str(row[1]) + "<p>"
except ora.Error, e:
    pass

#open right card div
print "<div class=\"review-right\">"
print("<div class=\"card border-success mb-3\">"+
"<div class=\"card-header\">Click on a portfolio to view it.</div>"+
"<div class=\"card-body\">")
#inside right card body
for row in portfolio_list:
    val_email = "\'" + email + "\'"
    val_portName = "\'" + str(row[1]) + "\'"
    vals = val_email + "," + val_portName
    print "<p><button onmousedown=\"goToUserPortfolio(" + vals + ")\" type=\"button\" class=\"btn btn-outline-primary\">" + str(row[1]) + "</button>"

#end right card body
print("</div>"+
"</div>")

print "<div class=\"backButton\">"
backButton = "<button onmousedown=\"logout()\" type=\"button\" class=\"btn btn-danger\">Logout</button>"
print backButton
print "</div>"


#close right card div
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
