import json

def get_json():
    ''' This function opens the file redundant_final.json and reads it
    '''
    with open("redundant_final.json") as reader:
        text = reader.read()
    text = text.split('\n')
    text = text[1::2]
    data = []
    for i in text:
        data.append(json.loads(i))
    return data

def remove_copies(data):
    ''' This function checks the data extracted and remooves the copies
    '''
    dic = 0
    #loop through cases
    while dic < len(data):
        new_dic1 = data[dic].copy()
        new_dic1.__delitem__('case type')
        to_remove = []
        to_add = []
        #checks that no other case exists that has all the same info
        for j in range(dic+1, len(data)):
            new_dic2 = data[j].copy()
            new_dic2.__delitem__('case type')
            if new_dic2 == new_dic1:
                if data[dic]['case type'] != data[j]['case type']:
                    to_add.append(data[j]['case type'])
                to_remove.append(j)
        #remove doubles
        to_add.append(data[dic]['case type'])
        data[dic]['case type'] = list(set(to_add))
        [data.pop(elem) for elem in to_remove[::-1]]
        dic += 1
    return data

def save_json(data):
    ''' This transform the data in a JSON file
    '''
    l = []
    for i in range(len(data)):
        l.append('{"index":{"_id":"%d"}}'%(i))
        l.append(json.dumps(data[i]))
    
    w = open('final.json','w')
    w.write("\n".join(l) + '\n')
    
    w.close()



def main():
    data = get_json()
    dic = remove_copies(data)
    save_json(dic)
