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
import json

import stockAPI

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

# gather CGI arguments passed from the URL
arguments = cgi.FieldStorage()
email = arguments["email"].value
portName = arguments["portName"].value

#print "<p>" + str([email, portName]) + "</p>"
     
########## ---------- BODY OF DOCUMENT ---------- ##########
def generateCard(cardType, header, value):
    out = ("<div class=\"" + cardType + " mb-3\">"+
           "<div class=\"card-header\">"+ header + "</div>"+
           "<div class=\"card-body\">"+
           "<h4 class=\"card-title\"><br>"+ value + "</h4>"+
           "</div>"+
           "</div>" )
    return out

def generateCardWithBody(cardType, header, value, body):

    backButton = "<button onmousedown=\"stockSelectBack()\" type=\"button\" class=\"btn btn-danger\">Back to Portfolio</button>"
    nextButton = "<button onmousedown=\"stockSelectNextSell()\" type=\"button\" class=\"btn btn-primary\">Next to Sell</button>"
    
    buttonDiv = "<div class=buttonDiv>" + backButton + nextButton + "</div>"

    out = ("<div class=\"" + cardType + " mb-3\">"+
           "<div class=\"card-header\">"+header+"</div>"+
           "<div class=\"card-body\">"+
           "<p><br>"+ value + "</p>"+
           body + buttonDiv +
           "</div>" + 
           "</div>" )
    return out


def getCurrBalance():
    bal = 0
    portID = "\'" + email + "_" + portName + "\'"
    query = "select balance from portfolio_balance where portfolioID=" + portID
    cur.execute(query)
    rows = cur.fetchall()
    #print "<p>" + str(query) + "</p>"
    #print "<p>" + str(rows) + "</p>"
    bal = rows[0][0]
    return str(bal)

def generateStockCardForm():  
    # dynamically construct drop-down options
    # read option.json
    #print "<p>"options + "</p>"
    
    # gather symbols
    formID = "sellStockSelect"
    portKey = "\'" + email + "_" + portName + "\'"
    queryGet = "select symbol, volume from portfolio_stocks where portfolioID=" + portKey
    cur.execute(queryGet)
    holds = cur.fetchall()
    symbols = []
    for elem in holds:
        symbols.append(elem[0])

    options = ""
    for row in symbols:
        options += "<option>" + str(row) + "</option>"
    f = ("<div class=\"form-group\">"+
         "<label for=\"exampleSelect1\">Select a stock from your portfolio:</label>"+
         "<select class=\"form-control\" id=\""+ formID + "\">"+
         options +
         "</select>"+
         "</div>")
    return f
    
    


print "<div id=\"buy-page\">"

# ---------------------------------------------- #
# ------------------ TOP DIV ------------------- #
# open top-div
print "<div class=\'buy-top\'>"
# ------------- NAME/PORTFOLIO NAME -- #
print "<div class=\'top-title\'>"#1
titleCard = generateCard("card text-white bg-dark", email + "\'s", portName)
print titleCard
print "</div>" #end top-title

# ------------ BUY STOCK TITLE -- #
print "<div class=\"top-bigText\">" #2
print("<div class=\"alert alert-dismissible alert-warning\">"+
"<h1>Sell Stocks:</h1>"+
"<p>You can sell any volume of a any stock that you own.  If you sell all of your shares in a particular stock, that stock will be removed from your portfolio.  After you complete your sell order, you balance will be updated to reflect the increase in available cash.</p>"+
"</div>")
print "</div>" 

# ------------ BALANCE -- #
print "<div class=\"top-Balance\">" #2
# NEED TO GET CURRENT BALANCE
curr_balance = getCurrBalance()
balanceCard = generateCard("card text-white bg-success", "Current Balance","$" + curr_balance)
print balanceCard
print "</div>"  

print "</div>" #end portfolio-top


# ---------------------------------------------- #
# --------------- Select Dropdown  ------------------- #
# - stock select

print "<div id=stockselect-page>"
print "<div class=\"stock-select\">"
stockCardForm = generateStockCardForm()
cardMessage = "Select a stock price below and you will be brought to a new page that:<br><br><ul><li>Displays current stock price for that listing.</li><li>Allows you to enter the number of shares you would like to sell.</li><li>Allows you to submit the sell order.</li>"
stockSelectCard = generateCardWithBody("card text-white bg-info", "Select stock ticker", cardMessage, stockCardForm)
print stockSelectCard
print "</div>"

print "</div>" #end stocks-div
# end login-page div





## - Close db connection
if con:
    con.close()

## - END HTML
print("</body>")
print("</html>")
