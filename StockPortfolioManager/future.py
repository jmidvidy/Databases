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
# connect to Plotly.js
print "<script src=\"https://cdn.plot.ly/plotly-latest.min.js\"></script>"
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
symbol = arguments["symbol"].value
interval = arguments["interval"].value
#print "<p>" + str([email, portName, symbol]) + "</p>"
     
# quote must exist!
globalCurrQuote = stockAPI.getStockQuote(symbol, "close")


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
    out = ("<div class=\"" + cardType + " mb-3\">"+
           "<div class=\"card-header\">"+ header + "</div>"+
           "<div class=\"card-body\">"+
           "<h4 class=\"card-title\"><br>"+ value + "</h4>"+
           body +
           "</div>"+
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

def generateSharesCardForm(maxAMT):
    # dynamically construct drop-down options
    print "<div id=\"maxAMTPurchase\" style=\"display:none;\">"
    print str(maxAMT)
    print "</div>"
    message = "No greater than " + str(maxAMT)
    form = ("<br><br><div class=\"form-group\">"+
            "<label class=\"col-form-label\" for=\"inputDefault\">Enter integer amount:</label>"+
            "<input type=\"text\" class=\"form-control\" placeholder=\""+ message  +"\" id=\"stockPurchaseAmount\">"+
            "</div>")
    return form


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
print("<div class=\"alert alert-dismissible alert-success\">"+
"<br><br><h1>Future Performance:</h1>"+
"<p>Below is the predicted future performance for "+ symbol +" over the next " + interval  + ".</p>"+
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
# --------------- Purchase DIV ------------------- #

## ----- DEPOSIT SECTION ----- ##
def errorCard(error_message, header):
    ret_url = "?email=" + email + "&portName=" + portName
    card = ("<div class = \"login-failure\">"+
          "<div class=\"card text-white bg-danger mb-3\">"+
          "<div class=\"card-header\">Error!</div>"+
          "<div class=\"card-body\">"+
          "<h4 class=\"card-title\"><br>" + header  +"</h4>"+
          "<p class=\"card-text\"><br>" + error_message +  "</p>"+
          "<br><br> <button onmousedown=\"returnToPortfolioReview("+ "\'"   + ret_url + "\'"  +")\"  type=\"button\" class=\"btn btn-secondary\">Return to Portfolio Page</button>" +
          "</div>"+ "</div>" +           "</div>")

    return card

# - Chart stocks div
print "<div id=\"historic-performance\">"

# - number of shares
print "<div class=\"chart\">"
vals = stockAPI.getFuturePrediction(symbol, interval) 
print "<div id=\"hidden-vals\" style=\"display:none \">"
print ",".join(vals)
print "</div>"

chartBody = "<div id=\"chartDiv\"></div>"
chartCard = generateCardWithBody("card bg-light", "Future Performance:", "", chartBody)
print chartCard   
print "</div>"


print "<div class=\"forward-backbuttons\">"
backButtonPortfolio = "<button onmousedown=\"backToPortPage()\"type=\"button\" class=\"btn btn-danger\">&nbsp;Back to Portfolio Page&nbsp;</button>"
print backButtonPortfolio
print "</div>"

print "</div>" #end stocks-div
# end login-page div
print "</div>"




## - Close db connection
if con:
    con.close()

## - END HTML
print("</body>")
print("</html>")
