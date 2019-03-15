#!/usr/bin/python

import os
import sys

def main(val):

    # 1 : clean with my_test_me.pl
    line = "perl my_test_me.pl"
    output = os.popen(line).read()

    # 2 : insert
    line = "./btree_insert __MYtest 64 13 AAAA"
    output = os.popen(line).read()
    print("\n ------- INSERT: 13 AAAA  ------ \n")
    print(output)
    if val == 1:
        return

    # 4: RIGHT CHILD
    line = "./btree_insert __MYtest 64 17 CCCC"
    print("\n ------- INSERT: 17 CCCC   ------ \n")
    output = os.popen(line).read()

    line = "./btree_insert __MYtest 64 19 DDDD"
    print("\n ------- INSERT: 19 DDDD   ------ \n")
    output = os.popen(line).read()
    #print(output)

    line = "./btree_insert __MYtest 64 15 BBBB"
    print("\n ------- INSERT: 15 BBBB   ------ \n")
    output = os.popen(line).read()


    # 5: LEFT CHILD
    line = "./btree_insert __MYtest 64 01 PPPP"
    print("\n ------- INSERT: 01 PPPP   ------ \n")
    output = os.popen(line).read()

    line = "./btree_insert __MYtest 64 05 RRRR"
    print("\n ------- INSERT: 05 RRRR   ------ \n")
    output = os.popen(line).read()

    line = "./btree_insert __MYtest 64 03 QQQQ"
    print("\n ------- INSERT: 03 QQQQ   ------ \n")
    output = os.popen(line).read()

    line = "./btree_insert __MYtest 64 07 SSSS"
    print("\n ------- INSERT: 07 SSSS   ------ \n")
    output = os.popen(line).read()

    """
    Root: 13
    
    LEFT: 01 03 05 07 
    
    RIGHT: 13 15 17 19
    """

    """
    val = 2
    Insert(14)
    Insert(16)
    Insert(20)
    Insert(21)
    Insert(22)
    Insert(04)
    """
    
    # get right before split root
    vals = ["14", "16", "20", "21", "22", "04", "30", "35"]
    for val in vals:
        line = "./btree_insert __MYtest 64 "+ val +" SSSS"
        print("\n ------- INSERT: "+ val  +" SSSS   ------ \n")
        output = os.popen(line).read()
        if val == "35":
            print(output)
        

    return


def main2():

    # 1 : clean with my_test_me.pl
    line = "perl my_test_me.pl"
    output = os.popen(line).read()


    # get right before split root
    vals = ["40", "00", "10", "20", "30", "50", "60", "70"]
    vals2 = ["01", "11", "12", "41", "61", "62", "71"]

    for val in vals:
        line = "./btree_insert __MYtest 64 "+ str(val) +" SSSS"
        print("\n ------- INSERT: "+ str(val)  +" SSSS   ------ \n")
        output = os.popen(line).read()
        #print(output)

    for val in vals2:
        line = "./btree_insert __MYtest 64 "+ str(val) +" SSSS"
        print("\n --------------------- INSERT: "+ str(val)  +" SSSS  --------------------- \n")
        output = os.popen(line).read()
        #print(output)
        
    # cause rihgt interior node to split
    vals3 = ["63", "64" ,"42", "43"]
    for val in vals3:
        line = "./btree_insert __MYtest 64 "+ str(val) +" SSSS"
        print("\n --------------------- INSERT: "+ str(val)  +" SSSS  --------------------- \n")
        output = os.popen(line).read()
        print(output)

    return

def main3():

    # 1 : clean with my_test_me.pl
    line = "perl my_test_me.pl"
    output = os.popen(line).read()

    return



if __name__ == "__main__":
    try:
        val = sys.argv[1]
        if val == 2:
            main2()
        else:
            main(val)
    except:
        main2()
