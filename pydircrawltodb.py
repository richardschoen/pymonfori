#!/QOpenSys/pkgs/bin/python3
#------------------------------------------------
# Script name: pydircrawltodb.py
#
# Description: 
# This script will crawl a directory structure and 
# output all the file info to a DB2 table so the 
# info can be analyzed. This is very useful when 
# you need to locate and determine which directories
# have the largest objects. 
# This will also crawl a library in QSYS.LIB or all librarys
# to help determine a library size.
# (Ex: Crawl all libraries, specify directory: /QSYS.LIB)
# (Ex: Crawl QGPL library, specify directory: /QSYS.LIB/QGPL.LIB)
#
# Parameters
# --dirname - Top level directory path to start from (Ex: / Root)
# --outputtable - Output DB2 table for IFS listing (Ex: TMP.DIRCRAWL)
# --followsymlinks - Follow symbolic links. True/False, Default-False
# --skipqsyslib - Skip QSYS.LIB objects. True/False, Default-False
#                     
# Process steps:
# -Create/replace DB2 table and clear it
# -Crawl dir and write entries to DB2 table
#------------------------------------------------

#https://janakiev.com/blog/python-filesystem-analysis/
#http://www.tutorialspoint.com/python/os_walk.htm
#https://stackoverflow.com/questions/13131497/os-walk-to-crawl-through-folder-structure
#https://stackoverflow.com/questions/3771696/python-os-walk-follow-symlinks
# Write file
#https://cmdlinetips.com/2012/09/three-ways-to-write-text-to-a-file-in-python/
#File size
#https://www.journaldev.com/32067/how-to-get-file-size-in-python


import argparse
import ibm_db_dbi as db2
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
dircount=0
filecount=0
saveddir=""
totalfilesize=0

#Output messages to STDOUT for logging
print("-------------------------------------------------------------------------------")
print("Crawl directory to database table/outfile")
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

def insert_dircrawl(cursor,table,ifsfull,ifsfile,ifsprefix,ifsext,ifssize,ifstype,ifssymlnk):
    #----------------------------------------------------------
    # Function: insert_dircrawl
    # Desc: Insert new record into directory crawler table
    # :return: Result value from query
    #----------------------------------------------------------
    try:
       # Create the SQL statement 
       sql = """insert into %s (ifsfull,ifsfile,ifsprefix,ifsext,ifssize,ifstype,ifssymlnk) VALUES('%s','%s','%s','%s',%s,'%s','%s')""" % (table,ifsfull,ifsfile,ifsprefix,ifsext,ifssize,ifstype,ifssymlnk)
       # Insert the record
       # Note: self parm not needed for execute when internal class function called
       rtnexecute=cursor.execute(sql)
       # Return result value
       return rtnexecute
    except Exception as e:
       print(e)  
       return -2 # return -2 on error 

def drop_dircrawl(cursor,table):
    #----------------------------------------------------------
    # Function: drop_dircrawl
    # Desc: Drop directory crawler table
    # :return: Result value from query
    #----------------------------------------------------------
    try:
       # Create the SQL statement 
       sql = """drop table %s""" % (table)
       # Drop the table
       # Note: self parm not needed for execute when internal class function called
       rtnexecute=cursor.execute(sql)
       if rtnexecute == True:
          print("Table " + table + " was dropped" ) 
       # Return result value
       return rtnexecute
    except Exception as e:
       print(e)  
       return -2 # return -2 on error 

def create_dircrawl(cursor,table):
    #----------------------------------------------------------
    # Function: create_dircrawl
    # Desc: Create directory crawler table
    # :return: Result value from query
    #----------------------------------------------------------
    try:
       # Create the SQL statement 
       sql = """create table %s (IFSFULL VARCHAR(256),IFSFILE VARCHAR(256),IFSPREFIX VARCHAR(256),IFSEXT VARCHAR(10),IFSSIZE DECIMAL(15,2),IFSTYPE VARCHAR(10),IFSSYMLNK VARCHAR(10))""" % (table)
       # Create the table
       # Note: self parm not needed for execute when internal class function called
       rtnexecute=cursor.execute(sql)
       if rtnexecute == True:
          print("Table " + table + " was created" ) 
       # Return result value
       return rtnexecute       
    except Exception as e:
       print(e)  
       return -2 # return -2 on error 

def execute_clcommand(cursor,clcommand):
    #----------------------------------------------------------
    # Function: execute_clcommand
    # Desc: Run IBM i CL Command
    # :return: Result value from query
    #----------------------------------------------------------
    try:
       # Create the SQL statement 
       clwork = """CALL QSYS2.QCMDEXC('%s')""" % (clcommand)
       # Run the CL command
       # Note: self parm not needed for execute when internal class function called
       rtnexecute=cursor.execute(clwork)
       # Return result value
       return rtnexecute
    except Exception as e:
        print(e)  
        return -2 # return -2 on error 

