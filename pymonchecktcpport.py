#!/QOpenSys/pkgs/bin/python3
#------------------------------------------------
# Script name: pymonchecktcpport.py
#
# Description: 
# This script will check the selected host/tcp port to see if it has an active
# service running on it.
#
# Parameters:
# --host - TCP/IP host name or IP address
# Valid formats: --host=1.1.1.1  or 
#                --host 1.1.1.1     
#                --host=1.1.1.1
#                --host "1.1.1.1"
#
# --port - TCP/IP port to check
# Ex: --port=80  - Scan TCP/IP port 80
#------------------------------------------------

import argparse
import sys
from sys import platform
import os
import os.path
import re
import time
import traceback
from pathlib import Path
from datetime import date
import datetime
from configparser import ConfigParser
import socket

#------------------------------------------------
# Script initialization
#------------------------------------------------

# Initialize or set variables
appname="Check for active TCP/IP port"
exitcode=0 #Init exitcode
exitmessage=''
dashes="-------------------------------------------------------------------"
today=date.today()
curr_date = datetime.datetime.now()
parmsexpected=6;
datestamp=time.strftime("%Y%m%d")
timestamp=time.strftime("%H%M%S")
datetime2=time.strftime("%d%H%M%S")
datetime3=time.strftime("%m/%d/%y-%H%M%S")

# Create parm variables
host=""
port=""

#------------------------------------------------
# Define some useful functions
#------------------------------------------------

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

def DoesServiceExist(host,port):
    #-------------------------------------------------------
    # Function: DoesServiceExist
    # Desc: Check for TCP/IP active port
    # https://stackoverflow.com/questions/14110841/how-do-i-test-if-there-is-a-server-open-on-a-port-with-python
    # :host: TCP/IP host name/ip
    # :port: TCP/IP port
    # :return: True-Service exists, False-Service does not exist
    #-------------------------------------------------------

   captive_dns_addr = ""
   host_addr = ""

   # Check for non-existent domain host name. Some DNS servers will return an IP address
   # if they have a service running, so this will return that IP address if so.
   # We can then check that IP address against what we get when we do a 
   # getbyhostname with the actual host name
   try:
     # Get the ip address for invalid host. 
     captive_dns_addr=socket.gethostbyname("BlahThisDomaynDontExist22.com") 
   except:
      # Continue 
      pass 

   # Let's see if our selected host exists now
   try:

    # Get IP address for our selected host
    host_addr = socket.gethostbyname(host)
    print(f"TCP/IP host IP address: {host_addr}")

    # If bogus host IP and actual IP match, our host name is probably invalid
    # or possibly offline ?
    if (captive_dns_addr == host_addr):
       return False
  
    # Now lets's check our actual host and port 
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.settimeout(1)
    s.connect((host,port))
    s.close()

   except:
    # Something happened. Return false  
    # Could add detailed exception messages here if desired.
    return False

   # All good, return true  
   return True

#------------------------------------------------
# Main script logic
#------------------------------------------------

# Output messages to STDOUT for logging
print(dashes)
print(appname)
print("Start of Main Processing - " + time.strftime("%H:%M:%S"))
print("OS:" + platform)

try: # Try to perform main logic      

   # Set up the command line argument parsing.
   # If the parse_args function fails, the program will
   # exit with an error 2. In Python 3.9, there is 
   # an argument to prevent an auto-exit
   # Each argument has a long and short version
   parser = argparse.ArgumentParser()
   parser.add_argument('-s','--host', required=True,help="TCP/IP host name or IP address to check")
   parser.add_argument('-p','--port', required=True,help="TCP/IP port to check")
   # Parse the command line arguments 
   args = parser.parse_args()

   # Pull arguments into variables so they are meaningful
   host=args.host.strip()
   port=args.port.strip()
 
   # Argument parsing is done. Let's do some work
   # In our case we will just PRINT the variables 
   # to the console. Good for debugging or logging
   print(dashes)
   print("Parameters:")
   print(f"TCP/IP host: {host}")
   print(f"TCP/IP port: {port}")

   # Check for app running on selected port
   rtn1 = DoesServiceExist(host,int(port))
   
   if (rtn1==True):
      msg = f"TCP/IP service exists on {host}:{port}"
      print (msg)
   else:
      msg = f"TCP/IP service does NOT exist on {host}:{port}"
      print (msg)
      raise Exception(msg) 

   # Set success info
   exitcode=0
   exitmessage=msg

#------------------------------------------------
# Handle Exceptions
#------------------------------------------------
# System Exit occurred. Most likely from argument parser
except SystemExit as ex:
     #print("Command line argument error.")
     #######print("Command line arguments triggered script exit.")
     exitcode=ex.code # set return code for stdout
     exitmessage=str(ex) # set exit message for stdout
     ###Enable the following for detailed trace
     ###print('Traceback Info') # output traceback info for stdout
     ###traceback.print_exc()      

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
     print("")
     print(dashes)
     print('ExitCode:' + str(exitcode))
     print('ExitMessage:' + exitmessage)
     print("End of Main Processing - " + time.strftime("%H:%M:%S"))
     print(dashes)
