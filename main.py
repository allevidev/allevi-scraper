from xml.dom import minidom
import urllib2
import xmltodict
import requests
import re
import csv
import sys

def fetchArticle(database, articleId, fileName):
    url = 'https://www.ncbi.nlm.nih.gov/' + database + '/' + articleId
    r = requests.get(url)
    page = xmltodict.parse(r.content)
    content =  page['html']['body']['div']['div']['form']['div'][0]['div']
    for div in content:
        if  '@id' in div:
            if div['@id'] == 'maincontent':
                for contentDiv in  div['div']['div']:
                  if contentDiv is None:
                      continue
                  if  '@class' in contentDiv:
                    if contentDiv['@class'] == 'rprt_all':
                        authors = []
                        sup = []
                        affl = []
                        for dataDiv in contentDiv['div']['div']:
                            if  '@class' in dataDiv:
                                if dataDiv['@class'] == 'auths':
                                    try:
                                        for aElem in dataDiv['a']:
                                            authors.append(aElem['#text'])
                                        sup = dataDiv['sup']
                                        for i in range(0, len(sup)):
                                          sup[i] = int(sup[i])
                                    except:
                                        continue
                                elif dataDiv['@class'] == 'afflist':
                                    #print dataDiv['dl']
                                    for aElem in dataDiv['dl']['dd']:
                                        try:
                                            affl.append(aElem)
                                        except:
                                            continue
                                    useDiv = False
                                    try:
                                      useDiv = max(sup) == len(affl)
                                    except: 
                                      continue
                                    if useDiv:
                                        try:
                                            with open(fileName, 'a') as csvfile:
                                              fieldnames = ['name', 'affiliation', 'email']
                                              writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                                              for count in range(0, len(authors)):
                                                  match = re.findall(r'[\w\.-]+@[\w\.-]+(?=\.)', affl[int(sup[count]) - 1])
                                                  email = ""
                                                  if len(match) > 0:
                                                      email = match[0]
                                                  print authors[count] , ' ' , affl[int(sup[count]) - 1], ' ', email
                                                  writer.writerow({'name': authors[count], 'affiliation': affl[int(sup[count]) - 1], 'email': email})
                                        except:
                                            continue
                                        continue

def fetchIdList(database, term, count):
    url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?' + 'db=' + database + '&term=' + term + '&retmax=' + str(count)
    r = requests.get(url)
    page = xmltodict.parse(r.content)
    return page['eSearchResult']['IdList']['Id']

def main(term):
  fileName = term +  ".csv"
  with open(fileName, 'w') as csvfile:
    fieldnames = ['name', 'affiliation', 'email']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    idList = fetchIdList('pubmed', term, 100000)
    for i in range(0, len(idList)):
        fetchArticle('pubmed', idList[i], fileName)

if __name__== "__main__":
    terms = sys.argv
    terms.pop(0)
    term =  " ".join(terms)
    main(term)


