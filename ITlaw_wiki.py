from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import wikipedia as wp
from collections import Counter

chromeOptions = webdriver.ChromeOptions()
chromeOptions.add_experimental_option('excludeSwitches', ['disable-component-update'])
chromeOptions.add_argument('headless')

####
# This function reads the names of the parties involved in cases extracted from eur-lex
# and saves them in a more ordered way in a file called "appellant_list.txt"

def create_company_list():
    txt = open('appellant.txt')
    applist = open('appellant_list.txt', 'w')
    companies = txt.read()
    c_list0 = companies.split('\n')
    c_list1 = []
    to_remove = ['', 'Others', 'others']
    for i in range(len(c_list0)):
        com = c_list0[i].replace("\'", "")
        singles = com.split(", ")
        for s in singles:
            if s not in c_list1 and s not in to_remove:
                c_list1.append(s)
                applist.write(s + '\n')
    txt.close()
    applist.close()
    return c_list1

    
# This function uses Python's module "wikipedia" to obtain the correct urls of the 
# companies' pages. This is necessary for 2 main reasons:
# - it cleans the data by eliminating parties that do not have a wikipedia page
# - it prepares the url that are going to be used in the extraction process

def get_urls_wiki():
    wp.set_lang("en")
    
    a = []
    with open('appellant_list.txt', 'r') as f:
        for line in f:
            a.append(line.strip())    
    b = {}    
    count_a = 0
    
    for element in a:
        try:
            b[element] = wp.page(element).url
            count_a += 1
        except Exception:
            pass
    print('Accepted: ' + str(count_a) + ' of ' + str(len(a)))  
    
    g = open('urls.txt', 'w')
    for i,j in b.items():
        g.write(i + " : " + j + '\n') 
    g.close()
    return b
    
def single_test(url):
    browser = webdriver.Chrome(chrome_options = chromeOptions)
    get_data_wiki(browser, url)
    browser.close()

# This function detects whether the given url redirects to a Wikipedia page about a company
# It "looks at" the box to the right that every company Wikipedia page has and checks
# whether there are some company-related keywords (Type, Revenue or Number of Empoyees)

def iscompany(browser, url):
    browser.get(url)
    try:
        box = browser.find_element_by_xpath('//*[@id="mw-content-text"]/div/table')
        if 'This article needs to be updated' in box.text or 'This article relies too much on references to primary sources' in box.text:
            box = browser.find_element_by_xpath('//*[@id="mw-content-text"]/div/table[2]')
#            print('second box')
        if 'Type' in box.text or 'Revenue' in box.text or 'Number of employees' in box.text:
            return True
        else:
            return False
    except:
        return False
    return

# This is the function that actually extracts the data from the Wikipedia pages
# It works as follows:
# 1 - the scraper selects the table from which it is going to select the data and puts all the information in a list
# 2 - After having discarded some of the elements (the ones with less than 6 characters
#     are considered meaningless), we divide the titles of each information from the actual content
#     splitting on the newlines. Sometimes the whole content is in a single row so we split looking 
#     for the first word with capital intial aftere the first word.
# 3 - At this point we have two lists (title and info) and organize them in a dictionary
#     This dictionary is the final result of the single extraction

def get_data_wiki(browser, url):
    browser.get(url)
    data = browser.find_elements_by_xpath('//*[@id="mw-content-text"]/div/table/tbody/tr')
    ld = len(data)
    content = []
    for i in range(ld):
        content.append(data[i].text)
    
    titles = []
    info = []
    for i in range(len(content)):
        c = content[i]
        if len(c) < 6:
            content[i] = None
            continue
        
        lc = c.split('\n')
        if len(lc) > 1:
            titles.append(lc[0])
            info.append(', '.join(lc[1:]))
        else:
            w = lc[0].split(' ')
            if w[0] == 'Founded':
                titles.append(w[0])
                info.append(' '.join(w[1:]))
                continue
            for i in range(1, len(w)):
                if w[i].istitle():
                    titles.append(' '.join(w[:i]))
                    info.append(' '.join(w[i:]))
                    break
                if '$' in w[i] or '€' in w[i] or '£' in w[i]:
                    titles.append(' '.join(w[:i]))
                    info.append(' '.join(w[i:]))
                    break
                if w[i].isdigit():
                    titles.append(' '.join(w[:i]))
                    info.append(' '.join(w[i:]))
                    break
    
    assert len(titles) == len(info)
    
    final_data = {}
    for t in range(len(titles)):
        final_data['"' + titles[t] + '"'] = '"' + info[t] + '"'
    
    return final_data
    
# This is the main function of the process. It begins by reading the urls of the companies
# from the urls.txt file (created with the get_urls_wiki() function)
# Then it loops over all the urls and carries out the extraction process.
# After checking whether the urls redirects to an actual company it collects the data
# with the get_data_wiki() function and stores in a dictionary.
# The final dictionary has the form {"company" : "data"}, where "data" is itself a dictionary
# indexed as {"key" : "content"}

def main():
#   urls = get_urls_wiki()
    urls = {}
    urlsfile = open('urls.txt', 'r')
    urlsread = urlsfile.read()
    couples = urlsread.split('\n')
    for couple in couples:
        if couple != '':
            company, url = couple.split(" : ")
            if url not in urls.values():
                urls[company] = url
    urlsfile.close()
        
    browser = webdriver.Chrome(chrome_options = chromeOptions)
    data = {}
    for c in urls:
        company = c
        url = urls[c]
        if iscompany(browser, url):
            data['"' + company + '"'] = get_data_wiki(browser, url)
    browser.close()
    return data

# This function checks whether there are keys common to every company. Since there are not,
# we created the function distribution() to gain grater insights.

def common_keys(data):
    ck = []
    companies = list(data.keys())
    tc = len(companies)
    for a in data[companies[0]]:
        for i in range(1, tc):
            if a not in data[companies[i]].keys():
                break
            if i == tc - 1:
                ck.append(a)
    return ck

# This function takes the "data" dictionary as input and checks the frequency distribution
# of the keys that are related to each company analyzed. We only consider keys that appear
# in at least 10 companies, so we discard meaningless keys.

def distribution(data):
    companies = list(data.keys())
    distr = Counter()
    for company in companies:
        keys = list(data[company].keys())
        for key in keys:
            distr[key] += 1
    to_del = []
    for d in distr:
        if distr[d] < 10:
            to_del.append(d)
    for i in to_del:
        del distr[i]
    return distr

# This function takes the "data" dictionary as input and saves it in a txt file
# Its purpose is to avoid having to run the main() code (which takes around 5 minutes).

def save_data(data):
    file = open('final_data.txt','w', encoding = 'utf-8')
    companies = list(data.keys())
    for company in companies:
        file.write(company + ' :\n' + str(data[company]) + '\n\n')
    file.close()

        
        
        
        
        
