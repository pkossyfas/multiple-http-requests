#!/usr/bin/python

import argparse
import csv
from jinja2 import Environment, FileSystemLoader
import requests
import yaml
import logging
import time
import sys

def getParameters():
    '''
        getParameters parses the command-line parameters 
    '''
    argparser = argparse.ArgumentParser('Executes multiple http post requests based on a given csv file')
    argparser.add_argument('-c', '--config-file', help='Input the configuration file (default "config.yml")', required=False, default='config.yml')
    argparser.add_argument('-u', '--url', help='Input the endpoint (url)', required=False)
    argparser.add_argument('-t', '--body', help='Input the template body with variables same as the first line of the csv file (default body.j2)', required=False, default='body.j2')
    argparser.add_argument('-f', '--file', help='Input csv file with the variable names in the first line', required=False)
    argparser.add_argument('-d', '--delimiter', help='Input the csv delimiter (default csv delimiter \';\')', required=False, default=';')
    argparser.add_argument('-H', '--header', help='Input header', required=False)
    return argparser.parse_args()

def fetchData(file, dl):
    '''
        fetchData opens the given file, and returns a list with the data 
    '''
    data = []
    with open(file, 'r') as csvFile:
        reader = csv.reader(csvFile, delimiter=dl)
        for item in reader:
            data.append(item)
    return data

def fetchDict(data):
    '''
        fetchDict transforms the given list to a dictionary with keys the first row of the list 
    '''
    d = {}
    i = 0
    for i in range(len(mydata)-1): 
        d[i] = {k: v for k, v in zip(mydata[0], mydata[i+1])}
    return d

def loadYaml(ymlfile):
    '''
        loadYaml reads data from a yml file
    '''
    try:
        with open(ymlfile, 'r') as y:
            stream = y.read()
        data = yaml.load(stream)
        return data
    except:
        print('No configuration file found. Command line arguments will be used (or the defaults).')
        logging.info('No configuration file found. Command line arguments will be used (or the defaults).')
        

def checkParameter(parameter1, parameter2):
    '''
        checkParameter returns parameter1 if exists, else it returns parameter2
    '''
    if parameter1 is None:
        return parameter2
    else:
        return parameter1
    
# def postRequest(url, body, headers):
#     '''
#         postRequest performs a POST HTTP request
#     '''
#     return requests.post(url, data=body, headers=headers)
    
if __name__ == '__main__':
    # initializing the logger, logfile will be created
    logging.basicConfig(filename='multi-requests.log',
                        format='%(asctime)s.%(msecs)03d | %(levelname)s | %(message)s', 
                        filemode='w', 
                        level=logging.DEBUG)
    print("Starting at " + time.strftime("%c") + ' UTC')
    logging.info("Starting at " + time.strftime("%c") + ' UTC')
    
    # parsing command line arguments
    parameters = getParameters()
    ymlfile = parameters.config_file
    
    # reading yml file
    print("Reading yaml file for parameters (url/headers etc.)...")
    logging.info("Reading yaml file for parameters (url/headers etc.)...")
    data = loadYaml(ymlfile)

    # reading parameters/input in variables either from configuration file (with priority) or from the command line arguments
    # endpoint
    try:
        url = checkParameter(data['endpoint'], parameters.url)
    except:
        url = parameters.url
    
    if url is None:
        print('Endpoint is missing.')
        logging.error('Endpoint is missing.')
        sys.exit(1)
 
    if not url.startswith( 'http://' ):
        url =  'http://' + url
    print(url)

    # http body
    try:
        body = checkParameter(data['body'], parameters.body)
    except:
        body = parameters.url

    if body is None:
        print('Template body is missing.')
        logging.error('Template body is missing.')
        sys.exit(1)
    print(body)

    # csv file with variables
    try:
        csvfile = checkParameter(data['csvfile'], parameters.file)
    except:
        csvfile = parameters.file

    if csvfile is None:
        print('File .csv is missing.')
        logging.error('File .csv is missing.')
        sys.exit(1)
    print(csvfile)
    
    # csv delimiter
    try:
        delim = checkParameter(data['csvdelimiter'], parameters.delimiter)
    except:
        delim = parameters.delimiter
    print(delim)

    # headers
    try:
        headers = checkParameter(data['Headers'], parameters.header)
    except:
        headers = parameters.headers
    print(headers)

    mydata = fetchData(csvfile, delim)

    ll = fetchDict(mydata)

    file_loader = FileSystemLoader('.')
    env = Environment(loader=file_loader)
    template = env.get_template(body)

    s = requests.Session()

    for item in ll:
        output = template.render(**ll[item])

        
        r = s.post(url, data=output, headers=headers) 
        # r = postRequest(url, output, data['Headers'])
        print(r.text)

    print("Finished at " + time.strftime("%c"))
    logging.info("Finished at " + time.strftime("%c"))
