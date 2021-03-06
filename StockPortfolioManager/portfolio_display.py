#!/usr/bin/python
#
# Oracle butt-finding
#
#

oracle_base = '/raid/oracle11g/app/oracle/product/11.2.0.1.0'
oracle_sid = 'CS339'
import os;
import stockAPI
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
import copy

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

globalMarketVal = 0

#print "<p>" + str([email, portName]) + "</p>"

###################################################
# - get stock holdings of the current portfolio - #

portfolio_info = {}
def getPortfolioInfo():
    portKey = "\'" + email + "_" + portName + "\'"
    queryGet = "select symbol, volume from portfolio_stocks where portfolioID=" + portKey
    cur.execute(queryGet)
    holds = cur.fetchall()
    symbs = []
    totalMarketVal = 0
    totalVariance = 0.00
    numStocks = 0

    for row in holds:
        curr_dict = {}
        symbol = row[0]
        volume = row[1]
        symbs.append(symbol)

        info = stockAPI.getStockQuote(symbol, "info")
        try:
            beta = stockAPI.getBeta(symbol)
        except:
            beta = .2
        open_price = info["open"]
        close_price = info["close"]
        volume_traded = info["volume"]

        # compute market val
        mk_val = int(float(close_price)*float(volume))
        # increment global market value
        totalMarketVal += mk_val
        market_val = str(mk_val)

        curr_dict["beta"] = beta
        curr_dict["open"] = open_price
        curr_dict["close"] = close_price
        curr_dict["volume_traded"] = volume_traded
        curr_dict["market_val"] = market_val
        curr_dict["shares_owned"] = volume
        
        # update portfolioInfoDict
        portfolio_info[symbol] = copy.deepcopy(curr_dict)

    return holds, symbs, totalMarketVal

holdings, symbols, globalMarketVal = getPortfolioInfo()
#print str(symbols)
symbols = sorted(symbols)



#print "<p>" + str(holdings) + "</p>"
#print "<p>" + str(symbols) + "</p>"
     
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

    if value == "":
         out = ("<div class=\"" + cardType + " mb-3\">"+
           "<div class=\"card-header\">"+ header + "</div>"+
           "<div class=\"card-body\">"+
           body +
           "</div>"+
           "</div>" )

    return out



def getDepositCard():
    out = ""
    form_group = ("<div class=\"form-group\">"+
                  "<fieldset>"+
                  "<label class=\"control-label\" for=\"inputDefault\">Enter amount:</label>"+
                  "<input class=\"form-control\" id=\"depositAMT\" type=\"text\" placeholder=\"  x to deposit x | -x to withdraw x\" >"+
                  "</fieldset>"+
                  "</div>")

    # need to ADD on mousedown event
    button = "<button onmousedown=\"depositSubmit()\" type=\"button\" class=\"btn btn-success\">Deposit/Withdraw!</button>"
    out = ("<div class=\"card border-success mb-3\">"+
           "<div class=\"card-body\">"+
           form_group + button +
           "</div>"+
           "</div>")
    return out

def getBuyStockCard():
    out = ""
    # need to ADD on mousedown event
    button1 = "<button onmousedown=\"buySubmit()\" type=\"button\" class=\"btn btn-dark\">Buy!</button>"
    button2 = "<button onmousedown=\"sellSubmit()\" type=\"button\" class=\"btn btn-dark\">Sell!</button>"
    out = ("<div class=\"card border-dark \">"+
           "<div class=\"card-header\">Buy or Sell Stock</div>"+
           "<div class=\"card-body\">"+
            button1 + button2 + 
           "</div>"+
           "</div>")


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

def makeButton(style, buttonTitle, mouseDownFunction):
    if style == "":
        style = "btn btn-outline-primary"
    mousedown = "onmousedown=\"" + mouseDownFunction + "\""
    b = "<button " + mousedown  + " type=\"button\" class=\""+ style  +"\">"+ buttonTitle  +"</button>"
    return b

def makeForm(formID, symbols, top_message):
    options = ""
    for row in symbols:
        options += "<option>" + str(row) + "</option>"
    f = ("<div class=\"form-group\">"+
         "<label for=\"exampleSelect1\">"+ top_message  +"</label>"+
         "<select class=\"form-control\" id=\""+ formID + "\">"+
         options + 
         "</select>"+
         "</div>")
    return f

def computePortfolioBeta():
    """
    Compute weighted sum of beta values
    """
    # (1) :: need total number of shares in the portfolio
    marketVal = 0
    for key in portfolio_info:
        marketVal += float(portfolio_info[key]["market_val"])


    # (2) :: num is sum of each symbol: (porpotion of total share)*(beta)
    topCovar = float(0)
    for key in sorted(portfolio_info.keys()):
        portionOfMktVal = float(portfolio_info[key]["market_val"]) / float(marketVal)
        currBeta = portfolio_info[key]["beta"]
        update = (currBeta * portionOfMktVal)
        topCovar += update

    # (3) :: normalize to number of stocks in the portfolio
    portBeta = topCovar 

    return round(portBeta, 2)

print "<div id=\"portfolio-page\">"

# ---------------------------------------------- #
# ------------------ TOP DIV ------------------- #
# open top-div
print "<div class=\'portfolio-top\'>"
# ------------- NAME/PORTFOLIO NAME -- #
print "<div class=\'top-title\'>"#1
titleCard = generateCard("card text-white bg-dark", email + "\'s", portName)
print titleCard
print "</div>" #end top-title

