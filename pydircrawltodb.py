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
#                 Note: Don't specify QTEMP as a library. Use a non-job related library.
# --followsymlinks - Follow symbolic links. True/False, Default-False
# --skipqsyslib - Skip QSYS.LIB objects. True/False, Default-False
# --printsql - Print SQL statements for debugging. True/False, Default-False
#                     
# Process steps:
# -Create/replace DB2 table and clear it
# -Crawl dir and write entries to DB2 table
#
# Modifications:
# - 8/31/2023 - Added create, modify and access times. Note: Create time in unix is the actual last attribute change so it is 
#   likely to change if a file permission or other attribute changes. Co you should relay on modify and access times
#   for any real work unless you trust your creation times. 
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
from datetime import datetime, timezone 

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
    
def strdoubleqt(instring):
    #-------------------------------------------------------
    # Function: strdoubleqt
    # Desc: Double up single quotes
    # :param instring: String parm value
    # :return: string return value
    #-------------------------------------------------------
    workval=instring
    try:
      # Double up the single quotes
      workval=instring.replace("'", "''" )
      return workval
    except Exception as e:
      # Send back original string on error
      return instring
      
def strreplace(instring,replaceval,replacewithval):
    #-------------------------------------------------------
    # Function: strreplace
    # Desc: Double up single quotes
    # :param instring: String parm value
    # :return: string return value
    #-------------------------------------------------------
    workval=instring
    try:
      # Double up the single quotes
      workval=instring.replace(replaceval,replacewithval)
      return workval
    except Exception as e:
      # Send back original string on error
      return instring
      
def strstripqt(instring):
    #-------------------------------------------------------
    # Function: strstripqt
    # Desc: Strip single quotes
    # :param instring: String parm value
    # :return: string return value
    #-------------------------------------------------------
    workval=instring
    try:
      # Double up the single quotes
      workval=instring.replace("'", "" )
      return workval
    except Exception as e:
      # Send back original string on error
      return instring      

