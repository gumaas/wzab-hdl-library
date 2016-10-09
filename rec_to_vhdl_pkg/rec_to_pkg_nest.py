#!/usr/bin/python
# The script below is written by Wojciech M. Zabolotny
# wzab<at>ise.pw.edu.pl 21.09.2016
# it is published as PUBLIC DOMAIN
# However, if you create any derived work, it would be nice
# if you provide information about the original author.
import sys
rec_types=[]
rec_dict={}
class record:
  def __init__(self,name):
    self.name = name
    self.fields = []
    self.nof_bits = 0
  def add_field(self,field_desc):
    self.fields.append(field(self,field_desc))

class field:
  def __init__(self,par_rec,field_desc):
    fd = field_desc.split(",")
    self.fname = fd[0]
    #"rec" is handled in a special way
    if fd[1]=="rec":
      self.ftype = fd[1]
      self.rec_name = fd[2]
      self.b1=rec_dict[fd[2]].nof_bits-1
      self.b2=0
    #"std_logic" is handled in a special way
    elif fd[1]=="std_logic":
      self.ftype = fd[1] 
      self.b1=0
      self.b2=0
    elif not fd[1] in ["signed","unsigned","std_logic_vector"]:
       raise Exception("Wrong field type")
    else:
      self.ftype = fd[1]
      if len(fd)==3:
         self.b1=int(fd[2])-1
         self.b2=0
      elif len(fd)==4:
         self.b1=int(fd[2])
         self.b2=int(fd[3])
      else:
         raise Exception("Syntax error in line: "+field_desc)
    #Assign vector bits
    self.v1=par_rec.nof_bits
    self.v2=par_rec.nof_bits+abs(self.b2-self.b1)
    par_rec.nof_bits = self.v2+1
 
if len(sys.argv) != 2:
   print """
The rec_to_pkg scripts creates VHDL package for conversion
between the VHDL records containing "signed", "unsigned",
"std_logic_vector" and "std_logic" fields and std_logic_vectors.
Additionally, the record may contain also another record,
defined previously in the same decription file.
It should be called as: rec_to_pkg_nest.py description_file
where the description file should have the following syntax:

#Optional comment line
package package_name
## Comments starting with double hash are accumulated and
## copied at the begining of the generated vhdl file
#Then one or more record definitions
record record_name
#optional comment lines
#[...]
field_name,signed_or_unsigned,width
#or
field_name,signed_or_unsigned,left_bit_nr,right_bit_nr
#or
field_name,rec,previously_defined_record
end

The generated package is written to the package_name.vhd file
"""
   exit(0)
fin=open(sys.argv[1])
#Read the full description of the type
type_desc=[]    
comments=[]
for l in fin.readlines():
  l=l.strip()
  if len(l) > 0:
    if l[0] != "#":
      type_desc.append(l)
    elif l[0:2] == "##":
      comments.append(l[2:])
#The first line should contain the package name
l=type_desc.pop(0).split(" ")
if l[0] != "package":
   raise Exception("Syntax error! The first line should have form \"package name_of_package\"")
pkg_name=l[1]
#Now we define the record types
while len(type_desc)>0:
  td=type_desc.pop(0)
  print td
  #The first line in the section should contain the record name
  l=td.split(" ")
  if l[0] != "record":
   raise Exception("Line: "+td+"\nSyntax error! The first line in the section should have form \"record name_of_type\"")
  type_name=l[1]
  cur_rec=record(type_name)
  rec_dict[type_name]=cur_rec
  rec_types.append(cur_rec)
   #Prepare for analysis of fields
  end_found = False
  #Find the field definitions
  while len(type_desc)>0:
    l=type_desc.pop(0)
    print l
    if l=="end":
       end_found=True
       break
    cur_rec.fields.append(field(cur_rec,l))
  if not end_found:
     raise Exception("Syntax error: no \"end\" found")
#If we got here, probably the syntax was correct
#Lets generate the package
p="""\
-------------------------------------------------------------------------------
-- This file has been autometically generated by the rec_to_pkg_nest.py tool
-- from the """+sys.argv[1]+""" record description file.
-- Don't edit it manually. To introduce any changes, edit the """+sys.argv[1]+""" file
-- and rerun the rec_to_pkg_nest.py 
-------------------------------------------------------------------------------
"""
for l in comments:
  p+="--"+l+"\n"
p+="""\
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
"""
p+="package "+pkg_name+" is\n\n"
# Now write definition of record types
for r in rec_types:
  p+="type "+r.name+" is record\n"
  for f in r.fields:
     if f.ftype=="rec":
       s="    "+f.fname+" : "+f.rec_name+";\n"
     elif f.ftype=="std_logic":
       s="    "+f.fname+" : "+f.ftype+";\n"
     else:
       s="    "+f.fname+" : "+f.ftype+"("
       if f.b1 > f.b2:
          s=s+str(f.b1)+" downto "+str(f.b2)+");\n"
       else:
          s=s+str(f.b1)+" to "+str(f.b2)+");\n"
     p+=s
  p+="end record;\n\n"
  #Write width of our type
  p+="constant "+r.name+"_width : integer := "+str(r.nof_bits)+";\n\n"
  #Write headers of conversion functions
  p+="function "+r.name+"_to_stlv(\n"
  p+="  constant din : "+r.name+")\n"
  p+="  return std_logic_vector;\n\n"
  p+="function stlv_to_"+r.name+"(\n"
  p+="  constant din : std_logic_vector)\n"
  p+="  return "+r.name+";\n\n"
p+="end "+pkg_name+";\n\n"
#Now the body of the package - the conversion functions
p+="package body "+pkg_name+" is\n\n"
# Iterate over the records
for r in rec_types:
  p+="function "+r.name+"_to_stlv(\n"
  p+="  constant din : "+r.name+")\n"
  p+="  return std_logic_vector is\n"
  p+="  variable res : std_logic_vector("+str(r.nof_bits-1)+" downto 0);\n"
  p+="begin\n"
  for f in r.fields:
    if f.ftype=="rec":
      p+="  res("+str(f.v2)+" downto "+str(f.v1)+") := "+f.rec_name+"_to_stlv(din."+f.fname+");\n"
    elif f.ftype=="std_logic":
      p+="  res("+str(f.v1)+") := din."+f.fname+";\n"
    else:
      p+="  res("+str(f.v2)+" downto "+str(f.v1)+ ") := std_logic_vector(din."+f.fname+");\n"
  p+="  return res;\n"
  p+="end "+r.name+"_to_stlv;\n\n"
  #
  p+="function stlv_to_"+r.name+"(\n"
  p+="  constant din : std_logic_vector)\n"
  p+="  return "+r.name+" is\n"
  p+="  variable sdin : std_logic_vector("+str(r.nof_bits-1)+" downto 0);\n"
  p+="  variable res : "+r.name+";\n"
  p+="begin\n"
  p+="  sdin := din;\n"
  for f in r.fields:
    if f.ftype=="rec":
      p+="  res."+f.fname+":= stlv_to_"+f.rec_name+"(sdin("+str(f.v2)+" downto "+str(f.v1)+"));\n"    
    elif f.ftype=="std_logic":
      p+="  res."+f.fname+" := sdin("+str(f.v1)+");\n"
    else:
      p+="  res."+f.fname+":="+f.ftype+"(sdin("+str(f.v2)+" downto "+str(f.v1)+"));\n"
  p+="  return res;\n"
  p+="end stlv_to_"+r.name+";\n\n"
p+="end "+pkg_name+";\n"

#The output file name
fout_name=pkg_name+".vhd"
fout=open(fout_name,"w")
fout.write(p)
fout.close()

