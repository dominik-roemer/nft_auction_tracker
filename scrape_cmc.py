import requests
import bs4
import pandas as pd

dateList = []
highList = []
low_list = []

response = requests.get('https://coinmarketcap.com/currencies/bitcoin/historical-data/')
soup = bs4.BeautifulSoup(response.text, features="lxml")
soup.find_all('td')

