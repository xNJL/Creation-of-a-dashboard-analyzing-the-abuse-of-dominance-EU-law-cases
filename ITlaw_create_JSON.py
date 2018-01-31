import json, csv, os, itertools, requests
import pandas as pd

french_letters = {'u00e7':'c', 'u00e9':'e', 'u00f1': 'n', 'u20ac':'u.s.d. ', 'u00a3': 'pounds ', 'u00f6': 'o', 'u00e0': 'a', 'u00f3': 'o', 'u00fc': 'u'}

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
    '''This is a simple function that transform the date contained in the title in the format that is accepted by Kibana. 
       This means transforming something like ‘4 January 1994’ into something like ‘1994-01-04’. 
       Obviously, the function needs to do some cleansing even before having the date written as ‘4 January 1994’.
    '''
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    date = date.split('(')[0]
    date = date.strip()
    date = date.split(' ')
    date = date[-3:]
    month = months.index(date[1])+1
    month = str(month)
    if len(month) < 2:
        month = '0'+month
    if len(date[0]) < 2:
        date[0] = '0'+date[0]
    date = date[2]+'-'+month+'-'+date[0]
    return date

def dictionary_creator(title, keyword):
    ''' This function takes a string with the titles and create a dictionary with the 
    informations from it
    They are:
        - court
        - chamber
        - type of procedure
        - date
        - appellant
        - appellee
        - market
    '''
    
    title = title[16:] # This eliminates the initial 'Judgement of the '
    title = title.split('\n')
    first_row = title[0].split(')')
    if len(first_row)>1:
        court_with_chamber = first_row[0]
        court = court_with_chamber.split('(')[0].strip()
        try:
            chamber = court_with_chamber.split('(')[1].strip()
        except:
            chamber = 'n.a.'
        date = first_row[1].strip('.')
        date = date_formatter(date)
    else:
        temp_first_row = first_row[0].split(' of ')
        date = temp_first_row[-1].strip('.')
        date = date_formatter(date)
        court = temp_first_row[0].strip()
        chamber = 'n.a.'
    
    if 'First Instance' in court:
        court = 'General Court'
    
    second_row = title[1].split(' v ')
    temp_appellant = second_row[0].split(', ')
    h = []
    for i in temp_appellant:
        h.extend(i.split(' and '))   
    appellant = str(h)[1:-1]
    appellant = appellant.replace("'", "")
    appellant = appellant.replace('"', "")
    appellant = appellant.split(',')
        
    temp_appellee = second_row[1].split(', ')
    h = []
    for i in temp_appellee:
        h.extend(i.split(' and '))   
    appellee = str(h)[1:-1]
    appellee = appellee.replace("'", '')
    appellee = appellee.strip('.')
    appellee = appellee.split(',')
        
    third_row = title[2].split('—')
    if len(third_row) == 1:
        third_row = third_row[0].split(' - ')
    market = []
    for i in third_row:
        i = i.lower()
        l = ['legislation','dominant', 'foreclosure', 'barriers', 'reserved','geographical', 'definition', 'decision', 'fixing', 'sharing', 'liberalisation', 'relevant', 'impact', 'authorisation', 'obstacles','competition', 'common', 'agreements']
        if 'market' in i and not any(word in i for word in l):
            market.append(i)
    market.append('n.a.')
    market = market[0].strip()
    d = {'court':court, 'case type': keyword, 'chamber':chamber, 'date':date, 'appellant':appellant, 'appellee':appellee, 'market':market}
    return d
    

def info_extractor(df, keyword):
    ''' This function gives a list of json strings, each containing the data that we want
    '''
    output = []
    
    for i in df['Title']:
        stringOfJsonData = json.dumps(dictionary_creator(i, keyword))
        stringOfJsonData = stringOfJsonData.replace('"{', '{')
        stringOfJsonData = stringOfJsonData.replace('}"', '}')
        stringOfJsonData = stringOfJsonData.replace('\\', '')
        weird_words = list(french_letters.keys())
        for j in weird_words:
            if j in stringOfJsonData:
                stringOfJsonData = stringOfJsonData.replace(j, french_letters[j])
        output.append(stringOfJsonData)
    return output

def extract_all(keywords):
    ''' This function loops through all the .csv file, transforms it in a Dataframe
        and calls info_extractor() on it. It collects all the strings in a list.
    '''
    output = []
    for keyword in keywords:
        print(keyword)
        pr_code = pr_dict[keyword]
        df = pd.read_csv('C:\\Users\\rdangelo\\Downloads\\cases_'+pr_code+'.csv')
        output.extend(info_extractor(df, keyword))
    return output

output = extract_all(keywords)

file = open('redundant_final.json', 'a')
for i in range(len(output)):
    line = '{"index":{"_id":"'+str(i)+'"}}\n'
    file.write(line)
    file.write(output[i]+'\n')
file.write('\n')
file.close()
