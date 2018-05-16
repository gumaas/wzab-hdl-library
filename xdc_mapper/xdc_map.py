#!/usr/bin/python3
"""
This is a simple script for creating the XDC mapping from the series of CSV files
describing the interface boards and cables used to connect the target chip
or device with the FPGA.
Please note, that the script is very simplified and there is no good error 
detection.

Written by Wojciech M. Zabołotny (wzab@ise.pw.edu.pl) 11.07.2017
License: PUBLIC DOMAIN of CC0 (whatever is more convenient for you)
"""

import csv

def read_csv(fname,cols):
    """
    The read_csv accepts two arguments.
    fname - name of the csv file to read
    cols - two element list describing position and transformation function
    
    """
    res={}
    for i in range(0,2):
        if len(cols[i])==1:
            cols[i].append(lambda x: x)
    #print(cols)
    with open(fname, newline='') as csvfile:
         myreader = csv.reader(csvfile, delimiter=',', quotechar='\"')
         for row in myreader:
             rkey=cols[0][1](row[cols[0][0]])
             rval=cols[1][1](row[cols[1][0]])
             if res.__contains__(rkey):
                 #raise(Exception("Duplicated pin:"+rkey))
                 print("Warning! Duplicated pin:"+rkey)
             res[rkey]=rval
    return res


def make(filename, dicts):
    #Now we open the output constraints file
    fxdc=open(filename,"w")
    #Now we can do the translation, but we first sort the keys
    pins=list(dicts[0].keys())
    pins.sort()
    for pin in pins:
        print(pin)
        key=pin
        for i in range(0,len(dicts)):
            key=dicts[i][key]
            print("->"+key)
        #Now write the lines to the output XDC
        fxdc.write("set_property PACKAGE_PIN %s [get_ports {%s}]\n" % (key, pin))
    fxdc.close()  

#