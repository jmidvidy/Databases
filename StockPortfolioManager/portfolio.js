//handle user-login page
function loginLogin(){
    $(".register-form").hide();
    $(".login-form").show();
}

function logout(){
    window.location.href = "https://murphy.wot.eecs.northwestern.edu/~jam658/portfolio/portfolio.py"
}

function loginRegister(){
    $(".login-form").hide();
    $(".register-form").show();
}

function loginSuccess(){
    alert("LOGIN SUCCESS!!");
}

function loginSubmit(){
    var email = $("#exampleInputEmail1").val();
    var password = $("#exampleInputPassword1").val();
    console.log(email, password);
    var url = "?act=login&email=" + email + "&password=" + password; 
    window.location.href = 'https://murphy.wot.eecs.northwestern.edu/~jam658/portfolio/portfolio_review.py' + url;
}

function createPortfolioSubmit(){
    var port_name = $("#newPortName").val();
    console.log(port_name);
    curr_url = window.location.href;
    console.log(curr_url);
    var add_url = "&addPortfolio=" + port_name;
    window.location.href = curr_url + add_url;

}

function registerSubmit(){
    var email = $("#exampleInputEmail2").val();
    var password = $("#exampleInputPassword2").val();
    var name = $("#registerName").val()
    console.log(name,email, password);
    var url = "?act=register&email=" + email + "&password=" + password + "&name=" + name;
    window.location.href = 'https://murphy.wot.eecs.northwestern.edu/~jam658/portfolio/portfolio_review.py' + url;
}

function returnToHomePage(){
    window.location.href = 'https://murphy.wot.eecs.northwestern.edu/~jam658/portfolio/portfolio.py';
}


function returnToPortPage(ret_url){
    console.log(ret_url);
    window.location.href = 'https://murphy.wot.eecs.northwestern.edu/~jam658/portfolio/portfolio_review.py' + ret_url;
}

function goToUserPortfolio(email, portName){
    console.log(email, portName);
    //change window to new python file
    var url_add = "?email=" + email + "&portName=" + portName
    window.location.href = "https://murphy.wot.eecs.northwestern.edu/~jam658/portfolio/portfolio_display.py" + url_add
}

function depositSubmit(){
    var url = window.location.href;
    var url_split = url.split('?');
    var url_end = url_split[1];
    var deposit_val = $("#depositAMT").val();
    if (deposit_val == ""){
	alert("You cannot deposit an empty value.  Please enter a dollar amount to deposit.");
    }
    else {
	var new_url = 'https://murphy.wot.eecs.northwestern.edu/~jam658/portfolio/alerts.py';
	var new_end = "?act=deposit&amt="+ deposit_val + "&"  + url_end;
	var new_end = new_end.replace('act=login&', '');
	// console.log(new_end);
	window.location.href = new_url + new_end;
    }
}

function returnToPortfolioReview(end_url){
    window.location.href = 'https://murphy.wot.eecs.northwestern.edu/~jam658/portfolio/portfolio_display.py' + end_url;
}

function buySubmit(){
    var url = window.location.href;
    var end_url = "?" + url.split("?")[1];
    window.location.href = 'https://murphy.wot.eecs.northwestern.edu/~jam658/portfolio/selectbuy.py' + end_url;
}

function sellSubmit(){
    var url = window.location.href;
    var end_url = "?" + url.split("?")[1];
    window.location.href = 'https://murphy.wot.eecs.northwestern.edu/~jam658/portfolio/selectsell.py' + end_url;
}

function stockSelectBack(){
    var curr_url = window.location.href;
    var end_url = "?" + curr_url.split("?")[1];
    window.location.href = "https://murphy.wot.eecs.northwestern.edu/~jam658/portfolio/portfolio_display.py" + end_url;
}

function stockSelectNext(){
    var symbol = $("#selectStock").val();
    if (symbol == ""){
	alert("You must select a stock symbol to advance to the next section");
    }
    var curr_url = window.location.href;
    var end_url = "?" + curr_url.split("?")[1] + "&symbol=" + symbol;
    window.location.href = "https://murphy.wot.eecs.northwestern.edu/~jam658/portfolio/buy.py" + end_url;
}

