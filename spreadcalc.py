#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
from bs4 import BeautifulSoup
import csv
from itertools import cycle
from statistics import mean 
import random
from random import randint
import numpy as np
import time
from datetime import date


# In[2]:


symbols = []
companyNames = []
companySectors = []
userAgentList = []

useragents = open("useragents.txt", "r")

for line in useragents:
    userAgentList.append(line.replace('\n', ''))   


# In[3]:


def getProxies(inURL):
    
    page = requests.get(inURL)
    soup = BeautifulSoup(page.text, 'html.parser')
    terms = soup.find_all('tr')
    IPs = []

    for x in range(len(terms)):  
        
        term = str(terms[x])        
        
        if '<tr><td>' in str(terms[x]):
            pos1 = term.find('d>') + 2
            pos2 = term.find('</td>')

            pos3 = term.find('</td><td>') + 9
            pos4 = term.find('</td><td>US<')
            
            IP = term[pos1:pos2]
            port = term[pos3:pos4]
            
            if '.' in IP and len(port) < 6:
                IPs.append(IP + ":" + port)
                #print(IP + ":" + port)

    return IPs 


proxyURL = "https://www.us-proxy.org/"
pxs = getProxies(proxyURL)
proxyPool = cycle(pxs)


# In[4]:


def getSymbolsCSV(fileName):
    
    global symbols
    
    print('\nLoading data from ' + fileName)

    with open(fileName) as csvfile:
    
        readCSV = csv.reader(csvfile, delimiter=',')
        
        for row in readCSV:
            
            symbol  = str(row[0]).replace('ï»¿', '')
            
            symbols.append(symbol)  
 

getSymbolsCSV('OptionsTradingStocks.csv')


# In[26]:


def getOptionsSpreads(sym, exp):
    
    reload = True
    
    while reload == True:
        
        date = ''
        
        if exp == '2/12': date = 'date=1613088000'
        if exp == '2/19': date = 'date=1613692800'
        if exp == '2/26': date = 'date=1614297600'
        if exp == '3/5': date = 'date=1614902400'
            
        url = 'https://finance.yahoo.com/quote/' + sym + '/options?' + date

        agent = random.choice(userAgentList)
        headers = {'User-Agent': agent}

        page = requests.get(url, headers=headers, proxies = {"http": next(proxyPool)})
        soup = BeautifulSoup(page.text, 'html.parser')
        s2 = str(soup)
        

        optionChain = soup.find(id='Col1-1-OptionContracts-Proxy')

        if optionChain != None:
            
            currPrice = s2[s2.find('<span class="Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)" data-reactid="50">') + 60 : s2.find('<span class="Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)" data-reactid="50">') + 130]
            currPrice = '$' + currPrice[currPrice.find('>') + 1 : currPrice.find('<')]
            
            options = optionChain.find_all('tr', class_='in-the-money')
            reload = False
            calls = []

            for x in options:
                
                x = str(x)
                
                quote = x[x.find('href="/quote/') : x.find('href="/quote/') + 100]
                
                if 'P00' in quote:
                    break
                    
                else:
                    
                    strike = x[x.find('options?strike=') + 15 : x.find('options?strike=') + 22]
                    strike = strike.replace('&amp', '').replace('&a', '').replace(';', '').replace('m', '')

                    askPrice = x[x.find('options?strike=') + 240 : x.find('class="data-col6 ')]
                    askPrice = askPrice[askPrice.find('>') + 1 : askPrice.find('<')]
                    
                    #print(sym, strike, askPrice)

                    calls.append([strike, askPrice])
            
            
            spreads = []
            
            
            for y in range(len(calls)):
                
                buyCallStrike = calls[y][0]
                buyCallAskPrice = calls[y][1]
                
                for z in range(y + 1, len(calls)):
                
                    sellCallStrike = calls[z][0]
                    sellCallAskPrice = calls[z][1]
                    
                
                    strikeDiff = float(sellCallStrike) - float(buyCallStrike)
                        
                    premium = round(((-1 * float(buyCallAskPrice)) + float(sellCallAskPrice)) * 100, 2)
                    
                    maxProfit = strikeDiff * 100 - abs(premium)
                    
                    percentReturn = round((maxProfit / abs(premium)) * 100, 2)
                    
                    spreads.append([buyCallStrike, buyCallAskPrice, sellCallStrike, sellCallAskPrice, strikeDiff, premium, maxProfit, percentReturn])
            
                    #print('(' + str(buyCallStrike) + ', ' + str(buyCallAskPrice) + ')', '(' + str(sellCallStrike) + ', ' + str(sellCallAskPrice) + ')', strikeDiff, premium, maxProfit)

            
            
            spreads = sorted(spreads,key=lambda l:l[-1], reverse=True)
            print('\n***', sym, '***\n')
            print('Current Price:', currPrice, '\n')
            
            for s in spreads[0 : 20]:
                print('BTO', str(s[0]) + 'c', 'Cost: ' + str(s[1]))
                print('STO', str(s[2]) + 'c', 'Cost: ' + str(s[3]))
                print('Entry Cost:', s[5])
                print('Max Profit:', s[6], '+' + str(s[7]) + '%')
                print('----------------------------\n')
                

# In[27]:


stock = input('Enter the stock you want to analyze: ')
expiration = input('Enter the expiration date (Ex: 2/12): ')
getOptionsSpreads(stock, expiration)


