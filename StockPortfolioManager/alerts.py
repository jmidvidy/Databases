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
act = arguments["act"].value
email = arguments["email"].value
portName = arguments["portName"].value
deposit_amt = ""
buy_amt = ""
symbol = ""
price = ""
sellAll = ""
sell_amt = ""
if act == "deposit":
     deposit_amt = arguments["amt"].value
if act == "buy":
    buy_amt = arguments["amt"].value
    symbol = arguments["symbol"].value
    price = arguments["price"].value
if act == "sell":
    sell_amt = arguments["amt"].value
    price = arguments["price"].value
    symbol = arguments["symbol"].value
    try:
        sellAll = arguments["sellAll"].value
    except:
        pass


#print "<p>" + str([act, email, portName, deposit_amt, buy_amt,sell_amt, symbol, price, sellAll]) + "</p>"

########## ---------- BODY OF DOCUMENT ---------- ##########
print "<div id=\"alerts-page\">"
print "<div class=\"jumbotron\">"

## ----- DEPOSIT SECTION ----- ##
def errorCard(error_message, header):
    ret_url = "?email=" + email + "&portName=" + portName
    print("<div class = \"login-failure\">"+
          "<div class=\"card text-white bg-danger mb-3\">"+
          "<div class=\"card-header\">Error!</div>"+
          "<div class=\"card-body\">"+
          "<h4 class=\"card-title\">" + header  +"</h4>"+
          "<p class=\"card-text\">" + error_message +  "</p>"+
          "<br><br> <button onmousedown=\"returnToPortfolioReview("+ "\'"   + ret_url + "\'"  +")\"  type=\"button\" class=\"btn btn-secondary\">Return to Portfolio Page</button>" +
          "</div>"+ "</div>" +           "</div>")

    return

def successCard(message, header):
    ret_url = "?email=" + email + "&portName=" + portName 
    print("<div class = \"login-failure\">"+
          "<div class=\"card text-white bg-primary mb-3\">"+
          "<div class=\"card-header\">Success!</div>"+
          "<div class=\"card-body\">"+
          "<h4 class=\"card-title\">" + header + "</h4>"+
          "<p class=\"card-text\">" + message + "</p>" + 
          "<br><br> <button onmousedown=\"returnToPortfolioReview("+ "\'"   + ret_url + "\'"  +")\"  type=\"button\" class=\"btn btn-secondary\">Return to Portfolio Page</button>" +
          "</div>"+ "</div>" +           "</div>")

    return

#try to make a deposit
#based on the inputted values
def tryDeposit():
    try:
        #check to see that deposit_amt is integer
        check = int(deposit_amt)
        query = "update portfolio_balance set balance=balance+" + deposit_amt + " where portfolioid=\'" + email + "_" + portName + "\'"
        cur.execute(query)
        successCard("Your deposit has been successfully added to you account.  You can return to the portfolio page to review your portfolio.", "Deposit successfully made!")
    except:
        errorCard("Could not make deposit.  Either poorly formatted or inconsistent with DB.  Please return to the portfolio page to try again.")
    if con:
        con.close()
    return

# try to execute a query
# that buys the stock to the given person's account
# NEED to UPDATE BALANCE and UPDATE STOCK HOLDINGS
def tryBuy():
    try:
        # key for most queries
        portKey = "\'" + email + "_" + portName + "\'"
        
        """
        Purchase Steps:
        - (1) Update account balance for the given portfolip
        - (2) If the portfolio already has shares of the given stock --> update volume/strike price
        - (3) If no current shares --> create new table entry
        """

        # (1) - Update balance
        updateAMT = int(float(price)*float(buy_amt)) + 1
        query = "update portfolio_balance set balance=balance-" + str(updateAMT) + "where portfolioid=" + portKey
        cur.execute(query)
        symbolQuery = "\'" + symbol + "\'"
        query = "select volume from portfolio_stocks where symbol=" + symbolQuery + " and portfolioID=" + portKey
 #       print "<p>" + query + "</p>"
        cur.execute(query)
        rows = cur.fetchall()
        if rows:
            # (2) User already has shares.  Update holdings
            strPrice = "\'" + price + "\'"
            query = "update portfolio_stocks set volume=volume+"+str(updateAMT)+",strike_price="+strPrice+" where portfolioID=" + portKey + " and symbol=" + symbolQuery
  #          print "<p>" + query + "</p>"
            cur.execute(query)
        else:
            # (3) No rows of stock owned, create new table entry
   #         print "<p>" + "NO ROWS!" + "</p>"
            # prepare ('val1', 'val2')
            vals_list = [symbol, buy_amt, price]
            vals_str = []
            for elem in vals_list:
                curr = "\'" + elem + "\'"
                vals_str.append(curr)
            vals_str.insert(0, portKey)
            vals = ','.join(vals_str)
            vals = "(" + vals + ")"
            query = "insert into portfolio_stocks values " + vals
    #        print "<p>" + query + "</p>"
            cur.execute(query)
                
        #cur.execute(query)
        successCard("You have successfully purchased " + buy_amt + " shares of " + symbol + " at $" + price + " per share.  Your account balance has also been updated to reflect this expenditure.  You can return to your porfolio to view these updates.", "Stock Purchased!")
    except:
        failureCard("Stock purchase failure.  Please return to your portfolio to try again.", "Purchase failed!")
    if con:
        con.close()
    
        return

def trySell():
    try:
        """
        SELL procedure:
        - (1) Update balance to (share_price * number of shares sold)
        - (2) If sell all, delete row from portfolio_stocks
        - (3) If not sell all, decrement volume from portfolio_stocks
        """

        # configure portName
        portKey = "\'" + email + "_" + portName + "\'"
        balUpdate = int(float(sell_amt)*float(price))
        
        # (1) update balance
        query = "update portfolio_balance set balance=balance+" + str(balUpdate) + "where portfolioid=" + portKey
        cur.execute(query)

        # (2) If sellAll = "1" -- DELETE row from table
        symbQ = "\'" + symbol + "\'"
        if sellAll == "1":
            query2 = "delete from portfolio_stocks where portfolioid=" + portKey + " and symbol=" + symbQ
            cur.execute(query2)
        else:
            query3 = "update portfolio_stocks set volume=volume-"+sell_amt+" where portfolioID=" + portKey + " and symbol=" + symbQ
            cur.execute(query3)
        
        successCard("You have successfully sold " + sell_amt + " shares of " + symbol + " at $" + price + " per share.  Your account balance has also been updated to reflect this increase in available funds.  You can return to your porfolio to view these updates.  If you sold all your shares, that stock will no longer be listed in your portfolio.", "Sale Complete!")
    except ora.Error, e:
        failureCard("Stock sale not completed.  Please return to your portfolio to try again.", "Sale failed!")

    if con:
        con.close()

    return


if act == "deposit":
    tryDeposit()

if act == "buy":
    tryBuy()


if act == "sell":
    trySell()

## --------------------------- ##


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
