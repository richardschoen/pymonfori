# pymonfori
Python Network or Process Monitoring Scripts for IBM i 

This repository will be used to share various Python based system monitoring scripts for IBM i systems.

The goal would be that developers and system admins can monitor various services by creating Python scripts and calling them from a QSH/PASE script or from an IBM i process via a CL, RPG or COBOL program using the QSHEXEC/QSHPYRUN commands that are part of the QShell on IBM i command wrappers. https://www.github.com/richardschoen/qshoni

# Available samples

### pymonping.py - Ping site by host or ip address to see if active. 

Example to ping google.com
```
python3 pymonping.py --host=google.com
```
Example to ping DSN host 8.8.8.8 with only 3 packets
```
python3 pymonping.py --host=8.8.8.8  --packets=3
```

### pymonhttp.py - Check web site to make sure site is up or down. Can also scan response data for a selected value.

Example to check if google.com is online using ssl security. Same as https://www.google.com
```
python3 pymonhttp.py --host=www.google.com --secure=True
```
Example to check if google.com is online and scan for the word "clientWidth in the results
```
python3 pymonhttp.py  --host=www.google.com --echoresults=true  --secure=false  --scanvalue=clientWidth --scanresults=true
```

### pymondirsize.py - This script processes a directory and all subdirectories to calculate size. Optionally the script can output just the total bytes or it can also list each individual file in a pipe (|) delimited list along with a running total to quickly identify when a large file has been encounterd because the total goes up rapidly.

Example to get the size of the /tmp directory. DO not list any file names, just the total bytes found
```
python3 pymondirsize.py  --dirname=/tmp  --dirtype=ifs  -listfile=false
```
Example to get the size of the QGPL library using IFS path name. List file and other object names and the total bytes found
```
python3 pymondirsize.py  --dirname=/QSYS.LIB/QGPL.LIB  --dirtype=ifs  --listfile=true
```
Example to get the size of the QGPL library using library name only. List file and other object names and the total bytes found
```
python3 pymondirsize.py  --dirname=QGPL  --dirtype=library  --listfile=true
```


# Feedback
If you have an idea for a specific command, please open an issue with your request.