#------------------------------------------------
# Main script logic
#------------------------------------------------
try: # Try to perform main logic

      # Set up the command line argument parsing
      # If the parse_args function fails, the program will
      # exit with an error 2. In Python 3.9, there is
      # an argument to prevent an auto-exit
      parser = argparse.ArgumentParser()
      parser.add_argument('--dirname', required=True,help="Top level directory name. (Ex: / = Root)")
      parser.add_argument('--outputtable', required=True,help="Output DB2 table (LIBRARY.FILENAME)")
      parser.add_argument('--followsymlinks',default=False,required=False,help="Follow symbolic links (True/False-Default)")   
      parser.add_argument('--skipqsyslib',default=False,required=False,help="Skip QSYS.LIB (True/False-Default)")   


      # Parse the command line arguments
      args = parser.parse_args()

      # Convert args to variables
      dirname=args.dirname
      outputtable = args.outputtable   
      followsymlinks = args.followsymlinks
      skipqsyslib = args.skipqsyslib

      # Connect to DB2
      conn = db2.connect()
      conn.set_option({ db2.SQL_ATTR_TXN_ISOLATION:
                        db2.SQL_TXN_NO_COMMIT })            
      # Enable auto-commit
      ##conn.set_autocommit(True)
      # Create curson
      cur1 = conn.cursor()

      # Drop table if it exist
      rtndrop=drop_dircrawl(cur1,outputtable)
      print("Drop: " + str(rtndrop))

      # Drop table if it exist
      rtncreate=create_dircrawl(cur1,outputtable)
      print("Create: " + str(rtncreate))
      if (rtncreate != True):
         raise Exception('Unable to create table ' + outputtable + '. Process cancelled.')          

      # Set parameter work variables from command line args
      parmdirname = dirname # Top level dir to crawl
      parmoutputtable= outputtable # Delimited output text file
      ##parmreplaceoutputtable= str2bool(sys.argv[3]) # Replace output file if already found 
      parmfollowlinks= followsymlinks #Follow symbolic links
      ## parmdelimiter= sys.argv[5] # Delimiter for output file
      parmskipqsyslib= skipqsyslib #Skip /QSYS.LIB files

      print("Top level dir: " + parmdirname)
      print("Output file: " + parmoutputtable)
      ##print("Replace output file: " + str(parmreplaceoutputtable))
      print("Follow symbolic links: " + str(parmfollowlinks))
      ##print("Field delimiter: " + str(parmdelimiter))
      print("Skip /QSYS.LIB path: " + str(parmskipqsyslib))

      # Make sure source dir exists
      if os.path.isdir(parmdirname)==False:
         raise Exception('Directory ' + parmdirname + ' not found. Process cancelled.')          

      # Walk thru the directory list and output
      for root, dirs, files in os.walk(parmdirname,topdown=True,followlinks=parmfollowlinks):
          # Do whatever you need to do
          for name in files:

              # If skip paths with /QSYS.LIB enabled, don't 
              # process current file
              if '/QSYS.LIB' in root.upper() and parmskipqsyslib: 
                  continue
 
              ##print(root + "-" + name)

              fullname=os.path.join(root,name)
              
              basename=os.path.basename(fullname)
              
              if os.path.islink(fullname):
                 file_size=0
              else:     
                 file_stats=os.stat(fullname)
                 file_size=file_stats.st_size

              # Build full file path
              split1=os.path.splitext(fullname)

              # Insert record        
              rtnins=insert_dircrawl(cur1,outputtable,fullname,basename,os.path.basename(split1[0]),split1[1],file_size,"file",str(os.path.islink(fullname)))

              # Make sure record insert succeeds
              if (rtnins != True ):
                 raise Exception('Error inserting file/link record to  ' + outputtable + ' . Process cancelled.')          

              # Increment file/object counter
              filecount = filecount + 1 

              # Increment total file size for selected path 
              totalfilesize=totalfilesize + file_size

          for name in dirs:

              # If skip paths with /QSYS.LIB enabled, don't 
              # process current file
              if '/QSYS.LIB' in root.upper() and parmskipqsyslib: 
                  continue

              # Built full directory path
              fulldir=os.path.join(root,name)

              if os.path.islink(fulldir):
                 dir_size=0
              else:     
                 file_stats=os.stat(fulldir)
                 dir_size=file_stats.st_size

              # Insert record. We are not capturing directory object size right now.
              # If you need to do so, write dir_size instead of 0 on this record
              rtnins=insert_dircrawl(cur1,outputtable,fulldir,"","","",0,"dir",str(os.path.islink(fulldir)))

              # Make sure record insert succeeds
              if (rtnins != True ):
                 raise Exception('Error inserting directory record to  ' + outputtable + ' . Process cancelled.')          

              # Save dir so we can skip last directory output
              saveddir = fulldir

              # Increment directory counter
              dircount = dircount + 1 

      # Close DB2 table
      conn.close()

      # Print file and dir counts
      print("Directory count: " + str(dircount))
      print("File count: " + str(filecount))
      print("Total file size: " + str(totalfilesize))

      # Set success info
      exitcode=0
      exitmessage='Completed successfully'

#------------------------------------------------
# Handle Exceptions
#------------------------------------------------
except Exception as ex: # Catch and handle exceptions
   exitcode=99 # set return code for stdout
   exitmessage=str(ex) # set exit message for stdout
   print('Traceback Info') # output traceback info for stdout
   traceback.print_exc()        

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

