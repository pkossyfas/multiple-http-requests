#!/usr/bin/python
import argparse
import csv
from jinja2 import Environment, FileSystemLoader
import requests
import yaml
import logging
import time

def getParameters():
    '''
        getParameters parses the command-line parameters 
    '''
    argparser = argparse.ArgumentParser('Executes multiple http post requests based on a given csv file')
    argparser.add_argument('-u', '--url', help='Input the endpoint (url)', required=False)
    argparser.add_argument('-c', '--config-file', help='Input the configuration file the headers and/or the url', required=False, default='config.yml')
    argparser.add_argument('-t', '--body', help='Input the template body with variables same as the first line of the csv file (in jinja2 format)', required=False, default='body.j2')
    argparser.add_argument('-f', '--file', help='Input csv file with the variable names in the first line', required=True)
    argparser.add_argument('-d', '--delimiter', help='Input the csv delimiter (default csv delimiter \';\')', required=False, default=';')
    return argparser.parse_args()

def fetchData(file, d):
    '''
        fetchData opens the given file, and returns a list with the data 
    '''
    data = []
    with open(file, 'r') as csvFile:
        reader = csv.reader(csvFile, delimiter=d)
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
    except Exception as e:
        logging.error('Configuration file is missing.')

def postRequest(url, body, headers):
    '''
        postRequest performs a POST HTTP request
    '''
    return requests.post(url, data=body, headers=headers)
    
if __name__ == '__main__':
    # initializing the logger, log file will be created
    logging.basicConfig(filename='multi-post-requests.log',
                        format='%(asctime)s.%(msecs)03d | %(levelname)s | %(message)s', 
                        filemode='w', 
                        level=logging.INFO)
    # parsing the given arguments
    parameters = getParameters()
    csvfile = parameters.file
    ymlfile = parameters.config_file
    body = parameters.body
    delim = parameters.delimiter
    
    print("Starting at " + time.strftime("%c") + ' UTC')
    logging.info("Starting at " + time.strftime("%c") + ' UTC')
    # reading yml file
    print("Reading yaml file for parameters (url/headers)...")
    logging.info("Reading yaml file for parameters (url/headers)...")
    data = loadYaml(ymlfile)

    if parameters.url is None:
        url = data['endpoint']
    else:
        url = parameters.url

    if not url.startswith( 'http://' ):
        url =  'http://' + url

    mydata = fetchData(csvfile, delim)

    ll = fetchDict(mydata)

    file_loader = FileSystemLoader('.')
    env = Environment(loader=file_loader)
    template = env.get_template(body)

    for item in ll:
        output = template.render(**ll[item]) 
        r = postRequest(url, output, data['Headers'])
        print(r.text)

    print("Finished at " + time.strftime("%c"))
    logging.info("Finished at " + time.strftime("%c"))
