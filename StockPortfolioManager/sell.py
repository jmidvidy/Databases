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
#print "<p>" + str([email, portName, symbol]) + "</p>"
     
# quote must exist!
# price per share
globalCurrQuote = stockAPI.getStockQuote(symbol, "close")

# gather number of shares that you own
numShares = 0
def getNumShares():
    portID = "\'" + email + "_" + portName + "\'"
    symbolQ = "\'" + symbol + "\'"
    query = "select volume from portfolio_stocks where portfolioID=" + portID +  " and symbol=" + symbolQ
    #print "<p>"+str(query) +"</p>"
    cur.execute(query)
    rows = cur.fetchall()
    num = rows[0][0]
    #print "<p>"+str(num) +"</p>"
    
    return num

numShares = getNumShares()


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
print("<div class=\"alert alert-dismissible alert-warning\">"+
"<h1>Sell Stocks:</h1>"+
"<p>You can sell any volume of a any stock that you own.  If you sell all of your shares in a particular stock, that stock will be removed from your portfolio.  After you complete your sel\
l order, you balance will be updated to reflect the increase in available cash.</p>"+
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

# - Purchase stocks div
print "<div class=\"buy-stocks\">"





# - stock select
print "<div class=\"stock-select\">"
print "<div id=\"currQuote\" style=\"display:none\">"
print "" + globalCurrQuote
print "</div>"

maxAMT = numShares
stockSelectMessage = "You can share any number of the stocks you own.  You currently own: <br><br><h3><mark>" + str(numShares) +  "</mark></h3><br> shares of this stock."
stockSelectCard = generateCardWithBody("card text-white bg-info", "Stock to Sell:", symbol, "Price per share: $" +globalCurrQuote + "<br><br><br>" + stockSelectMessage)
print stockSelectCard
print "</div>"

# - number of shares
print "<div class=\"shares-input\">"
shareInputForum = generateSharesCardForm(maxAMT)
shareInputCard = generateCardWithBody("card bg-light", "Enter number of shares:", "", shareInputForum)
print shareInputCard   
print "</div>"

# - purchase button
print "<div class=\"purchase-button\">"
purchaseButton = "<button onmousedown=\"submitStockSale()\"type=\"button\" class=\"btn btn-success\">&nbsp;Submit Sale!&nbsp;</button>"
purchaseCard = generateCardWithBody("card text-white bg-dark", "Submit sale request:", "Submit Order<br><br><br>", purchaseButton)
print purchaseCard
print "</div>"

print "<div id=\"buy-whitespace\">"
print "</div>"

print "<div class=\"forward-backbuttons\">"
backButtonPortfolio = "<button onmousedown=\"backToPortPage()\"type=\"button\" class=\"btn btn-danger\">&nbsp;Back to Portfolio Page&nbsp;</button>"
backButtonSelect = "<button onmousedown=\"backToStockSelectPageSell()\" type=\"button\" class=\"btn btn-danger\">&nbsp;Back to Select Stock Page Page&nbsp;</button>"
print backButtonPortfolio
print backButtonSelect
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
