from selenium import webdriver 
import pandas as pd

chromeOptions = webdriver.ChromeOptions()
chromeOptions.add_experimental_option('excludeSwitches', ['disable-component-update'])
chromeOptions.add_argument('headless')

pr_codes_appeals = ['PVOI=RF', 'SANC%3DOB', 'SANC%3DRF', 'PVOI%3DRI', 'SANC', 'PVOI%3DOB']

pr_codes_actions = ['ANNU=RF','ANNU=OB','ANNU','ANNU%3DRI','RESP%3DOB','CONS%3DOB','RESP%3DRF','CARE%3DRI','CARE%3DOB','RESP%3DRI','RENV','CARE%3DNL','ANNU%3DNL','CONS%3DRF','CARE%3DRF']

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


def get_data(browser, df, keyword):
    '''
    is the first and most important function: it has 3 arguments that need to be passed to it: 
    - browser (a reference to the web browser controlled by Python), 
    - df (a dataframe on which we will save the data extracted), 
    -  keyword (referring to the kind of case that is taken into consideration). 
    Thanks to the Selenium library, we use Python to loop4 through the pages of the search result (which depends on the keyword) and collect the data of interest (Title and CELEX number). 
    Ultimately, the dataframe is saved in a .csv5 file. This is useful because it allows us to avoid having to re-run the program in the future, all the data is now in .csv file and saves a lot of time.
    '''
    url = 'http://eur-lex.europa.eu/search.html?lang=en&text=abuse+of+dominant+position&qid=1512057591145&type=quick&DTS_SUBDOM=EU_CASE_LAW&scope=EURLEX&FM_CODED=JUDG&PR_CODED='+keyword
    browser.get(url)
    res = browser.find_element_by_class_name('resultNumber')
    maxnum = int(res.text.split(' ')[-1])
    iters = maxnum // 10 + 1 * (maxnum % 10 != 0) + 1
    index = 0
    
    for page in range(1,iters):
        print('page=' + str(page))
        url = "http://eur-lex.europa.eu/search.html?lang=en&text=abuse+of+dominant+position&qid=1512057591145&type=quick&DTS_SUBDOM=EU_CASE_LAW&scope=EURLEX&FM_CODED=JUDG&page="+str(page)+'&PR_CODED='+keyword
        browser.get(url)
        articles = browser.find_elements_by_class_name('publicationTitle')
        
        for i in range(len(articles)):
            c = browser.find_element_by_xpath('//*[@id="middleColumn"]/table/tbody/tr[' + str(3*(i+1)) + ']/td[1]/ul/li[2]')
            if not(c.text.startswith('CELEX')):
                c = browser.find_element_by_xpath('//*[@id="middleColumn"]/table/tbody/tr[' + str(3*(i+1)) + ']/td[1]/ul/li[1]') 
            title = articles[i].text
            df.set_value(index,"Title",title)
            df.set_value(index,"CELEX",c.text)
            index += 1
            
    df.to_csv("cases_" + str(keyword) + ".csv",encoding = "utf-8")
    df.to_pickle("cases_" + str(keyword) + ".csv")
    return df

def clean_df(df, keyword):
    '''
    This function, as the name suggests, provides us with better data by cleaning some features of the dataframe that are unnecessary for the goal of the project.
    For example, sometimes the get_data() function created an extra column in the dataframe with no content, and this function removes it.
    '''
    try:
        del df["Unnamed: 0"]
    except:
        pass
        
    n = len(df)
    for i in range(n):
        df["CELEX"][i] = df["CELEX"][i].replace('CELEX number: ','')
    df.to_csv("cases_" + str(keyword) + ".csv",encoding = "utf-8")
    df.to_pickle("cases_" + str(keyword) + ".csv")
    return df

def create_links(df, keyword):
    '''
    Uses the CELEX number to manipulate the URL of eur-lex.europa.eu and generates the links to the court decisions.
    '''
    n = len(df)
    df["Link"] = None
    for i in range(n):
        link = 'http://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:' + df["CELEX"][i]
        df["Link"][i] = link
    df.to_csv("cases_" + str(keyword) + ".csv",encoding="utf-8")
    df.to_pickle("cases_" + str(keyword) + ".csv")
    return df


def main(browser, keyword= 'appeal unfounded'):
    
    df = pd.DataFrame(columns = ["Title","CELEX"])
    
    pr_code = pr_dict[keyword]
    get_data(browser,df, pr_code)
    clean_df(df, pr_code)
    create_links(df, pr_code)
    return df

def extract_all(keywords = keywords):
    browser = webdriver.Chrome(chrome_options=chromeOptions)
    print('total keywords = '+ str(len(keywords)))
    for i in range(len(keywords)):
        df = main(browser, keywords[i])
        print ('done keyword', keywords[i])
        print ('done'+ str(i+1)+'/'+str(len(keywords)))        
    browser.close()
    return df
