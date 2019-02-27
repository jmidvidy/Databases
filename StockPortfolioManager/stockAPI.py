import urllib2
import json
import ssl
import os

"""
Returns a ret type for an inputted symbol.
 - IF retType == "close" :: return the last stock quote
 - IF retType == "info" :: return dictionary of values
"""
def getStockQuote(symbol, retType):
    line = "perl quote.pl " + symbol
    output = os.popen(line).read()
    
    # if retType is last, only want the close price
    if retType == "close":
        quote = output.split('\n')
        if len(quote) == 4:
            return "0"
        quote = quote[4].split('\t')[1]
        return quote
    
    # implement later
    if retType == "info":
        quote = output.split('\n')
        inds = [5,6,7]
        vals = []
        for i in inds:
            vals.append(quote[i].split('\t')[1])
        out = {"open":vals[0], "close":vals[1], "volume":vals[2]}
        return out

    return output

"""
Returns the beta value of the stock for the given interval
"""
def getBeta(symbol):
    
    # hardcode dates for now
    from_date = "1/1/97"
    to_date =  "2/1/07"
    
    """
    Procedure:
    - (1) :: Get the variance of the stock for the given time interval
    - (2) :: Get the covariance(stock, market) for the given time interval
    - (3) :: Return the 
    """

    # (1) :: Gather vaiance of the market for the given time period
    line = "perl get_info.pl --field=close --from=\""+ from_date  +"\" --to=\""+ to_date  +"\"  SPY"
    out = os.popen(line).read().split("\n")[1]
    marketSTD = out.split("\t")[4]
    marketVariance = float(marketSTD)**2
#    print(marketVariance)

    # (2) :: Gather the covariance of (stock, market) for the given time period
    line2 = "perl get_covar.pl --field1=close --field2=close --from=\""+ from_date  +"\" --to=\""+ to_date  +"\" "+ symbol  +" SPY"
    output = output = os.popen(line2).read()
    market_stock_variance = output.split("\n")[5].split("\t")[-1]
    
    beta = float(market_stock_variance) / float(marketVariance)
    beta = round(beta, 2)
    return beta


"""
Returns a list of prices for the last 5 years.
- Output[0] is the most recent price
- Output[-1] is the price from 5 years ago
"""
def getLastFiveYears(symb):
    line = "perl quotehist.pl --close " + symb
    out = os.popen(line).read().split("\n")
    o = []
    for line in out:
        try:
            o.append(line.split("\t")[2])
        except:
            pass

    #print(list(reversed(o)))
    return list(reversed(o))

"""
Returns a comma seperated list of close prices
for the given time interval
"""
def getHistoricInfo(symbol, interval):
    prices = getLastFiveYears(symbol)
    div = 7
    if interval == "week":
        div = 7
    elif interval == "month":
        div = 28 
    elif interval == "year":
        div = len(prices) // 5
    else:
        div = "none"

    if div != "none":
        return list(reversed(prices[:div]))
    else:
        return list(reversed(prices))
  
    #print(symbol, interval)

"""
"""
def getFuturePrediction(symbol, interval):
    
    if interval == "week":
        tm = 7
    elif interval == "month":
        tm = 32
    elif interval == "year":
        tm = 365
    else:
        tm = 365*5

    line = "perl time_series_symbol_project.pl "+ symbol  +" "+ str(tm)  +" AWAIT 200 AR 16"
    output = os.popen(line).read().split("\n")[-tm-1:-1]

    out = []
    for line in output:
        curr = line.split("\t")[2]
        out.append(curr)

    return out

def runATS(symbol, interval, val, cost):
    line = "perl shannon_ratchet.pl "+ symbol  +" " + val  +  " " + cost
   
    if interval == "week":
        tm = 7
    elif interval == "month":
        tm = 32
    elif interval == "year":
        tm = 365
    else:
        tm = 5504


    output = os.popen(line).read().split("\n")[-tm-5:-1]
    summaryStats = output[len(output)-4:]

    out = []
    for line in output[:len(output)-4]:
        out.append(line.split("\t")[1])

    ss = []
    for line in summaryStats:
        ss.append(line.split("\t")[1])

    ss_dict = {"invested":1,"days":1, "total":1, "total_with_costs":1}

    ss_dict["invested"] = ss[0]
    ss_dict["days"] = tm
    total = ss[2].split(" ")[0]
    total_w = ss[3].split(" ")[0]
    ss_dict["total"] = str(int(float(total) / (5505/tm)))
    ss_dict["total_with_costs"] = str(int(float(total_w)/(5505/tm))) 

   

    out_dict = {"x_vals":out, "summary_stats":ss_dict}
    return out_dict

                
if __name__ == "__main__":
  #getBeta("AAPL")
  #ret = getHistoricInfo("AAPL", "past%20")
  #print(ret)
#runATS("AAPL", "week")
    a = getBeta("GOOGL")
    print a
