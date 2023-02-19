import requests,pprint
from bs4 import BeautifulSoup
def extra_source1(url):
    r=requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    table=soup.find('table').text
    return table
    pass

    
# ############ Function Call ############
if __name__ == "__main__":
    pprint(extra_source1('https://sustainablesources.com/resources/country-abbreviations/'))


