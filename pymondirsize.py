#!/QOpenSys/pkgs/bin/python3
#------------------------------------------------
# Script name: pymondirsize.py
#
# Description:
# This script processes a directory and all subdirectories to calculate size.
# The script can output just the total bytes or it can also list each individual file
# in a pipe (|) delimited list along with a running total to quickly identify when a large 
# file has been encounterd because the total goes up rapidly.
#
# Parameters:
# --dirname - IFS directory name if ifs option used or 10 character library name if lib option is used.
# --dirtype - Directory type. ifs=IFS directory path, lib or library=10 character IBM i library name format. Default=ifs
# --listfiles - Output detailed list of files and sizes including running total to quickly identify where large files may exist 
#               in the directory. True=List all files,False=Don't list all files. Default=False
#
# Pip packages needed:
# None - argparse is a standard module.
#
# Returns:
# Exits with 0 on success or 99 on errors.
# This allows us to communicate back to command line with an appropriate return code.
#
#------------------------------------------------
# Web Links
# http://zetcode.com/python/argparse/
# https://stackoverflow.com/questions/5943249/python-argparse-and-controlling-overriding-the-exit-status-code
# https://www.techbeamers.com/use-try-except-python/
# argument parse exceptions
# https://stackoverflow.com/questions/8107713/using-argparse-argumenterror-in-python
#------------------------------------------------

import argparse
import sys
from sys import platform
import os
import re
import time
import traceback


#------------------------------------------------
# Script initialization
#------------------------------------------------

# Initialize or set variables
exitcode=0 #Init exitcode
exitmessage=''

#Output messages to STDOUT for logging
print("-------------------------------------------------------------------------------")
print("Script: " + sys.argv[0])
print("Start of Main Processing - " + time.strftime("%H:%M:%S"))
print("OS:" + platform)

def str2bool(strval):
    #-------------------------------------------------------
    # Function: str2bool
    # Desc: Constructor
    # :strval: String value for true or false
    # :return: Return True if string value is" yes, true, t or 1
    #-------------------------------------------------------
    return strval.lower() in ("yes", "true", "t", "1")

def trim(strval):
    #-------------------------------------------------------
    # Function: trim
    # Desc: Alternate name for strip
    # :strval: String value to trim. 
    # :return: Trimmed value
    #-------------------------------------------------------
    return strval.strip()

def rtrim(strval):
    #-------------------------------------------------------
    # Function: rtrim
    # Desc: Alternate name for rstrip
    # :strval: String value to trim. 
    # :return: Trimmed value
    #-------------------------------------------------------
    return strval.rstrip()

def ltrim(strval):
    #-------------------------------------------------------
    # Function: ltrim
    # Desc: Alternate name for lstrip
    # :strval: String value to ltrim. 
    # :return: Trimmed value
    #-------------------------------------------------------
    return strval.lstrip()


def getdirsize(start_path = '.',list_files=False):
    #-------------------------------------------------------
    # Function: getdirsize
    # Desc: Crawl directory and return size of all files and objects
    # :return: Total size of directory contents
    #-------------------------------------------------------
    total_size = 0
    firstrecord=True
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                file_size = os.path.getsize(fp)
                total_size += file_size
                # List file names and size info to console if enabled
                if (list_files):
                   
                   # Write headings on first record
                   if (firstrecord):
                      print(f"filepath|filesize|totalsize")
                      firstrecord=False
                      
                   # Write out file path and size   
                   print(f"{fp}|{file_size}|{total_size}")

    return total_size


#------------------------------------------------
# Main script logic
#------------------------------------------------
try: # Try to perform main logic

   # Set up the command line argument parsing
   # If the parse_args function fails, the program will
   # exit with an error 2. In Python 3.9, there is
   # an argument to prevent an auto-exit
   parser = argparse.ArgumentParser()
   parser.add_argument('--dirname', required=True,help="Directory name. Specify IFS path name if dirtype=ifs. If dirtype=library, specify just the library name.")
   parser.add_argument('--listfiles',default=False,required=False,help="List file names")   
   parser.add_argument('--dirtype',default="ifs",required=False,help="Directory naming ifs/library")   
   # Parse the command line arguments
   args = parser.parse_args()

   # Convert args to variables
   dirtype=args.dirtype
   dirname=args.dirname   
   
   # If library format path with /QSYS.LIB/LIBNAME.LIB notation
   if (dirtype.lower()=="lib" or dirtype.lower()=="library"):   
      dirname=f"/QSYS.LIB/{dirname}.LIB"
      dirname=dirname.upper()
   else:
      dirname=args.dirname
      
   listfiles=str2bool(str(args.listfiles))

   #Output IFS path to list
   print(f"IFS dir path to list: {dirname}")

   # Bail if directory not found
   if not (os.path.isdir(dirname)):
      raise Exception(f"{dirname} not found. Process cancelled.")

   # Process directory and return size
   totsize=getdirsize(dirname,listfiles)
   print(f"Total Size: {totsize} bytes")
      
   # Set success info and output total size
   exitcode=0
   exitmessage=f"Total Size: {totsize} bytes"

#------------------------------------------------
# Handle Exceptions
#------------------------------------------------
# System Exit occurred. Most likely from argument parser
except SystemExit as ex:
     print("Command line argument error.")
     exitcode=ex.code # set return code for stdout
     exitmessage=str(ex) # set exit message for stdout
     print('Traceback Info') # output traceback info for stdout
     traceback.print_exc()      

except argparse.ArgumentError as exc:
     exitcode=99 # set return code for stdout
     exitmessage=str(exc) # set exit message for stdout
     print('Traceback Info') # output traceback info for stdout
     traceback.print_exc()      
     sys.exit(99)

except Exception as ex: # Catch and handle exceptions
     exitcode=99 # set return code for stdout
     exitmessage=str(ex) # set exit message for stdout
     print('Traceback Info') # output traceback info for stdout
     traceback.print_exc()        
     sys.exit(99)
#------------------------------------------------
# Always perform final processing
#------------------------------------------------
finally: # Final processing
     # Do any final code and exit now
     # We log as much relevent info to STDOUT as needed
     print('ExitCode:' + str(exitcode))
     print('ExitMessage:' + exitmessage)
     print("End of Main Processing - " + time.strftime("%H:%M:%S"))
     print("-------------------------------------------------------------------------------")
     
     # Exit the script now
     sys.exit(exitcode) 
