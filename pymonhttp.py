#!/QOpenSys/pkgs/bin/python3
#------------------------------------------------
# Script name: pymonhttp.py
#
# Description: 
# This script can connect to an http/https site using Python curl-like package httpie.  
# We can simply check for site being active or can scan a response results for values.
# This is good for simple site monitoring. httpie supports several options. 
# This scsript could be adapted to use curl as well. 
#
# Parameters:
# --host - Host name to ping. Can omit the http/https. That is handle by the --secure parm.  Ex: Use google.com instead of https://google.com 
# --timeout - Timeout in seconds. Default=3
# --secure - Use https. True/False Default=False
# --scanresults - Scan http response results for a selected text value to make sure we have a good site. True-Scan results, False-Simply do an active site check.
# --scanvalue - Text value to scan results for if scanresults enabled.
# --ignorecase - Ignore case when scanning results if scanning results enabled. True/False Default=True
# --echoresults - Echo results to command line/stdout. If you want to capture the HTTP resonse or are debugging.
#
# Pip packages needed:
# https://pypi.org/project/httpie - pip3 install httpie
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
import subprocess


#------------------------------------------------
# Script initialization
#------------------------------------------------

# Initialize or set variables
exitcode=0 #Init exitcode
exitmessage=''
parmsexpected=6;
cmd=""

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
   parser.add_argument('--timeout',default="3",required=False,help="Timeout. Default=3 seconds")   
   parser.add_argument('--secure',default=False,required=False,help="Use https instead og http")
   parser.add_argument('--scanresults',default=False,required=False,help="Scan response results for text value. Just check site up or down. Default=False")   
   parser.add_argument('--scanvalue',default="",required=False,help="Scan for text value in valid response. Default=blanks")
   parser.add_argument('--ignorecase',default=True,required=False,help="Ignore case when scanning for value. Default=True")   
   parser.add_argument('--echoresults',default=False,required=False,help="Echo results to stdout. Default=False")   
   # Parsse the command line arguments 
   args = parser.parse_args()

   # Set work variables from args
   host=args.host
   secure=str2bool(str(args.secure))
   timeout=args.timeout
   ignorecase=str2bool(str(args.ignorecase))
   scanvalue=args.scanvalue
   echoresults=str2bool(str(args.echoresults))
   scanresults=str2bool(str(args.scanresults))   

   # Template commands
   # use http or https
   if (secure):
      cmdtemplate=f"https {host}  --timeout {timeout}"
   else:
      cmdtemplate=f"http {host}  --timeout {timeout}"

   # Set command to run via tempate
   cmd=cmdtemplate
   
   # Echo parms - only enable for testing
   print(f"host: {host}")
   print(f"secure: {secure}")
   print(f"cmd: {cmd}")
   print(f"scanvalue: {scanvalue}")

   # Run the external http or https command line using HTTPIe (HTTPIe must be installed)
   proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True) 

   # Get stdout info from subprocess command
   (out, err) = proc.communicate() 

   # Subprocess return code
   subrtncode = proc.poll() 

   # Bail if subprocess return code wasn't 0 for success
   if (subrtncode!=0):
      raise Exception(f"Http call failed with return code: {subrtncode}")

   # Echo HTTP results to console if enabled
   if (echoresults):
      print("subprocess output:", out)

   # Move results to string variable 
   outstr=str(out)

   #Equalize case if ignoring case    
   if (ignorecase):
       outstr=outstr.lower()
       scanvalue=scanvalue.lower()
   
   # If enabled, scan for string value in results and bail if not found
   if (scanresults):
      foundindex = outstr.find(scanvalue) #Locate substring
      if (foundindex < 0):
         raise Exception(f"{scanvalue} Not found in http call response data. Process cancelled.")           
        
      # Set success info
      exitcode=0
      exitmessage=f"Http call completed successfully. {scanvalue} found in response."
   else:
      # Set success info
      exitcode=0
      exitmessage=f"Http call completed successfully. Site {host} appears to be responding."
        
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
