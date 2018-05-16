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
import regex

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

def replace_right(source, target, replacement, replacements=None):
    return replacement.join(source.rsplit(target, replacements))

def make_bus(pinname, idx_offset = 0):

    # [name, nr, postfix] = re.match( r"(.*?)(\d+)(.*)", pinname).groups()
    # we want to use the last group of digits as bus index
    # multi digit groups must be supported

    # I split a string into 3 groups: name, index and postfix
    # name and index must have more then 1 char (+)
    #   and may contain any characters (.)
    # postfix is optional (*)
    # in order to make sure that last digit group will be matched as index 
    #   I use reverse parsing - right to left ((?r))
    # parsing from right regexp matches postfix first
    #   by default it would match as much characters as possible, 
    #   as long as other two brackets are fulfilled
    #   I'm changing this behaviour by using (?) - non-greedy version

    [name, nr, postfix] = regex.match( r"(?r)(.+)(\d+)(.*?)", pinname).groups()

    if postfix != '':
        postfix = '_'+postfix

    s = '{name}{postfix}[{id}]'.format(
            name=replace_right(name,'_','',1),
            postfix=replace_right(postfix,'_','',1),
            id=str(int(nr)+idx_offset)
        )

    return s

def make_bus_pattern( pattern, pinname):
    for k, v in pattern.items():
        if k in pinname:
            return make_bus(pinname, v)

    else:
        return pinname