function backToPortPage(){
    var url = window.location.href;
    var end_url = url.split("?")[1];
    var good_end = end_url.split("&symbol")[0];
    window.location.href = "https://murphy.wot.eecs.northwestern.edu/~jam658/portfolio/portfolio_display.py?" + good_end;
}

function backToStockSelectPage(){
    var url = window.location.href;
    var end_url = url.split("?")[1];
    var good_end = end_url.split("&symbol")[0];
    window.location.href = "https://murphy.wot.eecs.northwestern.edu/~jam658/portfolio/selectbuy.py?" + good_end;
}

function submitStockPurchase(){
    var buyAMT = $("#stockPurchaseAmount").val();
    var maxAMT = $("#maxAMTPurchase").html();
    var error = false;
    try{
	var amt = Number(buyAMT);
	if (Number.isInteger(amt) == false || buyAMT == "" ) {
	    alert("Must enter an integer amount!");
	    error = true;
	}
	if (amt > Number(maxAMT)){
	    var err = "Must eneter a number less than:" + maxAMT;
	    alert(err);
	    error = true;
	}
    }
    catch {
	alert("Invalid stock purchase number.  Please enter an integer less than " + maxAMT);
	error = true;
    }
    
    if (error == false) {
	var quote = $("#currQuote").html();
	var url = window.location.href;
	var end_url = url.split("?")[1];
	var end = "&act=buy" + "&amt=" + buyAMT + "&price=" + quote;  
	window.location.href = "https://murphy.wot.eecs.northwestern.edu/~jam658/portfolio/alerts.py?" + end_url + end;
	}
}

function stockSelectNextSell(){
    var symbol = $("#sellStockSelect").val();
    var curr_url = window.location.href;
    var end_url = "?" + curr_url.split("?")[1] + "&symbol=" + symbol;
    window.location.href = "https://murphy.wot.eecs.northwestern.edu/~jam658/portfolio/sell.py" + end_url;
}

function submitStockSale(){
    var buyAMT = $("#stockPurchaseAmount").val();
    var maxAMT = $("#maxAMTPurchase").html();
    var error = false;
    try{
        var amt = Number(buyAMT);
        if (Number.isInteger(amt) == false || buyAMT == "" ) {
            alert("Must enter an integer amount!");
            error = true;
        }
        if (amt > Number(maxAMT)){
            var err = "Must eneter a number less than:" + maxAMT;
            alert(err);
	    error = true;
        }
    }
    catch {
        alert("Invalid stock purchase number.  Please enter an integer less than " + maxAMT);
        error = true;
    }

    
    if (error == false) {
        var quote = $("#currQuote").html();
        var url = window.location.href;
        var end_url = url.split("?")[1];
        var end = "&act=sell" + "&amt=" + buyAMT + "&price=" + quote;
	if (Number(buyAMT) == Number(maxAMT)){
	    end = end +  "&sellAll=1"
	}
        window.location.href = "https://murphy.wot.eecs.northwestern.edu/~jam658/portfolio/alerts.py?" + end_url + end;
    }
}

function backToStockSelectPageSell(){
    var url = window.location.href;
    var end_url = url.split("?")[1];
    var good_end = end_url.split("&symbol")[0];
    window.location.href = "https://murphy.wot.eecs.northwestern.edu/~jam658/portfolio/selectsell.py?" + good_end;
}


function historicSubmit(){
    var symbol = $("#selectStockAction").val();
    var interval = $("#selectInterval").val();
    var end_url = "?" + window.location.href.split("?")[1] + "&symbol=" + symbol + "&interval=" + interval;
    var url = "https://murphy.wot.eecs.northwestern.edu/~jam658/portfolio/historic.py";
    window.location.href = url + end_url;
}

function futureSubmit(){
    var symbol = $("#selectStockAction").val();
    var interval = $("#selectInterval").val();
    var end_url = "?" + window.location.href.split("?")[1] + "&symbol=" + symbol + "&interval=" + interval;
    var url = "https://murphy.wot.eecs.northwestern.edu/~jam658/portfolio/future.py";
    window.location.href = url + end_url;
}

