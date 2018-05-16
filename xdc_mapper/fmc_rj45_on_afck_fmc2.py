#!/usr/bin/python3

from xdc_map import *

# We create the chain of dictionaries starting from the one defining the 
# desired connection of the target chip to the FPGA

dicts=[]

dicts.append(read_csv('fmc_rj45.csv',(
    [1,],
    [2,lambda x: x.replace("_CC","")]
)))

#If our gDPB is in FMC2, we remove LA2_ and HB2_ prefixes in pin definitions
dicts.append(read_csv('pinout.csv',(
        #[2,lambda x: x.replace("LA2_","").replace("HA2_","").replace("HB2_","").replace("_CC","")],
        [2,lambda x: x.replace("LA1_","").replace("HA1_","").replace("HB1_","").replace("_CC","")],
        [0  ,],
)))

make("fmc_rj45_on_afck_fmc2.xdc", dicts)


