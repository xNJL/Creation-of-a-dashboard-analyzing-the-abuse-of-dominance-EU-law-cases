import json, csv, os, itertools, requests
import pandas as pd

french_letters = {'u00e7':'c', 'u00e9':'e', 'u00f1': 'n', 'u20ac':'', 'u00a3': '', 'u00f6': 'o', 'u00e0': 'a', 'u00f3': 'o', 'u00fc': 'u'}

os.chdir('C:\\Users\\rdangelo\\Desktop')
keywords = ['appeal unfounded', 'against penalty, successful',
           'against penalty, unfounded', 'inadmissible-appeal',
           'against penalty', 'successful', 
           'annullment-unfounded','annulment successful', 'annullment', 'inadmissible-action',
           'for damages, successful', 'failure to fulfil obligations, successful',
           'for damages, unfounded', 'failure to act, inadmissible',
           'failure to act, successful', 'damages, inadmissible',
           'judgment delivered after back reference', 'Action for failure to act - decision unnecessary',
           'Action for annulment - decision unnecessary', 'Action for failure to fulfill obligations - unfounded',
           'Action for failre to act - unfounded']

#create dictionary of pr codes
pr_dict = {'appeal unfounded':'PVOI=RF', 'against penalty, successful':'SANC%3DOB',
           'against penalty, unfounded':'SANC%3DRF', 'inadmissible-appeal':'PVOI%3DRI',
           'against penalty':'SANC', 'successful':'PVOI%3DOB', 
           'annullment-unfounded':'ANNU=RF','annulment successful':'ANNU=OB', 'annullment':'ANNU', 'inadmissible-action':'ANNU%3DRI',
           'for damages, successful':'RESP%3DOB', 'failure to fulfil obligations, successful':'CONS%3DOB',
           'for damages, unfounded':'RESP%3DRF', 'failure to act, inadmissible':'CARE%3DRI',
           'failure to act, successful':'CARE%3DOB', 'damages, inadmissible':'RESP%3DRI',
           'judgment delivered after back reference':'RENV', 'Action for failure to act - decision unnecessary':'CARE%3DNL',
           'Action for annulment - decision unnecessary':'ANNU%3DNL', 'Action for failure to fulfill obligations - unfounded':'CONS%3DRF',
           'Action for failre to act - unfounded':'CARE%3DRF'}

def date_formatter(date):
    '''This function transform the dates from how it is in EUR-LEX in how it is readed by Kibana
    '''
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    date = date.split(';')[0]
    if '(' in date:
        date = date.split('(')[1]
        date = date.strip(')')
    date = date.strip()
    if len(date) == 4:
        return date+'-01-01'
    date = date.strip()
    date = date.replace(',', '')
    date = date.split(' ')
    
    if len(date) == 2:
        d = ['01']
        d.extend(date)
        date = d  
    
    if len(date[0]) > 2:
        date[0], date[1] = date[1], date[0]
    month = date[1]
    month = str(months.index(month) + 1)
    if len(month) < 2:
        month = '0'+ month
    if len(date[0]) < 2:
        date[0] = '0'+ date[0]
    date = date[2] + '-' + month +'-'+ date[0]
    return date

def create_dict():
    ''' This function creates a dictionary with the data extracted from wikipedia and as keys the company names
    '''
    file = open('C:\\Users\\rdangelo\\Desktop\\final_data.txt', encoding = 'utf-8')
    text = file.readlines()
    #clean the list
    t = []
    for i in range(len(text)):
        if text[i] != '\n':
            t.append(text[i])
    for i in range(len(t)):
        t[i] = t[i].strip('\n')
        t[i] = t[i].strip(' :')
        t[i] = t[i].replace('\'', '')
        
    d = dict(itertools.zip_longest(*[iter(t)] * 2, fillvalue=""))
    d = clean_values(d)
    file.close()
    return d

def geolocalizzatore(city):
    ''' Uses google API to get latitude and longitude of headquarters
    '''
    url = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {'sensor': 'false', 'address': city}
    r = requests.get(url, params=params)
    results = r.json()['results']
    location = results[0]['geometry']['location']
    return location

def clean_values(d):
    '''This function create a single dictionary that has as value the JSON string representing the company
    '''
    keys = ['Headquarter','Operating income','Number of employees','Total equity','Total assets','Founded','Net income', 'Industry']
    l = list(d.keys())
    final_d = dict()
    for i in l:
        dict_to_dump = {'name': i.strip('"')}
        temp_string = d[i]
        temp_list = temp_string.split('"')
        for j in range(len(temp_list)):
            for k in keys:
                if k in temp_list[j] and not temp_list[j].startswith(', , ,'):
                    dict_to_dump[k] = temp_list[j+2].split('[')[0]
    
        int_key = 'Number of employees'
        try:
            value = dict_to_dump[int_key]
            noises = ['worldwide','Approximately', 'ca.', '~', 'as of 2016']
            for noise in noises:
                value = value.replace(noise,'')
            if '–' in value:
                value = value[0]
            value = value.split('(')[0]
            value = value.replace(',','')
            if value == '58 271 ':
                value = 58271
            if value == '40 000':
                value = 40000
            
            value = float(value) // 1

            dict_to_dump[int_key] = int(value)
                        
        except:
            pass
        
        try:
            city = dict_to_dump['Headquarter']
            for count in range(10):
                try:
                    location = geolocalizzatore(city)
                except:
                    pass
            dict_to_dump['location'] = str(location['lat'])+','+str(location['lng'])
        except:
            pass
            
        try:
            date = dict_to_dump['Founded']
            dict_to_dump['Founded'] = date_formatter(date)
        except:
            try:
                del dict_to_dump['Founded']
            except:
                pass
        
        stringOfJsonData = json.dumps(dict_to_dump)
        final_d[i.strip('"')] = stringOfJsonData
        
    return final_d

output = create_dict()
file = open('companies.json', 'a')
companies = list(output.keys())
print(len(companies))
for i in range(len(companies)):
    line = '{"index":{"_id":"'+str(i)+'"}}\n'
    file.write(line)
    file.write(output[companies[i]]+'\n')
file.write('\n')
file.close()