function automatedSubmit(){
    var symbol = $("#selectStockAction").val();
    var interval = $("#selectInterval").val();
    var end_url = "?" + window.location.href.split("?")[1] + "&symbol=" + symbol + "&interval=" + interval + "&cost=20&val=1000";
    var url = "https://murphy.wot.eecs.northwestern.edu/~jam658/portfolio/ats.py";
    window.location.href = url + end_url;
}

function putChart(graph_title, symbol, interval){
    //collect y-vals from hidden div
    var y_vals_str = $("#hidden-vals").html();
    var y_vals = y_vals_str.split(",").map(Number);
    //console.log(y_vals);
    var x_vals = [];
    for (var i = 0; i < y_vals.length;i++){
	x_vals.push(i+1)
    }
    
    interval = "past " + interval;
    var trace1 = {
	x: x_vals,
	y: y_vals,
	type: 'scatter',
    };

    mod = "";
    if (graph_title == "Historic")
	mod = "past";
    if (graph_title == "Future" || graph_title == "Shannon Ratchet")
	mod = "next"
    if (interval.indexOf("week") != -1){
	interval = mod + " week";
    }

    if (interval.indexOf("month") != -1){
        interval = mod +" month";
    }

    if (interval.indexOf("year") != -1  && interval.indexOf("five") == -1){
        interval = mod +" year";
    }

    if (interval.indexOf("five") != -1) {
	interval = mod + "five years";
    }

    x_mod = "Performance (left is past, right is present)";
    if (mod == "next")
	x_mod = "Performance (left is present, right is future)";
 
    title_mod = "performance for";
    if (graph_title == "Shannon Ratchet"){
	title_mod = "strike prices for";
	x_mod = "Strike prices (left is present, right is future)";
    }

    var layout = {
	title: ""+ graph_title  + " "+ title_mod  +" " + symbol + " over the " + interval + ":",
	xaxis: {
	    title : x_mod
	},
	yaxis: {
	    title: "Close price"
     	}
    };

    var data = [trace1];

    Plotly.newPlot('chartDiv', data, layout, {showSendToCloud: true});
}


//load chart
window.onload = function(){
    //if at historic.py
    var url = window.location.href.split("?")[0];
    var curr_path = url.split("portfolio/")[1]
    if (curr_path == "historic.py" || curr_path == "future.py" || curr_path == "ats.py"){
	var end_url = window.location.href.split("?")[1];
	var params = end_url.split("&");
	var vals = [];
	// fetch symbol and interval
	for (var i = 0; i < params.length; i++){
	    var elem = params[i];
	    var split = elem.split("=");
	    var curr = [split[0], split[1]];
	    vals.push(curr);
	}
	console.log(vals);
	var symbol = vals[2][1];
	var interval = vals[3][1];
	
	if (curr_path == "historic.py")
	    putChart("Historic", symbol, interval);
	if (curr_path == "future.py")
	    putChart("Future", symbol, interval);
	if (curr_path == "ats.py")
	    putChart("Shannon Ratchet", symbol, interval);
    }
    
}

function backToPortSelectButton(){
    var url = window.location.href.split("?")[1];
    var params = url.split("&");
    var email = params[0].split("=")[1];
    var end = "?act=back&" + params[0];
    window.location.href = "https://murphy.wot.eecs.northwestern.edu/~jam658/portfolio/portfolio_review.py" + end;
}

function isGoodNumber(val){
    try{
	var a = Number(val);
	if (Number.isInteger(a)){
	    return 1;
	}
	else{
	    return 0;
	}
    }
    catch{
	return 0;
    }
}


function reloadATS(){
    
    error = false;
    var principal = $("#newPrincipal").val();
    console.log(principal);
    if (isGoodNumber(principal) != 1 || principal == ""){
	alert("New principal must be an integer!");
        error = true;
    }
    var tradeCost = $("#newTradeCost").val();
    if (isGoodNumber(tradeCost) != 1 || tradeCost == ""){
	alert("New trade cost must be an integer!");
	error = true;
    }

    if(error)
	return;
  
    var url = document.location.href.split("&cost")[0];
    var end = "&cost=" + tradeCost + "&val=" + principal;
    document.location.href = url + end;
    
}