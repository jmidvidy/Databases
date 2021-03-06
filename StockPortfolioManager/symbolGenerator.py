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


def main():
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

    out = ""
    query = "select symbol from cs339.StocksSymbols"
    cur.execute(query)
    rows = cur.fetchall()
    rows = sorted(rows)
    for elem in rows:
        out += "<option>" + str(elem[0]) + "</option>"

        
    a = {"body": out}
    with open('options.json', 'w') as outfile:
        json.dump(a, outfile)

    return


if __name__ == "__main__":
    main()









