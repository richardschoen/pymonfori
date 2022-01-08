# pymonfori
Python Network or Process Monitoring Scripts for IBM i 

This repository will be used to share various Python based system monitoring scripts for IBM i systems.

THe goal would be that developers and system admins can monitor various services by creating Python scripts and calling them from a QSH/PASE script or from an IBM i process via a CL, RPG or COBOL program using the QSHEXEC/QSHPYRUN commands that are part of the QShell on IBM i command wrappers. https://www.github.com/richardschoen/qshoni

# Available samples

**pymonping.py** - Ping site by host or ip address to see if active. 

**pymonhttp.py** - Check web sites to make sure site is up or down. Can also scan reponse data for a selected value.

# Feedback
If you have an idea for a specific command, please open an issue with your request.