# ------------ MARKET VALUE -- #
print "<div class=\"top-marketValue\">" #2
# NEED TO GET MARKET VALUE
marketValueCard = generateCard("card text-white bg-warning", "Present Market Value:", "$" + str(globalMarketVal))
print marketValueCard  
print "</div>" #end top-marketValue

# ------------  COVARIANCE MATRIX -- #
print "<div class=\"top-covMatrix\">" #2  
# NEED TO GET COVARIANCE MATRIX
globalCovariance = computePortfolioBeta()
sign = "+"
if globalCovariance < 0:
    sign = ""
covarianceMatrixCard = generateCard("card text-white bg-warning", "Portfolio Covariance:", sign + str(globalCovariance))
print covarianceMatrixCard  
print "</div>"

# ------------ BALANCE -- #
print "<div class=\"top-Balance\">" #2
# NEED TO GET CURRENT BALANCE
curr_balance = getCurrBalance()
balanceCard = generateCard("card text-white bg-success", "Current Balance","$" + curr_balance)
print balanceCard
print "</div>"  


# ------------ Deposit -- #
print "<div class=\"top-deposit\">"
depositCard = getDepositCard()
print depositCard
print "</div>"

# ------------ Buy Stock -- #
print "<div class=\"top-buystock\">"
buyStockCard = getBuyStockCard()
print buyStockCard
print "</div>"


print "</div>" #end portfolio-top
# ---------------------------------------------- #
# --------------- STOCKS DIV ------------------- #

def getTableRow(symbol):

    """
    For a given symbol, need to gather:
    - market value (computed)
    - close price
    - open price
    - shares traded (volume)
    - beta value
    """

    tstyle_dict = {1:"danger", 2:"success"}

    curr_dict = portfolio_info[symbol]

    market_val = curr_dict["market_val"]
    open_price = curr_dict["open"]
    close_price = curr_dict["close"]
    volume_traded = curr_dict["volume_traded"]
    shares_owned = curr_dict["shares_owned"]
    beta = curr_dict["beta"]
    
    sign = "+"
    tstyle = tstyle_dict[2]
    if beta < 0:
        sign = ""
        tstyle = tstyle_dict[1]

    trow = ("<tr class=\"table-"+tstyle+"\">"+
           "<th scope=\"row\">"+ symbol +"</th>"+
           "<td>"+ str(shares_owned) +"</td>"+
           "<td>$"+ market_val  +"</td>"+
           "<td>$"+ open_price +"</td>"+
           "<td>$"+ close_price  +"</td>"+
           "<td>"+ volume_traded  +"</td>"+
           "<td>"+ sign + str(beta) +"</td>"+
           "</tr>")

    return trow

def printStocks():
    table_body = ""
    count = 0
    for row in symbols:
        curr_symbol = row
        table_body += getTableRow(curr_symbol)  
        count += 1

    table = ("<table class=\"table\">"+
             "<thead>"+
             "<tr class=\"table-info\">"+
             "<th scope=\"col\">Symbol:</th>"+
             "<th scope=\"col\">Shares Owned:</th>"+
             "<th scope=\"col\">Market Value:</th>"+
             "<th scope=\"col\">Open:</th>"+
             "<th scope=\"col\">Close:</th>"+
             "<th scope=\"col\">Daily Volume:</th>"+ 
             "<th scope=\"col\">Beta:</th>"+ 
             "</tr>"+
             "</thead>"+
             "<tbody>"+
             table_body +
             "</tbody>"+
             "</table>") 
   
    print table
    return

##################################################


#stocks div
print "<div class=portfolio-stocks>"
print "<div class=action-bar>"

#stock-select
print "<div class=\"action-div stock-select\">"
selectForm = makeForm("selectStockAction", symbols, "Select a stock from your portfolio:")
stockSelectCard = generateCardWithBody("card text-white bg-info", "Select a stock:", "", selectForm)
print stockSelectCard
print "</div>" #end stock-select

#interval-select
print "<div class=\"action-div interval-select\">"
times = ["week", "month", "year", "five years"]
intervalForm = makeForm("selectInterval", times, "Select a time interval:")
selectIntervalCard = generateCardWithBody("card text-white bg-info", "Select time interval:", "", intervalForm)
print selectIntervalCard
print "</div>"

#historic-select
print "<div class=\"action-div historic-select\">"
historicButton = makeButton("", "Historic Performance!", "historicSubmit()")
historicSelectCard = generateCardWithBody("card border-primary", "See:", historicButton, "")
print historicSelectCard
print "</div>" #end stock-select

#future-select
print "<div class=\"action-div future-select\">"
futureButton = makeButton("", "Future Performance!", "futureSubmit()")
futureSelectCard = generateCardWithBody("card border-primary", "See:", futureButton, "")
print futureSelectCard
print "</div>" #end stock-select

#automated-select
print "<div class=\"action-div automated-select\">"
automatedButton = makeButton("", "ATS Performance!", "automatedSubmit()")
automatedSelectCard = generateCardWithBody("card border-primary", "See:", automatedButton, "")
print automatedSelectCard
print "</div>" #end stock-select
print "</div>" #end action bar


#### STOCKS DISPLAY DIV ####
print "<div class=stocks-display>"
# print individual stock information
printStocks()
backToPortSelectButton = makeButton("btn btn-danger" ,"Back to Portfolio Select!", "backToPortSelectButton()")
print backToPortSelectButton
print "</div>" # end stocks-display
#### END STOCK DISPAY DIV ###




print "</div>" #end stocks-div
# end login-page div
print "</div>"




## - Close db connection
if con:
    con.close()

## - END HTML
print("</body>")
print("</html>")
