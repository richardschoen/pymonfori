#!/QOpenSys/pkgs/bin/python3
#------------------------------------------------
# Script name: pygetcurrentip.py
#
# Description: 
# This script will get your current public IP address.
#
# Parameters
# None
#------------------------------------------------
import requests
import json

def get():
    endpoint = 'https://ipinfo.io/json'
    response = requests.get(endpoint, verify = True)

    if response.status_code != 200:
        return 'Status:', response.status_code, 'Problem with the request. Exiting.'
        exit()

    data = response.json()

    return data['ip']

#get my ip
my_ip = get()

#print my ip
print(my_ip)
