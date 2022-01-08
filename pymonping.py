#!/QOpenSys/pkgs/bin/python3
#------------------------------------------------
# Script name: pymonping.py
#
# Description: 
# This script pings a selected host using the CL based PING command.  
# QSH/PASE does not have a ping command which is odd but true.
#
# Parameters:
# --host - Host name to ping
# Valid formats: --inputfile=filename.txt  or 
#                --inputfile filename.txt     
#                --inputfile="filename.txt"
#                --inputfile "filename.txt"
#
# --packets - number of packets
# Valid formats: --packets=3 
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
parmsexpected=6;
host=""
packets=3

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


#------------------------------------------------
# Main script logic
#------------------------------------------------
try: # Try to perform main logic      

   # Set up the command line argument parsing
   # If the parse_args function fails, the program will
   # exit with an error 2. In Python 3.9, there is 
   # an argument to prevent an auto-exit
   parser = argparse.ArgumentParser()
   parser.add_argument('--host', required=True,help="Host name or ip address to ping is required")
   parser.add_argument('-p','--packets',default="3",required=False,help="Number of packets")   
   # Parsse the command line arguments 
   args = parser.parse_args()

   # Convert args to variables
   host=args.host
   packets=args.packets

   # Template commands
   # Run ping and send escape on errors
   cmdtemplate=f"PING RMTSYS('{host}')  MSGMODE(*VERBOSE *ESCAPE) NBRPKT({packets}) WAITTIME(1)"

   # Argument parsing is done. Let's do some work
   print(f"host: {host}")

   # Run CL command
   cmd = "system -v \"" + cmdtemplate + "\""
   rtnsys=os.system(cmd)
   ##rtnsys=os.system(f"system -v \'{srctemplate}\'")
   
   if rtnsys != 0:
      raise Exception('Error occurred running PING command. Process cancelled.')           
      
   # Set success info
   exitcode=0
   exitmessage='Completed successfully'

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