def insert_dircrawl(cursor,table,ifsfull,ifsfile,ifsprefix,ifsext,ifssize,ifstype,ifssymlnk,ifscrttime,ifsmodtime,ifsacctime,printsql):
    #----------------------------------------------------------
    # Function: insert_dircrawl
    # Desc: Insert new record into directory crawler table
    # :return: Result value from query
    #----------------------------------------------------------
    try:
       # Create the SQL statement 
       sql = """insert into %s (ifsfull,ifsfile,ifsprefix,ifsext,ifssize,ifstype,ifssymlnk,ifscrttime,ifsmodtime,ifsacctime) VALUES('%s','%s','%s','%s',%s,'%s','%s','%s','%s','%s')""" % (table,ifsfull,ifsfile,ifsprefix,ifsext,ifssize,ifstype,ifssymlnk,ifscrttime,ifsmodtime,ifsacctime)
       # Insert the record
       # Note: self parm not needed for execute when internal class function called
       # Print SQL only if enable for debugging
       if (printsql==True):
          print(sql)
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
       sql = """create table %s (IFSFULL VARCHAR(1024),IFSFILE VARCHAR(1024),IFSPREFIX VARCHAR(1024),IFSEXT VARCHAR(100),IFSSIZE DECIMAL(15,2),IFSTYPE VARCHAR(10),IFSSYMLNK VARCHAR(10),IFSCRTTIME TIMESTAMP,IFSMODTIME TIMESTAMP,IFSACCTIME TIMESTAMP)""" % (table)
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
      parser.add_argument('--printsql',default=False,required=False,help="Print SQL statements for debugging (True/False-Default)")


      # Parse the command line arguments
      args = parser.parse_args()

      # Convert args to variables
      dirname=args.dirname
      outputtable = args.outputtable   
      followsymlinks = str2bool(str(args.followsymlinks))
      skipqsyslib = str2bool(str(args.skipqsyslib))
      printsql = str2bool(str(args.printsql))

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
      parmprintsql=printsql #Print SQL

      print("Top level dir: " + parmdirname)
      print("Output file: " + parmoutputtable)
      ##print("Replace output file: " + str(parmreplaceoutputtable))
      print("Follow symbolic links: " + str(parmfollowlinks))
      ##print("Field delimiter: " + str(parmdelimiter))
      print("Skip /QSYS.LIB path: " + str(parmskipqsyslib))
      print("Print SQL statements: " + str(parmprintsql))

      # Make sure source dir exists
      if os.path.isdir(parmdirname)==False:
         raise Exception('Directory ' + parmdirname + ' not found. Process cancelled.')          

      # Capture top level directory info into table
      fullname=parmdirname
      
      basename=os.path.basename(fullname)
      
      if os.path.islink(fullname):
         file_size=0
      else:     
         file_stats=os.stat(fullname)
         file_size=file_stats.st_size

      # Build full file path
      fullname=strstripqt(fullname) #Double up single quotes if any
      ###fullname=strreplace(fullname," ","_") # Get rid of spaces
      split1=os.path.splitext(fullname)

      basename=strstripqt(basename) #Double up single quotes if any
      ###basename=strreplace(basename," ","_") # Get rid of spaces

      # Get create, modify and access times                  
      filecreatetime=file_stats.st_ctime # Time of last status change (attributes,create)
      fileaccesstime=file_stats.st_atime # Time of last file access 
      fileupdatetime=file_stats.st_mtime # Time of last file modification/change
      filecreatetime=datetime.fromtimestamp(file_stats.st_ctime).strftime('%Y-%m-%d-%H.%M.%S.000000')
      filemodifytime=datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d-%H.%M.%S.000000')
      fileaccesstime=datetime.fromtimestamp(file_stats.st_atime).strftime('%Y-%m-%d-%H.%M.%S.000000')

      # Insert first directory record for top level        
      print(fullname) #Debug 
      rtnins=insert_dircrawl(cur1,outputtable,fullname,"","","",0,"dir",str(os.path.islink(fullname)),
                            filecreatetime,filemodifytime,fileaccesstime,parmprintsql)

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
              fullname=strstripqt(fullname) #Double up single quotes if any
              ###fullname=strreplace(fullname," ","_") # Get rid of spaces
              split1=os.path.splitext(fullname)

              basename=strstripqt(basename) #Double up single quotes if any
              ###basename=strreplace(basename," ","_") # Get rid of spaces

              # Get create, modify and access times                  
              filecreatetime=file_stats.st_ctime # Time of last status change (attributes,create)
              fileaccesstime=file_stats.st_atime # Time of last file access 
              fileupdatetime=file_stats.st_mtime # Time of last file modification/change
              filecreatetime=datetime.fromtimestamp(file_stats.st_ctime).strftime('%Y-%m-%d-%H.%M.%S.000000')
              filemodifytime=datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d-%H.%M.%S.000000')
              fileaccesstime=datetime.fromtimestamp(file_stats.st_atime).strftime('%Y-%m-%d-%H.%M.%S.000000')

              # Insert record        
              print(fullname) #Debug 
              rtnins=insert_dircrawl(cur1,outputtable,fullname,basename,os.path.basename(split1[0]),split1[1],file_size,"file",
                                    str(os.path.islink(fullname)),filecreatetime,filemodifytime,fileaccesstime,parmprintsql)

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

              fulldir=strstripqt(fulldir) #Double up single quotes if any
              fulldir=strreplace(fulldir," ","_") # Get rid of spaces

              # Get create, modify and access times                  
              filecreatetime=file_stats.st_ctime # Time of last status change (attributes,create)
              fileaccesstime=file_stats.st_atime # Time of last file access 
              fileupdatetime=file_stats.st_mtime # Time of last file modification/change
              filecreatetime=datetime.fromtimestamp(file_stats.st_ctime).strftime('%Y-%m-%d-%H.%M.%S.000000')
              filemodifytime=datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d-%H.%M.%S.000000')
              fileaccesstime=datetime.fromtimestamp(file_stats.st_atime).strftime('%Y-%m-%d-%H.%M.%S.000000')

              # Insert record. We are not capturing directory object size right now.
              # If you need to do so, write dir_size instead of 0 on this record
              print(fulldir) #Debug 
              rtnins=insert_dircrawl(cur1,outputtable,fulldir,"","","",0,"dir",str(os.path.islink(fulldir)),
                                    filecreatetime,filemodifytime,fileaccesstime,parmprintsql)

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

